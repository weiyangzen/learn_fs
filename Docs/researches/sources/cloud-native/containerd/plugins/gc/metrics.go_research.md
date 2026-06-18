# sources/cloud-native/containerd/plugins/gc/metrics.go

## Purpose
Defines Prometheus-style metrics for the garbage collection scheduler.

## Important APIs, Types, And Functions
Package globals `collectionCounter` and `gcTimeHist` track collection counts by status and collection duration. `init` creates and registers the `containerd_gc` metrics namespace.

## Control Flow
At package init, metrics are created and registered. The scheduler updates them after successful or failed collection attempts.

## State And Persistence
Metrics are in-memory process counters/timers exported through the configured metrics server.

## Dependencies And Integration Points
Uses `docker/go-metrics`; consumed by `scheduler.go`. Exposed by the metrics HTTP server if configured.

## Risks
Metrics registration happens globally and can conflict if package init is repeated in unusual test setups.

## Test Signals
No direct tests. Scheduler tests exercise paths that update metrics, but do not assert metric values.
