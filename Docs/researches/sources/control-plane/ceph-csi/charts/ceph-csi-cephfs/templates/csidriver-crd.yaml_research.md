<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml

Purpose: CSIDriver resource template for the CephFS chart. It sets driver name, labels, `attachRequired` from attacher enablement, `podInfoOnMount`, and values-driven `fsGroupPolicy` and `seLinuxMount`. It integrates with Kubernetes storage registration. Risk is mismatch between driverName and sidecar arguments; signal is successful CSIDriver creation and CSI registration.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml -->
