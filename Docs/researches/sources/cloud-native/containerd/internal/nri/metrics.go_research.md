# sources/cloud-native/containerd/internal/nri/metrics.go

## Purpose
Exposes NRI plugin activity metrics for Prometheus-compatible collection.

## Important APIs, Types, And Functions
Global metrics include plugin invocation counter, latency timer, adjustment counter, and active plugin gauge. `nriMetrics` implements `nri.Metrics` with `RecordPluginInvocation`, `RecordPluginLatency`, `RecordPluginAdjustments`, and `UpdatePluginCount`. `getErrorType` normalizes context and gRPC errors.

## Control Flow
Package init registers a `containerd_nri` metrics namespace. Recording methods update labels for plugin, operation, status/error, adjustment type, or plugin count.

## State And Persistence
Metrics are process-global in-memory counters/gauges/histograms exposed by the metrics registry.

## Dependencies And Integration Points
Uses docker/go-metrics, gRPC status/codes, context errors, and the NRI adaptation metrics interface.

## Risks
Global metric registration can conflict in repeated test processes or embedded uses. Label cardinality depends on plugin names and operation strings.

## Test Signals
`metrics_test.go` checks invocation labels, latency histogram sum/count, adjustment counts, and active plugin gauge.
