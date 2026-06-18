<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/stat.c -->
## sources/distributed-fs/ceph-client/fs/proc/stat.c

Purpose: implements `/proc/stat`, reporting aggregate and per-CPU time accounting, interrupt counts, context switches, boot time, fork count, runnable/blocked process counts, and softirq counters.

Important APIs and functions: exports `get_idle_time` for `/proc/uptime`. Main functions are `get_iowait_time`, `show_irq_gap`, `show_all_irqs`, `show_stat`, `stat_open`, and `proc_stat_init`. Architecture hooks `arch_irq_stat_cpu` and `arch_irq_stat` default to zero if not supplied.

Control flow: `stat_open` sizes the seq buffer based on CPU and IRQ counts. `show_stat` fetches boot time adjusted for time namespaces, accumulates cpustat values over possible CPUs, uses tick/nohz idle and iowait accessors when available, prints aggregate `cpu` and per-online-CPU rows, prints a dense interrupt vector with gaps filled by zeros, and emits process/softirq summaries.

State and persistence behavior: no local state persists. Values are live scheduler, irq, time namespace, and kernel stat snapshots. `get_idle_time` and `get_iowait_time` fall back to cpustat fields for offline or unsupported nohz accounting.

Dependencies and integration points: integrates scheduler cputime accounting, kernel_stat IRQ/softirq counters, IRQ descriptor enumeration, time namespaces, boot-time accounting, procfs permanent entries, and `/proc/uptime`.

Risks: userspace depends on exact field order and units in USER_HZ ticks. Aggregate values are non-atomic and may not equal a sum of later per-CPU reads. IRQ vector gaps must be preserved to keep IRQ-number indexing. Time namespace adjustment affects `btime`.

Test signals: compare CPU counters under workloads, nohz idle, offline CPUs, and virtualization steal/guest time; verify interrupt vector length with sparse IRQs; read from time namespaces; monitor buffer sizing on large CPU/IRQ systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/stat.c -->
