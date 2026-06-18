<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_volume.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_volume.c

## Purpose
Manages FS-Cache volume cookies. A volume groups data-object cookies under a cache and volume key, handles backend volume acquisition/free, collision waiting, access pinning, withdrawal, relinquish coherency data, and procfs display.

## Important APIs, Types, And Functions
Exports `fscache_try_get_volume()`, `fscache_end_volume_access()`, `__fscache_acquire_volume()`, `fscache_put_volume()`, `__fscache_relinquish_volume()`, and `fscache_withdraw_volume()`. Internal functions include `fscache_alloc_volume()`, `fscache_hash_volume()`, `fscache_create_volume()`, `fscache_create_volume_work()`, `fscache_unhash_volume()`, and `fscache_free_volume()`.

## Control Flow
Acquire looks up a cache by name, allocates a variable-sized `fscache_volume` with coherency data, builds a length-prefixed padded key, hashes it, links it into proc/cache lists, inserts it into a bucket, and schedules backend volume creation. Hash collision with a non-relinquished equivalent fails with `-EBUSY`; collision with a relinquishing volume sets pending bits and waits for wakeup. `fscache_create_volume()` serializes backend `acquire_volume()` via `FSCACHE_VOLUME_CREATING` and can wait synchronously. Refcount drop calls `fscache_free_volume()`, which may invoke backend `free_volume()`, unlinks proc/cache state, unhashes, frees memory, and drops the cache reference.

## State And Persistence
Volume identity is `(cache, key_hash, key bytes)`. Runtime state includes `ref`, `n_accesses`, `n_cookies`, flags, `cache_priv`, coherency bytes, and proc/hash/list linkage. Access pinning prevents cache withdrawal while a volume is in use.

## Dependencies And Integration Points
Integrates with cache lookup/refcounting, backend cache ops, `fscache_addremove_sem`, cookie acquisition, procfs seq output, and FS-Cache stats. Cookie code pins volumes and increments `volume->n_cookies`.

## Risks
Potential hazards include collision wait deadlocks, incorrect wake of pending colliders, freeing backend volume while accesses remain, and mismatched `n_cookies` accounting. Volume withdrawal decrements the artificial access pin and waits for zero, so callers must balance access pins.

## Test Signals
Acquire/relinquish identical volume keys concurrently, simulate backend create failure, withdraw active volumes, and verify proc `volumes` output. Check collision stats and `n_cookies` transitions when cookies are acquired/relinquished.
