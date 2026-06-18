# sources/distributed-fs/ceph-client/drivers/regulator/rt5033-regulator.c

Purpose: registers the Richtek RT5033 PMIC buck, LDO, and safe LDO regulators from an MFD child platform device.

Important APIs/types/functions: `rt5033_buck_ranges` and `rt5033_ldo_ranges` describe selector ranges with a fixed 3.0 V plateau for high selectors. `rt5033_buck_ops` supports enable, voltage selection, and linear-range listing. `rt5033_safe_ldo_ops` supports only fixed voltage listing and enable state. `rt5033_regulator_probe()` loops over the descriptor table.

Control flow: probe obtains `struct rt5033_dev` from the parent, fills `regulator_config` with parent device and regmap, and registers all three descriptors. Any registration failure aborts probe with an error log.

State and persistence: the driver owns no private state. PMIC registers hold enable and selector state. The safe LDO is modeled as a one-voltage regulator.

Dependencies and integration: depends on RT5033 MFD headers and private register definitions, the platform ID `rt5033-regulator`, OF child names under `regulators`, and the regulator framework.

Risks and test signals: descriptor constants must match the MFD register map and enum IDs. SAFE_LDO has no voltage selector, so consumers must treat it as fixed. Tests should cover all rail registrations, selector-to-voltage mapping at range boundaries, enable bits in `RT5033_REG_CTRL`, and failures from parent regmap access.
