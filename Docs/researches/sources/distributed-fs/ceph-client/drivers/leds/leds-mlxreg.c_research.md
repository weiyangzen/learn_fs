# sources/distributed-fs/ceph-client/drivers/leds/leds-mlxreg.c

Purpose: generic Mellanox LED driver driven by `mlxreg_core_platform_data` and a parent regmap.

Important APIs/types/functions: `struct mlxreg_led_data` binds one `mlxreg_core_data` entry to a LED class device and base color. `mlxreg_led_store_hw()` and `mlxreg_led_get_hw()` update/read masked nibbles through regmap. `mlxreg_led_config()` iterates platform entries, applies capability checks, derives color from labels, and registers LEDs.

Control flow: platform probe obtains platform data, initializes a mutex, then configures each LED. If a capability register is present and the bit is absent, that LED is skipped. Brightness writes store base color or off; blink writes base color plus 3 Hz/6 Hz offsets; get maps current code back to LED_FULL/OFF.

State and persistence: LED state is in the parent regmap; no persistent software cache beyond per-LED pointers and generated names. Capability bit mutation clears the capability byte from `data->bit` before using the remaining offset bits.

Dependencies and integration: depends on Mellanox platform data, regmap, LED class, platform bus, and label conventions containing `red`, `orange`, or `amber` to infer color.

Risks: color selection from label strings is heuristic. `mlxreg_led_get_hw()` masks with `~data->mask`, which assumes platform masks are inverse preservation masks rather than direct field masks. Shared blink limitations accept only exact 3 Hz/6 Hz or solid requests.

Test signals: platform data with capability-present/skipped LEDs, mask/bit combinations for low/high nibbles, brightness get/set round trips, blink validation, and generated LED names.
