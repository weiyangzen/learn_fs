<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go

## Purpose
Implements a small TTL cache abstraction used by the NFS CSI driver, notably for volume deletion idempotency. It is a reduced version of an Azure cache pattern containing only methods used in this driver.

## Important APIs, Types, and Functions
Public types are `CacheReadType`, `GetFunc`, `Resource`, `TimedCache`, and `DisabledCache`. Internal `CacheEntry` stores key, data, per-entry mutex, and creation time. Key functions are `NewTimedCache()`, `TimedCache.getInternal()`, `TimedCache.Get()`, `TimedCache.Set()`, `DisabledCache.Get()`, and `DisabledCache.Set()`. Storage uses `k8s.io/client-go/tools/cache.Store`.

## Control Flow, State, and Persistence
`NewTimedCache` requires a getter and can return either a TTL-backed cache or disabled cache. `TimedCache.Get` creates a placeholder entry when missing, locks the entry, returns cached data if non-nil and not expired, otherwise calls the getter and updates `Data` and `CreatedOn`. `Set` inserts a fresh cache entry. State is in-memory only and lost on driver restart.

## Dependencies and Integration Points
It integrates with controller deletion flow through `Driver.volDeletionCache`, where a cached non-nil marker lets repeated `DeleteVolume` calls return success without redoing NFS deletion. It depends on Go synchronization, time, and Kubernetes cache store key functions.

## Risks and Test Signals
Risks include `Set` using `Store.Add` instead of update semantics, nil data never being considered cached, no deletion API, TTL-based idempotency only surviving process lifetime, and type assertions in `cacheKeyFunc`. Signals are concurrent `Get` calls invoking the getter once per expired key, TTL expiry causing refresh, and deletion retries being skipped within the cache window.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go -->
