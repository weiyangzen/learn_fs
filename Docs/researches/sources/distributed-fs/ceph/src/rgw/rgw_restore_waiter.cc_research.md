# sources/distributed-fs/ceph/src/rgw/rgw_restore_waiter.cc

## Purpose
`rgw_restore_waiter.cc` implements an in-memory registry for GET requests waiting for a cloud restore to complete. It provides blocking and coroutine-friendly wait paths, pools waiter objects to reduce allocation churn, maps object identity to waiter vectors, and wakes or cancels all registered waiters when restore processing completes or shuts down.

## Important APIs, Types, and Functions
`RestoreWaiter::wait_for()` waits on `completed`. With `optional_yield`, it creates a Boost.Asio steady-clock timer and uses timer cancellation as the wake mechanism. Without yield, it uses `std::condition_variable::wait_for()`. `complete()` stores success/result flags, sets `completed`, notifies blocking waiters, and cancels any active async timer. `reset()` prepares a pooled waiter for reuse.

`RestoreWaiterPool::acquire()` evicts stale free waiters, returns a reset pooled waiter or allocates a new one, and wraps it in a `shared_ptr` with a deleter that returns it to the owning registry. `release()` returns waiters to a bounded free list or deletes when the pool is full. `evict_old_waiters()` drops waiters unused for five minutes.

`RestoreWaiterRegistry::register_waiter()` creates a key from bucket and object, acquires a pooled waiter, and appends it under a shared registry lock unless shutdown has begun. `unregister_waiter()` removes one waiter from its cached-key vector. `notify_completion()` moves all waiters for a key out of the map and completes them outside the lock. `shutdown()` rejects new registrations, drains all vectors, and completes waiters with `-ECANCELED`.

## Control Flow
A caller registers a waiter for a bucket/object, waits with a timeout, and uses `WaiterGuard` from the header to unregister on exit. Restore completion calls `notify_completion()`, which removes the key and signals all active waiters. Timeout callers unregister themselves; completed waiters are also removed by the registry move. When the last `shared_ptr` drops, the custom deleter returns the waiter to the pool.

## State and Persistence Behavior
All state is process-local. The registry map uses a `std::shared_mutex`, waiter status uses atomics, and timer lifetime is stored as a weak pointer behind `timer_mtx`. No restore waiter state survives restart; after restart, GET callers must re-check object attrs and register again if needed.

## Dependencies and Integration Points
The implementation depends on `optional_yield`, Boost.Asio timers, Ceph coarse time, `rgw_bucket`, `rgw_obj_key`, and restore worker calls to `notify_completion()`. It integrates with read-through restore behavior rather than persistent restore queue management.

## Risks
`register_waiter()` can return `nullptr` during shutdown after acquiring a pooled waiter; the local `shared_ptr` then releases through the pool deleter, which is okay but should be covered. Async waits do not hold `mtx`, so correctness depends on atomic ordering and timer cancellation. Key construction includes bucket key, object name, and optional instance; mismatches with restore queue object identity would strand waiters.

## Test Signals
Tests should cover blocking wait success, blocking timeout, async-yield wake by timer cancellation, shutdown cancellation, unregister after timeout, multiple waiters on one object, multiple object keys, pool reuse, pool max-size deletion, stale waiter eviction, and registration races with shutdown.
