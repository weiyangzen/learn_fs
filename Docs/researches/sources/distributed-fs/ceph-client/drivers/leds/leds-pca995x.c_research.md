# sources/distributed-fs/ceph-client/drivers/leds/leds-pca995x.c

Purpose: PCA9952/PCA9955B/PCA9956B I2C LED driver for 16- or 24-output PWM controllers.

Important APIs/types/functions: `struct pca995x_chipdef` defines LED count, PWM base, and IREFALL register. `struct pca995x_chip` holds regmap and LED array. `pca995x_brightness_set()` selects LEDOUT off/on/PWM modes and writes per-output PWM values. Probe parses child `reg` nodes and registers LEDs.

Control flow: probe requires firmware node data, initializes regmap, collects child fwnodes by output index with duplicate validation, registers corresponding LED class devices, writes MODE1 normal mode, and sets global output current to half scale. Brightness full/off changes LEDOUT bits; intermediate brightness writes PWM then switches LEDOUT to PWM mode.

State and persistence: no software brightness cache beyond LED core. Hardware PWM, LEDOUT, MODE1, and IREFALL registers hold state. Fwnode handles are retained during registration and manually put on error.

Dependencies and integration: depends on I2C regmap, LED class extended registration, OF/fwnode child `reg`, and chip match data.

Risks: validation checks `reg >= PCA995X_MAX_OUTPUTS` rather than `chipdef->num_leds`, so a PCA9952/PCA9955B child above 15 can be accepted and later address unsupported outputs. Fwnode references are not explicitly put on successful registration. No blink support despite hardware families often having more features.

Test signals: valid/invalid child `reg` per chip type, full/off/PWM brightness writes, MODE1/IREFALL initialization, duplicate child detection, and regmap error propagation.
