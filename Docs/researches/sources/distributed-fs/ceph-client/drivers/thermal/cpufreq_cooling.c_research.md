# sources/distributed-fs/ceph-client/drivers/thermal/cpufreq_cooling.c

## Purpose
Generic thermal cooling-device implementation for cpufreq policies. It maps cooling states to maximum CPU frequencies, applies the limit through freq QoS, and when the Energy Model is available exposes power-actor callbacks used by the power allocator governor.

## Important APIs, Types, and Functions
- `struct cpufreq_cooling_device` stores current cooling state, max state, EM reference, cpufreq policy, ops, optional idle-time accounting, and `freq_qos_request`.
- Registration exports: `cpufreq_cooling_register()`, `of_cpufreq_cooling_register()`, and `cpufreq_cooling_unregister()`.
- Core callbacks: `cpufreq_get_max_state()`, `cpufreq_get_cur_state()`, and `cpufreq_set_cur_state()`.
- `get_state_freq()` maps thermal state to frequency using EM states when present or the cpufreq table sorted direction otherwise.
- Power allocator callbacks under `CONFIG_THERMAL_GOV_POWER_ALLOCATOR`: `cpufreq_get_requested_power()`, `cpufreq_state2power()`, and `cpufreq_power2state()`.
- Helper functions map frequency/state/power: `get_level()`, `cpu_freq_to_power()`, `cpu_power_to_freq()`, `get_dynamic_power()`, and `em_is_sane()`.

## Control Flow
Registration validates the cpufreq policy, CPU device, and frequency table, allocates private state, calculates `max_level`, installs thermal cooling ops, validates optional EM alignment, and adds a `FREQ_QOS_MAX` request initialized to the frequency for state 0. It then registers a named thermal cooling device, optionally bound to the CPU OF node. Setting a cooling state validates bounds, computes the target frequency, updates the freq QoS max request, and records the new state.

When IPA is enabled and EM is sane, power callbacks estimate current requested power from current frequency and CPU load, convert cooling states to 100-percent-load power, and convert power budgets back to cooling states. SMP uses scheduler utilization; non-SMP tracks idle-time deltas.

## State and Persistence
State is in-memory and tied to the cooling device lifecycle. The effective throttle persists in the cpufreq policy's freq QoS constraints until updated or unregistered. `last_load` is a rolling input for power-to-state conversion.

## Dependencies and Integration Points
Integrates with cpufreq policy/table APIs, freq QoS, thermal cooling devices, OF CPU nodes with `#cooling-cells`, Energy Model/OPP data, scheduler CPU utilization or idle-time accounting, and thermal tracepoints.

## Risks and Edge Cases
- Unsorted cpufreq tables are rejected unless a valid EM is used.
- EM must span exactly `policy->related_cpus` and have the same number of states as cpufreq levels; mismatches disable power callbacks or fail in non-EM sorted-table cases.
- `cpufreq_get_requested_power()` approximates requested power from recent current frequency and load, not hypothetical unconstrained demand.
- `last_load` is normalized to at least one in `power2state()`, so stale/zero load can bias budgets.
- State-to-frequency mapping assumes stable policy frequency table or EM state count after registration.

## Test Signals
Tests should verify state/frequency mapping for ascending and descending tables, rejection of unsorted tables, freq QoS add/update/remove behavior, OF registration only when `#cooling-cells` exists, EM mismatch diagnostics, power callback conversions, offline CPU load handling, and unregister cleanup.
