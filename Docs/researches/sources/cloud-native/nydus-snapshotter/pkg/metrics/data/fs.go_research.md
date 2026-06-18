# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/fs.go

This file declares filesystem-related Prometheus metrics and custom histogram descriptors. TTL-backed gauges track total read bytes, read hits, and read errors by image ref. `TotalHungIO` tracks the total number of hung IOs. `MetricHists` defines cumulative read block size and read latency histograms with bucket boundaries and functions that extract counters from `types.FsMetrics`.

State is held in metric objects and histogram collectors. The histogram descriptors are registered directly by the custom registry and are populated by `FsMetricsCollector`, which saves generated const histograms into each `MetricHistogram`.

Integration points include nydusd metrics JSON, `metrics/types.MetricHistogram`, and metrics server collection. Risks include strict expectation that counter slice lengths equal bucket lengths, image-ref label cardinality, and metric help/bucket changes affecting dashboards. `FsMetricsCollector` reads `FopHits` and `FopErrors` by operation index, so mismatched nydusd schemas can cause panics before histogram validation. No direct tests cover these definitions.
