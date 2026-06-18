<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid.c -->
# sources/distributed-fs/ceph-client/kernel/pid.c

Purpose: Implements PID allocation, lookup, task attachment/detachment, PID namespace sysctls, pidfd creation/open/getfd helpers, and init PID namespace setup.

Important APIs/types/functions: `init_struct_pid`, `init_pid_ns`, `put_pid()`, `free_pid()`, `free_pids()`, `alloc_pid()`, `disable_pid_allocation()`, `find_pid_ns()`, `find_vpid()`, `attach_pid()`, `detach_pid()`, `change_pid()`, `exchange_tids()`, `transfer_pid()`, `pid_task()`, `find_task_by_pid_ns()`, `find_get_pid()`, `pid_nr_ns()`, `pid_vnr()`, `__task_pid_nr_ns()`, `task_active_pid_ns()`, `find_ge_pid()`, `pidfd_get_pid()`, `pidfd_get_task()`, `pidfd_open`, `register_pidns_sysctls()`, `unregister_pidns_sysctls()`, `pid_idr_init()`, and `pidfd_getfd`.

Control flow: `alloc_pid()` validates requested set_tid values against namespace levels and checkpoint/restore capability, allocates a variable-sized `struct pid`, initializes task lists and pidfs state, preloads IDR memory, then allocates ids from the nested namespace up to root under `pidmap_lock`. It stores NULLs in IDRs until all levels succeed, verifies namespace init PID constraints and `PIDNS_ADDING`, then publishes with `idr_replace()`, increments per-namespace allocation counters, activates the namespace, and adds pidfs state. `free_pid()` removes all namespace id mappings, wakes namespace reapers when only init remains, removes pidfs state, and drops refs after RCU. Task attachment uses `tasklist_lock` and RCU hlist updates.

State and persistence: PID state is in per-namespace IDRs, `pid_allocated`, pid cache objects, pidfs entries, per-PID task hlist heads, wait queues, and namespace sysctl sets. PID bitmap pages/IDR storage are effectively persistent for the lifetime of the namespace. `cad_pid` and per-namespace `pid_max` are exposed through sysctl.

Dependencies/integration: Integrates with PID namespaces, user namespaces, checkpoint/restore, proc/sysctl, pidfs, anon file descriptors/pidfds, tasklist locking, RCU, ptrace permission checks, fd passing via `receive_fd()`, and CPU-count-derived PID limits.

Risks: PID allocation must be atomic across all nested namespaces or unwind precisely. The IDR preload retry path drops and reacquires `pidmap_lock`, so callers depend on the code preserving allocation correctness. `pidfd_open()` does not enforce thread-group leader when `PIDFD_THREAD` is passed; callers must interpret pidfd type flags correctly. `pidfd_getfd()` crosses task fd tables and relies on ptrace and `exec_update_lock` to avoid races. Namespace shutdown depends on `PIDNS_ADDING` and child reaper lifetime.

Test signals: nested PID allocation/free with set_tid arrays, pid_max sysctl bounds, namespace init PID requirement, PID wrap around `RESERVED_PIDS`, allocation failure unwind, find/attach/detach under RCU, pidfd open/get task/getfd permission and exit races, cad_pid sysctl update, pidfs add/remove failure, and namespace teardown wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid.c -->
