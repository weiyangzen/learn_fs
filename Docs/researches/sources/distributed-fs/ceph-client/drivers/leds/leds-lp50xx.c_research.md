# sources/distributed-fs/ceph-client/drivers/leds/leds-lp50xx.c

Purpose: TI LP5009/5012/5018/5024/5030/5036 I2C multicolor LED driver for RGB modules, supporting individual modules and banked groups.

Important APIs/types/functions: `struct lp50xx_chip_info` abstracts model register layout and module counts. `struct lp50xx_led` wraps `led_classdev_mc` plus bank/number metadata. `lp50xx_brightness_set()` writes per-module or bank brightness and per-color intensity registers. `lp50xx_set_banks()` enables bank control bits. `lp50xx_enable/disable()` handle optional enable GPIO, reset, and chip enable. `lp50xx_probe_dt()` parses multicolor child nodes.

Control flow: probe counts child nodes, allocates state, gets chip info from match data, initializes regmap, enables chip, then for each child parses `reg` count. Multiple `reg` values create a banked LED; one creates an individual module. Grandchildren define RGB color indices and module subregister positions. Each child registers a multicolor classdev.

State and persistence: private state stores chip info and child descriptors; hardware registers store bank config, brightness, and color mix. Mutex serializes brightness writes. Remove disables chip and optional regulator.

Dependencies/integration: I2C regmap, LED multicolor framework, GPIO/regulator, fwnode child/grandchild properties, OF/I2C model tables.

Risks: regulator is acquired after chip enable and never enabled, but remove may disable it. `led_number > num_leds` likely should be `>=` for zero-based modules. Bank setting is global and cumulative; duplicate banks are not rejected. Color grandchildren count is not required to be three.

Test signals: all model register layouts, banked and individual DTs, multicolor intensity writes, enable GPIO timing, reset and disable paths, invalid reg/color child cases, and regulator behavior.
