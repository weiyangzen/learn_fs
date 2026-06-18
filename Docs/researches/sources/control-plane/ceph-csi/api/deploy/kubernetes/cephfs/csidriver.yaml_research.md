<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml

Purpose: embedded CSIDriver manifest for CephFS. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, and `seLinuxMount: true`. Rendered by `NewCSIDriverYAML`; risk is changing driver identity or mount policy in a way Kubernetes storage behavior depends on. Unit tests verify parse/non-empty but not all spec values.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml -->
