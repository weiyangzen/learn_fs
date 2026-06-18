# sources/control-plane/rook/tests/integration/ceph_base_nfs_test.go

CephNFS integration helper layering NFS and optional NFS CSI validation on CephFS helpers. `runNFSFileE2ETest` creates a backing CephFilesystem, a CephNFS cluster named `my-nfs`, and, when `settings.TestNFSCSI` is true, an NFS CSI StorageClass plus consumer pod read/write, snapshot, and clone checks.

State includes CephFilesystem, CephNFS, NFS CSI StorageClass, PVC/PV/Pod resources, snapshot classes/snapshots/restored PVCs, cloned PVCs, and file contents. It depends on `helper.NFSClient`, shared CephFS helpers, `K8sHelper`, and testify.

Risks: an `assert.NoError` after `cleanupFilesystemConsumer` checks the prior error value rather than cleanup; snapshot CRD/controller resources are global; fixed names (`my-nfs`, `nfs-storageclass`, `file-test`) constrain parallelism; without `TestNFSCSI`, the helper mostly validates CR lifecycle rather than data access. Signals are create/delete success, pod state, read/write validation, snapshot/clone checksum equality, and PVC/PV cleanup.
