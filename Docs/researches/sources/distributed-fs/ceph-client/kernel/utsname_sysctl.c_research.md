<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c -->
# sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c

Purpose: exposes UTS namespace fields through `/proc/sys/kernel` sysctls such as hostname, domainname, ostype, osrelease, version, and arch.

Important APIs and state: `proc_do_uts_string()` is the namespace-aware sysctl handler. `uts_kern_table` defines entries and modes. `uts_proc_notify()` notifies poll waiters for selected UTS fields. `utsname_sysctl_init()` registers the table. Poll state exists for hostname and domainname.

Control flow: `get_uts()` translates a table data pointer based on the offset from `init_uts_ns` to the current task's UTS namespace. The handler copies the current value under `uts_sem`, drops the lock while calling `proc_dostring()`, and on write adds device randomness, writes the updated value back under write lock, and notifies pollers.

State and persistence: values live inside the current UTS namespace. Sysctl table entries are global but dynamically redirected to current namespace storage by pointer offset arithmetic.

Dependencies and integration: depends on proc sysctl, current nsproxy, `uts_sem`, random device entropy mixing, and sysctl poll notification.

Risks: the handler acknowledges parallel partial writes can produce theoretically incorrect combined results because it drops `uts_sem` during `proc_dostring()`. Pointer offset mapping assumes table data points into `init_uts_ns`. Test signals include per-namespace hostname/domainname reads and writes, poll notification, read-only entries, partial writes, and concurrent writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname_sysctl.c -->
