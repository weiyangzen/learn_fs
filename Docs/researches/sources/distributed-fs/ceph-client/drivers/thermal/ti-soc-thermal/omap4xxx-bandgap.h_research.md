# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4xxx-bandgap.h

## Purpose
`omap4xxx-bandgap.h` defines register offsets, bitfields, ADC limits, clock limits, and threshold codes for OMAP4430 and OMAP4460/4470 bandgap sensors.

## Important APIs, Types, and Functions
Macros cover OMAP4430 fuse/temp sensor offsets, continuous mode, SOC/EOCZ/DTEMP bits, ADC range `13..107`, fixed 32768 Hz clock, and OMAP4460 control/counter/threshold/TSHUT/status offsets, 10-bit DTEMP, ADC range `530..932`, 1-1.5 MHz clock range, and default hot/cold/shutdown codes.

## Control Flow
There is no executable flow. `omap4-thermal-data.c` maps these macros into the generic TI bandgap structures.

## State and Persistence Behavior
No state is owned; the file is compile-time hardware description.

## Dependencies and Integration Points
It integrates with `ti-bandgap.h` through `temp_sensor_registers` initialization and with OMAP4 Kconfig selection.

## Risks and Edge Cases
OMAP4430 and OMAP4460 use different ADC widths and register blocks. Reusing constants across variants without checking feature differences can corrupt programming or conversion.

## Test Signals
Compile OMAP4 support, validate register programming on 4430 and 4460/4470 hardware, and verify threshold codes correspond to expected millidegree trip behavior.
