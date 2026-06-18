# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-csi-nfs.yaml

## Purpose
This v4.6.0 RBAC file creates the NFS CSI service accounts and controller permissions. It is unchanged from v4.4.0 and v4.5.0 despite the controller upgrading to `csi-provisioner:v4.0.0`.

## Important APIs, Types, and Functions
Objects are `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`. The role covers PV get/list/watch/create/delete, PVC update, storage class reads, snapshot class/snapshot reads, snapshot content update/patch/status, event writes, CSINode/node reads, lease writes, and secret get.

## Control Flow, State, and Persistence
The file persists cluster authorization rules that gate every controller sidecar API operation. It does not grant a binding to the node service account because node plugin work primarily occurs through kubelet host paths and CSI registration.

## Dependencies and Integration Points
It is consumed by `csi-nfs-controller.yaml` and `csi-nfs-node.yaml`. Snapshot API rules integrate with CRDs and the sidecar snapshotter; lease rules integrate with leader election in `kube-system`.

## Risks and Test Signals
Risks include possible missing `patch` on persistentvolumes for the newer v4 provisioner, broad cluster access, and secret read permission. Test signals include no RBAC denials from the v4.6.0 controller, successful PV creation/deletion, leader-election leases, event writes, and snapshot content status updates.
