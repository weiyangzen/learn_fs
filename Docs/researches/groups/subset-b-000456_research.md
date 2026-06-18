# Research: subset-b-000456

Grouped research for Rook CephFS disruption toleration tests, CephFilesystem reconciliation, MDS deployment/probe logic, CephFS mirror reconciliation, and the MDS-map JSON fixtures used by probe tests. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration_test.go

## Purpose
This test validates the `controllerconfig.TolerationSet` helper used by disruption-controller configuration. It confirms that Kubernetes `corev1.Toleration` values are treated as unique by their full comparable struct value and that duplicates can be collapsed without losing semantically distinct tolerations.

## Important APIs, Types, and Functions
The only test entry point is `TestTolerationSet`. It builds two identical manual slices of `corev1.Toleration`, injects duplicates in shuffled adjacency, calls `(*TolerationSet).Add` repeatedly, and inspects `TolerationSet.ToList()`. The cases cover different keys, `Exists` versus `Equal` operators, different `Value` fields, and different taint effects including `NoSchedule`, `PreferNoSchedule`, and `NoExecute`.

## Control Flow, State, and Persistence
The test constructs an in-memory duplicate list by alternating each unique toleration with another toleration from the matching reference slice. It inserts all values into a fresh `TolerationSet`, converts the set back to a list, asserts the unique count, and does an order-independent membership check. No Kubernetes API state or persisted artifacts are involved.

## Dependencies and Integration Points
The file depends on Kubernetes core API toleration structs and `testify/assert`. It indirectly protects any controller code that stores tolerations through `TolerationSet`, especially code that merges tolerations from disruption or controller configuration.

## Risks
The test assumes `corev1.Toleration` remains Go-comparable. If future Kubernetes fields make the struct non-comparable, both the implementation and this equality-based test will need redesign. The test does not assert deterministic output ordering, which is appropriate for set semantics but means consumers must not rely on ordering from `ToList()`.

## Test Signals
Useful signals are exact unique cardinality and presence of every manual reference toleration after duplicate insertion. The test is strongest for full-struct uniqueness and weaker for serialization or ordering behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/controller.go

## Purpose
This is the controller-runtime reconciler for `CephFilesystem` custom resources. It wires watches, enforces finalizer-based cleanup, gates reconciliation on CephCluster readiness and Ceph version state, creates/deletes CephFS and MDS resources, configures mirroring, manages CephX key-rotation status, and starts or stops mirror-status monitoring goroutines.

## Important APIs, Types, and Functions
The public controller entry point is `Add`, which constructs a `ReconcileCephFilesystem` via `newReconciler` and registers watches in `add`. `ReconcileCephFilesystem` holds controller-runtime client/recorder/scheme, Rook cluster context, Ceph cluster spec/info, per-filesystem mirror health contexts, operator config, and a `shouldRotateCephxKeys` decision flag. `Reconcile` wraps `reconcile` with panic recovery and reporting. Helper methods include `reconcileCreateFilesystem`, `reconcileDeleteFilesystem`, `reconcileMirroring`, `reconcileAddBootstrapPeer`, `fsChannelKeyName`, and `cancelMirrorMonitoring`.

## Control Flow, State, and Persistence
`add` watches `CephFilesystem` CRs, owned Secrets and Deployments, and the monitor endpoint ConfigMap so bootstrap peer token changes can reconcile all filesystems. `reconcile` fetches the CR, cancels mirror monitoring on not-found, records the current generation, adds a finalizer, initializes status and CephX status when absent, and returns early until the owning `CephCluster` is ready. Once ready, it creates a per-filesystem cancelable context in `fsContexts`, reloads `ClusterInfo`, handles deletion by checking dependents and calling `reconcileDeleteFilesystem`, and removes the finalizer only after cleanup.

For normal reconciliation, it detects running and desired Ceph versions, waits during cluster upgrades, validates the filesystem spec, decides whether MDS CephX keys should rotate, and calls `reconcileCreateFilesystem`. It updates CephX status to Progressing, then handles mirroring: disabling mirroring when configured off, enabling the mirroring and snap-schedule modules, creating bootstrap peer secrets, importing peer tokens, setting Ready status with mirroring info, and optionally starting the periodic mirror checker. If mirroring did not update status, it sets Ready at the end.

## Dependencies and Integration Points
The controller integrates with controller-runtime watches, Kubernetes Secrets/Deployments/ConfigMaps, Rook `opcontroller` readiness/version/finalizer/status helpers, Ceph command clients, keyring rotation helpers, the `mds` package, mirror status checking, and deletion reporting. It depends on `CephFilesystemDependents` to prevent destructive deletion while subvolume state exists.

## Risks
`fsContexts` is a plain map modified from reconcile paths and read before indexing; concurrent reconciles for the same controller could race unless controller-runtime serialization and practical scheduling prevent overlap. Mirroring status goroutines use the `ClusterInfo` and spec pointer captured at startup; later cluster/spec updates may not affect a running checker until it is canceled and recreated. Status is set Ready even though a TODO notes it does not fully prove filesystem health. Deletion continues after some Ceph cleanup failures in lower layers, so operator status/events are important for operator visibility.

## Test Signals
Good signals include finalizer add/remove behavior, not-found mirror-monitor cancellation, requeue on missing or unready cluster, upgrade wait behavior, dependent deletion blocking events, CephX status transitions, mirroring enable/disable paths, bootstrap peer secret validation/import, and one mirror checker per filesystem when status checking is enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/controller_test.go

## Purpose
This test file exercises the `CephFilesystem` reconciler around cluster readiness, successful filesystem reconciliation, deletion blocking by dependents, and MDS CephX key rotation status. It uses fake Kubernetes clients and mock Ceph executors to validate controller behavior without a real Ceph cluster.

## Important APIs, Types, and Functions
`TestCephFilesystemController` covers missing cluster, unready cluster, successful ready-cluster reconciliation, and deletion blocked by a mocked `CephFilesystemDependents`. `TestMdsKeyRotation` covers first reconcile CephX status, repeated reconcile stability, brownfield unknown status preservation, transition from unknown to known during rotation, and additional generation-based rotations. The tests override `currentAndDesiredCephVersion`, `mds.UpdateDeploymentAndWait`, and executor command outputs.

## Control Flow, State, and Persistence
The tests construct `CephFilesystem`, `CephCluster`, monitor Secret, fake controller-runtime client, fake typed clientset, and a `ReconcileCephFilesystem`. Command responses simulate `ceph status`, `ceph fs get`, `ceph auth get-or-create-key`, `ceph auth rotate`, and `ceph versions`. Successful reconcile verifies `Status.Phase == Ready`. The deletion-block test gives the filesystem a deletion timestamp and replaces the dependency function to force a dependent event. The key-rotation test mutates the cluster CephX daemon policy and verifies CR status and generated keyring Secret data across several reconciles.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, controller-runtime fake clients, Rook API schemes, mock executor utilities, fake event recorders, `mds` deployment update stubs, keyring Secret creation, and Ceph version constants. It is a high-level integration test across controller, filesystem creation, MDS deployment/keyring generation, and status updating.

## Risks
The test suite mutates package-level functions and relies on deferred restoration only in some subtests, so future parallelization would be unsafe. Mock executor matching is argument-position based and may hide unasserted command changes by returning empty success for unmatched cases in some blocks. The deletion test mocks dependency discovery instead of exercising the real Ceph subvolume checks. The ready path does not validate all Kubernetes resources produced by MDS deployment generation.

## Test Signals
Signals include requeue results when the cluster is absent/unready, Ready status after successful reconcile, event content when deletion is blocked, CephX key generation/version persistence, Secret keyring updates on rotation, and absence of further Secret updates when the configured generation is already satisfied.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/dependent.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/dependent.go

## Purpose
This file implements deletion dependency detection for `CephFilesystem`. Since ordinary CephFS usage does not create RBD images, the operator blocks filesystem deletion by checking for CephFS subvolume groups containing subvolumes and `CephFilesystemSubVolumeGroup` CRs that reference the filesystem.

## Important APIs, Types, and Functions
The exported variable `CephFilesystemDependents` points to `cephFilesystemDependents` and is overridable for unit tests. `filesystemExists` wraps `cephclient.GetFilesystem` and treats Ceph `ENOENT` as safe absence. `subvolumeGroupDependents` calls `ListSubvolumeGroups` and `ListSubvolumesInGroup`, adds the explicit no-group case, ignores internal groups via `ignoreSVG`, and reports non-empty groups through a `dependents.DependentList`.

## Control Flow, State, and Persistence
`cephFilesystemDependents` creates an empty dependency list, checks whether the Ceph filesystem exists, and only queries Ceph subvolume groups when it does. It then lists Kubernetes `CephFilesystemSubVolumeGroup` resources in the namespace and adds those whose `Spec.FilesystemName` matches the filesystem. It returns aggregated errors from subvolume listing, but a filesystem-existence error is swallowed and returns an empty list.

## Dependencies and Integration Points
The logic integrates Ceph CLI-backed client calls, the Rook typed clientset, operator deletion reporting, and the common `dependents` utility. The dependent type string is written for user-facing deletion-block reports. Ignored Ceph group names include `_nogroup`, `_index`, `_legacy`, and `_deleting`, with a separate explicit no-group check represented as `<no group>`.

## Risks
Swallowing unexpected `filesystemExists` errors allows deletion to proceed without dependency checks if Ceph existence cannot be determined. Listing every subvolume in every non-ignored group can time out on large filesystems; the aggregate error message acknowledges this. Ignored internal groups could contain manually created data, but the code intentionally treats that as rare to avoid false deletion blocks from Ceph internals.

## Test Signals
Important signals are empty results for missing filesystem, detection of matching `CephFilesystemSubVolumeGroup` CRs, ignoring wrong-filesystem CRs, detection of non-empty Ceph subvolume groups, aggregation of list-subvolume errors, ignoring internal groups, and reporting subvolumes not in any group as `<no group>`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/dependent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/dependent_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/dependent_test.go

## Purpose
This test suite validates `CephFilesystemDependents` across Kubernetes subvolume group CRs, Ceph subvolume group contents, ignored internal groups, no-group subvolumes, and error aggregation.

## Important APIs, Types, and Functions
`TestCephFilesystemDependents` overrides `client.GetFilesystem`, `client.ListSubvolumeGroups`, and `client.ListSubvolumesInGroup`. It uses fake Rook clientsets to create `CephFilesystemSubVolumeGroup` resources and verifies `DependentList.Empty`, `PluralKinds`, and `OfKind`. Test helpers model missing and existing Ceph filesystems plus empty and non-empty subvolume lists.

## Control Flow, State, and Persistence
Each subtest sets mocked Ceph client functions, builds a `clusterd.Context`, optionally creates typed CRs, calls `CephFilesystemDependents`, and checks the resulting dependent categories/names. The mock functions assert that the filesystem name is propagated correctly and panic on unexpected group names to catch new control-flow paths. State is isolated in in-memory fake clients and restored mock functions via defer.

## Dependencies and Integration Points
The tests depend on Rook API types, fake versioned clientsets, Ceph client function variables, `client.AdminTestClusterInfo`, and `testify/assert`. They validate integration between Ceph-side dependency checks and Kubernetes CR-side dependency checks.

## Risks
The helper `newClusterdCtx` accepts objects but ignores them, so setup depends on explicit clientset creates inside each subtest. Mocking `GetFilesystem` with `syscall.Errno(2)` exercises the intended ENOENT path but not every possible command-error wrapper. Tests run serially because they mutate global Ceph client functions.

## Test Signals
Signals include no dependents for missing filesystems, no dependents for empty groups, blocking on matching `CephFilesystemSubVolumeGroup`, blocking on non-empty `csi` group, combined dependency categories, error text for failed subvolume listing, skipping `_index`, `_legacy`, `_deleting`, and explicit `<no group>` reporting when subvolumes are outside any group.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/dependent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/filesystem.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/filesystem.go

## Purpose
This file contains the CephFS creation, update, deletion, validation, and pool-naming logic used by the `CephFilesystem` reconciler. It bridges the CR spec to Ceph pools, Ceph filesystem commands, MDS daemons, standby replay settings, and the default CSI subvolume group.

## Important APIs, Types, and Functions
`Filesystem` stores filesystem name and namespace. `createFilesystem` starts the MDS cluster, creates or updates CephFS/pools when data pools are specified, configures standby replay and active MDS ranks, and creates the default `csi` subvolume group. `deleteFilesystem` removes MDS CephX/config objects, downs the filesystem, and optionally removes the CephFS and pools. `validateFilesystem`, `hasDuplicatePoolNames`, `createOrUpdatePools`, `updateFilesystem`, `doFilesystemCreate`, `downFilesystem`, `generateDataPoolNames`, `GenerateMetaDataPoolName`, and `generateMetaDataPoolName` implement validation and Ceph object naming.

## Control Flow, State, and Persistence
Creation starts MDS deployments first through `mds.NewCluster(...).Start()`. If `Spec.DataPools` is non-empty, it creates or updates Ceph pools and the Ceph filesystem. Existing filesystems are updated by setting `max_mds`, creating/updating pools, and adding data pools to the filesystem. New filesystems check existing pool names to avoid recreating pools, create metadata and data pools with the `cephfs` application, enable `allow_ec_overwrites` for erasure-coded data pools, and call `ceph fs new`. Afterward, standby replay, active rank count, and the `csi` subvolume group are reconciled.

Deletion builds the same MDS cluster object, deletes MDS daemon config and CephX objects for twice the active count, attempts to fail/down the filesystem, and permanently removes it only when Rook-created data pools exist and `PreserveFilesystemOnDelete` is false. Pool names are persisted in Ceph using either generated names (`<fs>-metadata`, `<fs>-dataN`, `<fs>-<named>`) or raw spec names when `PreservePoolNames` is true.

## Dependencies and Integration Points
The file integrates with `mds` daemon management, `cephclient` filesystem/pool/subvolume commands, pool validation, cluster specs, owner references, Rook logging, and Kubernetes resource sizing through the MDS package. CSI depends on the automatically created `csi` subvolume group for CephFS PVC provisioning.

## Risks
Starting MDS before creating a new filesystem means deployment success can precede CephFS creation failure. `SetNumMDSRanks` failures in update paths are logged and tolerated, potentially leaving lower availability than requested. Deletion logs and continues after down/remove failures, which may leave Ceph-side filesystem or pool state behind while the CR finalizer is removed by the caller. Duplicate pool-name validation ignores unnamed generated names that could still collide through spec changes.

## Test Signals
Signals include validation failures for missing required fields, duplicate named-pool detection, expected generated/preserved pool names, creation of metadata/data pools, adding new pools to existing filesystems, MDS deployment creation/update, successful no-pool external-filesystem MDS startup, EC overwrite setting attempts, standby replay and active-rank commands, and cleanup behavior on deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/filesystem_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/filesystem_test.go

## Purpose
This test file validates CephFilesystem spec validation, pool name generation, filesystem creation/update behavior, MDS deployment side effects, upgrade-related failure handling, and no-pool filesystem support.

## Important APIs, Types, and Functions
Tests include `TestValidateSpec`, `TestHasDuplicatePoolNames`, `TestGenerateDataPoolNames`, `TestPreservePoolNames`, `TestCreateFilesystem`, `TestUpgradeFilesystem`, and `TestCreateNopoolFilesystem`. Helpers `fsExecutor`, `fsTest`, `isBasePoolOperation`, and `validateStart` build mock Ceph responses and inspect created Kubernetes Deployments.

## Control Flow, State, and Persistence
`fsExecutor` models Ceph command behavior for `fs get/ls/dump/new/add_data_pool/subvolumegroup`, OSD pool/crush commands, MDS failure, auth, config, versions, and authtool paths. The creation test first creates a base filesystem and MDS deployments, reruns creation to exercise idempotent update, adds unnamed and named data pools, and validates pool create/add counters. The upgrade test creates a filesystem, then returns older MDS daemon versions and an MDS fail error to assert upgrade failure propagation. The no-pool test verifies MDS startup for an externally existing filesystem scenario where no CephFS pools are created by Rook.

## Dependencies and Integration Points
The file depends on fake Kubernetes clientsets, mock executors, Ceph client JSON models, Rook pool/MDS helper behavior, deployment update stubs, Ceph version constants, and resource specifications. It integrates filesystem.go with the `mds` package and Kubernetes Deployment creation.

## Risks
The large mock executor matches command slices manually, which makes the tests sensitive to argument order and incomplete for unanticipated command variants. Some unmatched paths return empty success after `assert.Fail`, so failures may be less direct if test assertions are not checked. Global `mds.UpdateDeploymentAndWait` is replaced and must remain serial. The no-pool mock returns an error for unknown commands but also returns key material broadly, which can hide exact command expectations.

## Test Signals
Signals include expected validation errors, duplicate pool detection, default and preserved pool naming, creation of `rook-ceph-mds-<fs>-a` and `-b` Deployments, no deployment update on first create and updates on subsequent starts, counters for newly added data pools, successful multi-filesystem creation, and upgrade failure text when standby failure cannot be performed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/health.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/health.go

## Purpose
This file implements the periodic CephFS mirroring status checker used by the `CephFilesystem` controller when mirroring is enabled. It updates CR status with mirror daemon health, snapshot schedule status, or error text.

## Important APIs, Types, and Functions
`mirrorChecker` stores Rook context, interval, controller-runtime client, cluster info, namespaced name, filesystem spec pointer, and filesystem name. `newMirrorChecker` constructs the checker and applies `Spec.StatusCheck.Mirror.Interval` when set. `checkMirroring` runs one immediate check and then loops on `time.After(interval)` until its context is canceled. `checkMirroringHealth` calls `cephclient.GetFSMirrorDaemonStatus` and, when snapshot schedules are enabled, `cephclient.GetSnapshotScheduleStatus`, then calls `updateStatusMirroring`.

## Control Flow, State, and Persistence
The checker is launched as a goroutine by the reconciler. It writes status through Kubernetes API updates rather than persisting local state. On any Ceph status error, it records nil mirror/schedule status plus the error message. On success, it stores the current mirror status and schedule status with an empty error. Cancellation is driven by the controller's per-filesystem context map when the CR is deleted or not found.

## Dependencies and Integration Points
The checker integrates with Ceph mirror daemon status commands, snapshot schedule status commands, `CephFilesystem` status updates, controller-runtime client access, and the CR's mirroring/status-check fields. It depends on `updateStatusMirroring` defined elsewhere in the package.

## Risks
The loop uses `time.After` each iteration, so a canceled context is only observed immediately if it wins the select; otherwise timers are short-lived but repeated. The checker captures `fsSpec` at creation time, so schedule enablement and interval changes may not be picked up until the checker is restarted. Errors cause status updates both inside `checkMirroringHealth` and again in the caller path, which can duplicate status writes.

## Test Signals
Useful signals are interval override behavior, immediate first check, cancellation shutdown, status updates on mirror daemon errors, schedule status inclusion only when schedules are enabled, and stable behavior when Ceph commands fail repeatedly.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/config.go

## Purpose
This file generates MDS CephX keyrings and writes default MDS-specific options to the Ceph monitor config store. It ensures each MDS daemon has appropriate Ceph capabilities, supports key rotation, removes legacy key Secrets, and sets cache and filesystem-join config.

## Important APIs, Types, and Functions
`generateKeyring` builds user `mds.<daemonID>`, requests caps `mon allow profile mds`, `osd allow *`, and `mds allow`, optionally rotates the key, deletes the legacy Secret named by `mdsConfig.ResourceName`, and writes the rendered keyring through the keyring secret store. `setDefaultFlagsMonConfigStore` computes `mds_cache_memory_limit` from resource memory limit or request and always sets `mds_join_fs` for `mds.<id>`.

## Control Flow, State, and Persistence
Keyring generation persists Ceph auth keys in Ceph and Kubernetes Secret data through the keyring store. If `shouldRotateCephxKeys` is true, it replaces the generated/existing key with `RotateKey`. Legacy Secret deletion is best-effort: not-found is debug, other errors are warnings. Config-store updates persist in Ceph monitor config for each MDS daemon. Memory limit takes precedence over request; custom factor fields override defaults.

## Dependencies and Integration Points
The file depends on Rook's keyring secret store, Ceph monitor config store, Kubernetes Secret API, MDS resource settings, `opcontroller` namespaced logging, and the `mdsConfig` generated during deployment startup. Its Secret resource version is later applied to MDS Deployment annotations to trigger restarts on key changes.

## Risks
The rendered keyring grants broad `osd allow *` and full `mds allow`, so key leakage is high impact. Config options are applied to running daemons and can fail if Ceph rejects runtime changes; callers ignore only EPERM in the deployment path. The map iteration order for config options is not deterministic, so tests should not depend on command order. Memory calculations cast float products to integer bytes, truncating fractional results.

## Test Signals
Signals include generated keyring contents, Secret resource version changes, legacy Secret deletion behavior, key rotation path, correct `mds_cache_memory_limit` values for limits and requests, custom factor behavior, and always setting `mds_join_fs`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/config_test.go

## Purpose
This test suite validates `setDefaultFlagsMonConfigStore`, especially how it derives `mds_cache_memory_limit` from MDS resource limits or requests and how custom factor fields override defaults.

## Important APIs, Types, and Functions
`TestSetDefaultFlagsMonConfigStore` builds `Cluster` instances with different `CephFilesystem.Spec.MetadataServer.Resources` and optional `CacheMemoryLimitFactor` or `CacheMemoryRequestFactor`. Each subtest installs a mock executor that inspects `ceph config set` calls for `mds_cache_memory_limit` and `mds_join_fs`.

## Control Flow, State, and Persistence
Subtests cover default limit factor for `1Gi`, custom limit factor `0.25`, default request factor for `512Mi`, custom request factor `0.6`, and no memory specified. The mock executor asserts the target daemon name `mds.myfs-a` and expected byte values, then `setDefaultFlagsMonConfigStore("myfs-a")` is called.

## Dependencies and Integration Points
The tests depend on Kubernetes resource quantity parsing, Rook Ceph config store command construction, mock executor utilities, and the `Cluster` struct. They validate command intent but do not talk to a real monitor config DB.

## Risks
Because config options are stored in a map, command order is nondeterministic; the mocks are permissive enough to tolerate this. The tests do not assert absence of `mds_cache_memory_limit` in the no-memory case except by only handling `mds_join_fs`, so an unexpected cache command could be missed if the mock returns success. They also do not cover executor errors.

## Test Signals
Signals are exact byte values `536870912`, `268435456`, `429496729`, and `322122547`, correct daemon identity, correct filesystem join target, and no error returned in all configured scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.go

## Purpose
This file embeds and renders the MDS liveness probe script and exposes the probe specification used in MDS containers. The probe checks whether the daemon ID appears as active or standby in the Ceph MDS map for the expected filesystem.

## Important APIs, Types, and Functions
Probe constants define timeout, command timeout, initial delay, period, success threshold, and failure threshold. `mdsLivenessProbeCmdScript` embeds `livenessprobe.sh`. `mdsLivenessProbeConfig` carries MDS ID, filesystem name, keyring path, and command timeout. `renderProbe` applies Go `html/template` to the script. `generateMDSLivenessProbeExecDaemon` returns a Kubernetes `v1.Probe` with `bash -c <rendered script>`.

## Control Flow, State, and Persistence
At deployment generation time, the MDS container receives the rendered script inline as an exec probe. Template parse/render failures are logged as warnings and still return a probe with whatever command string was produced. The probe state is persisted only in the Kubernetes Deployment/Pod spec.

## Dependencies and Integration Points
The file integrates with Kubernetes `v1.Probe`, embedded shell script assets, keyring mount paths, MDS deployment spec creation, and the Ceph CLI environment variables used inside the script. User-provided liveness probe config can override the generated defaults through higher-level configuration.

## Risks
Embedding a rendered multi-line shell script in the Pod spec makes correctness sensitive to template escaping and shell quoting. Use of `html/template` rather than `text/template` could escape special characters if future values contain them, though current values are controlled daemon IDs and paths. Logging render errors but continuing can create an invalid probe command.

## Test Signals
Signals include rendered command presence in MDS container probes, default timing values, correct daemon/filesystem/keyring substitution, and behavioral shell tests against representative `ceph fs dump` JSON.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.sh -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.sh

## Purpose
This bash template is the runtime MDS liveness probe. It avoids restarting MDS pods unless the daemon is definitely absent from the Ceph MDS map, which reduces the risk of destabilizing CephFS during monitor or cluster failure conditions.

## Important APIs, Types, and Functions
Template variables are `MDS_ID`, `FILESYSTEM_NAME`, `KEYRING`, and `CMD_TIMEOUT`. The script sets `CEPH_ARGS` with the keyring, runs `ceph fs dump` with monitor host/member environment variables and JSON output, parses standby and active MDS names with `jq`, exits `0` if the daemon is present, and exits `1` only when the daemon is absent from both standby and active maps.

## Control Flow, State, and Persistence
If `ceph fs dump` returns nonzero, the script prints the output and exits `0` because health cannot be determined safely. If the command succeeds, it computes `standbyMds` from `.standbys[].name` and `activeMds` from the matching filesystem's `.mdsmap.info[].name`. Presence in either path passes the probe; absence fails. The script has no persistent state.

## Dependencies and Integration Points
The script requires `ceph`, `jq`, mounted keyring credentials, `ROOK_CEPH_MON_HOST`, and `ROOK_CEPH_MON_INITIAL_MEMBERS`. It is rendered by `livenessprobe.go` and embedded into the MDS container's Kubernetes exec liveness probe.

## Risks
Invalid JSON or `jq` errors can produce values that do not equal `true`; in current tests some invalid cases pass because shell control flow ultimately avoids a definite absence signal. Missing `jq` in the container would likely make the probe fail on otherwise valid Ceph output. The script deliberately passes on Ceph command failures, so it cannot detect every unhealthy daemon state.

## Test Signals
Probe tests should confirm pass for active and standby daemons, fail for definitely absent daemons or filesystems, pass on Ceph command errors, and cover multi-filesystem maps where similarly named MDS daemons belong to different filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe_test.go

## Purpose
This file tests the embedded MDS liveness probe script end to end by rendering the Kubernetes probe command, running it through bash, shimming `ceph fs dump`, and feeding representative MDS map JSON fixtures.

## Important APIs, Types, and Functions
`probeShimWrapper` defines shell functions for `ceph` and `jq` so the rendered script can run under Go tests. Embedded fixture variables load `test/0FS.json`, `0FS-2MDS.json`, `1FS-2MDS.json`, and the four `2FS-*` maps. `writeLines` writes the generated command to a temporary script file. `Test_liveness_probe_script` discovers `jq` through `ROOK_UNIT_JQ_PATH` or `which jq`, then runs subtests for absent/present MDS scenarios, multiple filesystems, command errors, invalid JSON, and standby membership.

## Control Flow, State, and Persistence
Each subtest generates a probe for a daemon/filesystem pair, writes the exec command to `livenessprobeSample.sh`, launches bash with environment variables that provide monitor info, mocked command output, return code, and `JQ`, then checks process exit code. Temporary script files are removed with defer. If `jq` cannot be located, the whole test is skipped.

## Dependencies and Integration Points
The tests integrate Go unit tests, embedded JSON fixtures, the generated Kubernetes probe command, bash, a shimmed Ceph CLI, and real `jq`. They validate the shell script rather than only testing Go rendering.

## Risks
The test depends on a host `jq` binary unless CI sets `ROOK_UNIT_JQ_PATH`; otherwise important probe coverage is skipped. Several subtests share the same display name, which can make failure reports harder to scan. Temporary file name `livenessprobeSample.sh` is fixed in the working directory, so parallel test execution could collide. The shim asserts only one exact `ceph fs dump` argument shape.

## Test Signals
Signals include failure for zero filesystems and no matching MDS, success for MDS in the global standby list, success for active and standby-replay daemons in matching filesystems, failure for wrong filesystem or missing daemon, success for Ceph command failure and invalid JSON, and correct disambiguation across two filesystem maps.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/mds.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/mds.go

## Purpose
This file manages the lifecycle of Ceph MDS daemon Deployments for a CephFS filesystem, including keyring generation, deployment creation/update, upgrade sequencing, scale-down/deletion of unwanted daemons, and cleanup of daemon Ceph config/auth objects.

## Important APIs, Types, and Functions
`Cluster` stores cluster info, contexts, cluster spec, filesystem spec, owner info, host data path, and key-rotation flag. `NewCluster` constructs it. `Start` validates memory, detects upgrades with `isCephUpgrade`, runs `upgradeMDS` when needed, starts desired MDS deployments, and scales down extras. `startDeployment` builds per-daemon `mdsConfig`, generates keyrings, sets config flags, creates/updates Deployments, annotates key versions and last-applied hash, and sets owner references. `scaleDownDeployments`, `DeleteMdsCephObjects`, and `finishedWithDaemonUpgrade` handle cleanup and post-upgrade restoration.

## Control Flow, State, and Persistence
`Start` calculates desired replicas from `ActiveCount`, doubled when `ActiveStandby` is true. It honors skip-reconcile labels by returning without touching that daemon. For each desired daemon, it starts a Deployment named `rook-ceph-mds-<fs>-<letter>`. If a Ceph upgrade is detected from daemon versions lower than target `clusterInfo.CephVersion`, it disables standby replay, fails standby-replay daemons, reduces `max_mds` to 1, waits for one active rank, keeps only the active deployment, updates it, waits for standbys to disappear, then defers restoration of active count and standby replay.

Deployment state is persisted in Kubernetes. Ceph auth and config state are persisted in Ceph and keyring Secrets. Extra deployments are deleted or scaled to zero only after Ceph reports the desired number of active ranks, reducing filesystem downtime risk.

## Dependencies and Integration Points
The file integrates with Ceph daemon version discovery, CephFS rank and standby commands, Kubernetes Deployments, Rook deployment update gates, keyring Secret stores, monitor config stores, skip-reconcile labels, and deployment spec creation in `spec.go`. It relies on `mon.UpdateCephDeploymentAndWait` for safe rolling updates.

## Risks
Upgrade sequencing is complex and intentionally conservative; failures can leave `max_mds` or standby replay temporarily changed, with only logged remediation if deferred restoration fails. Daemon letter extraction splits the Ceph daemon name on `-`, so unusual filesystem names increase parsing ambiguity even though the last token should remain the letter. Returning immediately on a skip-reconcile daemon can skip reconciliation of later desired daemons. Extra deployment cleanup is gated by Ceph health/rank waits and may leave stale deployments when waits fail.

## Test Signals
Signals include memory validation, correct desired replica counts, generated deployment names, skip-reconcile handling, update path for existing deployments, upgrade detection from daemon versions, standby-replay disable/restore, active-rank waits, scale-down/delete behavior for extras, Ceph auth/config deletion, and deployment annotation changes on key rotation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/mds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/spec.go

## Purpose
This file constructs Kubernetes Deployment and container specs for MDS daemons. It applies Ceph daemon labels, volumes, init containers, probes, network settings, placement, annotations, resources, security contexts, log collection, and image/version labels.

## Important APIs, Types, and Functions
`makeDeployment` builds the full Deployment. `makeChownInitContainer` creates the init container for Ceph data directories. `makeMdsDaemonContainer` creates the `ceph-mds` container with daemon flags and generated liveness probe. `podLabels` builds stable labels including `rook_file_system`. `getMdsDeployments`, `deleteMdsDeployment`, and `scaleMdsDeployment` list, delete, or scale filesystem-specific MDS Deployments.

## Control Flow, State, and Persistence
The pod template starts with a chown init container and one MDS container. It mounts daemon volumes, applies unreachable-node toleration, placement, labels, annotations, host networking or Multus configuration, log collector sidecar when enabled, default service account, and priority class. The Deployment uses Recreate strategy, one replica, a selector based on pod labels, revision history limit, Rook version label, and Ceph version label. Non-host and non-Multus networking adds `--public-addr=$(ROOK_POD_IP)` to MDS args.

## Dependencies and Integration Points
The spec integrates with Rook controller helpers for daemon flags, volumes, env vars, log collection, security context, probes, Multus, version labels, and chown init containers. It consumes fields from `CephFilesystem.Spec.MetadataServer` and `ClusterSpec.Network`, `ClusterSpec.LogCollector`, and Ceph image settings.

## Risks
`scaleMdsDeployment` dereferences `d.Spec.Replicas` after a Get that may fail with not-found when scaling to zero, which can panic if callers pass a missing deployment and replicas is zero. The Deployment selector is immutable; changes to selector labels can force higher-level delete/recreate behavior elsewhere. Applying both Rook labels and user labels means user label conflicts could affect selectors or identity if not guarded upstream.

## Test Signals
Signals include full pod template conformance, resource requests/limits, priority class propagation, liveness probe override behavior, `--public-addr` presence only for pod networking, host-network DNS policy, log collector sidecar behavior, Multus annotation application, and `rook_file_system` selector listing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/spec_test.go

## Purpose
This test file validates generated MDS Deployment specs for pod networking and host networking, including labels, resources, priority class, service account, liveness probe override, and `--public-addr` behavior.

## Important APIs, Types, and Functions
`testDeploymentObject` builds a representative `CephFilesystem`, cluster spec, `Cluster`, and `mdsConfig`, then calls `makeDeployment`. `TestPodSpecs` validates the non-host-network Deployment with Rook's pod template tester. `TestHostNetwork` validates host-network-specific fields and absence of `--public-addr`.

## Control Flow, State, and Persistence
The helper sets MDS resources, priority class, image, data dir path, and a custom liveness probe initial delay of `900`. It asserts that the generated container carries the overridden liveness probe while preserving an exec handler. The tests then inspect the returned Deployment object in memory; no Kubernetes API state is created.

## Dependencies and Integration Points
The tests depend on Rook operator test utilities for label and pod template validation, fake clientsets, Ceph version constants, Kubernetes resource quantities, and controller daemon flag helpers. They cover the integration between `spec.go` and common Rook pod spec conventions.

## Risks
The helper contains assertions inside a subtest and then returns another deployment from a second `makeDeployment` call, which can obscure whether both calls are expected. Coverage is limited to host and default pod networking, not Multus or log collector sidecars. It does not exercise delete/scale helper functions.

## Test Signals
Signals include required Ceph labels, restart policy, service account, CPU/memory request and limit propagation, priority class, public address flag for pod networking, DNS policy for host networking, and liveness probe customization.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS-2MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS-2MDS.json

## Purpose
This fixture is a `ceph fs dump --format json` sample with no filesystems but two standby MDS daemons. It supports liveness probe tests proving that a daemon in the global standby list is considered healthy even before it joins a filesystem map.

## Important APIs, Types, and Functions
The JSON exposes top-level `epoch`, `default_fscid`, feature compatibility fields, `standbys`, and empty `filesystems`. The relevant standby names are `myfs-a-a` and `myfs-a-b`, both with `state: up:standby` and `join_fscid: -1`.

## Control Flow, State, and Persistence
The fixture is static test data embedded by `livenessprobe_test.go`. The probe's `jq` expression reads `.standbys | map(.name)` and should return true for `myfs-a-a` or `myfs-a-b` even though `.filesystems` is empty.

## Dependencies and Integration Points
It integrates with the rendered bash liveness probe and the Go test harness via `//go:embed`. It represents a Ceph state during early MDS startup or before filesystem association.

## Risks
The fixture validates standby presence but cannot prove filesystem correctness because no filesystem exists. If Ceph changes `fs dump` standby schema, the probe and fixture may diverge. Similar daemon names make it useful for name matching but also easy to misuse in unrelated tests.

## Test Signals
The expected signal is probe success for standby daemon IDs present in the top-level standby list, despite zero filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS-2MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS.json

## Purpose
This fixture is a minimal `ceph fs dump` sample with no filesystems and no standby MDS daemons. It is the negative baseline for MDS liveness probe tests.

## Important APIs, Types, and Functions
The JSON contains top-level epoch and compatibility metadata, `default_fscid: -1`, `feature_flags`, an empty `standbys` array, and an empty `filesystems` array.

## Control Flow, State, and Persistence
The fixture is embedded into the liveness probe test. Since both the standby and active MDS lookup paths are empty, a probe for any specific daemon should conclude definite absence and exit with failure.

## Dependencies and Integration Points
It integrates only with the probe test harness and the shell script's `jq` expressions. It models a Ceph cluster with no CephFS/MDS map entries.

## Risks
Because it is minimal, it does not exercise missing fields beyond the empty arrays. If the probe is changed to tolerate empty maps differently, this fixture should remain the strict negative case.

## Test Signals
The expected signal is exit code `1` when probing `myfs-c` or any other absent daemon.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/1FS-2MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/1FS-2MDS.json

## Purpose
This fixture represents one CephFS filesystem with one daemon in the filesystem MDS map and one daemon in the top-level standby list. It tests both active/in-filesystem and standby probe success paths, plus absent daemon and wrong-filesystem failures.

## Important APIs, Types, and Functions
The top-level standby list includes `myfs-b`. The single filesystem has `mdsmap.fs_name: myfs`, `max_mds: 1`, `up.mds_0: 36794`, and `info` containing daemon `myfs-a` in state `up:creating`. The liveness probe treats any `info[].name` for the selected filesystem as active enough for success.

## Control Flow, State, and Persistence
The fixture is static embedded data. The probe should pass for `myfs-a` on filesystem `myfs`, pass for `myfs-b` via the standby list, fail for an absent daemon like `myfs-c`, and fail when the requested filesystem name does not match.

## Dependencies and Integration Points
It integrates with the liveness probe script's active MDS lookup under `.filesystems[] | select(.mdsmap.fs_name == ...) | .mdsmap.info`, and with standby lookup under `.standbys`.

## Risks
The active daemon state is `up:creating`, not `up:active`; the probe intentionally checks membership rather than state. If future behavior should require active state, this fixture would need updated expectations.

## Test Signals
Signals are success for `myfs-a` and `myfs-b`, failure for `myfs-c`, and failure when probing filesystem `myfs1` with daemon `myfs-a`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/1FS-2MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,0)MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,0)MDS.json

## Purpose
This fixture represents two filesystems, `myfs` and `myfs1`, both with empty MDS maps and no standbys. It is a multi-filesystem negative case for the liveness probe.

## Important APIs, Types, and Functions
The JSON has two `filesystems` entries with `mdsmap.fs_name` values `myfs` and `myfs1`, empty `info` maps, empty `up` maps, and `max_mds: 1`. Top-level `standbys` is empty.

## Control Flow, State, and Persistence
The fixture is embedded data consumed by shell-based probe tests. The probe can find the requested filesystem but cannot find the requested daemon in active or standby locations, so it should fail.

## Dependencies and Integration Points
It tests the script's filesystem selection logic independently of daemon membership. This ensures an existing filesystem with no daemon does not falsely pass due to the filesystem name alone.

## Risks
The fixture includes full Ceph compatibility metadata that tests do not inspect. Its primary value is the empty `info` and `standbys`; if Ceph represents empty maps differently, probe parsing may need adjustment.

## Test Signals
The expected signal is exit code `1` for probing `myfs-a` on filesystem `myfs`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,0)MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,2)MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,2)MDS.json

## Purpose
This fixture represents two filesystems where `myfs` has no MDS daemons and `myfs-a` has two MDS daemons. It tests that the liveness probe scopes active daemon matching to the requested filesystem.

## Important APIs, Types, and Functions
The `myfs` entry has empty `info` and `up`. The `myfs-a` entry has `info` names `myfs-a-a` and `myfs-a-b`, with states `up:active` and `up:standby-replay`, and `up.mds_0` pointing to the active daemon. Top-level `standbys` is empty.

## Control Flow, State, and Persistence
When probing `myfs-a-a` or `myfs-a-b` for filesystem `myfs-a`, the script should pass. When probing `myfs-a` or `myfs-b` for filesystem `myfs`, it should fail even though similarly prefixed daemons exist in the other filesystem.

## Dependencies and Integration Points
The fixture validates the `jq` selector `.filesystems[] | select(.mdsmap.fs_name == "$FILESYSTEM_NAME")`, preventing cross-filesystem false positives.

## Risks
The fixture uses filesystem and daemon names with shared prefixes, which is good for disambiguation but can be confusing in failure output. It does not include top-level standbys, so it only covers filesystem-scoped map matching.

## Test Signals
Signals are success for both `myfs-a` filesystem daemons and failure for missing daemons in the `myfs` filesystem.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,2)MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(1,2)MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(1,2)MDS.json

## Purpose
This fixture represents two filesystems where `myfs` has one MDS daemon and `myfs-a` has two MDS daemons. It tests mixed partial/full daemon maps and name disambiguation.

## Important APIs, Types, and Functions
The `myfs` entry contains one `info` daemon named `myfs-b` in state `up:rejoin`. The `myfs-a` entry contains `myfs-a-a` and `myfs-a-b` in `up:active` and `up:standby-replay` states. There are no top-level standbys.

## Control Flow, State, and Persistence
The liveness probe should pass for `myfs-a-a` and `myfs-a-b` on filesystem `myfs-a`, fail for `myfs-a` on filesystem `myfs`, and pass for `myfs-b` on filesystem `myfs`. This proves the probe handles one filesystem having a partial daemon set while another has active plus standby-replay daemons.

## Dependencies and Integration Points
It is embedded by the Go liveness probe test and consumed by the shell script's filesystem-scoped `jq` map lookup.

## Risks
State `up:rejoin` is treated as present and therefore healthy by the probe. If liveness semantics become state-sensitive, this fixture's expected success for `myfs-b` may need reconsideration.

## Test Signals
Signals include success for present daemons regardless of active/rejoin/standby-replay state and failure for absent daemon names in the selected filesystem.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(1,2)MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(2,2)MDS.json -->
# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(2,2)MDS.json

## Purpose
This fixture represents two filesystems with two MDS daemons each. It is the full multi-filesystem positive case for the liveness probe and checks that similarly named daemon sets do not collide.

## Important APIs, Types, and Functions
Filesystem `myfs` has `info` names `myfs-a` and `myfs-b`, with states `up:standby-replay` and `up:active`. Filesystem `myfs-a` has `info` names `myfs-a-a` and `myfs-a-b`, with states `up:active` and `up:standby-replay`. Both have `max_mds: 1`, one active rank in `up`, and no top-level standbys.

## Control Flow, State, and Persistence
The fixture is embedded static JSON. The probe should pass for `myfs-a-a` on filesystem `myfs-a` and also pass for daemons in `myfs` when probed with that filesystem. Membership remains scoped to the selected filesystem.

## Dependencies and Integration Points
It validates the probe script against a realistic multi-filesystem MDS map with active and standby-replay daemons in each filesystem.

## Risks
The fixture's shared prefixes make it sensitive to any future bug that changes exact-name matching into substring matching. The probe still does not evaluate the health meaning of each MDS state beyond presence.

## Test Signals
The expected signal is successful probe exit for present daemon IDs in their respective filesystem maps, especially `myfs-a-a` under `myfs-a`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(2,2)MDS.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/config.go

## Purpose
This file generates and stores the CephX keyring for the `cephfs-mirror` daemon managed by `CephFilesystemMirror`. It defines the daemon user, capabilities, and key-rotation path.

## Important APIs, Types, and Functions
Constants define the keyring template, user `client.fs-mirror`, and user ID `fs-mirror`. `daemonConfig` carries the Kubernetes resource name, data path map, and owner info. `(*ReconcileFilesystemMirror).generateKeyring` requests caps for monitor, manager, MDS, and OSD access, optionally rotates the key, renders the keyring, and stores it with `CreateOrUpdate`.

## Control Flow, State, and Persistence
The reconciler calls `generateKeyring` before creating/updating the mirror Deployment. The key is generated or retrieved from Ceph auth state through the keyring store. If `shouldRotateCephxKeys` is true, `RotateKey` replaces it. The rendered keyring is persisted in the Kubernetes Secret named by `daemonConfig.ResourceName`, and its resource version is used to annotate the Deployment template.

## Dependencies and Integration Points
The file integrates with the keyring secret store, Ceph auth command helpers, filesystem mirror Deployment startup, owner references, and CephX rotation status in `CephFilesystemMirror.Status.Cephx`.

## Risks
The OSD cap string is nested in quotes inside the keyring template and must stay aligned with Ceph's parser. The `client.fs-mirror` user is shared for the daemon, so rotation affects all mirror daemon usage in the namespace. Failed rotation prevents deployment reconciliation.

## Test Signals
Signals include generated Secret data for `rook-ceph-fs-mirror-keyring`, resource version annotation changes, successful key generation, rotation when configured, and status updates reflecting the new key generation and Ceph version.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller.go

## Purpose
This is the controller-runtime reconciler for `CephFilesystemMirror` custom resources. It watches the mirror CR and owned resources, gates work on CephCluster readiness and version state, starts or updates the `cephfs-mirror` Deployment, and maintains phase, observed generation, and CephX key-rotation status.

## Important APIs, Types, and Functions
`Add`, `newReconciler`, `watchOwnedCoreObject`, and `add` register the controller. `ReconcileFilesystemMirror` stores Rook context, cluster info/spec, controller-runtime client/scheme, operator config, event recorder, and key-rotation flag. `Reconcile` wraps `reconcile` and reports results. `reconcile` handles fetch/status initialization/readiness/versioning/key-rotation/start/status update. `reconcileFilesystemMirror` validates external-cluster version compatibility and calls `start`. `updateStatus` retries status updates on conflicts.

## Control Flow, State, and Persistence
The controller watches `CephFilesystemMirror` CRs and owned ConfigMaps, Secrets, and Deployments. Reconcile returns cleanly for not-found, initializes empty status plus uninitialized CephX state, waits when the CephCluster is absent or unready, loads cluster info, detects running/desired Ceph versions, waits during upgrades for non-external clusters, decides whether daemon keys should rotate, starts the mirror deployment, computes updated CephX status, and writes Ready phase with observed generation. On reconcile errors, `Reconcile` attempts to mark the CR failed.

## Dependencies and Integration Points
It integrates with controller-runtime, Rook cluster readiness helpers, Ceph version reporting, keyring status helpers, `reporting.UpdateStatus`, fake and real Kubernetes clients, mirror deployment startup in `mirror.go`, and Ceph auth/keyring logic in `config.go`.

## Risks
There is no finalizer or deletion cleanup path in this controller; cleanup relies on owner references and Kubernetes garbage collection. The not-ready branch records a "successfully removed finalizer" event even though this CR has no finalizer path, which may be misleading. On reconcile error, a status-update failure shadows the original error in logging. The comment references `cephRBDMirror` in a CephFS mirror path, indicating copy/paste risk.

## Test Signals
Signals include requeue on missing/unready cluster, no requeue for too-old version handling if start path returns successfully/with status, requeue during cluster upgrade, Ready status on supported Ceph versions, CephX status initialization and generation updates, and failed status updates on reconciliation errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller_test.go

## Purpose
This test file exercises the `CephFilesystemMirror` controller for cluster readiness/version gates, successful mirror deployment reconciliation, and CephX key-rotation state transitions.

## Important APIs, Types, and Functions
`TestCephFilesystemMirrorController` covers missing cluster, unready cluster, ready cluster with old version scenario, cluster upgrade requeue, and successful creation on supported versions. `TestFSMirrorKeyRotation` covers first reconcile, stable subsequent reconcile, brownfield unknown status, rotation from unknown to known, no repeated rotation, and later generation updates. Tests override `currentAndDesiredCephVersion` and mock Ceph auth/status commands.

## Control Flow, State, and Persistence
The tests build a `CephFilesystemMirror` CR, fake `CephCluster`, monitor Secret, fake controller-runtime client, fake clientset, and `ReconcileFilesystemMirror`. Mock executors return Ceph status and auth keys, including rotated key material. Reconcile results are checked for requeue behavior, and CR status is fetched to assert phase or CephX key generation/version. Key rotation tests inspect the generated Secret `rook-ceph-fs-mirror-keyring`.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, fake controller-runtime client, API scheme registration, event recorder, mock executor, Ceph version constants, and keyring Secret behavior. It tests integration across controller logic, mirror deployment startup, keyring generation, and status updates.

## Risks
The test mutates package-level version detection and does not restore it between all subtests, so parallel execution would be unsafe. Some executor paths return success for unrecognized commands, which can hide changes in command behavior. The "version too old" case asserts no requeue but does not deeply inspect failure status or deployment absence. Scheme registration includes `CephRBDMirror` in the key-rotation test despite testing `CephFilesystemMirror`, a likely copy/paste artifact.

## Test Signals
Signals include requeue for missing/unready clusters, upgrade wait requeue, Ready phase after successful reconcile, initial CephX key generation `1`, retention of known and unknown CephX statuses, Secret updates on configured rotations to generations `2` and `3`, and no Secret change when no further rotation is required.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/controller_test.go -->
