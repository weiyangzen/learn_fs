# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and cluster RBAC for the NFS controller and node components.

## APIs, Control Flow, and State
When `serviceAccount.create` is true it emits controller and node `ServiceAccount` resources in the release namespace. When `rbac.create` is true it emits two `ClusterRole`s and two `ClusterRoleBinding`s. The provisioner role grants PV create/patch/delete, PVC get/list/watch/update, StorageClass and CSINode reads, Node reads, event writes, snapshot resource reads/updates, lease writes for leader election, and secret reads. The resizer role grants PV/PVC/status update, event writes, and lease writes.

## Dependencies and Integration Points
The controller Deployment references `serviceAccount.controller`; the node DaemonSet references `serviceAccount.node`. Provisioner, resizer, and snapshotter sidecars depend on these permissions to reconcile Kubernetes storage objects. Secret access supports provisioner-secret mount option handling.

## Risks and Test Signals
This is cluster-wide access; overly broad or missing verbs affect all NFS CSI operation. Snapshot verbs are present even if snapshotter is disabled. Test with `kubectl auth can-i` for the controller service account, PVC create/delete, expansion, snapshot flows, and leader-election lease updates.
