# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_update_test.go

## Purpose
This is the broadest snapshot reconciliation test file. It validates sync behavior for bound/unbound, ready/unready, dynamic/static, content-driven status updates, content finalizer additions, deletion annotation propagation, error status propagation, and recreation of missing content.

## Important APIs, Types, And Functions
`TestSync` defines one large `controllerTest` table. It uses helper constructors for snapshots, contents, claims, volumes, secrets, errors, annotations, and restore sizes. Test adapters include `testSyncSnapshot`, `testSyncSnapshotError`, `testSyncContent`, `testSyncContentError`, `testUpdateSnapshotErrorStatus`, and `testNewSnapshotContentCreation`.

## Control Flow
The test table covers missing content, misbound static and dynamic content, successful binding, no-op ready states, status rebuilds from content fields, API update failures, dynamic-vs-static content mismatch, adding content finalizers, marking content when snapshots are being deleted, propagating content errors into snapshot status, clearing snapshot errors, and creating new content when snapshot status is nil or stale.

## State And Persistence Behavior
Expected objects show how `VolumeSnapshot.Status` is rebuilt from `VolumeSnapshotContent.Status`: bound content name, ready state, creation time, restore size, and error. They also show how content metadata is changed by finalizer addition and deletion annotations. The file validates partial failure behavior where in-memory annotations may appear in expected reactor objects even when API update fails.

## Dependencies And Integration Points
The file integrates most of the common controller stack: snapshot/content listers, fake client reactors, snapshot classes, Kubernetes PVC/PV state, events, secrets, content statuses, and utility constants. It provides indirect coverage for `syncSnapshot`, `syncContent`, `syncReadySnapshot`, `syncUnreadySnapshot`, `updateSnapshotStatus`, and `addContentFinalizer`.

## Risks
Because this file is large and table-driven, understanding a failed case often requires tracing helper defaults in `framework_test.go`. Some cases intentionally set content status changes through reactor behavior, so the initial and expected content can differ in ways not obvious from one row. Still, the breadth is valuable for preventing regressions in the multi-step state machine.

## Test Signals
Expected warning events include `SnapshotContentMissing`, `SnapshotContentMisbound`, `SnapshotFinalizerError`, `SnapshotContentMismatch`, and `SnapshotContentCreationFailed`. The file is a strong signal for idempotence, status propagation, and safe handling of bad bindings.
