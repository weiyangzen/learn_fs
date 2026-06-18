# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/daemon.go

This file defines collectors for daemon lifecycle and identity metrics. `DaemonEventCollector` increments event counters by daemon state string. `DaemonInfoCollector` adjusts the daemon count gauge by version and a signed value. `DaemonResourceCollector` sets daemon RSS by daemon ID. `DaemonImageCollector` maintains a daemon-to-image gauge and can delete its label values.

State is stored in Prometheus metrics. Integration points include manager process start, recovery, destruction, liveness monitor death events, daemon RAFS add/remove, and metrics server daemon RSS polling. The `Version` pointer is protected by daemon locks in callers when necessary, not internally.

Risks include daemon count gauges requiring balanced positive and negative calls, nil version silently skipping count updates, RSS values being whatever the caller computed, and image-info labels needing explicit deletion on RAFS removal. There are no direct unit tests for these collectors in the subset, but the functions are simple wrappers around metric vectors.
