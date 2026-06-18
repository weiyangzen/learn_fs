# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/serve.go

This file implements periodic metrics collection. `Server` holds managers, snapshotter collectors, filesystem/cache/inflight vector collectors, and collection intervals. Options configure managers, metric interval, and hung-IO interval, rejecting negative durations. `NewServer` creates vector collectors and one snapshotter resource collector per manager cache directory.

Collection methods walk managers and daemons. `CollectDaemonResourceMetrics` samples daemon RSS. `CollectFsMetrics` polls fusedev daemons in `RUNNING` state and collects per-RAFS filesystem metrics. `CollectCacheMetrics` polls cache metrics for each daemon/RAFS. `CollectInflightMetrics` polls fusedev daemons and counts hung IOs. `StartCollectMetrics` runs two tickers: one for fs/cache/daemon/snapshotter metrics and one for inflight metrics, exiting on context cancellation.

State is rolling metric values plus collector baselines. Integration points include manager daemon lists, daemon client metrics APIs, RAFS caches, `/proc`, disk usage, and Prometheus collectors. Risks include ticker creation with zero intervals if not configured, sid handling differing from fscache readiness logic, skipped non-running daemons based on cached state, and no direct tests for server loops.
