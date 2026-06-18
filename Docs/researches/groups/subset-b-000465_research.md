# subset-b-000465 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/version/version.go -->
# sources/control-plane/rook/pkg/version/version.go

Purpose: this file defines the package-level Rook version string used by binaries and tests that import `pkg/version`. Its only exported API is `var Version = "0.0.0"`, with the documented expectation that release builds override it through Go linker `-X`.

Important APIs/types/functions: no functions or custom types exist. The mutable exported `Version` variable is the integration point. Any package importing `github.com/rook/rook/pkg/version` can read it after build-time injection.

Control flow: none at runtime beyond global initialization. The default value is assigned during package init before dependents execute.

State and persistence behavior: state is in-process only. Persistence comes indirectly from build metadata embedded into the binary. Because it is a mutable global, tests or other code could change it in-process.

Dependencies and integration points: no imports. The file depends on build tooling to inject the real version and on consumers to tolerate the local default in unversioned/dev builds.

Risks: incorrect linker flags leave binaries reporting `0.0.0`. The mutable global has no validation, so accidental test mutation can leak within a process.

Test signals: test coverage should validate build/release pipelines rather than this file itself. Unit tests that rely on a specific version should account for the default local value.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/external-cluster/external-config.ini -->
# sources/control-plane/rook/tests/external-cluster/external-config.ini

Purpose: this INI-style fixture supplies external-cluster configuration keys used by Rook external cluster tests or scripts. It enumerates expected configuration knobs for Ceph conf/keyring paths, cluster names, namespaces, RGW, monitoring, CephFS, RBD, topology, and upgrade behavior.

Important APIs/types/functions: no code APIs exist. The `[Configurations]` section is the contract. Notable non-empty defaults include `rbd-data-pool-name = replicapoolconfig` and `rados-namespace = radosnamespace2`; all other keys are intentionally present but blank.

Control flow: parsing is performed by external scripts/tests. This file is static data and defines which options are available to callers.

State and persistence behavior: state is persisted as a test fixture. It does not mutate at runtime unless a test harness writes over it.

Dependencies and integration points: integrates with external cluster resource generation paths that expect exact key names such as `cephfs-filesystem-name`, `rgw-endpoint`, `topology-failure-domain-label`, and `upgrade`.

Risks: blank values rely on parser defaults, so tests may silently change behavior if defaults change elsewhere. Typos or stale option names are hard to detect without end-to-end external-cluster tests. The fixture encodes specific pool and namespace names that may collide if reused outside an isolated test.

Test signals: useful tests verify the parser accepts this complete key set, honors the non-empty RBD pool and rados namespace values, and rejects or surfaces missing required external-cluster parameters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/external-cluster/external-config.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/block.go -->
# sources/control-plane/rook/tests/framework/clients/block.go

Purpose: `BlockOperation` is the integration-test wrapper for Rook/Ceph block storage operations. It creates block pools, storage classes, PVCs, pods, snapshots, restores, clones, and lists or deletes RBD images through Ceph clients.

Important APIs/types/functions: `BlockOperation` stores a `*utils.K8sHelper` and `installer.CephManifests`. `BlockImage` is a test DTO for image name, pool, size, device, and mount point. Key methods include `Create`, `CreatePoolAndStorageClass`, `CreatePVC`, `CreatePod`, snapshot class/snapshot helpers, `ListAllImages`, `ListImagesInPool`, and `DeleteBlockImage`.

Control flow: most mutating methods render YAML through `installer` manifest helpers and call `K8sHelper.ResourceOperation` or `KubectlWithStdin`. Listing methods use `client.ListPoolSummaries` followed by `client.ListImagesInPool` per pool. Deletion paths use typed Kubernetes clients for PVCs/storage classes and Ceph client calls for RBD images.

State and persistence behavior: Kubernetes resources and Ceph RBD images are persistent external state. The wrapper itself holds no durable state.

Dependencies and integration points: depends on Rook Ceph client APIs, test manifests, Kubernetes storage APIs, and the shared test logger from `object.go`.

Risks: several parameters are unused (`size`, `csi`, `namespace` in some methods), which can mislead callers. Delete helpers differ in not-found handling: storage class deletion ignores not found, PVC deletion does not. Raw Ceph image deletion bypasses Kubernetes ownership and can be destructive if pool/image names are wrong.

Test signals: strong signals are PVC bound/deleted checks, pod mount read/write checks, snapshot ready/restore behavior, and post-cleanup RBD image enumeration.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/bucket.go -->
# sources/control-plane/rook/tests/framework/clients/bucket.go

Purpose: `BucketOperation` wraps ObjectBucketClaim, bucket storage class, credentials, quota, and notification checks for Rook RGW object bucket integration tests.

Important APIs/types/functions: constructor `CreateBucketOperation`; resource methods `CreateBucketStorageClass`, `DeleteBucketStorageClass`, `CreateObc`, `CreateObcNotification`, `DeleteObc`, `UpdateObc`, and notification update variants; validators `CheckOBC`, `CheckOBMaxObject`, and `CheckBucketNotificationSetonRGW`; credential readers `GetAccessKey` and `GetSecretKey`.

Control flow: create/update/delete methods render manifests from `CephManifests` and delegate to kubectl via `K8sHelper.ResourceOperation`. `CheckOBC` checks OBC/Secret/ConfigMap existence, validates Bound phase when requested, confirms `spec.objectBucketName`, then verifies the ObjectBucket claim reference. Credential methods read Kubernetes secrets using JSONPath and base64-decode the result. RGW notification validation builds an S3 agent from OBC credentials and calls AWS SDK `GetBucketNotificationConfiguration`.

State and persistence behavior: persistent state includes storage classes, OBCs, ObjectBuckets, Secrets, ConfigMaps, and bucket notification configuration in RGW. No local state is persisted.

Dependencies and integration points: integrates Kubernetes object bucket APIs, Rook object operator S3 agent, AWS SDK v2 S3 client, test manifests, and `TestClient` object endpoint lookup.

Risks: base64 decode errors are ignored. `CheckOBC` treats any `GetResource` error as missing, hiding authorization/API failures. Access and secret keys are logged in notification checks, which is acceptable only for isolated test environments. RGW notification checks assume non-nil notification IDs.

Test signals: OBC created/bound/deleted checks, generated Secret/ConfigMap validation, ObjectBucket claim reference checks, maxObjects propagation, and real RGW notification configuration retrieval.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/client.go -->
# sources/control-plane/rook/tests/framework/clients/client.go

Purpose: `ClientOperation` manages `CephClient` CRs and validates resulting Ceph auth keys/caps in integration tests.

Important APIs/types/functions: `ClientOperation` holds `K8sHelper` and `CephManifests`. `Create` applies a `CephClient` manifest. `Delete` uses the Rook typed client to remove `CephClients`. `Get` calls `client.AuthGetKey`. `Update` reapplies caps and polls `client.AuthGetCaps` until the monitor cap matches the requested value.

Control flow: Kubernetes CR changes are applied first, then Ceph CLI/client calls observe whether the operator reconciled those changes. `Update` loops 30 times with 2-second sleeps and returns once `caps["mon"]` matches.

State and persistence behavior: persistent state is the `CephClient` custom resource and Ceph auth database entry. The wrapper has no persisted state.

Dependencies and integration points: depends on generated manifests, Rook Ceph client auth helpers, Rook typed Kubernetes clientset, and test logger.

Risks: `Update` only compares the `mon` capability, so mismatches in `osd`, `mgr`, or other caps may go undetected. The namespace parameter to `Create` is unused because the manifest settings own namespace selection. Ignored errors inside the polling loop can mask transient auth failures until timeout.

Test signals: after create/update, tests should verify key existence and all requested caps, not only monitor caps. Delete should verify both CR removal and Ceph auth cleanup where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/cluster.go -->
# sources/control-plane/rook/tests/framework/clients/cluster.go

Purpose: this file provides cluster health validation for integration tests. `IsClusterHealthy` verifies high-level Ceph status returned through the shared `TestClient`.

Important APIs/types/functions: `IsClusterHealthy(testClient, namespace)` returns a boolean and detailed error. Helper `monInQuorum` checks a mon rank against the quorum rank list.

Control flow: the function reads `testClient.Status`, logs it, then validates monitors, OSDs, manager availability, and placement group cleanliness. It fails fast on empty quorum, mon not in quorum, zero OSDs, any OSD not up/in, unavailable MGRs, or PG states not entirely `active+clean` when PGs exist.

State and persistence behavior: read-only; it observes Ceph cluster state but does not mutate Kubernetes or Ceph.

Dependencies and integration points: depends on Ceph status structures from `pkg/daemon/ceph/client` and `TestClient.Status`, which in turn uses the toolbox/cluster admin context.

Risks: health criteria are strict and may not fit transitional operator states. It requires at least one OSD, so it is incompatible with configurations intentionally skipping OSD creation. PG health only treats exactly `active+clean` as healthy, which can flag expected transient or mixed states.

Test signals: a passing result indicates monitors are in quorum, OSDs are all up/in, managers are available, and PGs are clean. Failures include enough status data in error messages to drive log collection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/cosi.go -->
# sources/control-plane/rook/tests/framework/clients/cosi.go

Purpose: `COSIOperation` wraps COSI test resources for Rook Ceph object storage, including the COSI driver, bucket classes, and bucket claims.

Important APIs/types/functions: constructor `CreateCOSIOperation`; `CreateCOSI`/`DeleteCOSI`; `CreateBucketClass`/`DeleteBucketClass`; `CreateBucketClaim`/`DeleteBucketClaim`.

Control flow: every method renders a manifest from `CephManifests` and calls `K8sHelper.ResourceOperation` with `create` or `delete`. There is no polling or status validation in this layer.

State and persistence behavior: persistent state is Kubernetes CRs for `CephCOSIDriver`, `BucketClass`, and `BucketClaim`. The wrapper itself has no state beyond helper references.

Dependencies and integration points: depends on the objectstorage API manifests emitted by `CephManifestsMaster`, the Rook operator namespace for COSI driver resources, and Kubernetes resource application through kubectl.

Risks: using `create` makes repeated test setup non-idempotent. Delete methods render the same manifest and rely on Kubernetes object identity, so parameter drift can delete or fail unexpectedly. No wait or readiness check means callers must separately verify COSI controller reconciliation.

Test signals: callers should check CR existence, status readiness, bucket provisioning, credentials/secrets, and cleanup of external object state after deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/cosi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/filesystem.go -->
# sources/control-plane/rook/tests/framework/clients/filesystem.go

Purpose: `FilesystemOperation` wraps CephFS lifecycle and CSI client-resource operations for integration tests.

Important APIs/types/functions: constructor `CreateFilesystemOperation`; `Create`, `ScaleDown`, `Delete`, and `List`; CSI helpers for storage classes, PVCs, pods, snapshots, restores, and clones; subvolume group helpers `CreateSubvolumeGroup` and `DeleteSubvolumeGroup`.

Control flow: create/scale operations apply `CephFilesystem` manifests, wait for MDS pods by label, and assert expected pod counts. Delete removes the default CSI subvolume group, deletes the filesystem CR through the typed Rook client, then waits for CR deletion. Subvolume group methods apply/delete the CR, wait for status/deletion, then verify raw CephFS state through toolbox `ceph fs subvolumegroup ls`.

State and persistence behavior: manages persistent CephFilesystem CRs, MDS pods, CephFS pools, CSI storage/snapshot classes, PVC/PV resources, and CephFS subvolume groups.

Dependencies and integration points: relies on Rook typed clientsets, Ceph client filesystem listing, installer manifest templates, Kubernetes storage APIs, toolbox remote execution, and testify assertions.

Risks: many methods assert directly with `k8sh.T()`, causing test failure rather than returning rich errors. Delete assumes a `name+"-csi"` subvolume group. Pod count expectation is `activeCount*2` because active/standby MDS pods are expected; changes in operator behavior can break tests. Namespace arguments to some methods are unused because manifest settings choose namespace.

Test signals: MDS pod readiness, filesystem list output, storage class/PVC binding, snapshot/clone success, and raw Ceph subvolume group presence/absence are primary signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/nfs.go -->
# sources/control-plane/rook/tests/framework/clients/nfs.go

Purpose: `NFSOperation` wraps creation, deletion, and CSI class setup for Rook CephNFS integration tests.

Important APIs/types/functions: constructor `CreateNFSOperation`; `Create`, `Delete`, `CreateStorageClass`, `CreateSnapshotClass`, and `DeleteSnapshotClass`.

Control flow: `Create` first applies an internal `.nfs` block pool, then applies the `CephNFS` CR, waits for labeled NFS pods, and asserts expected pod count/state. `Delete` removes the `CephNFS` CR, waits for deletion, deletes the `dot-nfs` block pool CR, then waits for pool deletion. Storage and snapshot class methods render manifests and apply/delete them through `ResourceOperation`.

State and persistence behavior: persistent state includes the `.nfs` CephBlockPool, CephNFS CR, NFS daemon pods, and CSI storage/snapshot classes.

Dependencies and integration points: uses installer manifests, Rook typed CephV1 clients, K8s helper waiting primitives, and test assertions.

Risks: `Delete` passes `name` to `WaitForCustomResourceDeletion` for the `dot-nfs` pool checker even though the pool name is `dot-nfs`, which can make logs misleading. Assertions inside `Create` fail tests directly. The generated NFS storage class hard-codes service DNS format and expects the first active daemon service suffix.

Test signals: successful NFS pod readiness, correct daemon count, storage class provisioning, snapshot class lifecycle, and absence of CephNFS/pool CRs after cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/notification.go -->
# sources/control-plane/rook/tests/framework/clients/notification.go

Purpose: `NotificationOperation` manages `CephBucketNotification` CRs and verifies notification delivery to a test HTTP endpoint.

Important APIs/types/functions: constructor `CreateNotificationOperation`; `CreateNotification`, `DeleteNotification`, `UpdateNotification`; `CheckNotificationCR`; `CheckNotificationFromHTTPEndPoint`.

Control flow: CRUD methods render `CephBucketNotification` manifests and use kubectl create/delete/apply. `CheckNotificationCR` performs a simple `kubectl get cephbucketnotification`. `CheckNotificationFromHTTPEndPoint` sleeps for five seconds, tails logs from pods matching a selector, and checks for both event and file name substrings.

State and persistence behavior: persistent state is the notification CR and backend RGW notification config created by operator reconciliation. Delivery evidence is transient in HTTP server pod logs.

Dependencies and integration points: depends on bucket topic resources, RGW bucket notifications, `K8sHelper.Kubectl`, and the HTTP server created by `TopicOperation`.

Risks: status is not inspected despite a TODO, so CR existence may be treated as success before reconciliation. Fixed sleep and tailing only five log lines are flaky under load. Log substring matching can false-positive if old messages remain.

Test signals: stronger tests should validate notification CR status, RGW notification config, and fresh HTTP endpoint receipt scoped to unique object names.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/notification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/object.go -->
# sources/control-plane/rook/tests/framework/clients/object.go

Purpose: `ObjectOperation` manages Rook `CephObjectStore` resources for RGW/S3/Swift integration tests and exposes endpoint discovery.

Important APIs/types/functions: package logger and constant `rgwPort = 80`; constructor `CreateObjectOperation`; methods `Create`, `Delete`, and `GetEndPointUrl`.

Control flow: `Create` applies a rendered object store manifest, waits up to 80 retries for RGW pods matching `rook_object_store=<storeName>`, then creates an external NodePort RGW service. `Delete` deletes the `CephObjectStore` resource and waits for pods with the store label to disappear. `GetEndPointUrl` queries the service cluster IP with label `rgw=<storeName>` and appends port 80.

State and persistence behavior: persistent external state includes object store CRs, RGW deployments/pods/services, and Ceph object pools/users managed by the operator.

Dependencies and integration points: depends on `CephManifests.GetObjectStore`, `K8sHelper.ResourceOperation`, `CreateExternalRGWService`, and kubectl JSONPath service lookup.

Risks: endpoint lookup uses cluster IP and fixed port 80, while TLS-enabled stores may use secure ports elsewhere. The create path always creates an external service after RGW readiness, so cleanup must remove it through broader cluster cleanup. The code comment explicitly notes weak error handling for endpoint lookup.

Test signals: RGW pod readiness, service endpoint reachability, object store deletion and pod disappearance, plus S3/Swift client operations are the meaningful checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/object_user.go -->
# sources/control-plane/rook/tests/framework/clients/object_user.go

Purpose: `ObjectUserOperation` manages `CephObjectStoreUser` resources and verifies RGW user state/secret creation.

Important APIs/types/functions: constructor `CreateObjectUserOperation`; `GetUser`, `UserSecretExists`, `Create`, and `Delete`.

Control flow: `Create` applies a rendered object store user CR with quotas/caps. `GetUser` reads the object store CR, creates an RGW multisite context using admin cluster info, and calls `rgw.GetUser`. `UserSecretExists` runs `kubectl get secrets` with labels for object store and user and interprets output text. `Delete` deletes the CR through kubectl.

State and persistence behavior: persistent state includes the Kubernetes user CR, generated secret, and RGW user account/quota/cap metadata.

Dependencies and integration points: depends on Rook object operator APIs, Ceph admin context, typed Rook clientset, installer manifests, and kubectl output conventions.

Risks: `UserSecretExists` treats successful command output containing `No resources found` as absence, which is sensitive to kubectl localization/output format. `GetUser` assumes the object store is available and RGW admin operations are reachable. Deletion does not wait for user or secret cleanup.

Test signals: user CR creation, generated secret labels/data, RGW `GetUser` details, quota/cap propagation, and post-delete absence of CR/secret/RGW user are useful signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/object_user.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/pool.go -->
# sources/control-plane/rook/tests/framework/clients/pool.go

Purpose: `PoolOperation` wraps CephBlockPool CR lifecycle, Ceph pool inspection, and pool deletion with RBD image cleanup.

Important APIs/types/functions: constructor `CreatePoolOperation`; `Create`, `Update`, internal `createOrUpdatePool`; inspection methods `ListCephPools`, `GetCephPoolDetails`, `ListPoolCRDs`, `PoolCRDExists`, `CephPoolExists`; cleanup method `DeletePool`.

Control flow: create/update apply a rendered block pool manifest. Ceph inspection uses `client.ListPoolSummaries` and `client.GetPoolDetails` against the admin test cluster. CR inspection uses the Rook typed client. `DeletePool` lists images in the pool, force-deletes each image with retry, deletes the pool CR, and waits for custom resource deletion.

State and persistence behavior: persistent state includes CephBlockPool CRs, Ceph pools, and RBD images. The wrapper keeps no local durable state.

Dependencies and integration points: integrates with `BlockOperation`, Rook Ceph client APIs, Kubernetes CephV1 clientset, and manifest generation.

Risks: `DeletePool` ignores the error returned by `ListImagesInPool`, potentially proceeding to delete the pool despite failing to enumerate images. The deletion retry logs the whole `BlockImage` with `%q`, which may be noisy. Ceph and CR existence checks can diverge during reconciliation and require caller-side waiting.

Test signals: pool CR existence, Ceph pool summary/details, RBD image cleanup, and custom resource deletion completion are primary validation points.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/rbd-mirror.go -->
# sources/control-plane/rook/tests/framework/clients/rbd-mirror.go

Purpose: `RBDMirrorOperation` manages `CephRBDMirror` resources for tests that validate RBD mirroring daemon deployment.

Important APIs/types/functions: constructor `CreateRBDMirrorOperation`; `Create` and `Delete`.

Control flow: `Create` applies a rendered `CephRBDMirror` manifest, waits for pods labeled `app=rook-ceph-rbd-mirror`, then asserts the expected daemon count in Running state. `Delete` removes the CR through the typed Rook client and ignores not-found errors.

State and persistence behavior: persistent state includes the CephRBDMirror CR and mirror daemon pods. Backend Ceph mirroring state is controlled indirectly by operator reconciliation.

Dependencies and integration points: uses installer manifests, `K8sHelper` pod wait/check methods, Rook typed clientset, Kubernetes API errors, and testify assertions.

Risks: pod checks use only the common app label, so multiple mirror resources in one namespace could affect counts. Delete does not wait for pod or CR finalizer cleanup. Assertions inside `Create` directly fail the test instead of returning detailed errors.

Test signals: expected mirror daemon pod count/running state, CR deletion, and Ceph mirroring status from CLI/client calls in higher-level tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/rbd-mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/test_client.go -->
# sources/control-plane/rook/tests/framework/clients/test_client.go

Purpose: `TestClient` aggregates all individual Rook test operation wrappers into one fixture object and exposes cluster status.

Important APIs/types/functions: `TestClient` fields include block, filesystem, NFS, object, object user, pool, bucket, Ceph client, RBD mirror, topic, notification, and COSI clients plus the underlying `K8sHelper`. `CreateTestClient` constructs each wrapper with the same helper/manifests. `Status` calls `client.Status` using admin test cluster info.

Control flow: construction is straight-line dependency injection. `Status` creates a Ceph context from the helper, builds namespace-scoped admin cluster info, and returns Ceph status or a wrapped error.

State and persistence behavior: the struct holds references only. It does not own external state; individual client wrappers mutate Kubernetes and Ceph.

Dependencies and integration points: central integration point between test suites, `installer.CephManifests`, `utils.K8sHelper`, and Rook Ceph client APIs.

Risks: all clients share one helper and manifest settings, so namespace/version mistakes propagate broadly. The struct exposes fields directly, which keeps tests convenient but permits nil or swapped clients if manually constructed.

Test signals: creation has no direct validation. `Status` success confirms toolbox/admin command path is usable for later health checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/test_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/topic.go -->
# sources/control-plane/rook/tests/framework/clients/topic.go

Purpose: `TopicOperation` manages `CephBucketTopic` resources and a simple HTTP endpoint used to receive RGW bucket notifications in integration tests.

Important APIs/types/functions: constructor `CreateTopicOperation`; topic CRUD methods `CreateTopic`, `DeleteTopic`, `UpdateTopic`; validator `CheckTopic`; helper `CreateHTTPServer`.

Control flow: topic CRUD methods render manifests and use kubectl create/delete/apply. `CheckTopic` ensures the CR exists and has a non-empty `.status.ARN`. `CreateHTTPServer` constructs a Deployment and NodePort Service YAML using a third-party Python web server image, applies it via stdin, then waits for pods labeled with the server name.

State and persistence behavior: persistent state includes the topic CR, HTTP server Deployment/Service, and backend RGW topic configuration after reconciliation.

Dependencies and integration points: depends on `CephManifests.GetBucketTopic`, Kubernetes deployments/services, RGW topic operator status, and the notification client that later tails HTTP server logs.

Risks: hand-built YAML string interpolation can break with invalid names/ports. The third-party image is explicitly noted by TODO and may disappear/change. `IsAlreadyExists` handling on `kubectl apply` errors is mostly irrelevant because apply should be idempotent. NodePort service choice requires cluster support.

Test signals: non-empty topic ARN, HTTP server pod readiness, notification delivery logs, and topic cleanup are the main signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/clients/topic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_helm_installer.go -->
# sources/control-plane/rook/tests/framework/installer/ceph_helm_installer.go

Purpose: this file implements Helm-based Rook operator, Ceph cluster, and Ceph CSI driver installation flows for integration tests.

Important APIs/types/functions: chart constants for `rook-ceph`, `rook-ceph-cluster`, and Ceph CSI drivers; default test resource names; `CreateRookOperatorViaHelm`, `UpgradeRookOperatorViaHelm`, `CreateRookCephClusterViaHelm`, `UpgradeRookCephClusterViaHelm`; `InstallCephCsiDriversViaHelm`; Helm cleanup/validation helpers; configuration builders for block, filesystem, and object store chart values.

Control flow: operator installation builds values for discovery, image tag, monitoring, history, and host network, creates the operator namespace, then installs local or versioned charts based on `RookVersion`. Cluster installation initializes `DataDirHostPath`, unmarshals generated CephCluster YAML to feed `cephClusterSpec`, adds toolbox/monitoring/ingress config, appends default storage CR values, installs/upgrades the chart, and optionally installs Ceph CSI drivers for local Helm tests. CSI driver installation creates snapshot CRDs/controller, waits for readiness, then installs a repo chart with RBD/CephFS and optional NFS drivers.

State and persistence behavior: persistent state includes Helm releases, namespaces, CRDs, Ceph custom resources, storage classes, Prometheus rules, CSI operator resources, and generated temporary Helm values files in the helper.

Dependencies and integration points: depends on `CephInstaller`, `HelmHelper`, `K8sHelper`, generated manifests, YAML marshal/unmarshal, snapshot helpers, and external Helm repositories.

Risks: chart value maps are loosely typed, so YAML schema drift may fail late. External repo/chart versions and Prometheus bundle URLs create network/version risk. Cleanup asserts not-found behavior but does not handle all asynchronous finalizers. Default Helm storage CR cleanup can interfere with tests if retention flags are wrong.

Test signals: successful Helm release install/upgrade, operator and cluster readiness, three expected storage classes, two RGW pods for the default object store, CSI driver deployment, and successful cleanup of default CRs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_helm_installer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_installer.go -->
# sources/control-plane/rook/tests/framework/installer/ceph_installer.go

Purpose: `CephInstaller` is the main integration-test orchestrator for installing, validating, and uninstalling Rook/Ceph clusters through kubectl or Helm.

Important APIs/types/functions: Ceph image/version constants; `CephInstaller` struct; `ReturnCephVersion`; install methods `CreateCephOperator`, `CreateCephCluster`, `CreateRookExternalCluster`, `InstallRook`; wait/validation helpers `waitForCluster`, `WaitForToolbox`, `checkCephHealthStatus`; cleanup methods `UninstallRookFromMultipleNS`, `waitForResourceDeletion`, `removeClusterFinalizers`, `waitForCleanupJobs`; constructor `NewCephInstaller`.

Control flow: non-Helm install creates CRDs, optional hostname mutations, namespaces/RBAC, volume replication CRDs, CSI operator, operator manifest, optional NFS CSI driver, cluster config maps, CephCluster CR with retries, and toolbox. Helm install delegates to Helm-specific methods. `InstallRook` pulls required images, installs the operator, installs the cluster, waits for pods/toolbox/status, and validates Helm defaults when needed. Uninstall collects logs/restart counts, skips cleanup on test failure, optionally adds cleanup policy and checks health, deletes cluster resources through Helm or kubectl, waits for finalizers and cleanup jobs, deletes common/operator/CSI/CRD resources, removes namespaces, verifies host data dir cleanup, and restores hostname labels.

State and persistence behavior: mutates substantial external state: Kubernetes namespaces, CRDs, RBAC, config maps, secrets, CephCluster and dependent CRs, pods/jobs, host data directories, node labels, Helm releases, and global Ceph client toolbox routing (`client.RunAllCephCommandsInToolboxPod`).

Dependencies and integration points: depends on Kubernetes typed clients, Rook clientsets, Ceph client helpers, manifest generators, Helm helper, test environment variables, remote URLs for volume replication CRDs, and Kubernetes wait primitives.

Risks: global and environmental side effects are broad. Cleanup is intentionally skipped on failed tests, leaving clusters for investigation. Forced finalizer removal after repeated waits can mask operator teardown bugs. External URL dependencies and image pulls add CI flake. `InstallCSIOperator` returns `err` after a readiness failure where `err` may be nil, weakening error reporting.

Test signals: operator pod readiness, CSI operator readiness, mon/mgr/osd pod counts, toolbox command success, Ceph status, cleanup job completion, namespace deletion, host path verification, and collected logs/events on failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_installer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_manifests.go -->
# sources/control-plane/rook/tests/framework/installer/ceph_manifests.go

Purpose: this file defines the `CephManifests` interface and the current-version `CephManifestsMaster` implementation that generates Rook/Ceph test manifests as strings.

Important APIs/types/functions: `CephManifests` includes methods for CRDs, operator, common RBAC, clusters, toolbox, block pools/storage/snapshot classes, CephFS/NFS/RBD mirror, object stores/users/buckets/notifications/topics, Ceph clients, filesystem subvolume groups, and COSI resources. `NewCephManifests` chooses master or previous-version implementations. `GetCephCluster` is the largest generator and conditions on PVC storage, mon count, crash pruner, multiple managers, messenger settings, encryption, compression, and OSD creation.

Control flow: static manifest files are loaded and namespace/image substitutions are applied for CRDs/operator/common/toolbox. Other resources are built through string concatenation or `renderTemplate`, using settings to determine namespace, cluster name, image, ports, TLS, Swift/Keystone, COSI names, and CSI provisioner names.

State and persistence behavior: no direct state mutation; the returned YAML becomes persistent Kubernetes state when applied by clients/installers.

Dependencies and integration points: depends on `TestCephSettings`, local `deploy/examples` manifests, previous-version manifest selection, COSI constants, Kubernetes/OpenShift platform detection, and installer helper templating.

Risks: string-built YAML has injection/formatting risk if test names contain special characters. Map iteration in `GetClient` creates nondeterministic caps order. Some comments are stale or duplicated. Changes in Rook CRD schema require coordinated updates here and in `ceph_manifests_previous.go`.

Test signals: manifest rendering should be exercised by end-to-end apply/reconcile tests. Unit-level signals would include namespace placeholder removal, valid YAML parsing, correct CSI driver names, and Swift/Keystone object store fields.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_manifests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_manifests_previous.go -->
# sources/control-plane/rook/tests/framework/installer/ceph_manifests_previous.go

Purpose: this adapter provides manifest generation for the prior Rook release used by upgrade tests, currently `v1.19.5`.

Important APIs/types/functions: constant `Version1_19`; struct `CephManifestsPreviousVersion` with `settings` and `latest`; methods satisfying `CephManifests`.

Control flow: base manifests such as CRDs, CSI operator, operator, common, common-external, and toolbox are read from GitHub for the target version and then patched for namespaces/settings. Most generated custom resources delegate to the current `CephManifestsMaster`. `GetObjectStore` explicitly panics if Swift/Keystone is requested for the previous version.

State and persistence behavior: no direct mutation. It returns YAML from remote release manifests and current generator wrappers that later become Kubernetes state.

Dependencies and integration points: depends on `TestCephSettings.readManifestFromGitHub`, `replaceOperatorSettings`, OpenShift selection, current manifest generator compatibility, and GitHub raw availability.

Risks: delegating most resource generators to the current implementation may produce resources unsupported by the prior release unless explicitly overridden. Remote GitHub reads add network flake and mutable availability risk. The Swift/Keystone panic is intentional but can fail upgrade tests abruptly if a caller does not gate scenarios by version.

Test signals: upgrade tests should verify previous-release installation, manifest fetch success, namespace substitution, and compatibility of delegated resources before upgrading to the local build.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_manifests_previous.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_settings.go -->
# sources/control-plane/rook/tests/framework/installer/ceph_settings.go

Purpose: `TestCephSettings` centralizes integration-test configuration for Ceph/Rook install behavior and provides manifest reading/substitution helpers.

Important APIs/types/functions: `TestCephSettings` fields cover namespaces, storage mode, Helm, mon count, discovery, external mode, cleanup flags, toolbox mode, network settings, volume replication, NFS CSI, hostname mutation, versions, CSI operator, and cluster concurrency. Methods include `ApplyEnvVars`, `readManifest`, `readManifestFromGitHub`, `readManifestFromGitHubWithClusterNamespace`, `replaceCSIOperatorSettings`, `replaceOperatorSettings`, and helper `replaceNamespaces`.

Control flow: `ApplyEnvVars` defaults cleanup skipping to true, but lets `SKIP_TEST_CLEANUP=false` and `SKIP_CLEANUP_POLICY=false` enable cleanup. Manifest readers load local or remote YAML and call namespace replacement. Operator replacement adjusts log levels, discovery, volume replication, allowed OBC fields, and optional concurrent cluster reconciliation.

State and persistence behavior: settings are in-memory but drive all persistent Kubernetes resources generated by installers. Environment variables affect settings at runtime.

Dependencies and integration points: depends on local/remote manifest readers, environment variables, Rook/Ceph version types, and string placeholders embedded in deployment YAML.

Risks: namespace replacement is string-based and panics if placeholders remain, which is good for detection but brittle for upstream manifest format changes. Cleanup defaults can surprise local users by leaving clusters unless env vars override. Operator settings assume exact source strings.

Test signals: rendered manifests should contain no namespace placeholders, operator environment variables should reflect settings, and cleanup flags should match environment input.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/ceph_settings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/environment.go -->
# sources/control-plane/rook/tests/framework/installer/environment.go

Purpose: this file exposes small environment helpers used by installer tests to discover Helm, logging, storage, base directories, and device filters.

Important APIs/types/functions: `TestHelmPath`, `TestLogCollectionLevel`, `StorageClassName`, `UsePVC`, `baseTestDir`, `TestScratchDevice`, `getDeviceFilter`, and `getEnvVarWithDefault`.

Control flow: each helper reads an environment variable and returns a default when unset. `TestHelmPath` checks `TEST_HELM_PATH`, then falls back to `exec.LookPath("helm")`. `baseTestDir` maps `TEST_BASE_DIR=WORKING_DIR` to the current working directory.

State and persistence behavior: no direct persistence. Returned values drive host-path directory creation, PVC mode, Helm execution, log collection, and OSD device selection elsewhere.

Dependencies and integration points: uses `os`, `os/exec`, current working directory, and the installer logger. Integrated by `CephInstaller`, `NewHelmHelper`, and manifest generation.

Risks: missing Helm path can propagate as an empty command string until Helm execution fails. Defaults such as `/data`, `/dev/nvme0n1`, and empty storage class/device filter are environment-specific. Logging environment values may expose sensitive paths but not credentials in this file.

Test signals: environment-driven tests should cover Helm path override/fallback, `WORKING_DIR` resolution, PVC mode detection from `TEST_STORAGE_CLASS`, and default values in local CI.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/environment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/general_manifests.go -->
# sources/control-plane/rook/tests/framework/installer/general_manifests.go

Purpose: this file generates generic Kubernetes manifests used by block/filesystem/NFS CSI tests: pods, PVCs, restored PVCs, cloned PVCs, and volume snapshots.

Important APIs/types/functions: `GetPodWithVolume`, `GetPVC`, `GetPVCRestore`, `GetPVCClone`, and `GetSnapshot`.

Control flow: each function returns YAML through string concatenation. Pod manifests use `busybox`, sleep forever, mount a PVC at the requested path, and set `restartPolicy: Never`. PVC restore and clone functions set `dataSource` to either `VolumeSnapshot` or another `PersistentVolumeClaim`.

State and persistence behavior: no direct mutation. Applied manifests create persistent Kubernetes pods, PVC/PV state, clone/restore relationships, and VolumeSnapshot resources.

Dependencies and integration points: used by `BlockOperation` and `FilesystemOperation`. Integrates with Kubernetes CSI provisioners and snapshot APIs installed by test helpers.

Risks: direct string interpolation assumes valid names, access modes, sizes, and paths. The busybox image and sleep command need to be available in the test cluster. YAML has no labels, so some helper functions that select by app label do not apply to these resources.

Test signals: applied manifests should result in bound PVCs, running pods with mounted volumes, ready snapshots, and successful restore/clone PVC binding.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/general_manifests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/installer.go -->
# sources/control-plane/rook/tests/framework/installer/installer.go

Purpose: this file contains package-wide installer constants and small helpers shared by Rook integration installers.

Important APIs/types/functions: `LocalBuildTag`, package logger, kubectl argument constants (`createArgs`, `createFromStdinArgs`, `deleteArgs`, `deleteFromStdinArgs`), `SystemNamespace`, `checkError`, and `renderTemplate`.

Control flow: `SystemNamespace` returns the namespace itself on OpenShift and `<namespace>-system` otherwise. `checkError` ignores nil and not-found errors during cleanup but asserts any other error. `renderTemplate` parses and executes a Go text template, panicking on parse or render errors.

State and persistence behavior: no direct persistence. Constants shape applied resource operations and image tags across installer files.

Dependencies and integration points: depends on capnslog, `utils.IsPlatformOpenShift`, testify assertions, Kubernetes API errors, and `text/template`. Used by manifest generation and installer cleanup paths.

Risks: panic-based template rendering is acceptable for tests but abrupt. Cleanup assertion behavior can fail a whole suite after the underlying test passed if teardown encounters unexpected errors. The shared argument slices should not be mutated by callers.

Test signals: platform-specific namespace calculation, not-found cleanup tolerance, and template rendering for object store manifests are the key behaviors to exercise indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/installer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/settings.go -->
# sources/control-plane/rook/tests/framework/installer/settings.go

Purpose: this file implements manifest reading from the local tree or GitHub release branches and rewrites the local Rook image tag for test manifests.

Important APIs/types/functions: package regexp `imageMatch`; functions `readManifest`, `buildURL`, `readManifestFromGitHub`, and `readManifestFromURL`.

Control flow: `readManifest` finds the Rook root, reads `deploy/examples/<filename>`, and rewrites `image: docker.io/rook/ceph:<tag>` to `local-build`. `buildURL` handles historical `v1.6` and `v1.7` release paths differently from current `deploy/examples`. `readManifestFromGitHub` constructs a raw GitHub URL, and `readManifestFromURL` retries HTTP GET up to three times before panicking and returns the response body.

State and persistence behavior: read-only except for network I/O. Returned manifest strings later become persisted Kubernetes resources.

Dependencies and integration points: depends on filesystem root discovery, GitHub raw content, HTTP client, regexp image replacement, and installer logger.

Risks: no HTTP status code validation means 404 pages can be treated as manifest content. `defer response.Body.Close()` will panic if all retries fail without a response, though the loop panics on third request error. URL path compatibility is hard-coded for only old releases. Image regexp only matches docker.io rook/ceph lines.

Test signals: local manifest reads, image replacement, previous-version URL construction, and HTTP status/error handling should be covered or observed by upgrade tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/installer/settings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/env.go -->
# sources/control-plane/rook/tests/framework/utils/env.go

Purpose: this file provides test-environment helpers for platform naming, retry counts, OpenShift detection, and default environment variable reads.

Important APIs/types/functions: `TestEnvName`, `TestRetryNumber`, `IsPlatformOpenShift`, and `GetEnvVarWithDefault`.

Control flow: `TestEnvName` reads `TEST_ENV_NAME` with default `localhost`. `TestRetryNumber` reads `RETRY_MAX` with default `55` and panics if conversion to integer fails. `IsPlatformOpenShift` is true only when `TestEnvName()` equals `openshift`.

State and persistence behavior: no persistence. Values influence package-level retry loop initialization and platform-specific command/manifest behavior.

Dependencies and integration points: used by `k8s_helper.go`, installer namespace/OpenShift paths, log collection naming, and test wait loops.

Risks: invalid `RETRY_MAX` panics at runtime. OpenShift detection is string-exact and depends on CI naming conventions. Since `RetryLoop` is initialized at package load, later changes to `RETRY_MAX` will not affect it.

Test signals: environment override tests should verify retry parsing, default values, and OpenShift command selection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/exec_utils.go -->
# sources/control-plane/rook/tests/framework/utils/exec_utils.go

Purpose: this file implements a generic OS command runner with stdin support and captured stdout/stderr for test utilities.

Important APIs/types/functions: `CommandArgs` describes command, args, stdin payload, and environment variables. `CommandOut` carries stdout, stderr, exit code, and error. `ExecuteCommand` runs the command and streams/captures output.

Control flow: `ExecuteCommand` builds `exec.Command`, appends caller-provided environment entries, obtains stdout/stdin/stderr pipes, starts goroutines scanning stdout/stderr, starts the process, optionally writes stdin, waits, and returns captured buffers plus exit status when available.

State and persistence behavior: no local persistence. It may execute commands with arbitrary external side effects, especially kubectl/oc calls from helpers.

Dependencies and integration points: used by `K8sHelper.KubectlWithStdin`. Depends on Go `os/exec`, `bufio.Scanner`, capnslog, and Rook `utilexec.ExitStatus`.

Risks: `cmd.Env = append(cmd.Env, ...)` starts from nil, so only supplied env vars are passed, not the parent environment; callers here usually supply none. Scanner default token limits may truncate very long output lines. Goroutine scanner errors are ignored. If no stdin is written, the stdin pipe is not explicitly closed before wait.

Test signals: command success/failure, stdin application, stderr filtering for “no buildable Go source files”, and correct exit code extraction are relevant.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/exec_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/helm_helper.go -->
# sources/control-plane/rook/tests/framework/utils/helm_helper.go

Purpose: `HelmHelper` wraps Helm CLI execution for Rook test installs, upgrades, and uninstalls.

Important APIs/types/functions: `HelmHelper` with executor and `HelmPath`; `NewHelmHelper`; `Execute`; `InstallLocalHelmChart`; `InstallVersionedChart`; `InstallOrUpgradeHelmRepoChart`; `UninstallHelmReleaseIfExists`; `DeleteLocalRookHelmChart`; helper `createValuesFile`; root finder `FindRookRoot`.

Control flow: install methods assemble Helm CLI args, optionally create a temporary `values-test.yaml`, and call `helm install`, `upgrade`, or `upgrade --install`. Local installs retry up to five times. Versioned installs add the `rook-release` repo and install chart versions. Repo chart installs force-update a repo, update repos, then install/upgrade. Uninstall tolerates “not found” messages. `FindRookRoot` walks parents until a `tests` folder is found.

State and persistence behavior: mutates Helm releases, repos/cache, namespaces, and temporary values files. `values-test.yaml` is removed after install attempt.

Dependencies and integration points: used by Helm installer methods; depends on Rook repo layout, Helm binary path, YAML marshaling, and Rook command executor.

Risks: temporary values file uses a fixed relative filename, which can race under parallel tests in the same working directory. `FindRookRoot` treats any parent with `tests` as root. Helm repo/network failures can make tests flaky. Missing `HelmPath` fails at command execution time.

Test signals: command argument construction, values serialization, retry behavior, not-found uninstall tolerance, and local chart path resolution.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/helm_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/k8s_helper.go -->
# sources/control-plane/rook/tests/framework/utils/k8s_helper.go

Purpose: `K8sHelper` is the central Kubernetes utility layer for Rook integration tests. It combines typed clients, kubectl/oc execution, pod/resource waits, log collection, storage checks, RGW service helpers, hostname mutation, and cleanup diagnostics.

Important APIs/types/functions: `K8sHelper` holds command executors, Kubernetes/Rook/bucket clientsets, in-cluster flag, testing callback, and remote pod executor. Key methods include `CreateK8sHelper`, `Kubectl`, `KubectlWithTimeout`, `KubectlWithStdin`, `ResourceOperation`, delete/get wrappers, pod/deployment/PVC/PV wait and status checks, `ExecToolboxWithRetry`, RGW URL/service helpers, namespace creation/deletion waits, log/event/describe collection, hostname change/restore, and anonymous cluster binding creation.

Control flow: helper creation builds REST config and clientsets. Most waits poll typed clients for up to `RetryLoop` iterations with `RetryInterval` sleeps. Kubectl paths run shell commands through `CommandExecutor` or `ExecuteCommand`. Resource application uses stdin. Diagnostics create files under `_output/tests/` and collect logs via typed pod log APIs with kubectl fallback.

State and persistence behavior: mutates Kubernetes resources, node hostname labels, cluster role bindings, external RGW services, files in `_output/tests`, and remote pod filesystem contents. It also observes persistent storage resources and cluster state.

Dependencies and integration points: used by nearly every client and installer file. Depends on controller-runtime config, Kubernetes client-go, Rook and object bucket clientsets, Rook command/remote executors, env-derived retry/platform settings, and kubectl/oc binaries.

Risks: broad API surface mixes typed and shell behavior, leading to inconsistent error semantics. `KubectlWithTimeout` always invokes `kubectl` instead of platform `cmd`, while stdin path uses `cmd`. Some helpers assume labels, first service port, first pod, or specific output strings. `CreateAnonSystemClusterBinding` grants cluster-admin to `system:anonymous` for kubeadm test environments and is high privilege. Log files are timestamped and can grow across repeated failures.

Test signals: successful clientset construction, pod/deployment readiness waits, PVC/PV lifecycle checks, resource apply/delete idempotence, toolbox exec, log/event capture on failure, RGW endpoint reachability, and hostname restoration are the principal signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/k8s_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/retry.go -->
# sources/control-plane/rook/tests/framework/utils/retry.go

Purpose: this file provides a small generic retry helper for test predicates.

Important APIs/types/functions: `Retry(count uint16, wait time.Duration, description string, f func() bool) bool`.

Control flow: the helper calls `f` up to `count` times. It returns true immediately on the first true result, logging the attempt number. On false, it logs and sleeps for `wait`. If all attempts fail, it logs final failure and returns false.

State and persistence behavior: no persistence. The callback can have arbitrary side effects; `Retry` itself only logs and sleeps.

Dependencies and integration points: depends on package logger from `exec_utils.go`. Used wherever tests need a concise polling loop outside the richer Kubernetes wait helpers.

Risks: only boolean success is supported, so error details must be logged inside the callback or are lost. Sleeps occur after every failed attempt including the last failed callback before final return. `uint16` count is unusual and can truncate larger configured retry values if cast by callers.

Test signals: retry count, early success behavior, wait interval usage, and log messages are straightforward to validate with a stub callback.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/snapshot.go -->
# sources/control-plane/rook/tests/framework/utils/snapshot.go

Purpose: this file installs/removes Kubernetes CSI snapshot CRDs/controllers and checks VolumeSnapshot readiness for integration tests.

Important APIs/types/functions: snapshotter constants for version `v8.5.0`, GitHub raw paths, `CheckSnapshotISReadyToUse`, `CreateSnapshotController`, `DeleteSnapshotController`, `CreateSnapshotCRD`, `DeleteSnapshotCRD`, and internal `snapshotController`/`snapshotCRD`.

Control flow: snapshot readiness polls `kubectl get volumesnapshot ... jsonpath={.status.readyToUse}` with increasing sleeps and parses a bool. Controller setup fetches the remote controller manifest, replaces `canary` with the pinned version, applies/deletes it via stdin, then applies/deletes RBAC by URL. CRD setup applies/deletes volume snapshot and volume group snapshot CRDs from remote URLs, adding `--validate=false` for create/apply.

State and persistence behavior: mutates cluster-scoped CRDs, snapshot-controller deployment/RBAC in `kube-system`, and VolumeSnapshot status observations.

Dependencies and integration points: used by Helm CSI driver installation and storage snapshot tests. Depends on GitHub raw content, kubectl, Kubernetes apps client for controller readiness, and shared retry interval.

Risks: external URL availability is required. `WaitForSnapshotController` may dereference deployment status even when not found because the zero-value object is not set when `ss` is nil in some client-go cases; this should be checked carefully. Readiness parsing treats non-bool output as retryable. Applying CRDs by URL depends on network and Kubernetes API compatibility.

Test signals: CRD existence, snapshot-controller ready replicas, VolumeSnapshot `readyToUse=true`, and cleanup deletion are key signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/storage.go -->
# sources/control-plane/rook/tests/framework/utils/storage.go

Purpose: this file copies Kubernetes storage helper logic to detect default StorageClasses by annotation.

Important APIs/types/functions: constants `isDefaultStorageClassAnnotation` and `betaIsDefaultStorageClassAnnotation`; function `isDefaultAnnotation`.

Control flow: `isDefaultAnnotation` checks the GA annotation first, then the beta annotation, returning true only when either value is exactly `"true"`.

State and persistence behavior: read-only. It inspects `metav1.ObjectMeta` annotations supplied by callers.

Dependencies and integration points: used by `K8sHelper.IsDefaultStorageClassPresent` after listing storage classes. Depends only on Kubernetes metav1 types.

Risks: nil annotation maps are safe for reads in Go. The helper does not parse truthy values other than lowercase `"true"`, matching Kubernetes behavior. It is copied from Kubernetes v1.21.1, so future upstream semantic changes would need manual sync.

Test signals: storage classes annotated with GA or beta default annotations should return true; absent/false annotations should return false.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/framework/utils/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_auth_keystone_test.go -->
# sources/control-plane/rook/tests/integration/ceph_auth_keystone_test.go

Purpose: this integration suite validates Rook RGW object store authentication through OpenStack Keystone for object-store creation, Swift access, and S3 access.

Important APIs/types/functions: `TestCephKeystoneAuthSuite`; suite type `KeystoneAuthSuite`; lifecycle methods `SetupSuite`, `TearDownSuite`, `AfterTest`; tests `TestObjectStoreOnRookInstalledViaHelmUsingKeystone`, `TestWithSwiftAndKeystone`, `TestWithS3AndKeystone`; helper `cleanUpTLSks`.

Control flow: setup creates Helm-based Rook settings in namespace `keystoneauth-ns`, enables discovery, hostname changes, encrypted connections, and cleanup, starts the test cluster, installs Keystone, creates a `usersecret` with OpenStack auth environment keys from generated test user data, and creates the shared `TestClient`. Tests set `swiftAndKeystone=true`, use non-TLS object stores, and call broader object/Swift/S3 E2E helpers. Teardown cleans Keystone, deletes the user secret with timeout, and uninstalls Rook. `AfterTest` collects operator logs when configured or on failure.

State and persistence behavior: creates a full Rook/Ceph cluster, Keystone deployment, Kubernetes secret with OpenStack credentials, object stores, TLS secrets from called helpers, buckets/containers/objects, and logs. Teardown attempts to remove these resources unless failure cleanup policy keeps them.

Dependencies and integration points: depends on clients, installer, K8s helper, Keystone setup helpers from sibling files, object E2E helpers, OpenStack CLI/AWS client behavior, cert-manager/trust-manager setup, and Yaook Keystone image assumptions.

Risks: heavyweight external integration has many flake points: Helm install, image pulls, Keystone readiness, generated credentials, certificate distribution, object store reconciliation, and client CLIs. `cleanUpTLSks` calls `logger.Fatal` on unexpected secret deletion failure, which can abort abruptly. The namespace/operator namespace are the same, which exercises a specific deployment topology.

Test signals: successful cluster setup, Keystone installation, usersecret creation, RGW object store with Keystone auth, Swift container/object operations, S3 operations with Keystone, invalid credential rejection in called helpers, and clean teardown/log collection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/ceph_auth_keystone_test.go -->
