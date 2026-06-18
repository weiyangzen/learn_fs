<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go

Purpose: shared abstraction for provisioner RBAC artifact generators.
Important APIs/types: `CSIProvisionerRBAC` interface exposes getters for ServiceAccount, ClusterRole, ClusterRoleBinding, Role, and RoleBinding; `CSIProvisionerRBACValues` carries namespace and service account name.
Control flow/state: pure interface/value definitions.
Dependencies/integration: implemented by NFS provisioner RBAC generator and available for other backends.
Risks/test signals: interface assumes exactly one of each RBAC object, which may constrain future drivers needing multiple roles. Tests live in implementation packages.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go -->
