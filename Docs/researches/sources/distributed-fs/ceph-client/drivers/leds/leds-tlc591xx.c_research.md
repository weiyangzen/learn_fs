# sources/distributed-fs/ceph-client/drivers/leds/leds-tlc591xx.c

Purpose: I2C LED driver for TI TLC59116 and TLC59108 PWM LED controllers. It registers child-node LEDs and drives each output as off, on, or PWM-dimmed.

Important APIs, types, and functions: `struct tlc591xx_led` tracks active channel, LED class device, and parent. `struct tlc591xx_priv` stores the regmap and LEDOUT offset. Per-chip `struct tlc591xx` data selects max LED count and LEDOUT register base. `tlc591xx_set_mode()` initializes MODE registers, `tlc591xx_set_ledout()` changes 2-bit output mode, and `tlc591xx_set_pwm()` writes per-channel PWM.

Control flow: probe requires an OF node and match data, validates child count, initializes I2C regmap, sets dim mode, then iterates child nodes. Each child must provide unique `reg`; the driver registers an LED with max brightness 256 and blocking brightness callback. Brightness 0 selects output-low off, max brightness selects on/HI-Z mode, and intermediate brightness selects dim mode plus PWM value.

State and persistence: active channel flags prevent duplicate registration. Runtime state is stored in chip registers via regmap, with no explicit cached brightness.

Dependencies and integration points: I2C, regmap, OF child nodes, LED class, compatibles `ti,tlc59116` and `ti,tlc59108`.

Risks and test signals: max brightness is 256, not U8_MAX, so test boundary values 0, 255, and 256. Validate duplicate/out-of-range `reg`, MODE register setup, LEDOUT bit packing, and behavior for chips with 8 versus 16 outputs.
