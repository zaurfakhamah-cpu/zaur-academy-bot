import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "328578333"))  # @zaur_academy

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ─── СОСТОЯНИЯ ───────────────────────────────────────────────
class OrderForm(StatesGroup):
    waiting_name = State()
    waiting_contact = State()
    waiting_description = State()


# ─── УСЛУГИ ──────────────────────────────────────────────────
SERVICES = {
    "bot_simple": {
        "name": "🤖 Простой Telegram бот",
        "price": "от 5 000 ₽",
        "desc": (
            "Эхо-боты, FAQ-боты, боты с кнопками.\n"
            "Срок: 1–2 дня.\n"
            "Идеально для старта и проверки идеи."
        ),
    },
    "bot_payment": {
        "name": "💳 Бот с оплатой",
        "price": "от 12 000 ₽",
        "desc": (
            "Telegram Stars, TON, ЮKassa или Stripe.\n"
            "Каталог товаров / услуг, корзина, чеки.\n"
            "Срок: 3–5 дней."
        ),
    },
    "bot_ai": {
        "name": "🧠 AI-бот (GPT / Claude)",
        "price": "от 20 000 ₽",
        "desc": (
            "Умный ассистент, транскрипция, генерация.\n"
            "Голосовой ввод, работа с файлами.\n"
            "Срок: 5–7 дней."
        ),
    },
    "automation": {
        "name": "⚙️ Автоматизация (n8n / Make)",
        "price": "от 8 000 ₽",
        "desc": (
            "Автопостинг, парсинг, CRM-интеграции.\n"
            "Соединяем любые сервисы без кода.\n"
            "Срок: 2–4 дня."
        ),
    },
    "miniapp": {
        "name": "📱 Telegram Mini App",
        "price": "от 25 000 ₽",
        "desc": (
            "Полноценное веб-приложение внутри Telegram.\n"
            "Магазины, курсы, трекеры, игры.\n"
            "Срок: 7–14 дней."
        ),
    },
}


# ─── КЛАВИАТУРЫ ──────────────────────────────────────────────
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠 Наши услуги", callback_data="services")],
        [InlineKeyboardButton(text="📋 Оставить заявку", callback_data="order")],
        [InlineKeyboardButton(text="💬 Примеры работ", callback_data="portfolio")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
    ])


def services_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=v["name"], callback_data=f"svc_{k}")]
        for k, v in SERVICES.items()
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def service_detail_menu(svc_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заказать", callback_data="order")],
        [InlineKeyboardButton(text="◀️ Назад к услугам", callback_data="services")],
    ])


def back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_main")]
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ])


# ─── СТАРТ ───────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Привет! Я бот Zaur Academy</b>\n\n"
        "Создаём Telegram боты и автоматизации под ключ.\n"
        "Быстро, надёжно, с поддержкой после сдачи.\n\n"
        "Выбери, что тебя интересует 👇",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# ─── ГЛАВНОЕ МЕНЮ ────────────────────────────────────────────
@dp.callback_query(F.data == "back_main")
async def back_to_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "👋 <b>Привет! Я бот Zaur Academy</b>\n\n"
        "Создаём Telegram боты и автоматизации под ключ.\n"
        "Выбери, что тебя интересует 👇",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# ─── УСЛУГИ ──────────────────────────────────────────────────
@dp.callback_query(F.data == "services")
async def show_services(call: types.CallbackQuery):
    await call.message.edit_text(
        "🛠 <b>Наши услуги</b>\n\nВыбери нужную — расскажем подробнее:",
        parse_mode="HTML",
        reply_markup=services_menu(),
    )


@dp.callback_query(F.data.startswith("svc_"))
async def show_service_detail(call: types.CallbackQuery):
    key = call.data.replace("svc_", "")
    svc = SERVICES.get(key)
    if not svc:
        await call.answer("Услуга не найдена")
        return
    text = (
        f"{svc['name']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{svc['desc']}\n\n"
        f"💰 <b>Стоимость: {svc['price']}</b>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=service_detail_menu(key))


# ─── ПОРТФОЛИО ───────────────────────────────────────────────
@dp.callback_query(F.data == "portfolio")
async def show_portfolio(call: types.CallbackQuery):
    await call.message.edit_text(
        "💼 <b>Примеры наших работ</b>\n\n"
        "🤖 <b>VoiceMaxAI</b> — транскрипция аудио/видео + GPT обработка\n"
        "📖 <b>Quran Tajweed Mini App</b> — обучающий Telegram Mini App\n"
        "🕌 <b>Ruqiyah Bot</b> — VIP-подписки, TON/Stars оплата\n"
        "🛒 <b>TopShop Bot</b> — маркетплейс с геолокацией и каталогом\n"
        "⚙️ <b>n8n автопостинг</b> — RSS → GPT → Telegram канал\n\n"
        "👉 Хочешь похожий проект? Оставь заявку!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Оставить заявку", callback_data="order")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")],
        ]),
    )


# ─── FAQ ─────────────────────────────────────────────────────
@dp.callback_query(F.data == "faq")
async def show_faq(call: types.CallbackQuery):
    await call.message.edit_text(
        "❓ <b>Частые вопросы</b>\n\n"
        "<b>Сколько стоит бот?</b>\n"
        "От 5 000 ₽ — зависит от сложности. Пиши, рассчитаем точно.\n\n"
        "<b>Как долго делается?</b>\n"
        "Простые боты — 1–2 дня. Сложные — до 2 недель.\n\n"
        "<b>Как происходит оплата?</b>\n"
        "50% предоплата, 50% после сдачи. Карта / криптo / Stars.\n\n"
        "<b>Будет ли поддержка?</b>\n"
        "Да, 30 дней бесплатной поддержки после сдачи.\n\n"
        "<b>На каком хостинге работает?</b>\n"
        "Hetzner VPS или Railway — стабильно 24/7.",
        parse_mode="HTML",
        reply_markup=back_main(),
    )


# ─── ЗАЯВКА ──────────────────────────────────────────────────
@dp.callback_query(F.data == "order")
async def start_order(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.waiting_name)
    await call.message.edit_text(
        "📋 <b>Оставить заявку</b>\n\n"
        "Шаг 1/3 — Как тебя зовут?",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )


@dp.message(OrderForm.waiting_name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.waiting_contact)
    await message.answer(
        "Шаг 2/3 — Укажи контакт для связи\n(Telegram @username или телефон):",
        reply_markup=cancel_kb(),
    )


@dp.message(OrderForm.waiting_contact)
async def order_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(OrderForm.waiting_description)
    await message.answer(
        "Шаг 3/3 — Опиши свою задачу:\n"
        "Что должен делать бот / что хочешь автоматизировать?",
        reply_markup=cancel_kb(),
    )


@dp.message(OrderForm.waiting_description)
async def order_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # Уведомление администратору
    admin_text = (
        "🔔 <b>Новая заявка!</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Контакт: {data['contact']}\n"
        f"🆔 Telegram ID: {message.from_user.id}\n"
        f"📝 Задача:\n{message.text}"
    )
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    except Exception:
        pass

    # Подтверждение клиенту
    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Мы свяжемся с тобой в течение нескольких часов.\n\n"
        "Пока можешь посмотреть наши услуги или задать вопрос 👇",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "cancel_order")
async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Заявка отменена.\n\nВозвращаемся в главное меню:",
        reply_markup=main_menu(),
    )


# ─── ЗАПУСК ──────────────────────────────────────────────────
async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
