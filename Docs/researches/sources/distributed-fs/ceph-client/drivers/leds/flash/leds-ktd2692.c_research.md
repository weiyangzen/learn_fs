# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-ktd2692.c

## Purpose
This platform driver supports the Kinetic KTD2692 flash LED controller through the LED ExpressWire single-wire protocol. It provides torch/movie brightness and flash strobe control through the LED flash class.

## Important APIs, Types, and Functions
`struct ktd2692_context` stores ExpressWire properties, flash class device, mutex, optional regulator, optional auxiliary GPIO, mode, and torch brightness. `ktd2692_timing` defines protocol pulse timing. LED operations are `ktd2692_led_brightness_set()`, `ktd2692_led_flash_strobe_set()`, and `ktd2692_led_flash_timeout_set()`. Setup/configuration helpers include `ktd2692_parse_dt()`, `ktd2692_init_flash_timeout()`, `ktd2692_init_movie_current_max()`, and `ktd2692_setup()`.

## Control Flow
Probe allocates context, sets ExpressWire timing, parses GPIO/regulator and the first child LED node, initializes flash timeout and max movie brightness, registers the flash LED class device, and writes initial hardware settings. Torch brightness writes movie current and mode registers over ExpressWire, using the auxiliary GPIO low for off. Flash strobe writes timeout, drives the auxiliary GPIO high for flash, programs flash mode, and clears brightness/mode state after the flash event.

## State and Persistence
The driver caches only volatile mode, brightness, and LED flash class settings. Regulator enable is managed by a devm cleanup action if the optional `vin` supply exists. Hardware is explicitly powered off during setup and disabled on brightness/strobe off.

## Dependencies and Integration Points
Dependencies include the ExpressWire helper namespace, `ctrl` GPIO, optional `aux` GPIO, optional `vin` regulator, OF child properties `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`, and the LED flash class. It binds `kinetic,ktd2692` and imports the `EXPRESSWIRE` namespace.

## Risks and Edge Cases
`aux_gpio` is optional but several paths call `gpiod_direction_output()` on it unconditionally; if optional GPIO absence returns NULL, behavior depends on gpiod helper tolerance and should be verified. Flash timeout setter is a no-op because the class core caches the value, but invalid hardware programming can still happen if timeout step calculation is wrong. ExpressWire pulse timing is tight and hardware-sensitive. Regulator enable failure logs an error but continues without returning if the regulator object exists and enable fails.

## Test Signals
Use a logic analyzer to validate ExpressWire writes, test torch off/on levels, flash timeout levels, regulator cleanup, optional aux GPIO absence, and suspend/resume LED core behavior. Build tests should confirm the ExpressWire namespace import and selected helper object.
