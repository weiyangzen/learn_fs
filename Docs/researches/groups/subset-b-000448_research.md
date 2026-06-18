# Research: subset-b-000448

Grouped research for the Rook Ceph cluster control-plane files in `sources/control-plane/rook/pkg/operator/ceph/cluster`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephx_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cephx_test.go

Purpose: exercises the cluster package's admin CephX keyring generation, admin key rotation, interrupted rotation recovery, and per-namespace admin rotation locking. The file is test-only but is the strongest executable specification for the admin rotation protocol used by local cluster startup before other Ceph CLI operations proceed.

Important APIs and helpers: `Test_genKeyring` validates `genKeyring` output shape and error handling for empty keys or malformed caps, including `adminKeyAccessCaps`. `Test_admin_key_rotation` builds a fake `clusterd.Context`, fake Kubernetes clients, a temp config dir, and a strict ordered mock executor. It directly calls `rotateAdminCephxKey` and `recoverPriorAdminCephxKeyRotation`. Local helpers `isCommand` and `hasArg` enforce exact Ceph command ordering and keyring identity. Constants model trimmed `ceph auth get-or-create-key`, `auth ls`, and `auth rotate` JSON outputs. `Test_adminRotationLock` validates `claimAdminRotationLock`, `releaseAdminRotationLock`, and the shared `adminRotationInProgress` map.

Control flow: the happy path expects creation of `client.admin-rotator`, `auth ls` as the rotator, `auth rotate client.admin`, validation by `auth ls` using the temporary new admin keyring, and deletion of the rotator. It expects the rotation function to return the sentinel `errSuccessfulAdminKeyRotation`, trigger `reloadManagerFunc`, update `CephCluster.Status.Cephx.Admin`, update the `rook-ceph-mon` secret's `ceph-secret`, and remove the temporary rotator secret. Failure subtests stop at each phase, then call recovery to prove the next reconcile can complete from partially persisted state.

State and persistence behavior: the tests assert three critical stores: Ceph auth state, represented by mock command output; Kubernetes `rook-ceph-mon` secret data, which carries the active admin key and must preserve `mon-secret`, `fsid`, and username; and `CephCluster.Status.Cephx.Admin`, which must only advance after the rotation is complete or recovered. The temporary `rook-ceph-admin-rotator-keyring` secret is intentionally persisted across some failures to enable recovery and removed on success.

Dependencies and integration points: depends on fake controller-runtime clients, fake Kubernetes clientsets, the Rook Ceph scheme, `client.ClusterInfo`, `k8sutil.OwnerInfo`, mocked Ceph command execution, and a temp config directory matching the keyring paths passed on command lines. It integrates with production functions from the cluster package but does not cover daemon rollout directly.

Risks: the tests reveal that command ordering and keyring selection are safety-critical; running the wrong command with the wrong keyring could lock Rook out of the cluster. The recovery path handles several partial states, but it relies on accurately detecting whether `client.admin` and `client.admin-rotator` can still run `auth ls`. The lock is process-local, so it prevents in-process concurrent rotations by namespace but is not a distributed lock.

Test signals: strong coverage for admin rotation success, failures at rotator creation, rotator `auth ls`, admin rotate, temporary admin validation, rotator deletion, cleanup-only recovery, and lock behavior. The tests are intentionally command-sequence-sensitive and would catch skipped Ceph commands, wrong `--name`, or wrong `--keyring` arguments.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephx_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup.go

Purpose: implements host data cleanup for a deleting local `CephCluster` when its cleanup policy requests data-dir sanitization. It waits until Ceph daemon pods are gone, determines the nodes that hosted Ceph daemons, and starts one privileged cleanup Job per host to run `ceph clean host`.

Important APIs and functions: `startClusterCleanUp` waits for daemon cleanup then calls `startCleanUpJobs`. `startCleanUpJobs` builds replaceable Kubernetes Jobs with cleanup labels and annotations. `cleanUpJobContainer` creates the privileged `host-cleanup` container and environment. `cleanUpJobTemplateSpec` builds pod volumes, security, service account, host networking, placement, and resources. `getCleanupPlacement` merges tolerations from global, cleanup, mon arbiter, mon, mgr, osd, and PVC device-set placement. `waitForCephDaemonCleanUp` polls until no daemon hosts remain or context is canceled. `getCephHosts` lists daemon pods by app label and maps Kubernetes node names to hostnames. `getCleanUpDetails` loads `ClusterInfo` and returns monitor secret and FSID.

Control flow: deletion reconcile captures mon secret, cluster FSID, and host list before starting cleanup. The goroutine waits until daemon pods for mons, mgrs, OSDs, object stores, MDS, RBD, and mirrors are gone, then schedules Jobs pinned to the saved hostnames with a hostname node selector. Each Job uses `k8sutil.RunReplaceableJob`, so reruns can replace existing cleanup jobs.

State and persistence behavior: creates batch Jobs named with truncated hostnames and labels including `rook-ceph-cleanup=true`. It mounts `DataDirHostPath`, `/dev`, and `/run/udev`; passes the namespace, monitor secret, FSID, sanitize method, data source, and iteration through env vars; defaults sanitize iteration to `1` by mutating the in-memory cluster spec when unset. It does not update `CephCluster` status itself.

Dependencies and integration points: uses Rook API cleanup annotations, labels, resources, and priority class helpers; daemon app names from mon/mgr/osd/object/mds/rbd/mirror packages; host lookup and job helpers from `k8sutil`; and `opcontroller` for privileged security context, app labels, loop-device setting, and host-network enforcement.

Risks: Jobs run privileged as UID 0 with host device access, so incorrect host selection or cleanup policy confirmation can destroy data. `getCephHosts` depends on app labels and node hostname lookup; missing labels or transient list errors block cleanup. Mutating `cluster.Spec.CleanupPolicy.SanitizeDisks.Iteration` inside container construction is surprising and could leak into later logic if the same object is reused. `waitForCephDaemonCleanUp` can wait indefinitely until the parent context is canceled.

Test signals: `cleanup_test.go` validates key env values and toleration merging, but there is no direct test for polling, hostname discovery, replaceable Job creation, error paths, or sanitization environment completeness.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup_test.go

Purpose: verifies the cleanup Job pod template and cleanup placement toleration aggregation for `cleanup.go`.

Important APIs and tests: `TestCleanupJobSpec` builds a minimal `CephCluster` with namespace, `DataDirHostPath`, and cleanup confirmation, then calls `cleanUpJobTemplateSpec` through a `ClusterController`. `TestCleanupPlacement` constructs a `ClusterSpec` with tolerations under multiple placement keys and a storage class device set, then checks the resulting `Placement`.

Control flow: the first test exercises the container/template path enough to confirm that `ROOK_DATA_DIR_HOST_PATH` and `ROOK_NAMESPACE_DIR` are placed in the first two env slots when a data dir is set. The second test incrementally adds tolerations for `all`, mon, mgr, mon arbiter, osd, and device-set placement and checks the count after each addition.

State and persistence behavior: test state is entirely fake clientsets and in-memory `CephCluster` objects. No Jobs are created; the test inspects generated `PodTemplateSpec` and `Placement` values only.

Dependencies and integration points: uses Rook fake clientsets, `clusterd.Context`, Rook Ceph API types, Kubernetes core toleration types, and `testify/assert`.

Risks: the env assertion is positional rather than name-based, so legitimate env reordering would break the test, while missing later env vars would not be detected. Placement tests validate counts more than exact ordering/content after the first case. There is no test that `startCleanUpJobs` creates correctly labeled Jobs or node selectors.

Test signals: provides focused regression coverage for cleanup pod env basics and toleration aggregation, leaving operational cleanup flow mostly untested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cluster.go

Purpose: contains the core local/external Ceph cluster orchestration object and startup sequence for mons, mgrs, OSDs, Ceph config, telemetry, msgr2 settings, CRUSH cleanup, and initial CephX status. It is the main reconcile engine invoked by `ClusterController`.

Important APIs and types: `cluster` stores `ClusterInfo`, `clusterd.Context`, namespace/spec metadata, `mon.Cluster`, owner info, upgrade flag, monitoring routines, and observed generation. `newCluster` seeds an admin `ClusterInfo` and mon orchestrator. `reconcileCephDaemons` runs the local daemon sequence. `initializeCluster` chooses external vs local orchestration and starts monitoring. `configureLocalCephCluster`, `preClusterStartValidation`, and `validateStretchCluster` validate and launch local clusters. Helpers manage CRUSH roots/rules, pre/post mon and mgr actions, storage ratios, config store updates, telemetry, msgr2, secret-sourced Ceph config, initial CephX status, and bootstrap key deletion.

Control flow: local reconcile populates the config override ConfigMap, runs pre-mon actions, starts mons, verifies cluster identity, runs post-mon actions including admin/mon key rotation and CSI/nodedaemon secrets, starts mgrs, runs post-mgr actions, starts OSDs, optionally configures stretch arbiter, and handles upgrade completion logging. `initializeCluster` first rejects disallowed host paths, configures external clusters if requested, otherwise loads prior cluster info, recovers interrupted admin key rotation before any Ceph CLI use, starts monitoring early if mgr deployments already exist, configures the local cluster, and reports telemetry asynchronously.

State and persistence behavior: persists config override ConfigMaps, cluster config store entries, CSI secrets, crash/exporter secrets, Ceph monitor-store options, CephX status, cluster conditions, bootstrap peer secret, Ceph telemetry config-keys, and Ceph auth/key changes through imported helpers. It mutates spec defaults such as monitor count and external msgr2 flags in memory. `initClusterCephxStatus` writes uninitialized daemon statuses only for new clusters before identity is established and uses retry-on-conflict for status updates.

Dependencies and integration points: coordinates mon, mgr, osd, nodedaemon, csi, config/keyring, telemetry, reporting, Ceph client commands, KMS validation, Rook version, Kubernetes clients, and operator settings. It relies on `detectAndValidateCephVersion`, monitoring setup, config map population, and key-rotation functions defined elsewhere in the package.

Risks: reconcile ordering is safety-critical: admin key recovery must run before Ceph commands, mon key rotation intentionally aborts with an error to trigger a restart reconcile, and mgr module configuration is asynchronous so module failures are logged but do not fail the main reconcile. `shouldUpdateFloatSetting` only updates ratios if relative change is more than 1 percent, which avoids churn but may ignore tiny requested changes. Secret-sourced Ceph config logs values at trace level. Telemetry is serialized with a mutex but still runs asynchronously after local reconcile.

Test signals: `cluster_test.go` covers validation, msgr2 config, CRUSH cleanup gating, telemetry, cluster full ratios, secret-sourced config, and initial CephX status. CephX admin rotation is covered separately in `cephx_test.go`. Full daemon orchestration is not end-to-end tested here because it depends on many package-level collaborators and Ceph command side effects.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external.go

Purpose: configures Rook to connect to and optionally manage aspects of an external Ceph cluster. It validates external specs, populates external `ClusterInfo`, writes connection/config state, creates optional secrets and monitoring resources, and cleans up external-mode connection artifacts during deletion.

Important APIs and functions: `configureExternalCephCluster` is the main external-mode reconcile path. `purgeExternalCluster` deletes connection ConfigMaps and Secrets. `validateExternalClusterSpec` enforces `DataDirHostPath` when an image is supplied and defaults external mgr prometheus port when monitoring is enabled. `configureExternalClusterMonitoring` creates a metrics Service, external metrics endpoint, and ServiceMonitor through the mgr package and controller helpers.

Control flow: external reconcile sets a Connecting condition, populates external cluster info from Kubernetes secrets, validates the health checker key is base64 keyring data, optionally writes local connection config when no Ceph image is specified, validates Ceph version and creates config override/config store when a Ceph image is specified, verifies cluster identity, infers `RequireMsgr2` from v2 mon endpoints, creates crash/exporter secrets when enabled and credentials allow, discovers external Ceph version for monitoring, creates CSI CephConnection and default client profile, and finally sets a Connected condition.

State and persistence behavior: persists connection config, config override ConfigMap, global config Secret, crash collector secret, exporter secret, monitoring Service, external metrics endpoint, ServiceMonitor, CephConnection, default client profile, and cluster status conditions. `purgeExternalCluster` removes mon endpoint/config override ConfigMaps and several mon/CSI/config Secrets, ignoring not-found errors.

Dependencies and integration points: uses `opcontroller.PopulateExternalClusterInfo`, mon connection config, Ceph client version/port helpers, nodedaemon secret helpers, mgr metrics and ServiceMonitor logic, CSI resource creation, and Kubernetes clientsets. It reuses the same `cluster` state object as local orchestration but does not start local daemon deployments unless external management settings require supporting artifacts.

Risks: external mode's behavior changes significantly depending on whether `Spec.CephVersion.Image` is set. Mutating `Spec.Network.Connections.RequireMsgr2` in memory based on external mon ports is important for CSI behavior but may not persist back to the CR. Exporter secret creation is conditional on admin credentials and a non-secret-name key value, which could surprise configurations with lower-privileged users. `purgeExternalCluster` deletes broad connection artifacts in the namespace and only logs failures.

Test signals: `cluster_external_test.go` covers only validation/defaulting. There are no tests here for full external connection, key validation, monitoring resource creation, msgr2 inference, or purge behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external_test.go

Purpose: unit tests the small external-cluster spec validation/defaulting helper.

Important APIs and tests: `TestValidateExternalClusterSpec` constructs a `cluster` with a mutable `ClusterSpec` and calls `validateExternalClusterSpec` under several states.

Control flow: the test verifies that a blank external spec is accepted, setting a Ceph image without `DataDirHostPath` returns an error, adding `DataDirHostPath` clears the error, and enabling monitoring defaults `ExternalMgrPrometheusPort` to `9283`.

State and persistence behavior: all effects are in-memory mutation of `cluster.Spec`; the key persisted-like behavior is defaulting `Monitoring.ExternalMgrPrometheusPort` when it was zero.

Dependencies and integration points: uses Rook Ceph API types, a `mon.Cluster` placeholder, and `testify/assert`.

Risks: coverage is narrow and does not validate the main external reconcile path. It also does not test nonzero prometheus port preservation or interactions with missing/invalid external secrets.

Test signals: good for protecting `DataDirHostPath` requirement and default metrics port, weak for operational external cluster behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_test.go

Purpose: tests core helper behavior from `cluster.go`: pre-start validation, msgr2 config, post-mgr CRUSH cleanup, telemetry reporting, cluster full-ratio settings, secret-sourced Ceph config, and initial CephX status.

Important APIs and tests: `TestPreClusterStartValidation` covers monitor defaults, node-count validation, floating mons, and stretch cluster zone/arbiter rules. `TestConfigureMsgr2` uses a mock executor and parses generated INI config for encryption/compression/rbd map options. `TestPostMgrStartupActionsCleansUnusedCrushRules` and the disabled variant validate `ROOK_DELETE_UNUSED_CRUSH_RULES`. `TestTelemetry` checks reported config-key values for normal and external clusters. `TestClusterFullSettings` verifies ratio commands are issued only when desired values differ enough. `TestFetchCephConfigFromSecrets` covers success and error cases. `Test_initClusterCephxStatus` covers initialized, uninitialized, nonzero, and canceled contexts.

Control flow: tests build fake cluster objects and fake executors so they can assert Ceph command inputs without a real cluster. The msgr2 test intercepts `config assimilate-conf` and config removal/get commands. Telemetry tests mutate fake pods to verify node-count reporting. CephX status tests use fake controller-runtime clients to inspect status changes after retry-on-conflict updates.

State and persistence behavior: validates generated Ceph config content, Ceph config-key write attempts, status mutations on `CephCluster.Status.Cephx`, and fake Kubernetes Secret reads. No real Kubernetes or Ceph state is touched.

Dependencies and integration points: uses fake Kubernetes clientsets, fake controller-runtime client, Rook test helpers, mocked Ceph executor, INI parsing, Rook Ceph API types, and Ceph client test cluster info.

Risks: several tests depend on command argument positions and mocked outputs, which is appropriate for regressions but can be brittle during refactors. Some branches, like full local cluster orchestration and actual monitor/mgr/OSD startup, remain integration-level and are not covered here.

Test signals: broad helper-level coverage with meaningful command and status assertions. It complements `cephx_test.go`, which covers admin rotation in more detail.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/controller.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/controller.go

Purpose: wires the controller-runtime `CephCluster` controller, watches cluster-owned resources and relevant cluster-wide resources, performs reconcile entry/exit handling, and owns deletion gating/finalizer cleanup.

Important APIs and types: `ClusterController` stores shared context, rook image, cached cluster map, controller client, recorder, and operator manager context. `ReconcileCephCluster` is the reconcile adapter. `Add`, `newReconciler`, `add`, and `watchOwnedCoreObject` register watches. `isSecretRefFromCluster` identifies Ceph config secret references. `Reconcile` wraps `reconcile` with panic recovery and reporting. `reconcileDelete`, `reconcileCephCluster`, `requestClusterDelete`, `csiVolumesAllowForDeletion`, `checkPVPresentInCluster`, `removeFinalizers`, `removeFinalizer`, and `deleteOSDEncryptionKeyFromKMS` implement lifecycle operations.

Control flow: `add` creates the controller with optional `ROOK_RECONCILE_CONCURRENT_CLUSTERS`, watches `CephCluster`, owned Deployments/Services/Secrets/ConfigMaps, Nodes, referenced config Secrets, hotplug ConfigMaps unless disabled, and cluster ConfigMaps. `reconcile` sets clients on shared context, fetches the CR, adds a finalizer, handles deletion, respects `SkipReconcileLabelKey`, and delegates active reconciliation to `ClusterController.reconcileCephCluster`. Deletion sets a Deleting condition, blocks if dependent custom resources remain, optionally starts cleanup jobs, checks CSI PVs unless allowed, purges external artifacts or KMS OSD keys, removes cached cluster state, and removes mon/cluster finalizers.

State and persistence behavior: updates finalizers, status conditions, event recorder events, clusterMap entries, deletion-blocked condition reporting, mon disaster-protection finalizers, CephCluster finalizers, external-mode ConfigMaps/Secrets, and optionally KMS keys. It reads PersistentVolumes clusterID/driver attributes to gate deletion.

Dependencies and integration points: controller-runtime manager/client/cache/predicates, CSI Addons and Ceph CSI operator schemes, Rook controller/reporting helpers, mon/osd/csi/kms packages, Kubernetes fake or real clients, and predicates defined elsewhere in the package. It assumes one CephCluster per namespace when managing cached cluster instances and deletion.

Risks: deletion safety depends on complete dependent-kind enumeration and accurate PV `clusterID` attributes. `requestClusterDelete` may skip deletion if another cached cluster name exists in the namespace, matching the one-cluster-per-namespace rule. Cleanup jobs are launched in a goroutine with operator manager context while deletion continues. The shared `clusterd.Context.Client` is overwritten per reconcile, which is typical for this controller but worth noting with concurrent reconciles.

Test signals: `controller_test.go` covers deletion blocked/unblocked by dependents, finalizer removal, and skip-reconcile event behavior. It does not directly test controller watch registration, PV gating, external purge, or KMS deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/controller_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/controller_test.go

Purpose: validates key controller lifecycle behaviors: deletion blocking by dependent resources, finalizer removal, and skip-reconcile handling.

Important APIs and tests: `TestReconcileDeleteCephCluster` builds a deleting `CephCluster` and a dependent `CephBlockPool`, then calls `Reconcile`. `TestRemoveFinalizers` directly tests `removeFinalizer` for a `CephCluster` and mon Secret. `TestReconcileSkipsWhenSkipReconcileLabelSet` calls the internal `reconcile` method for a labeled cluster and checks the emitted event.

Control flow: the deletion test first expects a requeue and a deletion-blocked event/condition while the block pool exists. It then deletes the pool and reconciles again, expecting zero result and a non-blocking deletion condition. The finalizer test builds fake clients with objects containing finalizers and verifies they are cleared. The skip test verifies no reconcile work is done when the skip label exists after the finalizer is already present.

State and persistence behavior: fake controller-runtime clients persist CR status conditions and finalizer changes. The fake event recorder captures deletion-blocked and skipped events. No real cleanup jobs, PVs, or KMS interactions are executed.

Dependencies and integration points: uses Rook Ceph API scheme, CSI addons scheme, fake Kubernetes and Rook clients, API extension fake client, controller-runtime fake client, and Kubernetes event recorder.

Risks: deletion unblocked flow does not exercise cleanup policy, volume checks, external purge, or finalizer removal all the way to object deletion. Finalizer tests call the helper directly rather than through full reconcile. Skip behavior assumes the finalizer has already been added; the first reconcile for a newly created labeled object may still add the finalizer before later skipping.

Test signals: strong focused signals for dependent deletion safety and skip event emission, moderate coverage for finalizer utility behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/dependents.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/dependents.go

Purpose: discovers custom resources in a namespace that depend on a `CephCluster` and therefore should block cluster deletion until removed.

Important APIs and functions: `cephClusterDependentListKinds` enumerates list kinds for pools, mirrors, filesystems, object stores/users/zones/zonegroups/realms, NFS, clients, bucket topics/notifications, subvolume groups, and RADOS namespaces. `CephClusterDependents` lists each kind using an unstructured list and returns a `dependents.DependentList`. `listKindToSingularKind` trims the `List` suffix for display/reporting.

Control flow: for each configured list kind, it sets group/version/kind to the Rook Ceph API, calls the controller-runtime client in the target namespace, records list errors, and adds each object's name under the singular kind. After scanning all kinds, it aggregates any errors while still returning whatever dependents were found.

State and persistence behavior: read-only. It builds an in-memory dependent list and does not mutate Kubernetes objects or status directly; callers use the result to report deletion blocking.

Dependencies and integration points: uses `clusterd.Context.Client`, unstructured Kubernetes objects, Rook Ceph API scheme metadata, controller-runtime namespace filtering, Rook util aggregate errors, and `pkg/util/dependents`.

Risks: the list kind table is a deletion safety boundary. Missing a dependent CRD kind can allow cluster deletion while resources still exist. Some entries in the table are not suffixed with `List` (`CephBucketTopic`, `CephBucketNotification`, `CephFilesystemSubVolumeGroup`, `CephBlockPoolRadosNamespace`), so `listKindToSingularKind` returns the same string and correctness depends on controller-runtime accepting those kind names for list objects. Errors are aggregated but partial results can still be used by callers.

Test signals: `dependents_test.go` covers many listed kinds and namespace isolation, but error aggregation is noted as TODO and not currently exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/dependents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/dependents_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/dependents_test.go

Purpose: verifies that `CephClusterDependents` discovers dependent Rook Ceph custom resources by kind and namespace.

Important APIs and tests: `TestCephClusterDependents` creates a fake controller-runtime client with the Rook Ceph scheme and uses subtests for `CephBlockPool`, `CephRBDMirror`, `CephFilesystem`, `CephFilesystemMirror`, `CephObjectStore`, `CephObjectStoreUser`, `CephObjectZone`, `CephObjectZoneGroup`, `CephObjectRealm`, `CephNFS`, `CephClient`, `CephBucketTopic`, `CephBucketNotification`, and an all-types scenario.

Control flow: each subtest creates objects in the target namespace, calls `CephClusterDependents`, and asserts `PluralKinds` plus names from `OfKind`. The combined scenario also verifies that querying another namespace returns an empty dependent list.

State and persistence behavior: all state is in a fake client. No status or real Kubernetes resources are modified.

Dependencies and integration points: uses the Rook Ceph scheme, controller-runtime fake client, `clusterd.Context`, and `testify/assert`.

Risks: not every kind in `cephClusterDependentListKinds` appears to be fully asserted in the visible active tests; error-path testing is commented out because fake client list failures are not configured. Tests rely on fake client behavior for unstructured list kinds, which may differ from discovery behavior in a real API server when CRDs are absent or versioned differently.

Test signals: strong signal that common dependents block deletion and namespace filtering works; weak signal for aggregate error handling and newly added dependent kinds unless tests are updated with the list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/dependents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/config.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/config.go

Purpose: defines manager daemon keyring generation and dashboard port selection helpers used by the mgr cluster orchestrator.

Important APIs and types: constants include `minPortWithoutPrivileges` and the `keyringTemplate` for `mgr.<id>` caps. `mgrConfig` holds Kubernetes resource name, Ceph daemon ID, and data path map. `dashboardInternalPort`, `dashboardPublicPort`, and `dashboardDefaultPort` map CR dashboard settings to service/container ports. `generateKeyring` creates or rotates mgr CephX keys and stores the keyring Secret.

Control flow: dashboard public port defaults to HTTP or HTTPS default when unset; internal port falls back to the default if the public port is `<=1024` so the pod does not bind a privileged port. `generateKeyring` gets the keyring secret store, generates `mgr.<daemonID>` with mon/mds/osd caps, optionally rotates it if `Cluster.shouldRotateCephxKeys` is true, deletes legacy per-mgr secret names from older Rook versions, formats the keyring, and persists it through the secret store.

State and persistence behavior: writes or updates keyring Secrets and returns the secret resource version for deployment annotations. It may delete legacy Kubernetes Secrets named like the mgr resource. It does not update CephCluster status itself; `mgr.go` updates status after iterating mgrs.

Dependencies and integration points: uses `config/keyring` secret store, `config.DataPathMap`, Kubernetes CoreV1 Secrets, API error helpers, and mgr cluster state. It is called from `Cluster.Start` before deployment creation so the deployment template can include the key identifier annotation.

Risks: key rotation and deployment rollout are coupled through the returned resource version; failure to propagate it could leave pods using stale keys. Deleting legacy secrets is best-effort and logged on non-not-found errors. Port mapping must stay consistent with service creation in `spec.go` and dashboard tests.

Test signals: no direct tests in this file, but `dashboard_test.go` validates low/default dashboard port behavior through service generation, and mgr key rotation is indirectly covered through mgr start paths elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard.go

Purpose: manages Ceph mgr dashboard exposure and module configuration, including the Kubernetes Service, Ceph module enable/disable, monitor-store settings, self-signed TLS certificate, dashboard admin password Secret, and login credentials.

Important APIs and functions: `configureDashboardService` creates/updates or deletes the dashboard Service. `configureDashboardModules` enables/disables the Ceph dashboard module and performs initialization/config. `deleteManagerDaemonConfiguration` removes old per-daemon dashboard config keys. `configureDashboardModuleSettings` writes global dashboard settings. `initializeSecureDashboard`, `createSelfSignedCert`, `setLoginCredentials`, `getOrGenerateDashboardPassword`, `GeneratePassword`, `GenerateRandomBytes`, and `decodeSecret` handle secure dashboard setup.

Control flow: if dashboard is disabled, service is deleted and module disable is attempted. If enabled, the module is enabled, initialization waits briefly, a password Secret is fetched or generated, a self-signed cert is created when SSL is enabled, login credentials are applied with retrying Ceph dashboard commands, global settings are written to the mon store, stale per-daemon settings are removed once, and the dashboard module is restarted if cert or config changed.

State and persistence behavior: persists the `rook-ceph-dashboard-password` Secret owned by the cluster, creates/deletes a dashboard Service, writes mon-store config under `mgr/dashboard/*`, creates Ceph dashboard cert/config-key state, and creates/updates dashboard user credentials in Ceph. A package-level `removeMgrDaemonConfiguration` boolean controls one-time cleanup attempts across calls.

Dependencies and integration points: uses Ceph client module/config/dashboard commands, Rook config mon store, Kubernetes Services/Secrets, owner references, random crypto, temp password files, command retry helpers, and dashboard Service construction from `spec.go`.

Risks: dashboard initialization uses sleeps and retries because the module may not be immediately ready. `createSelfSignedCert` returns success with no error after retry exhaustion, which avoids blocking reconcile but can leave SSL not fully initialized. Passwords are written to temp files and removed with deferred cleanup; logging avoids printing the password except secret-sourced values could be exposed by lower-level debug if changed. The package-level per-daemon cleanup flag is shared process-wide, not per cluster.

Test signals: `dashboard_test.go` covers password generation/reuse, service port mapping including privileged public ports, enable/disable module counts, self-signed cert retry on invalid-argument readiness and wrapped deadline exceeded, and service deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard_test.go

Purpose: tests dashboard password generation, password Secret persistence, dashboard Service/module behavior, and self-signed certificate retry handling.

Important APIs and tests: `TestGeneratePassword` validates requested password lengths. `TestGetOrGeneratePassword` verifies missing Secret creation, owner-backed storage, decode, and reuse. `TestStartSecureDashboard` mocks Ceph commands, drives `configureDashboardService` and `configureDashboardModules`, checks module enable/disable counts, retry count, service port/targetPort behavior, and service deletion. `TestCreateSelfSignedCertRetriesWrappedDeadlineExceeded` validates retry behavior when cert creation returns wrapped `context.DeadlineExceeded`.

Control flow: the secure dashboard test sets dashboard wait time to zero, uses a mock executor to simulate module readiness failures via `EINVAL`, and toggles dashboard enabled/disabled plus port values. It checks that public port 443 maps to internal 8443, port 1025 maps directly, and port 0 defaults to 8443 under SSL.

State and persistence behavior: fake Kubernetes clientset stores the dashboard password Secret and dashboard Service. Mocked Ceph commands represent Ceph module and dashboard state; no real Ceph state is changed.

Dependencies and integration points: uses Rook test clientsets, fake Ceph executor, `cephclient.ClusterInfo`, Rook Ceph API types, Kubernetes API errors, and `testify`.

Risks: tests assert command counts rather than full argument sequences for all dashboard commands, so some command argument regressions could slip. The global `dashboardInitWaitTime` is mutated and not restored in the visible test, which can affect same-package tests if order-dependent.

Test signals: good coverage for dashboard lifecycle basics, port mapping, password persistence, and retry semantics; limited coverage for mon-store setting keys and per-daemon config cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain.go

Purpose: manages the mgr PodDisruptionBudget so clusters with multiple mgrs can tolerate voluntary disruptions while preserving at least one available mgr.

Important APIs and functions: `mgrPDBName` is `rook-ceph-mgr-pdb`. `reconcileMgrPDB` creates or updates a `policy/v1` PDB with selector `app=rook-ceph-mgr` and `maxUnavailable=1`. `deleteMgrPDB` removes the PDB when not needed.

Control flow: `mgr.go` calls `reconcileMgrPDB` when desired mgr count is greater than one and `deleteMgrPDB` otherwise. The reconcile helper uses controller-runtime `CreateOrUpdate` with a mutate function that replaces the PDB spec. Delete first GETs the PDB and ignores not-found errors, logging other get/delete errors.

State and persistence behavior: creates, updates, or deletes one namespaced PDB. It does not inspect cluster disruption-management settings directly in this file; caller policy determines whether and when it is invoked.

Dependencies and integration points: uses controller-runtime client, Kubernetes policy/v1 PDB, `k8sutil.AppAttr`, API errors, and the mgr cluster's namespace/context.

Risks: selector is broad for all mgr pods by app label and assumes all mgr pods in the namespace belong to the cluster. The mutate function overwrites the PDB spec, which is correct for reconciliation but will remove out-of-band edits. Delete logs errors without returning, so failure to delete does not fail mgr reconcile.

Test signals: `drain_test.go` covers create/update idempotence and deletion with fake clients.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain_test.go

Purpose: verifies mgr PDB reconciliation and deletion.

Important APIs and tests: `createFakeCluster` builds a mgr `Cluster` with controller-runtime fake client, Kubernetes fake clientset, policy/v1 scheme, owner info, and a fake Kubernetes version. `TestReconcileMgrPDB` calls `reconcileMgrPDB`, fetches the PDB, asserts `maxUnavailable=1`, and calls reconcile again to verify idempotent update. `TestDeleteMgrPDB` creates the PDB, calls `deleteMgrPDB`, and expects a later GET to fail.

Control flow: tests operate directly on mgr `Cluster` methods rather than through `Cluster.Start`, so they isolate PDB behavior from deployment creation and mgr count decisions.

State and persistence behavior: fake controller-runtime client stores the PDB. No status or external state is modified.

Dependencies and integration points: uses Rook client scheme, fake controller-runtime client, Rook test clientset, Kubernetes policy/v1 types, and `testify/assert`.

Risks: the test case name says "1 mgr" even though direct reconciliation creates the PDB regardless of count; the caller's count-based decision is not tested here. Delete error logging paths and not-found behavior are not asserted.

Test signals: solid unit signal for PDB object shape and delete behavior, limited signal for integration with mgr replica counts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr.go -->
## sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr.go

Purpose: orchestrates Ceph manager daemon deployment, keyring generation/rotation, service reconciliation, mgr role labels for active/standby routing, optional ServiceMonitor creation, and asynchronous mgr module configuration.

Important APIs and types: `Cluster` stores context, cluster info, spec, rook version, exit-code parser, and CephX rotation flag. `New` constructs the mgr cluster. `getReplicas` and `getDaemonIDs` determine daemon IDs. `Start` is the main orchestration method. Supporting methods include `removeExtraMgrs`, `SetMgrRoleLabel`, `GetActiveMgr`, `reconcileServices`, `updateServiceSelectors`, `configureModules`, `configurePrometheusModule`, `restartMgrModule`, `enableBalancerModule`, `configureMgrModules`, `moduleMeetsMinVersion`, `wellKnownModule`, `EnableServiceMonitor`, `applyMonitoringLabels`, `shouldRotateMgrKeys`, and `updateMgrCephxStatus`.

Control flow: `Start` validates mgr pod memory, calculates daemon IDs, gets skip-reconcile daemon labels, determines whether mgr CephX keys should rotate, then for each daemon generates or rotates a keyring, builds a Deployment, annotates it with the key secret resource version, stores last-applied annotation, creates or updates the Deployment unless skipped, and waits for newly created deployments. It then updates mgr CephX status, disables insecure global IDs on clean deployment, removes extra mgr deployments, reconciles or deletes the PDB based on desired count, reconciles services, and launches module configuration goroutines.

State and persistence behavior: creates/updates keyring Secrets, Deployments, Services, ServiceMonitor, PDB, CephCluster CephX status, service selectors, and Ceph mgr module/config state. `SetMgrRoleLabel` updates pod labels to `mgr_role=active|standby` and then reconciles services so selectors route to active mgr pods. Module configuration is persisted in Ceph via mgr module enable/disable and mon-store settings.

Dependencies and integration points: depends on deployment and service builders in other mgr files, `mon.UpdateCephDeploymentAndWait`, keyring status helpers, Ceph client module/stat APIs, config mon store, controller helpers for memory and skip labels, Prometheus operator types, controller-runtime client, Kubernetes clientset, and reporting status update. It is invoked from `cluster.go` after mons and before OSDs.

Risks: module configuration is asynchronous and failures only log, so reconcile may appear successful while dashboard/prometheus/custom modules fail later. Skipped mgr daemons still have keyrings generated before the skip check. Service selector migration removes legacy daemon ID selectors and adds `mgr_role=active`, so pod label update failures can affect dashboard/metrics routing. The one-cluster-per-namespace assumption appears in selectors using namespace plus app labels.

Test signals: this file's behavior is covered indirectly by dashboard and drain tests plus tests in neighboring mgr files not in this work item. There is no direct comprehensive test here for `Start`, extra mgr removal, skip reconcile handling, ServiceMonitor labeling, or async module failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr.go -->
