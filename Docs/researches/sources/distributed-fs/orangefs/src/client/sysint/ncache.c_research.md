# sources/distributed-fs/orangefs/src/client/sysint/ncache.c
## sources/distributed-fs/orangefs/src/client/sysint/ncache.c

**Purpose:** Implements the client-side name cache mapping `(parent object ref, entry name)` to child `PVFS_object_ref` on top of `PINT_tcache`.

**APIs and control flow:** `PINT_ncache_initialize()` creates the tcache, reads `PVFS2_NCACHE_TIMEOUT` or uses 60 seconds, sets soft/hard/reclaim defaults, and initializes perf counters. `PINT_ncache_get_cached_entry()` builds an `ncache_key`, looks it up, copies the cached child ref when valid, and records hit/miss counters. `PINT_ncache_update()` skips work if disabled, allocates and copies a payload/name, then replaces or inserts the tcache entry and updates purge/replacement counters. `PINT_ncache_invalidate()` deletes a matching entry. Hashing sums entry-name bytes plus parent handle/fsid.

**State and dependencies:** Global `ncache`, `ncache_mutex`, and `ncache_pc`; depends on tcache, perf counters, gossip, PVFS object refs, and cached-config-related utilities.

**Risks and tests:** In `PINT_ncache_get_cached_entry()`, a miss path unlocks and then calls `PINT_perf_count`, so the perf counter can be touched outside the mutex. `PINT_ncache_update()` calls `PINT_tcache_get_info` without locking `ncache_mutex`. The null-payload free function assumes valid payload/name. Tests should cover timeout expiry, disabled cache, parent disambiguation, replacement, invalidation, duplicate names under different parents, and concurrent lookup/update.
