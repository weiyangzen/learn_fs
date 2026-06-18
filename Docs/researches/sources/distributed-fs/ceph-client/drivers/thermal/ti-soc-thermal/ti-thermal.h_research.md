# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal.h

## Purpose
`ti-thermal.h` declares TI thermal framework bridge functions and shared thermal constants for OMAP/DRA hotspot extrapolation and trip planning.

## Important APIs, Types, and Functions
It defines PCB gradient constants for OMAP4430/4460/4470/5430 and DRA752, common trip temperatures `OMAP_TRIP_COLD`, `OMAP_TRIP_HOT`, `OMAP_TRIP_SHUTDOWN`, trip count/step, and `FAST_TEMP_MONITORING_RATE`. Under `CONFIG_TI_THERMAL` it declares expose/remove/report/cooling APIs; otherwise it provides success-returning stubs.

## Control Flow
No runtime flow exists in the header. It lets per-SoC data files assign callbacks even when the generic thermal bridge is optional.

## State and Persistence Behavior
No state is stored here; constants are compile-time calibration and policy defaults.

## Dependencies and Integration Points
It includes `ti-bandgap.h` and is used by every TI SoC data file plus `ti-thermal-common.c`.

## Risks and Edge Cases
Disabled stubs mean the hardware bandgap driver can probe without exposing sensors to the thermal framework. Calibration constants directly affect reported hotspot temperatures and policy behavior.

## Test Signals
Build with `CONFIG_TI_THERMAL` enabled/disabled, verify callback presence in per-SoC data, and validate hotspot calculations against expected calibration constants.
