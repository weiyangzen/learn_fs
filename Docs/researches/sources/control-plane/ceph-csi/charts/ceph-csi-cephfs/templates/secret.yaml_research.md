<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml

Purpose: optional Secret for Ceph user credentials. It requires `.Values.secret.userID` and `.Values.secret.userKey` and writes them under `stringData`. It integrates with StorageClass snapshot/provisioner/node secret references. Risk is storing credentials in Helm release history and render failure when required values are absent. Signal is secret creation and volume operations.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml -->
