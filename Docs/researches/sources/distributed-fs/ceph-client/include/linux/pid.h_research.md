# sources/distributed-fs/ceph-client/include/linux/pid.h

## Purpose
Kernel internal PID object API. It provides stable `struct pid` references across numeric PID reuse, task attachment lists for PID/TGID/PGID/SID, PID namespace number translation, pidfd support, and task PID helper accessors.

## Important APIs, Types, and Functions
Defines `RESERVED_PIDS`, `struct upid`, `struct pid`, `init_struct_pid`, and helpers including `get_pid()`, `put_pid()`, `pid_task()`, `get_pid_task()`, `get_task_pid()`, `attach_pid()`, `detach_pid()`, `change_pid()`, `exchange_tids()`, `transfer_pid()`, `find_pid_ns()`, `find_vpid()`, `find_get_pid()`, `alloc_pid()`, `free_pid()`, `free_pids()`, `disable_pid_allocation()`, `pid_nr()`, `pid_nr_ns()`, and `pid_vnr()`. Pidfd functions include `pidfd_pid()`, `pidfd_get_pid()`, `pidfd_get_task()`, `pidfd_prepare()`, and `do_notify_pidfd()`.

## Control Flow
PID allocation creates a namespace-level number array, attaches tasks under tasklist locking, and exposes lookup under tasklist or RCU protection. Task helpers convert `task_struct` PID pointers to numbers in init/current/specified namespaces. Iteration macros walk task lists attached to a pid and handle thread-group cases.

## State and Persistence
`struct pid` persists a refcount, namespace level, lock, pidfs inode/hash/dentry/attrs, per-pid-type task hlist heads, inode list, pidfd waitqueue, RCU callback, and namespace-specific `struct upid numbers[]`. It deliberately outlives numeric PID reuse while references are held.

## Dependencies and Integration Points
Depends on pid namespaces, RCU hlist, refcounting, rhashtable, scheduler/task structures, waitqueues, pidfs, pidfd, tasklist locking, and namespace-aware task APIs.

## Risks
Dereferencing stale tasks without `pid_alive()` or RCU/tasklist locking is unsafe. Numeric PID storage can race PID reuse; code should hold `struct pid` references. Attachment changes require tasklist write lock. Namespace translation can return zero when a PID is not visible.

## Test Signals
Fork/exit stress, pid namespace tests, pidfd wait/notification tests, PID reuse tests, task iteration under RCU, and lockdep/KCSAN checks around attach/detach paths.
