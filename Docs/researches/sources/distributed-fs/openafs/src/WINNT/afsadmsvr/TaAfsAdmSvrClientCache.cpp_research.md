# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.cpp

Purpose: implements the client-side per-cell object property cache for admin-server clients.

Important APIs/types/functions: `CELLCACHE` holds a cell ASID, a hash list of `ASOBJPROP` entries keyed by object ASID, and a reference count. `CreateCellCache()`/`DestroyCellCache()` manage cache lifetime. `GetCachedProperties()` looks up an object. `UpdateCachedProperties()` inserts or replaces cached properties and notifies listeners. `RefreshCachedProperties()` overloads fetch one object or a list from the server using property versions to request only out-of-date data. Hash callbacks compare/hash cell and object ASIDs.

Control flow: cell open creates/increments a cache. Property getters call refresh, which builds version inputs from cached entries, performs `AfsAdmSvr_GetObject(s)` inside RPC exception handling, and updates local cache for returned objects. Destroy decrements reference count and frees all cached `ASOBJPROP` allocations when it reaches zero.

State/persistence: process-global `l` stores all cell caches and their hash key. State is in memory only and tied to ASIDs from a server process.

Dependencies/integration: depends on `HASHLIST`, `asc_Enter/Leave` critical section, generated RPC functions, object notification helpers, and OpenAFS allocation macros.

Risks/test signals: returned pointers from `GetCachedProperties()` are only stable while cache entries remain; callers copy immediately in most paths. Reference-count and hash-list cleanup are key. Tests should cover multiple opens of the same cell, list refresh with version lParams, deleted/no-object properties, notification firing, destroy while listeners exist, and RPC failures.
