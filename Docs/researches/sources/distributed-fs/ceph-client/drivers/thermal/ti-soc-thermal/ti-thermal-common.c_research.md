# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-thermal-common.c

## Purpose
`ti-thermal-common.c` bridges TI bandgap sensors into the generic Linux thermal framework, including thermal-zone operations, hotspot extrapolation, hwmon exposure, asynchronous updates, and optional CPU cooling registration.

## Important APIs, Types, and Functions
`struct ti_thermal_data` stores cpufreq policy, thermal zones, cooling device, bandgap pointer, work item, sensor id, and ownership flags. Public APIs are `ti_thermal_expose_sensor`, `ti_thermal_remove_sensor`, `ti_thermal_report_sensor_temperature`, `ti_thermal_register_cpu_cooling`, and `ti_thermal_unregister_cpu_cooling`.

## Control Flow
Exposure builds or reuses sensor private data, registers a DT thermal zone using `.get_temp` and `.get_trend`, stores the data in bandgap `regval`, programs a 250 ms update interval, and adds hwmon sysfs. Temperature reads get bandgap temperature, optionally subtract PCB zone temperature, choose slope/constant from either zone params or sensor PCB calibration, and return extrapolated hotspot temperature. TALERT reports schedule work that calls `thermal_zone_device_update`. CPU cooling is skipped for DT thermal-sensor-cell deployments and otherwise registers cpufreq cooling for CPU 0.

## State and Persistence Behavior
Per-sensor state is devm-allocated and referenced from `ti_bandgap->regval[id].data`. Work items and cpufreq policies live until driver removal; hwmon is devm-managed.

## Dependencies and Integration Points
It depends on thermal OF registration, thermal hwmon, cpufreq/cpu cooling, optional PCB thermal zone named `"pcb"`, and TI bandgap APIs.

## Risks and Edge Cases
`ti_thermal_report_sensor_temperature` assumes sensor data exists. PCB zone read failures fall back to default slope/offset. CPU cooling registration can defer probe if no cpufreq policy exists.

## Test Signals
Zone registration and hwmon files, hotspot math with and without PCB zone, trend mapping from bandgap trend, TALERT workqueue update, cpufreq cooling register/unregister, and probe-defer behavior.
