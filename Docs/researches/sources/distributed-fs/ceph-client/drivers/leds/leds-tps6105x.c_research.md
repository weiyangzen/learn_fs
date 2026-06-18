# sources/distributed-fs/ceph-client/drivers/leds/leds-tps6105x.c

Purpose: platform LED driver for TPS6105x devices operating in torch mode. It exposes the torch current control as a LED class device.

Important APIs, types, and functions: `struct tps6105x_priv` stores regmap, LED class device, and optional child fwnode. `tps6105x_brightness_set()` writes `TPS6105X_REG0_TORCHC_MASK` according to brightness. `tps6105x_led_probe()` validates torch mode, sets mode bits, and registers the LED as `tps6105x:*:torch`.

Control flow: probe receives parent MFD/platform data, exits if the chip is not configured for torch mode, gets an optional child fwnode from the parent, registers a cleanup action to put it, programs register 0 for torch mode, and registers the class device with max brightness 7.

State and persistence: hardware register 0 contains mode and torch current state. The fwnode reference is lifetime-managed through a devm action. No explicit remove action is required because LED registration is devm-managed.

Dependencies and integration points: TPS6105x MFD platform data and regmap, platform device, LED class extended registration, optional firmware child node.

Risks and test signals: test non-torch-mode probe rejection, fwnode absence, brightness values 0-7 mapping to shifted register bits, mode programming preserving unrelated bits, and cleanup of child fwnode references.
