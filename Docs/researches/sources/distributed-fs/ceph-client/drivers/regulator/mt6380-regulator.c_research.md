# sources/distributed-fs/ceph-client/drivers/regulator/mt6380-regulator.c

Purpose: implements the MediaTek MT6380 PMIC regulator platform driver for three buck rails and five LDO/fixed rails.

Important APIs/types/functions: `struct mt6380_regulator_info` carries a `regulator_desc`, optional hardware control selector register, and mode-set register/mask. Macros `MT6380_BUCK`, `MT6380_LDO`, and `MT6380_REG_FIXED` define the descriptor table. Ops `mt6380_volt_range_ops`, `mt6380_volt_table_ops`, and `mt6380_volt_fixed_ops` share regmap enable/disable and mode callbacks, with range, table, or fixed voltage listing.

Control flow: probe fetches the parent regmap and registers all `MT6380_MAX_REGULATOR` descriptors. Buck voltages are linear ranges; LDOs use small voltage tables; fixed VPHYLDO reports a single 1.8 V rail. `mt6380_regulator_set_mode()` maps NORMAL to AUTO and FAST to FORCE_PWM by writing each rail's mode bit. `mt6380_regulator_get_mode()` reads back and maps the same bit.

State and persistence: rail enable bits, voltage selectors, and mode bits persist in PMIC registers. The driver has no dynamic state beyond the static descriptor table and per-rdev driver-data pointer. No shutdown or remove programming is performed.

Dependencies and integration: depends on a parent MFD/platform regmap, `linux/regulator/mt6380-regulator.h` IDs, DT compatible `mediatek,mt6380-regulator`, and regulator core helpers. Unlike many MediaTek PMIC drivers here, descriptors do not set `regulators_node`, so matching relies on the core's default node search behavior.

Risks and test signals: probe does not check for a missing parent regmap before passing it to regulator registration. Fixed regulator descriptors set `min_uV` but not `fixed_uV`, while using `regulator_list_voltage_linear`. Mode callbacks are exposed for LDOs and fixed rails as well as bucks. Test missing parent regmap, all rail selector masks and tables, mode set/get on every rail, DT matching behavior, and fixed VPHYLDO voltage reporting.
