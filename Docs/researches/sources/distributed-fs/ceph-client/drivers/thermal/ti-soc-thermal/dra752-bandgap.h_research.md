# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/dra752-bandgap.h

## Purpose
`dra752-bandgap.h` defines DRA752-specific bandgap register offsets, bit masks, ADC conversion range, clock limits, and alert threshold constants.

## Important APIs, Types, and Functions
The file declares macros for two common control/status register groups, five sensor domains (`core`, `iva`, `mpu`, `dspeve`, `gpu`), temperature sensor fields, alert threshold masks, ADC start/end values `540..945`, and per-domain hot/cold thresholds and min/max clock rates.

## Control Flow
There is no executable control flow. `dra752-thermal-data.c` consumes these constants to populate `temp_sensor_registers`, `temp_sensor_data`, and `ti_bandgap_data`.

## State and Persistence Behavior
No state is stored. The macros describe hardware layout and default programming values.

## Dependencies and Integration Points
It depends on `BIT`/`GENMASK` style bit definitions through including context and integrates with the generic TI bandgap structures.

## Risks and Edge Cases
Wrong offsets or masks can program the wrong DRA752 domain or fail to clear/freeze alert state. DRA752 uses split control/status blocks, so copying masks between domains is particularly risky.

## Test Signals
Compile with `CONFIG_DRA752_THERMAL`, probe on DRA7 hardware or emulation, verify each domain reports plausible temperatures and hot/cold alert bits map correctly.
