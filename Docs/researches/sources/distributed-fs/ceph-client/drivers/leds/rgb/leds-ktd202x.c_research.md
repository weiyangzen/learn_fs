# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ktd202x.c

Purpose: I2C driver for Kinetic KTD2026/KTD2027 RGB/white LED controllers. It supports single-channel LEDs and grouped multicolor LEDs with brightness and hardware blink.

Important APIs, types, and functions: `struct ktd202x` stores mutex, regulators, regmap, enabled flag, chip channel count, and LED array. `struct ktd202x_led` is either a regular LED or multicolor LED. `ktd202x_chip_enable()/disable()` manage regulators and sleep/wake register. `ktd202x_brightness_set()` writes current registers and channel-control modes. `ktd202x_blink_set()` converts requested delays to flash-period and on-time register values. Setup helpers parse single or RGB child layouts.

Control flow: probe counts children, initializes regmap/mutex/regulators, enables regulators for reset and registration, resets the chip, registers each child LED, then disables regulators until needed. Brightness paths set the classdev brightness, lock the chip, compute subled brightness for multicolor, write current and channel mode, and power the chip down when no LEDs are in use. Blink defaults to 500/500 ms and uses PWM1 mode.

State and persistence: LED brightness in classdevs is used to determine whether the chip is in use. Regcache defaults describe reset state, but hardware power is explicitly disabled when idle. Shutdown resets registers to ensure LEDs are off.

Dependencies and integration points: I2C, regmap with flat cache, regulator bulk supplies `vin`/`vio`, fwnode child parsing, LED and multicolor APIs, compatibles `kinetic,ktd2026`/`ktd2027`.

Risks and test signals: test regulator enable/disable sequencing, chip-in-use logic around the current LED being updated, single versus RGB parsing, blink delay quantization, no-off/no-on blink edge cases, and shutdown reset. Validate child channel bounds and that multicolor channel control cannot mix blink and steady-on unexpectedly.
