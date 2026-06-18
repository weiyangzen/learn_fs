# sources/distributed-fs/ceph-client/drivers/regulator/atc260x-regulator.c

Purpose: platform child regulator driver for Actions Semi ATC2603C and ATC2609A PMICs, exposing DCDC, LDO, switch-LDO, bypass, discharge, fixed, and range-based rails.

Important APIs/types/functions: descriptor macro families build `atc2603c_reg[]`, `atc2603c_reg_dcdc2_ver_b`, and `atc2609a_reg[]`. Ops tables select generic regmap helpers, pickable ranges, bypass, active discharge, or no ops. `struct atc260x_regulator_data` stores fixed voltage ramp times used by `atc260x_dcdc_set_voltage_time_sel()` and `atc260x_ldo_set_voltage_time_sel()`.

Control flow: probe gets the parent `struct atc260x`, allocates timing data, selects descriptor table by `ic_type`, applies ATC2603C revision-B DCDC2 override when needed, and registers every descriptor against the parent regmap.

State and persistence: runtime state is only the devm timing structure. Voltage, enable, bypass, and discharge state are PMIC register bits. Voltage ramp time is a conservative constant per regulator class/chip, returned only when selector increases.

Dependencies and integration: depends on ATC260x MFD register definitions, regmap, platform bus, OF regulator matching embedded in descriptors, and regulator core helpers.

Risks and test signals: large macro-generated descriptors make bitfield mistakes easy. LDO12 has no ops and only a fixed voltage, so consumers cannot enable/disable it through this driver. Tests should cover both chip families, ATC2603C revision-B DCDC2, switch-LDO inverted enable/discharge, pickable LDO ranges on ATC2609A, ramp-time reporting, and unsupported `ic_type`.
