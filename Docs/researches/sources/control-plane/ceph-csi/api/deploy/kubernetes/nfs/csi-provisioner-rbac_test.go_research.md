<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go

Purpose: unit tests for NFS provisioner RBAC rendering. It validates `NewCSIProvisionerRBAC`, combined YAML output, and internal typed renderers for ClusterRole, ClusterRoleBinding, Role, and RoleBinding. State is in-memory only. The tests signal template parse/unmarshal regressions but do not inspect individual rules, subjects, or ServiceAccount YAML rendering.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go -->
