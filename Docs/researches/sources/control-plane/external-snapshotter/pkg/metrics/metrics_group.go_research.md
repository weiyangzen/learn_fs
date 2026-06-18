# sources/control-plane/external-snapshotter/pkg/metrics/metrics_group.go

## Purpose
This file extends the snapshot metrics manager with group snapshot operation names and recording behavior. It mirrors single-snapshot metric semantics for `VolumeGroupSnapshot` workflows.

## Important APIs, Types, And Functions
It defines `CreateGroupSnapshotOperationName`, `CreateGroupSnapshotAndReadyOperationName`, `DeleteGroupSnapshotOperationName`, `DynamicGroupSnapshotType`, and `PreProvisionedGroupSnapshotType`. The main function is `RecordVolumeGroupSnapshotMetrics`, a method on `operationMetricsManager` exposed through `MetricsManager`.

## Control Flow
`RecordVolumeGroupSnapshotMetrics` locks the metrics cache, returns if the operation was not started, resolves status and driver name, observes operation duration in the shared latency histogram, handles delete-triggered cancellation for pending group create and create-and-ready operations, deletes the completed operation key, and updates the in-flight gauge.

## State And Persistence Behavior
It uses the same in-memory `operationMetricsManager.cache` as snapshot metrics. Group snapshot operations are distinguished only by operation name and resource UID. No state is persisted beyond Prometheus metric samples.

## Dependencies And Integration Points
The file depends on `time` and the types/constants from `metrics.go`. It integrates group snapshot controller code with the same metric labels used for ordinary snapshot operations: driver name, operation name, snapshot type, and operation status.

## Risks
The implementation intentionally duplicates `RecordMetrics` logic; future changes to single-snapshot metric behavior must be mirrored here to avoid semantic drift. It shares the same reliance on correct `OperationStart` calls and the same in-flight gauge behavior.

## Test Signals
Metrics package tests include group snapshot recording and pre-provisioned group snapshot cases. These tests confirm the group operation names emit through the common histogram path.
