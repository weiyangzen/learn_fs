# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Provides optional RBAC for the external snapshot controller in the v4.8.0 chart.

## Important APIs, Types, And Functions
When enabled, emits a snapshot-controller `ServiceAccount`, cluster role/binding, and namespaced role/binding for leader-election leases. Permissions cover snapshots, snapshot contents/classes, PVCs, PVs, events, statuses, and optionally nodes.

## Control Flow
The template is skipped unless `.Values.externalSnapshotter.enabled` is true. The distributed snapshotting flag conditionally adds node permissions.

## State And Persistence
RBAC state persists in Kubernetes and controls the controller's ability to reconcile snapshot API objects and update status.

## Dependencies And Integration Points
Pairs with `csi-snapshot-controller.yaml` and snapshot CRDs. It must remain compatible with the external-snapshotter image version configured in values.

## Risks And Edge Cases
This file is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Name collisions are possible across releases if the same snapshotter name is reused. Missing status permissions cause partial reconciliation.

## Test Signals
Authorization checks for snapshot status verbs and an end-to-end snapshot lifecycle test.
