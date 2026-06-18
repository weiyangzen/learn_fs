<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml

Purpose: embedded CSIDriver manifest for NFS. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, `seLinuxMount: true`, and `volumeLifecycleModes: Persistent`. Rendered by `NewCSIDriverYAML`; risk is lifecycle/attach policy drift. Unit tests verify basic render only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml -->
