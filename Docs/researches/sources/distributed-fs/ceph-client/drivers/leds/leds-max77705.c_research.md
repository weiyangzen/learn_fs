# sources/distributed-fs/ceph-client/drivers/leds/leds-max77705.c

Purpose: MAX77705 PMIC RGB LED driver supporting single-color and multicolor LED class devices.

Important APIs/types/functions: `struct max77705_led` stores single and multicolor class devices, regmap, and subled metadata. `max77705_rgb_blink()` maps requested delays to hardware blink register fields. `max77705_led_brightness_set()` writes per-channel brightness and enable bits. `max77705_add_led()` parses one LED node, handling RGB child channels or single-channel LEDs.

Control flow: probe creates a regmap over the RGB LED register window on the parent I2C client, then iterates child nodes. RGB nodes allocate subled info from children and register a multicolor class device; non-RGB nodes allocate one subled and register a normal LED. Each LED is turned off after registration. Blink programming writes one global blink register shared by all channels.

State and persistence: brightness and enable are hardware register state; subled brightness is cached in `mc_subled` structures for LED-core calculations. No remove-time explicit shutdown beyond managed resources.

Dependencies and integration: depends on MAX77705 private register definitions, I2C regmap, LED multicolor class, OF/fwnode properties `color` and `reg`, and platform-device MFD binding.

Risks: `max77705_parse_subled()` rejects `reg == 0`, so channel 0 cannot be used despite `MAX77705_LED_NUM_LEDS` being 4. The enable update call appears to pass value and mask arguments in reversed order for `regmap_update_bits()`, a high-risk functional bug. Blink timing math has threshold edge cases and is global, not per LED.

Test signals: single-channel and RGB DT parsing, all channel numbers including 0, brightness register writes and LEDEN bit masks, blink delay boundary values, multicolor intensity calculations, and initial off state.
