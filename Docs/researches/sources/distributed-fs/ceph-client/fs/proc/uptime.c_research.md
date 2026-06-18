<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/uptime.c -->
## sources/distributed-fs/ceph-client/fs/proc/uptime.c

Purpose: implements `/proc/uptime`, reporting system uptime and accumulated idle time in seconds with two decimal places.

Important APIs and functions: `uptime_proc_show` uses `kcpustat_cpu_fetch`, exported `get_idle_time`, `ktime_get_boottime_ts64`, and `timens_add_boottime`; `proc_uptime_init` registers a permanent single proc entry.

Control flow: each read sums idle nanoseconds over all possible CPUs, obtains boottime uptime, applies time namespace offset, converts idle nanoseconds to seconds/nanoseconds, and formats both values. Init creates and marks the PDE permanent.

State and persistence behavior: no local state persists. Values are live snapshots from scheduler idle accounting and timekeeping.

Dependencies and integration points: depends on `/proc/stat`'s `get_idle_time`, kernel cpustat, time namespaces, procfs, and seq_file. Userspace tools compare it with `/proc/stat` idle counters.

Risks: idle time is summed over possible CPUs, so on multicore systems it can exceed wall-clock uptime. Snapshot is non-atomic across CPUs. Time namespace adjustment affects the uptime component but not the cumulative idle accounting in the same way wall-clock users may expect.

Test signals: compare idle sum with `/proc/stat`; read in time namespaces; CPU hotplug/possible CPU configs; nohz idle fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/uptime.c -->
