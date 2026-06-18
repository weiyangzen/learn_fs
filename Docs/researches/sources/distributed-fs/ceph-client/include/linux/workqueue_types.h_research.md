# sources/distributed-fs/ceph-client/include/linux/workqueue_types.h

## Purpose
`workqueue_types.h` provides the minimal core type declarations for Linux workqueues. It lets other headers refer to `struct work_struct`, work function callbacks, and delayed work timer support without importing the full workqueue API.

## Important APIs, Types, and Functions
The file forward-declares `struct workqueue_struct`, declares `struct work_struct`, defines `work_func_t`, and declares `delayed_work_timer_fn()`. `struct work_struct` contains encoded atomic data, a list entry, callback function pointer, and optional lockdep map under `CONFIG_LOCKDEP`.

## Control Flow
The header has no runtime control flow. It defines the object shape consumed by `workqueue.h` initialization and queueing logic. At runtime, workqueue implementations inspect `data`, link `entry` into internal lists, and call `func(work)`.

## State and Persistence
`struct work_struct` is persistent state embedded in caller objects. Its `data` word encodes pending/off-queue/pool/disable state; `entry` links into workqueue lists; `func` is the callback. Lockdep state persists for debugging when enabled.

## Dependencies and Integration Points
Dependencies include atomics, lockdep type definitions, timer types, and generic types. Integration points include any structure embedding a `work_struct` while trying to avoid full workqueue header dependencies.

## Risks
Callers must initialize `work_struct` before queueing, usually via macros in `workqueue.h`. Directly modifying `data` or `entry` corrupts workqueue state. Embedded work must outlive any queued or running callback. Lockdep map presence changes structure layout by config.

## Test Signals
Signals include compile coverage for headers embedding `work_struct`, lockdep and non-lockdep builds, and runtime workqueue tests that verify initialization, queueing, cancellation, and callback invocation.
