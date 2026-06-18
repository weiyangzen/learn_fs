# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: Controller service account and external-provisioner RBAC for v2.0.0.

Important APIs/types/functions: Optional `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`; Helm gates `.Values.serviceAccount.create` and `.Values.rbac.create`; fixed names `csi-nfs-controller-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`.

Control flow: Service account creation and RBAC creation are independently gated. The role grants PV create/delete, PVC update, StorageClass/CSINode/node reads, events mutation, and lease access for leader election.

State and persistence: Persists authorization and identity for the controller Deployment.

Dependencies and integration points: Bound to `csi-nfs-controller.yaml` and external-provisioner leader election.

Risks: Fixed names complicate multi-release installs. No secrets permission exists, so StorageClass provisioner-secret workflows may not work. Test signals: render with gates toggled and provisioner startup/RBAC error checks.
