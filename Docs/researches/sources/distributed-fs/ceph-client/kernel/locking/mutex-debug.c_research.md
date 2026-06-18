# sources/distributed-fs/ceph-client/kernel/locking/mutex-debug.c research

## Purpose
`mutex-debug.c` provides debug-only helpers for Linux mutex internals. It poisons and validates mutex waiters, checks waiter/task relationships, tracks mutex initialization/destruction through a magic pointer, integrates mutex destruction with devres, and exports `mutex_destroy()` for marking a mutex unusable after teardown.

## Important APIs, Types, and Functions
`debug_mutex_lock_common()` initializes a `struct mutex_waiter` while `lock->wait_lock` is held: it fills the waiter with `MUTEX_DEBUG_INIT`, sets `waiter->magic` to itself, initializes the list node, and poisons the wound/wait context pointer. `debug_mutex_wake_waiter()` asserts `wait_lock` is held, `first_waiter` exists, and the waiter's magic value is intact. `debug_mutex_free_waiter()` verifies the waiter list node is empty and poisons the waiter with `MUTEX_DEBUG_FREE`.

`debug_mutex_add_waiter()` asserts the current task is not already blocked on a mutex. `debug_mutex_remove_waiter()` verifies the waiter belongs to the task and that any blocked-on mutex matches the lock being removed, then clears the waiter list and task pointer. `debug_mutex_unlock()` checks the mutex magic pointer when debug locks are still enabled. `debug_mutex_init()` sets `lock->magic = lock`.

`__devm_mutex_init()` registers `devm_mutex_release()` as a devres cleanup action; the release callback calls `mutex_destroy()`. `mutex_destroy()` warns if the mutex is locked and clears `lock->magic`, making later use detectable. `__devm_mutex_init()` and `mutex_destroy()` are exported GPL symbols.

## Control Flow
Mutex slow paths call these helpers around waiter lifecycle operations. A waiting task's waiter is initialized before queueing, checked before wakeup, removed when it stops waiting, and poisoned after use. Mutex initialization sets the magic field. Unlock and destroy paths validate the magic/liveness state. Device-managed mutex initialization attaches destruction to device cleanup so driver teardown marks the mutex invalid automatically.

## State and Persistence Behavior
The debug state is embedded in existing mutex and waiter objects. Waiter poison values are transient stack/queue lifetime checks. `lock->magic` persists from initialization until `mutex_destroy()`, after which it is NULL. There is no global state in this file, but behavior depends on global `debug_locks`: some checks are skipped after lock debugging has been disabled to avoid cascading diagnostics.

## Dependencies and Integration Points
The file includes mutex internals through `"mutex.h"` plus debug locks, lockdep assertions, scheduler blocked-task helpers, device devres, poison constants, and export support. It is integrated into the mutex implementation rather than called by ordinary subsystem code directly. Device-managed users reach it through devm mutex initialization wrappers.

## Risks and Edge Cases
The helpers assume callers hold `lock->wait_lock` where documented; missing that lock weakens waiter-list validation and can race with wakeups. Destroying a locked mutex triggers a warning but still clears magic, so subsequent diagnostics may report use-after-destroy rather than the original lifetime bug. Waiter poisoning catches stale waiter reuse but cannot prevent memory corruption if callers continue using a freed stack waiter. `__devm_mutex_init()` only registers cleanup; the mutex must still have been initialized by the caller/wrapper before use.

## Test Signals
Useful signals are `DEBUG_LOCKS_WARN_ON()` reports for corrupted waiter magic, nonempty waiter lists at free time, blocked-task mismatches, unlocking uninitialized/destroyed mutexes, and destroying locked mutexes. Devres tests should verify device cleanup calls `mutex_destroy()` through `devm_mutex_release()`.
