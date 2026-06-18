# sources/distributed-fs/orangefs/src/client/sysint/acache.c
## sources/distributed-fs/orangefs/src/client/sysint/acache.c

**Purpose:** Implements the client-side attribute cache for OrangeFS/PVFS object attributes and logical file size on top of the generic `PINT_tcache`.

**APIs and control flow:** `PINT_acache_initialize()` creates the tcache, sets a 60-second payload timeout, applies soft/hard/reclaim defaults, and initializes perf counters. `PINT_acache_get_cached_entry()` looks up by `PVFS_object_ref`, treats expired/missing attrs as misses, separately checks dynamic size freshness with a 10-second timeout, copies valid attrs, and returns attr/size status. `PINT_acache_update()` copies incoming attrs into an `acache_payload`, excludes capabilities and dirent-count size arrays, records size and update time if supplied, and inserts/replaces via `load_payload()`. Invalidation deletes whole entries or strips the `PVFS_ATTR_DATA_SIZE` bit.

**State and dependencies:** Global state includes `acache`, `acache_mutex`, and perf counter `acache_pc`. It depends on `tcache`, object-attr copy/free helpers, time utilities, gossip logging, and client perf rollover timers.

**Risks and tests:** Timeouts are hard-coded despite TODOs for env overrides. `PINT_acache_finalize()` assumes initialized pointers. Size validity depends on attr mask discipline by callers. Tests should cover stale static attrs, stale dynamic size, update replacement, size-only invalidation, masked-out capability/dirent count, disabled cache behavior via tcache options, and perf counter updates.
