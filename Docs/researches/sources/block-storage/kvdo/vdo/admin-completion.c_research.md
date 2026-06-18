# File Research: sources/block-storage/kvdo/vdo/admin-completion.c

## Purpose

Implements synchronous administrative operation orchestration on top of VDO’s asynchronous completion system.

## Main Responsibilities

- Initializes an embedded admin completion and sub-task completion for a `struct vdo`.
- Enforces one admin operation at a time using `atomic_t busy`.
- Provides helpers to:
  - assert expected admin operation type,
  - recover `struct admin_completion` from a sub-task completion,
  - recover `struct vdo` from an admin sub-task,
  - assert phase-specific thread affinity.
- Prepares admin sub-task completions to run on the current phase thread.
- Runs an admin operation by enqueueing a sub-task and waiting for completion.

## Important Functions

- `vdo_initialize_admin_completion()` initializes admin and sub-task completions plus the Linux completion used for synchronization.
- `vdo_reset_admin_sub_task()` resets a sub-task and assigns the current phase thread.
- `vdo_prepare_admin_sub_task()` prepares a sub-task on the same thread as the enclosing admin completion.
- `vdo_perform_admin_operation()` is the synchronous entry point for load, suspend, resume, and grow operations.

## Behavior Details

`vdo_perform_admin_operation()` uses `atomic_cmpxchg()` to reject concurrent admin operations. It prepares the outer admin completion to run on the admin thread, records operation type and phase thread resolver, prepares the sub-task, enqueues it, then waits on a Linux `struct completion`.

The wait uses `wait_for_completion_interruptible()` to avoid long kernel wait warnings, but ignores signals and sleeps briefly before retrying. Once the callback signals completion, the result is read, a write barrier is issued, and `busy` is cleared.

## Dependencies and Interactions

- Depends on `completion.c` for callback execution.
- Uses `thread-config.h` for admin thread selection.
- Used by higher-level VDO administrative workflows that need a blocking kernel-control path over async base-thread work.

## Notable Edge Cases

- A second admin operation returns/logs `VDO_COMPONENT_BUSY`.
- Signals during the wait do not abort the operation.
- Thread assertions are log-only assertions through `ASSERT_LOG_ONLY`.
