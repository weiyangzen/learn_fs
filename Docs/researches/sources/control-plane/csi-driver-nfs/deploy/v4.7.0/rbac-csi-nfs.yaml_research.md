<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml

## Purpose
Defines service accounts and cluster-wide permissions needed by the CSI NFS controller and node components for dynamic provisioning, snapshot sidecar interaction, event emission, node discovery, and leader election.

## Important APIs, Types, and Functions
The file creates `ServiceAccount` objects `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, a `ClusterRole` named `nfs-external-provisioner-role`, and a `ClusterRoleBinding` named `nfs-csi-provisioner-binding`. Rules cover PVs, PVCs, storage classes, snapshot classes/snapshots/contents/status, events, CSINodes, nodes, leases, and read-only secrets.

## Control Flow, State, and Persistence
The controller service account is bound to provisioner permissions. Runtime state is Kubernetes API state: PV/PVC create-update-delete operations, snapshot content status patches, event writes, and lease objects for leader election. The node service account is created here but does not receive a binding in this file.

## Dependencies and Integration Points
This RBAC is consumed by `csi-nfs-controller` deployments and must match sidecar permissions for `csi-provisioner` and `csi-snapshotter`. Secret `get` supports CSI sidecar secret references, while lease permissions support leader-elected controllers.

## Risks and Test Signals
Risks include over-broad cluster permissions, missing verbs for newer sidecar versions, stale snapshot API group permissions, and namespace mismatches in bindings. Signals are clean startup of provisioner/snapshotter sidecars, no RBAC forbidden events, successful PV provisioning/deletion, and successful snapshot content status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml -->
