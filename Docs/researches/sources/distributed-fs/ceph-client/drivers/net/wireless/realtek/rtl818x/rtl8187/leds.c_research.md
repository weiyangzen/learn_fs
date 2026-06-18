# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.c

## Purpose
This file implements optional LED class support for RTL8187 devices when `CONFIG_RTL8187_LEDS` is enabled. It maps EEPROM customer IDs to LED pins and registers radio, TX, and RX LED class devices using mac80211 LED trigger names.

## Important APIs, Types, And Functions
The public functions are `rtl8187_leds_init()` and `rtl8187_leds_exit()`. Internal helpers include `rtl8187_register_led()`, `rtl8187_unregister_led()`, `rtl8187_led_brightness_set()`, `led_turn_on()`, and `led_turn_off()`.

The code controls GPIO0 or PGSELECT LED bits depending on `ledpin` (`LED_PIN_GPIO0`, `LED_PIN_LED0`, `LED_PIN_LED1`, or hardware-controlled `LED_PIN_HW`). `struct rtl8187_led` stores the LED classdev, parent hardware pointer, pin mode, name, and radio-vs-activity flag.

## Control Flow
Initialization reads the customer ID passed from EEPROM handling in `dev.c`, selects a pin policy, initializes delayed work items in `rtl8187_priv`, and registers radio, TX, and RX LEDs. If later registrations fail, it unregisters earlier LEDs.

Brightness callbacks do not touch hardware directly. For the radio LED they queue on/off work and track a static `radio_on` flag. For TX/RX activity they blink by queuing off work immediately and on work after `HZ / 20`, but only while the radio LED is considered on. The delayed work functions lock `conf_mutex`, check that a vif exists and the LED is registered, then write GPIO/PGSELECT state.

Exit unregisters all LED class devices, flushes/cancels delayed work, and clears device pointers.

## State And Persistence
LED state is held in `rtl8187_priv` under `CONFIG_RTL8187_LEDS`: three `rtl8187_led` objects and `led_on`/`led_off` work. A file-static `radio_on` boolean gates TX/RX blinking. Hardware state persists in GPIO0, GP_ENABLE, and PGSELECT bits until changed or the device is stopped/reset.

## Dependencies And Integration Points
This file depends on mac80211 LED trigger naming, the Linux LED class, USB device ownership for classdev registration, EEPROM customer IDs from `dev.c`, and RTL8187 register I/O helpers. It shares `conf_mutex` with device configuration because LED writes touch the same hardware register space.

## Risks
The static `radio_on` flag is global across devices, which can be wrong if multiple RTL8187 adapters are present. Both on/off workers always use `priv->led_tx` as the selected LED object, so radio/RX class state mainly drives the same pin behavior rather than independent LEDs. Work cancellation and unregister ordering must prevent callbacks from using a cleared `led->dev`. Hardware LED mode (`LED_PIN_HW`) intentionally does nothing in software.

## Test Signals
Build with and without `CONFIG_RTL8187_LEDS`, probe devices with different EEPROM customer IDs, verify radio/TX/RX LED class entries and triggers, test TX/RX blink while associated, unload/disconnect under active LED work, and test multiple adapters for cross-device `radio_on` interference.
