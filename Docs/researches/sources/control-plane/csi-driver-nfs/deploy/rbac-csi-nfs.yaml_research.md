# sources/control-plane/csi-driver-nfs/deploy/rbac-csi-nfs.yaml

Purpose: grants the Kubernetes permissions needed by the NFS CSI controller and, in newer manifests, names the node service account used by the DaemonSet.

Important APIs/types/functions: the RBAC bundle defines service accounts such as `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` objects for `nfs-external-provisioner-role` and sometimes `nfs-external-resizer-role`, plus `ClusterRoleBinding` objects binding those roles in `kube-system`. This version contains controller and node service accounts, a provisioner ClusterRole with PV/PVC/StorageClass/snapshot/Event/CSINode/Node/Lease/Secret permissions, and a separate resizer ClusterRole for PVC status and resize events.

Control flow: sidecar containers authenticate through the bound service account tokens, watch Kubernetes resources, update PV/PVC or snapshot status, emit Events, and use `coordination.k8s.io` Leases for leader election. The RBAC file must be applied before controller pods start or their informers fail authorization.

State and persistence: RBAC objects are persistent cluster security policy. They do not store volume data, but they define which controllers can mutate storage and snapshot API state.

Dependencies and integration points: consumed by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, the provisioner, resizer, and snapshotter sidecars. Secret access supports optional mount-option secrets referenced from StorageClass comments.

Risks: overbroad cluster roles increase blast radius for compromised controller pods. Missing snapshot or resize verbs surface as stuck PVCs or snapshots rather than manifest syntax errors. Older variants cannot support features added by later controller manifests without RBAC expansion.

Test signals: run `kubectl auth can-i` as the controller service account for PV/PVC/watch/update, leases create/update, secret get, and snapshot verbs where applicable; then exercise dynamic provisioning, resize, and snapshot examples.
