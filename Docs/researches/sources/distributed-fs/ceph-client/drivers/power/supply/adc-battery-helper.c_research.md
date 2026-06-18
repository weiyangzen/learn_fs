# sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.c

## Purpose
`adc-battery-helper.c` is a reusable helper for simple ADC/fuel-gauge drivers that can measure battery voltage and current accurately but need software OCV/capacity estimation. It exports common power-supply properties, polling work, status/capacity calculation, internal-resistance adaptation, external-power handling, and suspend/resume helpers.

## Important APIs, Types, And Functions
- `adc_battery_helper_properties[]` exports the common property list: status, voltage now, voltage OCV, current now, capacity, present, and scope.
- `adc_battery_helper_init()` wires the helper to a registered power supply, a combined voltage/current getter, optional charge-finished GPIO, validates battery-info requirements, seeds internal resistance, and starts polling.
- `adc_battery_helper_work()` is the core polling loop: samples voltage/current, computes OCV, updates moving averages, determines supplied/status/capacity, optionally updates internal resistance, reschedules itself, and notifies on status changes.
- `adc_battery_helper_get_property()` returns helper-backed properties while holding the helper mutex and calls the driver getter for fresh `VOLTAGE_NOW`/`CURRENT_NOW`.
- `adc_battery_helper_external_power_changed()` accelerates the next poll after a settle delay.
- `adc_battery_helper_suspend()` and `adc_battery_helper_resume()` stop and restart helper work.

## Control Flow
Initialization validates that `battery_info` contains factory internal resistance, constant charge voltage, and an OCV table. It seeds the resistance moving average from battery info and immediately starts work. The work function samples current and voltage via the driver callback, estimates OCV as `volt - current * resistance`, averages OCV over an eight-sample window, reads supplied state, computes status, computes capacity from OCV unless full, then uses current/voltage deltas to refine internal resistance when conditions are suitable. It polls every five seconds for the initial 30 polls, then every 30 seconds.

## State And Persistence
State is held in `struct adc_battery_helper`: OCV and resistance moving-average arrays, indexes, poll counters, current voltage/current, capacity, status, and supplied flag. There is no persistent storage; all estimates restart from battery-info factory resistance on probe/resume. Work is devm-managed and canceled automatically on device teardown.

## Dependencies And Integration Points
The helper depends on the power-supply framework, `power_supply_batinfo_ocv2cap()`, `power_supply_am_i_supplied()`, optional charge-finished GPIO, `system_percpu_wq`, devm mutex/work helpers, and a client-supplied `get_voltage_and_current_now()` callback. Known users in the same directory include `ug3105_battery.c` and `intel_dc_ti_battery.c`.

## Risks
- The header requires `struct adc_battery_helper` to be the first member of client driver data when using callbacks directly; violating this causes invalid casts in get-property and PM helpers.
- The helper calls the client getter under `help->lock`; client callbacks must avoid re-entering helper property paths or creating lock inversions.
- OCV calculation assumes current sign and resistance units match helper expectations. A client with reversed current polarity will bias capacity.
- Internal resistance adaptation relies on current/voltage deltas and outlier rejection. Devices with noisy ADCs may never update resistance or may drift slowly.
- Work reschedules even after a sample read failure, but notification only tracks status changes, not capacity changes; clients needing capacity-change uevents may need extra signaling.

## Test Signals
- Unit-style tests with fake getter values should cover charging, discharging, not charging, full via GPIO, full via OCV threshold, low-battery resistance-skip, charger plug/unplug skip, and getter failures.
- Validate moving average behavior for OCV and resistance windows, initial fast polling versus steady polling, and external-power settle timing.
- Probe validation should fail when battery-info resistance, constant charge voltage, or OCV table is absent.
- Confirm suspend cancels work and resume restarts with reset OCV averaging.
