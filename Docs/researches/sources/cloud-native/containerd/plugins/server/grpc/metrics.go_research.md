# sources/cloud-native/containerd/plugins/server/grpc/metrics.go

## Purpose
Registers gRPC metrics plugins for Prometheus and OpenTelemetry instrumentation.

## Important APIs, Types, And Functions
`metricsConfig` controls Prometheus handling-time histograms. The `grpc-prometheus` plugin returns `*grpc_prometheus.ServerMetrics`; the `grpc-otel` plugin returns an `otelgrpc` stats handler.

## Control Flow
Prometheus init creates optional histogram settings, registers metrics with the default Prometheus registry, and returns the metrics object. OTEL init returns a new server handler.

## State And Persistence
Metrics/tracing state is process-local and exported through configured telemetry pipelines.

## Dependencies And Integration Points
Requires gRPC plugin type, integrates with `server/grpc/plugin.go` to install interceptors and stats handlers.

## Risks
Prometheus global registration can fail/panic on duplicate registrations in unusual test processes. Histogram enablement increases metric cardinality/cost.

## Test Signals
No direct tests in this subset.
