# sources/distributed-fs/ceph-client/drivers/leds/leds-acer-a500.c

## Purpose
Implements two one-bit power-button LEDs for the Acer Iconia Tab A500 embedded controller. The hardware exposes commands to enable the white or orange LED and a shared reset command that turns both off.

## Important APIs, Types, And Functions
`struct a500_led` stores an LED classdev, an enable register sequence, a pointer to the other LED, and the parent EC regmap. `a500_ec_led_brightness_set` is the class callback, and `a500_ec_leds_probe` registers `power:white` and `power:orange`.

## Control Flow
Probe obtains regmap `KB930` from the parent, writes the reset/off sequence, allocates two LED objects, fills names, max brightness, suspend/resume flag, enable sequences, mutual `other` pointers, and registers both through devm LED registration.

Setting brightness on writes the LED-specific enable sequence. Setting brightness off writes the shared reset command; if the other LED's cached brightness is nonzero, it appends the other LED's enable command so that the reset does not unintentionally turn it off.

## State And Persistence
There is no explicit lock or private cache beyond each LED classdev's `brightness` field. Hardware state is stored in the EC and updated through regmap multi-register writes with 100 ms command delays.

## Dependencies And Integration Points
Depends on a parent embedded-controller regmap named `KB930`, platform-device probing, and the LED class. Platform alias is `acer-a500-iconia-leds`.

## Risks
The shared reset/restore behavior depends on the LED core brightness cache for the other LED. Concurrent sysfs writes could interleave because there is no driver-level mutex. Hardware only supports on/off, so max brightness is one and triggers requiring arbitrary brightness will collapse to binary behavior.

## Test Signals
Probe should reset both LEDs and create `power:white` and `power:orange`. Turning either LED off while the other is on should restore the other. Suspend/resume should preserve LED class behavior through `LED_CORE_SUSPENDRESUME`.
