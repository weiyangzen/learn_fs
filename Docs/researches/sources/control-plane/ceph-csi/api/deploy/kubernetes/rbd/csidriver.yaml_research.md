<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml

Purpose: embedded CSIDriver manifest for RBD. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `seLinuxMount: true`, and `fsGroupPolicy: File`. Rendered by `NewCSIDriverYAML`; risk is spec drift affecting attach and SELinux behavior. Unit tests only verify basic rendering.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml -->
