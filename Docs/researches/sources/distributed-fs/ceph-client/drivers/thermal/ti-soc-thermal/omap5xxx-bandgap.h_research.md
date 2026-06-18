# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5xxx-bandgap.h

## Purpose
`omap5xxx-bandgap.h` defines OMAP5430 bandgap register offsets, bit masks, ADC range, clock limits, and threshold constants for GPU, MPU, and CORE sensors.

## Important APIs, Types, and Functions
Macros describe per-domain fuse/temp/threshold/TSHUT/history offsets, common control/status offsets, temperature sensor fields, freeze/hot/cold masks, counter mask, threshold masks, ADC range `540..945`, 1-1.5 MHz clocks, and default TSHUT/TALERT codes.

## Control Flow
No runtime flow exists. `omap5-thermal-data.c` consumes the definitions to initialize OMAP5430 descriptors.

## State and Persistence Behavior
No state is stored; it is static hardware metadata.

## Dependencies and Integration Points
It integrates with TI bandgap generic structures and OMAP5 Kconfig selection.

## Risks and Edge Cases
The comment labels CORE offsets as MPU in one heading, so readers must trust macro names and data initialization rather than comments alone. Wrong freeze masks or history offsets would break trend and errata-safe reads.

## Test Signals
Compile OMAP5 support, verify each domain's DTEMP/history registers, alert masks, TSHUT thresholds, and conversion bounds on OMAP5430 hardware.
