# sources/control-plane/ceph-csi/examples/cephfs/pvc-restore.yaml

Purpose: example CephFS PVC restored from a `VolumeSnapshot`.

Important fields and flow: PVC `cephfs-pvc-restore` uses StorageClass `csi-cephfs-sc`, snapshot data source `cephfs-pvc-snapshot` in API group `snapshot.storage.k8s.io`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: creates a new CephFS volume from snapshot content. Used by snapshot restore and upgrade tests.

Risks and test signals: snapshot must exist and be ready. Restore size must be at least source size. Binding plus checksum tests validate data restoration.
