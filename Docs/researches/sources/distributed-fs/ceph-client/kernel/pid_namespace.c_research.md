<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_namespace.c -->
# sources/distributed-fs/ceph-client/kernel/pid_namespace.c

Purpose: Implements PID namespace creation, destruction, process zapping on namespace init exit, PID namespace reboot behavior, proc namespace operations, and checkpoint/restore sysctl registration.

Important APIs/types/functions: `copy_pid_ns()`, `put_pid_ns()`, `zap_pid_ns_processes()`, `reboot_pid_ns()`, `pidns_is_ancestor()`, `pidns_operations`, `pidns_for_children_operations`, and `pid_namespaces_init()`. Internal helpers include `create_pid_cachep()`, `create_pid_namespace()`, `destroy_pid_namespace_work()`, `pid_ns_ctl_handler()`, `pidns_get()`, `pidns_for_children_get()`, `pidns_put()`, `pidns_install()`, `pidns_get_parent()`, and `pidns_owner()`.

Control flow: creating a PID namespace verifies user namespace ancestry, max nesting, and ucount limits, allocates a namespace object and level-specific PID cache, initializes common namespace state and sysctls, inherits `memfd_noexec_scope`, links parent/user refs, sets `PIDNS_ADDING`, initializes destroy work, and adds the namespace to the namespace tree. Destruction removes the namespace tree/sysctls, frees the proc inode and IDR, then RCU-frees user/ucount references. `zap_pid_ns_processes()` disables PID allocation, ignores SIGCHLD, sends SIGKILL to remaining namespace tasks by IDR iteration, waits for children, then sleeps until only namespace init tasks remain.

State and persistence: PID namespaces store IDRs, parent/user namespace refs, ucount charging, `pid_allocated`, `child_reaper`, reboot signal, pid cache pointer, sysctl set/header, active namespace nodes, and optional memfd noexec scope. Destruction is deferred through workqueue and RCU to avoid freeing while visible to lookups.

Dependencies/integration: Integrates with user namespace ucounts, proc namespace operations, namespace trees, sysctl, checkpoint/restore `ns_last_pid`, memfd sysctl helper, reboot syscall behavior, signal delivery, wait/reaping, tasklist lock, accounting exit, and PID allocation in `pid.c`.

Risks: Namespace destruction cascades through parents while using active refs; incorrect `ns_ref_put()` handling can leak or prematurely destroy parent namespaces. `zap_pid_ns_processes()` relies on child reaper signal disposition and `pid_allocated` wakeups to avoid hangs. `pidns_install()` must prevent escaping to ancestor/incomparable PID namespaces. `pid_ns_ctl_handler()` updates the IDR cursor and requires checkpoint/restore capability.

Test signals: nested PID namespace creation at max depth, ucount exhaustion, failed init fork cleanup, sysctl registration failures, namespace init exit with live children/zombies/parent-namespace tracers, reboot commands in nested namespaces, setns PID ancestry validation, proc namespace get/put/parent, and `ns_last_pid` writes under checkpoint/restore capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/pid_namespace.c -->
