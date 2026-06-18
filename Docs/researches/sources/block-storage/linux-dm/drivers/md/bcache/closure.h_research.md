# File Research: sources/block-storage/linux-dm/drivers/md/bcache/closure.h

## Purpose
Defines the closure abstraction used by bcache for refcounted asynchronous control flow, parent-child completion, workqueue continuations, synchronous waits, and debug state.

## Main Interfaces
- Types: `struct closure`, `struct closure_waitlist`, `closure_fn`, and internal `closure_syncer`.
- State bits: destructor, waiting, running, guard mask, and remaining refcount mask.
- Inline helpers: `closure_sync()`, `closure_get()`, `closure_init()`, `closure_init_stack()`, `closure_wake_up()`, `closure_queue()`, and debug IP/wait annotations.
- Continuation macros: `continue_at()`, `closure_return()`, `continue_at_nobarrier()`, `closure_return_with_destructor()`, and `closure_call()`.

## Control Flow
Closures start with a refcount of one owned by the running context. Extra asynchronous work takes refs and drops them on completion. `continue_at()` installs the next function/workqueue and drops the running ref; when outstanding refs reach zero the next function is invoked. Parent closures hold a lifetime ref until the child fully returns.

## State And Synchronization
Continuation setup uses memory barriers around atomic refcount transitions. Workqueue queuing relies on `struct closure` field layout matching `struct work_struct` function layout, enforced by `BUILD_BUG_ON`.

## Integration Points
Included by `bcache.h` and used by btree IO, journal, superblock writes, request paths, and debug support. `BCACHE_CLOSURES_DEBUG` adds magic values, list linkage, and origin/wait-site tracking.

## Notable Behaviors
- The long header comment is the primary contract for safe closure usage.
- `closure_wait()` returns whether the closure was newly placed on a wait list, enforcing one wait list at a time.
- Stack closures can be initialized without debug registration.

## Risks And Review Focus
- The API requires immediate return after `continue_at()`; touching closure-owned state afterward is unsafe.
- The overloaded union with `work_struct` is layout-sensitive.
- Debug and non-debug builds have different validation strength, so misuse may only fail reliably with debug enabled.
