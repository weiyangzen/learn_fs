# sources/control-plane/rook/tests/integration/ceph_base_file_test.go

Shared CephFS integration helpers. It validates filesystem creation, CSI PVC provisioning, pod mount/read/write, deletion blocking by subvolume dependents, snapshot/restore, clone, and cleanup.

Key functions are `runFileE2ETest`, `runFileE2ETestLite`, `fileSystemCSISnapshotTest`, `fileSystemCSICloneTest`, `createFilesystem`, `createFilesystemConsumerPod`, `cleanupFilesystemConsumer`, `cleanupFilesystem`, `getFilesystemCSITestPod`, and `waitForFilesystemActive`. Full flow creates a CephFilesystem, storage class, consumer pod/PVC, writes and reads data, creates a `CephFilesystemSubVolumeGroup`, deletes the filesystem while dependents exist, validates `ConditionDeletionIsBlocked`, removes blockers, and waits for deletion. Lite flow focuses on filesystem creation plus CSI snapshot and clone behavior.

State includes CephFilesystem and CephFilesystemSubVolumeGroup CRs, StorageClasses, PVCs/PVs/Pods, snapshot infrastructure, snapshots, restored PVCs, cloned PVCs, and test files. It depends on Rook FS/NFS clients, `K8sHelper`, Ceph command helpers, Kubernetes polling, and shared block cleanup helpers.

Risks: snapshot CRDs/controllers are global and can race with block/NFS tests; `mountUser` is unused; MDS downscale coverage is commented out; fixed names and default namespace reduce parallel safety. Test signals include filesystem list count, PVC/PV/pod state, read/write checks, snapshot readiness, checksum equality, deletion-blocked condition reason/message, and `ceph fs status` active output.
