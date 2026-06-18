# sources/distributed-fs/ceph-client/ipc/sem.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/sem.c` implements System V semaphore sets, including `semget`, `semctl`, `semop`, timed waits, SEM_UNDO, namespace initialization/teardown, wakeup ordering, proc reporting, and compat/time32 syscall support. The source was read as a complete 2484-line file.

## Important APIs, Types, and Functions

`struct sem` stores one semaphore value, last-modifier pid, per-semaphore lock, pending alter/const wait queues, and replicated operation time. `struct sem_array` stores IPC permissions, set-wide timestamps, global pending queues, undo-list linkage, number of semaphores, complex-operation counters, global-lock mode, and the flexible array of semaphores. `struct sem_queue` represents one blocked semop. `struct sem_undo` and `struct sem_undo_list` implement SEM_UNDO state.

Major functions include `sem_init_ns()`, `sem_exit_ns()`, `newary()`, `freeary()`, `ksys_semget()`, `ksys_semctl()`, `semctl_main()`, `semctl_setval()`, `semctl_down()`, `__do_semtimedop()`, `do_semtimedop()`, `copy_semundo()`, and `exit_sem()`. Concurrency helpers include `sem_lock()`, `complexmode_enter()`, `complexmode_tryleave()`, `merge_queues()`, `unmerge_queues()`, `perform_atomic_semop()`, `update_queue()`, and `do_smart_update()`.

## Control Flow

`semget` uses generic `ipcget()` with `newary()` to allocate a semaphore set, initialize all per-semaphore queues/locks, charge `ns->used_sems`, and publish an id. `semctl` handles info/stat commands, permission updates, removal, get/set value operations, and bulk get/set. `SETVAL` and `SETALL` clear related undo adjustments and run smart wakeups because blocked operations may now complete.

`semop` copies user `sembuf` operations, validates counts and semaphore indexes, optionally allocates an undo entry, checks permissions and LSM policy, and attempts atomic execution. Nonblocking success updates values, SEM_UNDO adjustments, pids, operation time, and pending waiters. If an operation would block, it is inserted into either per-semaphore queues for simple operations or global queues for complex operations, then sleeps with timeout/signal handling. Wakers complete blocked operations while holding the relevant semaphore locks and store final status before waking the task.

## State and Persistence Behavior

Semaphore sets persist in `ns->ids[IPC_SEM_IDS]` until `IPC_RMID` or namespace exit. Semaphore values, pids, timestamps, pending queues, and undo lists are runtime kernel state. SEM_UNDO entries persist per task or shared task group when `CLONE_SYSVSEM` is used; `exit_sem()` applies bounded adjustments and frees undo objects on final reference. Namespace tunables control maximum set size, total semaphores, operations per call, and number of sets.

## Dependencies and Integration Points

This file integrates SysV IPC id/key utilities, LSM hooks, audit, RCU, wake queues, hrtimer timeouts, pid and user namespaces, proc sysvipc output, sysctl validation through `sem_check_semmni()`, clone/exit task hooks, and compat/time32 syscall layers.

## Risks and Edge Cases

The file has high concurrency risk. Correctness depends on the documented barriers for `use_global_lock` and `queue.status`, lock ordering between set locks and per-semaphore locks, and active wakeup semantics. FIFO behavior requires careful queue merging when complex operations appear. SEM_UNDO must handle id reuse, `IPC_RMID` races, duplicate semops in one transaction, undo range limits, and exit-time clamping to `0..SEMVMX`.

## Test Signals

Tests should cover simple and multi-op semop success/failure, wait-for-zero, FIFO wake order, timeout and signal interruption, `IPC_NOWAIT`, duplicate operations on the same semaphore, `SEM_UNDO` across fork/clone/exit, `IPC_RMID` with sleepers, `SETVAL`/`SETALL` wakeups and undo clearing, sysctl limit changes, proc output, namespace isolation, compat semctl, and time32 semtimedop.
