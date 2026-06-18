<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml

Purpose: optional ServiceAccount for provisioner pods. It uses helper-generated name and release/chart labels. Risk is deployment failure when creation is disabled without an existing account. Signal is Deployment admission.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml -->
