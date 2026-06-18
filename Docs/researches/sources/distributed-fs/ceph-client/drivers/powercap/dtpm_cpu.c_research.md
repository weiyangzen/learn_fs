# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_cpu.c

## Purpose
`dtpm_cpu.c` implements the CPU backend for DTPM using CPU frequency policies and the Energy Model. It registers one DTPM leaf per cpufreq performance domain and enforces power limits by applying maximum-frequency QoS constraints.

## Important APIs, Types, And Functions
`struct dtpm_cpu` embeds `struct dtpm`, a `freq_qos_request`, and representative CPU id. Per-CPU `dtpm_per_cpu` maps related CPUs to the same leaf. Backend ops are `set_pd_power_limit()`, `get_pd_power_uw()`, `update_pd_power_uw()`, and `pd_release()`. Hotplug callbacks `cpuhp_dtpm_cpu_online()` and `_offline()` call `dtpm_update_power()`. Setup functions include `__dtpm_cpu_setup()` and `dtpm_cpu_setup()`.

## Control Flow
For a DT CPU node, setup maps the node to a CPU, gets its cpufreq policy, rejects missing or artificial energy models, allocates a backend, assigns all related CPUs to the same `dtpm_cpu`, registers a DTPM leaf, and adds a max-frequency QoS request initialized to the highest EM frequency. Limit setting walks EM performance states until power exceeds the requested limit, applies the previous state's frequency through QoS, and returns the achieved power. Current power estimates choose the EM state at or above current cpufreq and scale by scheduler utilization across online CPUs in the domain.

## State, Persistence, And Dependencies
State includes per-domain DTPM node, QoS request, representative CPU, and per-CPU pointers. Power min/max depend on current online CPUs, so hotplug updates the DTPM tree. Dependencies include cpufreq, CPU hotplug, Energy Model, scheduler utilization, OF CPU node mapping, and DTPM core.

## Integration Points
`dtpm_cpu_ops` is included in `dtpm_subsys.h` under `CONFIG_DTPM_CPU`. It registers CPU hotplug states in its init hook and removes them in exit. Leaf names are `cpuN-cpufreq`.

## Risks
`set_pd_power_limit()` indexes `table[i - 1]`; if a requested limit is below the first performance state's power, `i` remains 0 and this underflows. `update_pd_power_uw()` assumes `em_cpu_get()` succeeds after setup and does not recheck. Hotplug-state cleanup calls `cpuhp_remove_state_nocalls(CPUHP_AP_ONLINE_DYN)`, but dynamic online state ids are normally returned by `cpuhp_setup_state()`; storing the returned id would be safer. Power estimation depends on scheduler utilization snapshots and can be approximate.

## Test Signals
Test EM missing/artificial rejection, related-CPU grouping, min-limit and below-min limit behavior, hotplug online/offline power updates, QoS request add/remove, current power scaling under load, DTPM unregister release cleanup, and cpuhp setup failure unwinding.
