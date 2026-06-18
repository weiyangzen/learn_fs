<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml

Purpose: binds the provisioner service account to the namespaced provisioner Role. Risk is service account naming mismatch. Signal is successful leader election/API access.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml -->
