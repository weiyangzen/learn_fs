# sources/control-plane/ceph-csi/examples/cephfs/pvc.yaml

Purpose: baseline dynamically provisioned CephFS PVC example.

Important fields and flow: PVC `csi-cephfs-pvc` requests `1Gi`, `ReadWriteMany`, and StorageClass `csi-cephfs-sc`.

State, dependencies, and integration: creates a CephFS subvolume through the provisioner. It is the source object for baseline pod, deployment, clone, snapshot, resize, and data persistence examples.

Risks and test signals: requires valid StorageClass and secrets. Bound status and successful pod mount are the primary signals.
