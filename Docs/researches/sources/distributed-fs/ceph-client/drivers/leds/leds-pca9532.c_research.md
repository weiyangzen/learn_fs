# sources/distributed-fs/ceph-client/drivers/leds/leds-pca9532.c

Purpose: PCA9530/31/32/33 I2C LED dimmer driver with optional GPIO and Thecus N2100 beeper support.

Important APIs/types/functions: `struct pca9532_data` stores client, LED array, mutex, optional input device/work, optional gpio chip, chip info, PWM/PSC state, and hardware-blink availability. `pca9532_set_brightness()`, `pca9532_set_blink()`, `pca9532_setled()`, `pca9532_configure()`, and `pca9532_of_populate_pdata()` are core paths.

Control flow: probe gets platform data or parses OF, checks SMBus byte support, allocates state, then configures initial PWM/PSC registers and each channel as none, GPIO, LED, or beeper. LED brightness routes off/full directly or non-full brightness through shared PWM0. Hardware blink uses PWM1 only when not reserved by beeper. Optional GPIO exposes LED pins through gpiochip operations.

State and persistence: driver caches PWM/PSC values and each LED state; hardware selector registers hold output routing. Beeper PWM updates are deferred via workqueue from input events. GPIO and LED roles are fixed by platform/DT data.

Dependencies and integration: depends on I2C SMBus, LED class, optional GPIO library, input subsystem for beeper, platform data header `leds-pca9532.h`, OF parsing, mutex/workqueue.

Risks: shared PWM channels mean multiple dimmed LEDs get averaged brightness and one blink configuration. I2C read/write return values are often ignored in low-level setters. GPIO mode can conflict with LED mode if platform data is wrong. Hardware blink is disabled when PWM1 is reserved for beeper.

Test signals: all supported chip sizes, OF/platform data parsing, LED off/full/dim routing, shared PWM averaging, blink conflict/period bounds, beeper input events, GPIO request/set/get, and cleanup after partial registration failure.
