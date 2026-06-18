# sources/distributed-fs/ceph-client/drivers/regulator/rk808-regulator.c

Purpose: implements the regulator child driver for Rockchip RK80x/RK81x PMIC families. One platform driver supports RK801, RK805, RK806, RK808, RK809, RK816, RK817, and RK818 variants by selecting variant-specific `regulator_desc` tables and common helper ops for bucks, LDOs, boost outputs, and switches.

Important APIs/types/functions: descriptor macros such as `RK8XX_DESC_COM`, `RK806_REGULATOR`, `RK817_DESC`, and switch/boost helpers build large regulator tables. `rk808_regulator_probe()` selects the table based on `struct rk808->variant` from the parent MFD and registers each regulator against the parent regmap. Ops families include `rk801_*`, `rk806_ops_dcdc/nldo/pldo`, `rk808_buck1_2_ops`, `rk816_*`, and `rk817_*`. DVS support is handled by `struct rk808_regulator_data` and `rk808_regulator_dt_parse_pdata()`.

Control flow: probe attaches the child OF node to the parent, fetches the regmap, allocates driver data, optionally parses RK808 DVS GPIOs and polarity bits, chooses descriptors, then loops through `devm_regulator_register()`. Runtime control is largely regmap-backed: enable bits, voltage selectors, suspend selectors, ramp tables, and mode bits are written through regulator helpers or small variant adapters. RK806 has custom ramp handling because the DCDC ramp selector MSB lives in separate registers. RK808 DCDC1/2 can switch between ON and DVS voltage registers by toggling GPIOs; without GPIOs, voltage increases are stepped to reduce overshoot.

State and persistence: persistent hardware state lives in PMIC registers. The only driver-owned state is the optional DVS GPIO array. Suspend voltage and enable/disable settings are programmed into PMIC sleep registers and survive until overwritten or reset.

Dependencies and integration: depends on `linux/mfd/rk808.h` definitions, the parent MFD regmap, OF regulator nodes, optional `dvs` GPIOs, and the regulator framework. Probe is forced synchronous, which likely reflects consumers needing these rails early.

Risks and test signals: table/register drift across variants is the largest risk. Sleep-enable polarity differs by family, write-mask enable registers need correct `enable_val`/`disable_val`, and DVS GPIO polarity changes both register programming and selected voltage source. Test signals include compile coverage for all variants, DT matching of every regulator node, voltage selector boundary tests, suspend voltage/mode writes, RK806 ramp MSB writes, RK808 DVS toggling, and missing/invalid variant handling.
