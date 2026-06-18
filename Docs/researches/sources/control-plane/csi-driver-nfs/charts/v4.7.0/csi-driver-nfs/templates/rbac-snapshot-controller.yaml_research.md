# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Defines optional RBAC for the external snapshot controller in the v4.7.0 chart.

## Important APIs, Types, And Functions
Gated by `.Values.externalSnapshotter.enabled`. Emits a `ServiceAccount`, cluster-scoped `ClusterRole`/`ClusterRoleBinding`, and namespace-scoped `Role`/`RoleBinding` for leader election. Permissions cover PVs, PVCs, events, VolumeSnapshot classes/contents/snapshots, status subresources, and optionally nodes for distributed snapshotting.

## Control Flow
When enabled, the snapshot controller gets cluster-wide watch/update/delete permissions for snapshot reconciliation and namespaced lease permissions in the release namespace. The optional distributed snapshotting branch adds node list/watch/get access.

## State And Persistence
RBAC objects persist in the cluster and authorize the controller to mutate snapshot API state. The actual reconciliation state is in snapshot objects and leader election leases.

## Dependencies And Integration Points
Works with `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must match external-snapshotter controller expectations for the image version configured in values.

## Risks And Edge Cases
Cluster-wide snapshot permissions are powerful. If multiple chart releases use the same external snapshotter name, role and binding names can collide. Missing status permissions break readiness and snapshot status updates.

## Test Signals
Check `kubectl auth can-i` for `volumesnapshotcontents/status patch` and `volumesnapshots/status update` as the snapshot service account, then create/delete a snapshot to verify controller reconciliation.
