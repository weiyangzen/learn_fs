# sources/distributed-fs/ceph-client/arch/s390/kernel/guarded_storage.c

## Purpose
Implements the s390 guarded-storage syscall, per-task guarded-storage control block management, and broadcast loading of guarded-storage control blocks across threads.

## Important APIs, Types, And Functions
Exports `guarded_storage_release()` and `gs_load_bc_cb()`. The syscall is `sys_s390_guarded_storage(command, struct gs_cb __user *)`. Internal commands are handled by `gs_enable()`, `gs_disable()`, `gs_set_bc_cb()`, `gs_clear_bc_cb()`, and `gs_broadcast()`.

## Control Flow
The syscall first checks `cpu_has_gs()`, then dispatches command IDs. Enabling allocates a zeroed control block, sets default `gsd`, disables preemption, sets CR2 guarded-storage bit, loads the control block, and stores it in the current thread. Broadcast control blocks are copied from userspace into `thread.gs_bc_cb`. `gs_broadcast()` scans sibling threads, sets `TIF_GUARDED_STORAGE`, and kicks them. On return-to-user handling, `gs_load_bc_cb()` swaps the pending broadcast block into active state and loads it.

## State And Persistence
Per-task state lives in `thread.gs_cb` and `thread.gs_bc_cb`; CR2 guarded-storage bit is per-CPU hardware state while active. Release frees both blocks.

## Dependencies And Integration Points
Depends on guarded-storage instruction helpers, syscall dispatch, tasklist locking, thread flags, signal/return-to-user path, and control-register helpers.

## Risks And Edge Cases
Preemption is disabled around hardware state changes to bind control-register and load operations to the current CPU. Broadcast races with thread exit and repeated pending blocks require careful freeing. User copy failures leave allocated pending blocks intact.

## Test Signals
Signals include guarded-storage syscall tests for every command, unsupported CPU behavior, multithread broadcast delivery, context-switch preservation, thread exit cleanup, and invalid userspace pointer handling.
