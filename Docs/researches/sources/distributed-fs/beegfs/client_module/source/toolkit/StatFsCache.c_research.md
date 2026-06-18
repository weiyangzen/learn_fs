## sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.c

**Purpose:** Implements a small cache for `statfs` free-space totals to avoid querying every storage target on each syscall.

**Important APIs/types/functions:** Implements `StatFsCache_getFreeSpace`.

**Control flow:** Reads `tuneStatFsCacheSecs` from config. If caching is enabled and `lastUpdateTime` is nonzero and not expired, returns cached total/free values under the read lock. Otherwise it releases the lock, calls `FhgfsOpsRemoting_statStoragePath` with `ignoreErrors=true`, zeroes outputs on failure, and on success updates cached values/time under the write lock.

**State and persistence behavior:** Caches total/free byte counts and last update time in memory. Values are approximate and may be concurrently refreshed by multiple threads; the code intentionally allows racing remote calls and last-writer-wins cache updates.

**Dependencies and integration points:** Depends on `App` config and `FhgfsOpsRemoting_statStoragePath`, which aggregates storage target stats. Used by VFS statfs handling.

**Risks:** Cache staleness is controlled only by config seconds and may hide fast capacity changes. Ignoring per-target errors can produce partial totals. Concurrent misses can fan out multiple expensive stat-storage requests. Failed refresh clears caller outputs but does not invalidate old cached values explicitly.

**Test signals:** Test disabled cache, first miss, hit before expiry, refresh after expiry, remoting failure, partial target errors, and concurrent statfs calls.
