# sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.h

## Purpose
`rgw_restore_waiter.h` declares the in-memory waiter subsystem used by restore/read-through paths. It abstracts a single waiting GET request, a bounded object pool, a bucket/object registry, and an RAII guard for automatic unregistration.

## Important APIs, Types, and Functions
`RestoreWaiter` contains the synchronization state for one waiter: a condition variable for blocking callers, a Boost.Asio steady-clock timer for coroutine callers, atomic `completed`, `failed`, and `result`, a cached registry key, and a last-used timestamp. `wait_for()`, `complete()`, and `reset()` are the core operations.

`RestoreWaiterPool` owns a mutex-protected `free_list` of `unique_ptr<RestoreWaiter>`, bounded by `MAX_POOL_SIZE` and aged by `EVICTION_TIME`. `acquire()` returns a `shared_ptr` using a custom deleter; `release()` and `evict_old_waiters()` are private registry-owned helpers.

`RestoreWaiterRegistry` derives from `enable_shared_from_this` so pooled waiters can safely return to their owner. It maps string keys to vectors of waiters and exposes `register_waiter()`, `unregister_waiter()`, `notify_completion()`, and `shutdown()`. `WaiterGuard` unregisters a waiter in its destructor and is non-copyable.

## Control Flow
Callers acquire a registry from `Restore`, register a waiter for the object, construct a `WaiterGuard`, and then call `wait_for()` with either a blocking or coroutine yield context. Restore completion uses the same bucket/object key to notify all matching waiters. Shutdown flips an atomic flag before draining the map so late callers are rejected.

## State and Persistence Behavior
The subsystem intentionally persists nothing. Registry keys are derived from RGW bucket and object identity. Pooled waiters are reset before reuse; `last_used` only drives memory reclamation. Result codes are stored as `int16_t`, which assumes restore-related error values fit in that range.

## Dependencies and Integration Points
The header depends on C++ synchronization primitives, Boost.Asio timers, Ceph time, `optional_yield`, `rgw_common.h`, and SAL object identity types. It is used by `rgw_restore.{h,cc}` and by request paths that need to block until restore completion.

## Risks
The `int16_t` result field can truncate uncommon large negative errors. `WaiterGuard` relies on callers keeping both registry and waiter pointers valid and on `unregister_waiter()` being safe after completion moved the waiter vector out of the registry. The timer and condition-variable paths must stay semantically aligned.

## Test Signals
Header-level tests should instantiate the RAII guard, verify non-copyability, validate that shutdown prevents registration, and exercise result/failed/completed state after `complete()` and `reset()`. Integration tests should cover a GET waiting on a restore entry completed by the background worker.
