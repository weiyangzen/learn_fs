<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml

## Purpose
Defines RBAC for the v4.9.0 NFS CSI controller and declares controller/node service accounts.

## Important APIs, Types, and Functions
It creates `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and binding `nfs-csi-provisioner-binding`. The role includes permissions for PV/PVC provisioning, storage class reads, snapshot classes/snapshots/contents/status, event emission, CSINode/node reads, leader-election leases, and secret reads.

## Control Flow, State, and Persistence
The controller sidecars use these verbs to reconcile storage state through the Kubernetes API. Leases persist leader election state, events persist operation feedback, and PV/PVC/snapshot objects persist storage desired and observed state.

## Dependencies and Integration Points
It must match the sidecar versions in `csi-nfs-controller.yaml` and snapshot CRDs. It also supports CSI secret references and Kubernetes node/CSINode discovery.

## Risks and Test Signals
Risks include overbroad cluster privileges, missing verbs for sidecar upgrades, and namespace mismatches. Signals are no RBAC forbidden errors, successful leader election, successful dynamic provisioning, and snapshot content status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml -->
