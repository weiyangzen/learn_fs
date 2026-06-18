# sources/control-plane/external-snapshotter/pkg/metrics/metrics.go

## Purpose
This file implements Prometheus/Kubernetes metrics for snapshot controller operations. It tracks operation start times, emits latency histograms, tracks operations in flight, and supports cancellation metrics when deletes terminate unfinished creates.

## Important APIs, Types, And Functions
Public constants name operations (`CreateSnapshot`, `CreateSnapshotAndReady`, `DeleteSnapshot`), snapshot provision types (`dynamic`, `pre-provisioned`), and status types (`unknown`, `success`, `cancel`). `MetricsManager` exposes `PrepareMetricsPath`, `OperationStart`, `DropOperation`, `RecordMetrics`, `RecordVolumeGroupSnapshotMetrics`, and `GetRegistry`. `OperationKey` identifies an operation by name and resource UID; `OperationValue` stores driver, snapshot type, and start time. `NewMetricsManager` creates an `operationMetricsManager`; `NewOperationKey`, `NewOperationValue`, and `NewSnapshotOperationStatus` are constructors.

## Control Flow
`OperationStart` records a start time only if the key is not already cached, making starts idempotent. `RecordMetrics` returns if no start exists, computes duration, resolves unknown driver names from the cached value, observes the histogram, handles delete-triggered cancel metrics for pending create operations, removes cached entries, and updates the in-flight gauge. `DropOperation` removes cached state without histogram emission. `PrepareMetricsPath` attaches the registry to an HTTP mux.

## State And Persistence Behavior
The manager's only state is an in-memory map protected by a mutex plus Prometheus registry objects. It periodically resets `operations_in_flight` from cache length. There is no persisted state; process restart loses pending operation starts.

## Dependencies And Integration Points
The file depends on Kubernetes component-base metrics, Prometheus `promhttp`, Kubernetes UIDs, HTTP muxes, and `time`. The snapshot controller records create/delete metrics through this interface during status and deletion transitions.

## Risks
`init` starts a goroutine with a context canceled by deferred `cancel`, so the scheduled in-flight refresh likely exits immediately after initialization; the gauge is still updated on start/finish operations, but leak correction may not run. Metrics are process-local and depend on every operation path correctly calling start and record/drop. Missing driver names fall back to `"unknown"` or cached driver names.

## Test Signals
Separate metrics tests in the package cover manager creation, non-existing operation handling, recording, unknown status, concurrency, in-flight gauge, process start time, and group snapshot metrics. This file itself has no tests but is well-covered by adjacent tests.
