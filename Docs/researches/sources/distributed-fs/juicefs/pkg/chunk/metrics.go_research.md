## sources/distributed-fs/juicefs/pkg/chunk/metrics.go

Purpose: declares and registers Prometheus metrics for cache manager operations.

Important APIs/types/functions: `cacheManagerMetrics` contains counters for cache drops/writes/evicts/write bytes/stage write bytes, a histogram for cache write latency, and gauges for staged blocks and staged bytes. `newCacheManagerMetrics` initializes and registers metrics. `registerMetrics` also adds a gauge function `staging_writing_blocks` backed by global `stagingBlocks`.

State and persistence: metrics are process-local Prometheus collectors; no disk persistence.

Dependencies and integration points: used by disk and memory cache implementations and registered into the supplied Prometheus registerer from `NewCachedStore`.

Risks and test signals: repeated registration into the same registry can panic through `MustRegister`. Tests read collectors directly to validate stage/cache counters. Metric names are user-facing operational contracts.
