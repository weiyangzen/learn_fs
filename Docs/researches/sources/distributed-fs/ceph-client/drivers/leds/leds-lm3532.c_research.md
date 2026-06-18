# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3532.c

Purpose: DT/regmap backlight LED driver for TI LM3532 with up to three control banks, optional ALS control, enable GPIO, regulator, ramp settings, and LED-string assignment.

Important APIs/types/functions: `struct lm3532_data` owns GPIO, regulator, regmap, mutex, ALS data, ramp config, and flexible LED array. `struct lm3532_led` describes one control bank. `lm3532_brightness_set()` enables/disables a bank and writes zone target brightness. `lm3532_init_registers()` maps LED strings, writes mode/full-scale current/ramp registers. `lm3532_parse_node()` parses child fwnodes.

Control flow: probe counts child LEDs, initializes regmap and mutex, then parses top-level enable/regulator/ramp properties and each child `reg`, `ti,led-mode`, current, and `led-sources`. ALS children trigger top-level ALS parsing and hardware zone configuration. Each child is registered and then initialized.

State and persistence: enabled flag is per bank; mutex protects register transitions. Regmap cache holds defaults. Hardware retains output mapping, ramp, ALS, and brightness registers until reset.

Dependencies/integration: I2C regmap, GPIO descriptor, regulator, firmware-node child properties, LED class extended registration, ALS-related DT properties.

Risks: regulator is optional but `lm3532_led_enable()` unconditionally calls `regulator_enable()`, so missing regulator can lead to NULL dereference if a bank is enabled. Some invalid child configurations `continue` rather than fail, leaving index handling subtle. ALS parsing can allocate only one shared ALS data instance.

Test signals: child parsing for all control banks, regulator-present/absent behavior, ALS mode configuration, ramp index rounding, LED string output config masks, brightness OFF/ON transitions, and error paths during per-child registration.
