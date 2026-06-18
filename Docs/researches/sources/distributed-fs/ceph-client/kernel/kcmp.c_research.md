# sources/distributed-fs/ceph-client/kernel/kcmp.c

## Purpose
Implements the `kcmp` syscall, allowing authorized userspace to compare whether two tasks share kernel resources such as files, VM, fs, sighand, IO context, SysV semaphore undo lists, or epoll targets.

## Important APIs, Types, and Functions
Main entry is `SYSCALL_DEFINE5(kcmp)`. Helpers are `kptr_obfuscate`, `kcmp_ptr`, `get_file_raw_ptr`, `kcmp_lock`, `kcmp_unlock`, optional `kcmp_epoll_target`, and `kcmp_cookies_init`. `cookies[KCMP_TYPES][2]` obfuscates pointer ordering.

## Control Flow
The syscall finds both tasks in the caller's PID namespace under RCU, pins them, takes their `exec_update_lock` semaphores in address order, checks `ptrace_may_access`, then dispatches by `type`. File comparisons acquire file references transiently; epoll mode copies a userspace slot and compares the target file stored in an epoll instance.

## State and Persistence
Only boot-initialized random cookies persist. Comparisons return equality/order over obfuscated pointer values; real pointers are never exposed. No per-call state persists after task refs and locks are released.

## Dependencies and Integration Points
Integrates with ptrace permissions, PID namespaces, file tables, epoll, task signal locks, SysV IPC when enabled, and `arch_initcall` random cookie setup.

## Risks
Permission checks are central because resource sharing is sensitive. Lock ordering must prevent deadlocks when comparing a task with itself or another task. `get_file_raw_ptr` intentionally returns a raw pointer after dropping a ref for comparison only; callers must not dereference it later.

## Test Signals
Expected syscall errors include `-ESRCH`, `-EPERM`, `-EBADF`, `-EINVAL`, and `-EOPNOTSUPP`. KCMP behavior is typically validated by userspace tests that compare known shared and non-shared resources.
