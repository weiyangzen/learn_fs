<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tsacct.c -->
# sources/distributed-fs/ceph-client/kernel/tsacct.c

Purpose: fills taskstats accounting records for basic and extended per-task resource usage. It is used by taskstats/acct paths to report elapsed time, CPU time, credentials, page faults, command names, IO counts, and memory-time integrals.

Important APIs: `bacct_add_tsk()` populates base task accounting fields. Under `CONFIG_TASK_XACCT`, `xacct_add_tsk()` adds extended memory and IO fields, `acct_update_integrals()` updates RSS/VM time integrals in interrupt-safe context, `acct_account_cputime()` updates after CPU time changes, and `acct_clear_integrals()` resets accumulators.

Control flow: base accounting calculates elapsed nanoseconds from task start times, converts to microseconds, derives boot time fields, records exit flags, pid/tgid/ppid in the requested pid namespace, maps uid/gid through a user namespace under RCU, collects CPU times, faults, and command name. Extended accounting converts stored page-nsec integrals to Mbyte-usec style taskstats units and samples mm high-water marks if an mm is available.

State and persistence: accounting accumulators live in `task_struct` fields such as `acct_rss_mem1`, `acct_vm_mem1`, and `acct_timexpd`. Output is copied into a caller-provided `struct taskstats`; this file does not persist records.

Dependencies and integration: depends on scheduler CPU time helpers, namespaces, credentials, mm references, task IO accounting, and taskstats structures.

Risks: unit conversions and overflow boundaries matter, especially legacy `ac_btime` clamping. `__acct_update_integrals()` skips kernel threads and mm-less tasks. Test signals include exited and live tasks, namespace uid/gid mapping, high-water RSS/VM reporting, IO accounting disabled builds, and sub-tick integral updates being ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tsacct.c -->
