# sources/distributed-fs/ceph-client/include/linux/pid_namespace.h

## Purpose
PID namespace state and lifecycle API. It defines the namespace object used to allocate and translate PIDs independently across nested process namespaces.

## Important APIs, Types, and Functions
Defines `MAX_PID_NS_LEVEL`, memfd noexec scope constants when applicable, `struct pid_namespace`, `init_pid_ns`, and `PIDNS_ADDING`. Enabled builds expose `to_pid_ns()`, `get_pid_ns()`, `pidns_memfd_noexec_scope()`, `copy_pid_ns()`, `zap_pid_ns_processes()`, `reboot_pid_ns()`, `put_pid_ns()`, and `pidns_is_ancestor()`. Common APIs include `task_active_pid_ns()`, `pidhash_init()`, `pid_idr_init()`, sysctl registration helpers, and `task_is_in_init_pid_ns()`.

## Control Flow
Namespace creation through `copy_pid_ns()` either reuses the existing namespace or creates a child when `CLONE_NEWPID` is set. Process teardown can zap namespace processes or record namespace reboot status. Memfd noexec scope walks parent namespaces and takes the maximum effective restriction.

## State and Persistence
`struct pid_namespace` persists an IDR allocator, allocated count, sysctl state, child reaper task, PID cache, nesting level, pid_max, parent namespace, BSD accounting pin, user namespace, ucounts, reboot code, namespace common object, and cleanup work item.

## Dependencies and Integration Points
Depends on scheduler, mm, workqueues, namespace core, IDR, sysctl, memfd, user namespaces, ucounts, and process accounting.

## Risks
Namespace nesting is capped by `MAX_PID_NS_LEVEL` because `struct pid` embeds per-level numbers. Reaper lifetime and namespace teardown are delicate; `zap_pid_ns_processes()` is invalid when PID namespaces are disabled. Sysctl state must follow namespace lifetime.

## Test Signals
PID namespace clone/unshare tests, nested namespace limits, namespace reboot tests, memfd noexec inheritance tests, pid_max sysctl tests, and process reaper teardown stress.
