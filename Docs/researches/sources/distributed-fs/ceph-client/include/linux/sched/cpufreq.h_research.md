# sources/distributed-fs/ceph-client/include/linux/sched/cpufreq.h

Purpose: defines the scheduler-to-cpufreq utilization update hook interface used by governors such as schedutil.

Important APIs and types: `SCHED_CPUFREQ_IOWAIT`, `struct update_util_data`, `cpufreq_add_update_util_hook()`, `cpufreq_remove_update_util_hook()`, `cpufreq_this_cpu_can_update()`, `map_util_freq()`, and `map_util_perf()` are exported when CPU frequency support is enabled.

Control flow: cpufreq code registers a per-CPU callback; scheduler utilization updates invoke it with timestamp and flags, including I/O wait boost signals. Mapping helpers translate scheduler utilization/capacity into frequency or performance requests.

State and persistence: hook state is per-CPU runtime callback data owned by cpufreq/scheduler code. No persistent policy is stored here.

Dependencies and integration points: integrates scheduler PELT utilization, CPU capacity, and cpufreq policy updates. Depends on `CONFIG_CPU_FREQ` and cpufreq policy definitions.

Risks and test signals: risks include stale per-CPU hooks during policy teardown, divide-by-zero capacity assumptions, I/O wait flag mishandling, and cross-CPU update races. Test schedutil governor behavior, hotplug, policy changes, I/O wait workloads, and CPU_FREQ disabled builds.
