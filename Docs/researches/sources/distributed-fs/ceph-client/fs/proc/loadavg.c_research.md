<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/loadavg.c -->
## sources/distributed-fs/ceph-client/fs/proc/loadavg.c

Purpose: implements `/proc/loadavg`, reporting 1/5/15-minute load averages, runnable/total thread counts, and the last allocated PID cursor in the reader's active PID namespace.

Important APIs and functions: `loadavg_proc_show` calls `get_avenrun`, `nr_running`, global `nr_threads`, and `idr_get_cursor(&task_active_pid_ns(current)->idr)`. `proc_loadavg_init` registers a permanent single-file proc entry.

Control flow: each read computes fixed-point load averages with a small bias (`FIXED_1/200`) and formats the traditional five fields. The initcall creates `loadavg` under proc root.

State and persistence behavior: no local state persists. Values are live scheduler and PID namespace snapshots; they are not mutually atomic.

Dependencies and integration points: depends on scheduler load average accounting, PID namespaces, procfs single-file helpers, and seq_file output. It is consumed by uptime/top/procps-style tools.

Risks: output semantics are ABI-stable, so field order and formatting must not change. The last PID field is namespace-sensitive and can be surprising if current task's active PID namespace differs from the proc mount namespace.

Test signals: compare `/proc/loadavg` with scheduler load under idle and CPU-bound workloads; read from nested PID namespaces; verify permanent entry creation and stable formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/loadavg.c -->
