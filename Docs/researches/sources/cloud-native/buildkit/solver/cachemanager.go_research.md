## sources/cloud-native/buildkit/solver/cachemanager.go

Purpose: implements the main solver cache manager that maps cache keys to persisted metadata and actual result storage.

Important APIs/types/functions: `NewInMemoryCacheManager`, `NewCacheManager`, `ReleaseUnreferenced`, `Query`, `Records`, `Load`, `LoadWithParents`, `Save`, `ensurePersistentKey`, `getIDFromDeps`, and `rootKey`. `LoadedResult` carries a loaded result with its cache result and key.

Control flow: creation runs `ReleaseUnreferenced` to prune metadata for missing result blobs. `Query` intersects dependency links by input/output/digest/selector and repairs missing links across dependency alternatives. Root queries check root key existence. `Save` persists the actual result, stores result metadata, and recursively persists dependency links. `LoadWithParents` optionally asks result storage for parent results and filters them through cache key ancestry.

State and persistence: mutex protects manager operations. Metadata persists through `CacheKeyStorage`; result payloads persist through `CacheResultStorage`. Cache key ids may be deterministic root ids or generated ids based on dependency graph intersection.

Dependencies and integration points: called by scheduler edges for cache probing, loading, and saving. Emits trace logs with cache operation fields.

Risks and test signals: `filterResults` appears to check `m[id]` while iterating cache results and may be sensitive to whether result-storage parent maps are keyed by cache-key id or result id. `ReleaseUnreferenced` ignores `Release` errors. Cache tests cover common graph/link behavior and deletion recovery.
