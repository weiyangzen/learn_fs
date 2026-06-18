# File Research: sources/block-storage/linux-dm/drivers/md/bcache/closure.c

## Purpose
Implements bcache closures: asynchronous refcounted continuations, wait-list wakeups, synchronous waiting, optional debugfs tracking, and module metadata.

## Main Interfaces
- Refcount completion: `closure_sub()`, `closure_put()`.
- Wait-list operations: `__closure_wake_up()`, `closure_wait()`.
- Synchronous wait: `__closure_sync()`.
- Debug support under `CONFIG_BCACHE_CLOSURES_DEBUG`: create/destroy tracking, debugfs show, `closure_debug_init()`.

## Control Flow
Dropping the refcount to zero either queues/calls the stored continuation, runs a destructor, and/or releases the parent closure. `__closure_wake_up()` atomically drains a lockless wait list, reverses it to preserve FIFO order, then releases each waiting closure reference. `__closure_sync()` installs a temporary continuation that wakes the current task once pending refs drain.

## State And Synchronization
Uses atomic `remaining` bits from `closure.h`, lockless linked lists for waiters, RCU while waking the sync waiter, and optional spinlock-protected global debug list.

## Integration Points
Used throughout bcache metadata and IO code to wait on bios, journal writes, btree writes, and nested asynchronous operations. Debugfs output lives under the global `bcache_debug` directory.

## Notable Behaviors
- The wait-list wake path explicitly preserves FIFO fairness.
- Debugfs closure listing prints closure address, origin instruction pointer, continuation, parent, remaining refs, queued/running state, and wait site.
- `MODULE_AUTHOR` and `MODULE_LICENSE` are declared here for the closure component.

## Risks And Review Focus
- Closure users must follow the ownership rule: a running closure owns one ref and must use `continue_at()`/return macros.
- Incorrect flag/refcount transitions trigger `BUG_ON()` and can cause use-after-free or missed continuations.
- `__closure_sync()` depends on the temporary syncer staying valid until the wake function runs.
