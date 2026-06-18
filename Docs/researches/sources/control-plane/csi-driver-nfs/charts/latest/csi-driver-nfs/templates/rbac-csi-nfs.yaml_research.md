# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: Helm RBAC template for the latest CSI NFS chart. It creates controller and node ServiceAccounts when `serviceAccount.create` is true, and cluster-scoped provisioner/resizer roles when `rbac.create` is true.

Important APIs/types/functions: Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`; Helm values `.Values.serviceAccount.*`, `.Values.rbac.name`, `.Release.Namespace`, and `include "nfs.labels"`.

Control flow: Two top-level Helm gates render service accounts independently from RBAC. The provisioner role covers PV/PVC/storageclass/node/csinode/event/lease/secrets access plus snapshot API reads and VolumeSnapshotContent updates. A separate resizer role grants PV/PVC/status and event/lease access.

State and persistence: Persistent state is Kubernetes RBAC and service-account identity. No workload state is stored here.

Dependencies and integration points: Bound to the controller ServiceAccount used by `csi-nfs-controller.yaml`; permissions serve external-provisioner, csi-resizer, and snapshotter sidecars.

Risks: Cluster-wide RBAC is broad, especially PV mutation, secrets get, and snapshot content patch/update. Turning off service account creation requires matching pre-created names. Test signals: `helm template` with RBAC on/off and Kubernetes RBAC dry-run should verify all generated bindings.
