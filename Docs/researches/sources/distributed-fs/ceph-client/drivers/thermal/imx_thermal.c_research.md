# sources/distributed-fs/ceph-client/drivers/thermal/imx_thermal.c

## Purpose
Legacy Freescale/NXP i.MX6/i.MX7 tempmon thermal driver. It reads calibration/temperature-grade data, programs tempmon measurement and alarm registers, registers a thermal zone with passive and critical trips, optionally registers legacy cpufreq cooling, and manages runtime/system PM.

## Important APIs, Types, and Functions
- `struct thermal_soc_data` captures register offsets, masks, shifts, and version-specific fields for i.MX6Q, i.MX6SX, and i.MX7D.
- `struct imx_thermal_data` stores device, cpufreq policy/cooling device, zone, tempmon regmap, calibration coefficients `c1/c2`, trip temperatures, alarm/last temperature, IRQ state, clock, SoC data, and temp grade.
- `imx_init_calib()` derives conversion coefficients from OCOTP calibration.
- `imx_init_temp_grade()` derives max/passive/critical trip temperatures from fuse grade.
- `imx_get_temp()` runtime-resumes hardware, validates sample completion, converts raw measurements, adjusts i.MX6Q alarm between passive and critical trips, and re-enables IRQ when below alarm.
- `imx_set_alarm_temp()` and `imx_set_panic_temp()` program hardware thresholds.
- `imx_change_mode()` manages runtime PM and IRQ enable state.
- `imx_set_trip_temp()` allows changing passive trip temperature and alarm.
- `imx_thermal_register_legacy_cooling()` creates cpufreq cooling if CPU node lacks `#cooling-cells`.
- Probe initializes regmaps, calibration, sensor state, cooling, clock, zone, measurement frequency, alarm, runtime PM, IRQ, and zone enable.

## Control Flow
Probe obtains the tempmon syscon regmap and SoC match data, clears i.MX6SX stale IRQ state, reads calibration/temp-grade from nvmem or legacy `fsl,tempmon-data`, initializes hardware to a known powered-down state, registers legacy cpufreq cooling if needed, enables the thermal clock, registers the thermal zone with two trips, configures 10 Hz measurement and alarm thresholds, powers the sensor, enables runtime PM, enables the thermal zone, and requests the alarm IRQ. Alarm top half disables the IRQ and wakes the thread; the thread updates the thermal zone. Temperature reads resume hardware, convert sample, update dynamic alarm for i.MX6Q, and re-enable IRQ once temperature falls below the programmed alarm.

## State and Persistence
Global static `trips[]` stores passive/critical trip definitions and is modified at probe and by `set_trip_temp()`. Per-device state tracks calibration coefficients, temp grade, alarm temperature, last temp, IRQ enable, cpufreq cooling, and runtime PM state. Hardware alarm/measurement registers persist while powered.

## Dependencies and Integration Points
Depends on syscon/regmap, nvmem or legacy OCOTP regmap, clocks, runtime PM, platform IRQs, thermal core, optional cpufreq cooling APIs, OF thermal/cooling bindings, and device PM callbacks.

## Risks and Edge Cases
- Static `trips[]` is shared across instances, so multiple devices would share mutable trip temperatures.
- `imx_get_temp()` and `imx_set_trip_temp()` return without `pm_runtime_put()` on some error paths after successful resume.
- Legacy cpufreq cooling is only registered when CPU0 lacks `#cooling-cells`.
- Calibration math is fuse-sensitive; invalid or all-ones data fails probe.
- Dynamic alarm switching for i.MX6Q is subtle and tied to passive/critical trip ordering.
- IRQ re-enable depends on reads occurring after temperature drops below alarm.

## Test Signals
Tests should cover nvmem and legacy calibration paths, each SoC register layout, temp-grade trip selection, conversion formulas, passive trip sysfs update bounds, IRQ disable/thread/update/re-enable flow, runtime PM error paths, legacy cpufreq cooling registration, suspend/resume, and i.MX6SX stale interrupt clearing.
