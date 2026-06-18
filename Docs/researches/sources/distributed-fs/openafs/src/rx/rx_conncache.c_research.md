# Research: sources/distributed-fs/openafs/src/rx/rx_conncache.c

## sources/distributed-fs/openafs/src/rx/rx_conncache.c

### Purpose
`rx_conncache.c` implements a small process-local cache of client RX connections keyed by remote address, port, service, security object, and security index.

### Important Functions and Types
- `rx_connParts_t` captures the cache key.
- `cache_entry_t` stores queue link, connection pointer, key parts, `inUse` channel count, and error marker.
- Internal helpers: `rxi_CachedConnectionsEqual`, `rxi_FindCachedConnection`, `rxi_AddCachedConnection`, and `rxi_GetCachedConnection`.
- Public functions: `rx_GetCachedConnection`, `rx_ReleaseCachedConnection`, and `rxi_DeleteCachedConnections`.

### Control Flow
`rx_GetCachedConnection` builds a key and calls the internal getter. Under `rxi_connCacheMutex` on pthread builds, the cache is scanned for a matching non-error entry with `inUse < RX_MAXCALLS`; on hit, `inUse` is incremented and the existing connection is returned. On miss, `rx_NewConnection` creates a new connection and `rxi_AddCachedConnection` prepends a cache entry and sets `RX_CONN_CACHED`.

`rx_ReleaseCachedConnection` destroys non-cached connections directly. For cached connections, it decrements `inUse`; if `rx_ConnError` is set, the entry is marked errored and destroyed once no users remain. `rxi_DeleteCachedConnections` is intended for `rx_Finalize` and destroys all cached connections.

### State and Persistence
The cache is an in-memory global `opr_queue`. It persists until RX finalization and has no durable storage.

### Dependencies and Integration Points
Depends on `rx_NewConnection`, `rxi_DestroyConnection`, `rx_ConnError`, `RX_MAXCALLS`, `RX_CONN_CACHED`, and `opr_queue`. It is an optimization for callers that repeatedly contact the same service/security tuple.

### Risks and Edge Cases
- `malloc` failure in `rxi_AddCachedConnection` silently leaves a connection flagged as cached even without an entry, which can make release leak or fail to find it.
- `inUse` tracks handed-out uses, not necessarily live RX calls; caller release discipline is critical.
- Only pthread builds lock the cache; non-pthread/LWP assumes cooperative execution.
- Cache search is linear.

### Test Signals
Tests should cover cache hit/miss behavior, reuse up to `RX_MAXCALLS`, errored connection retirement, non-cached release behavior, and finalization cleanup. A memory-failure test for `rxi_AddCachedConnection` would expose the flag/entry inconsistency.
