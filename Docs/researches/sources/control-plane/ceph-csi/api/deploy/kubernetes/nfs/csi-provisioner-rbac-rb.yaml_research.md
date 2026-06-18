<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml

Purpose: embedded RoleBinding for the NFS provisioner namespaced Role. It binds `.ServiceAccount` in `.Namespace` to `nfs-external-provisioner-cfg`. Risk is template/name coupling; tests verify parsing only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml -->
