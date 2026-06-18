<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml

## Purpose
Provides the service account and RBAC policy for the shared external snapshot controller used by the v4.12.0 NFS CSI deployment.

## Important APIs, Types, And Objects
Creates `snapshot-controller` service account in `kube-system`. The `snapshot-controller-runner` ClusterRole grants reads on PVs, get/list/watch/update on PVCs, event writes, reads on `VolumeSnapshotClass`, full create/get/list/watch/update/delete/patch on `VolumeSnapshotContent`, patch on content status, get/list/watch/update/patch/create on `VolumeSnapshot`, and update/patch on snapshot status. A namespaced Role grants Lease operations for leader election.

## Control Flow
The snapshot controller Deployment uses these permissions to reconcile snapshot requests, create or delete content objects, update statuses, and coordinate active replicas through Leases.

## State And Persistence Behavior
The RBAC policy is durable cluster configuration. It enables the controller to persist snapshot lifecycle state in CR objects and write events; the policy itself has no runtime storage.

## Dependencies And Integration Points
Requires snapshot CRDs to make the referenced resources meaningful. Integrates with `csi-snapshot-controller.yaml`, `VolumeSnapshotClass`, per-driver CSI snapshotter sidecars, and PVC/PV resources used as snapshot sources.

## Risks And Edge Cases
This is cluster-wide snapshot authority, so misbinding or accidental changes can impact all CSI drivers. The leader-election Role includes Lease delete, which is broader than minimal update-only election in some deployments. If applied before CRDs, RBAC can exist but controller startup still depends on API discovery.

## Test Signals
Use `kubectl auth can-i` for content create/delete, snapshot status patch, and Lease update as the snapshot-controller account. Integration tests should verify dynamic snapshot creation, pre-provisioned content binding, status updates, and deletion policy handling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml -->
