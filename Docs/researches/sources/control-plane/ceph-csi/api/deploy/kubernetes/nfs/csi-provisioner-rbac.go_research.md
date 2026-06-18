<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go

Purpose: renders and exposes typed NFS external provisioner RBAC artifacts.
Important APIs/functions: `CSIProvisionerRBACDefaults`, `NewCSIProvisionerRBAC`, `NewCSIProvisionerRBACYAML`, internal `newYAML`, `newServiceAccount`, `newClusterRole`, `newClusterRoleBinding`, `newRole`, `newRoleBinding`, and the `csiProvisionerRBAC` getter methods implementing `kubernetes.CSIProvisionerRBAC`.
Control flow/state: embeds five YAML templates, renders them with namespace/serviceAccount values, unmarshals into typed Kubernetes RBAC objects, and joins YAML docs for textual output. No persistent state.
Dependencies/integration: shared Kubernetes RBAC interface, `ghodss/yaml`, corev1/rbacv1 API types, and adjacent YAML templates.
Risks/test signals: `NewCSIProvisionerRBAC` manually constructs ServiceAccount instead of rendering `newServiceAccount`, so divergence from the SA YAML template could go unnoticed; tests cover object creation but not every RBAC rule.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go -->
