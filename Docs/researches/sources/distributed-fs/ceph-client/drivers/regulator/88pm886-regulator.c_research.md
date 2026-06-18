# sources/distributed-fs/ceph-client/drivers/regulator/88pm886-regulator.c

Purpose: registers regulators for the Marvell 88PM886 PMIC. It creates a regulator-page I2C dummy client, initializes a regmap for that page, and registers sixteen LDOs plus five buck regulators.

Important APIs and data: `pm886_regulator_regmap_config` defines 8-bit registers/values and max register. Ops are split into table-based `pm886_ldo_ops` and linear-range `pm886_buck_ops`. Voltage tables `pm886_ldo_volt_table1/2/3` and buck ranges define selectors. `pm886_regulators[]` holds descriptors with OF matches, enable registers/masks, voltage select registers, and masks. `pm886_regulator_probe()` performs all registration.

Control flow: probe retrieves the parent `pm886_chip`, creates a dummy I2C device at the regulator page offset, initializes an I2C regmap for that page, sets `rcfg.regmap` and parent device, then iterates over every descriptor and registers it. `dev_err_probe()` is used for deferred or direct errors.

State and persistence: there is no private per-regulator mutable state. The dummy I2C client, regmap, and regulator devices are devm-managed. PMIC register contents hold actual enable/voltage state.

Dependencies and integration: depends on the 88PM886 MFD parent, I2C adapter/addressing, regulator core, regmap I2C, platform driver ID `88pm886-regulator`, Kconfig `REGULATOR_88PM886`, and Makefile object mapping.

Risks: the descriptor array omits explicit `.id` and `.owner`; modern regulator core can work without owner, but missing IDs may affect diagnostics or board constraints expecting numeric IDs. A failed dummy page client prevents all regulators. The code assumes `chip->client->addr + PM886_PAGE_OFFSET_REGULATORS` is valid on the bus.

Test signals: probe with valid and failing dummy I2C page, registration of all 21 rails, OF child matching under `regulators`, LDO selector masks and tables, buck range endpoints, enable masks across LDO_EN1/LDO_EN2/BUCK_EN, and deferred parent readiness.
