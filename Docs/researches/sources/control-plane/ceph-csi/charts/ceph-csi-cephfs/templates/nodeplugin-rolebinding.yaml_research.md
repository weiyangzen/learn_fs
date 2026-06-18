<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml

Purpose: least-privilege RoleBinding for nodeplugin KMS secret access in the secret namespace. It binds the release namespace service account to the Role. Risk is cross-namespace binding mistakes; signal is nodeplugin authorization for the KMS secret.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml -->
