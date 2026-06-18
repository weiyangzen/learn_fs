# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Defines optional RBAC for the v4.9.0 external snapshot controller.

## Important APIs, Types, And Functions
When enabled, emits a snapshot-controller service account, cluster role/binding for snapshot reconciliation, and namespaced role/binding for leader election leases. Optional distributed snapshotting adds node read/watch permissions.

## Control Flow
Skipped when `externalSnapshotter.enabled` is false. When rendered, the controller can read PV/PVC objects, create/update/delete snapshot contents, update snapshot statuses, write events, and manage its lease.

## State And Persistence
RBAC resources persist as cluster authorization state. Snapshot controller state persists in snapshot API objects and leases.

## Dependencies And Integration Points
Pairs with `csi-snapshot-controller.yaml` and the snapshot CRD template. Permission shape must match the configured external-snapshotter image.

## Risks And Edge Cases
Byte-identical to prior versions in this set. Cluster-wide permissions and naming collisions across releases are the main risks. Missing leader-election role prevents stable controller operation.

## Test Signals
Authorization checks for snapshot status and content verbs, plus end-to-end snapshot creation and deletion.
