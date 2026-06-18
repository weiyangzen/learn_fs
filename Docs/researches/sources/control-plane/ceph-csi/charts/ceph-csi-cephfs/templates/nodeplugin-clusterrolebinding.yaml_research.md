<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml

Purpose: binds the nodeplugin service account in the release namespace to the nodeplugin ClusterRole. It is conditional on `rbac.create`. Risk is name coupling to helper templates and missing RBAC when disabled; signal is node pods authorized for required API reads.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml -->
