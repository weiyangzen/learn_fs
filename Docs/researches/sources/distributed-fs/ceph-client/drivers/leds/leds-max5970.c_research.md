# sources/distributed-fs/ceph-client/drivers/leds/leds-max5970.c

Purpose: LED driver for MAX5970/MAX5978 hot-swap controller indicator outputs.

Important APIs/types/functions: `struct max5970_led` stores parent regmap, LED class device, index, and device pointer. `max5970_led_set_brightness()` updates the LED flash register bit for one LED. `max5970_led_probe()` walks the parent `leds` firmware node and registers one binary LED per valid child `reg`.

Control flow: probe gets the parent MFD regmap and named child node, parses child `reg` and optional `label`, assigns max brightness 1 and default trigger `none`, then registers each LED. Brightness clears a bit for on and sets it for off, matching active-low hardware semantics.

State and persistence: no software cache; state is the parent regmap register. Device-managed LED registration owns cleanup.

Dependencies and integration: depends on MAX5970 MFD definitions, regmap, firmware-node child properties, and LED class.

Risks: probe returns the last registration status, initialized to `-ENODEV`, so a `leds` node with no valid children fails. Active-low semantics are easy to invert in tests or board descriptions. Invalid children are logged and skipped rather than aborting immediately.

Test signals: parent MFD probe with valid/invalid `reg`, on/off bit polarity in `MAX5970_REG_LED_FLASH`, label fallback, and absent regmap or `leds` node.
