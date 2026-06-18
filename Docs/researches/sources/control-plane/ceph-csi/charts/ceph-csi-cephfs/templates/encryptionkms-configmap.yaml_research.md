<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml

Purpose: KMS configuration ConfigMap. It writes `config.json` from `.Values.encryptionKMSConfig` and labels as nodeplugin component. It integrates with encryption features in Ceph CSI. Risk is leaking or misplacing KMS metadata and invalid JSON; signal is encrypted volume workflow success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml -->
