## sources/cloud-native/buildkit/solver/cache_test.go

Purpose: unit tests for in-memory cache manager/storage behavior and cache-key graph semantics.

Important APIs/types/functions: helper constructors `depKeys`, `testCacheKey`, `testCacheKeyWithDeps`, `expKey`, `dgst`, and `testResult`. Tests include `TestInMemoryCache`, `TestInMemoryCacheSelector`, `TestInMemoryCacheSelectorNested`, `TestInMemoryCacheReleaseParent`, `TestInMemoryCacheRestoreOfflineDeletion`, and `TestCarryOverFromSublink`.

Control flow: tests save root and dependent cache keys, query by digest/input/output/selectors, load records, release backing results, and verify graph pruning or retained links. Selector tests prove that dependency selectors constrain matches and that alternate sublinks can carry cache matches forward.

State and persistence: uses in-memory cache key and result storage. Release tests mutate storage to simulate deleted results and offline restore.

Dependencies and integration points: exercises `cacheManager`, `CacheKey`, in-memory storage implementations, and dummy results.

Risks and test signals: strong coverage for query/link intersection semantics, selector matching, result release cleanup, and restoration after result storage changes. It does not test bbolt directly except through the separate conformance test.
