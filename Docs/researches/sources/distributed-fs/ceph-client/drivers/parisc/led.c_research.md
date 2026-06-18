# sources/distributed-fs/ceph-client/drivers/parisc/led.c

## Purpose
This file implements chassis LED and LCD support for HP PA-RISC machines. It discovers PDC-reported display hardware or accepts later LASI/ASP registration, exposes LED class devices with standard triggers, updates hardware-specific LED/LCD registers in software, and writes shutdown messages on reboot/halt/poweroff.

## Important APIs, Types, And Functions
The exported platform API is `register_led_driver()`, and the user-facing LCD helper is `lcd_print()`. Hardware writers are `led_ASP_driver()`, `led_LASI_driver()`, `led_LCD_driver()`, and `lcd_print_now()`. LED class integration uses `struct hppa_led`, `struct hppa_drvdata`, `set_led()`, `hppa_led_generic_probe()`, `platform_led_probe()`, and `platform_led_remove()`. Initialization is split between `early_led_init()` and `startup_leds()`.

## Control Flow
`early_led_init()` prepares a default Linux release string, handles KittyHawk-specific LCD defaults, otherwise queries `pdc_chassis_info()`, validates returned data, and calls `register_led_driver()`. `register_led_driver()` selects the correct hardware writer, records command/data registers, registers the platform LED driver, and installs a reboot notifier. Later `startup_leds()` registers the `platform-leds` device and reserves display MMIO regions. LED class brightness updates call `set_led()`, update the global bitmap, and invoke the selected hardware writer. LCD text changes set `lcd_new_text` and are flushed either immediately for LCD-only devices or during LED updates for combined LCD/LED devices.

## State And Persistence
Global state tracks display type, last LED bitmap, pending LCD text, LCD text buffer, KittyHawk no-LED flag, PDC LCD information, and the selected writer function. Registered LED class devices and MMIO resource reservations persist for the boot. Hardware state is entirely software-maintained through repeated register writes.

## Dependencies And Integration Points
The driver integrates PDC chassis info, PA-RISC GSC register writes, Linux LED class triggers, platform devices/drivers, reboot notifiers, LASI/ASP bridge discovery, and the power driver’s `lcd_print()` shutdown message. It avoids registering LEDs when running under QEMU.

## Risks
There is a single global LED/LCD backend; later registration attempts fail once `led_func_ptr` is set. Hardware command timing relies on PDC-provided microsecond delays. LCD writes are not protected by a lock, so concurrent messages/brightness changes can interleave. Platform driver registration happens before the platform device is registered, which is intentional but order-sensitive. `platform_register_drivers()` return value is ignored.

## Test Signals
Signals include PDC LCD/LED discovery logs, sysfs LEDs under `/sys/class/leds/`, working heartbeat/disk/network/panic triggers, correct LCD boot and shutdown messages, requested MMIO regions, no LED registration on QEMU, and correct KittyHawk/LASI/ASP hardware behavior. Test unknown PDC models, disabled `act_enable`, and machines where LASI registers LEDs after PDC discovery fails.
