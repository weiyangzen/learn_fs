# sources/distributed-fs/ceph-client/include/linux/sched/stat.h

Purpose: declares scheduler and fork counters exposed to proc/sys consumers and lightweight runtime queries.

Important APIs and types: `total_forks`, `nr_threads`, per-CPU `process_counts`, `nr_processes()`, `nr_running()`, `single_task_running()`, `nr_iowait()`, `nr_iowait_cpu()`, `sched_info_on()`, and optional `force_schedstat_enabled()` are key.

Control flow: scheduler/fork code updates counters; proc, sysinfo, drivers, and heuristics query approximate values without strict locking.

State and persistence: global and per-CPU counters track live processes, runnable tasks, iowait, forks, and optional schedstats. They are runtime diagnostic/accounting state.

Dependencies and integration points: depends on percpu and Kconfig. Integrates scheduler accounting with `/proc`, sysinfo, and optional schedstats.

Risks and test signals: risks include readers treating approximate unlocked counts as exact, schedstats enablement overhead, and per-CPU aggregation drift. Test proc/stat outputs, fork stress, iowait workloads, schedstats toggles, and CPU hotplug.
