<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c

Purpose: implements regulator support for Samsung S2MPA01 PMICs, exposing 26 LDOs and 10 bucks from the Samsung MFD parent as regmap-backed voltage regulators.

Important APIs/types/functions: `struct s2mpa01_info` tracks grouped ramp-delay state for buck rails. `get_ramp_delay()` converts a requested microvolt-per-microsecond delay into the PMIC two-bit selector. `s2mpa01_regulator_set_voltage_time_sel()` computes transition time based on the rail's configured ramp group. `s2mpa01_set_ramp_delay()` programs ramp enable bits and ramp selector fields in `S2MPA01_REG_RAMP1`/`RAMP2`. `s2mpa01_ldo_ops` and `s2mpa01_buck_ops` define common regulator ops, with buck ops adding custom ramp support.

Control flow: probe obtains the parent `sec_pmic_dev`, allocates ramp-delay state, builds a `regulator_config` using the parent device and PMIC regmap, then registers every descriptor in static order. Descriptor macros compute LDO and buck voltage selector, enable, min voltage, step, and ramp defaults from Samsung PMIC register definitions. Runtime voltage changes go through regulator core helpers; ramp changes update both software state and PMIC ramp registers before voltage transition timing is reported.

State and persistence: software state holds the maximum selected ramp delay for shared ramp groups such as buck2/4, buck1/6, and buck8/9/10. Hardware state lives in PMIC voltage, enable, and ramp registers. There is no persistent state outside the PMIC and no explicit suspend handling in this file.

Dependencies and integration: depends on the Samsung MFD core, `linux/mfd/samsung/s2mpa01.h`, regmap, platform devices, and regulator OF child nodes named `LDO#` and `BUCK#` under `regulators`. The platform ID is `s2mpa01-pmic` and probe is asynchronous.

Risks and test signals: ramp groups share hardware fields, so setting a lower ramp on one rail may retain a larger previously requested group value. `get_ramp_delay()` clamps values above the supported selector range. Test signals include all regulator registrations, buck ramp enable/disable for buck1-4, shared ramp behavior for grouped bucks, voltage transition timing, invalid regulator IDs, and standard LDO/buck voltage and enable operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/s2mpa01.c -->
