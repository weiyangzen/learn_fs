# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp3xxx_data.c

## Purpose
`opp3xxx_data.c` defines OMAP34xx and OMAP36xx voltage data tables for the voltage layer and SmartReflex calibration. It maps nominal voltages to control-module eFuse offsets and SmartReflex error parameters.

## Important APIs, Types, and Functions
The exported arrays are `omap34xx_vddmpu_volt_data[]`, `omap34xx_vddcore_volt_data[]`, `omap36xx_vddmpu_volt_data[]`, and `omap36xx_vddcore_volt_data[]`. They are built with `VOLT_DATA_DEFINE()` and include sentinel zero rows.

## Control Flow
There are no local functions. Voltage-domain initialization consumes these arrays after PMIC registration and SoC identification, using nominal voltage entries and eFuse offsets to configure voltage scaling and SmartReflex.

## State and Persistence Behavior
The file contains immutable voltage descriptors. Runtime effects include voltage-domain state, SmartReflex calibration data, and PMIC register programming.

## Dependencies and Integration Points
It depends on `soc.h`, `control.h`, `omap_opp_data.h`, and `pm.h`. It integrates with OMAP3 voltage domains `mpu_iva` and `core`, TWL4030 PMIC support, SmartReflex, and OPP/cpufreq consumers.

## Risks
Wrong voltage values or eFuse offsets can destabilize OMAP3 silicon or break adaptive voltage scaling. OMAP3630 high OPP entries are especially sensitive because they run near upper voltage limits.

## Test Signals
Boot OMAP34xx/36xx boards, verify voltage table registration, eFuse reads, SmartReflex initialization, and stable operation at each CPU/CORE OPP. Run suspend/resume and CPU load tests while monitoring voltage transitions.
