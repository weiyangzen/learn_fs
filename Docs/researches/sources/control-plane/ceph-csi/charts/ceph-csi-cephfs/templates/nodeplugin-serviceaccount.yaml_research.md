<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml

Purpose: optional ServiceAccount for nodeplugin pods. It uses helper-generated name, release namespace, chart labels, and common labels. Risk is mismatch when users disable creation but do not provide an existing account; signal is DaemonSet admission.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml -->
