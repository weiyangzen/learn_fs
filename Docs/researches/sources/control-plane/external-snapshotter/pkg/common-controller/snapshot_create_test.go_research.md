# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_create_test.go

## Purpose
This test file validates dynamic `VolumeSnapshotContent` creation from `VolumeSnapshot` objects. It covers successful content creation, secret annotation propagation, and many failure paths before or during content/status updates.

## Important APIs, Types, And Functions
The main entry is `TestCreateSnapshotSync`. It uses `controllerTest` tables run through `runSyncTests` and usually invokes `testSyncSnapshot`. Shared fixtures include `newSnapshotArray`, `newContentArrayNoStatus`, `newClaimArray`, `newVolumeArray`, `withContentAnnotations`, and reactor error injection through `reactorError`.

## Control Flow
Each test seeds initial snapshots, claims, volumes, classes, optional secrets, and expected objects. Success cases create a deterministic `snapcontent-<snapshotUID>` object and update snapshot status with the bound content name. Failure cases cover nonexistent classes, missing class names, missing PVCs, missing PVs, unbound PVCs, PVC finalizer update failures, snapshot status update failures, invalid secret parameters, and content create API failures.

## State And Persistence Behavior
The expected state demonstrates that creation is multi-step: add or verify PVC finalizer, resolve class/PV/secret, create `VolumeSnapshotContent`, update snapshot status, and record events/errors when steps fail. Secret references are persisted as deletion secret annotations on content. When content creation succeeds but status update fails, the test expects content to exist while snapshot status may remain unbound, matching retry-oriented controller behavior.

## Dependencies And Integration Points
The file integrates the controller with snapshot classes, Kubernetes PVC/PV binding, CSI volume handles, snapshotter secret parameter parsing, fake client reactors, and event recording. It indirectly tests `createSnapshotContent`, `getCreateSnapshotInput`, `ensurePVCFinalizer`, and `updateSnapshotStatus`.

## Risks
Creation has several partial-success states. The tests show content can be created even when later snapshot status updates fail, so idempotent retry and deterministic naming are critical. Secret parameter validation is covered, but credential lookup details live in utility code. Distributed snapshotting and source volume mode conversion are not explicitly exercised here.

## Test Signals
The table covers both happy path and high-value error paths, with expected events such as `SnapshotContentCreationFailed` and `CreateSnapshotContentFailed`. It is a strong regression suite for dynamic snapshot creation preconditions.
