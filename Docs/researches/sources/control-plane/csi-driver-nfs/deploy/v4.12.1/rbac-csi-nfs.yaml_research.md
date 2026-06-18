<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml

## Purpose
Provides RBAC for the NFS CSI controller and node service accounts in the v4.12.1 manifest set.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa`. Binds `nfs-external-provisioner-role` and `nfs-external-resizer-role` to the controller account. Provisioner rules cover PV/PVC lifecycle, StorageClass reads, snapshot class/snapshot/content access, events, CSINode/node reads, Lease leader election, and Secret reads. Resizer rules cover PV updates, PVC status updates, events, and Leases.

## Control Flow
CSI sidecars in `csi-nfs-controller.yaml` use these permissions while watching storage API objects and writing reconciled state. The node account is present for the DaemonSet but does not receive additional Kubernetes API permissions here.

## State And Persistence Behavior
The RBAC objects persist as cluster policy and determine which API objects sidecars can mutate. They indirectly permit persistent state changes in PVs, PVC statuses, snapshot content statuses, events, and leader-election Leases.

## Dependencies And Integration Points
Must match the service account names used in controller and node workload manifests. Snapshot permissions rely on snapshot CRDs and are used by the CSI snapshotter sidecar.

## Risks And Edge Cases
Cluster-wide permissions are broad, and Secret read access should be limited to the controller account's actual needs. Missing or changed verbs usually surface as sidecar retry loops and events. The node account may need more permissions if future node plugin behavior starts calling the Kubernetes API directly.

## Test Signals
Run `kubectl auth can-i` checks as `csi-nfs-controller-sa` and execute dynamic provisioning, expansion, snapshot creation, and deletion. Watch sidecar logs for forbidden errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml -->
