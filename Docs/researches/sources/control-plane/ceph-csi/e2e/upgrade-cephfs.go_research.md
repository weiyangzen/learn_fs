# sources/control-plane/ceph-csi/e2e/upgrade-cephfs.go

Purpose: Ginkgo e2e scenario that deploys an older CephFS CSI release, creates data, upgrades back to the current code, and validates remount, snapshot restore, PVC clone, resize, and cleanup compatibility.

Important APIs and flow: the `Describe("CephFS Upgrade Testing")` block creates a privileged framework namespace. `BeforeEach` gates on `upgradeTesting` and `testCephFS`, initializes deployment method, creates namespace when needed, records working directory, deploys Vault, clones/deploys the requested older release via `upgradeAndDeployCSI`, creates config map, CephFS users/secrets, snapshot class, and storage class. The main `It` waits for provisioner and nodeplugin readiness, creates PVC/app, writes and syncs a test file, records SHA512, snapshots the PVC, validates backend snapshot count, deletes app and old plugin, changes back to current source, deploys current plugin, remounts the old PVC, restores from snapshot and validates checksum, creates a smart clone and validates checksum, expands the original PVC, then deletes app/PVC and Ceph users. `AfterEach` dumps logs on failure and removes config, secrets, classes, Vault, plugin, namespace, and related resources.

State and persistence: touches two versions of CephFS CSI deployment, Vault resources, Ceph users, Kubernetes secrets, StorageClass, VolumeSnapshotClass, PVCs, pods, snapshots, clones, and CephFS subvolume/snapshot backend state.

Dependencies and integration: integrates Ginkgo/Gomega-style e2e framework, deployment helpers, `upgrade.go`, snapshot helpers, resize helpers, CephFS backend validators, checksum helpers, Vault/KMS setup, and example CephFS manifests.

Risks and test signals: `upgradeCSI` clones into `/tmp/ceph-csi`, so stale directories can break repeated runs. The test relies on current working directory switching to return from the cloned release to the current tree. Cleanup uses fatal `logAndFail`, so one cleanup failure can obscure later leaks. Passing signals backward compatibility for existing CephFS volumes, snapshot data, clone data, resize behavior, and deployment manifests.
