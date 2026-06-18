<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/softirqs.c -->
## sources/distributed-fs/ceph-client/fs/proc/softirqs.c

Purpose: implements `/proc/softirqs`, exposing per-CPU counters for each softirq vector.

Important APIs and functions: `show_softirqs` formats the table using `softirq_to_name`, `for_each_possible_cpu`, and `kstat_softirqs_cpu`; `proc_softirqs_init` creates a permanent single proc file.

Control flow: each read prints a CPU header row, then one row per `NR_SOFTIRQS` vector with fixed-width per-possible-CPU counters. Init creates and marks the proc entry permanent.

State and persistence behavior: no local state is stored. Counters are live kernel softirq statistics and can change during output.

Dependencies and integration points: depends on kernel softirq names/statistics, procfs, and seq_file. It complements aggregate softirq data in `/proc/stat`.

Risks: output is not atomic across CPUs, and CPU hotplug can change online status while possible CPUs remain stable. Formatting is consumed by monitoring tools.

Test signals: read under network/block/timer softirq load; compare aggregates with `/proc/stat`; CPU hotplug systems; verify all configured softirq names appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/softirqs.c -->
