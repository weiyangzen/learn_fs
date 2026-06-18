<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c

Purpose: provides the I2C transport binding for Arizona-class codecs. It selects a chip-specific I2C regmap configuration from match data and delegates all common initialization and teardown to the Arizona core.

Important APIs and functions: `arizona_i2c_probe` handles allocation and regmap setup; `arizona_i2c_remove` calls `arizona_dev_exit`. Match tables cover `wm5102`, `wm5110`, `wm8280`, `wm8997`, `wm8998`, and `wm1814` I2C IDs and OF compatibles.

Control flow: probe obtains match data via `i2c_get_match_data`, selects the appropriate regmap config only if matching Kconfig support is enabled, allocates `struct arizona`, initializes `devm_regmap_init_i2c`, stores type/device/IRQ, and calls `arizona_dev_init`. Remove fetches the core state from device driver data and tears it down.

State and persistence: this file owns only the bus-specific allocation and I2C regmap lifetime. Persistent codec state, PM state, IRQ domains, child devices, and regulators are owned by `arizona-core.c`.

Dependencies and integration points: depends on I2C, regmap, PM runtime hooks through `arizona_pm_ops`, OF/I2C matching, and the regmap config symbols declared in the local Arizona header. It has a soft dependency on `arizona_ldo1`.

Risks: unsupported Kconfig combinations produce `-EINVAL` even if the hardware is present. The I2C path does not support WM1831/CS47L24, which are SPI-only in this file. Correct IRQ number and reset/regulator descriptors must come from board firmware for core initialization to succeed.

Test signals: I2C modalias and OF matching for each supported type, failure when a disabled Kconfig variant is matched, regmap initialization errors, shared core probe/remove behavior, runtime PM callbacks through the I2C driver, and module soft dependency ordering with LDO1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c -->
