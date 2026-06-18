# sources/control-plane/ceph-csi/examples/nfs/pvc-clone.yaml

Purpose: example NFS PVC clone from another PVC.

Important fields and flow: PVC `nfs-pvc-clone` uses StorageClass `csi-nfs-sc`, source PVC `csi-nfs-pvc`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: requests a new NFS export backed by cloned CephFS data.

Risks and test signals: source PVC name in this file differs from baseline `cephcsi-nfs-pvc`, so examples or tests may need name adjustment. Binding and data checks validate clone behavior.
