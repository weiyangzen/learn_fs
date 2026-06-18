# subset-b-000342 Research

Grouped research report for the requested Ceph-CSI e2e and example subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/rbd_helper.go -->
# sources/control-plane/ceph-csi/e2e/rbd_helper.go

Purpose: central RBD e2e helper library for Ceph-CSI. It creates and mutates RBD StorageClasses, secrets, pools, namespaces, VolumeAttributesClasses, PVC/PV bindings, and Ceph backend state, then validates image metadata, encryption, cloning, snapshot side effects, QoS, service-account restrictions, and cleanup.

Important APIs and flow: `imageSpec` and `rbdOptions` build pool/image command arguments with optional `radosNamespace`. `supportsVolumeAttributesClass` gates VAC tests on Kubernetes and ceph-csi versions. `createRBDStorageClass`, `createKRBDStorageClassWithModifySecret`, `createRBDSecret`, `createRadosNamespace`, `createRBDVolumeAttributesClass`, `deleteRBDVolumeAttributesClass`, and `modifyPVCVolumeAttributesClass` prepare Kubernetes storage objects and wait for status convergence. `getImageInfoFromPVC`, `getEncryptionOptionsFromPV`, `getLuksStatusFromMount`, `getImageMeta`, `setImageMeta`, and `removeImageMeta` connect Kubernetes PVC/PV state to backend RBD metadata. Higher-level validators cover clone-in-different-pool scenarios, encrypted block and filesystem PVCs, RBD group snapshot support detection, image/snapshot/trash listing, pool deletion/creation, journal OMAP checks, stripe/image-feature/data-pool checks, cgroup and RBD QoS, multi-PVC pod creation, I/O enforcement, and service-account based volume access restrictions.

Control flow: most helpers follow create or discover Kubernetes resource, derive image identity from the bound PV, execute Ceph CLI commands inside the toolbox or CSI pods, poll API/backend state, then delete resources. Clone and snapshot validators use goroutines plus per-index error arrays to create many snapshots or clones in parallel and log all failures before failing. Encryption validation checks RBD image metadata first, then inspects node-plugin mount state or filesystem attributes, verifies KMS passphrase creation, deletes PVC/app objects, and confirms KMS cleanup or key destruction.

State and persistence: persistent effects include Kubernetes StorageClasses, VolumeAttributesClasses, Secrets, ServiceAccounts, Pods, PVCs, PVs, RBD images, snapshots, pools, namespaces, OMAP journals, RBD image metadata, KMS passphrases, cgroup I/O state, and trash entries. Process-local state is limited to helper structs such as `imageInfoFromPVC`, `snapInfo`, `imageInfo`, and test-local error slices; backend state is authoritative.

Dependencies and integration: depends on Kubernetes client-go, e2e framework/Gomega, external-snapshotter APIs, Ceph toolbox commands (`rbd`, `rados`, `ceph`), CSI node/provisioner pods, `cryptsetup` parsing, kernel capability gates, and shared e2e helpers from `utils.go`. It integrates with RBD examples under `examples/rbd`, KMS test configs, Ceph user helpers, and version gates for VAC and librbd group snapshot support.

Risks and test signals: many checks depend on exact CLI output and on `stdErr == ""`, so Ceph warnings can fail tests. Parallel clone/snapshot paths reuse template object copies and require careful per-goroutine mutation. `modifyPVCVolumeAttributesClass` uses a Gomega `Expect` inside a helper, causing immediate test failure rather than returning update errors. The service-account restriction test waits for detach before metadata changes, which is important for a fresh `ControllerPublishVolume`. Strong test signals include backend image counts, OMAP counts, metadata assertions, KMS passphrase lifecycle checks, checksum preservation, and pod mount success/failure.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/rbd_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/resize.go -->
# sources/control-plane/ceph-csi/e2e/resize.go

Purpose: provides reusable PVC expansion helpers for filesystem and raw-block e2e cases.

Important APIs and flow: `expandPVCSize` fetches the latest PVC, updates `Spec.Resources.Requests[storage]`, then polls until resize conditions clear and `Status.Capacity` equals the requested size. `resizePVCAndValidateSize` accepts either a PVC YAML path or a prebuilt PVC, creates the PVC plus app pod, validates the initial mounted size, expands to `10Gi`, waits for the pod, revalidates the mounted size, and deletes both objects. `checkDirSize`, `checkDeviceSize`, `getDirSizeCheckCmd`, `getDeviceSizeCheckCmd`, and `checkAppMntSize` wrap pod-exec size probes.

State and persistence: mutates PVC spec/status in the Kubernetes API and validates filesystem or block-device state from inside an app pod. It creates and deletes one PVC and one pod in the test namespace when using `resizePVCAndValidateSize`.

Dependencies and integration: uses client-go PVC updates, Kubernetes wait polling, e2e pod exec helpers, `resource.Quantity`, and `helpers.RoundUpToGiB`. It is reused by RBD, CephFS, NFS, static PV, controller recovery, and upgrade tests.

Risks and test signals: `expandPVCSize` assumes any first condition of `Resizing` or `FileSystemResizePending` means it should keep waiting; additional conditions are only logged. Block size validation parses `blockdev --getsize64` output as a Kubernetes quantity and rounds to GiB. Filesystem validation shells through `df -h|grep`, which can be sensitive to mount path matching and human-readable units. Passing tests prove the controller expansion and node expansion paths converged and are visible in the workload.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/resize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/snapshot.go -->
# sources/control-plane/ceph-csi/e2e/snapshot.go

Purpose: wraps Kubernetes CSI snapshot APIs for e2e creation, deletion, class setup, content discovery, and restore-size validation.

Important APIs and flow: `getSnapshotClass` and `getSnapshot` unmarshal example YAML. `newSnapshotClient` builds an external-snapshotter v1 client from the e2e kubeconfig. `createSnapshot` creates a `VolumeSnapshot` and polls `Status.ReadyToUse`. `deleteSnapshot` deletes and polls for NotFound. `createRBDSnapshotClass`, `createCephFSSnapshotClass`, and `createNFSSnapshotClass` load example classes, inject cluster ID and secret references, then create them. Delete helpers remove the classes. `getVolumeSnapshotContent` follows `VolumeSnapshot.Status.BoundVolumeSnapshotContentName`. `validateBiggerPVCFromSnapshot` provisions a source PVC/app, snapshots it, restores into a larger PVC, validates filesystem or block size, and for block RBD verifies snapshot metadata keys were not propagated to the restored image.

State and persistence: creates cluster-scoped `VolumeSnapshotClass` objects, namespace-scoped `VolumeSnapshot` and PVC/app objects, and backend snapshots through the CSI snapshotter. Restore validation leaves no intended resources after cleanup.

Dependencies and integration: depends on external-snapshotter client APIs, shared PVC/pod helpers, RBD/CephFS/NFS example paths, cluster ID discovery, RBD metadata helpers, and resize validation from `resize.go`.

Risks and test signals: snapshot readiness depends on CRD/controller availability. `getVolumeSnapshotContent` dereferences snapshot status fields and assumes the snapshot is already bound. `validateBiggerPVCFromSnapshot` assumes an RBD image list ordering when checking restored block metadata. Successful tests signal snapshot class wiring, snapshot controller readiness, restore provisioning, resize-from-snapshot support, and correct cleanup of snapshot metadata on RBD restore.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/staticpvc.go -->
# sources/control-plane/ceph-csi/e2e/staticpvc.go

Purpose: constructs and validates statically provisioned RBD and CephFS PV/PVC objects, including migration-style RBD volumes and static resize behavior.

Important APIs and flow: `getStaticPV` builds a CSI PV with driver name, volume handle, volume attributes, node-stage secret, reclaim policy, volume mode, optional annotations, and storage class. `getStaticPVC` binds a PVC directly to that PV. `validateRBDStaticPV` creates a backend RBD image, constructs a static RBD PV/PVC, starts an app or expects a missing `imageFeatures` failure, validates static resize by resizing the backend image and remounting, then deletes PV/PVC and the image. `validateRBDStaticMigrationPVC` creates an in-tree migration-like volume handle from monitors and image name, annotates the PV as provisioned by RBD CSI, mounts it, then deletes through CSI. `validateCephFsStaticPV` creates a CephFS subvolume group and subvolume, discovers root path, creates a secret with admin key, binds a static CephFS PV/PVC, mounts it, then deletes pod, PVC, PV, secret, subvolume, and group. `validateRBDStaticResize` exercises backend resize visibility after remount.

State and persistence: creates real backend RBD images or CephFS subvolumes, Kubernetes PV/PVC/Secret objects, and app pods. Static RBD PVs use Retain for normal static tests and Delete for migration tests; cleanup explicitly removes retained backend images or CephFS objects.

Dependencies and integration: uses Ceph toolbox commands, Kubernetes core APIs, RBD namespace helpers, monitor discovery, migration volume ID composition, CephFS secret templates, static volume CSI attributes, and shared app/PVC lifecycle helpers.

Risks and test signals: static provisioning depends on exact CSI volume attributes such as `staticVolume`, `imageFeatures`, `rootPath`, `pool`, `clusterID`, and optional `radosNamespace`. Cleanup is multi-step and can leak backend resources if an early error returns. CephFS static validation uses admin credentials from the toolbox and fixed names, which can collide if tests run concurrently in the same cluster. Passing tests prove NodeStage/NodePublish can consume pre-existing backend volumes and migration handles.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/staticpvc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-block-deployment.yaml -->
# sources/control-plane/ceph-csi/e2e/templates/rbd-block-deployment.yaml

Purpose: Kubernetes Deployment template for testing RBD raw block PVC use by multiple replicas. It runs three CentOS pods and exposes PVC `raw-block-pvc` as `/dev/xvda` through `volumeDevices`.

Important fields and flow: `metadata.name` and labels are `pod-block-rx-volume`; selector matches the pod template label; container sleeps forever to keep the block device attached. The `data` volume references the PVC with `readOnly: false`.

State, dependencies, and integration: creates an apps/v1 Deployment and resulting Pods that attach an existing block-mode RBD PVC. It is consumed by e2e helpers that validate deployment binding, multi-replica attach semantics, and block device availability.

Risks and test signals: requires a compatible block-mode PVC and access mode that permits the requested replica count. The `latest` CentOS image makes runtime behavior dependent on registry availability. Success is observed through Deployment readiness and pod-visible block device paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-block-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-fs-deployment.yaml -->
# sources/control-plane/ceph-csi/e2e/templates/rbd-fs-deployment.yaml

Purpose: Kubernetes Deployment template for testing filesystem RBD PVC use across three nginx replicas.

Important fields and flow: Deployment `pod-fs-rx-volume` selects matching labels, runs `nginx:latest`, and mounts PVC `rbd-pvc` at `/var/lib/www/html`. The template keeps `readOnly: false` for write-capable filesystem validation.

State, dependencies, and integration: creates a Deployment and pods that depend on an existing filesystem-mode RBD PVC. E2E helpers load and optionally adjust replica counts to test binding and controller behavior.

Risks and test signals: multi-replica RBD filesystem use requires access-mode compatibility. The `latest` image tag and external registry can affect reproducibility. Readiness confirms Kubernetes attach/mount and application container startup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-fs-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-block.yaml -->
# sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-block.yaml

Purpose: Pod template for testing a single workload with three raw block RBD PVCs.

Important fields and flow: Pod `pod-multi-pvc-block` runs a sleeping CentOS container with `volumeDevices` `vol-0`, `vol-1`, and `vol-2` mapped to `/dev/xvda`, `/dev/xvdb`, and `/dev/xvdc`. Volumes reference PVCs `rbd-pvc-0` through `rbd-pvc-2`.

State, dependencies, and integration: creates one Pod that attaches multiple existing block-mode PVCs. It complements helper-created multi-PVC pods and exercises code paths that must update per-device cgroup or staging state without overwriting sibling volumes.

Risks and test signals: device path collisions or missing block PVCs will fail pod startup. It uses a long-running sleep command, so validation depends on external exec checks. Passing tests indicate all three devices attach and publish to the same pod.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-block.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-fs.yaml -->
# sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-fs.yaml

Purpose: Pod template for testing a single workload with three filesystem RBD PVC mounts.

Important fields and flow: Pod `pod-multi-pvc-fs` runs a sleeping CentOS container and mounts PVCs `rbd-pvc-0`, `rbd-pvc-1`, and `rbd-pvc-2` at `/mnt/vol-0`, `/mnt/vol-1`, and `/mnt/vol-2`.

State, dependencies, and integration: creates one Pod that requires three existing filesystem-mode PVCs. It is used by QoS and multi-volume attach tests to validate independent mount handling in one cgroup and pod.

Risks and test signals: missing PVCs, access-mode conflicts, or mount path issues prevent pod readiness. Success gives direct signal that multiple filesystem volumes can be published to a single pod without state collision.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/templates/rbd-multi-pvc-pod-fs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade-cephfs.go -->
# sources/control-plane/ceph-csi/e2e/upgrade-cephfs.go

Purpose: Ginkgo e2e scenario that deploys an older CephFS CSI release, creates data, upgrades back to the current code, and validates remount, snapshot restore, PVC clone, resize, and cleanup compatibility.

Important APIs and flow: the `Describe("CephFS Upgrade Testing")` block creates a privileged framework namespace. `BeforeEach` gates on `upgradeTesting` and `testCephFS`, initializes deployment method, creates namespace when needed, records working directory, deploys Vault, clones/deploys the requested older release via `upgradeAndDeployCSI`, creates config map, CephFS users/secrets, snapshot class, and storage class. The main `It` waits for provisioner and nodeplugin readiness, creates PVC/app, writes and syncs a test file, records SHA512, snapshots the PVC, validates backend snapshot count, deletes app and old plugin, changes back to current source, deploys current plugin, remounts the old PVC, restores from snapshot and validates checksum, creates a smart clone and validates checksum, expands the original PVC, then deletes app/PVC and Ceph users. `AfterEach` dumps logs on failure and removes config, secrets, classes, Vault, plugin, namespace, and related resources.

State and persistence: touches two versions of CephFS CSI deployment, Vault resources, Ceph users, Kubernetes secrets, StorageClass, VolumeSnapshotClass, PVCs, pods, snapshots, clones, and CephFS subvolume/snapshot backend state.

Dependencies and integration: integrates Ginkgo/Gomega-style e2e framework, deployment helpers, `upgrade.go`, snapshot helpers, resize helpers, CephFS backend validators, checksum helpers, Vault/KMS setup, and example CephFS manifests.

Risks and test signals: `upgradeCSI` clones into `/tmp/ceph-csi`, so stale directories can break repeated runs. The test relies on current working directory switching to return from the cloned release to the current tree. Cleanup uses fatal `logAndFail`, so one cleanup failure can obscure later leaks. Passing signals backward compatibility for existing CephFS volumes, snapshot data, clone data, resize behavior, and deployment manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade-cephfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade-rbd.go -->
# sources/control-plane/ceph-csi/e2e/upgrade-rbd.go

Purpose: Ginkgo e2e scenario that deploys an older RBD CSI release, provisions data, upgrades to current code, and validates remount, snapshot restore, PVC clone, expansion, and cleanup.

Important APIs and flow: `BeforeEach` gates on `upgradeTesting` and `testRBD`, selects deployment mode, creates namespace when needed, records `cwd`, deploys Vault, clones/deploys the target release, creates config map, RBD StorageClass, Ceph users/secrets, RBD snapshot class, and node topology labels. The test waits for controller and daemonset readiness, provisions a `2Gi` PVC/app, writes and syncs a file, stores SHA512, creates a `VolumeSnapshot`, deletes the app and old plugin, changes back to the current tree, deploys current RBD plugin, remounts the original PVC, restores from the snapshot and checks checksum, creates a PVC clone and checks checksum, expands the original PVC to `5Gi`, validates mounted size, then deletes resources and Ceph users. `AfterEach` dumps CSI logs and namespace information on failure and tears down config, secrets, classes, Vault, plugin, namespace, and node labels.

State and persistence: creates and deletes old/current RBD CSI deployments, Vault, Ceph users, Kubernetes secrets, StorageClass, VolumeSnapshotClass, PVCs, pods, snapshots, clones, node labels, and RBD backend images/snapshots.

Dependencies and integration: uses `upgrade.go`, RBD deployment helpers, RBD StorageClass/secret/snapshot helpers, checksum and pod exec helpers, resize helpers, e2e debug dumps, and example RBD manifests.

Risks and test signals: like the CephFS upgrade test, it depends on `/tmp/ceph-csi` being usable and on working-directory restoration. It assumes snapshot and clone data should match exactly by SHA512. Node labels are global cluster mutations and must be cleaned. Passing tests signal upgrade compatibility for staged/published RBD volumes, snapshots, clones, and expansion across release boundaries.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade-rbd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade.go -->
# sources/control-plane/ceph-csi/e2e/upgrade.go

Purpose: small helper layer for upgrade tests that checks out a requested ceph-csi release branch and deploys the selected driver from that checkout.

Important APIs and flow: `upgradeCSI` runs `git clone --single-branch --branch <version> https://github.com/ceph/ceph-csi.git /tmp/ceph-csi`, streams output to the test process, and changes directory to `/tmp/ceph-csi/e2e`. `upgradeAndDeployCSI` calls `upgradeCSI`, then dispatches to `deployCephfsPlugin` or `deployRBDPlugin` based on `testtype`.

State and persistence: writes a clone under `/tmp/ceph-csi` and mutates process current working directory. It deploys Kubernetes resources indirectly through driver-specific deploy helpers.

Dependencies and integration: uses local `git`, OS process execution, and driver deployment functions. It is called from `upgrade-cephfs.go` and `upgrade-rbd.go`.

Risks and test signals: no cleanup or pre-removal of `/tmp/ceph-csi` is performed, so reruns can fail if the directory exists. Working-directory mutation is process-global and relies on callers to restore `cwd`. The only direct validation is successful clone, chdir, and deploy helper completion.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/utils.go -->
# sources/control-plane/ceph-csi/e2e/utils.go

Purpose: broad shared utility library for Ceph-CSI e2e tests, covering deployment metadata, cluster discovery, YAML loading, Kubernetes resource lifecycle, pod exec validations, clone/snapshot workflows, version gates, kubectl retries, NFS export validation, and CephFS subvolume group management.

Important APIs and flow: global flags and constants define enabled drivers, namespaces, poll cadence, reclaim policies, app labels, cluster name, and cached monitors. `DeploymentMethod` and `DriverInfo` abstract deployment/daemonset names, pod selectors, cluster name updates, and fencing toggles. Ceph discovery helpers list CephFS filesystems, metadata pools, monitors, monitor hashes, and cluster ID. YAML helpers load StorageClasses, VolumeAttributesClasses, Secrets, and arbitrary manifests; `deleteResource` applies namespace replacement then `kubectl delete`s. Lifecycle helpers create/delete PVC+Pod, PVC+Deployment, wait-for-first-consumer flows, normal-user access tests, inode checks, mount option checks, LUKS status, data persistence, and data writing/checksum calculation.

Control flow: validation helpers generally load templates, set namespace/name/labels, create PVCs and apps, poll for readiness or backend counts, execute commands in app/toolbox/CSI pods, then delete resources. `validatePVCClone` and `validatePVCSnapshot` are high-complexity concurrent workflows: they create source PVCs, write data, create multiple clones or snapshots, verify checksums/KMS/data-pool/encryption/backend image counts, delete resources in staged order, and assert final backend cleanup. `validateController` simulates controller recovery by creating a retained PVC/PV, deleting OMAP journal data, recreating static binding, mounting, then resizing or validating encryption. Version helpers parse Kubernetes and ceph-csi versions and gate features. Kubectl retry helpers feed input, files, or args through e2e kubectl with retry-aware handling. NFS helpers parse detailed export JSON and validate client access entries.

State and persistence: mutates Kubernetes namespaces, PVCs, PVs, Pods, Deployments, Jobs, StorageClasses, Secrets, VolumeSnapshots, VolumeAttributesClasses, and node/plugin deployments indirectly. Backend persistence includes Ceph OMAP journals, RBD/CephFS/NFS objects, KMS passphrases, NFS exports, and subvolume groups. Process-local state includes global flags, `clusterID`, `monsCache`, and `rwopSupported`.

Dependencies and integration: depends on client-go, Kubernetes e2e framework and kubectl wrapper, external snapshotter APIs, Ceph toolbox commands, cryptsetup parsing, RBD helpers, CephFS/NFS helpers, app/deployment loaders, and common test constants from the e2e package. It is one of the main integration hubs for nearly every driver e2e test.

Risks and test signals: many helpers call `logAndFail` or Gomega expectations from utility code, which can abort tests instead of returning errors. Several shell commands are string-composed and parse grep/awk output, making them sensitive to formatting and warnings. Global caches and flags are not concurrency-safe across fully parallel suites. `retryKubectlInput` joins extra args without separators, which is safe only for the current calling patterns. Strong signals include API readiness, backend OMAP/image/export counts, checksum preservation, mount flags, non-root write access, version parsing unit tests, and final zero-resource backend assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/utils_test.go -->
# sources/control-plane/ceph-csi/e2e/utils_test.go

Purpose: unit tests the ceph-csi version parser used for feature gating in e2e helpers.

Important APIs and flow: `TestParseCephCSIVersion` runs parallel subtests for `canary`, `v3.16-canary`, `v3.17-canary`, release versions such as `v3.16.8`, and invalid strings. It asserts parsed major/minor values and expected error presence.

State and persistence: no external state; pure in-memory table test.

Dependencies and integration: covers `parseCephCSIVersion` in `utils.go`, including the convention that unversioned `canary` maps to `math.MaxInt` for feature gates.

Risks and test signals: useful focused signal for version parsing, but it does not test `getCephCSIVersion` output scanning or pod exec failures. It protects VAC and other feature gates from regressions in release/canary string handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/volumegroupsnapshot.go -->
# sources/control-plane/ceph-csi/e2e/volumegroupsnapshot.go

Purpose: driver-specific VolumeGroupSnapshot e2e implementations for CephFS and RBD, layered over the shared base workflow.

Important APIs and flow: `newCephFSVolumeGroupSnapshot` and `newRBDVolumeGroupSnapshot` create a `volumeGroupSnapshotterBase` and wrap it with driver-specific validation. Both `TestVolumeGroupSnapshot` methods delegate to the base. CephFS `GetVolumeGroupSnapshotClass` loads the CephFS group snapshot class, injects secret refs, `fsName`, and cluster ID. CephFS create validation obtains the metadata pool, inspects the `VolumeGroupSnapshotContent`, computes expected derived `VolumeSnapshot` names from group snapshot UID plus volume handle, validates clone subvolume count, per-source snapshot count, and OMAP counts for volumes/snaps/groupsnaps. CephFS delete validation requires zero OMAP counts. RBD class setup injects RBD secret refs, pool, and cluster ID; create validation checks volume OMAP count after clones; delete validation checks zero volume/snap/group OMAPs, zero RBD images, and trash cleanup.

State and persistence: creates driver-specific `VolumeGroupSnapshotClass` parameters and validates backend CephFS metadata pool OMAPs, CephFS subvolume snapshots, RBD OMAPs, RBD images, and trash entries.

Dependencies and integration: depends on external-snapshotter group snapshot APIs, shared base workflow, cluster ID discovery, CephFS metadata pool helpers, OMAP validators, RBD image/trash helpers, and example group snapshot class YAML.

Risks and test signals: derived snapshot names duplicate external-snapshotter naming logic using SHA256 of UID and volume handle, so upstream naming changes would break validation. Backend count assertions are strong but can fail if unrelated test resources share the same pools. Passing tests signal that group snapshots create per-volume snapshots, clones can be created, and driver metadata is fully cleaned.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/volumegroupsnapshot_base.go -->
# sources/control-plane/ceph-csi/e2e/volumegroupsnapshot_base.go

Purpose: shared VolumeGroupSnapshot test harness that creates PVC groups, group snapshot classes, group snapshots, clones, pods, and cleanup in a driver-neutral way.

Important APIs and flow: `volumeGroupSnapshotter` defines common create/delete operations; exported `VolumeGroupSnapshotter` adds driver-specific class construction and backend validation. `newVolumeGroupSnapshotBase` builds group snapshot and volume snapshot clients. `CreatePVCs` provisions labeled PVCs with requested volume mode. `CreatePVCClones` reads the bound group snapshot content, locates each generated `VolumeSnapshot`, copies the source PVC spec, sets a snapshot data source, clears `VolumeName`, and provisions clones. `CreatePods` starts one sleeping CentOS pod per clone with either a block device or filesystem mount. `CreateVolumeGroupSnapshotClass`, `CreateVolumeGroupSnapshot`, `DeleteVolumeGroupSnapshot`, and `DeleteVolumeGroupSnapshotClass` wrap CRD operations with polling. `testVolumeGroupSnapshot` orchestrates source PVC creation, class creation, primary and additional group snapshots, clone creation, pod creation, backend validation, pod/clone/source cleanup, snapshot deletion, backend delete validation, and class deletion.

State and persistence: creates Kubernetes PVCs, Pods, VolumeGroupSnapshotClasses, VolumeGroupSnapshots, generated VolumeSnapshots/Contents, and clone PVCs. Backend persistence is validated by driver-specific implementations.

Dependencies and integration: depends on external-snapshotter v1beta2 group snapshot client, volume snapshot client, core Kubernetes API, shared PVC/pod helpers, and driver implementations in `volumegroupsnapshot.go`.

Risks and test signals: cleanup is sequential and returns on first error, so later resources may leak when an earlier delete fails. Snapshot clone creation assumes generated VolumeSnapshot names follow SHA256 naming over group snapshot UID and volume handle. Additional group snapshots exercise create/delete churn before clone validation. Passing tests confirm group snapshot CRD readiness, source selection by labels, clone provisioning from generated snapshots, pod publishing, and backend cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/volumegroupsnapshot_base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/deployment.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/deployment.yaml

Purpose: example nginx Deployment that consumes the standard CephFS PVC.

Important fields and flow: Deployment `csi-cephfs-demo-depl` runs one `web-server` replica and mounts PVC `csi-cephfs-pvc` at `/var/lib/www/html`.

State, dependencies, and integration: creates an apps/v1 Deployment relying on `pvc.yaml` and `storageclass.yaml`. E2E helpers load it for PVC+Deployment binding checks.

Risks and test signals: depends on the PVC being bound and nginx image availability. Readiness validates that a CephFS filesystem volume can be published into a Deployment workload.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/exec-bash.sh -->
# sources/control-plane/ceph-csi/examples/cephfs/exec-bash.sh

Purpose: operator convenience script for opening an interactive shell in the first CephFS nodeplugin pod.

Important APIs and flow: selects a pod with label `app=csi-cephfsplugin`, polls its phase until `Running`, then runs `kubectl exec -it <pod> -c csi-cephfsplugin bash`.

State, dependencies, and integration: reads pod status and opens an exec session; it does not create cluster resources. It integrates with the example/development deployment labels.

Risks and test signals: assumes label uniqueness, namespace from current kubectl context, and bash availability in the container. It has no timeout and can wait forever if the pod never runs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/exec-bash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/groupsnapshot.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/groupsnapshot.yaml

Purpose: example `VolumeGroupSnapshot` selecting CephFS PVCs by label.

Important fields and flow: creates `new-groupsnapshot-demo-1` with selector `group: test` and class `csi-cephfsplugin-groupsnapclass`. Any PVCs with that label are included by the group snapshot controller.

State, dependencies, and integration: creates a namespace-scoped group snapshot CRD instance and requires the group snapshot CRDs/controller plus `groupsnapshotclass.yaml`.

Risks and test signals: unlabeled PVCs are ignored, and unsupported clusters will reject the CRD. Readiness signals group snapshot controller and CephFS driver support.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/groupsnapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/groupsnapshotclass.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/groupsnapshotclass.yaml

Purpose: example cluster-scoped `VolumeGroupSnapshotClass` for CephFS.

Important fields and flow: uses driver `cephfs.csi.ceph.com`, placeholder `clusterID` and `fsName`, group snapshotter secret name/namespace, and `deletionPolicy: Delete`.

State, dependencies, and integration: configures how group snapshot requests reach the CephFS CSI group snapshotter. E2E code loads this file and injects real cluster ID, filesystem name, and secret namespace/name.

Risks and test signals: placeholders must be replaced before real use. Delete policy removes backend snapshots with the class-owned content. Successful creation is required before `groupsnapshot.yaml` can become ready.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/groupsnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/logs.sh -->
# sources/control-plane/ceph-csi/examples/cephfs/logs.sh

Purpose: convenience script for following logs from the first CephFS nodeplugin pod.

Important APIs and flow: selects `app=csi-cephfsplugin`, waits until the pod phase is `Running`, and executes `kubectl logs -f` for container `csi-cephfsplugin`.

State, dependencies, and integration: reads pod status/logs only. It depends on deployment labels and the current kubectl namespace/context.

Risks and test signals: no timeout and no explicit namespace can make it hang or target the wrong context. It provides operational debug signal but is not an automated test.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/plugin-deploy.sh -->
# sources/control-plane/ceph-csi/examples/cephfs/plugin-deploy.sh

Purpose: simple deployment script for CephFS CSI Kubernetes manifests.

Important APIs and flow: accepts an optional deployment base path, defaults to `../../deploy/cephfs/kubernetes`, changes into that directory, and runs `kubectl create -f` for RBAC, config map, provisioner, nodeplugin, and CSIDriver objects.

State, dependencies, and integration: creates cluster and namespace resources from the deploy manifests. Used for examples and local e2e-style deployment.

Risks and test signals: fails if the directory is wrong or resources already exist. It relies on current kubectl context and lacks rollback. Successful completion means all manifests were accepted, not necessarily that pods are ready.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/plugin-deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/plugin-teardown.sh -->
# sources/control-plane/ceph-csi/examples/cephfs/plugin-teardown.sh

Purpose: simple teardown script for CephFS CSI Kubernetes manifests.

Important APIs and flow: accepts an optional deployment base path, defaults to `../../deploy/cephfs/kubernetes`, changes there, and deletes provisioner, nodeplugin, config map, RBAC, and CSIDriver manifests in an order that removes workloads before shared support objects.

State, dependencies, and integration: deletes resources created by `plugin-deploy.sh` from the current kubectl context.

Risks and test signals: no `--ignore-not-found`, so missing resources can fail the script. It does not wait for pod termination or check final cluster state.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/plugin-teardown.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-clone.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pod-clone.yaml

Purpose: example pod that consumes a CephFS PVC clone.

Important fields and flow: Pod `csi-cephfs-clone-demo-app` runs nginx and mounts PVC `cephfs-pvc-clone` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc-clone.yaml` creating a bound clone. E2E clone tests load this template and adjust names/labels.

Risks and test signals: clone PVC must exist and be publishable. Pod readiness and file checksum checks validate clone data access.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-ephemeral.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pod-ephemeral.yaml

Purpose: example pod using Kubernetes generic ephemeral volumes backed by the CephFS StorageClass.

Important fields and flow: Pod `csi-cephfs-demo-ephemeral-pod` defines an inline `ephemeral.volumeClaimTemplate` requesting `1Gi` from `csi-cephfs-sc` and mounts it at `/myspace`.

State, dependencies, and integration: the kubelet/controller creates a temporary PVC for the pod lifetime. It depends on generic ephemeral volume support and the CephFS StorageClass.

Risks and test signals: storage is deleted with the pod, so this is not for persistence. Success validates dynamic provisioning through ephemeral PVC templates.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-restore.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pod-restore.yaml

Purpose: example pod consuming a CephFS PVC restored from a snapshot.

Important fields and flow: Pod `csi-cephfs-restore-demo-pod` runs nginx and mounts PVC `cephfs-pvc-restore` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc-restore.yaml` and snapshot support. E2E restore and upgrade tests use it for checksum validation.

Risks and test signals: restore PVC must be bound before pod readiness. Successful file reads indicate snapshot restore data is usable.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-rwop.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pod-rwop.yaml

Purpose: example pod consuming a CephFS `ReadWriteOncePod` PVC.

Important fields and flow: Pod `csi-cephfs-demo-rwop-pod` mounts PVC `csi-cephfs-rwop-pvc` at `/var/lib/www`.

State, dependencies, and integration: works with `pvc-rwop.yaml` and tests Kubernetes RWOP access-mode behavior for CephFS.

Risks and test signals: RWOP requires sufficient Kubernetes feature support; helper `rwopMayFail` handles older clusters. Pod startup signals exclusive pod-level write access works.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pod.yaml

Purpose: baseline CephFS example pod.

Important fields and flow: Pod `csi-cephfs-demo-pod` runs nginx and mounts PVC `csi-cephfs-pvc` at `/var/lib/www`.

State, dependencies, and integration: depends on `pvc.yaml` and `storageclass.yaml`. Many e2e helpers load and mutate this pod template for create, persistence, resize, snapshot, and upgrade tests.

Risks and test signals: uses external nginx image and assumes PVC name alignment. Pod readiness is the basic signal for CephFS NodeStage/NodePublish success.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-clone.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pvc-clone.yaml

Purpose: example CephFS PVC clone from another PVC.

Important fields and flow: PVC `cephfs-pvc-clone` uses StorageClass `csi-cephfs-sc`, `dataSource` kind `PersistentVolumeClaim` named `csi-cephfs-pvc`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: requests dynamic provisioning of a CephFS clone. E2E clone tests update names and bind it to clone pods.

Risks and test signals: source PVC must exist and support cloning. Binding and checksum preservation validate clone correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-restore.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pvc-restore.yaml

Purpose: example CephFS PVC restored from a `VolumeSnapshot`.

Important fields and flow: PVC `cephfs-pvc-restore` uses StorageClass `csi-cephfs-sc`, snapshot data source `cephfs-pvc-snapshot` in API group `snapshot.storage.k8s.io`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: creates a new CephFS volume from snapshot content. Used by snapshot restore and upgrade tests.

Risks and test signals: snapshot must exist and be ready. Restore size must be at least source size. Binding plus checksum tests validate data restoration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-rwop.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pvc-rwop.yaml

Purpose: example CephFS PVC using `ReadWriteOncePod`.

Important fields and flow: PVC `csi-cephfs-rwop-pvc` requests `1Gi` from `csi-cephfs-sc` with access mode `ReadWriteOncePod`.

State, dependencies, and integration: provisions a CephFS volume with pod-exclusive access semantics. Paired with `pod-rwop.yaml`.

Risks and test signals: unsupported clusters reject the access mode. Successful binding/pod start validates RWOP support through CephFS CSI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/pvc.yaml

Purpose: baseline dynamically provisioned CephFS PVC example.

Important fields and flow: PVC `csi-cephfs-pvc` requests `1Gi`, `ReadWriteMany`, and StorageClass `csi-cephfs-sc`.

State, dependencies, and integration: creates a CephFS subvolume through the provisioner. It is the source object for baseline pod, deployment, clone, snapshot, resize, and data persistence examples.

Risks and test signals: requires valid StorageClass and secrets. Bound status and successful pod mount are the primary signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/secret.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/secret.yaml

Purpose: example Kubernetes Secret for CephFS CSI credentials and optional encryption passphrase.

Important fields and flow: Secret `csi-cephfs-secret` in `default` uses `stringData` for `userID`, `userKey`, and `encryptionPassphrase`.

State, dependencies, and integration: consumed by CephFS StorageClass and SnapshotClass secret references for provisioning, expansion, publish, and snapshots. E2E helpers load this and replace credentials.

Risks and test signals: placeholder credentials are not usable as-is, and plaintext examples must not be reused in production. Successful provisioning verifies the secret matches Ceph auth caps.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/snapshot.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/snapshot.yaml

Purpose: example `VolumeSnapshot` for the baseline CephFS PVC.

Important fields and flow: Snapshot `cephfs-pvc-snapshot` uses class `csi-cephfsplugin-snapclass` and source PVC `csi-cephfs-pvc`.

State, dependencies, and integration: creates snapshot CRD state and backend CephFS snapshot through the CSI snapshotter. Used by restore examples and e2e snapshot helpers.

Risks and test signals: requires snapshot CRDs/controller and ready source PVC. `ReadyToUse` status and restore success validate snapshot behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/snapshotclass.yaml

Purpose: example CephFS `VolumeSnapshotClass`.

Important fields and flow: class `csi-cephfsplugin-snapclass` uses driver `cephfs.csi.ceph.com`, placeholder `clusterID`, optional snapshot name prefix, snapshotter secret refs, and `deletionPolicy: Delete`.

State, dependencies, and integration: cluster-scoped snapshot class consumed by `snapshot.yaml`; e2e code injects cluster ID and secret namespace/name.

Risks and test signals: placeholders must be replaced. Delete policy removes backend snapshots when content is deleted. Creation plus snapshot readiness validate snapshotter configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/storageclass.yaml -->
# sources/control-plane/ceph-csi/examples/cephfs/storageclass.yaml

Purpose: canonical CephFS StorageClass example for dynamic provisioning.

Important fields and flow: StorageClass `csi-cephfs-sc` uses provisioner `cephfs.csi.ceph.com`, placeholder `clusterID` and `fsName`, optional data pool, mount options, mounter, volume name prefix, backing snapshot and encryption settings, KMS ID, secret refs for provisioning/expand/publish/stage, `reclaimPolicy: Delete`, and `allowVolumeExpansion: true`.

State, dependencies, and integration: drives dynamic CephFS subvolume provisioning and expansion. Referenced by all CephFS PVC examples and many e2e helpers that inject real cluster details.

Risks and test signals: invalid cluster/filesystem/secret values prevent provisioning. Optional encryption and KMS settings require matching config. Bound PVCs, expansion success, and pod mounts validate this class.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/cephfs/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/aws-credentials.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/aws-credentials.yaml

Purpose: example Secret for AWS KMS metadata-provider credentials.

Important fields and flow: Secret `ceph-csi-aws-credentials` contains access key, secret key, optional session token, and CMK ARN as `stringData`.

State, dependencies, and integration: consumed by KMS configs referencing AWS metadata providers for encrypted volumes.

Risks and test signals: values are sample credentials and must be replaced. Secret presence plus successful passphrase/key operations validate integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/aws-credentials.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/aws-sts-credentials.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/aws-sts-credentials.yaml

Purpose: example Secret for AWS STS-backed KMS access.

Important fields and flow: Secret `ceph-csi-aws-credentials` contains role ARN, CMK ARN, and AWS region for fetching temporary credentials.

State, dependencies, and integration: used by KMS configurations with `aws-sts-metadata` to obtain KMS access dynamically.

Risks and test signals: placeholder ARNs/region must match an AWS account and trust setup. Successful encrypted volume creation validates STS and KMS wiring.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/aws-sts-credentials.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/azure-credentials.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/azure-credentials.yaml

Purpose: example Secret for Azure Key Vault client certificate material.

Important fields and flow: Secret `ceph-csi-azure-credentials` contains base64 `CLIENT_CERT` under `data`.

State, dependencies, and integration: referenced by Azure KMS provider config entries.

Risks and test signals: empty certificate is a placeholder. Correct certificate, client ID, tenant ID, and vault URL are required for encrypted volume key operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/azure-credentials.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/csi-kms-connection-details.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/csi-kms-connection-details.yaml

Purpose: alternative ConfigMap format for Ceph-CSI encryption KMS provider definitions when the mounted `ceph-csi-encryption-kms-config` file is absent.

Important fields and flow: ConfigMap `csi-kms-connection-details` stores one JSON blob per KMS ID key. Entries cover Vault Kubernetes auth, Vault token tenants, Vault tenant service accounts, metadata secrets, AWS metadata, IBM Key Protect, AWS STS metadata, KMIP, and Azure Key Vault. StorageClasses reference these keys through `encryptionKMSID`.

State, dependencies, and integration: read by Ceph-CSI RBD/CephFS encryption code to choose and configure passphrase storage. It integrates with companion Secrets and tenant objects in the same directory.

Risks and test signals: many values are placeholders or point at in-cluster dev Vault. Incorrect provider key names break StorageClass references. Successful encrypted volume lifecycle and key deletion checks validate the selected entry.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/csi-kms-connection-details.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/csi-vaulttokenreview-rbac.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/csi-vaulttokenreview-rbac.yaml

Purpose: RBAC setup that permits Vault Kubernetes auth token review for Ceph-CSI KMS tests.

Important fields and flow: creates ServiceAccount `rbd-csi-vault-token-review`, ClusterRole permitting `authentication.k8s.io` `tokenreviews` create/get/list, and ClusterRoleBinding binding that role to the service account in `default`.

State, dependencies, and integration: cluster-scoped RBAC and a service account used by Vault init and tenant setup jobs so Vault can validate Kubernetes service account tokens.

Risks and test signals: namespace is hard-coded to `default`, so non-default deployments need adjustment. Excess verbs are broader than minimal token review create. Successful Vault auth setup validates the RBAC.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/csi-vaulttokenreview-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kmip-credentials.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/kmip-credentials.yaml

Purpose: example Secret for KMIP KMS integration.

Important fields and flow: Secret `ceph-csi-kmip-credentials` provides `CA_CERT`, `CLIENT_CERT`, `CLIENT_KEY`, and `UNIQUE_IDENTIFIER` as `stringData`.

State, dependencies, and integration: referenced by KMIP provider config in KMS ConfigMaps.

Risks and test signals: empty values are placeholders. TLS material and KMIP endpoint must match. Successful encrypted PVC operations validate KMIP connectivity.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kmip-credentials.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kms-config.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/kms-config.yaml

Purpose: primary Ceph-CSI encryption KMS ConfigMap with `config.json` containing multiple provider definitions.

Important fields and flow: ConfigMap `ceph-csi-encryption-kms-config` maps KMS IDs to JSON objects for Vault, Vault tokens, Vault tenant service accounts, Vault namespaces, metadata secrets, IBM Key Protect, AWS STS, KMIP, and Azure. Entries include backend paths, tenant config/token/SA names, destroy-key flags, TLS verification, secret names, service IDs, and provider-specific endpoint fields.

State, dependencies, and integration: mounted/read by Ceph-CSI encryption code. StorageClasses reference keys such as `vault-test`, `vault-tokens-test`, `vault-tenant-sa-test`, or provider-specific IDs through `encryptionKMSID`.

Risks and test signals: JSON syntax and provider field names are critical; a bad entry can disable encryption setup. Many endpoints and IDs are examples. E2E encryption tests validate passphrase creation, retrieval, and deletion through these configs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kms-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kp-credentials.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/kp-credentials.yaml

Purpose: example Secret for IBM Key Protect credentials.

Important fields and flow: Secret `ceph-csi-kp-credentials` contains API key, customer root key ID, optional session token, and CRK ARN.

State, dependencies, and integration: referenced by IBM Key Protect KMS configuration entries.

Risks and test signals: sample values must be replaced. Valid credentials and service instance settings are required for encryption key lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/kp-credentials.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-config.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/tenant-config.yaml

Purpose: tenant-side ConfigMap for overriding Vault connection settings.

Important fields and flow: ConfigMap `ceph-csi-kms-config` contains `vaultAddress`, `vaultBackend`, `vaultBackendPath`, TLS server name, and CA verification flag.

State, dependencies, and integration: created in a tenant namespace for Vault token or tenant-service-account KMS modes, allowing per-tenant backend selection.

Risks and test signals: must live in the namespace expected by the KMS config and match tenant credentials. Successful encrypted PVC creation in that namespace validates it.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa-admin.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa-admin.yaml

Purpose: administrator example for preparing Vault access for a tenant service account.

Important fields and flow: ConfigMap `vault-tenant-sa-script` contains `add-tenant-sa.sh`, which logs into Vault, enables a tenant KV store, writes a tenant policy, and configures a Vault Kubernetes auth role bound to `ceph-csi-vault-sa` in namespace `tenant`. Job `vault-tenant-sa` runs that script using service account `rbd-csi-vault-token-review`.

State, dependencies, and integration: creates ConfigMap and Job in `default`, mutates Vault policy/auth/secret-engine state, and enables tenant KMS mode used with `tenant-sa.yaml`.

Risks and test signals: intended for examples/testing; it uses a root token and `vault:latest`, and assumes Vault is reachable at `vault.default.svc`. Successful job completion indicates tenant Vault role setup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa-admin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa.yaml

Purpose: tenant namespace resources for Vault tenant service-account KMS mode.

Important fields and flow: creates ServiceAccount `ceph-csi-vault-sa` and ConfigMap `ceph-csi-kms-config` with tenant Vault backend, path, and role values.

State, dependencies, and integration: tenant workloads use this service account/config so Ceph-CSI can authenticate to Vault as the tenant.

Risks and test signals: must be created in the tenant namespace and aligned with admin-created Vault role/policy. Encrypted volume provisioning validates the tenant-specific path.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-sa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-token.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/tenant-token.yaml

Purpose: tenant Secret containing a Vault token for `vaulttokens` KMS mode.

Important fields and flow: Secret `ceph-csi-kms-token` stores `token: sample_root_token_id`.

State, dependencies, and integration: read by Ceph-CSI when the selected KMS config uses tenant token authentication.

Risks and test signals: sample root token is for dev/test only. The secret must exist in the tenant namespace and be scoped appropriately for production.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/tenant-token.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/user-secret.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/user-secret.yaml

Purpose: user-provided metadata KMS Secret containing an encryption passphrase.

Important fields and flow: Secret `storage-encryption-secret` includes `encryptionPassphrase: test-encryption`.

State, dependencies, and integration: used by metadata KMS modes that reference a user secret by name and optional namespace.

Risks and test signals: static passphrases are sensitive and should be rotated/secured outside examples. Successful encrypted PVC creation validates secret lookup and passphrase use.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/user-secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/vault.yaml -->
# sources/control-plane/ceph-csi/examples/kms/vault/vault.yaml

Purpose: complete in-cluster HashiCorp Vault dev deployment for Ceph-CSI KMS e2e testing.

Important fields and flow: creates headless Service `vault`, Deployment `vault` with a dev Vault server and monitor sidecar, ConfigMap `init-scripts` containing `init-vault.sh`, and Job `vault-init-job`. The init script waits for Vault, logs in with `VAULT_DEV_ROOT_TOKEN_ID`, enables Kubernetes auth under the cluster identifier, writes token reviewer config, writes a policy for `secret/data/ceph-csi/*` and metadata, creates a role bound to Ceph-CSI service accounts, and disables issuer validation.

State, dependencies, and integration: creates Kubernetes service/deployment/config/job resources and mutates Vault auth, policy, and secret engine configuration. It integrates with token-review RBAC and KMS configs that point to `http://vault.default.svc.cluster.local:8200`.

Risks and test signals: dev Vault, root token, old fixed image version, disabled issuer validation, and default namespace assumptions make this non-production. Job success and encrypted volume passphrase operations are the primary signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/kms/vault/vault.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-clone.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pod-clone.yaml

Purpose: example pod that consumes an NFS PVC clone.

Important fields and flow: Pod `csi-nfs-clone-demo-app` runs nginx and mounts PVC `nfs-pvc-clone` at `/var/lib/www`.

State, dependencies, and integration: depends on clone PVC creation from `pvc-clone.yaml`. Used by e2e clone flows for NFS.

Risks and test signals: clone PVC must bind and export must be mountable. Pod readiness and checksum checks validate clone access.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-restore.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pod-restore.yaml

Purpose: example pod for an NFS PVC restored from snapshot.

Important fields and flow: Pod `csi-nfs-restore-demo-pod` mounts PVC `nfs-pvc-restore` at `/var/lib/www`.

State, dependencies, and integration: pairs with `pvc-restore.yaml` and NFS snapshot support.

Risks and test signals: snapshot restore PVC must be ready. Successful pod access validates restored export mount.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-rwop.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pod-rwop.yaml

Purpose: example pod consuming an NFS `ReadWriteOncePod` PVC.

Important fields and flow: Pod `csi-nfs-demo-rwop-pod` mounts PVC `csi-nfs-rwop-pvc` at `/var/lib/www`.

State, dependencies, and integration: paired with `pvc-rwop.yaml` for access mode tests.

Risks and test signals: RWOP support depends on Kubernetes version/features. Pod readiness validates exclusive pod-level use through NFS CSI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pod.yaml

Purpose: baseline NFS CSI example pod.

Important fields and flow: Pod `cephcsi-nfs-demo-pod` runs nginx and mounts PVC `cephcsi-nfs-pvc` at `/var/lib/www`.

State, dependencies, and integration: depends on `pvc.yaml`, `storageclass.yaml`, and a reachable Ceph-managed NFS server/export.

Risks and test signals: external nginx image and export availability affect startup. Pod readiness is the primary NodePublish signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-clone.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pvc-clone.yaml

Purpose: example NFS PVC clone from another PVC.

Important fields and flow: PVC `nfs-pvc-clone` uses StorageClass `csi-nfs-sc`, source PVC `csi-nfs-pvc`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: requests a new NFS export backed by cloned CephFS data.

Risks and test signals: source PVC name in this file differs from baseline `cephcsi-nfs-pvc`, so examples or tests may need name adjustment. Binding and data checks validate clone behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-restore.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pvc-restore.yaml

Purpose: example NFS PVC restored from snapshot.

Important fields and flow: PVC `nfs-pvc-restore` uses StorageClass `csi-nfs-sc`, snapshot data source `nfs-pvc-snapshot`, `ReadWriteMany`, and `1Gi`.

State, dependencies, and integration: provisions an NFS export backed by restored snapshot data.

Risks and test signals: snapshot must exist and the restored PVC must satisfy source size. Pod access validates restore.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-rwop.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pvc-rwop.yaml

Purpose: example NFS PVC using `ReadWriteOncePod`.

Important fields and flow: PVC `csi-nfs-rwop-pvc` requests `1Gi` from `csi-nfs-sc` with access mode `ReadWriteOncePod`.

State, dependencies, and integration: used with `pod-rwop.yaml` to validate RWOP behavior.

Risks and test signals: unsupported clusters reject RWOP. Successful bind/mount validates NFS CSI handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/pvc.yaml

Purpose: baseline dynamically provisioned NFS CSI PVC.

Important fields and flow: PVC `cephcsi-nfs-pvc` requests `1Gi`, `ReadWriteMany`, and StorageClass `csi-nfs-sc`.

State, dependencies, and integration: creates a Ceph-backed NFS export via the NFS CSI provisioner.

Risks and test signals: requires valid NFS StorageClass, CephFS backing config, and NFS server. Bound PVC and pod mount validate provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/rook-nfs.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/rook-nfs.yaml

Purpose: example Rook `CephNFS` custom resource for deploying a Ceph-managed NFS server.

Important fields and flow: creates `CephNFS` `my-nfs`, configures RADOS pool `.nfs`, namespace `my-nfs`, and one active NFS server.

State, dependencies, and integration: consumed by Rook to create NFS-Ganesha resources used by the NFS CSI StorageClass `nfsCluster` and `server` parameters.

Risks and test signals: requires Rook Ceph CRDs/operator and version-specific RADOS behavior. A ready NFS server and export creation validate it.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/rook-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/snapshot.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/snapshot.yaml

Purpose: example NFS `VolumeSnapshot`.

Important fields and flow: Snapshot `nfs-pvc-snapshot` uses class `csi-nfsplugin-snapclass` and source PVC `csi-nfs-pvc`.

State, dependencies, and integration: requests a snapshot of the backing CephFS subvolume/export through NFS CSI.

Risks and test signals: source PVC name differs from baseline `cephcsi-nfs-pvc`, requiring adjustment in some flows. Ready status and restore success validate snapshotting.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/snapshotclass.yaml

Purpose: example NFS `VolumeSnapshotClass`.

Important fields and flow: class `csi-nfsplugin-snapclass` uses driver `nfs.csi.ceph.com`, placeholder `clusterID`, optional snapshot name prefix, CephFS secret refs, and `deletionPolicy: Delete`.

State, dependencies, and integration: configures NFS CSI snapshotter to snapshot the CephFS-backed export.

Risks and test signals: placeholders and secret refs must match deployment. Successful snapshot creation validates the class.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/storageclass.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/storageclass.yaml

Purpose: canonical NFS CSI StorageClass example backed by CephFS and a Ceph-managed NFS server.

Important fields and flow: StorageClass `csi-nfs-sc` uses provisioner `nfs.csi.ceph.com`, required `nfsCluster`, `server`, `clusterID`, and `fsName`, optional pool, secret refs for provision/expand/publish/modify, volume prefix `nfs-export-`, optional security types and client restrictions, `reclaimPolicy: Delete`, and expansion enabled.

State, dependencies, and integration: provisions CephFS subvolumes and NFS exports. It integrates with Rook CephNFS, CephFS secrets, and VolumeAttributesClass modification.

Risks and test signals: NFS server endpoint, CephFS config, and secrets must be valid. Export validation helpers inspect resulting Ceph NFS exports and client restrictions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/volumeattributesclass.yaml -->
# sources/control-plane/ceph-csi/examples/nfs/volumeattributesclass.yaml

Purpose: example `VolumeAttributesClass` for changing NFS volume parameters.

Important fields and flow: VAC `updated-parameters` uses driver `nfs.csi.ceph.com` and sets `server` to an alternative NFS endpoint.

State, dependencies, and integration: Kubernetes applies this to PVCs that reference the class, and Ceph-CSI uses controller/node modify secret refs from the StorageClass to update attachment behavior.

Risks and test signals: requires Kubernetes VAC support and a valid replacement server. Tests validate updated publish behavior after reattachment.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nfs/volumeattributesclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pod.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/pod.yaml

Purpose: baseline NVMe-oF filesystem PVC consumer pod.

Important fields and flow: Pod `csi-nvmeof-demo-pod` runs nginx and mounts PVC `nvmeof-pvc` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc.yaml` and the NVMe-oF StorageClass/gateway configuration.

Risks and test signals: pod readiness validates attach, NVMe connection, filesystem mount, and publish path.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pvc-restore.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/pvc-restore.yaml

Purpose: example NVMe-oF PVC restored from a snapshot.

Important fields and flow: PVC `nvme-pvc-restore` uses StorageClass `csi-nvmeof-sc`, snapshot data source `nvme-pvc-snapshot`, `ReadWriteOnce`, and `1Gi`.

State, dependencies, and integration: provisions a new NVMe-oF volume backed by an RBD snapshot restore.

Risks and test signals: restored size must be compatible with source snapshot and gateway config must be valid. Binding/pod access validate restore.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pvc.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/pvc.yaml

Purpose: baseline NVMe-oF filesystem PVC example.

Important fields and flow: PVC `nvmeof-pvc` requests `64Mi`, `ReadWriteOnce`, and StorageClass `csi-nvmeof-sc`.

State, dependencies, and integration: creates an RBD-backed NVMe-oF volume through the NVMe-oF CSI provisioner.

Risks and test signals: small size is suitable for examples but may not match all filesystem requirements. Bound status and pod mount validate provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pod.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pod.yaml

Purpose: example pod consuming an NVMe-oF raw block PVC.

Important fields and flow: Pod `pod-with-raw-block-volume` runs CentOS sleep and maps PVC `raw-block-pvc` to `/dev/xvda` through `volumeDevices`.

State, dependencies, and integration: paired with `raw-block-pvc.yaml` to validate block-mode NVMe-oF publishing.

Risks and test signals: block PVC must exist and attach successfully. Device visibility in the container is the primary signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pvc.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pvc.yaml

Purpose: example NVMe-oF raw block PVC.

Important fields and flow: PVC `raw-block-pvc` requests `1Gi`, `ReadWriteOnce`, `volumeMode: Block`, and StorageClass `csi-nvmeof-sc`.

State, dependencies, and integration: provisions a block volume for direct device publishing through NVMe-oF.

Risks and test signals: consumers must use `volumeDevices`, not filesystem mounts. Successful pod device access validates raw block support.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/snapshot.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/snapshot.yaml

Purpose: example NVMe-oF `VolumeSnapshot`.

Important fields and flow: Snapshot `nvme-pvc-snapshot` uses class `csi-nvmeplugin-snapclass` and source PVC `nvmeof-pvc`.

State, dependencies, and integration: creates an RBD snapshot for the NVMe-oF-backed volume through the CSI snapshotter.

Risks and test signals: requires snapshot class, secrets, and a ready source PVC. Restore success validates snapshot data.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/snapshotclass.yaml

Purpose: example NVMe-oF `VolumeSnapshotClass`.

Important fields and flow: class `csi-nvmeplugin-snapclass` uses driver `nvmeof.csi.ceph.com`, `deletionPolicy: Delete`, placeholder `clusterID`, optional snapshot name prefix, and snapshotter list/secret refs to `csi-nvme-secret`.

State, dependencies, and integration: configures snapshotting for NVMe-oF volumes, which are backed by RBD images.

Risks and test signals: placeholders and secret names must align with deployment. Snapshot readiness validates controller-side configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/storageclass.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/storageclass.yaml

Purpose: canonical NVMe-oF StorageClass example for Ceph-CSI.

Important fields and flow: StorageClass `csi-nvmeof-sc` enables expansion, uses `Immediate` binding, provisioner `nvmeof.csi.ceph.com`, secret refs for expand/stage/publish/provision, RBD parameters (`clusterID`, `fstype`, `imageFeatures`, `pool`), subsystem NQN, gateway management address/port, and JSON listener definitions for NVMe data path.

State, dependencies, and integration: provisions RBD images and exposes them through an NVMe-oF gateway/subsystem. PVC and snapshot examples depend on this configuration.

Risks and test signals: gateway IP, listener JSON, pool, NQN, and secrets must match the environment. Successful PVC binding and pod mount/device access validate gateway and CSI integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-default.yaml -->
# sources/control-plane/ceph-csi/examples/nvmeof/vac-default.yaml

Purpose: example NVMe-oF `VolumeAttributesClass` providing default QoS-like parameters.

Important fields and flow: VAC `default` uses driver `nvmeof.csi.ceph.com` and sets `rwIosPerSecond: "5000"`.

State, dependencies, and integration: applied to PVCs through Kubernetes VAC support to modify NVMe-oF volume attributes.

Risks and test signals: requires Kubernetes VAC API support and driver-side parameter handling. Reattachment or modification tests should confirm the I/O parameter is honored.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-default.yaml -->
