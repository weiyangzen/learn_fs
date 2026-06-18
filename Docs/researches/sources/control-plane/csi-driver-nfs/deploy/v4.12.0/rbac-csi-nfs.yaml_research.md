<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml

## Purpose
Defines service accounts and cluster RBAC used by the NFS CSI controller and node components in the v4.12.0 deployment set.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`. `nfs-external-provisioner-role` allows PV create/patch/delete, PVC get/list/watch/update, StorageClass reads, snapshot object reads and content/status updates, event writes, CSINode/node reads, Lease leader election, and Secret get. `nfs-external-resizer-role` allows PV/PVC reads, PV update/patch, PVC status update/patch, events, and Leases. Both ClusterRoles bind to `csi-nfs-controller-sa`.

## Control Flow
The controller Deployment uses these permissions for its sidecars. Provisioner permissions support dynamic PV lifecycle; resizer permissions support PVC expansion status; snapshot permissions let the snapshotter coordinate `VolumeSnapshotContent`; Lease permissions enable leader election.

## State And Persistence Behavior
RBAC objects are durable cluster policy. They do not store driver runtime state, but they gate all API mutations that the controller sidecars need to persist PVs, PVC status, snapshot content status, events, and election Leases.

## Dependencies And Integration Points
Tied directly to `serviceAccountName: csi-nfs-controller-sa` in the controller Deployment and `serviceAccountName: csi-nfs-node-sa` in the node DaemonSet. Snapshot permissions depend on snapshot CRDs being installed.

## Risks And Edge Cases
The controller account has broad cluster-level write access to PVs and snapshot contents plus read access to Secrets. The node service account is created but receives no explicit permissions in this file, which is fine if the node pod only needs kubelet/CSI host integration but should be checked against plugin behavior. Missing `update` on PVC status for the provisioner is deliberate because resizer owns status updates.

## Test Signals
Run `kubectl auth can-i --as=system:serviceaccount:kube-system:csi-nfs-controller-sa` checks for PV create, PVC status patch, Lease create/update, and snapshot content status patch. Exercise provisioning, expansion, and snapshot flows while watching for RBAC denial events.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml -->
