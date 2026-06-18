<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml

## Purpose
Provides RBAC for the external snapshot-controller. It allows the controller to bind snapshots to contents, update snapshot statuses, emit events, and coordinate leader election.

## Important APIs, Types, and Functions
The file creates service account `snapshot-controller`, cluster role `snapshot-controller-runner`, cluster role binding `snapshot-controller-role`, namespace role `snapshot-controller-leaderelection`, and role binding of the same name. Rules cover PV/PVC reads, PVC update, event creation/update/patch, snapshot class reads, snapshot content CRUD/status patch, snapshot read/update/patch, snapshot status update/patch, and coordination leases in `kube-system`.

## Control Flow, State, and Persistence
The snapshot-controller watches snapshot API objects and writes binding and status state through the permissions granted here. Leader election is scoped to `kube-system` leases, while resource reconciliation is cluster-scoped for snapshot content objects and namespaced for snapshots/PVCs.

## Dependencies and Integration Points
It pairs with `csi-snapshot-controller.yaml` and the snapshot CRDs. It also coordinates with CSI driver snapshotter sidecars that create or update `VolumeSnapshotContent` objects.

## Risks and Test Signals
Risks include missing status verbs causing stuck snapshots, overly broad delete access to snapshot contents, and role binding namespace mismatches. Signals are absence of `forbidden` logs in snapshot-controller, lease acquisition in `kube-system`, and snapshots progressing to bound/ready states.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml -->
