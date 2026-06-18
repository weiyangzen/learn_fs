# sources/control-plane/csi-lib-utils/metrics/metrics.go

## Purpose
This package provides Prometheus/Kubernetes metrics management for CSI sidecars and plugins, centered on CSI operation latency histograms labeled by driver, method, gRPC status, and optional custom labels.

## Important APIs, Types, And Functions
Public interface `CSIMetricsManager` exposes registry access, `RecordMetrics`, `WithLabelValues`, `HaveAdditionalLabel`, `WithAdditionalRegistry`, `SetDriverName`, `RegisterToServer`, and `RegisterPprofToServer`. Options include `WithSubsystem`, `WithStabilityLevel`, `WithLabelNames`, `WithLabels`, `WithMigration`, `WithProcessStartTime`, and `WithCustomRegistry`. Constructors are `NewCSIMetricsManagerForSidecar`, `NewCSIMetricsManager`, `NewCSIMetricsManagerForPlugin`, and `NewCSIMetricsManagerWithOptions`. Helpers include `VerifyMetricsMatch` and `getErrorCode`.

## Control Flow
The constructor initializes a kube registry, applies options, optionally registers `process_start_time_seconds`, builds a histogram vector with default/additional labels, sets the driver name or `unknown-driver`, registers metrics, and initializes gatherers. `RecordMetrics` builds label values and observes duration. `WithLabelValues` returns immutable-ish wrappers that accumulate values and reject undefined or overwritten labels. HTTP registration exposes gathered metrics and pprof handlers.

## State, Persistence, And Dependencies
State lives in the manager instance: registry, driver name, label definitions, gatherers, and histogram vector. Dependencies include Prometheus client, Kubernetes component-base metrics, grpc status/codes, net/http/pprof, and standard time/string utilities.

## Integration Points
`connection.go` uses this through interceptors. CSI sidecars/plugins use it to serve `/metrics` and optionally pprof endpoints.

## Risks And Test Signals
Registering process start time by default can conflict with other registries, so an option disables it. Additional registry mutation appends gatherers in place. Missing label values become empty strings. Unit tests cover metrics shape, labels, endpoint registration, pprof, and process start metric existence.
