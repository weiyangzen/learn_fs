# subset-b-000466 Research

Grouped research for Rook Ceph integration test files. Each section preserves the source path and is intended to be split into the mapped source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_block_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_block_test.go

## Purpose
Shared block-storage integration helpers for Rook Ceph test suites. The file exercises CSI RBD provisioning, PVC binding, pod mount/read/write behavior, PVC clone and snapshot/restore flows, reclaim policy behavior, PV cleanup, OSD restart survival, and a lighter block path used by Helm and upgrade tests.

## Important APIs, Types, And Functions
The exported surface is package-level helper functions rather than Go exported APIs. `runBlockCSITest` is the full smoke path. It creates `replicapool` and `replicapoolretained`, two storage classes with `Delete` and `Retain`, two PVCs, pods mounted with RBD-backed volumes, data writes/reads, OSD pod restart validation, reclaim-policy validation, pool deletion, and storage-class deletion. `runBlockCSITestLite` creates a pool/storage class/PVC and then calls snapshot and clone tests.

`blockCSICloneTest` provisions a parent PVC, writes a deterministic file with `dd` and `md5sum`, creates a clone PVC, mounts it in another pod, compares checksums, and deletes pods/PVCs/PVs. `blockCSISnapshotTest` installs snapshot CRDs/controller, creates a `VolumeSnapshotClass`, snapshots a PVC, restores it to a second PVC, validates checksum preservation, then removes restore PVC, snapshot, parent PVC, snapshot class, and snapshot infrastructure. `setupBlockLite`, `createAndWaitForPVC`, `deleteBlockLite`, `deletePVC`, `blockTestDataCleanUp`, `retryBlockImageCountCheck`, `retryPVCheck`, and `getCSIBlockPodDefinition` implement the common creation, cleanup, polling, and test pod YAML.

## Control Flow
The full test path starts by asserting the Ceph pool has no images, creates pool/storage class/PVC pairs, waits for two RBD images, mounts pods, writes and reads data through `K8sHelper`, restarts all OSD pods by label, reads again, attempts a second pod mount for a ReadWriteOnce PVC, deletes pods, deletes PVCs, validates PV state based on reclaim policy, and finally deletes pools and storage classes. Lite setup creates one RBD image, then separately runs snapshot and clone flows.

## State And Persistence Behavior
The file mutates Kubernetes `PersistentVolumeClaim`, `PersistentVolume`, `Pod`, `StorageClass`, snapshot CRD/controller resources, `VolumeSnapshot` resources, CephBlockPool CRs, and backend RBD images. Persistence is validated by checksum equality across clone/restore and by read-after-OSD-restart. Cleanup expects Delete reclaim PVs and RBD images to disappear, while Retain reclaim PVs move to `Released` before explicit PV deletion. Several helpers always use Kubernetes `default` namespace for test consumers, even when the Ceph cluster namespace differs.

## Dependencies And Integration Points
The helpers depend on Rook test framework clients (`BlockClient`, `PoolClient`), `utils.K8sHelper`, `client.AdminTestClusterInfo`, Kubernetes API helpers, Rook `k8sutil.DefaultNamespace`, and testify assertions. They are called by smoke, Helm, and upgrade suites. Snapshot flows depend on external Kubernetes snapshot CRDs and controller installation through `K8sHelper`.

## Risks And Edge Cases
The commented RWO fencing assertion means the full block test no longer proves that simultaneous mounts are rejected. Several resources use fixed names in `default`, so concurrent suites or interrupted cleanup can collide. `retryPVCheck` can dereference `pv` after a get error when `exists` is true, depending on helper behavior. Cleanup defers may run after partial setup and therefore rely on `assertNoErrorUnlessNotFound`. Snapshot CRD/controller install/delete is global to the cluster and can interfere with parallel file snapshot tests.

## Test Signals
Strong signals include PVC bound checks, RBD image count checks, pod running/terminated checks, checksum comparison for clone and restore, PV deletion or release state, OSD restart readiness, pool deletion polling, and snapshot readiness. Missing or weakened signals include disabled RWO fencing validation and a non-failing pool-deletion check that logs instead of asserting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_deploy_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_deploy_test.go

## Purpose
Common deployment bootstrap and health helpers for all Rook Ceph integration suites. It centralizes cluster installation, pod-count validation, health polling, dashboard ingress validation, panic cleanup, and package-level logging.

## Important APIs, Types, And Functions
`defaultNamespace` is the shared `"default"` Kubernetes namespace constant used by many helpers. `logger` is the package logger. `checkIfRookClusterIsInstalled` validates expected operator, mgr, osd, mon, and crashcollector pods. `checkIfRookClusterIsHealthy` polls `clients.IsClusterHealthy`. `checkIfRookClusterHasHealthyIngress` checks the dashboard ingress resource. `HandlePanics` fails the test, invokes a provided uninstaller, and calls `FailNow` when a suite panics. `StartTestCluster` creates a `K8sHelper`, injects Kubernetes version into settings, sets global DEBUG logging, builds a `CephInstaller`, installs Rook, gathers logs on failure, uninstalls failed installs, and returns installer/helper handles.

## Control Flow
Suites call `StartTestCluster` from `SetupSuite`. Failure during install triggers log gathering, test failure, uninstall, and `FailNow`. Suite `Test...` functions defer `HandlePanics(recover(), TearDownSuite, T)` so unexpected panics still drive teardown. Health checks are explicit test steps that retry or assert current resource state.

## State And Persistence Behavior
This file does not define persistent application state itself, but `StartTestCluster` creates a full Rook/Ceph cluster and updates `settings.KubernetesVersion`. It also sets the global capnslog level. `HandlePanics` can uninstall live cluster resources through the injected uninstaller.

## Dependencies And Integration Points
It binds together `utils.CreateK8sHelper`, `installer.NewCephInstaller`, `InstallRook`, `UninstallRook`, `GatherAllRookLogs`, `clients.IsClusterHealthy`, and testify suite assertions. Almost every file in this work item depends on these helpers.

## Risks And Edge Cases
Pod count checks assume exact labels and expected replica counts, which can lag during rolling updates or multi-manager configurations. `checkIfRookClusterIsHealthy` requires the final `err` to be nil after retries, so repeated unhealthy false results with nil errors can produce weaker diagnostics. `StartTestCluster` mutates shared settings and global logging, which can surprise parallel tests.

## Test Signals
The key signals are Kubernetes pod counts/states, Ceph health from the test client, ingress resource status, install return values, and collected logs on install failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_deploy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_file_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_file_test.go

## Purpose
Shared CephFS integration helpers for Rook tests. The file verifies filesystem creation, CSI PVC provisioning, pod mount/read/write, filesystem deletion blocking by subvolume groups and CSI subvolumes, snapshot/restore, clone, and cleanup.

## Important APIs, Types, And Functions
`filePodName` is the canonical CephFS consumer pod/PVC name. `runFileE2ETest` is the full smoke path. It creates a CephFilesystem with active MDS count 2, optionally patches `preserveFilesystemOnDelete`, creates a CephFS storage class, mounts a consumer pod, writes/reads data, creates a `CephFilesystemSubVolumeGroup`, verifies filesystem deletion is blocked by subvolume-group and CSI dependents, deletes the subvolume group, verifies the condition narrows, deletes the consumer pod/PVC, waits for filesystem deletion, and handles preserve-on-delete follow-up.

`runFileE2ETestLite` creates a smaller filesystem and storage class, then runs snapshot and clone helpers. `fileSystemCSISnapshotTest` installs snapshot infrastructure, creates a snapshot class through either FS or NFS client, snapshots/restores a PVC, compares checksums, and tears down all resources. `fileSystemCSICloneTest` creates a parent PVC and clone PVC and compares checksums. `createFilesystem`, `createFilesystemConsumerPod`, `createPodWithFilesystem`, `getFilesystemCSITestPod`, `cleanupFilesystemConsumer`, `cleanupFilesystem`, `fileTestDataCleanUp`, `writeAndReadToFilesystem`, and `waitForFilesystemActive` provide the lower-level mechanics.

## Control Flow
Full E2E flow creates CephFilesystem, creates storage class and pod/PVC, validates file I/O, creates a subvolume group, sends a delete request for the filesystem while dependents exist, polls status conditions for `ConditionDeletionIsBlocked`, removes the explicit subvolume group, verifies only CSI subvolumes remain as blockers, deletes the consumer, and waits until the filesystem disappears. Lite flow focuses on creation plus CSI snapshot and clone semantics.

## State And Persistence Behavior
The file creates CephFilesystem CRs, CephFilesystemSubVolumeGroup CRs, Kubernetes StorageClasses, PVCs, PVs, Pods, snapshot CRDs/controller, snapshot classes, snapshots, and restored/cloned PVCs. Data persistence is tested with md5 checksum equality and read-after-write. Cleanup expects PV count to return to zero after consumer cleanup. Preserve-on-delete intentionally leaves the filesystem around after deletion request and then deletes it directly.

## Dependencies And Integration Points
It depends on Rook Ceph API types, Ceph client command helpers, `FSClient`, `NFSClient`, `K8sHelper`, shared block helpers `retryPVCheck` and `assertNoErrorUnlessNotFound`, Kubernetes wait polling, and testify. It is called by smoke, NFS, Helm, and upgrade tests.

## Risks And Edge Cases
Snapshot controller/CRDs are cluster-global and installed/deleted inside helper flows, so parallel block/file/NFS snapshot tests can race. `mountUser` is accepted by `createPodWithFilesystem` but unused. The disabled MDS scale-down block documents a known regression and leaves MDS downscale uncovered. Fixed pod/PVC names and `defaultNamespace` use can collide with parallel test runs. `fileTestDataCleanUp` asserts delete success, so failed partial setup may cause noisy cleanup failures.

## Test Signals
Signals include filesystem list count, PVC bound/deleted checks, pod running/terminated checks, file read/write checks, snapshot readiness, clone/restore checksum equality, PV deletion and zero-PV waits, filesystem deletion-blocked condition status/reason/message, and active MDS status via `ceph fs status`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_keystone_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_keystone_test.go

## Purpose
Keystone, Swift, and S3 authentication integration support for Rook RGW tests. The file installs an in-cluster Keystone stack with TLS, creates OpenStack CLI clients, configures RGW Swift endpoints, and validates authorized and unauthorized object workflows.

## Important APIs, Types, And Functions
`testuserdata` defines admin, RGW admin, member, project admin, and unprivileged users with generated passwords. `InstallKeystoneInTestCluster` installs cert-manager and trust-manager via Helm, creates issuers/certificates/bundles, configures Keystone Apache and Keystone secrets, deploys Keystone, waits for readiness, creates its service, and starts one OpenStack client deployment per user. `initializePasswords` fills the global user password map using `sethvargo/go-password`.

Manifest functions generate YAML strings for OpenStack clients, trust-manager bundle, cert-manager issuers/certificates, Keystone service, Keystone deployment, Keystone config, and Apache config. `CleanUpKeystoneInTestCluster` deletes the Keystone configmap, secret, and deployment. `runSwiftE2ETest` exercises OpenStack Swift container/object operations with member, admin, and unprivileged users. `runS3E2ETest` creates EC2 credentials through OpenStack and validates AWS CLI S3 access to RGW. `prepareE2ETest`, `cleanupE2ETest`, `testInOpenStackClient`, and `rgwServiceUri` provide shared setup, teardown, command execution, and endpoint construction.

## Control Flow
Keystone installation first initializes passwords, installs Helm dependencies, applies certificate resources, creates config and secret resources, deploys Keystone, waits for pod readiness, creates service, and deploys client pods. Swift/S3 tests create a Keystone project/users/roles, create a CephObjectStore with Swift/Keystone enabled, register Swift service endpoints, run object workflows from specific OpenStack client deployments, verify failures for the no-role user, and then delete endpoints, service, users, project, and optionally the object store.

## State And Persistence Behavior
The file persists cluster-wide Helm releases, CRDs, cert-manager resources, trust-manager bundles, TLS secrets, ConfigMaps, Keystone SQLite data on an `emptyDir`, OpenStack client deployments, Keystone users/projects/roles/services/endpoints, CephObjectStore resources, Swift containers, and S3 objects. Passwords are stored in a package global map for the duration of the process and injected into deployment environment variables.

## Dependencies And Integration Points
It depends on Helm, external chart repositories `jetstack`, images from `registry.yaook.cloud` and `nixery.dev`, cert-manager/trust-manager APIs, Rook object-store helpers, OpenStack CLI, AWS CLI, jq, Kubernetes API clients, and shared object helpers from `ceph_base_object_test.go`.

## Risks And Edge Cases
This test has a large external supply-chain and network footprint: Helm repos, images, and CRDs must be reachable and compatible. Generated passwords are placed in pod environment variables and YAML strings, acceptable for tests but not a production pattern. `CleanUpKeystoneInTestCluster` intentionally leaves cert-manager resources for later uninstall. `testInOpenStackClient` always waits for the admin client label before running any user command, which may miss readiness issues in the target client deployment. Several shell commands are composed as strings and depend on CLI output formats.

## Test Signals
Signals include Helm install success, Keystone pod readiness, OpenStack command success/failure, object upload/download/diff success, negative authorization failures for Mallory, successful admin access for Carol, endpoint/service cleanup, AWS S3 list/copy/remove success, and object-store deletion checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_keystone_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_nfs_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_nfs_test.go

## Purpose
CephNFS integration helper that layers NFS and optional NFS CSI validation on top of the shared CephFS helpers.

## Important APIs, Types, And Functions
`runNFSFileE2ETest` creates a CephFilesystem, creates a CephNFS cluster named `my-nfs`, and, when `settings.TestNFSCSI` is true, creates an NFS CSI storage class, mounts a filesystem consumer pod, performs read/write validation, deletes the consumer, and runs filesystem snapshot and clone flows against the NFS storage class.

## Control Flow
The function defers generic file cleanup, creates the backing filesystem with one active MDS, creates the NFS cluster, conditionally creates and exercises the NFS CSI storage class and consumer, runs snapshot and clone checks, deletes the NFS cluster, and deletes the filesystem.

## State And Persistence Behavior
It creates a CephFilesystem, CephNFS CR, NFS CSI StorageClass, PVC/PV/Pod resources, snapshot infrastructure, snapshots, restored PVCs, cloned PVCs, and file contents used for read/write/checksum validation. Cleanup cascades through shared file helpers.

## Dependencies And Integration Points
Depends on `helper.NFSClient`, `helper.FSClient`, shared `createFilesystem`, `createFilesystemConsumerPod`, `writeAndReadToFilesystem`, `cleanupFilesystemConsumer`, `fileSystemCSISnapshotTest`, `fileSystemCSICloneTest`, and `cleanupFilesystem`. It is invoked by the smoke suite when NFS CSI testing is enabled.

## Risks And Edge Cases
The `assert.NoError(s.T(), err)` after `cleanupFilesystemConsumer` checks the last NFS storage class creation error rather than a cleanup error. Snapshot infrastructure is global and can conflict with block/file snapshot tests. Fixed names (`my-nfs`, `nfs-storageclass`, `file-test`) limit parallelism. If `TestNFSCSI` is false, the function mainly validates CephNFS CR lifecycle and not actual NFS data access.

## Test Signals
Signals include successful CephFilesystem and CephNFS creation/deletion, optional pod running state, file read/write validation, snapshot readiness and checksum equality, clone checksum equality, PVC/PV deletion, and absence of errors from NFS client operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_object_test.go -->
# sources/control-plane/rook/tests/integration/ceph_base_object_test.go

## Purpose
Shared RGW/CephObjectStore helper layer. It creates and deletes object stores, validates RGW deployment/service/status readiness, creates and checks object-store users, and generates test TLS secrets.

## Important APIs, Types, And Functions
Constants and globals define RGW naming, TLS secret name, default object user/bucket/object/quota values, and storage class names. `runObjectE2ETestLite` creates an object store and optionally deletes it. `RgwServiceName` composes RGW service names. `createCephObjectStore` optionally generates TLS certs, creates a `CephObjectStore`, waits for RGW pods and deployments, validates object-store `Ready` or legacy `Connected` phase with endpoint info, checks deployment liveness by unavailable replicas, checks service reachability, and probes dashboard-admin user creation. `deleteObjectStore` and `assertObjectStoreDeletion` drive deletion and verify deletion-unblocked status. `createCephObjectUser` and `checkCephObjectUser` create and validate `CephObjectStoreUser` plus its secret/status. `generateRgwTlsCertSecret` runs the repo TLS script and creates a Kubernetes Secret.

## Control Flow
Object store creation follows TLS setup, CR creation, RGW pod wait, status polling, liveness and service checks, and dashboard-admin user probe. Deletion sends a delete, waits briefly, then either returns if the resource is gone or polls deletion conditions until `ConditionDeletionIsBlocked=False` with `ObjectHasNoDependentsReason`, then waits for resource deletion.

## State And Persistence Behavior
The helpers create CephObjectStore CRs, RGW deployments/services, TLS Secrets, CephObjectStoreUser CRs, user Secrets, dashboard users, RGW realms/zones/pools, and test buckets/users indirectly through callers. Deletion logic explicitly checks object-store status conditions before final absence. TLS materials are generated in a temporary directory and stored as a single `cert` entry in a Kubernetes Secret named after the store.

## Dependencies And Integration Points
Depends on Rook Ceph API types, `ObjectClient`, `ObjectUserClient`, `K8sHelper`, `CephInstaller.Execute`, `k8sutil.ReadyStatus`, Kubernetes API clients, wait polling, and `tests/scripts/generate-tls-config.sh`. Main object, smoke, COSI, bucket notification, Keystone, and upgrade tests reuse this helper layer.

## Risks And Edge Cases
`createCephObjectStore` checks pod count with prefix `rook-ceph-rgw` but later expects `replicaSize`, so multiple stores in a namespace can complicate counts. Dashboard-admin lookup logs errors instead of failing because readiness is not reliable. TLS secret naming uses the store name, while `objectTLSSecretName` is a separate constant used elsewhere. Deletion condition logic assumes status is still readable after delete and may be sensitive to fast deletion. Shared global values like `obcName` and `bucketname` couple object-related tests.

## Test Signals
Signals include CephObjectStore phase/info endpoint, RGW pod count, deployment readiness, service reachability, deletion condition reason/status, final resource absence, user secret presence, RGW user metadata, and object-store-user Kubernetes phase.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_base_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_bucket_notification_test.go -->
# sources/control-plane/rook/tests/integration/ceph_bucket_notification_test.go

## Purpose
End-to-end bucket notification coverage for RGW-backed ObjectBucketClaims. It validates HTTP topic/notification creation, OBC label-driven bucket notification configuration, event delivery for S3 put/delete operations, update ordering, and cleanup.

## Important APIs, Types, And Functions
Constants define the HTTP receiver service, endpoint URL, and RGW event names. `testBucketNotifications` is the single helper entry point. It creates an HTTP server through `TopicClient`, a `CephBucketTopic`, a `CephBucketNotification`, an OBC with a notification label, an S3 client from OBC credentials, and then checks notification receipt through `NotificationClient.CheckNotificationFromHTTPEndPoint`. It also manipulates OBC labels, adds a second notification to an existing OBC, tests reverse OBC/notification/topic creation order, and deletes OBCs/topics/notifications/object store.

## Control Flow
The test skips on OpenShift, builds an RGW multisite/admin context, creates the receiver, topic, notification, storage class, and OBC, waits for the bucket to exist in RGW, performs S3 put/delete and checks positive and negative notification observations, verifies backend notification configuration, mutates labels, adds and removes secondary topics/notifications, validates reverse order reconciliation, deletes reverse and primary OBCs with backend bucket absence checks, then deletes notification, topic, and object store.

## State And Persistence Behavior
Creates an HTTP server deployment/service, CephBucketTopic CRs, CephBucketNotification CRs, ObjectBucketClaims, ObjectBuckets, bucket StorageClasses, RGW bucket notification configuration, S3 objects, and an object store used for the test. Label mutations on OBCs are used as reconciliation inputs. Cleanup deletes OBCs and validates RGW bucket absence with `rgw.GetBucket`.

## Dependencies And Integration Points
Depends on `TopicClient`, `NotificationClient`, `BucketClient`, Rook RGW object package, `client.AdminTestClusterInfo`, `K8sHelper`, shared object constants/helpers, and S3 agent operations. It is invoked from the main object suite against a dedicated object store.

## Risks And Edge Cases
Several intended checks are skipped with `t.Skipped()` inside retry callbacks, so notification removal/non-notification-label invariance is not fully asserted. After a skipped removal test, later "notifications are no longer received" expectations may be difficult to reason about because the removal path itself is skipped. Fixed names and default namespace limit parallelism. The function deletes the object store it was passed, so callers must use a dedicated store.

## Test Signals
Signals include topic/notification CR existence, OBC bound state, RGW bucket existence/absence, S3 put/delete success, HTTP endpoint event presence/absence for put/delete events, backend bucket notification configuration, and cleanup success for OBC/storage class/topic/notification/object store.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_bucket_notification_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_cosi_test.go -->
# sources/control-plane/rook/tests/integration/ceph_cosi_test.go

## Purpose
Container Object Storage Interface integration coverage for Rook's Ceph COSI driver. It installs upstream COSI CRDs/controller, creates a Ceph object store/user, configures the CephCOSIDriver, creates a BucketClass and BucketClaim, verifies backend RGW bucket creation, and cleans everything up.

## Important APIs, Types, And Functions
Constants define object store, user, bucket class, deletion policy, and bucket claim names. `testCOSIDriver` is the single test helper. It drives `kubectl create -k` against upstream COSI API/controller kustomize URLs, `createCephObjectStore`, `helper.COSIClient.CreateCOSI`, driver pod readiness checks, `createCephObjectUser`, bucket class/claim creation, BucketClaim status reads, backend `rgw.GetBucket` checks, and reverse-order deletion.

## Control Flow
The test skips on OpenShift, installs upstream COSI components, creates an RGW store, creates the Rook COSI driver CR, checks driver deployment readiness, creates an object user and BucketClass using the generated user secret, creates a BucketClaim, waits for Bucket and BucketClaim readiness, validates the bucket in RGW via multisite context, deletes claim/class/user/store/driver, and deletes upstream COSI components.

## State And Persistence Behavior
It creates cluster-level COSI CRDs/controllers, a CephObjectStore, CephCOSIDriver CR, COSI driver deployment, CephObjectStoreUser and secret, BucketClass, BucketClaim, Bucket, and backend RGW bucket. Cleanup deletes all of those resources through helper clients and `kubectl delete -k`.

## Dependencies And Integration Points
Depends on upstream `kubernetes-sigs/container-object-storage-interface-*` kustomize manifests, Rook COSI helper client, RGW object helpers, Ceph admin cluster info, Rook API clients, and the shared object store/user helpers. It is invoked from the main object suite only when TLS is disabled.

## Risks And Edge Cases
The driver readiness retry loop is written as `for i := 24; i < 24 && ...`, so it never retries and proceeds directly to assertions. The install/delete assertions for upstream COSI delete paths use failure messages that still say "create". Pulling kustomize manifests from GitHub adds network/version drift. COSI resources are cluster-scoped or operator-namespace-scoped and can collide with parallel tests.

## Test Signals
Signals include successful COSI CRD/controller install, CephCOSIDriver creation/deletion, driver pod/deployment readiness, BucketClass/BucketClaim creation, BucketClaim status `bucketName`, Bucket `bucketReady=true`, RGW backend bucket existence, and successful cleanup calls.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_cosi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_helm_test.go -->
# sources/control-plane/rook/tests/integration/ceph_helm_test.go

## Purpose
Suite-level integration coverage for installing Rook/Ceph via Helm and then validating basic block, file, and object functionality on that Helm-managed cluster.

## Important APIs, Types, And Functions
`TestCephHelmSuite` registers the testify suite and panic handler. `HelmSuite` stores helper, installer, settings, and Kubernetes helper handles. `SetupSuite` creates Helm-specific `TestCephSettings` with one mon, raw-device OSDs, discovery, hostname changes, encrypted connections, Squid Ceph, and CSI operator enabled. Test methods call shared deployment, block-lite, file-lite, and object-lite helpers. `AfterTest` collects operator logs and `TearDownSuite` uninstalls Rook.

## Control Flow
Setup applies env vars, starts the cluster through `StartTestCluster`, and builds a test client. Tests validate install/ingress, then run block storage, file storage, and object store helper flows. Teardown uninstalls the Helm-managed cluster.

## State And Persistence Behavior
The suite creates a namespace `helm-ns`, Helm releases, Rook/Ceph cluster resources, block pools/storage classes/PVCs, CephFilesystem/storage classes/snapshots/clones, and a lite object store. Most persistent state is created and cleaned by shared helpers.

## Dependencies And Integration Points
Depends on `CephInstaller` Helm support, shared deploy/block/file/object helpers, `clients.CreateTestClient`, `utils.K8sHelper`, and testify suite lifecycle. It is also conceptually paired with upgrade Helm coverage in `ceph_upgrade_test.go`.

## Risks And Edge Cases
The tests rely heavily on shared helpers with fixed resource names, so failures can leave resources that affect later methods in the same namespace. Helm chart behavior and CRD lifecycle can differ from manifest installs. Running object/file/block tests in one cluster makes failures cascade when cluster setup is unhealthy.

## Test Signals
Signals include pod counts, dashboard ingress status, block PVC/snapshot/clone signals, CephFS snapshot/clone signals, object store readiness and deletion, operator logs after each test, and final uninstall.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_helm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_mgr_test.go -->
# sources/control-plane/rook/tests/integration/ceph_mgr_test.go

## Purpose
Integration suite for Ceph manager Rook orchestrator commands. It validates `ceph orch` device listing, status, host listing, and service listing against Kubernetes state.

## Important APIs, Types, And Functions
`CephMgrSuite` owns settings/helper/installer state. Structs `host`, `serviceStatus`, and `service` model JSON output from `ceph orch host ls json` and `ceph orch ls --format json`. `SetupSuite` installs a `mgr-ns` cluster with no OSD creation, Main Ceph version, and then waits for/sets the Rook orchestrator module and creates a local storage class. `executeWithRetry` wraps `ceph orch` commands through the installer. `prepareLocalStorageClass` creates a no-provisioner storage class and sets `mgr/rook/storage_class`. `enableOrchestratorModule` enables the Rook mgr module and sets backend. `waitForOrchestrationModule` polls `ceph orch status --format json` and enables the module when needed. Test methods validate device, status, host, and service outputs.

## Control Flow
Setup starts the cluster, waits for orchestrator availability, and configures local storage. Tests execute individual `ceph orch` commands. Host tests sort orchestrator hostnames and Kubernetes node hostnames before comparing. Service tests parse service JSON and compare each service's running count with Kubernetes pods selected by derived labels.

## State And Persistence Behavior
Creates a Ceph cluster in `mgr-ns`, a `local-storage` StorageClass, and sets Ceph mgr config `mgr/rook/storage_class`. It may enable the Rook mgr module and change the active orchestrator backend. Teardown deletes the storage class and uninstalls the cluster.

## Dependencies And Integration Points
Depends on Ceph CLI via toolbox/installer execution, Rook mgr orchestrator module, Kubernetes node and pod APIs through `k8sutil`, JSON output shapes from Ceph, and testify. This suite tests Rook's integration with Ceph's orchestrator abstraction rather than CSI or RGW.

## Risks And Edge Cases
`waitForOrchestrationModule` type-asserts command errors to `*exec.ExitError`; if another error type occurs, calling `ExitCode` on nil can panic. `TestStatus` asserts exact text `"Backend: rook\nAvailable: Yes"`, which is brittle across Ceph output changes. Service label derivation assumes `app=rook-ceph-<serviceName>` except crashcollector. Local storage class config is cluster-global within the mgr.

## Test Signals
Signals include successful `ceph orch` commands, JSON parse success, orchestrator backend `rook`, Kubernetes host equality, service running counts matching pod counts, and storage-class configuration success.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_mgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_multi_cluster_test.go -->
# sources/control-plane/rook/tests/integration/ceph_multi_cluster_test.go

## Purpose
Integration suite validating multiple Rook Ceph clusters: a core cluster and an external cluster connected to it, with health checks from both toolbox contexts.

## Important APIs, Types, And Functions
`MultiClusterDeploySuite` stores the core test client, Kubernetes helper, settings, external manifests, installer, toolbox command names, and a pool name. `SetupSuite` configures a core cluster in `multi-core` with system namespace, PVC settings, multiple managers, msgr2 requirement, and cluster concurrency, then configures an external cluster manifest for `multi-external`. `setupMultiClusterCore` runs `tests/scripts/localPathPV.sh` against the scratch device, starts the core cluster, creates the test client, and stores the core toolbox function. `createPools` and `deletePools` manage a test pool. `startExternalCluster` uses `CreateRookExternalCluster` and stores the external toolbox function. `TestInstallingMultipleRookClusters` switches `client.RunAllCephCommandsInToolboxPod` to each toolbox and validates install/health.

## Control Flow
The suite creates the core cluster, creates a pool to generate PGs, starts the external cluster connected to the core, then tests the core install and health followed by external cluster health. Teardown deletes the pool and uninstalls resources from both namespaces.

## State And Persistence Behavior
Creates local-path PV setup on the host scratch device, Rook core cluster resources, external-cluster resources, a Ceph pool, and modifies the global `client.RunAllCephCommandsInToolboxPod` function to point at different toolbox contexts. Cleanup deletes the pool and uninstalls both namespaces.

## Dependencies And Integration Points
Depends on the local path PV script, `CephInstaller` multi-namespace and external-cluster support, Rook clients, Ceph toolbox command dispatch, `client.AdminTestClusterInfo`, and shared deployment health helpers.

## Risks And Edge Cases
The global toolbox command function is mutated during the test and may affect parallel suites. The local path PV script touches host-level storage setup and depends on the configured scratch device. Pool deletion failures are logged but do not fail teardown. External cluster setup failures gather logs only for the external namespace.

## Test Signals
Signals include successful local PV setup, core cluster install pod counts, core Ceph health, external Ceph health through the external toolbox, pool create/delete logs, and multi-namespace uninstall.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_multi_cluster_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_object_test.go -->
# sources/control-plane/rook/tests/integration/ceph_object_test.go

## Purpose
Main RGW/Object integration suite. It validates object stores with and without TLS, OBC bucket lifecycle, S3 operations, quota enforcement, bucket policy/lifecycle management, object-store deletion blocking, shared-store subpackages, bucket notifications, and COSI.

## Important APIs, Types, And Functions
`ObjectSuite` owns cluster settings and helper state. `TestWithTLS` and `TestWithoutTLS` run `runObjectE2ETest`; TLS cleanup removes the test secret. `runObjectE2ETest` creates the primary object store, checks that all RGW `zone.json` `*_pool` fields are represented in Rook's shared pool mapping, creates/deletes a second object store, runs `testObjectStoreOperations`, sets up a shared object store for non-TLS subpackage tests, creates a dedicated bucket-notification store, runs bucket notifications, and runs COSI only for non-TLS.

`testObjectStoreOperations` is the large scenario body. It creates a CephObjectStoreUser, creates an OBC and verifies RGW bucket existence, performs S3 put/get/delete and user quota update/enforcement, tests OBC bucket quotas using direct Kubernetes API objects, tests OBC bucket policy create/update/remove with AWS SDK `GetBucketPolicy`, tests OBC bucket lifecycle create/update/remove with AWS SDK and cmp options, checks that an OBC does not regress from Bound to Pending, verifies object-store deletion is blocked by OBC/user dependents, deletes OBC/user, checks mgr pods, and verifies object-store deletion after dependents are gone.

## Control Flow
The suite installs an object-capable cluster in `object-ns`, runs TLS and non-TLS variants, and delegates most behavior to shared base helpers. The operation flow creates store/user/OBC, validates S3 and quota behavior, creates additional direct OBCs for quota/policy/lifecycle tests, then intentionally deletes the object store while dependents remain to assert deletion-blocked status before removing dependents and letting deletion complete.

## State And Persistence Behavior
Creates CephObjectStore CRs, RGW deployments/services/realms/zones/pools, TLS secret, CephObjectStoreUsers and secrets, OBCs/ObjectBuckets, bucket StorageClasses, S3 objects, bucket policies, lifecycle configs, quota configs, shared object stores, Kafka/topic/user-cap/user-key/op-mask subtest resources, bucket notification resources, and COSI resources. It uses package-global object constants and changes `objectStoreServicePrefix`.

## Dependencies And Integration Points
Depends on AWS SDK v2 S3 APIs, smithy errors, go-cmp, lib-bucket-provisioner APIs, Rook Ceph API/client/object package, shared object helpers, bucket-owner/topic-kafka/user subpackages, sharedstore helper, bucket notification helper, COSI helper, and Kubernetes API clients.

## Risks And Edge Cases
The suite is broad and long-running, so failures can leave many dependent resources and make later cleanup noisy. It mutates the global `objectStoreServicePrefix`. Several checks depend on exact RGW/AWS error codes and Ceph version behavior; lifecycle removal explicitly skips Ceph `19.2.3`. The direct S3 endpoint uses ClusterIP `:80`, which assumes non-TLS internal service shape. The test creates and deletes object stores inside a single suite, so namespace-level fixed names can collide after partial failures.

## Test Signals
Signals include object-store readiness, zone pool mapping coverage, second store lifecycle, OBC/OB bound states, RGW bucket existence, S3 object read/write/delete, user and bucket quota enforcement, bucket policy/lifecycle equality and removal error codes, deletion-blocked condition contents, user secret deletion, mgr pod running state, shared-store subpackage results, notification delivery results, and COSI bucket readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_smoke_test.go -->
# sources/control-plane/rook/tests/integration/ceph_smoke_test.go

## Purpose
Primary smoke suite for a manifest-installed Rook Ceph cluster. It validates core install, monitor failover, pool resize, client CRD updates, RBD mirror CRD lifecycle, and basic NFS/block/file/object storage workflows.

## Important APIs, Types, And Functions
`SmokeSuite` holds helper/settings/installer/k8shelper. `SetupSuite` installs `smoke-cluster` in `smoke-ns` with three mons, PVC setting from environment, encrypted and compressed connections, crash pruner, volume replication, NFS CSI testing, hostname changes, selected Ceph version, and CSI operator. Individual tests delegate to `runNFSFileE2ETest`, `runBlockCSITest`, `runFileE2ETest`, and `runObjectE2ETestLite`, or implement cluster checks directly.

`TestMonFailover` scales a non-canary mon deployment to zero and waits either for it to be recreated or for a replacement mon. `TestPoolResize` creates a pool, waits for it in Ceph, updates size from 1 to 2 and back to 1, and checks mirror bootstrap peer token Secret when mirroring is enabled. `TestCreateClient` creates a Ceph client, waits for it in Ceph, updates caps, and deletes it. `TestCreateRBDMirrorClient` creates/deletes an RBDMirror CR. `getNonCanaryMonDeployments` filters mon deployments by suffix.

## Control Flow
Setup creates the cluster and test client. Tests run storage smoke scenarios and cluster-management scenarios. After each test the operator log is collected. Teardown uninstalls Rook. Many storage tests use shared helpers that perform their own cleanup.

## State And Persistence Behavior
Creates and mutates a full Ceph cluster, NFS/File/Block/Object test resources, monitor deployment replicas, CephBlockPool CRs and backend pools, optional mirror bootstrap Secret, Ceph client CR/user, RBDMirror CR, and test PVC/PV/pod state. Pool resize intentionally returns size to 1 to avoid hangs in small OSD setups.

## Dependencies And Integration Points
Depends on shared deploy, NFS, block, file, and object helpers; Rook clients for pools/users/RBDMirror; `k8sutil` and Kubernetes deployment APIs; Ceph client admin info; and testify.

## Risks And Edge Cases
The suite combines many subsystems, so failure in one helper can affect later tests in the same namespace. Monitor failover accepts original mon recreation as success, so it validates recovery but not always replacement. Pool resize assumes enough OSD state to move from size 1 to 2 and back. Object store tests skip on OpenShift. Fixed resource names across helpers limit parallelism.

## Test Signals
Signals include install pod counts, mon deployment replacement/recreation, Ceph pool list/details size changes, optional mirror token Secret contents, client existence and caps, RBDMirror create/delete success, plus all delegated NFS/block/file/object signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_smoke_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_upgrade_test.go -->
# sources/control-plane/rook/tests/integration/ceph_upgrade_test.go

## Purpose
Upgrade integration suite that verifies Rook operator and Ceph daemon upgrades preserve block, file, and object functionality. It covers manifest and Helm upgrade paths plus stable-to-devel Ceph image upgrades.

## Important APIs, Types, And Functions
Constants define upgrade test pod/PVC names and test data. `UpgradeSuite` stores helper/k8s/settings/installer/namespace. `baseSetup` installs an initial Rook/Ceph cluster in namespace `upgrade` with optional Helm and retained Helm storage CRs. `testUpgrade` installs from `installer.Version1_19`, creates pre-upgrade block/file/object resources through `deployClusterforUpgrade`, upgrades Rook to local build, verifies daemon image labels and data access, then, for non-Helm, upgrades Ceph from Squid to Tentacle and revalidates data. `TestUpgradeCephToSquidDevel` and `TestUpgradeCephToTentacleDevel` test stable-to-devel Ceph image changes.

`deployClusterforUpgrade` creates or reuses block pool/storage class/PVC, mounts a block pod, creates CephFS/storage class/consumer, creates object store/user/OBC, writes pre-upgrade RBD data, and returns OSD count plus file lists. `upgradeToMaster` applies new CSI operator, CRDs, common resources, operator image, and toolbox, or runs Helm upgrades. `upgradeCephVersion`, `verifyOperatorImage`, `verifyRookUpgrade`, `waitForUpgradedDaemons`, `verifyFilesAfterUpgrade`, and `gatherLogs` implement the upgrade assertions.

## Control Flow
Each upgrade test starts a baseline cluster, deploys storage consumers before upgrade, records OSD count and old labels, upgrades Rook or Ceph image, waits for mons/mgrs/osds/rgws and sometimes MDSes to have labels different from the previous version, waits for readiness, verifies toolbox availability, reads pre-existing data, writes/reads new data, checks object user and OBC state, and defers cleanup of all storage resources.

## State And Persistence Behavior
Creates a long-lived cluster with `SkipClusterCleanup=true`, block PVC/PV/RBD image and pod, CephFS and consumer PVC/PV/pod, object store/user/OBC/storage class, bucket, and Ceph daemon deployments. It patches `CephCluster.spec.cephVersion.image`, applies CRDs/manifests, changes operator deployment image, and can upgrade Helm releases. Persistence is validated by reading old block data and writing new block/CephFS data after each upgrade.

## Dependencies And Integration Points
Depends on installer version constants, shared block/file/object helpers, Kubernetes deployment label queries, Ceph admin info, toolbox execution, Helm upgrade support, and manifest generation. It reuses helper cleanup functions from other files in this group.

## Risks And Edge Cases
`cephFSFilesToRead` starts empty because no pre-upgrade CephFS file is written before the first upgrade; the suite validates new CephFS writes after upgrade more than old CephFS persistence. Cleanup sets `requireBlockImagesRemoved=false`, which weakens image deletion verification. Version assertions rely on deployment labels changing from old values and exact operator image string containing `docker.io/rook/ceph:<tag>`. Pulling devel images can be slow, so timeouts are extended only for mons.

## Test Signals
Signals include operator image, mon/mgr/osd/MDS/RGW deployment counts and readiness with new labels, toolbox availability, RBD read/write retry success across upgrades, CephFS active status and read/write success, object user readiness, OBC bound state, and pre-upgrade log gathering.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/bucket/owner/owner.go -->
# sources/control-plane/rook/tests/integration/object/bucket/owner/owner.go

## Purpose
Focused object-bucket-owner integration test package. It validates the `bucketOwner` OBC additional config path: creating buckets owned by existing CephObjectStoreUsers, changing bucket owners, preserving user quotas, sharing owners across buckets, rejecting nonexistent owners, and cleanup.

## Important APIs, Types, And Functions
`WaitForPodLogContainingText` selects the first pod matching a label selector, streams logs with a timeout, and returns success when the desired text appears. `TestObjectBucketClaimBucketOwner` builds all test resources inline: namespace, bucket StorageClass, two CephObjectStoreUsers (`osu1` without quotas and `osu2` with quotas), two valid OBCs with `bucketOwner`, and one bogus-owner OBC. It uses Kubernetes clients for CR creation/update/deletion and `go-ceph/rgw/admin` for backend RGW user/bucket checks.

## Control Flow
The test skips TLS mode, creates a namespace and storage class, creates `osu1`, waits for readiness, creates `obc1`, waits for OBC/OB bound state and owner propagation, creates an RGW admin client, verifies backend bucket owner and unchanged user quotas, creates `osu2`, updates `obc1` owner to `osu2`, verifies OBC/OB/backend synchronization and quota preservation, removes owner config while ensuring backend owner remains, changes owner back to `osu1`, creates `obc2` with same owner, verifies both buckets share owner, deletes valid OBCs and ensures users remain, creates a bogus-owner OBC, checks operator log text, verifies Pending state and missing backend user, deletes bogus resources, deletes users/storage class/namespace.

## State And Persistence Behavior
Creates a namespace, StorageClass, CephObjectStoreUsers, ObjectBucketClaims, ObjectBuckets, backend RGW buckets, backend RGW users with quota state, and then updates OBC `AdditionalConfig`. The backend bucket owner persists even after the `bucketOwner` key is removed from OBC/OB state. Cleanup deletes OBCs, users, storage class, and namespace.

## Dependencies And Integration Points
Depends on Rook Ceph API types, lib-bucket-provisioner APIs, Kubernetes core/storage APIs, go-ceph RGW admin API, shared admin-client helper, Rook installer and K8s helper, capnslog, and the parent object suite's shared object store. It is invoked by `ceph_object_test.go` only for non-TLS stores.

## Risks And Edge Cases
`WaitForPodLogContainingText` breaks out on a matching line but returns nil even if the stream ends without finding the text; it does not track a found boolean, so the bogus-owner log assertion can pass falsely when logs stream cleanly without the target text. The expected log text uses `test-bucket-owner-bogus-user`, while the configured default prefix is `test-bucketowner`, suggesting possible mismatch. Some backend checks call `GetBucketInfo` with `obc1.Name` instead of `obc1.Spec.BucketName`; currently those strings match, but the assumption is fragile. The test skips TLS, leaving bucketOwner+TLS interaction uncovered.

## Test Signals
Signals include OBC and OB Bound phases, OBC/OB `bucketOwner` state, RGW admin bucket owner, RGW user quotas before/after ownership changes, users remaining after OBC deletion, bogus OBC Pending phase, backend `ErrNoSuchUser`, operator log text, and resource absence after cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/bucket/owner/owner.go -->
