# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/cache.go

This file maps `types.CacheMetrics` returned by nydusd into Prometheus gauges. `CacheMetricsCollector` carries one metrics payload, image ref, and daemon ID. `CacheMetricsVecCollector` iterates a slice of collectors.

`Collect` guards nil metrics, computes a prefetch duration value, and sets TTL-backed gauges for partial/whole hits, total cache requests, entry count, prefetched bytes, prefetch request count, workers, unmerged chunks, cumulative prefetch time, total duration, and buffered backend size. Labels are keyed by image ref. It depends on metric definitions in `pkg/metrics/data` and daemon metrics schemas from `pkg/daemon/types`.

There is no persistence; state is held in Prometheus collectors, with TTL cleanup managed by the metric type. Integration points include `metrics.Server.CollectCacheMetrics`, daemon `GetCacheMetrics`, and the registry. Risks include the duration formula subtracting begin and end timestamps while adding `PrefetchCumulativeTimeMillis` to both sides, which cancels cumulative time and may indicate a bug; also no delete path for stale image labels beyond TTL. There are no direct tests for this collector.
