<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml

Purpose: binds the provisioner service account to the provisioner ClusterRole when RBAC is enabled. Risk is helper-name coupling and missing permissions when `rbac.create=false`. Signal is sidecar authorization.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml -->
