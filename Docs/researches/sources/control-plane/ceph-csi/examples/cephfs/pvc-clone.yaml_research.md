# sources/control-plane/ceph-csi/examples/cephfs/pvc-clone.yaml

Purpose: example CephFS PVC clone from another PVC.

Important fields and flow: PVC `cephfs-pvc-clone` uses StorageClass `csi-cephfs-sc`, `dataSource` kind `PersistentVolumeClaim` named `csi-cephfs-pvc`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: requests dynamic provisioning of a CephFS clone. E2E clone tests update names and bind it to clone pods.

Risks and test signals: source PVC must exist and support cloning. Binding and checksum preservation validate clone correctness.
