# sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller_test.go

## Purpose
This test file exercises the `CephFilesystemMirror` controller for cluster readiness/version gates, successful mirror deployment reconciliation, and CephX key-rotation state transitions.

## Important APIs, Types, and Functions
`TestCephFilesystemMirrorController` covers missing cluster, unready cluster, ready cluster with old version scenario, cluster upgrade requeue, and successful creation on supported versions. `TestFSMirrorKeyRotation` covers first reconcile, stable subsequent reconcile, brownfield unknown status, rotation from unknown to known, no repeated rotation, and later generation updates. Tests override `currentAndDesiredCephVersion` and mock Ceph auth/status commands.

## Control Flow, State, and Persistence
The tests build a `CephFilesystemMirror` CR, fake `CephCluster`, monitor Secret, fake controller-runtime client, fake clientset, and `ReconcileFilesystemMirror`. Mock executors return Ceph status and auth keys, including rotated key material. Reconcile results are checked for requeue behavior, and CR status is fetched to assert phase or CephX key generation/version. Key rotation tests inspect the generated Secret `rook-ceph-fs-mirror-keyring`.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, fake controller-runtime client, API scheme registration, event recorder, mock executor, Ceph version constants, and keyring Secret behavior. It tests integration across controller logic, mirror deployment startup, keyring generation, and status updates.

## Risks
The test mutates package-level version detection and does not restore it between all subtests, so parallel execution would be unsafe. Some executor paths return success for unrecognized commands, which can hide changes in command behavior. The "version too old" case asserts no requeue but does not deeply inspect failure status or deployment absence. Scheme registration includes `CephRBDMirror` in the key-rotation test despite testing `CephFilesystemMirror`, a likely copy/paste artifact.

## Test Signals
Signals include requeue for missing/unready clusters, upgrade wait requeue, Ready phase after successful reconcile, initial CephX key generation `1`, retention of known and unknown CephX statuses, Secret updates on configured rotations to generations `2` and `3`, and no Secret change when no further rotation is required.
