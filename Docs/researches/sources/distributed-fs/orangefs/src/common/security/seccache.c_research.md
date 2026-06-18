<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.c -->
# sources/distributed-fs/orangefs/src/common/security/seccache.c

## Purpose
Implements a generic locked security cache used by capability, credential, and certificate caches. It provides chained hash buckets, per-entry expiration, configurable properties, statistics, and implementation-specific callbacks.

## Important APIs, Types, And Functions
Exports `PINT_seccache_new`, `PINT_seccache_set`, `PINT_seccache_get`, `PINT_seccache_expired_default`, `PINT_seccache_lock`, `PINT_seccache_unlock`, `PINT_seccache_reset_stats`, `PINT_seccache_cleanup`, `PINT_seccache_lookup`, `PINT_seccache_lookup_cmp`, `PINT_seccache_insert`, and `PINT_seccache_remove`. Internal helpers print stats, wrap generic mutex calls, and remove expired entries from one or all chains.

## Control Flow
New cache allocation initializes a lock, method table, defaults, a hash-table array, one linked list per bucket, and a sentinel entry for each chain. Lookup computes the method-defined index, searches under lock, unlocks, checks expiration, removes expired hits, refreshes live hits, updates stats, and returns the entry. Insert allocates an entry, removes expired entries in the target chain, sets expiration, locks, adds to the list head, unlocks, and updates stats. Remove locks, searches/removes by entry data, unlocks, and calls the cache-specific cleanup method.

## State And Persistence
All state is in memory: description, callbacks, lock, property values, stats, and linked-list hash buckets. No entry or size limits are actually enforced by insertion despite stored properties.

## Dependencies And Integration Points
Depends on `llist`, `gen-locks`, PVFS types/errors, and gossip. Specialized caches provide hash, compare, expiration, cleanup, and debug methods.

## Risks And Test Signals
`PINT_seccache_set` locks `cache->lock` before checking `cache` for NULL, insert failure can return while still holding the lock, stats are updated partly outside locks, lookup returns mutable entry pointers after unlocking, and configured entry/size limits are unused. Tests should cover allocation failure cleanup, lookup hit/miss/expired, property get/set, insert failure paths, concurrent lookup/remove stress, sentinel handling, and stats frequency output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.c -->
