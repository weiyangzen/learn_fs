# sources/control-plane/external-snapshotter/pkg/common-controller/snapshotclass_test.go

## Purpose
This file tests `VolumeSnapshotClass` lookup and defaulting behavior before snapshot reconciliation proceeds. It verifies both explicit class names and automatic default class assignment.

## Important APIs, Types, And Functions
`TestUpdateSnapshotClass` defines table-driven `controllerTest` rows and runs them with `runUpdateSnapshotClassTests`. The test path targets `checkAndUpdateSnapshotClass` and `SetDefaultSnapshotClass`. Fixtures use PVC/PV pairs whose storage class and CSI driver influence default class selection.

## Control Flow
Case `1-1` starts with no class name and expects the controller to patch the default class matching the source PV driver. Case `1-2` verifies a pre-set class remains unchanged. Case `1-3` verifies a missing explicit class records an error and event. Case `1-5` verifies defaulting fails when the source PVC cannot be found.

## State And Persistence Behavior
Defaulting persists by patching `snapshot.Spec.VolumeSnapshotClassName` and updating the controller's local store. Failure paths persist error status on the snapshot with warnings such as `GetSnapshotClassFailed` or `SetDefaultSnapshotClassFailed`.

## Dependencies And Integration Points
The file depends on global `snapshotClasses`, Kubernetes PVC/PV fixtures, and the shared test framework. It integrates class defaulting with `pvDriverFromSnapshot`, which means default class selection depends on a valid PVC/PV binding and CSI driver match.

## Risks
The file covers missing class and missing PVC, but not multiple default classes, non-CSI PVs, or pre-provisioned snapshots where class lookup can be skipped. Multiple defaults are an important production risk because the controller refuses ambiguous defaulting.

## Test Signals
The expected state and events confirm that class errors are visible to users and that defaulting mutates spec only when prerequisites are satisfied.
