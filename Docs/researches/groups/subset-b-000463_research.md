# subset-b-000463 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller.go

Purpose: implements the controller-runtime reconciler for `CephBlockPoolRadosNamespace`, creating, deleting, status-reporting, CSI-profile, and RBD mirroring behavior for RADOS namespaces under Ceph block pools.

Important APIs/types/functions: `ReconcileCephBlockPoolRadosNamespace`, `Add`, `newReconciler`, `reconcile`, `createOrUpdateRadosNamespace`, `deleteRadosNamespace`, `updateStatus`, `buildClusterID`, `cleanup`, `reconcileMirroring`, `radosNamespaceChannelKeyName`, and `cancelMirrorMonitoring`. `mirrorHealth` tracks the context/cancel pair and whether a mirror checker goroutine has started. The controller registers an index field named `blockPoolName/radosNamespaceName` so deletion can detect duplicate CRs pointing at the same pool namespace.

Control flow: `Reconcile` wraps `reconcile` with panic recovery, named logging, and `reporting.ReportReconcileResult`. `reconcile` gets the CR, installs the finalizer, initializes status, checks CephCluster readiness, loads cluster info, resolves the running OSD Ceph version, handles deletion, handles external-cluster short circuiting, fetches the referenced `CephBlockPool`, waits for pool readiness, creates the namespace with Ceph CLI helpers, reconciles mirroring, marks Ready, and writes CSI client profile RADOS namespace config. Deletion skips Ceph delete for external clusters, avoids deleting the shared namespace until the last duplicate CR is removed, blocks finalizer removal if the namespace has images, and can launch a cleanup job when force-delete is annotated.

State and persistence: persistent state is Kubernetes CR finalizers/status, status `Info["clusterID"]`, CSI operator `ClientProfile` resources, and Ceph-side RADOS namespaces/mirroring settings. Runtime state is the in-memory `radosNamespaceContexts` map that owns mirror-monitoring goroutine cancellation. This map is not persisted and is rebuilt by later reconciles.

Dependencies/integration: depends on controller-runtime, Rook `opcontroller` readiness/finalizer helpers, `cephclient` Ceph CLI wrappers, CSI config helpers, `reporting.UpdateStatus`, `k8sutil.Hash`/job-name truncation, and dependent-deletion condition helpers.

Risks: deletion correctness depends on field-index consistency and duplicate CR detection. `radosNamespaceChannelKeyName` parameter order is easy to misuse because call sites pass namespace/name in different textual orders. Mirror monitoring has shared mutable map state with goroutines but no mutex. The controller logs status-update errors without returning them in `updateStatus`. Force cleanup can remove Ceph resources asynchronously while finalizer blocking still depends on Ceph delete results.

Test signals: covered by `controller_test.go` for no cluster, unready cluster, unready block pool, successful namespace creation, external mode CSI profile update, cluster ID hashing, implicit namespace resolution, and mirroring enable/disable variants. Deletion, duplicate CR handling, force cleanup, and monitor cancellation are less directly tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller_test.go

Purpose: unit/integration-style test coverage for the RADOS namespace reconciler using fake controller-runtime clients, fake Kubernetes clients, and mock Ceph command execution.

Important APIs/types/functions: `TestCephBlockPoolRadosNamespaceController`, `Test_buildClusterID`, and `TestGetRadosNamespaceName`. The main test constructs `CephBlockPoolRadosNamespace`, `CephCluster`, `CephBlockPool`, secrets, fake CSI config, and a `ReconcileCephBlockPoolRadosNamespace` directly instead of going through manager setup.

Control flow: the primary test mutates shared test objects across subtests to move through controller states. It first verifies reconcile requeues when no cluster or an unready cluster is present. It then injects monitor secrets and a ready pool to validate successful create, Ready status, and CSI config presence. Further subtests toggle external mode and mirroring specs, with mock command handlers matching `namespace create`, `mirror pool info`, `mirror pool enable`, `mirror pool disable`, `mirror pool status`, and `versions`.

State and persistence behavior: fake Kubernetes object trackers persist CR status changes and config maps across individual test branches. The test also creates a Rook clientset namespace resource and a Kubernetes secret so `LoadClusterInfo` can assemble cluster info. Environment variables such as `POD_NAMESPACE` and `ROOK_LOG_LEVEL` influence CSI config and logging setup.

Dependencies/integration: uses Rook fake clientsets, controller-runtime fake client, Ceph API scheme registration, `csi.CreateCsiConfigMap`, `k8sutil.NewOwnerInfoWithOwnerRef`, and `exectest.MockExecutor`.

Risks: many subtests reuse and mutate objects like `cephCluster`, `cephBlockPool`, and `cephBlockPoolRadosNamespace`; this can hide ordering dependencies. Some assertions check only result/error/status and not all created/updated resources. Deletion paths, finalizer removal, duplicate CR field index behavior, cleanup jobs, and long-running mirror goroutine cancellation are not strongly exercised.

Test signals: positive signals include coverage for cluster readiness gates, block pool readiness, external mode, successful CSI profile update, mirror-mode compatibility with block pool mirroring, remote namespace argument placement, mirroring disable with empty image list, deterministic cluster ID generation, and implicit namespace name mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/radosnamespace/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/status.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/status.go

Purpose: status helper logic for `ReconcileCephBlockPool`, centralizing status phase, info map, observed generation, CephX peer token, and pool ID updates.

Important APIs/types/functions: `updateStatus`, `updateStatusInfo`, and `updatePoolID`. `updateStatus` is a method on `ReconcileCephBlockPool`; `updateStatusInfo` is a pure-ish helper over a `CephBlockPool`; `updatePoolID` queries Ceph pool details.

Control flow: `updateStatus` retries on Kubernetes update conflicts. It fetches the latest pool, initializes status when nil, populates pool ID when transitioning to Ready and `PoolID` is unset, updates `Phase`, rebuilds status `Info`, records observed generation when available, stores CephX peer token when provided, and writes through `reporting.UpdateStatus`. `updateStatusInfo` adds mirroring bootstrap info only when the pool is Ready and mirroring enabled, then records type and failure domain. `updatePoolID` calls `cephclient.GetPoolDetails` and logs rather than returning on failure.

State and persistence: persists status subresource fields on `CephBlockPool`: `Phase`, `Info`, `ObservedGeneration`, `Cephx.PeerToken`, and `PoolID`. It reads Ceph cluster state to fill the numeric pool ID.

Dependencies/integration: depends on controller-runtime client, retry-on-conflict, `cephclient.GetPoolDetails`, `opcontroller.GenerateStatusInfo`, `k8sutil.ObservedGenerationNotAvailable`, and `reporting.UpdateStatus`.

Risks: the method logs any final retry error but always returns nil, which can hide failed status persistence from callers. Pool ID retrieval failure does not fail reconcile. Status `Info` is rebuilt from scratch, so consumers must not expect arbitrary existing keys to survive.

Test signals: `status_test.go` focuses on `updateStatusInfo` for replicated vs erasure-coded pools, default vs explicit failure domain, and mirroring info only when Ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/status_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/status_test.go

Purpose: focused unit tests for the pool status info map generation logic.

Important APIs/types/functions: `TestUpdateStatusInfo` exercises `updateStatusInfo` directly with hand-built `CephBlockPool` objects.

Control flow: the test creates a replicated pool in Progressing state, verifies `type=Replicated`, default failure domain, and no mirror bootstrap key. It then creates an erasure-coded pool with failure domain `osd`, verifies `type=Erasure Coded`, the explicit failure domain, and no mirror info. Finally it enables mirroring while still Progressing, verifies mirror info is absent, then changes phase to Ready and verifies `opcontroller.RBDMirrorBootstrapPeerSecretName` appears.

State and persistence behavior: no Kubernetes client is used; state changes are in-memory mutations of `Status.Info`, `Status.Phase`, and `Spec.Mirroring`.

Dependencies/integration: imports Ceph API types and `opcontroller` constants so it validates the public keys consumed by mirroring status users.

Risks: does not test the full `updateStatus` retry/update path, observed generation, CephX token persistence, NotFound handling, conflict handling, or `updatePoolID` Ceph query behavior.

Test signals: confirms the most user-visible status info shape and guards against accidentally exposing mirroring bootstrap data before the pool is Ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/validate.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/validate.go

Purpose: validates `CephBlockPool` and `PoolSpec` objects before reconcile applies Ceph-side pool configuration.

Important APIs/types/functions: `validatePool`, exported `ValidatePoolSpec`, `validateDeviceClasses`, and `validateDeviceClassOSDs`.

Control flow: `validatePool` checks name/namespace, delegates base CR validation to `cephv1.ValidateCephBlockPool`, then validates the embedded pool spec. `ValidatePoolSpec` validates hybrid storage device classes, rejects simultaneous replicated and erasure-coded settings, rejects identical failure/subfailure domains, enforces stretch-cluster restrictions, lazily reads the CRUSH map when failure domain or CRUSH root is specified, validates requested failure domain/root/subdomain names, validates replica size and `ReplicasPerFailureDomain`, validates compression mode in `Parameters`, and validates mirroring mode and snapshot schedule combinations. Snapshot schedules without mirroring only warn.

State and persistence behavior: no persistent writes. It reads Ceph cluster state for CRUSH map and device-class OSD membership when specs require live validation. It logs deprecated compression mode and snapshot schedule warnings.

Dependencies/integration: depends on Ceph API spec helpers like `IsReplicated`, `IsErasureCoded`, `IsHybridStoragePool`, and `SnapshotSchedulesEnabled`, plus `cephclient.GetCrushMap` and `cephclient.GetDeviceClassOSDs`.

Risks: validation can fail due to temporary Ceph command errors, not only invalid specs. The error string for allowed mirroring modes says image and pool even though code also accepts `init-only`. Deprecated `CompressionMode` is only warned, while `Parameters["compression_mode"]` is enforced. Stretch-cluster rules are hard-coded to replicated size 4 and no erasure coding.

Test signals: `validate_test.go` covers missing fields, invalid replication/EC combinations, replica safety, compression modes, replica-per-failure-domain constraints, CRUSH domain/root lookup, mirroring modes/schedules, subfailure domain conflicts, and hybrid storage device-class OSD presence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/validate_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/validate_test.go

Purpose: validates pool-spec guardrails with mock Ceph command output and hand-built pool specs.

Important APIs/types/functions: `TestValidatePool`, `TestValidateCrushProperties`, and `TestValidateDeviceClasses`.

Control flow: `TestValidatePool` exercises local spec validation branches: missing replication/EC settings, missing name/namespace, both replicated and EC settings, safe size-1 replication, known/unknown compression modes, replica count vs replicas per failure domain, unknown subdomain, EC pool with deprecated compression mode, mirroring mode validation, snapshot schedule interval validation, and identical failure/subfailure domain rejection. `TestValidateCrushProperties` mocks `ceph osd crush dump` JSON to test known/unknown failure domains and CRUSH roots. `TestValidateDeviceClasses` mocks `ceph osd crush class ls-osd` output for primary and secondary device classes.

State and persistence behavior: no Kubernetes persistence; tests use in-memory specs and `exectest.MockExecutor` output to simulate Ceph state.

Dependencies/integration: uses `clusterd.Context`, `cephclient.AdminTestClusterInfo`, `exectest.MockExecutor`, Ceph API types, and testify assertions.

Risks: no explicit test for stretch cluster restrictions, warnings-only branches, malformed CRUSH JSON, Ceph command errors, or `ValidatePoolSpec` callers with nil cluster/spec context. A duplicate subtest label says "not a power of 2" although implementation validates divisibility/factor behavior.

Test signals: coverage is broad for expected user-facing validation failures and live Ceph lookup integration, especially CRUSH and hybrid device-class paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/predicate.go -->
# sources/control-plane/rook/pkg/operator/ceph/predicate.go

Purpose: provides a typed controller-runtime predicate for filtering operator-settings ConfigMap events.

Important APIs/types/functions: `operatorSettingConfigMapPredicate[T *corev1.ConfigMap]()` returns `predicate.TypedFuncs[T]` with Create, Delete, Update, and Generic filters.

Control flow: Create and Generic events are ignored. Delete events are accepted only when the deleted ConfigMap name is `rook-ceph-operator-config`. Update events are accepted only when the new object has that name. This limits watches to changes relevant to operator config settings.

State and persistence behavior: no writes or persistence. It only examines event objects.

Dependencies/integration: depends on controller-runtime typed event/predicate APIs and `corev1.ConfigMap`. It integrates with controllers that watch the operator config map and need to ignore unrelated ConfigMap churn.

Risks: the function is unexported and generic, so usage depends on same-package integration. Updates are keyed only by name, not namespace; callers must scope watches appropriately. Creates are ignored, meaning a newly created settings ConfigMap will not trigger through this predicate unless another path loads it.

Test signals: no direct test file in this subset; behavior is simple but create-ignore semantics should be covered where used by controllers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/reporting.go -->
# sources/control-plane/rook/pkg/operator/ceph/reporting/reporting.go

Purpose: shared reporting helpers for reconcile outcomes, events, deletion-blocked conditions, and status-condition retries.

Important APIs/types/functions: `statusConditionGetter`, `objIsNil`, `objKindOrBestGuess`, `copyObject`, `ReportReconcileResult`, `GenerateConditionBlockedDueToDependents`, `GenerateConditionUnblockedDueToDependents`, `ReportDeletionBlockedDueToDependents`, `UpdateStatusConditionsWithRetry`, and `ReportDeletionNotBlockedDueToDependents`.

Control flow: `ReportReconcileResult` derives a kind, deep-copies or materializes typed-nil objects, fills missing name/namespace from request, logs and emits either `ReconcileFailed`, `ReconcileRequeuing`, or `ReconcileSucceeded` events, and returns controller-runtime result/error. If both an error and a non-zero result are provided, it records the failure but suppresses the error so controller-runtime honors delayed requeue. Dependent-deletion helpers build conditions and update status under retry.

State and persistence behavior: writes Kubernetes events via `events.EventRecorder` and status conditions through `UpdateStatusCondition`. It does not store data outside the target object status/events.

Dependencies/integration: depends on capnslog, Ceph condition types, `dependents.DependentList`, controller-runtime client, Kubernetes events, and retry-on-conflict.

Risks: reflection around typed nil is essential; callers passing non-client objects would panic on type assertions. Suppressing errors when result is non-zero is intentional but easy for new callers to misunderstand. Event emission for empty placeholder objects relies on name/namespace backfill.

Test signals: `reporting_test.go` verifies kind inference, typed nil handling, success/error/requeue event text, and delayed requeue with logged event but nil returned error.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/reporting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/reporting_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/reporting/reporting_test.go

Purpose: exercises reconcile reporting helper behavior, especially log/event side effects and nil/empty object handling.

Important APIs/types/functions: `Test_objKindOrBestGuess` and `TestReportReconcileResult`.

Control flow: `Test_objKindOrBestGuess` checks kind extraction from TypeMeta, fallback from Go type, wrong API kind preservation, untyped nil, and typed nil. `TestReportReconcileResult` creates a fake logger/recorder and verifies successful reconcile, reconcile with error, requeue without error, error plus delayed requeue, success with empty object metadata, and failure with typed-nil object.

State and persistence behavior: no Kubernetes API persistence; state is captured in the fake recorder channel and capnslog buffer.

Dependencies/integration: uses Ceph API objects, controller-runtime reconcile request/result, fake event recorder, capnslog formatter, and testify.

Risks: event strings are exact-match assertions, so legitimate message changes require test updates. Dependent deletion reporting helpers are not tested here.

Test signals: strong coverage for the critical controller contract that a non-zero delayed requeue result suppresses returned error while still emitting failure information to users.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/reporting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/status.go -->
# sources/control-plane/rook/pkg/operator/ceph/reporting/status.go

Purpose: thin helpers for writing object status and status conditions through controller-runtime clients.

Important APIs/types/functions: `UpdateStatus` and `UpdateStatusCondition`.

Control flow: `UpdateStatus` attempts `client.Status().Update` with a background context and falls back to full-object `client.Update` only when Status update returns NotFound. `UpdateStatusCondition` applies each new condition through `cephv1.SetStatusCondition` to the object condition slice, then calls `UpdateStatus`, wrapping errors with kind/name context.

State and persistence behavior: persists the target object's status subresource or, for not-yet-created status behavior, the whole object. Mutates the in-memory object condition slice before writing.

Dependencies/integration: uses controller-runtime client, Kubernetes NotFound detection, Ceph condition helpers, and the `statusConditionGetter` interface from `reporting.go`.

Risks: uses `context.Background()` instead of caller-provided context, so status writes are detached from reconcile cancellation. The fallback only covers NotFound from status update, not status-subresource unsupported errors unless fake clients represent them as NotFound. Condition ordering and replacement are delegated to `cephv1.SetStatusCondition`.

Test signals: `status_test.go` checks status update when status is initially nil, ordinary phase update, adding one condition, adding two condition types, and replacing an existing condition.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/status_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/reporting/status_test.go

Purpose: verifies status and condition update helpers against controller-runtime fake clients.

Important APIs/types/functions: `TestUpdateStatus` and `TestUpdateStatusCondition`.

Control flow: `TestUpdateStatus` first covers an object whose status is initially unset, then covers a block pool status phase transition to Ready. `TestUpdateStatusCondition` sets up an object store and block pool, then subtests adding a new deletion-blocked condition, adding two distinct conditions to a block pool, and updating an existing condition to a different status/reason/message.

State and persistence behavior: fake client object tracker persists status mutations, and tests fetch objects after each update to validate persisted data rather than only local object mutation.

Dependencies/integration: uses Ceph API schemes/objects, controller-runtime fake client, Kubernetes condition statuses, and testify.

Risks: the first subtest prints an object copy but does not assert much about it. Conflict retry, status-subresource failure modes, and background-context cancellation behavior are not covered.

Test signals: confirms that condition insertion and replacement flow through `cephv1.SetStatusCondition` and that persisted status phase changes can be observed by a fresh client get.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/reporting/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/containers.go -->
# sources/control-plane/rook/pkg/operator/ceph/test/containers.go

Purpose: shared test assertions for Ceph container specs generated by Rook operator code.

Important APIs/types/functions: `ContainersTester`, `(*PodSpecTester).Containers`, `AssertArgsContainCephRequirements`, `RequireAdditionalEnvVars`, `AssertEnvVarsContainCephRequirements`, `AssertArgReferencesMatchEnvVars`, `AssertCephImagesMatch`, `RunFullSuite`, `isCephCommand`, `argEnvReferences`, `varNames`, nonrequired set helpers, and `FindDuplicateEnvVars`.

Control flow: the tester aggregates init and regular containers from a pod spec, skips non-Ceph command containers for Ceph-specific checks, verifies required Ceph flags and `--fsid`, verifies required env vars and their sources, checks env references in args match declared env vars, verifies no unexpected extra env refs/vars outside the required set, checks image equality, and detects duplicate env vars.

State and persistence behavior: no persistence. The package-level `requiredEnvVars` slice is mutable through `RequireAdditionalEnvVars`, which affects subsequent checks in the same process.

Dependencies/integration: uses Kubernetes core container types and testify assertions. It is designed for other operator tests to reuse through `PodSpecTester`.

Risks: `isCephCommand` indexes `command[0]` and will panic on containers with empty command slices. `RequireAdditionalEnvVars` mutates global state and its comment says single-test use, but it does not automatically restore values. Resource limit arguments are accepted in `RunFullSuite` but not directly used in this file.

Test signals: no local tests in this subset; value is indirect through pod-spec tests in other packages.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/info.go -->
# sources/control-plane/rook/pkg/operator/ceph/test/info.go

Purpose: package marker and documentation holder for shared Rook-Ceph operator test helpers.

Important APIs/types/functions: no exported declarations beyond the `test` package itself.

Control flow: none.

State and persistence behavior: none.

Dependencies/integration: establishes package documentation alongside helper files like `containers.go`, `podspec.go`, `podtemplatespec.go`, and `spec.go`.

Risks: no runtime risk. Any package-level documentation here may be missed because it is only the package comment and has no code.

Test signals: no tests are needed for this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/podspec.go -->
# sources/control-plane/rook/pkg/operator/ceph/test/podspec.go

Purpose: shared assertions for Ceph pod specs, layering Ceph-specific expectations over generic operator pod-spec tests.

Important APIs/types/functions: `PodSpecTester`, `(*PodTemplateSpecTester).Spec`, `NewPodSpecTester`, `AssertVolumesMeetCephRequirements`, `AssertRestartPolicyAlways`, `AssertChownContainer`, `AssertPriorityClassNameMatch`, `RunFullSuite`, `allContainers`, and `containerExists`.

Control flow: `RunFullSuite` builds generic resource expectations, runs generic pod spec checks, then validates required Ceph volumes, restart policy, required chown init container by daemon type, priority class, and all Ceph container requirements. Volume validation computes daemon keyring secret names with special cases for mon and filesystem mirror daemons and validates volume source kinds for data/config/keyring volumes.

State and persistence behavior: no persistence; all checks are in-memory assertions on `v1.PodSpec`.

Dependencies/integration: depends on Ceph daemon type constants, generic `pkg/operator/test` pod-spec helpers, Kubernetes core types, and `containers.go`.

Risks: expected volume-source rules are encoded by daemon type and can become stale as daemon specs evolve. `allContainers` appends to the init container slice, which can reuse backing arrays but only returns a combined slice for reads here.

Test signals: no direct tests in this subset; these helpers are intended to raise consistency failures in many daemon-specific unit tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/podspec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/podtemplatespec.go -->
# sources/control-plane/rook/pkg/operator/ceph/test/podtemplatespec.go

Purpose: top-level test helper for validating complete Ceph `PodTemplateSpec` objects.

Important APIs/types/functions: `PodTemplateSpecTester`, `NewPodTemplateSpecTester`, `AssertLabelsContainCephRequirements`, and `RunFullSuite`.

Control flow: `RunFullSuite` first checks labels on the pod template, then delegates to `Spec().RunFullSuite` for pod spec, volumes, containers, resources, restart policy, chown container, and priority class checks.

State and persistence behavior: no persistence; wraps an in-memory pointer to a `v1.PodTemplateSpec`.

Dependencies/integration: depends on `spec.go` label checks and `podspec.go` pod spec checks.

Risks: this helper assumes caller supplies all daemon identity strings correctly; wrong expectations can make tests pass against wrong labels if both code and test use the same bad inputs.

Test signals: no local tests. Its effectiveness comes from daemon-specific tests using the shared full suite.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/podtemplatespec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/test/spec.go

Purpose: shared label assertions for Ceph operator resources.

Important APIs/types/functions: `AssertLabelsContainCephRequirements`.

Control flow: the helper first delegates generic Rook label checks to `optest.AssertLabelsContainRookRequirements`, then converts the label map to `key=value` strings and asserts it contains expected Kubernetes recommended app labels, Ceph daemon identity labels, operator namespace, and Rook cluster namespace.

State and persistence behavior: no persistence. Reads `POD_NAMESPACE` from the environment to validate the operator namespace label.

Dependencies/integration: depends on generic operator test helpers, `os.Getenv`, Kubernetes label conventions, and testify assertions.

Risks: environment dependence means tests must set `POD_NAMESPACE` consistently. It validates subset containment, so extra labels are allowed.

Test signals: no direct tests in this subset; consumers get consistency checks for Ceph pod/deployment/daemonset label generation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/test/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/version/version.go -->
# sources/control-plane/rook/pkg/operator/ceph/version/version.go

Purpose: defines Ceph version representation, supported-release constants, parsing from `ceph --version`, comparisons, and external-cluster compatibility validation.

Important APIs/types/functions: `CephVersion`, `Minimum`, `Squid`, `Tentacle`, `Umbrella`, `supportedVersions`, regex patterns, `String`, `CephVersionFormatted`, `ReleaseName`, `ExtractCephVersion`, `Supported`, `Unsupported`, `isRelease`, `isExactly`, `IsAtLeast`, release-specific helpers, `IsIdentical`, `IsSuperior`, `IsInferior`, and `ValidateCephVersionsBetweenLocalAndExternalClusters`.

Control flow: parsing uses regexes to extract major/minor/extra, optional numeric build suffix, and optional commit ID. Support checks match by major release, while unsupported checks match exact versions from a currently empty list. Comparison helpers manually compare major, minor, extra, build, and in `IsSuperior`, any commit ID difference at otherwise equal version counts as superior. External validation rejects external versions before Ceph 15, rejects local versions higher than external, warns but allows external minor/major versions higher than local, and allows identical versions.

State and persistence behavior: no persistence. Package globals define current supported release policy.

Dependencies/integration: used by operator controllers and Ceph client code to gate features and validate cluster compatibility. Depends only on regexp/strconv/fmt, capnslog, and pkg/errors.

Risks: supported versions must be maintained with Ceph release lifecycle. `IsSuperior` treating different commit IDs as superior is asymmetric and may surprise callers. `Unsupported` comment says "supported" but checks unsupported list. Build regex only captures numeric build after a hyphen; other version forms intentionally fail.

Test signals: `version_test.go` covers formatting, release names, parsing release/development builds, failed no-version parsing, support checks, comparisons, external-version validation, and empty unsupported list behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/version/version_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/version/version_test.go

Purpose: verifies Ceph version formatting, parsing, support decisions, ordering, and external-cluster compatibility rules.

Important APIs/types/functions: `TestToString`, `TestCephVersionFormatted`, `TestReleaseName`, `extractVersionHelper`, `TestExtractVersion`, `TestSupported`, `TestIsRelease`, `TestVersionAtLeast`, `TestVersionAtLeastX`, `TestIsIdentical`, `TestIsSuperior`, `TestIsInferior`, `TestValidateCephVersionsBetweenLocalAndExternalClusters`, and `TestCephVersion_Unsupported`.

Control flow: parse tests feed release output, multiline shell output, development build output, no-version development output, and round-trip serialized output. Comparison tests check major/minor/extra/build relationships. External validation tests allow identical, allow external major/minor ahead, and reject local ahead. Unsupported tests assert current versions are not in the unsupported list.

State and persistence behavior: no persistence; all tests are pure in-memory assertions.

Dependencies/integration: uses testify and package-level version constants/regex behavior.

Risks: current tests do not cover commit-ID superiority/inferiority asymmetry deeply, Umbrella `IsAtLeast` helpers, or future unsupported-version entries. Duplicate test case names in `TestCephVersion_Unsupported` are harmless but reduce clarity.

Test signals: strong guard for parser compatibility with real `ceph --version` outputs and release policy changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/discover/discover.go -->
# sources/control-plane/rook/pkg/operator/discover/discover.go

Purpose: manages the rook-discover DaemonSet and provides helpers to read discovered devices and mark selected devices as in use.

Important APIs/types/functions: constants for operator settings and ConfigMap names, `Discover`, `New`, `Start`, `createDiscoverDaemonSet`, `getLabels`, `ListDevices`, `ListDevicesInUse`, `matchDeviceFullPath`, `GetAvailableDevices`, and `Stop`.

Control flow: `Start` creates or updates the DaemonSet. DaemonSet creation builds privileged pod spec with `/dev`, `/sys`, `/run/udev` host paths, discovery interval args, optional `--use-ceph-volume`, parsed resource settings, owner refs from the operator pod, tolerations from legacy and YAML settings, optional node affinity, optional pod label override preserving `app`, loop-device env, host network setting, priority class, and service account. `ListDevices` waits up to 30 attempts for discovery ConfigMaps, optionally maps hostname to node name, unmarshals local disk JSON by node, and skips malformed entries. `GetAvailableDevices` joins requested devices, regex filters, or `useAllDevices` against discovered devices, marks claimed devices in a cluster/node ConfigMap, and returns Ceph device specs.

State and persistence: persistent state is the DaemonSet and ConfigMaps labeled as discovered devices or claimed devices. Claimed device ConfigMaps are created or updated with JSON disk lists. Operator settings are read from environment/configmap through `k8sutil.GetOperatorSetting`.

Dependencies/integration: integrates Kubernetes client-go, Rook discovery daemon labels/data keys, `k8sutil` settings and object helpers, `opcontroller` pod security/network helpers, and `sys.LocalDisk` JSON.

Risks: `ListDevices` has fixed retry/sleep timings and can wait a long time. The current loop over devices in use has a TODO and does not actually filter them from `nodeDevices` because it breaks only the inner loop and still appends. Regex errors are silently treated as non-matches. ConfigMap updates for claimed devices are not conflict-retried.

Test signals: `discover_test.go` covers DaemonSet creation/update with priority class and tolerations, and available-device lookup plus claimed-device persistence for a requested device.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/discover/discover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/discover/discover_test.go -->
# sources/control-plane/rook/pkg/operator/discover/discover_test.go

Purpose: validates discover DaemonSet construction and device-selection behavior against fake Kubernetes clients.

Important APIs/types/functions: `TestStartDiscoveryDaemonset` and `TestGetAvailableDevices`.

Control flow: `TestStartDiscoveryDaemonset` sets operator env vars, creates a fake operator pod, starts discovery, fetches the DaemonSet, and asserts namespace/name, service account, priority class, privileged root container, volumes/mounts/env count, image, and tolerations. It then sets YAML tolerations and calls `Start` again to exercise update-on-already-exists behavior. `TestGetAvailableDevices` creates a discovery ConfigMap with local disk JSON, calls `ListDevices`, then calls `GetAvailableDevices` twice for a requested `sdc` plus missing `foo`.

State and persistence behavior: fake ConfigMaps and DaemonSets persist in the fake client. `GetAvailableDevices` writes a claimed-device ConfigMap, and the second call confirms idempotent behavior returns the same selected device.

Dependencies/integration: uses Rook test fake client, discovery daemon label/data constants, `k8sutil` env var names, Ceph device API types, and large realistic `sys.LocalDisk` JSON.

Risks: tests do not cover node affinity, pod label override, loop-device env, malformed YAML, no configmaps timeout, in-use filtering, regex-only selection, use-all-devices, full-path matching, or Stop deletion.

Test signals: establishes the core DaemonSet shape and validates the discovery ConfigMap to selected Ceph device path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/discover/discover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/cmdreporter/cmdreporter.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/cmdreporter/cmdreporter.go

Purpose: builds and runs Kubernetes Jobs that execute Rook's `cmd-reporter` utility and return stdout/stderr/retcode through a ConfigMap.

Important APIs/types/functions: constants `CmdReporterContainerName`, `CopyBinariesInitContainerName`, `CopyBinariesMountDir`; `CmdReporterInterface`; `CmdReporter`; `cmdReporterCfg`; `New`; `Job`; `Run`; `newWatcher`; `waitForConfigMap`; `initJobSpec`; `initContainers`; `container`; `needToCopyBinaries`; `copyBinariesVolAndMount`; `newInt32`; and `MockCmdReporterJob`.

Control flow: `New` validates required inputs, builds a job spec, and returns a reporter. Job spec creation optionally adds an init container to copy the rook binary when the run image differs from the rook image, builds the cmd-reporter container args using `util.CommandToCmdReporterFlagArgument`, adds host network, default service account, labels, rook version label, owner reference, and shared EmptyDir. `Run` deletes any stale result ConfigMap, runs a replaceable job, watches for the result ConfigMap with timeout and watcher restart on channel close, reads stdout/stderr/retcode keys, deletes the job and result ConfigMap best-effort, and returns command output even for nonzero retcode.

State and persistence: creates/deletes Kubernetes Jobs and result ConfigMaps. Uses ConfigMap presence as completion signal and ConfigMap data as output persistence.

Dependencies/integration: depends on client-go, k8sutil delete/job/version/owner helpers, Ceph resource defaults, and daemon util command encoding and ConfigMap key names.

Risks: any ConfigMap event on the watched name is treated as completion without validating data until later. Cleanup failures are logged but not returned. `Run` requires stale ConfigMap deletion to complete first, which can block on deletion behavior. No direct tests are in this subset; behavior depends on integration tests elsewhere.

Test signals: not directly tested here. The `MockCmdReporterJob` helper indicates other packages can test generated job specs without input validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/cmdreporter/cmdreporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/configmap.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/configmap.go

Purpose: utility functions for ConfigMap deletion, create/update, and loading operator settings from the operator config ConfigMap into environment variables.

Important APIs/types/functions: package variable `loadedOperatorSettings`, `DeleteConfigMap`, `CreateOrUpdateConfigMap`, `GetOperatorSetting`, and `ApplyOperatorSettingsConfigmap`.

Control flow: `DeleteConfigMap` adapts ConfigMap delete/get operations to generic `DeleteResource` with foreground, zero-grace deletion defaults. `CreateOrUpdateConfigMap` gets by name, creates on NotFound, or updates existing Data and OwnerReferences. `GetOperatorSetting` warns when settings are read before the configmap load flag is set, then returns an environment value if present or the provided default. `ApplyOperatorSettingsConfigmap` reads `rook-ceph-operator-config` in `POD_NAMESPACE`, sets each data key into process env, and marks settings loaded even when the ConfigMap is absent.

State and persistence: writes ConfigMaps and process environment variables. `loadedOperatorSettings` is process-global state that affects warnings only.

Dependencies/integration: depends on client-go CoreV1 ConfigMaps, generic `DeleteResource`, Kubernetes NotFound errors, and env var constants from k8sutil.

Risks: setting configmap data into environment mutates global process state and can affect tests or later reconciles. Existing labels/annotations are not updated in `CreateOrUpdateConfigMap`, only data and owner refs. `GetOperatorSetting` cannot distinguish unset from intentionally empty env values because `LookupEnv` returns true for empty strings.

Test signals: `configmap_test.go` covers delete with wait, env/default/configmap precedence, configmap application, and create/update data mutation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/configmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/configmap_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/configmap_test.go

Purpose: tests ConfigMap deletion, operator-setting loading, and create-or-update behavior.

Important APIs/types/functions: `TestDeleteConfigMap`, `TestGetOperatorSetting`, and `TestCreateOrUpdateConfigMap`.

Control flow: deletion test creates a ConfigMap, calls `DeleteConfigMap` with wait and timeout error enabled, then asserts a later get returns NotFound. Operator setting test checks default before config load, env override, configmap load into env, unset handling after load, missing setting default, and env override for another key. Create/update test creates a ConfigMap through helper, verifies data, mutates input data, calls helper again, and verifies updated data.

State and persistence behavior: fake Kubernetes client persists ConfigMaps. Tests mutate process env via `t.Setenv` and `os.Unsetenv`.

Dependencies/integration: uses client-go fake client, Kubernetes API error helpers, and testify.

Risks: package-global `loadedOperatorSettings` can leak between tests in the same package. Tests do not cover owner references on create/update, retrieval errors other than NotFound, or labels/annotations preservation.

Test signals: good coverage for core user-facing behavior: settings precedence and idempotent ConfigMap updates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/configmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/customresource.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/customresource.go

Purpose: defines a simple metadata struct for Kubernetes custom resources.

Important APIs/types/functions: `CustomResource` with fields `Name`, `Plural`, `Group`, `Version`, `Kind`, and `APIVersion`.

Control flow: none. The struct is a data container.

State and persistence behavior: none by itself. Instances can describe CRD/API metadata for other code paths.

Dependencies/integration: no imports. Package comment says Kubernetes operator kit.

Risks: no validation methods are attached, so callers must ensure fields are complete and consistent.

Test signals: no direct tests in this subset; behavior is structural only.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/customresource.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/delete.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/delete.go

Purpose: generic deletion helper logic shared by Kubernetes resource-specific delete wrappers.

Important APIs/types/functions: `BaseKubernetesDeleteOptions`, `DeleteOptions`, test variable `unitTestRetryIntervalRecord`, and `DeleteResource`.

Control flow: `BaseKubernetesDeleteOptions` returns foreground deletion with zero grace period. `DeleteResource` invokes caller-supplied delete, handles NotFound as success unless `MustDelete`, returns errors for other delete failures, optionally waits by repeatedly invoking caller-supplied verify until it returns NotFound, and either returns or logs timeout depending on `ErrorOnTimeout`. Retry count/interval come from opts with defaults supplied by the resource wrapper.

State and persistence behavior: no direct Kubernetes access; persistence is through injected delete/verify closures. Records retry interval in a package variable for tests.

Dependencies/integration: used by `DeleteConfigMap` and other delete helpers. Depends on Kubernetes API error classification and `WaitOptions` from elsewhere in k8sutil.

Risks: callers must provide a verify function where NotFound means deleted; other errors do not break early and are reported only at timeout. Passing nil `opts` would panic because fields are accessed directly. Logs use seconds formatting, losing sub-second precision in messages.

Test signals: `delete_test.go` covers delete errors, NotFound with/without MustDelete, no-wait default, wait timeout with and without error, successful wait after retries, and explicit retry option overrides.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/delete_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/delete_test.go

Purpose: validates the generic `DeleteResource` state machine with stubbed delete and verify functions.

Important APIs/types/functions: `TestDeleteResource`.

Control flow: the test configures delete to return generic errors, NotFound, or nil, then checks MustDelete behavior, idempotent missing-resource behavior, no-wait behavior, timeout behavior with `ErrorOnTimeout` true and false, successful verification after retries, and override of retry count/interval from `DeleteOptions`.

State and persistence behavior: no Kubernetes objects are created. Local counters model resource existence and package variable `unitTestRetryIntervalRecord` records selected retry interval.

Dependencies/integration: uses Kubernetes API NotFound errors, schema group resource, time durations, and testify.

Risks: no test for nil `DeleteOptions`/`WaitOptions`, verify returning transient API errors followed by NotFound, or context cancellation because `DeleteResource` has no context parameter.

Test signals: strong coverage for the helper's intended deletion and wait contract.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/deployment.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/deployment.go

Purpose: Kubernetes Deployment and CronJob utilities for image lookup, declarative update, rollout waiting, owner reference lookup, labeling, and create/update operations.

Important APIs/types/functions: `GetDeploymentImage`, `GetDeploymentSpecImage`, `UpdateDeploymentAndWait`, `WaitForDeploymentToStart`, `DeploymentNames`, `DeploymentsUpdated`, `Failure`, `Failures.CollatedErrors`, `UpdateMultipleDeployments`, `WaitForDeploymentsToUpdate`, `UpdateMultipleDeploymentsAndWait`, `deploymentIsDoneUpdating`, `progressDeadlineExceeded`, `updateDeployment`, `GetDeployments`, `DeleteDeployment`, `GetDeploymentOwnerReference`, version/label helpers, `CreateDeployment`, `CreateOrUpdateDeployment`, `CreateOrUpdateCronJob`, and `maxInt32Ptr`.

Control flow: update helpers compare desired vs current objects using `k8s-objectmatcher` patches, annotate last-applied hash, update only changed deployments, and record old observed generation. Rollout wait loops list deployments, detects progress deadline exceeded, checks observed generation plus updated/ready replicas, and times out based on the max progress deadline. Single-deployment update additionally calls a verification callback before stop and before continuing. Create/update helpers create with last-applied annotation and update on AlreadyExists.

State and persistence: reads and writes Kubernetes Deployments, CronJobs, Jobs, Pods, ReplicaSets, labels, annotations, and owner references through client-go. No durable state beyond Kubernetes objects.

Dependencies/integration: depends on client-go, Rook `clusterd.Context`, objectmatcher patch annotations, `util.RetryWithTimeout`, version label helpers, and generic deletion helpers.

Risks: rollout readiness check requires both updated and ready replicas greater than zero, which may not represent desired zero-replica deployments. `Failures.CollatedErrors` builds errors in reverse-ish order with a trailing nil string. Long waits use package globals and sleeps. Create/update directly updates full objects, so resourceVersion/spec conflicts must be managed by callers.

Test signals: `deployment_test.go` covers multi-deployment update and wait integration, no-change detection, missing deployments, rollout success, timeouts, list errors, missing listed deployments, progress deadline exceeded, and `maxInt32Ptr`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/deployment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/deployment_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/deployment_test.go

Purpose: exercises multi-deployment update and rollout-wait helpers with fake clients and controlled list functions.

Important APIs/types/functions: `TestUpdateMultipleDeploymentsAndWait`, `TestUpdateMultipleDeployments`, `TestWaitForDeploymentsToUpdate`, `Test_maxInt32Ptr`, `newInt32`, and `createDeploymentOrDie`.

Control flow: the integration test updates three deployments, leaves one unchanged, includes one missing deployment, and simulates one progress-deadline failure and one timeout. `TestUpdateMultipleDeployments` verifies empty inputs, successful updates, no-change skip behavior, progress deadline aggregation, and missing-deployment failures. `TestWaitForDeploymentsToUpdate` uses list functions that advance status over calls or return errors to cover success, timeout, never-listed deployment, list failure, and progress deadline exceeded.

State and persistence behavior: fake clientset stores deployments; a reactor records update actions. Package global wait period/timeout are temporarily shortened and restored.

Dependencies/integration: uses client-go fake/reactor APIs, Kubernetes deployment statuses/conditions, and testify.

Risks: tests cover the multi-update path but not `UpdateDeploymentAndWait`, image lookup, owner reference discovery, delete deployment, label helpers, create/update deployment, or cronjob helpers.

Test signals: strong coverage of the rollout waiting algorithm and failure aggregation for batch deployment updates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/deployment_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/endpoint.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/endpoint.go

Purpose: create-or-update helper for Kubernetes `EndpointSlice` resources.

Important APIs/types/functions: `CreateOrUpdateEndpointSlice`.

Control flow: attempts to create the given EndpointSlice in the target namespace. On AlreadyExists, updates the full provided definition. Non-AlreadyExists create errors and update errors are wrapped with endpoint slice name context.

State and persistence behavior: writes EndpointSlice objects through the discovery v1 client.

Dependencies/integration: client-go DiscoveryV1 EndpointSlices, Kubernetes API error helpers, and k8sutil logger.

Risks: update uses the provided object directly, so callers must ensure resourceVersion and desired metadata are valid for updates. No conflict retry. Namespace is a separate parameter even though the object also has a namespace field; mismatches could be confusing.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/job.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/job.go

Purpose: helpers for replaceable Kubernetes Jobs, batch job deletion, and Rook version labeling on Jobs.

Important APIs/types/functions: `RunReplaceableJob`, `DeleteBatchJob`, and `AddRookVersionLabelToJob`.

Control flow: `RunReplaceableJob` checks for an existing job. If it exists and is active and caller did not request deletion, it leaves it running. Otherwise it deletes the old job with wait, then creates the new job. `DeleteBatchJob` foreground-deletes with zero grace, ignores NotFound, optionally polls up to 30 times at 3 seconds for NotFound, and logs timeout as warning without returning an error. `AddRookVersionLabelToJob` initializes labels and delegates to the shared rook-version label sanitizer.

State and persistence behavior: creates/deletes Kubernetes Jobs and mutates Job labels in memory before persistence by callers.

Dependencies/integration: client-go BatchV1 Jobs, Kubernetes API error helpers, and deployment/k8sutil label helpers.

Risks: delete wait timeout is non-fatal, so a later create can still fail if the old job remains. Existing-job get errors other than NotFound are only warned before create is attempted. The wait loop is fixed at up to roughly 90 seconds.

Test signals: no direct tests in this subset; `cmdreporter.Run` depends on this behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/k8sutil.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/k8sutil.go

Purpose: core Kubernetes utility constants and helpers for stable hashing, safe resource names, foreground deletion waiting, and Rook version label sanitization.

Important APIs/types/functions: constants for namespaces, data dirs, env vars, labels, and default service account; `Hash`, `TruncateNodeNameForJob`, `TruncateNodeName`, `truncateNodeName`, `deleteResourceAndWait`, `addRookVersionLabel`, and `validateLabelValue`.

Control flow: `Hash` returns the first 16 bytes of SHA-256 as hex and is documented as stable across versions. Name truncation hashes the node name when format plus node name exceed DNS label length, with a stricter max for Jobs due to Kubernetes pod-name generation behavior. `deleteResourceAndWait` foreground-deletes a resource and polls for NotFound up to 45 times. Version label sanitization replaces invalid label characters, trims invalid leading/trailing characters, and truncates to 63 characters.

State and persistence behavior: no direct persistent storage except deletion via injected closures. Hash outputs are a compatibility contract.

Dependencies/integration: capnslog, Rook version string, Kubernetes API errors, meta delete options, and Kubernetes label validation constants.

Risks: changing `Hash` or truncation behavior would break stable object-name mappings. `deleteResourceAndWait` has fixed sleeps and no context. `validateLabelValue` truncates after trimming but does not re-trim after truncation, so a truncated value could theoretically end with an invalid separator depending on input.

Test signals: `k8sutil_test.go` guards truncation outputs for node/job names and label value sanitization.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/k8sutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/k8sutil_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/k8sutil_test.go

Purpose: unit tests for stable node-name truncation and Kubernetes label value sanitization.

Important APIs/types/functions: `TestTruncateNodeName`, `TestTruncateJobName`, and `TestValidateLabelValue`.

Control flow: truncation tests use maps keyed by expected output to validate short names, max-length names, long names hashed to a stable 32-character value, job-specific stricter length behavior, and formats whose fixed text is too long for the final DNS limit. Label tests validate empty strings, valid versions, replacement of `+` with `-`, 63-character truncation, and trimming leading/trailing punctuation.

State and persistence behavior: no persistence.

Dependencies/integration: uses testify and the exact stable hash produced by `Hash`.

Risks: map iteration order is nondeterministic but tests are independent. Expected hashes form a compatibility guard, so intentional hash changes would require careful migration.

Test signals: strong signal for backwards-compatible object naming, which other controllers rely on for stable Kubernetes resources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/k8sutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/kvstore.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/kvstore.go

Purpose: implements a simple ConfigMap-backed key-value store abstraction.

Important APIs/types/functions: `ConfigMapKVStore`, `NewConfigMapKVStore`, `GetValue`, `SetValue`, `SetValueWithLabels`, `GetStore`, and `ClearStore`.

Control flow: `GetValue` gets the ConfigMap and returns a NotFound error if the key is absent. `SetValue` delegates to `SetValueWithLabels`. `SetValueWithLabels` gets the ConfigMap; on NotFound it creates one with initial data, optional labels, and controller owner reference; otherwise it mutates `Data[key]` and updates the ConfigMap. `GetStore` returns the ConfigMap `Data` map. `ClearStore` deletes the ConfigMap and ignores NotFound.

State and persistence behavior: persists data in Kubernetes ConfigMaps in the configured namespace. Owner references are applied only when creating a new store.

Dependencies/integration: depends on client-go CoreV1 ConfigMaps, Kubernetes NotFound errors, schema group resource for key-not-found, and k8sutil `OwnerInfo`.

Risks: updating an existing ConfigMap assumes `cm.Data` is non-nil; a nil Data map would panic on assignment. No conflict retry on update. `GetStore` returns the underlying map from the fetched object, so callers can mutate the map locally without persistence unless they call Set/Update.

Test signals: `kvstore_test.go` covers missing store/key, get, set-create, set-update, get-store, and clear-store behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/kvstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/kvstore_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/kvstore_test.go

Purpose: tests ConfigMap-backed key-value store behavior.

Important APIs/types/functions: `TestGetValueStoreNotExist`, `TestGetValueKeyNotExist`, `TestGetValue`, `TestSetValueStoreNotExist`, `TestSetValueUpdate`, `TestGetStoreNotExist`, `TestGetStore`, `TestClearStoreNotExist`, `TestClearStore`, and helper `newKVStore`.

Control flow: tests verify NotFound for missing store and missing key, successful get, automatic store creation on set, value update on existing store, whole-store retrieval, idempotent clear of missing store, and delete-on-clear of existing store. `newKVStore` attaches namespace/name to input ConfigMaps, builds a fake client, creates owner info, and returns a store.

State and persistence behavior: fake ConfigMaps persist in the fake client. Tests validate behavior by calling store methods after mutations.

Dependencies/integration: client-go fake client, Kubernetes NotFound helpers, runtime objects, owner refs, and testify.

Risks: tests do not cover `SetValueWithLabels`, owner reference contents, nil `Data` map on existing ConfigMap, update conflicts, or labels on existing-store updates.

Test signals: good coverage for the normal CRUD contract used by operator components that need small persisted key/value state.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/kvstore_test.go -->
