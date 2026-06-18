# sources/distributed-fs/ceph-client/drivers/leds/leds-ariel.c

## Purpose
Implements Dell Wyse 3020 "Ariel" embedded-controller status LEDs. It exposes blue power, amber status, and green status LEDs backed by simple EC RAM register values.

## Important APIs, Types, And Functions
`struct ariel_led` stores the parent EC regmap, EC index, and LED classdev. Main callbacks are `ariel_led_get`, `ariel_led_set`, `ariel_blink_set`, and `ariel_led_probe`.

## Control Flow
Probe obtains parent regmap `ec_ram`, allocates three LEDs, assigns EC indexes/names/default triggers, sets brightness get/set and blink callbacks, and registers each via devm LED registration.

Brightness get reads the EC register and reports `LED_FULL` only when the value is `EC_LED_STILL`. Brightness set writes `EC_LED_OFF` or `EC_LED_STILL`. Blink rejects unspecified default blink, maps zero-on to off, zero-off to steady, and otherwise forces 500/500 ms while writing `EC_LED_BLINK`.

## State And Persistence
No private mutable state beyond classdev caches; EC RAM registers persist hardware LED modes. Default triggers are set for blue power and green status.

## Dependencies And Integration Points
Depends on a parent platform device with regmap named `ec_ram`, the LED class, and the platform driver named `dell-wyse-ariel-led`.

## Risks
Only one hardware blink frequency is exposed, so arbitrary blink requests are normalized to 500/500. `ariel_led_get` treats blink/fade as off from the brightness perspective. Regmap write errors in set/blink are ignored because callbacks are nonblocking `void` or return success after writes.

## Test Signals
Probe should create three named LEDs, default triggers should apply, brightness reads should match EC still/off state, blink should write EC blink mode and adjust delays to 500 ms, and missing `ec_ram` should return `-ENODEV`.
