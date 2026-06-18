# sources/distributed-fs/ceph-client/include/linux/sem_types.h

Purpose: `sem_types.h` defines the task-embedded SysV semaphore state container without pulling in the full semaphore API.

Important APIs/types/functions: It forward declares `struct sem_undo_list` and defines `struct sysv_sem`, which contains `struct sem_undo_list *undo_list` only when `CONFIG_SYSVIPC` is enabled.

Control flow: No functions are present. Task lifecycle code and SysV IPC code manipulate the undo-list pointer through APIs declared in `sem.h`.

State and persistence behavior: The `undo_list` pointer is per-task state. It links a task to semaphore undo adjustments that must be applied or released at exit. Disabled builds intentionally make the structure empty.

Dependencies and integration points: It integrates with `task_struct`, SysV IPC namespaces, semaphore arrays, clone, and exit paths.

Risks: Conditional structure layout means code must not access `undo_list` without `CONFIG_SYSVIPC`. Lifetime and sharing of `sem_undo_list` require external locking/refcounting in implementation code.

Test signals: Build both configs, verify task struct layout users, fork/exit with undo entries, shared undo list handling, and IPC namespace cleanup.
