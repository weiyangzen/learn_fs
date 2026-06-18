<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml

Purpose: least-privilege namespaced Role for metadata KMS secret access. It renders only when RBAC and leastPrivileges are enabled and metadata KMS secret namespace/name are set, granting get on a single secret resourceName. Risk is absent role when KMS values are incomplete; signal is encrypted volume key retrieval.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml -->
