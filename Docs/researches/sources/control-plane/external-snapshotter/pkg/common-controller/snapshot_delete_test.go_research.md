# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_delete_test.go

## Purpose
This file validates deletion reconciliation for `VolumeSnapshot` and `VolumeSnapshotContent`, including dynamic and static snapshots, delete versus retain policies, API failures, misbinding, and restore-in-progress blocking.

## Important APIs, Types, And Functions
The main test is `TestDeleteSync`. It defines reusable snapshot class parameter maps and `snapshotClasses`, then runs table entries through `runSyncTests`. Test calls include `testSyncContent`, `testSyncSnapshot`, and `testSyncSnapshotError`, sometimes wrapped by `wrapTestWithInjectedOperation` to mutate reactor state during reconciliation.

## Control Flow
The table first verifies content-side no-ops and already-deleted content. It then exercises snapshot deletion with pending restore PVCs, dynamic content deletion, content delete API failure, retain policy, missing content, mismatched content UID/name, and parallel static cases. For delete policy, expected content is removed and snapshot retains the bound finalizer until content deletion completes. For retain policy or no/misbound content, snapshot finalizers can be removed while content is retained or ignored.

## State And Persistence Behavior
Deletion persists `AnnVolumeSnapshotBeingDeleted` on content before deletion decisions. A `Delete` policy leads to `VolumeSnapshotContent` API deletion and retention of the snapshot bound finalizer. A `Retain` policy keeps content but annotates it and removes snapshot finalizers. Pending restore PVCs keep the snapshot from deletion and produce a retryable error. Tests verify finalizer state, object existence, and warning events.

## Dependencies And Integration Points
The file depends on snapshot class fixtures, PVC restore data source helpers, fake client reactors, and event validation. It directly exercises integration between snapshot deletion, content deletion policy, PVC restore safety, and sidecar-triggering annotations.

## Risks
Deletion is data-loss-sensitive. The tests highlight why content is not deleted when binding is ambiguous and why restore PVCs block deletion. There is still limited direct coverage for group snapshot membership deletion guards in this file; those are implemented in the main controller and covered elsewhere.

## Test Signals
Important expected events include `SnapshotDeletePending` and `SnapshotContentObjectDeleteError`. The tests strongly validate idempotent deletion and safe behavior under missing/misbound content.
