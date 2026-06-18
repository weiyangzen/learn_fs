## sources/distributed-fs/juicefs/pkg/chunk/mem_cache.go

Purpose: in-memory implementation of `CacheManager` behavior for disabled/memory cache modes and disk-cache fallback.

Important APIs/types/functions: `memItem` stores access time and `*Page`. `memcache` tracks capacity, max items, used bytes, map entries, eviction policy, expiry, and metrics. Methods implement cache/store contract: `cache`, `remove`, `load`, `exist`, `stats`, `usedMemory`, `cleanup`, `cleanupExpire`, and no-op/unsupported staging methods.

Control flow and state: `cache` acquires page references, records metrics, and evicts using two-random sampling if full and eviction is enabled. `load` and `exist` refresh access time. A finalizer releases all retained pages if the memcache is collected. Expiry cleanup periodically removes old entries.

Dependencies and integration points: used by `newCacheManager` when `CacheDir == "memory"`, cache size is disabled, no cache dirs exist, or disk cache becomes empty. Integrates with `Page` refcounting and cache metrics.

Risks and test signals: staging/writeback is unsupported in memory cache mode, so config must disable writeback before selecting it. Refcount leaks are possible if entries are not released on eviction/removal. Eviction is approximate and map-order dependent.
