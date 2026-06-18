<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.c -->
# sources/distributed-fs/orangefs/src/common/misc/tcache.c

## Purpose
Implements OrangeFS's generic timeout cache. It stores caller-owned payloads behind opaque keys, combines `quickhash` lookup with a least-recently-used `quicklist`, supports entry expiration, and provides soft/hard limit reclamation for higher-level caches such as client capability caching.

## Important APIs, Types, And Functions
The public API is `PINT_tcache_initialize`, `PINT_tcache_finalize`, `PINT_tcache_get_info`, `PINT_tcache_set_info`, `PINT_tcache_insert_entry`, `PINT_tcache_insert_entry_ex`, `PINT_tcache_lookup`, `PINT_tcache_reclaim`, `PINT_tcache_delete`, and `PINT_tcache_refresh_entry`. Internal helpers are `check_expiration` and `tcache_lookup_oldest`. Callers provide key comparison, key hashing, and payload cleanup callbacks.

## Control Flow
Initialization allocates a `PINT_tcache`, installs callbacks, sets defaults, creates the hash table, and initializes the LRU list. Inserts optionally reclaim expired entries once the soft limit is reached, evict the oldest entry at the hard limit, allocate a cache entry, set an explicit or refreshed expiration time, add it to both hash and LRU structures, and increment `num_entries`. Lookup searches the hash table, reports expiration status, and moves the entry to the LRU tail. Reclaim walks the LRU head forward, deleting expired entries until it reaches a live entry or the reclaim percentage cap.

## State And Persistence
All state is in memory: timeout options, entry counts, hash buckets, and LRU links. Payload ownership transfers to the cache at insert time and `free_payload` is called on disabled inserts, deletes, evictions, reclaim, and finalize. No disk or configuration persistence is performed here.

## Dependencies And Integration Points
Depends on `pvfs2-internal.h` error codes/time helpers, `quickhash`, `quicklist`, and `gossip` for diagnostics. The cache is deliberately not thread-safe; wrappers such as `client-capcache.c` provide their own mutexes.

## Risks And Test Signals
Risks include no duplicate-key rejection, caller-after-lookup lifetime hazards, no internal locking, option combinations where `soft_limit` exceeds `hard_limit`, null pointer assumptions for `purged` and `tcache`, and time arithmetic edge cases. Tests should cover disabled-cache insert cleanup, expiration status, refresh behavior, soft-limit reclaim, hard-limit LRU replacement, explicit expiration insertion, finalize freeing all payloads, and invalid option handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.c -->
