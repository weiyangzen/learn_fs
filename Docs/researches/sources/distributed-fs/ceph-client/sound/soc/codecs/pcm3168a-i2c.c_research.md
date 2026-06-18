# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-i2c.c

Purpose: I2C bus driver for the PCM3168A shared codec core. It creates an I2C regmap, delegates probe/remove to the core, and wires runtime PM for I2C/OF/ACPI matched devices.

Important APIs and functions: `pcm3168a_i2c_probe()` calls `devm_regmap_init_i2c()` with `pcm3168a_regmap` and then `pcm3168a_probe()`. `pcm3168a_i2c_remove()` calls `pcm3168a_remove()`. Matching includes I2C ID `pcm3168a`, ACPI IDs `PCM3168A`/`104C3168`, and OF compatible `ti,pcm3168a`.

Control flow: bus probe only prepares transport; the core owns clocks, regulators, reset GPIO, DAI constraints, controls, regcache, and runtime PM. Driver `.pm` points at `pm_ptr(&pcm3168a_pm_ops)`.

State and persistence: no private I2C state beyond regmap and devres. Runtime state is stored by `pcm3168a_probe()` with `dev_set_drvdata()`.

Dependencies and integration points: Linux I2C, ACPI/OF matching, regmap, ALSA SoC, and `pcm3168a.h`.

Risks: core remove must be called for reset/runtime-PM cleanup; this wrapper does so. I2C-specific failures are limited to regmap initialization.

Test signals: bind via I2C, OF, and ACPI IDs; exercise runtime suspend/resume through the core PM ops; verify component registration and regmap access.
