# subset-b-000451 research

Grouped research for Rook Ceph OSD operator files under `sources/control-plane/rook/pkg/operator/ceph/cluster/osd`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create.go

## Purpose
This file owns the creation side of OSD reconciliation. It starts OSD prepare Jobs for node-backed and PVC-backed OSDs, tracks which status ConfigMaps are expected from those Jobs, and creates OSD Deployments from completed orchestration status. It is the bridge between storage specification parsing, provisioning Jobs, and daemon Deployment creation.

## Important APIs, Types, and Functions
`createConfig` stores the current reconcile's provisioning config, expected status ConfigMaps, completed status ConfigMaps, and existing OSD deployments. `newCreateConfig()`, `progress()`, and `doneCreating()` are lightweight lifecycle helpers. `createNewOSDsFromStatus()` is the key callback for status ConfigMap results. It ignores stale or already processed ConfigMaps, skips OSD IDs whose Deployments already exist, initializes first-deploy cephx status with `keyring.UpdatedCephxStatus()`, and dispatches to node or PVC daemon creation.

`startProvisioningOverPVCs()` prepares `StorageClassDeviceSet` PVCs, skips PVCs with existing OSD Deployments, handles migration re-preparation, creates dmcrypt keys and KMS secrets for encrypted PVC OSDs, writes starting orchestration status, and launches prepare Jobs. `startProvisioningOverNodes()` resolves valid nodes, enforces `dataDirHostPath`, derives node storage settings and device class, writes starting status, and launches prepare Jobs. `runPrepareJob()` delegates Job construction to `makeJob()` and runs it with `k8sutil.RunReplaceableJob()`. `createDaemonOnPVC()` and `createDaemonOnNode()` build and create OSD Deployments, update CephCluster progressing status, and perform a second Deployment update when multicluster service export requires external IP arguments.

## Control Flow
The file is used from `Cluster.Start()`: PVC provisioning runs first, node provisioning runs second, both return sets of status ConfigMap names, and `createConfig` processes watcher results through `updateAndCreateOSDs()`. Prepare Job failures are accumulated as `provisionErrors` without necessarily halting all provisioning. Context cancellation during loops returns immediately to stop reconcile.

## State and Persistence
State is persisted in Kubernetes objects: PVC-backed encryption material is stored through the configured KMS using the PVC claim name as key; orchestration progress is stored in status ConfigMaps; prepare Jobs are Kubernetes Jobs; successful OSDs become Deployments. `createConfig.finishedStatusConfigMaps` is in-memory per reconcile and prevents duplicate processing of a status object.

## Dependencies and Integration Points
The code depends on Ceph CRD storage specs, `deviceSet.go` for PVC source synthesis, `osd.go` for Deployment builders, KMS support from `pkg/daemon/ceph/osd/kms`, Kubernetes helper utilities, and Cephx keyring status helpers. It integrates with condition updates through the overridable `updateConditionFunc`, which is stubbed in tests.

## Risks and Edge Cases
Important risks are stale status ConfigMaps from old reconciles, accidental encryption key overwrite, partial provisioning when one node or PVC fails, device-class conflicts on nodes, and multicluster service requiring Deployment mutation after initial create. PVC migration uses a substring match against `migrateOSD.BlockPath`, which is pragmatic but depends on stable block-path naming. Node provisioning mutates `c.spec.Storage.Nodes` when `UseAllNodes` is set, so callers should treat the cluster instance as reconcile-scoped.

## Test Signals
`create_test.go` covers stale and duplicate status handling, skipping existing OSD IDs, error aggregation, PVC provisioning with missing templates, node provisioning with empty `dataDirHostPath`, `UseAllNodes`, individual node selection, prepare Job failure, and device-class resolution from node labels. `integration_test.go` exercises this file through repeated full `Cluster.Start()` reconciles, cancellation, failures, and cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create_test.go

## Purpose
This test file validates the OSD creation and prepare-job launch paths in `create.go`. It focuses on deterministic behavior around status ConfigMaps, node/PVC provisioning gates, prepare Job failures, and device-class selection.

## Important APIs, Types, and Helpers
`Test_createNewOSDsFromStatus` overrides `createDaemonOnNodeFunc` and `createDaemonOnPVCFunc` to record requested OSD IDs and inject failures. It constructs a `createConfig` with expected status ConfigMaps and an `existenceList` representing existing Deployments. `Test_startProvisioningOverPVCs` uses a complex fake clientset with generated-name support to verify PVC prepare orchestration and status ConfigMap creation. `Test_startProvisioningOverNodes` uses fake nodes and Kubernetes reactors to simulate successful and failed Job creation. `Test_startProvisioningOverNodes_deviceClassNodeLabel` creates nodes with `osd.rook.io/device-class` labels to validate conflict and fallback rules. `newDummyPVC()` creates block-mode PVC templates for storage class device set tests.

## Control Flow Covered
The tests drive `createNewOSDsFromStatus()` through node-backed and PVC-backed branches. They assert that only ConfigMaps created for the current reconcile are processed, already existing OSD IDs are skipped, failed daemon creation is recorded while later OSDs still get attempted, and completed status ConfigMaps are marked finished. PVC provisioning tests verify no-op behavior with empty specs or zero counts, successful status ConfigMap creation for two PVCs, idempotent repeat reconcile before daemon creation, and error reporting for missing volume claim templates. Node tests verify no-op storage specs, hard failure accumulation for missing `dataDirHostPath`, expansion of `UseAllNodes`, warning-compatible behavior when `UseAllNodes` and explicit nodes coexist, individual node selection, no-node behavior, and per-node Job creation failure isolation.

## State and Persistence Behavior
The test state is entirely fake Kubernetes API state: ConfigMaps represent orchestration status, Jobs represent prepare work, fake nodes drive valid-node selection, and fake PVCs are generated for storage class device sets. Global function variables are restored with defers, which is important because package-level overrides affect other tests.

## Dependencies and Integration Points
The tests depend on Rook test helpers (`test.New`, `test.NewComplexClientset`), fake Kubernetes reactors, `cephclient.ClusterInfo`, and Ceph version fixtures. They indirectly exercise `makeJob()`, status ConfigMap helpers, and node validation helpers even though those helpers live outside this file.

## Risks and Gaps
The tests are strong for control-flow branching but do not deeply inspect generated Job pod specs in the main provisioning cases; there is an inline TODO noting this. KMS/encryption setup in `startProvisioningOverPVCs()` is not covered here. Since tests mutate package-level function variables, missing restoration would cause cross-test contamination, but defers handle the current overrides.

## Test Signals
The file itself is the signal for create-path behavior. It provides regression coverage for idempotency, stale ConfigMap filtering, partial failures, and new node-label device-class behavior, which are high-risk areas in OSD reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceSet.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceSet.go

## Purpose
This file converts `StorageClassDeviceSet` entries from the CephCluster spec into concrete PVCs and internal `deviceSet` records used by OSD preparation and Deployment generation. It is responsible for idempotent PVC creation, backward-compatible PVC identity, PVC expansion waiting, and carrying storage-class-derived properties into OSD provisioning.

## Important APIs, Types, and Functions
`deviceSet` is the processed representation of one OSD's PVC sources and settings: data/metadata/wal PVC sources, crush device class, initial weight, primary affinity, resource requests, placement, portability, scheduler, tuning flags, and encryption. `PrepareStorageClassDeviceSets()` exposes the internal preparation path for tests. `prepareStorageClassDeviceSets()` lists existing PVCs, validates prepare OSD memory and volume templates, preserves existing PVC indexes, creates missing PVC groups, and waits for pending PVC expansions.

`createDeviceSetPVCsForIndex()` creates or reuses data, metadata, and wal PVCs for one set index. It handles blank template names as backward-compatible data volumes, rejects duplicate template names, extracts crush annotations, and returns a populated `deviceSet`. `createDeviceSetPVC()` resolves old and new PVC IDs, sets owner references, expands existing PVCs if size changed, records resize state, or creates new PVCs. `makeDeviceSetPVC()` builds generated-name PVCs with Rook labels plus user-provided labels. `GetExistingPVCs()` returns PVCs keyed by device-set PVC ID and a per-device-set set of existing indexes. `deviceSetPVCID()` normalizes spaces in template names and dots in device-set names. `createValidImageVersionLabel()` sanitizes image strings for Kubernetes label values. `waitForPvcToExpandWithTimeout()` and `checkAllPvcResize()` poll PVC spec/status capacity convergence.

## Control Flow
For each device set, existing PVC indexes are processed first so missing companion PVCs can be recreated. New indexes begin after the highest existing ID to avoid reusing old OSD identities. The desired count controls how many new PVC groups are created, but extra existing PVCs are not deleted here.

## State and Persistence
Persistent state is Kubernetes PVCs. Labels `ceph.rook.io/DeviceSet`, `ceph.rook.io/setIndex`, and `ceph.rook.io/DeviceSetPVCId` form the reconciliation identity. Image-at-creation labels persist Ceph and Rook image versions. Owner references connect PVCs to the CephCluster owner. PVC resize state is transient in `pvcResizeMap`, with actual progress observed from the Kubernetes API.

## Dependencies and Integration Points
The file integrates with CephCluster storage spec types, controller memory validation, Kubernetes client-go and controller-runtime clients, Rook label helpers in `labels.go`, and OSD provisioning in `create.go`/`osd.go`. It uses Kubernetes resource quantities for resize comparisons.

## Risks and Edge Cases
PVC identity must remain backward compatible with legacy IDs while supporting template-name-specific IDs. Generated names reduce OSD ID reuse risk but mean tests and controllers must rely on labels, not exact names. Resize waiting can delay reconciliation until timeout. Duplicate template names and invalid existing indexes are accumulated as provision errors. The resize equality check compares desired spec size and status capacity, so delayed CSI status updates can leave OSDs needing manual restart.

## Test Signals
`deviceset_test.go` covers blank and explicit template names, scheduler propagation, image labels, holes in PVC sets, scale-down/scale-up index behavior, crush annotation extraction, PVC ID normalization, valid image label sanitization, and PVC resize confirmation logic.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceSet.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceset_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceset_test.go

## Purpose
This file tests `deviceSet.go`, especially idempotent PVC creation for `StorageClassDeviceSet`, naming compatibility, generated PVC labels, storage annotation propagation, and PVC resize checking.

## Important APIs, Types, and Helpers
`TestPrepareDeviceSets` and `testPrepareDeviceSets` validate both blank and explicit volume claim template names. `TestPrepareDeviceSetWithHolesInPVCs` uses a fake PVC reactor to assign generated names, then exercises multi-template data/metadata/wal PVC groups through scale-up, repeat reconcile, missing companion PVC recreation, scale-down, and scale-up with new indexes. `assertPVCExists()` verifies expected generated resources. `testVolumeClaim()` provides minimal templates. `TestPrepareDeviceSetsWithCrushParams` validates `crushDeviceClass`, `crushInitialWeight`, and `crushPrimaryAffinity` annotation extraction. `TestPVCName` covers `deviceSetPVCID()` normalization. `TestCreateValidImageVersionLabel` covers image-label sanitization. `TestCheckAllPvcResize` uses a controller-runtime fake client and status subresource support to validate resize bookkeeping.

## Control Flow Covered
The tests prove that a single unnamed template is treated as data, that generated names include the default or explicit template name, that device set count drives group creation, and that existing labeled PVC indexes are reused before new indexes are allocated. The holes test shows an important behavior: deleting one companion PVC in an existing index causes the missing PVC to be recreated, but reducing the count prevents deleted lower-index PVC groups from being recreated if enough other indexes already satisfy the count. Scaling back up then allocates a higher new index instead of reusing a deleted one.

## State and Persistence Behavior
All state is fake Kubernetes PVC state. Labels are the primary source of identity for `GetExistingPVCs()`. Generated names are simulated by a reactor because the fake client does not automatically behave exactly like the apiserver for this test's purposes. Resize state is represented by an in-memory `pvcResizeMap` and fake PVC spec/status resource quantities.

## Dependencies and Integration Points
The tests depend on Rook's fake clientsets, client-go reactors, controller-runtime fake client, Kubernetes resource quantities, and the CephCluster storage API. They indirectly validate `labels.go` because PVC label keys and image labels are asserted.

## Risks and Gaps
The tests exercise PVC object creation well, but do not run real CSI resize behavior or validate asynchronous wait timeout timing. They do not cover memory validation failure in this file directly, although create tests cover provisioning error paths. The holes test encodes nuanced index behavior that future refactors must preserve to avoid unintended OSD identity reuse.

## Test Signals
This is strong regression coverage for source-tree state alignment between CephCluster storage specs and persistent PVCs. It is especially useful for changes to PVC naming, label keys, generated names, and scale behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs.go

## Purpose
This file centralizes environment variable construction for OSD prepare, activate, daemon, and key-rotation containers. It defines the env var names that form the contract between the Rook operator, Rook OSD entrypoints, `ceph-volume`, KMS support, and Kubernetes-injected runtime data.

## Important APIs, Types, and Functions
Constants define Rook-specific variables such as `ROOK_OSD_DATABASE_SIZE`, `ROOK_OSDS_PER_DEVICE`, `ROOK_ENCRYPTED_DEVICE`, `ROOK_PVC_NAME`, `ROOK_PVC_BACKED_OSD`, `ROOK_BLOCK_PATH`, `ROOK_CV_MODE`, `ROOK_OSD_CRUSH_DEVICE_CLASS`, `ROOK_REPLACE_OSD`, and `ROOK_CRUSHMAP_ROOT`. `CephVolumeEncryptedKeyEnvVarName` preserves the hard-coded `ceph-volume` dmcrypt variable.

`Cluster.getConfigEnvVars()` builds common env vars for prepare and daemon contexts: node name, cluster UID/name, pod IPs, namespace, monitor endpoint, config directory, config override, node name, crush root, CRUSH host hint, ceph-volume variables, and optional store-config variables. In prepare mode it adds the Ceph username, FSID from `rook-ceph-mon`, and OSD store type. It hides the CRUSH hostname for non-portable PVC prepare pods until the pod's node is known.

Helper constructors return individual `v1.EnvVar` values for data devices, filters, metadata/wal devices, PVC flags, wipe behavior, debug logging, block path, ceph-volume mode, LV-backed PV, crush class, store type, replacement OSD ID, initial weight, encryption, and PVC name. `cephVolumeEnvVar()` returns the ceph-volume runtime contract (`CEPH_VOLUME_DEBUG`, `CEPH_VOLUME_SKIP_RESTORECON`, `DM_DISABLE_UDEV`). `osdActivateEnvVar()` adds monitor host and `CEPH_ARGS`. `getEnvFromSources()` includes an optional `rook-ceph-osd-env-override` ConfigMap. `getTcmallocMaxTotalThreadCacheBytes()` reads an explicit value or parses `/etc/sysconfig/ceph` with `ini`.

## Control Flow
Callers compose helper outputs into pod specs. `getConfigEnvVars()` branches on prepare mode and on non-zero store config fields, leaving absent settings unset instead of adding empty env vars. TCMalloc lookup falls back to an empty value if the packaged config file cannot be read.

## State and Persistence
This file does not persist state itself, but env vars it creates become part of Job, Deployment, and CronJob pod specs. Those pod specs preserve OSD identity, block device paths, encryption flags, and activation details across reconciles and upgrades.

## Dependencies and Integration Points
It integrates with Ceph monitor env helpers, Kubernetes downward API helpers, Ceph client crush-root derivation, and `gopkg.in/ini.v1`. It is consumed by prepare job construction, daemon deployment construction, activation init containers, and key rotation jobs.

## Risks and Edge Cases
Env var names are compatibility-sensitive because older Deployments are parsed by `getOSDInfo()`. Changing names can break upgrades or migration. Optional override ConfigMap use is intentionally non-fatal. `getTcmallocMaxTotalThreadCacheBytesFromFile()` silently returns empty on parse/read failure, which avoids blocking pods but can hide packaging problems.

## Test Signals
`envs_test.go` validates ceph-volume env ordering/content, activation env additions, explicit TCMalloc override, missing file behavior, empty file behavior, and sysconfig parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs_test.go

## Purpose
This file tests the stable environment variable helpers from `envs.go`, with emphasis on ceph-volume defaults, activation monitor wiring, and TCMalloc configuration lookup.

## Important APIs, Types, and Helpers
The `sysconfig` byte slice models `/etc/sysconfig/ceph` content containing `TCMALLOC_MAX_TOTAL_THREAD_CACHE_BYTES=134217728`. `TestCephVolumeEnvVar` checks the three ceph-volume env vars. `TestOsdActivateEnvVar` verifies that activation env vars include ceph-volume settings plus `ROOK_CEPH_MON_HOST` and `CEPH_ARGS=-m $(ROOK_CEPH_MON_HOST)`. `TestGetTcmallocMaxTotalThreadCacheBytes` exercises no-file, empty-file, explicit argument, and parsed-file behavior by redirecting the package global `cephEnvConfigFile` to a temporary file.

## Control Flow Covered
The TCMalloc test covers the branch where no explicit value is provided and file loading fails, the branch where file loading succeeds but no key exists, the branch where an explicit value bypasses file parsing, and the branch where the key is found in sysconfig. The ceph-volume and activation tests assert helper output positionally, which also protects callers that may rely on deterministic env order in generated pod specs or snapshot comparisons.

## State and Persistence Behavior
The tests do not use Kubernetes state. They mutate the package global `cephEnvConfigFile` to point to a temporary file. The temp file is removed with defer, but the global is not reset in this file, so test isolation relies on package test ordering not depending on the default path afterward.

## Dependencies and Integration Points
The tests use only the standard library and `testify/assert`. They indirectly protect pod-spec consumers in create, deployment, activation, and key-rotation code by ensuring shared env helpers do not change unexpectedly.

## Risks and Gaps
There appears to be a minor assertion typo: the `DM_DISABLE_UDEV` value checks `cvEnv[1].Value` and `osdActivateEnv[1].Value` instead of index 2. The expected value is still `"1"`, so the test passes while not directly asserting the third variable's value. Broader `getConfigEnvVars()` behavior is not covered here, including prepare-mode FSID, crush-root, non-portable PVC hostname hiding, and store-config optional env vars.

## Test Signals
The file is a focused regression signal for low-level env helper contracts. Its coverage is narrow but important because these variables are shared across OSD provisioning, activation, and maintenance jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health.go

## Purpose
This file implements periodic OSD health monitoring. It checks Ceph OSD dump state, optionally removes OSD Deployments that are out and safe to destroy, and periodically applies `require-osd-release` once all OSD daemons converge on one Ceph release.

## Important APIs, Types, and Functions
`OSDHealthMonitor` stores Kubernetes/Ceph context, cluster info, the removal policy `removeOSDsIfOUTAndSafeToRemove`, the health interval, and `lastRequireOSDRelease` cache. `NewOSDHealthMonitor()` applies the default 60 second interval or a user-specified OSD health check interval. `Start()` runs until the cluster health context is canceled or the monitoring routine map no longer contains the daemon key. `Update()` changes the removal policy.

`checkOSDHealth()` calls `checkOSDDump()` and then `checkRequireOSDRelease()`. `checkRequireOSDRelease()` reads all Ceph daemon versions, requires exactly one OSD version entry, extracts the release name, skips if it matches the cached value, and calls `client.EnableReleaseOSDFunctionality()`. `checkOSDDump()` reads `ceph osd dump`, iterates OSD status, skips healthy `up` OSDs, and when an OSD is both down and out, calls removal logic if enabled. `removeOSDDeploymentIfSafeToDestroy()` looks up the Deployment by `ceph-osd-id`, checks `ceph osd safe-to-destroy`, waits a one-hour grace time from Deployment creation, and deletes the Deployment.

## Control Flow
The monitor runs as a long-lived goroutine controlled by `monitoringRoutines` and `ClusterHealth.InternalCtx`. Errors from health checks are logged and retried rather than terminating monitoring. OSD deletion requires multiple gates: down, out, removal feature enabled, Deployment exists, Ceph reports safe-to-destroy, and the grace period elapsed.

## State and Persistence
Persistent state affected by this file is OSD Deployment deletion and Ceph's require-osd-release setting. `lastRequireOSDRelease` is in-memory and prevents redundant Ceph commands during one monitor lifetime. The grace-time decision uses Deployment creation timestamps from Kubernetes.

## Dependencies and Integration Points
The code depends on Ceph client commands for OSD dump, safe-to-destroy, daemon versions, and release enablement. It integrates with Rook controller monitoring routines, Kubernetes Deployment helpers, and Ceph version parsing.

## Risks and Edge Cases
Deletion safety relies on accurate Ceph safe-to-destroy output and Deployment timestamps. If versions never converge, require-osd-release is not applied here, but reconcile also has a one-shot path in `applyUpgradeOSDFunctionality()`. The monitor logs and continues on many errors, which is resilient but can delay cleanup or release enablement indefinitely if errors persist.

## Test Signals
`health_test.go` covers down/out safe-to-destroy Deployment deletion, monitor startup/cancel behavior, default and custom intervals, and all major `checkRequireOSDRelease()` branches including convergence, cache skip, mixed versions, version query error, and enable failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health_test.go

## Purpose
This file tests OSD health monitoring behavior in `health.go`: deletion of safe-to-destroy out OSDs, monitor lifecycle setup, interval selection, and periodic require-osd-release convergence logic.

## Important APIs, Types, and Helpers
`TestOSDHealthCheck` uses a mock Ceph executor returning an OSD dump with osd.0 down/out and safe-to-destroy output. It creates a fake Deployment with `ceph-osd-id=0`, runs `checkOSDDump()`, and asserts the Deployment is deleted. `TestMonitorStart` creates a `sync.Map` entry with `ClusterHealth`, starts the monitor goroutine, and cancels the internal context. `TestNewOSDHealthMonitor` compares default and custom interval monitor structs. `TestCheckRequireOSDRelease` uses subtests with mock executor responses for `ceph versions` and `ceph osd require-osd-release`.

## Control Flow Covered
The deletion test covers status parsing, safe-to-destroy command invocation, and Kubernetes Deployment deletion. It uses the default zero creation timestamp, which is older than the one-hour grace time, so deletion proceeds. The require-release tests cover the happy path where a single OSD version maps to `squid`, the cached-release skip path, mixed-version early return, version query failure, and enable failure without cache update.

## State and Persistence Behavior
Fake Kubernetes Deployments represent persistent OSD daemons. The mock executor count confirms Ceph calls are made. `lastRequireOSDRelease` is inspected as in-memory monitor state. The tests do not persist Ceph state; command success is inferred from executor calls and cache changes.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, `exectest.MockExecutor`, Ceph client command wrappers, Kubernetes Deployment labels, and controller health structs. It provides integration-like coverage across monitor logic, Kubernetes helpers, and Ceph command parsing.

## Risks and Gaps
The grace-period branch is only covered through an already-old timestamp; there is no test that a newly created Deployment is retained. `Start()` is only smoke-tested and does not assert map deletion after cancel. Error handling in `checkOSDDump()` for malformed OSD IDs or command failures is not deeply asserted.

## Test Signals
The tests give strong signals for destructive behavior and require-release idempotency. They are especially valuable because health monitoring runs outside the main reconcile loop and can delete Kubernetes objects asynchronously.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/integration_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/integration_test.go

## Purpose
This file is an end-to-end unit integration test for OSD create and update reconciliation. It drives `Cluster.Start()` through initial provisioning, no-op updates, scale-up, cancellation and resume, status failures, Deployment update failures, Deployment creation failures, malformed device sets, and dangling ConfigMap cleanup.

## Important APIs, Types, and Helpers
`TestOSDIntegration` wraps `testOSDIntegration()` in a timeout and shortens OSD update ticker durations. `testOSDIntegration()` builds a fake Kubernetes environment with ready nodes, complex Job reactors, ConfigMap watch reactors, Deployment reactors, fake CephCluster runtime object, controller-runtime fake client, and a mock Ceph executor. The test stubs `updateConditionFunc` because the fake environment does not include the full Rook client path.

`osdIntegrationTestExecutor()` handles Ceph commands used by the reconcile path: auth key creation, `osd ok-to-stop`, `osd ls`, `osd tree`, device class lookups, device class list, `osd df`, and `versions`. `osdIDGenerator` provides deterministic OSD IDs per named status resource. `newDummyStorageClassDeviceSet()` creates simple PVC-backed device sets. `waitForNumConfigMaps()`, `setStatusConfigMapToCompleted()`, `setStatusConfigMapToFailed()`, and `updateStatusConfigmap()` simulate prepare Job result updates.

## Control Flow Covered
The test starts with a spec that creates six node OSDs, six portable PVC OSDs, and three non-portable PVC OSDs. It then reconciles with no spec changes, increases node and PVC OSD counts, cancels mid-reconcile after some status ConfigMaps complete, resumes, injects failed status ConfigMaps, recovers, injects Deployment update failures, recovers, injects Deployment creation failures, recovers, adds a malformed device set, fixes it, and finally verifies dangling status ConfigMaps are removed.

## State and Persistence Behavior
State is represented by fake Kubernetes ConfigMaps, PVCs, Jobs, Deployments, watches, and CephCluster status updates. Deployment reactors mark Deployments ready immediately and record create/update counts. Status ConfigMaps hold serialized `OrchestrationStatus` JSON and are the synchronization point between prepare Jobs and daemon creation. The fake Ceph executor derives some command outputs from current fake Deployment state.

## Dependencies and Integration Points
The test crosses `create.go`, `deviceSet.go`, `osd.go`, update logic in neighboring files, status ConfigMap helpers, Deployment generation, and Ceph command wrappers. It also relies on Kubernetes fake reactors to simulate apiserver behavior that ordinary fake clients do not provide.

## Risks and Edge Cases
The test is intentionally timing-sensitive, with goroutines, watch events, and a timeout wrapper. It reduces ticker durations to keep runtime small. Because fake Deployments are marked ready immediately, it does not validate real rollout timing. The TODO near the top notes strategic merge patch noise in unit tests around missing merge keys.

## Test Signals
This is the strongest broad regression signal for the OSD reconcile lifecycle. It proves idempotent repeated reconciles, partial failure recovery, cancellation recovery, update/create interplay, and cleanup of stale orchestration artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation.go

## Purpose
This file reconciles Kubernetes CronJobs that periodically rotate encryption keys for encrypted PVC-backed OSDs. It builds the rotation container, pod template, CronJob object, placement rules, and cleanup behavior when key rotation is disabled.

## Important APIs, Types, and Functions
`keyRotationCronJobName()` formats stable per-OSD CronJob names. `applyKeyRotationPlacement()` removes topology spread constraints and pod anti-affinity, then installs required pod affinity matching the target OSD labels on the hostname topology key. This forces the rotation job onto the same node as the OSD pod.

`getKeyRotationContainer()` builds a privileged root container using the operator image (`c.rookVersion`) with args `key-management rotate-key <pvc> <devices...>`, debug logging, Ceph version, KMS env vars, ceph-volume config env vars, env-from overrides, resources, and security context dropping `NET_RAW`. `getKeyRotationPodTemplateSpec()` mounts `/dev`, `/run/udev`, and the OSD bridge host path under the cluster data dir; adds block, metadata, and wal devices when present; adds Vault TLS volumes when configured; applies host networking or Multus; applies key-rotation annotations/labels; applies global and device-set placement; applies same-node affinity; enables HostIPC for cryptsetup/udev synchronization; and removes duplicate env vars.

`makeKeyRotationCronJob()` wraps the pod template in a `batch.CronJob` with `ForbidConcurrent`, default `@weekly` schedule, and OSD resources. `reconcileKeyRotationCronJob()` deletes all key-rotation CronJobs when disabled. When enabled, it lists PVC-backed OSD Deployments, extracts OSD info and PVC name, rebuilds OSD props from device sets, skips unencrypted OSDs, creates a CronJob, sets the OSD Deployment as owner, and create-or-updates it.

## Control Flow
The reconcile path is all-or-error: list failures, bad OSD info, missing PVC label, config generation failure, owner-reference failure, or create/update failure return errors. Unencrypted OSDs are skipped. Disabled reconciliation performs collection deletion by app label and ignores not found.

## State and Persistence
Persistent state is Kubernetes CronJobs owned by OSD Deployments. Pod template labels, annotations, volumes, affinity, and schedule encode rotation behavior. The job uses mounted host data and block devices; secrets are accessed through KMS env/config integration, not by this file directly.

## Dependencies and Integration Points
The file depends on env helpers, KMS helpers, Kubernetes batch/core APIs, Rook placement/annotation/label APIs, Multus helpers, Deployment-derived OSD info from `osd.go`, PVC labels from `labels.go`, and encryption path helpers from neighboring OSD code.

## Risks and Edge Cases
Same-node placement is critical; incorrect labels or affinity can schedule rotation away from the device. The host path is built from `DataDirHostPath`, namespace, PVC name, and OSD ID, so layout changes affect rotation. Only PVC-backed encrypted OSDs are reconciled. Deleting all CronJobs when disabled uses an app label, so label drift can leave orphaned jobs.

## Test Signals
`key_rotation_test.go` covers name formatting and placement mutation. Full container, pod template, KMS, owner reference, and reconcile behavior are not deeply unit-tested in the listed files.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation_test.go

## Purpose
This file tests small but safety-relevant helpers from `key_rotation.go`: stable CronJob naming and same-node placement mutation for key rotation jobs.

## Important APIs and Tests
`Test_keyRotationCronJobName` verifies that OSD IDs 0 and 1 are formatted with `keyRotationCronJobAppNameFmt`. `Test_applyKeyRotationPlacement` provides pod specs with existing affinity, anti-affinity, and topology spread constraints, plus a case with nil affinity. It calls `applyKeyRotationPlacement()` and asserts anti-affinity and topology spread constraints are removed while required pod affinity is set to the supplied labels and hostname topology key.

## Control Flow Covered
The placement test covers both branches of affinity initialization: existing `Affinity` and nil `Affinity`. It also verifies that prior scheduling constraints are intentionally cleared. This is important because key rotation must run on the same node as the target OSD and should not inherit constraints that could prevent that.

## State and Persistence Behavior
The test uses in-memory `v1.PodSpec` values only. It does not create CronJobs or persist Kubernetes objects.

## Dependencies and Integration Points
The tests use Kubernetes core API structs and `testify/assert`. They indirectly protect the CronJob builder because `getKeyRotationPodTemplateSpec()` calls `applyKeyRotationPlacement()` after global and device-set placement application.

## Risks and Gaps
The tests do not cover `getKeyRotationContainer()`, Vault TLS volume wiring, device list construction, host path construction, Multus/host networking, schedule defaulting, owner references, deletion when disabled, or filtering to encrypted PVC-backed OSDs. Since the covered helper intentionally removes topology spread and anti-affinity, any future change to placement layering should add tests here.

## Test Signals
The file is a narrow regression signal. It protects the scheduling invariant that rotation jobs must be co-located with their OSDs, which is the highest-risk small helper in the key-rotation path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels.go

## Purpose
This file defines the Kubernetes labels used to identify OSD PVCs and OSD Deployments, and provides helpers to construct PVC labels, OSD daemon labels, and topology-location labels derived from CRUSH location strings.

## Important APIs, Types, and Functions
Constants include `CephDeviceSetLabelKey`, `CephSetIndexLabelKey`, `CephDeviceSetPVCIDLabelKey`, `OSDOverPVCLabelKey`, `TopologyLocationLabel`, `CephImageLabelKey`, and `RookImageLabelKey`. These keys are used by device-set PVC reconciliation, PVC-backed OSD Deployment filtering, key-rotation filtering, and status/reporting.

`makeStorageClassDeviceSetPVCLabel()` returns the base label set for PVCs created from storage class device sets: device set name, set index, device set PVC ID, Ceph image-at-creation, and Rook image-at-creation. `Cluster.getOSDLabels()` starts with standard Ceph daemon app labels, adds OSD ID, failure domain, portability, device class, store type, optional device type, and topology-location labels. `getOSDTopologyLocationLabels()` parses a space-separated CRUSH location string like `root=default host=node zone=zone-a` into labels named with `topology-location-<key>`.

## Control Flow
The helpers are deterministic mappers. `getOSDLabels()` overlays topology labels after base daemon labels. `getOSDTopologyLocationLabels()` ignores malformed tokens that do not split into exactly two `key=value` parts.

## State and Persistence
Labels generated here persist on PVCs and Deployments. They are used later as selectors for existing PVC detection, OSD Deployment lookup, key rotation CronJob owner targeting, health deletion, migration detection, storage status, and topology visibility. Because labels persist across upgrades, key names and values are compatibility-sensitive.

## Dependencies and Integration Points
The file depends on Rook controller label helpers and Ceph config constants. It is used by `deviceSet.go`, `osd.go`, `key_rotation.go`, migration logic, and tests. It also indirectly feeds Kubernetes selectors in health and key rotation paths.

## Risks and Edge Cases
Changing label keys can orphan existing resources from reconciliation. Label values sourced from CRUSH location can include topology dimensions only if the location string is well-formed. Device class and store labels may be empty but are still added by `getOSDLabels()`, which downstream code should tolerate. PVC image labels are sanitized in `deviceSet.go`, not here.

## Test Signals
`labels_test.go` validates topology label extraction for root, host, region, and zone entries. `deviceset_test.go` and other tests indirectly verify PVC label keys and image label presence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels_test.go

## Purpose
This file tests topology-location label extraction from an OSD CRUSH location string.

## Important APIs and Tests
`TestOSDTopologyLabels` passes `root=default host=ocs-deviceset-gp2-1-data-0-wh5wl region=us-east-1 zone=us-east-1c` to `getOSDTopologyLocationLabels()` and asserts the generated labels for host, region, and zone. The test does not assert root, but the helper would generate a `topology-location-root` label for well-formed `root=default` as well.

## Control Flow Covered
The test covers the normal split path where each space-separated token has exactly one `=` and becomes a label with the `topology-location-%s` format. It does not cover malformed tokens or values containing additional equals signs.

## State and Persistence Behavior
No Kubernetes objects are persisted. The returned map models labels that would later be persisted on OSD Deployments by `getOSDLabels()`.

## Dependencies and Integration Points
The test uses only `testify/assert`. It protects a helper consumed by OSD Deployment labeling and therefore by topology observability and any selector or diagnostic code that expects topology labels.

## Risks and Gaps
Coverage is narrow. It does not test `makeStorageClassDeviceSetPVCLabel()` or `getOSDLabels()` as a whole, and it does not assert behavior for malformed location strings. If future code starts relying on root labels, this test could be expanded to assert root explicitly.

## Test Signals
The file is a small regression guard for topology label naming and parsing. It complements broader tests that inspect PVC labels and Deployment creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate.go

## Purpose
This file detects and stages OSD migrations required by changes to encryption settings or OSD store type. It coordinates one-at-a-time migration by deleting one OSD Deployment, saving the migrated ID in a ConfigMap, and blocking further migration until that OSD Deployment is recreated.

## Important APIs, Types, and Functions
Constants define user confirmations (`yes-really-migrate-osds`, legacy `yes-really-update-store`), the migration ConfigMap name `osd-migration-config`, and data key `osdID`. `migrationConfig` stores a map of pending OSD IDs to `OSDInfo`.

`Cluster.newMigrationConfig()` lists current OSD Deployments and populates pending migration candidates by calling `migrateForEncryption()` and `migrateForOSDStore()`. `migrateForEncryption()` maps requested device-set encryption from the CephCluster spec and compares it to each Deployment's `encrypted` label, then records mismatches. `migrateForOSDStore()` compares the Deployment `osd-store` label with `spec.Storage.GetOSDStore()`. `getOSDToMigrate()` returns and removes an arbitrary pending OSD from the map. `getOSDIds()` returns all pending IDs, used to remove them from the update queue while migration is in progress.

`saveMigrationConfig()` writes the last migrated OSD ID to a ConfigMap with the CephCluster owner reference. `isLastOSDMigrationComplete()` reads the last migrated ID and returns false until the expected `rook-ceph-osd-<id>` Deployment exists. `getLastMigratedOSDId()` reads and parses the ConfigMap, returning `-1` for missing or empty config.

## Control Flow
`Cluster.startOSDMigration()` in `osd.go` gates this file's logic behind explicit confirmation, healthy PGs, and completion of the previously migrated OSD. When candidates exist, exactly one OSD is deleted and saved as the in-progress migration. Later provisioning sees `c.migrateOSD` and allows the prepare job for that PVC to be updated.

## State and Persistence
Persistent migration state is the `osd-migration-config` ConfigMap and OSD Deployments. Deployment labels are the source of current encryption/store truth. The pending map is in-memory and recalculated from live Deployments.

## Dependencies and Integration Points
The file depends on Deployment discovery and `getOSDInfo()` from `osd.go`, Kubernetes ConfigMaps/Deployments, CephCluster storage spec, and `k8sutil.CreateOrUpdateConfigMap()`. It integrates with the main reconcile update queue to avoid upgrading OSDs that need migration.

## Risks and Edge Cases
`getOSDToMigrate()` chooses an arbitrary map entry, so migration order is nondeterministic. `migrateForEncryption()` assumes a device-set name label maps to a spec entry; missing entries yield zero-value device sets. Missing `encrypted` labels are treated as false. Store migration only considers Deployments with an `osd-store` label. A malformed ConfigMap `osdID` blocks migration with an error.

## Test Signals
`migrate_test.go` covers no-op and mismatch detection for encryption and store type, plus last-migration completion for absent ConfigMap, missing Deployment, and recreated Deployment.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate_test.go

## Purpose
This file tests migration candidate detection and last-migration completion logic from `migrate.go`.

## Important APIs, Types, and Helpers
`TestMigrateForEncryption` creates fake OSD Deployments with device-set and `encrypted` labels, configures requested `StorageClassDeviceSet.Encrypted`, and verifies whether `migrationConfig.osds` is populated. `TestMigrationForOSDStore` creates Deployments with `osd-store` labels and compares them against `spec.Storage.Store.Type`. `createMigrationConfigmap()` writes the migration ConfigMap used by completion tests. `TestIsLastOSDMigrationComplete` verifies behavior when the ConfigMap is absent, when it references an OSD whose Deployment is not up, and when that Deployment exists.

## Control Flow Covered
Encryption tests cover a no-op case where requested and actual encryption are true, and a mismatch case where requested true versus actual false adds osd.1. Store tests cover matching store labels and a mismatch that adds osd.1. Completion tests cover `getLastMigratedOSDId()` returning `-1` for missing state, false when the expected Deployment does not exist, and true after the Deployment is created.

## State and Persistence Behavior
Fake Kubernetes Deployments and ConfigMaps represent all persistent state. The tests reuse a fake clientset and switch namespaces between subtests to isolate cases. Deployment labels are the source of actual settings; the ConfigMap data key `osdID` is the persisted migration cursor.

## Dependencies and Integration Points
The tests depend on fake client-go, CephCluster spec types, `cephclient.ClusterInfo`, and package helpers such as `getDummyDeploymentOnNode()` and `createDeploymentOrPanic()` from other test files in the package. They indirectly exercise `getOSDInfo()` because migration detection records full `OSDInfo` for candidate Deployments.

## Risks and Gaps
`TestMigrationForOSDStore`'s no-op subtest calls `migrateForEncryption()` instead of `migrateForOSDStore()`, which appears unintended and weakens store no-op coverage. The tests do not cover malformed migration ConfigMap data, missing device-set spec entries, duplicate candidates from encryption and store checks, or nondeterministic `getOSDToMigrate()` ordering. They also do not exercise `saveMigrationConfig()` owner-reference behavior.

## Test Signals
The file gives useful coverage for basic candidate selection and migration cursor completion, but has notable gaps around error handling and one likely copy-paste issue in the store no-op test.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/osd.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/osd.go

## Purpose
This is the central OSD manager for the Rook Ceph operator. It defines cluster-level OSD state, OSD metadata models, validation, the main reconcile entrypoint, migration orchestration, Deployment property extraction, topology/CRUSH location helpers, post-reconcile Ceph updates, storage status reporting, and node-specific configmap discovery.

## Important APIs, Types, and Functions
`Cluster` holds operator context, `ClusterInfo`, Rook/Ceph spec, valid storage, ConfigMap KV store, processed device sets, migration target, deprecated OSDs, and node configmaps. `New()` initializes a reconcile manager. `OSDInfo` serializes OSD identity and runtime attributes including ID, UUID, block paths, device class, topology, encryption, export service, node/PVC names, device type, and Cephx status. `OrchestrationStatus` is the JSON shape used by prepare status ConfigMaps. `osdProperties` carries resolved provisioning inputs for node or PVC OSDs.

`validateOSDSettings()` checks OSD memory and duplicate device set names. `validateTopologyAcrossNodes()` optionally detects topology label conflicts and fails new clusters with no existing OSDs. `Start()` is the main reconcile: validate, initialize node configmaps, set OSD timeout, compute skip-reconcile daemons, start migration, get update info, provision PVCs and nodes, process updates/creates, aggregate errors, clean orphaned prepare artifacts, apply upgrade OSD functionality, reconcile key rotation, update OSD properties, update CephCluster storage status, and delete the bootstrap keyring.

Deployment-related helpers include `deploymentOnNode()`, `deploymentOnPVC()`, `setOSDProperties()`, `resolveNode()`, `getOSDPropsForNode()`, `getOSDPropsForPVC()`, `getPVCHostName()`, `GetOSDID()`, `findOSDContainer()`, and `getOSDInfo()`. Topology helpers include `getLocationFromPod()`, `getTopologyFromNode()`, `GetLocationWithNode()`, `getNode()`, `resolveDeviceClass()`, `updateLocationWithNodeLabels()`, and `getOSDLocationFromArgs()`. Post-reconcile helpers include `applyUpgradeOSDFunctionality()`, `deleteOSDDeployment()`, `waitForHealthyPGs()`, `updateCephOsdStorageStatus()`, `getOSDStoreStatus()`, and `initializeNodeConfigmaps()`.

## Control Flow
The main reconcile deliberately separates update and create planning. Migration can remove candidate OSDs from the update queue and delete one Deployment before provisioning. PVC prepare runs before node prepare; status ConfigMaps from both feed creation. After all OSD create/update work, cleanup and Ceph-side post-processing occur. Many non-critical post-processing errors are logged and reconciliation continues; accumulated provisioning errors fail the reconcile after create/update attempts.

## State and Persistence
Persistent state includes OSD Deployments, prepare Jobs, status ConfigMaps, PVCs, node override ConfigMaps, migration ConfigMaps, CephCluster status, Ceph auth/bootstrap keyrings, Ceph CRUSH/device-class state, and Ceph require-osd-release state. `getOSDInfo()` reconstructs desired/actual OSD state from Deployment labels, env vars, container args, annotations, pod/node state, and legacy activation init scripts. Cephx status is persisted as a JSON annotation on the pod template.

## Dependencies and Integration Points
This file integrates nearly every OSD subsystem: create/update configs, device sets, key rotation, migration, topology, Ceph client commands, Kubernetes clients, reporting status updates, Rook placement/resource helpers, and health/upgrade behavior. It also uses package globals for topology validation and timeouts, which tests override.

## Risks and Edge Cases
Compatibility fallbacks are numerous: legacy block path extraction, missing CV mode defaulting to `lvm`, topology affinity detection after upgrade, CRUSH location fallback from pods/nodes, encryption detection from dmcrypt block path when labels are absent, and hostname lookup by node name or hostname label. These reduce upgrade risk but make behavior dependent on old pod specs and live pod availability. `resolveDeviceClass()` intentionally errors when both CR config and node label specify a device class. `validateTopologyAcrossNodes()` uses a package-global `topologyValidated`, so process lifetime affects repeated validation. `getOSDStoreStatus()` returns nil status if no deployments are found, which callers should handle carefully.

## Test Signals
The listed tests cover major portions indirectly: `integration_test.go` drives `Start()` across many reconcile scenarios; `create_test.go` covers provisioning entrypoints and device-class label conflict; `migrate_test.go` covers migration helpers; `health_test.go` covers release and deletion behavior; `labels_test.go` covers topology labels. Some important helpers, especially `getOSDInfo()` compatibility fallbacks and status update edge cases, are not comprehensively tested in the listed files.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/osd.go -->
