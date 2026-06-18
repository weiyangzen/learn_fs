## sources/distributed-fs/openafs/src/libafscp/afscp_fid.c

Purpose: Owns FID allocation helpers and status cache behavior for `libafscp`. It converts `AFSFetchStatus` into POSIX `stat`, stores and invalidates cached fetch status entries, and exposes callback waiting helpers.

Important APIs and functions: `afscp_MakeFid`, `afscp_DupFid`, `afscp_FreeFid`, `afscp_WaitForCallback`, `afscp_GetStatus`, `afscp_Stat`, `afscp_CheckCallBack`, `_StatInvalidate`, `_StatStuff`, and `afscp_StoreStatus`.

Control flow: FID constructors allocate shallow structures that point at existing `afscp_cell` objects. `afscp_GetStatus` first searches `volume->statcache`; if present, it copies cached status, wakes waiters, and returns. On a miss, it walks volume servers and connections, calls `RXAFS_FetchStatus`, then records the returned callback and status. `_StatStuff` inserts a newly allocated `afscp_statent` in the tree. `_StatInvalidate` removes an entry and either frees it immediately or marks it for cleanup after waiters leave. `afscp_WaitForCallback` waits on the cached entry's condition variable until invalidation or timeout.

State and persistence: Maintains per-volume process-local stat caches keyed by vnode and unique. Cache entries contain mutexes, condition variables, waiter counts, cleanup flags, and copied AFS status. No disk persistence.

Dependencies and integration: Uses `tsearch` trees, pthread synchronization, RXAFS file server calls, volume/server lookup, and callback tracking from `afscp_callback.c`. POSIX `stat` conversion integrates with consumers expecting local metadata semantics.

Risks: `_StatStuff` calls `tsearch` and unconditionally overwrites the slot with a new allocation when `cached != NULL`; if an entry already existed, the old object can be orphaned. Comparator keys ignore volume and cell, relying on per-volume trees. `afscp_CheckCallBack` computes an unsigned-ish remaining expiration value that can underflow if expired. Thread-safety is partial: tree operations themselves are not globally locked.

Test signals: Cover cache hit and miss, callback invalidation with and without waiters, timed waits, `stat` mode mapping for files/directories/symlinks, store-status cache refresh, concurrent lookup and invalidation, and missing volume failures.
