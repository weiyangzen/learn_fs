## sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.h

**Purpose:** Declares and defines the `StatFsCache` structure and lifecycle helpers for cached filesystem free-space reporting.

**Important APIs/types/functions:** Defines `struct StatFsCache` with `App*`, `RWLock`, `Time lastUpdateTime`, `cachedSizeTotal`, and `cachedSizeFree`. Inline APIs include `StatFsCache_init`, `construct`, and `destruct`; external API is `StatFsCache_getFreeSpace`.

**Control flow:** Construction allocates and initializes lock/time state. Consumers call `getFreeSpace` to obtain cached or freshly queried totals. Destruction frees the wrapper object.

**State and persistence behavior:** State is in-memory only and starts with zero time to mark the cache uninitialized. Cached totals are stored in bytes.

**Dependencies and integration points:** Depends on BeeGFS storage errors, `RWLock`, `Time`, and `os_kmalloc`. Integrated into filesystem statfs paths through the app object.

**Risks:** `StatFsCache_destruct` frees without explicit lock uninit; this relies on `RWLock` not requiring teardown or on module conventions. Callers must not use the cache after `App` teardown. Cache validity depends on configuration read by the `.c` implementation.

**Test signals:** Construct/destruct under leak checking, verify zero-time initial miss, test cached byte outputs, and run lockdep around concurrent statfs access.
