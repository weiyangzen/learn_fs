<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml

Purpose: optional CephFS StorageClass template. It sets provisioner driver, clusterID, fsName, optional pool/encryption/KMS/mount/mounter/volume prefix parameters, CSI secret references for provisioner, expand, controller-publish, and node-stage operations, reclaimPolicy, expansion flag, and mountOptions. Risk is incorrect secret namespaces, missing fsName/clusterID, or enabling encryption without KMS config. Signal is PVC provisioning and mount success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml -->
