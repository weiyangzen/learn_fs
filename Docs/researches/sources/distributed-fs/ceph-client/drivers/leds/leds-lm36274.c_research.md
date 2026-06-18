# sources/distributed-fs/ceph-client/drivers/leds/leds-lm36274.c

Purpose: TI LM36274 backlight LED MFD child driver using the shared TI LMU brightness helper.

Important APIs/types/functions: `struct lm36274` stores platform device, classdev, `ti_lmu_bank`, parent regmap, child LED sources, and count. `lm36274_brightness_set()` calls `ti_lmu_common_set_brightness()`. `lm36274_parse_dt()` requires exactly one child node and reads `led-sources`. `lm36274_init()` enables selected strings and the global backlight enable bit.

Control flow: probe obtains parent `struct ti_lmu`, allocates state, parses the single child and fwnode naming data, initializes enable bits, fills `ti_lmu_bank` with 11-bit brightness registers, and registers one extended LED classdev.

State and persistence: enabled LED strings and brightness registers persist in parent LMU hardware. Software state is minimal and device-managed. The child fwnode is manually put after registration or init failure.

Dependencies/integration: TI LMU MFD, regmap, `leds-ti-lmu-common.h`, firmware-node LED naming, OF compatible `"ti,lm36274-backlight"`.

Risks: exactly one child is required; multiple logical banks are not supported. `led-sources` count is not explicitly bounded against `LM36274_MAX_STRINGS` before array read. No remove/shutdown disables backlight explicitly.

Test signals: single-child validation, `led-sources` parsing and enable mask, 11-bit brightness writes through common helper, fwnode reference release, and parent regmap error handling.
