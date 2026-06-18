<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml

Purpose: embedded NFS provisioner ClusterRoleBinding. It binds `.ServiceAccount` in `.Namespace` to cluster role `nfs-external-provisioner-runner`. Risk is name coupling to the ClusterRole template; tests assert typed object creation only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml -->
