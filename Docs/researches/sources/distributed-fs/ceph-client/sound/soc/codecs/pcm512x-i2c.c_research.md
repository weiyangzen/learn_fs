# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-i2c.c

Purpose: I2C wrapper for the PCM512x/PCM514x/PCM5242/TAS575x shared codec core. It adapts regmap flags for I2C auto-increment and delegates lifecycle to `pcm512x_probe()`/`pcm512x_remove()`.

Important APIs and functions: `pcm512x_i2c_probe()` copies `pcm512x_regmap`, sets `read_flag_mask` and `write_flag_mask` to `0x80`, initializes `devm_regmap_init_i2c()`, and calls the shared probe. Matching includes I2C IDs, OF compatibles, and ACPI IDs. `.pm` points to `pcm512x_pm_ops`.

Control flow: I2C probe prepares the regmap and shared core; remove calls the core cleanup. The shared core owns regulators, clocks, PLL configuration, DAI ops, controls, DAPM, and runtime PM.

State and persistence: no transport-private state beyond devres regmap. The copied regmap config prevents mutating the global config when enabling I2C auto-increment.

Dependencies and integration points: Linux I2C, ACPI, OF, regmap, and the PCM512x core. Supports `ti,tas5754` and `ti,tas5756` only on I2C in this set.

Risks: I2C auto-increment relies on the MSB flag masks; mistakes here would corrupt multi-register operations. Device-specific TAS575x `force_pll_on` behavior is decided in the shared core using OF node name.

Test signals: probe all IDs, verify multi-register regmap transactions auto-increment, runtime suspend/resume, and PLL/master-mode playback through the shared DAI.
