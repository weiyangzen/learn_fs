<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.14.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml -->
