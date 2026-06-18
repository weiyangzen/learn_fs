# sources/distributed-fs/ceph-client/fs/netfs/fscache_cache.c

## Purpose

`fscache_cache.c` manages FS-Cache cache-level records. It tracks registered cache backends, cache lookup/acquisition by name, cache activation and withdrawal, access pinning, I/O-error state transitions, and optional `/proc/fs/fscache/caches` enumeration.

## Important APIs and Functions

Exported globals are `fscache_addremove_sem` and `fscache_clearance_waiters`. Exported functions are `fscache_acquire_cache()`, `fscache_put_cache()`, `fscache_relinquish_cache()`, `fscache_add_cache()`, `fscache_io_error()`, and `fscache_withdraw_cache()`. `fscache_lookup_cache()`, `fscache_begin_cache_access()`, and `fscache_end_cache_access()` are non-exported or internal-facing helpers visible in this file.

Important internal state includes the global `fscache_caches` list, per-cache `ref`, `n_accesses`, `n_volumes`, `object_count`, `state`, `ops`, `cache_priv`, `name`, and `debug_id`. Cache states are displayed with `fscache_cache_states` as not-present, preparing, active, I/O error, or withdrawn.

## Control Flow

`fscache_lookup_cache()` first searches the global list under a read lock. It matches exact named caches, exact unnamed caches, or, for unnamed lookups, any named cache. If nothing matches, it allocates a candidate and repeats the search under the write lock. A newly added real cache can claim an existing unnamed record, allowing volumes that found an unnamed placeholder to attach to the backend when it appears. Otherwise the candidate is inserted and returned with one reference.

`fscache_acquire_cache()` looks up a named cache for backend registration and atomically transitions it from `FSCACHE_CACHE_IS_NOT_PRESENT` to `FSCACHE_CACHE_IS_PREPARING`. If another backend is using the tag, it drops the reference and returns `-EBUSY`.

`fscache_add_cache()` publishes a prepared backend. It requires the preparing state, artificially increments `n_accesses` to keep access wakeups suppressed while active, installs backend ops and private data under `fscache_addremove_sem`, transitions to active, and logs the added cache.

`fscache_begin_cache_access()` permits users to pin a live cache. It checks liveness, increments `n_accesses`, uses a memory barrier, rechecks liveness, and backs out if the cache was withdrawn concurrently. `fscache_end_cache_access()` decrements `n_accesses` and wakes waiters when it reaches zero.

`fscache_io_error()` transitions an active cache to I/O-error state and logs that it stopped. `fscache_withdraw_cache()` marks the cache withdrawn, drops the artificial active pin, and waits for `n_accesses` to drain. `fscache_relinquish_cache()` clears backend ops/private data, resets state to not-present, and releases the backend's reference. `fscache_put_cache()` removes and frees a record when the final ref drops.

## State and Persistence Behavior

The file manages in-memory cache registry state. It does not persist data itself; actual cache storage is delegated to backend `fscache_cache_ops`. State transitions determine whether volumes/cookies may access cache resources. The `n_accesses` counter is a runtime pin that prevents backend withdrawal from racing with ongoing operations.

## Dependencies and Integration Points

It depends on FS-Cache internal state helpers/macros, tracepoints, refcount APIs, rwsems, wait queues, and optional procfs seq operations. Cache backends call `fscache_acquire_cache()`, then `fscache_add_cache()`, later `fscache_withdraw_cache()` and `fscache_relinquish_cache()`. Volume and cookie code uses cache lookup/access state to bind network filesystem data to cache backends.

## Risks and Edge Cases

Concurrency risks center on lookup versus backend registration, unnamed placeholder adoption, state transitions during access pinning, and final reference removal while iterating `/proc`. `fscache_begin_cache_access()` must recheck liveness after incrementing `n_accesses`; otherwise withdrawal could complete while an operation begins. Backend error handling must reliably prevent new accesses after `fscache_io_error()`.

Naming behavior is subtle: unnamed lookups can match the first named cache, and real caches can rename an unnamed placeholder. This is designed behavior but can surprise tests if multiple cache backends or volumes are configured. `fscache_put_cache()` removes the cache record under the global write semaphore only after refcount reaches zero.

## Test Signals

Useful tests include cache backend registration and duplicate-name `-EBUSY`, unnamed volume before named backend registration, withdrawal waiting for active accesses, I/O-error transition blocking new access, procfs cache listing under concurrent add/remove, refcount leak checks, and FS-Cache integration tests that mount a netfs with cache enabled, withdraw the backend, and verify graceful fallback.
