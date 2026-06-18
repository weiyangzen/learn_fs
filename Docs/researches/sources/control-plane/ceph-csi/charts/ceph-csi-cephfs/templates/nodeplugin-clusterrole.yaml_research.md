<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml

Purpose: node plugin ClusterRole template. It grants node get, configmap get, and optionally broad secret get/list/watch for metadata KMS unless least-privileges mode is enabled. It integrates with nodeplugin service account. Risk is broad cluster secret read when not least-privileged; signal is node plugin access to config/KMS.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml -->
