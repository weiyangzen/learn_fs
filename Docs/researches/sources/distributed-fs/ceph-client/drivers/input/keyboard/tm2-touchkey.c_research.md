# sources/distributed-fs/ceph-client/drivers/input/keyboard/tm2-touchkey.c

## Purpose

This I2C driver supports Samsung/Cypress/Coreriver touchkey devices used on TM2, Midas, Aries, and TC360 platforms. It reports capacitive touch keys and exposes a LED class device for touchkey backlight control, with variant-specific I2C command formats and regulator behavior.

## Important APIs, Types, and Functions

`struct touchkey_variant` describes keycode register, command register, LED commands, no-register protocol, and fixed-regulator behavior. `struct tm2_touchkey_data` stores client, input, LED device, regulators, variant, and keycodes. `tm2_touchkey_power_enable()` enables supplies and waits for initialization. `tm2_touchkey_irq_handler()` reads event data, decodes key index and press/release bit, and reports input events. `tm2_touchkey_led_brightness_set()` sends LED commands and optionally changes VDD voltage.

## Control Flow

Probe checks I2C capabilities, selects OF variant data, gets three regulators, reads optional `linux,keycodes` or uses defaults, powers the device, installs a devm power-off action, registers input keys, requests a threaded IRQ, registers the LED class device, and turns LEDs on for fixed-regulator variants. IRQ handling reads either a byte or byte-data register, validates the key index, reports `MSC_SCAN`, releases all keys on release events, or presses the indexed key, then syncs. Suspend disables IRQ and power; resume reenables IRQ and power.

## State and Persistence Behavior

Keycodes and variant selection persist for device lifetime. LED brightness is stored in the LED class device, while actual hardware state is controlled by I2C commands and possibly VDD voltage. Regulators are kept enabled while active and disabled on suspend/remove.

## Dependencies and Integration Points

The driver depends on OF match data, I2C SMBus byte/byte-data support, regulator bulk APIs, input key events, LED class, and threaded IRQs. Compatibles include `cypress,tm2-touchkey`, `cypress,midas-touchkey`, `cypress,aries-touchkey`, and `coreriver,tc360-touchkey`.

## Risks and Edge Cases

The handler references `data` in the fixed-regulator LED sync block even after a failed I2C read path, so error handling should be reviewed. Release events release all configured keys rather than the indexed key. Suspend enables IRQ before power in resume, allowing a narrow race if the line fires before the device is initialized. Regulator voltage changes are ignored for fixed-regulator variants.

## Test Signals

Test all variants, no-register and register protocols, custom/default keycodes, invalid key indexes, I2C read failures, LED on/off commands, regulator voltage behavior, suspend/resume race behavior, and fixed-regulator backlight synchronization.
