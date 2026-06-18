# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/omap4-thermal-data.c

## Purpose
`omap4-thermal-data.c` supplies OMAP4430, OMAP4460, and OMAP4470 bandgap configurations for a single MPU/CPU thermal sensor.

## Important APIs, Types, and Functions
The file defines register descriptors, threshold/clock data, conversion tables, and exported `omap4430_data`, `omap4460_data`, and `omap4470_data`. OMAP4460/4470 include TALERT, TSHUT, counter, mode, power-switch, and clock-control features.

## Control Flow
No functions run here. Probe selects the matching `ti_bandgap_data`, configures clocks and thresholds, registers CPU cooling where configured, exposes the CPU thermal zone, and reports TALERT events through `ti_thermal_report_sensor_temperature`.

## State and Persistence Behavior
Static descriptors and conversion tables only. Runtime state is stored by the bandgap and thermal common layers.

## Dependencies and Integration Points
It depends on `omap4xxx-bandgap.h`, `ti-bandgap.h`, and `ti-thermal.h`. CPU cooling uses `ti_thermal_register_cpu_cooling` and unregister counterpart.

## Risks and Edge Cases
OMAP4430 is continuous-mode-only and lacks the richer alert/shutdown programming used by OMAP4460/4470. ADC range differences must stay aligned with table sizes and conversion bounds.

## Test Signals
Build/probe each compatible, verify CPU zone and cpufreq cooling registration, TALERT/TSHUT behavior on OMAP4460/4470, and ADC conversion near table boundaries.
