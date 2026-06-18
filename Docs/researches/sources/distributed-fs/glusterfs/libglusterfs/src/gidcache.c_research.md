# sources/distributed-fs/glusterfs/libglusterfs/src/gidcache.c

## Purpose
`gidcache.c` implements a small set-associative timeout cache for auxiliary group lists. It avoids repeated group-list lookups for the same id/uid/gid tuple while preserving correctness when credentials change.

## Important APIs, Types, and Functions
- `gid_cache_init(cache, timeout)`: initializes lock, max age, bucket count, and clears entries.
- `gid_cache_reconf(cache, timeout)`: changes the cache timeout under lock.
- `gid_cache_lookup(cache, id, uid, gid)`: finds a live entry and returns it while keeping the cache locked.
- `gid_cache_release(cache, agl)`: unlocks after a successful lookup.
- `gid_cache_add(cache, gl)`: inserts or updates an entry, reusing expired/matching entries and maintaining LRU order within a bucket.

## Control Flow
Lookup hashes `id` to a bucket, scans up to `AUX_GID_CACHE_ASSOC` entries in LRU order, skips empty entries, requires matching id plus matching uid/gid, and returns only if `gf_time()` is before `gl_deadline`. It intentionally leaves the lock held so the caller can copy the returned `gid_list_t` without an extra allocation or race, then calls `gid_cache_release()`.

Add ignores null lists and disabled timeout (`gc_max_age == 0`). It scans for an entry with the same id or the first free slot, frees any reused list, evicts the oldest slot when the bucket is full, slides later populated entries down, and stores the new entry at the newest populated position with a refreshed deadline.

## State and Persistence
The cache is entirely in memory. Entries own `gl_list` pointers transferred from the caller into the cache. Reconfiguration changes only future lookup/add behavior; entries may remain but become unusable when timeout is zero.

## Dependencies and Integration Points
Depends on `gidcache.h`, `mem-pool.h`, `common-utils.h`, Gluster locks, `GF_FREE`, and `gf_time()`. It integrates with authentication/request contexts that need supplemental groups for a process or client identity.

## Risks and Edge Cases
- Successful lookup returns with the cache lock held; caller must release promptly or block all cache operations.
- Lookup breaks on credential mismatch or expiration and does not reclaim; add performs reuse/eviction.
- `gid_cache_add()` takes ownership of `gl->gl_list`; callers must not free it after successful add.
- Timeout reconfiguration to zero disables new inserts but does not immediately free old entries.

## Test Signals
Test bucket hashing, LRU slide/eviction, update of expired same-id entries, uid/gid mismatch invalidation, timeout zero behavior, lookup lock/release discipline, and memory ownership of `gl_list`.
