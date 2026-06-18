# sources/distributed-fs/ceph-client/drivers/mfd/madera-i2c.c

Purpose: this is the I2C transport frontend for Cirrus Logic Madera codecs. It chooses the correct 16-bit and 32-bit regmap configurations for the matched codec type and delegates device bring-up to `madera_dev_init()`.

Important APIs, types, and functions: `madera_i2c_probe()` obtains `type` from `i2c_get_match_data()`, selects codec-specific I2C regmap configs under the relevant `CONFIG_MFD_CS47L*` gate, allocates `struct madera`, initializes both regmaps with `devm_regmap_init_i2c()`, fills type/name/device/IRQ fields, and calls `madera_dev_init()`. `madera_i2c_remove()` calls `madera_dev_exit()`. `madera_i2c_id[]` lists all supported device names.

Control flow: unsupported or not-built-in codec types fail before allocation, with an error naming the missing codec support. Probe creates the 16-bit map first and the 32-bit map second; either failure aborts. Successful probe has no additional bus-specific side effects after entering the shared core.

State and persistence: bus-level state is minimal: a `struct madera` attached as driver data by the shared core and two regmaps over the same I2C device. Persistent codec state is managed by `madera-core.c`.

Dependencies and integration points: I2C, OF match table exported by `madera-core.c`, codec-specific regmap configs declared in `madera.h`, shared PM ops `madera_pm_ops`, and the Madera common core.

Risks: OF and I2C match data must agree with built-in codec support; otherwise probe returns `-EINVAL`. Remove assumes `madera_dev_init()` set driver data. Tests should cover every type-to-regmap selection, disabled Kconfig support, regmap init failures, IRQ propagation, and remove cleanup through `madera_dev_exit()`.
