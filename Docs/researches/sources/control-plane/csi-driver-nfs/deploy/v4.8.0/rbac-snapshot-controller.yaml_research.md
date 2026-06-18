<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml

## Purpose
Grants snapshot-controller v8.0.1 the permissions required to reconcile CSI snapshot API objects.

## Important APIs, Types, and Functions
The file creates service account `snapshot-controller`, cluster role `snapshot-controller-runner`, cluster role binding `snapshot-controller-role`, role `snapshot-controller-leaderelection`, and a role binding in `kube-system`. It grants reads on PV/PVC/snapshot classes, update on PVCs and snapshots, CRUD on snapshot contents, status patch/update on snapshot resources, event writes, and lease CRUD.

## Control Flow, State, and Persistence
The controller watches `VolumeSnapshot` and `VolumeSnapshotContent`, updates binding/status fields, and uses a namespace lease to ensure only one active reconciler. Persistent state is all in Kubernetes API resources.

## Dependencies and Integration Points
It pairs with `csi-snapshot-controller.yaml`, the snapshot CRDs, and CSI snapshotter sidecars running with drivers such as NFS. The permissions are storage-wide and not tied to only NFS snapshots.

## Risks and Test Signals
Risks include stuck snapshots from missing status verbs, accidental delete power over snapshot contents, and lease namespace mismatches. Signals are a healthy leader lease, no RBAC denial events, and snapshots progressing through binding to ready.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml -->
