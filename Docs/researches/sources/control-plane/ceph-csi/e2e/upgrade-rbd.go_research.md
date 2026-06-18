# sources/control-plane/ceph-csi/e2e/upgrade-rbd.go

Purpose: Ginkgo e2e scenario that deploys an older RBD CSI release, provisions data, upgrades to current code, and validates remount, snapshot restore, PVC clone, expansion, and cleanup.

Important APIs and flow: `BeforeEach` gates on `upgradeTesting` and `testRBD`, selects deployment mode, creates namespace when needed, records `cwd`, deploys Vault, clones/deploys the target release, creates config map, RBD StorageClass, Ceph users/secrets, RBD snapshot class, and node topology labels. The test waits for controller and daemonset readiness, provisions a `2Gi` PVC/app, writes and syncs a file, stores SHA512, creates a `VolumeSnapshot`, deletes the app and old plugin, changes back to the current tree, deploys current RBD plugin, remounts the original PVC, restores from the snapshot and checks checksum, creates a PVC clone and checks checksum, expands the original PVC to `5Gi`, validates mounted size, then deletes resources and Ceph users. `AfterEach` dumps CSI logs and namespace information on failure and tears down config, secrets, classes, Vault, plugin, namespace, and node labels.

State and persistence: creates and deletes old/current RBD CSI deployments, Vault, Ceph users, Kubernetes secrets, StorageClass, VolumeSnapshotClass, PVCs, pods, snapshots, clones, node labels, and RBD backend images/snapshots.

Dependencies and integration: uses `upgrade.go`, RBD deployment helpers, RBD StorageClass/secret/snapshot helpers, checksum and pod exec helpers, resize helpers, e2e debug dumps, and example RBD manifests.

Risks and test signals: like the CephFS upgrade test, it depends on `/tmp/ceph-csi` being usable and on working-directory restoration. It assumes snapshot and clone data should match exactly by SHA512. Node labels are global cluster mutations and must be cleaned. Passing tests signal upgrade compatibility for staged/published RBD volumes, snapshots, clones, and expansion across release boundaries.
