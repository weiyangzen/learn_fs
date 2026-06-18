## sources/cloud-native/buildkit/solver/combinedcache.go

Purpose: combines multiple cache managers, typically remote/imported caches plus a main writable cache, behind one `CacheManager` interface.

Important APIs/types/functions: `NewCombinedCacheManager`, `combinedCacheManager.ID`, `ReleaseUnreferenced`, `Query`, `Load`, `Save`, and `Records`. `ID` hashes the comma-joined child manager IDs. `Load` can promote loaded results from a non-main cache into the main cache.

Control flow: `ReleaseUnreferenced`, `Query`, and `Records` run child managers in parallel with `errgroup`. Query/record maps deduplicate by cache key or result id, preferring main manager entries. `Load` calls `LoadWithParents` on the record's owning manager, saves loaded parent/result chain into main when needed, releases all non-returned results, and returns the first loaded result.

State and persistence: no independent storage; delegates to child managers. It may persist promoted results into `main`.

Dependencies and integration points: used by solver when combining local cache with imported cache sources.

Risks and test signals: parallel goroutines use `context.TODO` for query records rather than caller cancellation in some paths. If `main` is nil, `Save` is a no-op returning nil key. No direct tests in this subset; cache tests cover underlying manager semantics.
