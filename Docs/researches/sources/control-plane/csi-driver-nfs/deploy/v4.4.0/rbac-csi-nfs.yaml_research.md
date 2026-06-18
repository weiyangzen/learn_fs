# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-csi-nfs.yaml

## Purpose
This RBAC bundle grants the NFS CSI controller the cluster permissions needed for provisioning, snapshot sidecar coordination, events, and leader election. It also creates the node service account used by the DaemonSet.

## Important APIs, Types, and Functions
The file creates `ServiceAccount` objects `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, a `ClusterRole` named `nfs-external-provisioner-role`, and a `ClusterRoleBinding` named `nfs-csi-provisioner-binding`. Rules allow PV get/list/watch/create/delete, PVC get/list/watch/update, storageclasses get/list/watch, snapshot class/snapshot get/list/watch, snapshot content get/list/watch/update/patch including status, event create/update/patch, CSINode and node reads, lease create/update/patch, and secret get.

## Control Flow, State, and Persistence
RBAC resources are persistent cluster state. They do not execute logic, but Kubernetes authorization checks use them whenever the controller pod's sidecars watch objects, update PVC/PV metadata, write snapshot content status, emit events, or acquire leader-election leases.

## Dependencies and Integration Points
The binding targets `csi-nfs-controller-sa`, which is referenced by `csi-nfs-controller.yaml`. The node service account is referenced by `csi-nfs-node.yaml`, although this file does not grant node-specific cluster permissions. Snapshot permissions depend on the snapshot CRDs existing or being installable later.

## Risks and Test Signals
Risks include broad cluster-scoped rights, missing `patch` on PVs for newer sidecars, secret read exposure, and install ordering where RBAC references API groups before CRDs are available. Test signals are successful `kubectl auth can-i` checks as the controller service account, sidecars acquiring leases, PV/PVC event creation, and no forbidden errors in provisioner or snapshotter logs.
