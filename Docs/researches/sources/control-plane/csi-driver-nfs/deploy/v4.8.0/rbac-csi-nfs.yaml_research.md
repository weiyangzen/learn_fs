<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml

## Purpose
Creates the service accounts and cluster permissions needed by the v4.8.0 CSI NFS controller-side sidecars and node service account.

## Important APIs, Types, and Functions
Objects include service accounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` `nfs-external-provisioner-role`, and `ClusterRoleBinding` `nfs-csi-provisioner-binding`. The role grants PV CRUD, PVC read/update, storage class read, snapshot object reads and content status updates, event writes, CSINode/node reads, lease CRUD, and secret reads.

## Control Flow, State, and Persistence
The external provisioner and snapshotter use these permissions while reconciling PVs, PVCs, snapshot contents, events, and leader election leases. The node service account is only declared here; node operations mainly rely on kubelet/host privileges in the DaemonSet.

## Dependencies and Integration Points
This RBAC must match `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, snapshot CRDs, and the controller deployment namespace. Secret read access supports CSI secret references passed to controller operations.

## Risks and Test Signals
Risks include cluster-wide permission breadth, missing verbs after sidecar upgrades, and service account namespace drift. Signals are sidecars starting without `forbidden` errors, leader election success, PV create/delete success, and snapshot content status patch success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml -->
