# sources/distributed-fs/ceph-client/drivers/thermal/hisi_thermal.c

## Purpose
HiSilicon thermal sensor driver for HI6220 and HI3660-style tsensors. It abstracts SoC-specific register layouts and temperature conversion through ops, registers OF thermal zones, programs passive-threshold alarms, and handles alarm IRQs.

## Important APIs, Types, and Functions
- `struct hisi_thermal_sensor` stores parent data, thermal zone, IRQ name, sensor id, and passive threshold.
- `struct hisi_thermal_ops` defines get/enable/disable/irq/probe hooks per SoC.
- `struct hisi_thermal_data` stores ops, sensor array, platform device, clock, base registers, and sensor count.
- Conversion helpers implement HI6220 and HI3660 step-to-temperature and temperature-to-step formulas.
- HI6220/HI3660 helpers program lag, threshold, interrupt enable/clear, reset, and sensor selection fields.
- `hisi_thermal_register_sensor()` registers OF zone and records first passive trip as `thres_temp`.
- `hisi_thermal_alarm_irq_thread()` clears hardware interrupt, reads temperature, logs alarm/stop, and updates zone when still above threshold.
- Probe maps registers, runs SoC probe, registers each sensor, requests IRQs, enables hardware, and enables thermal zones.

## Control Flow
OF match chooses HI6220 or HI3660 ops. The SoC probe allocates one sensor and sets its hardware id/IRQ name. Generic probe maps MMIO, registers each sensor as a thermal zone, scans trips for the passive threshold, requests the platform IRQ, enables the sensor using SoC register programming, and enables the zone. The IRQ thread clears the alarm, reads current temperature, and updates the thermal zone if temperature is still above the configured passive threshold.

## State and Persistence
State includes the chosen ops, sensor id, threshold temperature from DT thermal trips, and clock state for HI6220. Hardware lag/threshold/interrupt registers persist until disabled or reprogrammed. Suspend disables sensors; resume re-enables them.

## Dependencies and Integration Points
Depends on OF thermal zones, platform IRQ, MMIO, common clock for HI6220, and thermal PM callbacks. It uses passive trip definitions from DT as hardware alarm thresholds.

## Risks and Edge Cases
- Probe retrieves `platform_get_irq(pdev, 0)` inside the sensor loop, so multi-sensor expansion would need per-sensor IRQ handling.
- `hisi_trip_walk_cb()` leaves `thres_temp` zero if no passive trip exists, causing threshold programming at 0 mC.
- `hisi_thermal_resume()` ORs return values, which may obscure the first specific failure.
- Only one sensor is currently configured per supported SoC despite constants for more sensors.

## Test Signals
Tests should cover HI6220 and HI3660 conversion formulas, passive trip discovery, missing passive trip behavior, IRQ clear/update path above and below threshold, suspend/resume register operations, and clock enable/disable failures.
