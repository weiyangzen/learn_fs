# sources/distributed-fs/ceph-client/drivers/leds/leds-an30259a.c

## Purpose
Implements the Panasonic AN30259A three-channel I2C LED driver. It supports brightness, hardware blink/slope mode, and firmware-described default state for up to three channels.

## Important APIs, Types, And Functions
`struct an30259a_led` stores chip pointer, fwnode, classdev, channel number, default state, and `sloping`. `struct an30259a` stores mutex, client, LED array, regmap, and LED count. Key functions are `an30259a_brightness_set`, `an30259a_blink_set`, `an30259a_dt_init`, `an30259a_init_default_state`, and `an30259a_probe`.

## Control Flow
Probe parses child nodes with `reg` values 1-3, records default state, initializes mutex/client/regmap, applies default state for each LED, assigns blocking brightness and blink callbacks, and registers through `devm_led_classdev_register_ext`.

Brightness reads `LED_ON`, clears enable/slope for off, or enables the channel and optional slope bit for on, programs full duty max/mid, writes `LED_ON`, then writes the current register. Blink validates delays are multiples of 500 ms and at most 7500 ms, defaults unspecified blink to 500/500, writes slope/duty/detention registers, enables slope and channel bits, and caches `sloping`.

## State And Persistence
The driver maintains `sloping` per LED and brightness in the classdev. Hardware state persists in LED_ON, LEDCC, SLOPE, and LEDCNT registers. `default-state = keep` reads current hardware enable/current before reprogramming.

## Dependencies And Integration Points
Depends on I2C, regmap, OF child nodes, LED class, and `led_init_default_state_get`. Compatible string is `panasonic,an30259a`.

## Risks
Blink callback parameter names are `delay_off, delay_on`, opposite the usual LED API naming convention, so maintainers must verify call-site expectations carefully. Default-state initialization calls the brightness callback before classdev registration, which relies on initialized chip/regmap and no `cdev.dev` use in the callback. Invalid child nodes reduce the count and can reject all LEDs.

## Test Signals
Validate DT parsing for channels 1-3, default-state off/on/keep behavior, brightness on/off with slope clearing, blink validation for unsupported delays, hardware register writes for 500 ms increments, and devm cleanup on probe failures.
