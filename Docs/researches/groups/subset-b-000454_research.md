# Research: subset-b-000454

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/config/store.go -->
# sources/control-plane/rook/pkg/operator/ceph/config/store.go

## Purpose
`store.go` manages the Kubernetes-backed Ceph config data that every Ceph daemon needs at runtime, especially the current monitor host list and initial monitor members. Although `Store` still owns a `ConfigMapKVStore`, the active behavior in this file persists monitor settings in the `rook-ceph-config` Secret because CSI consumers require Secret-backed data.

## Important APIs, Types, and Functions
`StoreName` is the shared object name for both the historical ConfigMap store and the Secret. `GetStore()` wires namespace, `clusterd.Context`, Kubernetes clientset, and owner info. `CreateOrUpdate()` delegates to `createOrUpdateMonHostSecrets()`. That helper calls `cephclient.PopulateMonHostMembers()` to derive monitor IDs and host endpoints, writes `mon_host` and `mon_initial_members`, sets the controller reference, creates the Secret if missing, and updates it. `StoredMonHostEnvVars()` exposes `ROOK_CEPH_MON_HOST` and `ROOK_CEPH_MON_INITIAL_MEMBERS` from Secret keys. `StoredMonHostEnvVarFlags()` converts those env refs to Ceph CLI flags with `config.NewFlag`.

## Control Flow, State, and Persistence
The state is persisted in a namespace-scoped `v1.Secret` named `rook-ceph-config` with type `k8sutil.RookType`. Consumers mount or reference it via env vars, then Ceph commands receive `--mon-host=$(ROOK_CEPH_MON_HOST)` and `--mon-initial-members=$(ROOK_CEPH_MON_INITIAL_MEMBERS)`. The update path is deliberately simple: compute from the current `ClusterInfo`, create on not found, then issue an update. Ownership is anchored through `OwnerInfo.SetControllerReference()`.

## Dependencies and Integration Points
This integrates with `cephclient.ClusterInfo`, monitor endpoint formatting, Kubernetes Secrets, `clusterd.Context.Clientset`, `k8sutil.OwnerInfo`, daemon env construction in `controller/spec.go`, and all Ceph daemon argument builders that include stored monitor flags.

## Risks
The create path falls through to an update after creating the Secret. Fake clients tolerate this in tests, but real Kubernetes updates usually require a current `resourceVersion`; this path relies on client behavior or may be fragile if the newly created object is not reused. Error text contains a typo (`moh host`). `Store.configMapStore` is retained but unused here, which can confuse readers. Since daemons consume these Secret keys dynamically as env vars, missing or malformed monitor endpoints can break every daemon startup.

## Test Signals
`store_test.go` verifies create and update across one- and three-monitor cluster infos and both msgr2-only and v1/v2 endpoint strings. It also validates env var and CLI flag pairing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/config/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/config/store_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/config/store_test.go

## Purpose
`store_test.go` validates the monitor config Secret behavior and the public env/flag helpers from `store.go`.

## Important APIs, Types, and Functions
`TestStore` builds a fake clientset, `clusterd.Context`, and minimal owner info, then exercises `Store.CreateOrUpdate()` with one-monitor and three-monitor `ClusterInfo` fixtures. The local `assertConfigStore` helper reads `rook-ceph-config`, splits `mon_host` and `mon_initial_members`, and checks that every monitor ID and endpoint is represented. `TestEnvVarsAndFlags` asserts that `StoredMonHostEnvVars()` and `StoredMonHostEnvVarFlags()` point at the same Secret keys.

## Control Flow, State, and Persistence
The tests persist Secret state only in the fake Kubernetes client. `TestStore` first creates the Secret with one monitor, updates it with three monitors, then mutates endpoint strings to v1-style `1.2.3.4:6789` and repeats. `mon1EndpointsEnabled` doubles expected endpoint count because split host entries include both v1 and v2 forms when legacy endpoints are supplied.

## Dependencies and Integration Points
The tests depend on `testop.New()` fake Kubernetes clients, `clienttest.CreateTestClusterInfo()`, `cephclient.NewMinimumOwnerInfoWithOwnerRef()`, and the Secret API. They are direct unit coverage for daemon env integration.

## Risks
Assertions read `Secret.StringData`, which fake-client behavior preserves, while real Kubernetes stores Secret data under `Data` after admission. That makes the test less representative of a round trip through an API server. The test does not exercise owner-reference failures, Kubernetes update conflicts, malformed monitor data, missing internal monitor entries, or the create-then-update real-client behavior.

## Test Signals
Strong signals are Secret creation/update and env/flag consistency. Missing signals include real API-server serialization, Secret `Data` validation, and failure paths for create, get, update, or owner-reference setup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/config/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller.go

## Purpose
This file defines the controller-runtime reconciler for the Rook Ceph operator configuration ConfigMap. It watches `rook-ceph-operator-config` and applies changes to operator-wide runtime settings without requiring a full operator restart for every setting.

## Important APIs, Types, and Functions
`ReconcileConfig` stores the controller-runtime client, shared `clusterd.Context`, `OperatorConfig`, and operator manager context. `Add()` registers the controller. `add()` creates the controller named `rook-ceph-operator-config-controller` and watches ConfigMaps with `operatorSettingConfigMapPredicate()`. `Reconcile()` wraps panics with `opcontroller.RecoverAndLogException()`. `reconcile()` applies operator settings, refreshes Ceph command timeout, log level, discovery daemon state, loop-device allowance, host-network enforcement, revision history limit, and OBC extra config field allowance. `reconcileDiscoveryDaemon()` starts or stops the discovery DaemonSet.

## Control Flow, State, and Persistence
On a matching ConfigMap event, the reconciler loads operator settings through `k8sutil.ApplyOperatorSettingsConfigmap()`, then updates several process-global settings in memory. Some settings also cause cluster-side persistence: discovery daemon start/stop creates or deletes Kubernetes DaemonSet resources. Other settings mutate package globals used by later reconciles.

## Dependencies and Integration Points
The controller depends on controller-runtime manager/controller/source/handler primitives, `k8sutil` operator settings, `discover.New()`, shared `clusterd.Context.Clientset`, and the helper globals in `pkg/operator/ceph/controller`. Every Ceph CR controller indirectly observes these settings through shared process state.

## Risks
Most effects are global mutable state, so ordering and concurrency matter if reconciles overlap. The code only applies the operator settings ConfigMap when the request name exactly matches `OperatorSettingConfigMapName`, but still refreshes settings for any watched request that passes the predicate. Discovery daemon operations depend on manager context lifetime and operator namespace/image/service account values. Panics are logged but not converted into explicit reconcile errors by `RecoverAndLogException()`.

## Test Signals
No direct tests are listed for this file in the subset. Related coverage exists in `controller_utils_test.go` for individual setting parsers, but controller registration, predicate selection, discovery daemon side effects, and end-to-end ConfigMap reconciliation need integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cleanup.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/cleanup.go

## Purpose
`cleanup.go` builds and launches Kubernetes Jobs that perform destructive or forced cleanup for Rook Ceph custom resources. It also provides the annotation check used to detect user-requested force deletion.

## Important APIs, Types, and Functions
`ResourceCleanup` holds the target Kubernetes object, owning `CephCluster`, Rook image, and cleanup env configuration. `NewResourceCleanup()` constructs it. `StartJob()` creates a `batch.Job` and delegates execution to `k8sutil.RunReplaceableJob()`. `jobContainer()` builds the privileged cleanup container with args `ceph clean <Kind>`, resource-specific env vars, optional `ROOK_DATA_DIR_HOST_PATH`, pod namespace, and cleanup resources. `jobTemplateSpec()` wraps the container with volumes, restart policy, priority class, service account, and pod security context. `ForceDeleteRequested()` checks `rook.io/force-deletion: true` case-insensitively.

## Control Flow, State, and Persistence
Cleanup state is represented by an owned or replaceable Kubernetes Job. If `DataDirHostPath` is set, the path is mounted into the cleanup container and passed by env var. Resource-specific state is passed as environment variables from `config`. The job container runs the Rook image and relies on command dispatch inside that image to perform actual deletion work.

## Dependencies and Integration Points
The file integrates with Ceph CR types, cleanup resource/priority helpers from `cephv1`, Kubernetes batch/core APIs, `PrivilegedContext()` from `spec.go`, and `k8sutil.RunReplaceableJob()`. Constants define env names used by CephFS subvolume group and block pool RADOS namespace cleanup commands.

## Risks
`jobTemplateSpec()` always appends a hostPath volume using `cluster.Spec.DataDirHostPath`, even when the path is empty; the container only mounts it when non-empty. Cleanup jobs run privileged and as root, so incorrect config can have broad host impact. Map iteration over `config` makes env var order nondeterministic, which tests should avoid depending on. Force deletion is controlled by a simple annotation and should only be honored by callers after other safety checks.

## Test Signals
`cleanup_test.go` verifies job args/env count for a CephFS subvolume group and annotation detection. It does not run the job, verify hostPath behavior when empty, check owner references, or cover error paths from `RunReplaceableJob()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cleanup_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/cleanup_test.go

## Purpose
`cleanup_test.go` provides focused unit tests for cleanup Job template construction and force-delete annotation parsing.

## Important APIs, Types, and Functions
`TestJobTemplateSpec` creates a `CephCluster`, a `CephFilesystemSubVolumeGroup` with TypeMeta Kind, and a two-entry config map, then asserts the cleanup command uses the resource kind and that five env vars are present. `TestForceDeleteRequested` toggles `rook.io/force-deletion` and checks the boolean result.

## Control Flow, State, and Persistence
The tests instantiate pod template objects in memory only; no Kubernetes Job is submitted. The env count implicitly confirms three host-path-related env vars plus two resource-specific entries when `DataDirHostPath` is set.

## Dependencies and Integration Points
The tests depend on Ceph CR structs, metav1 object metadata, and the cleanup constants from `cleanup.go`.

## Risks
The env count assertion is brittle if common cleanup env vars change. The test does not assert container image, security context, volume definitions, restart policy, service account, resource requests, priority class, or behavior when `DataDirHostPath` is empty. It also covers only lowercase `"true"` despite production using case-insensitive parsing.

## Test Signals
Signals are basic command-kind plumbing and annotation enablement. Important missing signals are job submission/replacement behavior, privileged settings, cleanup resources, and failure propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cleanup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info.go

## Purpose
`cluster_info.go` creates, loads, migrates, and updates the cluster identity and monitor connection state used by the Ceph operator. It is the persistence layer for FSID, mon/admin credentials, monitor endpoint maps, out-of-quorum status, external monitor classification, and CSI defaults derived from the CephCluster spec.

## Important APIs, Types, and Functions
Core constants name the `rook-ceph-mon` Secret, the `rook-ceph-mon-endpoints` ConfigMap, Secret keys, endpoint keys, and disaster-protection finalizer. `LoadClusterInfo()` and `CreateOrLoadClusterInfo()` are the primary entry points. `createNamedClusterInfo()` generates FSID and cephx keys with `ceph-authtool`; `genSecret()` and `ExtractKey()` parse generated keyrings. `createClusterAccessSecret()` persists new cluster credentials. `UpdateClusterAccessSecret()` updates admin and mon keys. `loadMonConfig()` parses monitor endpoint ConfigMap data, out-of-quorum marks, max mon ID, mon scheduling mapping JSON, and external monitor IDs. `ParseMonEndpoints()` parses `a=ip:port,b=ip:port` strings. `PopulateExternalClusterInfo()` waits for externally supplied connection info.

## Control Flow, State, and Persistence
`CreateOrLoadClusterInfo()` first tries to read `rook-ceph-mon`. If missing and owner info is present, it creates a new FSID and cephx secrets, then writes a Secret with the disaster-protection finalizer. If the Secret exists, it loads FSID, monitor secret, and either new-style username/secret keys or migrates old `admin-secret` data into `ceph-username` and `ceph-secret`. It then loads monitor config from `rook-ceph-mon-endpoints`. CSI settings are copied from the CR and defaulted for topology labels and CephFS kernel mount options, including `ms_mode=secure` when network encryption is enabled. External clusters may use legacy `rook-ceph-operator-creds` if the Secret stores an admin placeholder.

## Dependencies and Integration Points
The file depends on `clusterd.Context` for clientset, executor, and config dir; `cephclient.ClusterInfo` for runtime cluster state; `cephv1.ClusterSpec` for network/CSI defaults; Kubernetes Secrets and ConfigMaps; OSD topology defaults; `k8sutil.OwnerInfo`; and Ceph CLI tooling via `ceph-authtool`. Many controllers call this before running Ceph commands or constructing daemon specs.

## Risks
Key generation writes temporary keyring files under `ConfigDir/namespace`; path sanitization only replaces the first `..`. `ExtractKey()` greps for `"key"` and assumes the third field is the secret, which is format-sensitive. `loadMonConfig()` logs invalid mapping JSON but returns success with an empty mapping, which may hide corrupted scheduling state. External cluster population loops every 60 seconds until context cancellation. Backward-compatibility branches around `AdminSecretNameKey` are subtle and can fail if Secrets contain mixed old/new keys. Updating the old Secret during migration can conflict under concurrent reconciles.

## Test Signals
`cluster_info_test.go` covers new Secret creation, owner info reconstruction, old admin-secret migration, legacy external credentials, and CSI kernel mount defaults. Endpoint parsing, max mon ID repair, out-of-quorum flags, mapping JSON, and external monitor filtering lack direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info_test.go

## Purpose
`cluster_info_test.go` validates cluster credential creation/loading and CSI setting defaulting for `CreateOrLoadClusterInfo()`.

## Important APIs, Types, and Functions
`TestCreateClusterSecrets` uses a mock executor that intercepts `ceph-authtool --create-keyring` and writes a fake keyring. It then calls `CreateOrLoadClusterInfo()` through several Secret formats and ClusterSpec variants. Assertions cover admin username/secret, FSID presence, `rook-ceph-mon` Secret contents, owner-reference reconstruction, old `admin-secret` migration, legacy external creds, and CephFS kernel mount option defaulting.

## Control Flow, State, and Persistence
The test creates a local temporary config dir and persists Kubernetes Secrets in a fake clientset. It mutates the stored `rook-ceph-mon` Secret to simulate older clusters and external-cluster placeholders, then creates `rook-ceph-operator-creds` for legacy external credentials. It also toggles operator env `CSI_CEPHFS_KERNEL_MOUNT_OPTIONS` and spec CSI values.

## Dependencies and Integration Points
It depends on fake Kubernetes clients, `exectest.MockExecutor`, Ceph CR specs, `cephclient.NewMinimumOwnerInfoWithOwnerRef()`, and Kubernetes Secret APIs. It exercises file-system writes for generated keyrings.

## Risks
The test is broad and stateful, which makes ordering important. It does not validate monitor endpoint ConfigMap parsing even though `CreateOrLoadClusterInfo()` always calls `loadMonConfig()`. It uses fake client behavior for status and Secret updates. The mock executor writes identical key text for mon and admin keys, so it does not catch command argument mix-ups beyond the first args.

## Test Signals
Strong signals are credential persistence, backward compatibility, owner ref reuse, and CSI mount option precedence: explicit spec over env, env over empty default, encryption default when applicable. Missing signals include invalid keyring parsing, Secret update conflicts, mon mapping JSON errors, and context-canceled external cluster waits.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/conditions.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/conditions.go

## Purpose
`conditions.go` centralizes CephCluster condition and phase updates, including backward-compatible translation from newer condition phases to the older `Status.State` values.

## Important APIs, Types, and Functions
`UpdateCondition()` fetches a `CephCluster` from the controller-runtime client and delegates to `UpdateClusterCondition()`. `UpdateClusterCondition()` filters existing conditions, updates or creates the requested condition, refreshes heartbeat/transition times, sets observed generation for Ready conditions, updates phase/state/message, and persists status through `reporting.UpdateStatus()`. `translatePhasetoState()` maps `Connecting`, `Connected`, `Progressing`, `Ready`, and `Deleting` to legacy cluster states, returning `Error` for false conditions.

## Control Flow, State, and Persistence
Condition updates are persisted to the CephCluster status subresource via the reporting helper. Long-term conditions such as created/connected and deletion-related conditions are preserved; transient conditions are discarded unless `preserveAllConditions` is true. Once phase is `Deleting`, later updates do not revert phase/message/state.

## Dependencies and Integration Points
The file depends on `clusterd.Context.Client`, Ceph API status types, Kubernetes condition timestamps, `k8sutil.ObservedGenerationNotAvailable`, and `pkg/operator/ceph/reporting`. All controllers that report cluster progress or health use this behavior indirectly.

## Risks
Status update errors are logged but not returned, so callers cannot requeue directly from failure. Time comparisons in tests can be difficult because timestamps are generated inline. The retention rules can drop transient conditions unexpectedly if callers do not pass `preserveAllConditions`. The phase lock on Deleting is intentional but means later recovery-like messages will not surface in `Status.Phase`.

## Test Signals
No direct test file is included for this source in the subset. Useful coverage would assert condition retention, transition-time changes only on status/message changes, observed generation updates only for Ready, Deleting phase stickiness, and reporting failure behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/conditions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils.go

## Purpose
`controller_utils.go` contains shared controller configuration, retry results, readiness gates, global operator setting parsers, panic recovery, and small naming helpers used across Ceph CR reconcilers.

## Important APIs, Types, and Functions
`OperatorConfig` describes operator namespace, image, service account, and watched namespace. `ClusterHealth` carries a cancelable health-check context. Requeue constants encode common retry timing. `DiscoveryDaemonEnabled()`, `SetCephCommandsTimeout()`, `SetAllowLoopDevices()`, `SetEnforceHostNetwork()`, `SetRevisionHistoryLimit()`, and `SetObcAllowAdditionalConfigFields()` read operator settings/env and update package/global state. Accessors expose loop-device allowance, host-network enforcement, revision history, and OBC key allowlist. `canIgnoreHealthErrStatusInReconcile()` allows known health errors (`MDS_ALL_DOWN`, `MGR_MODULE_ERROR`). `IsReadyToReconcile()` checks for a usable CephCluster and health state. `ClusterOwnerRef()`, `ClusterResource`, `RecoverAndLogException()`, and `NsName()` provide common metadata helpers.

## Control Flow, State, and Persistence
Most functions mutate in-process state rather than Kubernetes state. `exec.CephCommandsTimeout`, `loopDevicesAllowed`, global host-network enforcement, `revisionHistoryLimit`, and OBC allowlist are updated from settings. `IsReadyToReconcile()` lists CephClusters in the namespace, treats a deleting cluster with destructive cleanup policy as absent, and gates on health status before allowing controllers to run Ceph commands.

## Dependencies and Integration Points
This file integrates operator settings from `k8sutil`, Ceph API status and cleanup policy semantics, controller-runtime clients and reconcile results, `pkg/util/exec`, global Ceph API host-network enforcement, and logging helpers. Nearly every Ceph controller uses the readiness and retry constants.

## Risks
Global mutable state can leak between tests and between reconciles if settings change frequently. `IsReadyToReconcile()` takes the first CephCluster returned by list and does not select by name; single-cluster-per-namespace policy elsewhere makes this acceptable but important. Health gating depends on status details being populated consistently. Panics are logged but not surfaced as reconcile errors.

## Test Signals
`controller_utils_test.go` covers health-error allowlisting, timeout parsing, loop devices, host network parsing, revision history, readiness behavior for several CephCluster states, and OBC allowlist behavior. It does not cover panic recovery or multiple clusters in this helper.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils_test.go

## Purpose
`controller_utils_test.go` verifies global operator setting parsers and CephCluster readiness gating.

## Important APIs, Types, and Functions
`CreateTestClusterFromStatusDetails()` builds health-status fixtures. Tests cover `canIgnoreHealthErrStatusInReconcile`, `SetCephCommandsTimeout`, `SetAllowLoopDevices`, `SetEnforceHostNetwork`, `SetRevisionHistoryLimit`, `IsReadyToReconcile`, and `SetObcAllowAdditionalConfigFields`/`ObcAdditionalConfigKeyIsAllowed`.

## Control Flow, State, and Persistence
Tests set and unset environment variables to drive operator settings and mutate package-level globals. `TestIsReadyToReconcile` uses controller-runtime fake clients with CephCluster objects in different deletion/cleanup states. No persistent cluster resources are created outside the fake client.

## Dependencies and Integration Points
The tests depend on Ceph API scheme registration, controller-runtime fake client, `exec.CephCommandsTimeout`, Kubernetes metav1 deletion timestamps, and the process environment.

## Risks
Because tested functions mutate globals, test isolation depends on careful env cleanup and value resets. Some subtests use shared variables and global scheme, which can hide order-sensitive issues. Readiness tests do not cover `HEALTH_OK`, `HEALTH_WARN`, initialization error messages, or ignored health-error details even though those branches are important.

## Test Signals
Signals are strong for parsing defaults and invalid inputs. Missing signals include concurrent setting changes, panic recovery, multi-cluster namespace behavior, and full health-status readiness outcomes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/finalizer.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/finalizer.go

## Purpose
`finalizer.go` manages Rook Ceph CR finalizers so controllers can block deletion until external Ceph or Kubernetes cleanup is complete.

## Important APIs, Types, and Functions
`AddFinalizerIfNotPresent()` builds a finalizer from object kind and `ceph.rook.io`, appends it when absent, updates the object, and reports whether the object generation changed. `RemoveFinalizer()` removes the kind-derived finalizer. `RemoveFinalizerWithName()` refreshes the latest object from the API, removes a specific finalizer, and updates. `buildFinalizerName()` lowercases the kind and appends the Ceph custom resource group. The local `remove()` helper deletes a string from a slice.

## Control Flow, State, and Persistence
Finalizer changes are persisted via controller-runtime `client.Update()`. Removal first performs a fresh `Get()` to avoid updating stale finalizer state. The generated finalizer format is `<lowercase-kind>.ceph.rook.io`, for example `cephblockpool.ceph.rook.io`.

## Dependencies and Integration Points
The file depends on Kubernetes object metadata access, controller-runtime client operations, `cephv1.CustomResourceGroup`, and logging helpers. It is used by CR reconcilers that need cleanup protection.

## Risks
`remove()` mutates while iterating and does not break after removal; duplicate entries could be skipped or handled unexpectedly, though finalizers should be unique. Finalizer naming depends on `ObjectKind().GroupVersionKind().Kind`; missing TypeMeta can produce an empty-kind finalizer. Add does not refresh before update, so concurrent finalizer edits can conflict. Generation-change semantics differ between fake clients and API server behavior.

## Test Signals
`finalizer_test.go` covers add, remove by derived name, and remove by explicit name against a fake client. It does not cover missing TypeMeta, conflicts, duplicate finalizers, or metadata accessor failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/finalizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/finalizer_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/finalizer_test.go

## Purpose
`finalizer_test.go` validates basic finalizer add/remove behavior for Ceph CR objects.

## Important APIs, Types, and Functions
`TestAddFinalizerIfNotPresent` starts with a `CephBlockPool` with no finalizers and asserts one is added without a fake-client generation change. `TestRemoveFinalizer` removes the derived finalizer from a `CephBlockPool`. `TestRemoveFinalizerWithName` removes the same finalizer by explicit string.

## Control Flow, State, and Persistence
The tests register Ceph types in the scheme and use a controller-runtime fake client seeded with the object. Updates persist only in fake-client memory.

## Dependencies and Integration Points
The tests depend on Ceph API scheme registration, runtime objects, fake client, and metav1 object metadata.

## Risks
Fake clients do not model all API-server generation/resourceVersion behavior, so generation assertions are weak. Test objects use lower-case TypeMeta Kind for removal, matching the expected finalizer but not necessarily all live object TypeMeta forms. Error and conflict branches are untested.

## Test Signals
Signals prove the happy paths for add and remove. Missing signals include idempotent add/remove, stale object refresh, duplicate finalizers, conflict retries, and empty Kind behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/finalizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/handler.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/handler.go

## Purpose
`handler.go` provides a generic map function that lets a watch on one object type enqueue reconcile requests for all objects of another CR type.

## Important APIs, Types, and Functions
`ObjectToCRMapper[List client.ObjectList, T runtime.Object]()` determines the list GVK with `apiutil.GVKForObject()`, returns a `handler.TypedMapFunc`, lists objects of that GVK through the controller-runtime client into an `unstructured.UnstructuredList`, and maps every item to a `reconcile.Request`.

## Control Flow, State, and Persistence
The mapper does not persist state. On each watched event, it lists all target CRs cluster-wide or within whatever scoping the client/cache enforces, then enqueues reconcile requests by namespace/name. List errors return nil and silently skip enqueueing.

## Dependencies and Integration Points
It depends on controller-runtime client/list handling, unstructured lists, runtime schemes, typed handlers, and reconcile request construction. It is intended for cross-resource watches, such as reconciling CephFilesystem objects when a CephCluster changes.

## Risks
Listing all target CRs on every event can be expensive in large clusters. Errors are swallowed with no log, which can make missed reconciles hard to diagnose. The mapper currently takes no list options, so callers cannot easily namespace-filter here. GVK resolution must be correct for list types registered in the scheme.

## Test Signals
`handler_test.go` confirms that a fake CephFilesystem list maps to the expected request. It does not cover list failures, multiple objects, namespace filtering, or missing scheme registrations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/handler_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/handler_test.go

## Purpose
`handler_test.go` verifies that `ObjectToCRMapper()` can turn a watched event into reconcile requests for existing target CRs.

## Important APIs, Types, and Functions
`TestObjectToCRMapper` creates a `CephFilesystem`, registers Ceph list/object types in the scheme, builds a fake client, obtains a mapper for `CephFilesystemList`, and asserts that invoking it returns the filesystem's namespace/name request.

## Control Flow, State, and Persistence
The test keeps all objects in fake-client memory. The event object passed to the mapper is not itself used beyond triggering the list.

## Dependencies and Integration Points
It depends on Ceph API scheme registration, controller-runtime fake clients, runtime objects, and reconcile request types.

## Risks
The expected request name is shared package test data (`name`, `namespace`) from another test file, which couples tests in the package. Only a single object is listed. Error handling is not exercised because fake list succeeds.

## Test Signals
The test confirms happy-path GVK/list/request mapping. Missing signals include list error behavior, multiple CRs, empty lists, and mapper construction failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/label.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/label.go

## Purpose
`label.go` serializes detected Ceph versions into Kubernetes-safe labels and applies them to controller-owned resources.

## Important APIs, Types, and Functions
`CephVersionLabelKey` is `ceph-version`. `GetCephVersionLabel()` formats `version.CephVersion` as `Major.Minor.Extra-Build`. `ExtractCephVersionFromLabel()` converts the label back by prepending `ceph version `. `AddCephVersionLabelToDeployment()`, `AddCephVersionLabelToDaemonSet()`, `AddCephVersionLabelToJob()`, and `AddCephVersionLabelToObjectMeta()` initialize label maps if needed and add the version label.

## Control Flow, State, and Persistence
The functions mutate passed Kubernetes objects in memory; persistence happens only when callers create or update those objects. The file explicitly warns not to label pod templates because label changes could force unnecessary daemon restarts during upgrades.

## Dependencies and Integration Points
This integrates with `pkg/operator/ceph/version`, Kubernetes Deployment/DaemonSet/Job/ObjectMeta types, and upgrade/reporting logic that uses labels to track detected Ceph versions.

## Risks
The label format is part of the implicit contract and comments state not to change it. `ExtractCephVersionFromLabel()` depends on the version parser accepting the synthetic `ceph version` prefix. Applying labels to selectors or pod templates by mistake can cause disruptive rollouts.

## Test Signals
No direct test file is included for this source. Useful tests would cover nil resources, nil label maps, round-trip parse/format, and label format compatibility for multi-digit versions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer.go

## Purpose
`mirror_peer.go` creates, validates, names, and stores bootstrap peer tokens used for RBD and CephFS mirroring. It also manages cluster-level RBD mirror peer cephx rotation status.

## Important APIs, Types, and Functions
`CreateBootstrapPeerSecret()` dispatches by object type: `CephBlockPool` creates a pool-scoped RBD peer token, `CephCluster` creates a cluster-wide RBD token with optional key rotation, and `CephFilesystem` creates a CephFS peer token. `GenerateBootstrapPeerSecret()` builds the Kubernetes Secret with `token` and entity key (`pool`, `fs`, or `cluster`). `buildBootstrapPeerSecretName()` creates deterministic names. `GenerateStatusInfo()` reports Secret names for pool/filesystem status. `ValidatePeerToken()` checks required Secret data. `expandBootstrapPeerToken()` base64-decodes the token JSON, injects cluster namespace, and re-encodes it. `shouldRotateMirrorPeerKeys()` and `updateCephClusterCephxRbdMirrorStatus()` integrate with cephx rotation policy and status.

## Control Flow, State, and Persistence
Token creation starts with Ceph CLI/client calls, then the token is optionally expanded and stored in a `v1.Secret` via `k8sutil.CreateOrUpdateSecret()`. Owner references are set before persistence. Cluster-level RBD peer creation fetches the current CephCluster, decides whether to rotate keys, creates a token, then updates `Status.Cephx.RBDMirrorPeer` with conflict retry.

## Dependencies and Integration Points
The file integrates with `cephclient` mirror bootstrap APIs, Kubernetes Secrets, Ceph CR types, owner references, `keyring` cephx rotation helpers, `reporting.UpdateStatus()`, controller-runtime clients, and `WatchPeerTokenSecretPredicate()` in `predicate.go`.

## Risks
The default case wraps a nil `err`, producing an unclear error for unsupported object types. `ValidatePeerToken()` only requires `pool` for `CephRBDMirror`; CephFS mirror validation only requires `token`. Token expansion assumes valid base64 JSON matching `cephclient.PeerToken`. Secret creation ignores `AlreadyExists` even though `CreateOrUpdateSecret` should normally handle updates. Status update and token creation are separate operations, so partial success can leave token/status skew.

## Test Signals
`mirror_peer_test.go` covers token validation requirements and namespace injection in expanded tokens. It leaves status info tests empty and does not cover Secret creation, Ceph client failures, unsupported object types, key rotation decisions, or status conflict retries.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer_test.go

## Purpose
`mirror_peer_test.go` provides unit coverage for mirror peer token validation and token expansion.

## Important APIs, Types, and Functions
`TestValidatePeerToken` verifies empty data, missing `pool` for `CephRBDMirror`, and success for RBD and CephFS mirror objects. `TestGenerateStatusInfo` is a placeholder with no cases. `TestExpandBootstrapPeerToken` passes a base64-encoded peer token into `expandBootstrapPeerToken()` and checks the decoded result contains `namespace`.

## Control Flow, State, and Persistence
The tests do not persist Kubernetes Secrets or update CephCluster status. Token expansion is done fully in memory. A mock executor is present but not used by `expandBootstrapPeerToken()` in the current implementation.

## Dependencies and Integration Points
The tests depend on Ceph CR mirror types, `cephclient.AdminTestClusterInfo()`, base64 decoding, and testify assertions.

## Risks
`TestGenerateStatusInfo` provides no signal. The mock executor setup appears obsolete for token expansion and could mislead maintainers. The namespace assertion is substring-based rather than JSON-struct-based, so it would miss malformed JSON that happens to contain the word.

## Test Signals
Signals are basic validation rules and successful namespace injection. Missing signals include invalid base64, invalid JSON, exact token fields, Secret naming/status info, and cluster-level key rotation status.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/network.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/network.go

## Purpose
`network.go` applies Ceph public and cluster network CIDR settings, including automatic Multus CIDR discovery through a canary command-reporter Job.

## Important APIs, Types, and Functions
`ApplyCephNetworkSettings()` is the entry point. It only acts for host networking or Multus, merges user-provided `spec.network.addressRanges` with auto-discovered ranges, and calls `setNetworkCIDRs()` for `public_network` and `cluster_network`. `discoverCephAddressRanges()` discovers public and cluster ranges in parallel with a 15-minute deadline. `discoverAddressRanges()` builds a network canary `cmdreporter` Job, attaches the selected Multus network, waits for the network-status annotation, captures both the annotation and `ip --json address show`, and cross-references them. `crossReferenceNetworkStatusAndIpResult()`, `cidrForIp()`, and `findAddrInfoForIp()` reduce pod IP/prefix data to stable network CIDRs.

## Control Flow, State, and Persistence
User-specified address ranges are authoritative and skip discovery for that network. Multus discovery launches Kubernetes Jobs and reads their stdout. Applying CIDRs persists Ceph config options through the mon config store (`global public_network` and `global cluster_network`) using `SetIfChanged()`. Empty CIDR lists are logged but not written.

## Dependencies and Integration Points
The file integrates with CephCluster network selectors/address ranges, Multus network attachment annotations, CNI network-status annotations, `cmdreporter`, OSD placement, command reporter labels/annotations, `k8sutil` network parsers, and `config.GetMonStore()`.

## Risks
The canary path is operationally complex and depends on Multus, downward API timing, `ip --json`, network-status annotation format, service account `rook-ceph-cmd-reporter`, and OSD placement being schedulable. Channels are closed by the parent after reads; goroutines must send before close under the current flow. Auto-discovery can delay reconciliation up to 15 minutes. CIDR order follows reported IP order and can cause config churn if upstream order changes. Host-network mode does not auto-discover ranges, so users must specify address ranges if they want Ceph network settings.

## Test Signals
`network_test.go` is broad: it covers discovery success/failures, IPv4/IPv6 CIDR reduction, interface/IP mismatches, missing outputs, cmdreporter errors, placement propagation, explicit address range precedence, hostnet behavior, and mon-store errors. It does not run a real Multus canary.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/network_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/network_test.go

## Purpose
`network_test.go` validates Multus network CIDR discovery and Ceph network setting application without launching real Kubernetes Jobs.

## Important APIs, Types, and Functions
The file defines `mockCmdReporter`, `mockNewCmdReporter()`, `mockDiscoverAddressRangesFunc()`, and `mockMonStore` to replace package-level seams. `Test_discoverAddressRanges` covers public/cluster network selection, output parsing, error cases, multiple IPs, and placement propagation. `TestApplyCephNetworkSettings` covers pod-network no-op, Multus discovery, explicit public/cluster ranges, mixed explicit/discovered ranges, host networking, and mon-store failure propagation. Helpers `netStatus()` and `ipAddrOutput()` synthesize Multus annotation and `ip --json` output.

## Control Flow, State, and Persistence
Tests swap package-level function variables and restore them with defers. The command reporter mock returns stdout/stderr/retcode without Kubernetes execution. The mon-store mock verifies `SetIfChanged("global", "<network>_network", "<cidrs>")` calls and avoids real Ceph config writes.

## Dependencies and Integration Points
The tests depend on Ceph network specs, fake `clusterd.Context`, cmdreporter job construction, Kubernetes batch/core types, testify mock/assert, and `k8sutil` network parsers indirectly through production code.

## Risks
Package-level mock replacement means tests must not run these cases in parallel without additional isolation. The generated JSON strings are hand-built and can drift from real CNI output. Mock expectations verify intended calls but do not assert every job field, service account, annotation, or volume/mount detail in all cases.

## Test Signals
Signals are strong for deterministic CIDR logic and decision-making around explicit versus discovered ranges. Remaining gaps are real Multus/downward API behavior, long timeout cancellation, Job cleanup/replacement, and network-status variations from different CNI plugins.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/object_operations.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/object_operations.go

## Purpose
`object_operations.go` provides a small generic create-or-update helper for controller-runtime objects.

## Important APIs, Types, and Functions
`CreateOrUpdateObject()` obtains object metadata with `meta.Accessor()`, attempts `client.Create()`, and on `AlreadyExists` attempts `client.Update()`. It logs created or updated object type/name using reflection and `NsName()`.

## Control Flow, State, and Persistence
State is persisted through controller-runtime client create/update calls. The function does not fetch the existing object before update; it updates the object passed by the caller when creation reports already exists.

## Dependencies and Integration Points
It depends on Kubernetes API error classification, controller-runtime clients, metadata accessors, reflection, and Rook logging. It is a convenience helper for Ceph controller object reconciliation.

## Risks
Updating a caller-provided object after `AlreadyExists` may fail if it lacks the current `resourceVersion`, especially with real API servers. There is no patch/merge behavior and no conflict retry. Status subresources are not handled separately. Reflection output may be noisy but is only for logs.

## Test Signals
No direct tests are included in this subset. Useful tests would cover create success, already-exists update with a fake client, accessor failure, update conflict, and real-client-like resourceVersion requirements.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/object_operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/owner.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/owner.go

## Purpose
`owner.go` implements owner-reference matching so controllers can filter child object events to only those owned by the CR instance being reconciled.

## Important APIs, Types, and Functions
`OwnerMatcher` stores the owner object, owner metadata, owner group/kind, and scheme. `NewOwnerReferenceMatcher()` initializes metadata and derives group/kind with `scheme.ObjectKinds()`. `Match()` reads a child object's controller owner reference and returns true when group, kind, and UID match. If the owner UID is empty, kind/group match is enough. `getOwnersReferences()` returns only the controller owner reference. `setOwnerTypeGroupKind()` records the owner type's group/kind.

## Control Flow, State, and Persistence
No Kubernetes state is persisted. Matching is purely in-memory event filtering. Only the controller owner reference is considered, not all owner references.

## Dependencies and Integration Points
This integrates with controller predicates for non-CRD object watches, Kubernetes metadata accessors, runtime schemes, and owner references set by `k8sutil.OwnerInfo`.

## Risks
`meta.Accessor(owner)` ignores its error in `NewOwnerReferenceMatcher()`, so invalid owner metadata can lead to nil metadata and later panics or false matches. Empty owner UID allows broad matching by kind/group, useful for tests but risky if used before a real UID is assigned. Non-controller owner references are ignored. API version parse errors on children cause match errors and event suppression by callers.

## Test Signals
`owner_test.go` covers wrong kind, right kind/wrong UID, and right kind/right UID. It does not cover empty UID, multiple owner refs, non-controller owner refs, invalid APIVersion, or metadata accessor failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/owner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/owner_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/owner_test.go

## Purpose
`owner_test.go` verifies `OwnerMatcher.Match()` behavior for child objects with controller owner references.

## Important APIs, Types, and Functions
`TestMatch` creates a `CephObjectStore` owner with a UID and a Secret child with a controller owner reference. It initializes a matcher through `NewOwnerReferenceMatcher()` and mutates the child owner reference through wrong kind, right kind/wrong UID, and right kind/right UID cases.

## Control Flow, State, and Persistence
The test operates entirely in memory and does not use a Kubernetes client. Scheme registration is used only for owner group/kind detection.

## Dependencies and Integration Points
It depends on Ceph API scheme registration, Kubernetes core Secret metadata, owner reference semantics, and reflect-derived Kind setup.

## Risks
The test does not cover namespace differences because owner references do not encode namespace. It does not validate non-controller owner references or multiple owners. The owner TypeMeta and scheme setup are enough for this case but may not reveal failures for unregistered types.

## Test Signals
The test gives clear signal for the primary UID/kind gate. Missing signals include empty owner UID behavior, bad API versions, absent controller refs, and scheme object-kind errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/owner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/predicate.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/predicate.go

## Purpose
`predicate.go` defines controller-runtime predicates for Ceph CR watches, child Kubernetes object watches, peer-token Secret watches, duplicate CephCluster detection, and manager reload signaling.

## Important APIs, Types, and Functions
`WatchControllerPredicate()` reconciles creates/deletes and update events with spec diffs, deletion timestamp changes, or generation changes, while ignoring `do_not_reconcile=true`. `WatchPredicateForNonCRDObject()` filters child object events by owner reference and suppresses noisy resources. `objectChanged()` calculates patches with `k8s-objectmatcher`, normalizing resourceVersion. `isValidEvent()` drops `status` and `metadata` patch fields before deciding to reconcile. Helpers ignore canary/crash/exporter deployments, OSD status ConfigMaps, and `rook-ceph-config` Secret updates. `DuplicateCephClusters()` enforces one CephCluster per namespace. `GetSpec()` reflectively extracts a Spec field. `WatchPeerTokenSecretPredicate()` watches bootstrap peer token Secret create/update events. `ReloadManager()` sends SIGHUP to the operator process.

## Control Flow, State, and Persistence
Predicates do not persist state; they decide whether events enqueue reconciles. For CR updates, spec comparison uses `cmp.Diff()` and a `resource.Quantity` comparer. For child objects, create events are ignored, deletes reconcile only matching important children, and updates reconcile only meaningful data/spec changes after blacklists and patch trimming. Secret diffs are redacted and cephx keyring Secret updates are suppressed.

## Dependencies and Integration Points
The file integrates with controller-runtime event/predicate APIs, owner matching, Kubernetes Secrets/ConfigMaps/Deployments, Rook config and keyring annotations, Ceph CR specs, `k8s-objectmatcher`, `go-cmp`, and manager reload handling.

## Risks
Reflective `GetSpec()` will panic if called on an object without an exported Spec field? It logs and returns nil only when the field is missing after reflection; non-struct pointer shapes remain risky. Child object create events are always ignored, so recovery from missing owned objects relies on the primary CR reconcile path. Patch filtering removes all metadata changes, so meaningful label/annotation changes on child objects can be ignored except special config override handling. Peer-token predicates use substring name matching, which can match unintended Secret names. `DuplicateCephClusters()` returns true on list errors, effectively blocking reconciliation.

## Test Signals
`predicate_test.go` covers object diffing, patch trimming, canary detection, ConfigMap/Secret ignore rules, do-not-reconcile labels, and duplicate cluster detection. It does not cover the full typed predicates with create/update/delete events, peer token predicates, keyring Secret annotation suppression, or `ReloadManager()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/predicate_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/predicate_test.go

## Purpose
`predicate_test.go` validates key helper logic used by controller-runtime event predicates.

## Important APIs, Types, and Functions
`TestObjectChanged` checks patch-based object change detection. `TestIsValidEvent` verifies patch trimming and invalid JSON handling. Tests cover `isCanary`, `shouldReconcileCM`, `isCMToIgnoreOnDelete`, `isSecretToIgnoreOnUpdate`, `IsDoNotReconcile`, and `DuplicateCephClusters`.

## Control Flow, State, and Persistence
Most tests operate on in-memory objects. `TestDuplicateCephClusters` uses a controller-runtime fake client with CephCluster objects across same and different namespaces. No real watch events are created.

## Dependencies and Integration Points
The tests depend on Ceph CR types, Kubernetes ConfigMaps/Secrets/Deployments, controller-runtime fake clients, scheme registration, and package-level test constants shared with other tests.

## Risks
The suite tests helper functions more than the composed typed predicates, so event-specific behavior can regress without detection. `TestIsValidEvent` expects a patch containing `spec` to reconcile after metadata/status trimming, but does not cover metadata-only patches. Secret redaction and keyring annotation suppression are not directly tested.

## Test Signals
Signals are good for individual whitelist/blacklist decisions and duplicate cluster blocking. Missing signals include create/delete/update predicate end-to-end behavior, peer-token Secret predicates, and object matcher error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/predicate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/spec.go

## Purpose
`spec.go` is the shared pod/container spec construction library for Rook Ceph daemons and sidecars. It defines common volumes, mounts, flags, env vars, labels, probes, security contexts, log collection, external metrics endpoints, and skip-reconcile discovery.

## Important APIs, Types, and Functions
Volume helpers include `PodVolumes`, `CephVolumeMounts`, `RookVolumeMounts`, `DaemonVolumesBase`, `DaemonVolumesDataPVC`, `DaemonVolumesDataHostPath`, `DaemonVolumes`, `DaemonVolumeMounts`, and `AddVolumeMountSubPath`. Flag/env helpers include `DaemonFlags`, `AdminFlags`, `NetworkBindingFlags`, `DaemonEnvVars`, `ApplyNetworkEnv`, and `ContainerEnvVarReference`. Labels are built with `AppLabels` and `CephDaemonAppLabels`. Validation and init helpers include `CheckPodMemory`, `ChownCephDataDirsInitContainer`, and `GenerateMinimalCephConfInitContainer`. Probe helpers generate admin-socket, TCP, and rpcinfo probes. Security helpers include `DefaultContainerSecurityContext`, `CephSecurityContext`, and `PrivilegedContext`. Log/ops sidecars are built by `LogCollectorContainer` and `RgwOpsLogSidecarContainer`. External metrics are handled by `createExternalMetricsEndpoints`, `ConfigureExternalMetricsEndpoint`, and `extractMgrIP`. `GetDaemonsToSkipReconcile()` lists deployments labeled for skip-reconcile.

## Control Flow, State, and Persistence
Most functions build Kubernetes API structs in memory. Persistence happens when callers create/update pods, controllers, endpoint slices, or deployments. `ConfigureExternalMetricsEndpoint()` queries Ceph mgr map, adjusts the first external endpoint to the active mgr IP, builds an EndpointSlice, compares it with the current one, and creates or updates it. Log collector containers run an embedded bash loop to rewrite logrotate config and rotate logs every 15 minutes.

## Dependencies and Integration Points
This file integrates with `opconfig` data path and default flag helpers, keyring volume helpers, stored monitor env vars, Ceph CR specs/resources/placement/labels, Kubernetes core/discovery APIs, Ceph mgr map client calls, `k8sutil` endpoint helpers, and the broader daemon deployment code for mons, mgrs, OSDs, MDS, RGW, NFS, and mirror daemons.

## Risks
Because this file is shared by many daemons, small changes can have broad rollout impact. Volume/mount name mismatches can break pod creation. Several helpers depend on env vars for privileged/root behavior. Embedded shell scripts must remain compatible with image tools and logrotate config format. `ConfigureExternalMetricsEndpoint()` mutates a local copy of monitoring spec and can set an empty endpoint if mgr-map lookup fails but the spec differs. `CheckPodMemory()` warns on below-recommended memory but only errors when limit is below request. External metric EndpointSlice deep equality may be sensitive to server-populated fields.

## Test Signals
`spec_test.go` covers representative volume/mount matching, memory validation, admin socket commands, liveness probes, daemon/network flags, mgr IP extraction, external metrics endpoint create/update, log collector script generation, image pull policy defaulting, network env vars, and skip-reconcile deployment discovery. Many branches remain untested, including PVC/subpath helpers, security env toggles, minimal ceph.conf init, TCP/rpcinfo probes, labels, and RGW ops log sidecar.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/spec_test.go

## Purpose
`spec_test.go` validates representative shared pod-spec and endpoint construction behavior from `spec.go`.

## Important APIs, Types, and Functions
Tests cover `PodVolumes`, volume/mount matching for Ceph and Rook mounts, `CheckPodMemory`, daemon socket path/command builders, `GenerateLivenessProbeExecDaemon`, `DaemonFlags`, `NetworkBindingFlags`, `extractMgrIP`, `ConfigureExternalMetricsEndpoint`, `LogCollectorContainer`, `GetContainerImagePullPolicy`, `ApplyNetworkEnv`, and `GetDaemonsToSkipReconcile`.

## Control Flow, State, and Persistence
Most tests build Kubernetes structs in memory. External metrics tests use fake Kubernetes clients and mock Ceph command output for `mgr dump`, then assert EndpointSlice creation/update. Log collector tests compare generated bash script text. Skip-reconcile tests create fake Deployments and list them by label selector.

## Dependencies and Integration Points
The tests depend on fake clientsets, fake Rook clientsets, mock executors, Ceph version helpers, Kubernetes core/apps/discovery types, resource quantities, and Rook test volume helpers.

## Risks
Generated shell scripts are asserted as exact strings, which catches drift but can make harmless formatting edits noisy. Some tests rely on package-level `namespace` constants. External metrics tests use fake clients and do not model server-side EndpointSlice defaults. The network flag test has a guard that can skip mismatches when either side is empty, reducing failure sensitivity for empty-output regressions.

## Test Signals
Signals are strong for common daemon flags, network env encoding, logrotate script conversion, and external metrics endpoint IP selection. Missing signals include security contexts, minimal ceph.conf generation, PVC data volumes, subpath mutation, labels, TCP/rpcinfo probes, and error branches in endpoint creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/version.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller/version.go

## Purpose
`version.go` detects and compares Ceph versions for local images, running daemons, and external clusters.

## Important APIs, Types, and Functions
`ValidateCephVersionsBetweenLocalAndExternalClusters()` reads the external mon version and validates it against the local cluster version. `GetImageVersion()` returns the version recorded in CephCluster status when it matches the current spec image. `DetectCephVersion()` runs a command-reporter Job using the desired Ceph image and `ceph --version`, then parses stdout. `CurrentAndDesiredCephVersion()` detects the desired image version and reads the least up-to-date running mon version. `ErrorCephUpgradingRequeue()` formats an upgrade wait error including the standard requeue interval.

## Control Flow, State, and Persistence
Version detection launches a Kubernetes Job through `cmdreporter`, applies mon placement without pod anti-affinity, applies command reporter annotations/labels, and waits up to 15 minutes. It does not itself persist the detected version; callers are expected to store status/labels. External validation uses Ceph CLI/client calls against monitor state.

## Dependencies and Integration Points
The file depends on `cephclient` version queries, `pkg/operator/ceph/version` parsing/validation, `cmdreporter`, Kubernetes clientsets, owner references, CephCluster placement/resources/image pull policy, and requeue constants from `controller_utils.go`.

## Risks
Detecting version requires scheduling and completing a Job, so image pull, placement, service account, or command failures block reconciliation. `GetImageVersion()` returns a timeout-like error immediately when status does not match the current image; callers must handle waiting. Current/desired comparison uses least-up-to-date mon daemon version, which is appropriate for monitor upgrade gating but not a full cluster version inventory.

## Test Signals
No direct tests are included in this subset. Related tests in `spec_test.go` exercise placement-like command reporter behavior for metrics, but version detection job success/failure, parse errors, and external version validation should have dedicated coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller/version.go -->
