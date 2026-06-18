# sources/distributed-fs/ceph-client/kernel/locking/mutex.h

## Purpose
Private non-PREEMPT_RT mutex header defining the stack waiter record, owner flag layout, owner access helper, scheduler blocked-on helper, and debug hook declarations used by `mutex.c`.

## Important APIs, Types, and Functions
- `struct mutex_waiter` contains the wait-list link, blocked task, optional `ww_acquire_ctx`, and debug magic.
- `MUTEX_FLAG_WAITERS`, `MUTEX_FLAG_HANDOFF`, and `MUTEX_FLAG_PICKUP` occupy low bits of the owner word; `MUTEX_FLAGS` masks them.
- `__mutex_owner()` returns the owner pointer after masking flags.
- `get_task_blocked_on()` reads a task's blocked mutex under `blocked_lock`.
- Debug declarations or no-op macros provide `debug_mutex_*()` integration.

## Control Flow
This header has no independent runtime loop, but its flag layout drives the `mutex.c` state machine. The `WAITERS` flag causes unlock slow path wakeups, `HANDOFF` prevents opportunistic stealing, and `PICKUP` lets a designated waiter atomically claim ownership.

## State and Persistence
No persistent storage. It defines in-memory stack waiters and the owner-bit encoding contract for `struct mutex`.

## Dependencies and Integration Points
Included only when `CONFIG_PREEMPT_RT` is disabled. It depends on `linux/mutex.h` and task blocked-on scheduler internals. Debug hooks are supplied by the debug mutex implementation when `CONFIG_DEBUG_MUTEXES` is enabled.

## Risks
The low-bit flag scheme depends on task pointer alignment. Any change to flag values must match every atomic owner manipulation in `mutex.c`. `__mutex_owner()` intentionally drops flag state; using it where flags matter can hide handoff or waiter transitions.

## Test Signals
Compile matrix should cover debug and non-debug mutex builds. Behavioral signals are lockdep/debug mutex warnings for bad magic, recursive locking, wait-list corruption, and owner/blocked-on mismatches.
