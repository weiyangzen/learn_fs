# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap3-thermal-data.c

## Purpose
`omap3-thermal-data.c` provides OMAP34xx and OMAP36xx one-sensor bandgap configurations and conversion tables.

## Important APIs, Types, and Functions
It defines MPU `temp_sensor_registers`, sensor data with fixed 32768 Hz clock limits, ADC-to-mCelsius tables for OMAP34xx and OMAP36xx, and exported `omap34xx_data` and `omap36xx_data`.

## Control Flow
The data is consumed by `ti-bandgap.c` probe through OF matching. These SoCs are marked `TI_BANDGAP_FEATURE_CLK_CTRL | TI_BANDGAP_FEATURE_UNRELIABLE`, so runtime flow warns about unreliable readings, manages the clock, exposes one CPU thermal zone, and uses single-read conversion when reading temperature.

## State and Persistence Behavior
Static tables and descriptors only. Runtime sensor data is held in `ti_bandgap->regval[id].data` by the common thermal bridge.

## Dependencies and Integration Points
It depends on `ti-thermal.h` and `ti-bandgap.h`; thermal exposure uses `ti_thermal_expose_sensor` and removal uses `ti_thermal_remove_sensor`.

## Risks and Edge Cases
The comments explicitly warn that OMAP3 sensors are inaccurate and poorly placed. The conversion tables clamp high ADC values to 125 C, so policy decisions need conservative interpretation.

## Test Signals
Compile with `CONFIG_OMAP3_THERMAL`, OF match for OMAP34xx/36xx, single-zone registration, temperature read conversion, and warning visibility for unreliable sensors.
