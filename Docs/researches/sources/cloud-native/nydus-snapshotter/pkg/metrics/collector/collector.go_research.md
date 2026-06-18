# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/collector.go

This file provides factory functions and a shared `Collector` interface for Prometheus metric collectors. It constructs daemon event/info/image collectors, filesystem metrics collectors, inflight metrics collectors, snapshotter resource collectors, snapshot operation timers, and cache metrics collectors.

`NewSnapshotterMetricsCollector` is the only factory with substantive work: it samples the current process stat for the supplied PID and stores it as the baseline for later CPU/resource calculations. Other constructors mostly package values into structs. `NewSnapshotMetricsTimer` returns a Prometheus timer that observes elapsed time in milliseconds through `CollectSnapshotMetricsTimer`.

State is limited to constructed collector objects and the initial process stat baseline. Integration points include daemon event handling, daemon lifecycle metrics, filesystem/cache/inflight polling, snapshotter operation instrumentation, and Prometheus histograms. Risks include factory calls failing when `/proc` stats are unavailable, process stat baseline staleness, and no direct tests for constructor wiring. Most behavior is validated through downstream collector tests or runtime metric scraping rather than this file.
