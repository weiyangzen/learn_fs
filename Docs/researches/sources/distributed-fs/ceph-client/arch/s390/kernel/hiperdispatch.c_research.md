# sources/distributed-fs/ceph-client/arch/s390/kernel/hiperdispatch.c

Purpose: implements s390 hiperdispatch capacity steering. It tracks vertical CPU polarization, steal time, and topology state to decide whether all online cores should advertise high scheduler capacity or only entitled vertical-high/medium cores should do so.

Important APIs and state: exported topology hooks are `hd_reset_state()`, `hd_add_core()`, `hd_enable_hiperdispatch()`, and `hd_disable_hiperdispatch()`. Persistent runtime state is held in `hd_vl_coremask`, `hd_vmvl_cpumask`, `hd_high_capacity_cores`, `hd_entitled_cores`, `hd_online_cores`, `hd_previous_steal`, high/low time counters, and `hd_adjustments`. User controls are `/proc/sys/s390/hiperdispatch`, CPU root sysfs attributes `hiperdispatch/hd_steal_threshold` and `hiperdispatch/hd_delay_factor`, and debugfs counters under `s390/hiperdispatch`.

Control flow: topology rebuild code calls reset/add/enable while holding or coordinating with `smp_cpu_state_mutex`. The delayed work computes averaged steal percentage from vertical-medium/low CPUs and calls `topology_schedule_update()` when the desired high-capacity core count changes. `hd_update_capacities()` then assigns low/high capacity to vertical-low cores in core order.

Dependencies and integration: relies on s390 topology, CPU polarization, scheduler capacity constants, `kcpustat_cpu()`, `system_dfl_wq`, tracepoints, debugfs, sysctl, and CPU sysfs. Capacity reads/writes are serialized with `smp_cpu_state_mutex`; debug counters use `hd_counter_mutex`.

Risks and test signals: sensitive to CPU hotplug order, stale steal-time baselines, division/time units, and extra rebuilds if capacity state races. Test by toggling sysctl/sysfs controls, hotplugging CPUs, checking tracepoints/debugfs counters, and verifying scheduler domains rebuild only when thresholds are crossed.
