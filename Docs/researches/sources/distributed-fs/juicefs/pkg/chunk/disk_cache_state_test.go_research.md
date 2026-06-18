## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state_test.go

Purpose: tests disk cache health-state transitions for different numbers of cache directories.

Important tests and control flow: helper `setState` swaps a `cacheStore` into a requested `dcState`. `testDiskCacheState` creates a cache manager, manipulates stores through normal/unstable/down states, triggers events and IO outcomes, and verifies manager length/removal behavior. `TestDiskCacheState` runs the helper for multiple cache counts.

State and persistence: uses temp cache directories and live `cacheStore` goroutines. State changes are in-memory but affect cache manager store maps and consistent hash membership.

Dependencies and integration points: depends on `newCacheManager`, `dcState` implementations, and testing assertions.

Risks and test signals: protects the degraded-disk removal path. Because production code has background goroutines and timers, tests may require careful sleeps or direct state injection to avoid flakes.
