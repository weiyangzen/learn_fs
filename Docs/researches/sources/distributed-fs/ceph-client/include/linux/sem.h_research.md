# sources/distributed-fs/ceph-client/include/linux/sem.h

Purpose: `sem.h` ties SysV semaphore undo state to task lifecycle while including UAPI semaphore definitions.

Important APIs/types/functions: It includes `<uapi/linux/sem.h>` and `sem_types.h`, forward declares `struct task_struct`, and declares `copy_semundo()` plus `exit_sem()` under `CONFIG_SYSVIPC`. Disabled builds provide no-op success for copy and an empty exit hook.

Control flow: Fork/clone paths call `copy_semundo()` to share or duplicate semaphore undo state based on clone flags. Task exit calls `exit_sem()` to apply and release undo adjustments. Without SysV IPC, the hooks compile away.

State and persistence behavior: Per-task SysV semaphore undo state is represented by `struct sysv_sem` in `sem_types.h`; actual undo lists and semaphore arrays live in IPC implementation code. Undo adjustments persist for the task lifetime and are applied at exit.

Dependencies and integration points: It integrates with task cloning, task exit, SysV IPC semaphore operations, and UAPI semaphore commands.

Risks: Undo-list sharing semantics must match clone flags. Missing `exit_sem()` would leak or fail to apply undo adjustments. Disabled stubs must not leave callers expecting real IPC state.

Test signals: SysV semaphore create/op with `SEM_UNDO`, fork/clone sharing, task exit rollback, disabled `CONFIG_SYSVIPC` builds, and IPC namespace teardown.
