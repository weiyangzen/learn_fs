# sources/distributed-fs/ceph-client/drivers/regulator/rt5120-regulator.c

Purpose: registers six regulators for the Richtek RT5120 PMIC child: four bucks, one LDO, and one external enable rail. Buck1 is adjustable through I2C, while other rails are modeled as fixed-voltage rails with enable, mode, discharge, suspend, and error support as applicable.

Important APIs/types/functions: `struct rt5120_priv` contains the parent regmap and dynamically filled descriptors. `rt5120_fillin_regulator_desc()` builds descriptors by rail ID. `rt5120_parse_regulator_dt_data()` matches DT children and validates fixed-voltage constraints. `rt5120_device_property_init()` configures under/overvoltage hiccup behavior. `rt5120_regulator_get_error_flags()` reads PG/UV/OV and hot-die status.

Control flow: probe obtains the parent regmap, applies board protection properties, parses the `regulators` node, fills fixed voltages from DT for non-buck1 rails, then registers all six regulators. Runtime mode operations update `RT5120_REG_MODECTL`; suspend enable/disable uses `RT5120_REG_SLPCTL`; buck1 suspend voltage writes `RT5120_REG_CH1SLPVID`.

State and persistence: descriptor fields are driver-owned and populated at probe. Hardware registers persist enable, mode, discharge, protection, sleep, and fault state. Non-buck1 fixed voltages are derived from DT constraints rather than read from hardware.

Dependencies and integration: platform child of an MFD with a parent regmap and regulator children named `buck1` through `exten`. Uses OF regulator matching and Richtek-specific DT booleans.

Risks and test signals: `regmap_raw_read(..., &stat, 3)` reads three bytes into an `unsigned int`, making endian/layout assumptions for bit macros spanning bits 1, 9, and 16. Fixed rails reject unequal min/max constraints. Tests should cover DT absence, fixed-voltage validation, hiccup booleans, mode mapping, suspend bits, buck1 voltage limits, and error flag mapping.
