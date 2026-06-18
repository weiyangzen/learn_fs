# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3697.c

Purpose: TI LM3697 I2C backlight driver with up to two control banks, shared LED string output configuration, optional GPIO/regulator, and TI LMU common brightness/ramp helpers.

Important APIs/types/functions: `struct lm3697` owns regmap, mutex, GPIO/regulator, bank config, and flexible bank array. `struct lm3697_led` stores LED strings, classdev, `ti_lmu_bank`, control bank, enabled brightness, and count. `lm3697_brightness_set()` writes brightness via common helper and toggles bank enable bits. `lm3697_probe_dt()` parses children, brightness resolution, `led-sources`, ramp params, and output config bits. `lm3697_init()` resets/enables hardware and writes ramp settings.

Control flow: probe validates one or two child nodes, allocates state, initializes regmap, parses DT, then initializes hardware. Each child maps `reg` 0/1 to control bank A/B, registers a classdev, and accumulates output routing in `bank_cfg`.

State and persistence: per-bank `enabled` caches nonzero state. Hardware stores output config, ramp, brightness, and enable bits. Remove disables both banks, lowers GPIO, disables regulator if present, and destroys mutex.

Dependencies/integration: I2C regmap, LED class, fwnode properties, regulator/GPIO, `leds-ti-lmu-common.h`.

Risks: regulator is acquired but never enabled in probe/init, yet remove attempts to disable it if present. Output config bit construction depends on `led-sources` values. Duplicate control banks are not explicitly rejected.

Test signals: one/two-bank DTs, LED source routing, brightness resolution and ramp parsing, enable/disable register masks, regulator behavior, duplicate bank handling, and remove cleanup.
