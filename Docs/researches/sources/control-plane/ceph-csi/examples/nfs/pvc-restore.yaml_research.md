# sources/control-plane/ceph-csi/examples/nfs/pvc-restore.yaml

Purpose: example NFS PVC restored from snapshot.

Important fields and flow: PVC `nfs-pvc-restore` uses StorageClass `csi-nfs-sc`, snapshot data source `nfs-pvc-snapshot`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: provisions an NFS export backed by restored snapshot data.

Risks and test signals: snapshot must exist and the restored PVC must satisfy source size. Pod access validates restore.
