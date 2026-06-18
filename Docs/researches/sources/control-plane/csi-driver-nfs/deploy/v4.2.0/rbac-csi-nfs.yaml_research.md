## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/rbac-csi-nfs.yaml

Purpose: Creates the ServiceAccounts and controller-side ClusterRole/Binding needed by the v4.2.0 NFS CSI controller. This early v4 manifest grants external-provisioner permissions but does not include snapshotter or resizer permissions.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, ClusterRole `nfs-external-provisioner-role`, and ClusterRoleBinding `nfs-csi-provisioner-binding`. The role can get/list/watch/create/delete PVs, get/list/watch/update PVCs, read StorageClasses, write events, read CSINodes and Nodes, manage coordination leases, and get Secrets.

Control flow: The `csi-provisioner` sidecar in `csi-nfs-controller.yaml` uses these permissions to watch PVCs and StorageClasses, create/delete PVs, update PVCs, emit events, and use leases for leader election. The NFS driver container itself talks over the CSI socket and does not directly use most Kubernetes API permissions.

State and persistence behavior: RBAC objects persist authorization policy. They authorize PV/PVC mutations and lease updates but do not store volume state themselves. The node ServiceAccount is created for the DaemonSet even though this file grants no node-specific ClusterRole.

Dependencies and integration points: Paired with the v4.2.0 controller and node manifests. It supports `storageclass.yaml`-style dynamic provisioning in nearby versions, but v4.2.0's listed subset does not include snapshot CRDs or snapshot controller manifests.

Risks: The PV rule lacks `patch`, while later manifests add it; sidecar versions or workflows that patch PVs may fail. No resizer RBAC exists, matching the absence of a resizer sidecar. No snapshot permissions exist, matching the absence of snapshotter resources. Granting `secrets get` cluster-wide is useful for provisioner secrets but should be constrained in hardened deployments where possible.

Test signals: Check `kubectl auth can-i` for the controller ServiceAccount against PV create/delete, PVC update, StorageClass watch, events create/patch, leases create/update, and secrets get. Provision and delete a PVC, inspect events, and verify leader-election leases are created in the configured namespace.
