# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/types/types.go

This file defines filesystem operation indexes and a custom Prometheus histogram collector. The `Fop` enum assigns operation positions such as Getattr, Open, Read, Lookup, Readdir, Access, and BatchForget. `GetMaxFops` and `MakeFopBuckets` expose operation count and bucket values.

`MetricHistogram` stores a descriptor, bucket boundaries, a function that extracts counters from `types.FsMetrics`, and the last generated const histograms. `ToConstHistogram` validates counter and bucket lengths, accumulates cumulative bucket counts and weighted sum, then builds a `prometheus.MustNewConstHistogram`. `Clear`, `Save`, `Describe`, and `Collect` implement state management and the Prometheus collector interface.

State is in-memory `constHists`, cleared and repopulated by filesystem metrics collection. Integration points include `metrics/data/fs.go` histogram definitions and `FsMetricsCollector`. Risks include counter/bucket length mismatch, cumulative histogram assumptions, weighted sum interpretation, no locking around `constHists`, and operation indexes needing to match nydusd's metrics arrays. There are no direct tests for this file in the subset.
