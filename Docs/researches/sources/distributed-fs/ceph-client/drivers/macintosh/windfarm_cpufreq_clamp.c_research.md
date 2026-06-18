# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_cpufreq_clamp.c

## Purpose
Provides a Windfarm boolean control named `cpufreq-clamp` that forces CPU 0's cpufreq maximum limit down to the hardware minimum during thermal failures and restores it to the maximum when cleared.

## Important APIs, Types, And Functions
The control ops are `clamp_set()`, `clamp_get()`, `clamp_min()`, and `clamp_max()`. `wf_cpufreq_clamp_init()` obtains CPU 0's `cpufreq_policy`, records `cpuinfo.min_freq` and `cpuinfo.max_freq`, installs a `FREQ_QOS_MAX` request, creates a `wf_control`, and registers it. Exit unregisters the Windfarm control and removes the QoS request.

## Control Flow
Thermal clients call `wf_control_set_max()` on this control to clamp, because its max is `1`; they call `wf_control_set_min()` to unclamp. `clamp_set()` chooses `min_freq` for any nonzero value and `max_freq` for zero, updates the global `clamped` flag, and calls `freq_qos_update_request()`.

## State, Dependencies, And Integration
Global state includes `clamped`, `clamp_control`, the `freq_qos_request`, and cached min/max frequency values. It depends on cpufreq, CPU device discovery, Linux frequency QoS, and Windfarm control registration. Platform controllers treat it as optional but use it aggressively on sensor/fan failures and overtemperature.

## Risks And Test Signals
The driver only tracks CPU 0 policy, so correctness depends on platform cpufreq policy topology matching all relevant CPUs. Probe can defer when cpufreq is not ready. Failure paths must remove the QoS request exactly once. Test signals include module load before/after cpufreq, sysfs control writes of `0` and `1`, thermal-client clamp/unclamp transitions, and checking effective cpufreq max constraints.
