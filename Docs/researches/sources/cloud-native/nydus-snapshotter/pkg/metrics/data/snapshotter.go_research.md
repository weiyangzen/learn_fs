# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/snapshotter.go

This file declares snapshotter-level Prometheus metrics. It defines default duration buckets for snapshot operation histograms, then declares gauges for cache usage, CPU usage, memory usage, CPU system/user time, fd count, runtime, thread count, and cache cleanup counters/gauges for deleted blobs, in-use blobs, and deletion errors.

These metrics are registered by `metrics/registry`. Snapshot operation histograms are populated through `collector.NewSnapshotMetricsTimer`, while process and cache resource gauges are populated by `SnapshotterMetricsCollector`. Cache cleanup metrics are updated by cleanup code outside this subset.

State is metric-only. Integration points include snapshotter operation handlers, process `/proc` sampling, disk usage scanning, and cache cleanup. Risks include units encoded in names/help text, bucket choices affecting alerting precision, and cleanup counters needing consistent caller updates. There are no direct tests in this subset; correctness depends on collector behavior and Prometheus registration.
