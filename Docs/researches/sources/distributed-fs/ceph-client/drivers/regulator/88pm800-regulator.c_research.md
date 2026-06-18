# sources/distributed-fs/ceph-client/drivers/regulator/88pm800-regulator.c

Purpose: registers buck and LDO regulators for the Marvell 88PM800 PMIC through the regulator framework, using the parent 88pm80x MFD power regmap.

Important APIs and data: `struct pm800_regulator_info` wraps a `regulator_desc` and max current. Macros `PM800_BUCK()` and `PM800_LDO()` build descriptors for five bucks and nineteen LDOs. Ops are split into `pm800_volt_range_ops` for buck linear ranges and `pm800_volt_table_ops` for LDO voltage tables. `pm800_get_current_limit()` exposes static current limits. `pm800_regulator_probe()` registers all or board-selected regulators.

Control flow: probe obtains parent `pm80x_chip` and optional platform data. If platform data declares regulators, it validates that non-NULL entries match `num_regulators` and only registers those entries. Otherwise it registers all IDs from `PM800_ID_RG_MAX`. It sets `config.dev` to `chip->dev`, `config.regmap` to `chip->subchip->regmap_power`, and `config.driver_data` to the descriptor wrapper before each registration.

State and persistence: descriptors and voltage tables are static. The driver has no runtime cache beyond regulator devices. Hardware enable and voltage state lives in PMIC registers via regmap.

Dependencies and integration: depends on MFD `88pm80x`, platform driver name `88pm80x-regulator`, regulator core, optional platform init data, OF regulator matching under `regulators`, and Makefile/Kconfig `CONFIG_REGULATOR_88PM800`.

Risks: board-data path indexes `pdata->regulators` and `pm800_regulator_info` by PM800 IDs; mismatched enum/table ordering would register wrong rails. `config.init_data` is not reset to NULL after a selected platform-data regulator, though the loop skips NULL entries in that path. Voltage/current limits are static and require datasheet accuracy.

Test signals: all-regulator registration, board-data subset registration, invalid `num_regulators`, buck voltage range endpoints, LDO table selectors, enable bit operations across enable registers, and current limit reporting.
