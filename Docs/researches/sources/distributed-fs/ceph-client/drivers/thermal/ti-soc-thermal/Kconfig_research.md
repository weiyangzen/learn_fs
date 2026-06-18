# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Kconfig

## Purpose
This Kconfig file controls build-time selection for the Texas Instruments SoC bandgap thermal driver and per-family support.

## Important APIs, Types, and Functions
Symbols are `TI_SOC_THERMAL`, `TI_THERMAL`, `OMAP3_THERMAL`, `OMAP4_THERMAL`, `OMAP5_THERMAL`, and `DRA752_THERMAL`. Family symbols depend on `TI_SOC_THERMAL` plus architecture or `COMPILE_TEST`.

## Control Flow
There is no runtime flow. User-selected symbols determine whether the core driver, generic thermal framework bridge, and per-SoC data files are compiled.

## State and Persistence Behavior
No runtime state. Kconfig choices persist in kernel configuration and drive object composition.

## Dependencies and Integration Points
The symbols feed `ti-soc-thermal/Makefile` and conditional externs in `ti-bandgap.h`. `TI_THERMAL` enables thermal-zone exposure and CPU cooling integration.

## Risks and Edge Cases
Selecting a family without matching data would produce null match data or missing objects, so symbol dependencies must stay aligned with OF match entries and Makefile fragments. OMAP3 help text warns about unreliable sensors.

## Test Signals
Kernel allmodconfig/allyesconfig and COMPILE_TEST builds for each family, plus DT probe tests for enabled compatibles.
