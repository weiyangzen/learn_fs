<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml

## Purpose
Provides RBAC for the v8.4.0 external snapshot controller used by the v4.13.0 bundle.

## Important APIs, Types, And Objects
Creates `snapshot-controller` service account, a cluster role for snapshot reconciliation, a cluster role binding, and a namespaced leader-election Role/RoleBinding. Permissions include PV/PVC reads, PVC update, event writes, snapshot class reads, full snapshot content lifecycle with status patch, snapshot object create/update/patch/read, snapshot status update/patch, and Lease operations.

## Control Flow
The snapshot controller uses these permissions to watch snapshot resources, create and bind content objects, update status, emit events, and coordinate two replicas with leader election.

## State And Persistence Behavior
RBAC is durable cluster state. It enables writes to snapshot resources and Leases but stores no snapshot runtime data directly.

## Dependencies And Integration Points
Requires snapshot CRDs and is consumed by `csi-snapshot-controller.yaml`. It coordinates with per-driver snapshotter sidecars, including the NFS v4.13.0 controller's snapshotter.

## Risks And Edge Cases
Cluster-wide snapshot permissions affect all CSI drivers. The RBAC appears unchanged from v4.12.x while the controller image moves to v8.4.0, so compatibility should be verified. Leader election includes Lease delete permission.

## Test Signals
Use auth checks for snapshot content lifecycle, snapshot status patch, event write, and Lease update/delete. Run snapshot lifecycle tests with controller failover and inspect for forbidden errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml -->
