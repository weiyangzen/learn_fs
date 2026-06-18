# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap5-thermal-data.c

## Purpose
`omap5-thermal-data.c` provides OMAP5430 thermal configuration for MPU, GPU, and CORE sensors.

## Important APIs, Types, and Functions
It defines three `temp_sensor_registers`, three `temp_sensor_data` threshold/clock descriptors, `omap5430_adc_to_temp`, and exported `const struct ti_bandgap_data omap5430_data`.

## Control Flow
The data is consumed by bandgap probe. Feature bits select TSHUT threshold configuration, TALERT, counter-delay programming, history-buffer trend support, and freeze-bit reads. The MPU sensor also registers CPU cooling. Temperature reads freeze history where needed and convert ADC code using the OMAP5430 table.

## State and Persistence Behavior
All objects are static configuration. Runtime per-sensor data and saved registers live in `ti_bandgap`.

## Dependencies and Integration Points
It includes `omap5xxx-bandgap.h`, `ti-bandgap.h`, and `ti-thermal.h`; it integrates with thermal OF zones and cpufreq cooling.

## Risks and Edge Cases
The three domains share common control/status registers but use distinct masks and threshold offsets. Counter-delay values must match hardware-supported intervals, and history-buffer trend support depends on freeze/unfreeze correctness.

## Test Signals
OMAP5430 build/probe, three zone registrations, CPU cooling registration for MPU, history-buffer trend reads, TALERT notification, and ADC boundary conversion tests.
