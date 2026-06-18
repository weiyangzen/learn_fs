# sources/control-plane/rook/tests/integration/ceph_base_block_test.go

Shared block-storage integration helpers for Rook Ceph test suites. The file exercises CSI RBD provisioning, PVC binding, pod mount/read/write behavior, PVC clone and snapshot/restore flows, reclaim policy behavior, PV cleanup, OSD restart survival, and a lighter block path used by Helm and upgrade tests.

Important functions are `runBlockCSITest`, `runBlockCSITestLite`, `blockCSICloneTest`, `blockCSISnapshotTest`, `setupBlockLite`, `createAndWaitForPVC`, `deletePVC`, `deleteBlockLite`, `blockTestDataCleanUp`, `retryBlockImageCountCheck`, `retryPVCheck`, and `getCSIBlockPodDefinition`. Full flow creates Delete and Retain RBD-backed storage classes/PVCs, mounts pods, writes and reads data, restarts OSD pods, validates reclaim behavior, then deletes pools and storage classes. Lite flow sets up a single RBD PVC and runs clone/snapshot checks.

State spans Kubernetes PVCs, PVs, Pods, StorageClasses, snapshot CRDs/controllers/classes/snapshots, CephBlockPool CRs, and backend RBD images. Persistence signals are checksum equality across clone/restore and read-after-OSD-restart. Dependencies include Rook `BlockClient`/`PoolClient`, `utils.K8sHelper`, `client.AdminTestClusterInfo`, Kubernetes API helpers, and testify.

Risks: the RWO fencing assertion is commented out, fixed names and `default` namespace usage limit parallelism, snapshot infrastructure is cluster-global, and cleanup relies on not-found-tolerant helpers after partial setup. Test signals include PVC bound/deleted checks, image counts, pod state, PV deletion/release state, checksum matches, OSD readiness, and pool deletion polling.
