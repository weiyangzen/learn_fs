# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_opp_data.h

## Purpose
`omap_opp_data.h` defines OMAP-specific OPP and voltage-data helper contracts used by OMAP3/4 voltage and OPP table files. It documents that these helpers are for SoC-level initialization only, not board files or PM core logic.

## Important APIs, Types, and Functions
The key type is `struct omap_opp_def`, containing `hwmod_name`, `freq`, `u_volt`, and `default_available`. Macros are `OPP_INITIALIZER()` and `VOLT_DATA_DEFINE()`. The header declares voltage arrays for OMAP34xx, OMAP36xx, OMAP443x, and OMAP446x voltage domains.

## Control Flow
There is no executable flow. Data files instantiate voltage arrays and, in older code paths, OPP definitions using these macros. Later PM/voltage initialization registers the voltage data with the voltage layer and OPP framework users.

## State and Persistence Behavior
The header stores no state. Its consumers create static voltage tables that influence runtime voltage scaling, SmartReflex calibration, and OPP availability.

## Dependencies and Integration Points
It includes `omap_hwmod.h` and `voltage.h`. It integrates with `opp3xxx_data.c`, `opp4xxx_data.c`, voltage-domain registration, SmartReflex eFuse handling, and hwmod naming conventions.

## Risks
Frequency/voltage data must match silicon validation and eFuse layout. Bad nominal voltages or eFuse offsets can cause undervoltage, excess power, unstable frequency scaling, or SmartReflex miscalibration.

## Test Signals
Compile OMAP3/4 PM and voltage code. Runtime signals include correct voltage-domain registration, cpufreq/OPP availability, SmartReflex calibration reads, and stable operation at each advertised OPP under load and suspend/resume.
