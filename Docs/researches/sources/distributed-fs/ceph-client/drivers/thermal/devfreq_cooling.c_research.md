# sources/distributed-fs/ceph-client/drivers/thermal/devfreq_cooling.c

## Purpose
Generic thermal cooling-device implementation for devfreq-managed devices. It caps device frequency through dev PM QoS, maps cooling states to OPP/EM frequencies, and optionally exposes power-actor callbacks for the IPA power allocator governor.

## Important APIs, Types, and Functions
- `struct devfreq_cooling_device` stores the thermal cdev, ops, devfreq pointer, current state, fallback frequency table, max state, optional power ops, utilization scaling, capped state, QoS request, and Energy Model domain.
- Core callbacks: `devfreq_cooling_get_max_state()`, `devfreq_cooling_get_cur_state()`, and `devfreq_cooling_set_cur_state()`.
- Power callbacks: `devfreq_cooling_get_requested_power()`, `devfreq_cooling_state2power()`, and `devfreq_cooling_power2state()`.
- Helpers: `get_perf_idx()`, `get_voltage()`, `_normalize_load()`, and `devfreq_cooling_gen_tables()`.
- Exported registration APIs: `of_devfreq_cooling_register_power()`, `of_devfreq_cooling_register()`, `devfreq_cooling_register()`, `devfreq_cooling_em_register()`, and `devfreq_cooling_unregister()`.

## Control Flow
Registration allocates state, installs base callbacks, obtains a non-artificial Energy Model if present, and enables IPA power callbacks when available. Without EM it builds a descending frequency table from OPPs for backward compatibility. It adds a `DEV_PM_QOS_MAX_FREQUENCY` request, registers a named thermal cooling device, and returns it. Setting state maps the state to an EM performance index or fallback frequency and updates the PM QoS max frequency.

Power accounting reads `df->last_status` under the devfreq lock. With `get_real_power`, it looks up voltage and lets the device model compute real power, then adjusts `res_util`. Without real power, it normalizes busy time and scales EM power by utilization. Power-to-state scales the requested budget back to estimated full-use power and chooses the first EM state within budget.

## State and Persistence
The current cooling state, capped state, resource-utilization correction, fallback frequency table, and PM QoS request are in memory. The effective cap persists in the device PM QoS framework until changed or unregistered.

## Dependencies and Integration Points
Integrates with devfreq, OPP, Energy Model, dev PM QoS, thermal OF cooling-device registration, optional `devfreq_cooling_power` callbacks, and thermal tracepoints.

## Risks and Edge Cases
- OPP additions/removals after registration are explicitly not handled.
- `get_perf_idx()` requires exact EM frequency match to `current_frequency / 1000`; mismatch returns `-EAGAIN`.
- Fallback frequency table is only for non-IPA cooling and must be freed on failure/unregister.
- Real-power path depends on valid voltage lookup and device-specific power model.
- `devfreq_cooling_unregister()` unregisters EM perf domain even if this file did not create it, relying on EM API behavior.

## Test Signals
Tests should cover EM and non-EM registration paths, OPP table generation order, PM QoS update values, power callback calculations with normalized load, real-power error paths, unregister cleanup, and `devfreq_cooling_em_register()` behavior when EM registration fails but cooling registration succeeds.
