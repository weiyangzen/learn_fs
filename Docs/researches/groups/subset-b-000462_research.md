# Research: subset-b-000462

This grouped report covers Rook Ceph operator code for RGW object users, object zones, zonegroups, operator bootstrap, and block pool reconciliation. Each section is source-tree aligned and intended to be split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/user/controller.go

## Purpose

This file implements the `CephObjectStoreUser` controller for RGW/S3 users. It reconciles Kubernetes `CephObjectStoreUser` CRs into Ceph RGW admin-ops users, maintains generated access-key Secrets, supports explicit user keys from Kubernetes Secrets, validates account-linked IAM display names, and removes RGW users during CR deletion. The controller is part of the object store integration path and depends on a ready `CephCluster` and an initialized `CephObjectStore`.

## Important APIs, Types, and Functions

- `ReconcileObjectStoreUser` holds the controller-runtime client, scheme, clusterd context, RGW admin ops context, advertise endpoint, cluster spec/info, operator manager context, and event recorder.
- `Add`, `newReconciler`, and `add` register the controller, watch `CephObjectStoreUser` resources, watch owned generated Secrets, index `spec.keys` Secret references, and watch referenced Secrets for resource-version changes or deletion.
- `Reconcile` wraps `reconcile` with panic recovery, status failure updates, event reporting, and `reporting.ReportReconcileResult`.
- `reconcile` is the main state machine: fetch CR, add finalizer, check cluster readiness, load cluster info, initialize object-store admin context, handle deletion, generate RGW user config, resolve account references, create/update Ceph user, update `.status.keys`, reconcile generated credentials Secret, and mark Ready.
- `createOrUpdateCephUser` is the core Ceph-side idempotency path. It gets or creates the RGW user, modifies scalar fields when `isUserSync` says they drifted, reconciles user caps, sets quota, chooses target keys, and calls `reconcileUserKeys`.
- `generateUserConfig` builds `admin.User` from the CR: ID, display name, default max buckets, quota max buckets, capabilities string, and operation mask.
- `initializeObjectStoreContext` calls `object.InitializeObjectStoreContext`, enforces cross-namespace user allowance using `allowUsersInNamespaces`, stores the advertised endpoint, and records `AdminOpsContext`.
- `resolveAccountRef` loads a same-namespace `CephObjectStoreAccount`, verifies store match, requires Ready status and non-empty account ID, and returns a short requeue result while the account is absent or not ready.
- `generateCephUserSecret`, `reconcileCephUserSecret`, `generateCephUserSecretName`, and `generateStatusInfo` maintain the user-facing Kubernetes Secret and `.status.info.secretName`.
- `getSecretValue`, `generateUserKeySpec`, `reconcileUserKeys`, and `updateKeyStatus` implement explicit key pairs and status backreferences to referenced Secrets.
- `validateUser`, `clusterStoreNamespace`, `deleteUser`, `generateUserCaps`, `userInNamespaceAllowed`, and `isUserSync` are local validation/utility helpers.

## Control Flow

The controller setup first registers a direct CR watch. It also watches generated `corev1.Secret` objects owned by a `CephObjectStoreUser`, so generated credential Secret changes can be restored. For explicit key references, the controller indexes all access-key and secret-key reference names into `spec.keys.secretNames`; a Secret change or deletion maps back to all users in the same namespace that reference that Secret, forcing immediate reconciliation failures when a referenced Secret disappears.

On reconcile, missing CRs are ignored. Existing CRs receive a finalizer. The cluster namespace is `spec.clusterNamespace` when set, otherwise the user namespace. If the cluster is not ready, the controller only removes the finalizer for deleting users after the cluster has disappeared; otherwise it returns the cluster readiness requeue result. Once cluster info loads, the object store context must initialize. If initialization fails while deleting, the finalizer is removed because there is no usable object-store context to clean up; if not deleting, the reconcile requeues on object-store readiness.

For non-deleted resources, `generateUserConfig` creates the target `admin.User`. If `spec.keys` is non-empty, `generateUserKeySpec` reads all referenced Secret values and assigns explicit target keys. Validation runs after config generation and checks name, namespace, store, and IAM-compatible display names for account users. Account references add `AccountID` to the RGW user only when the account CR exists, belongs to the same store, is Ready, and has an account ID.

The Ceph-side reconcile gets the live user by ID. A missing user is created. Existing users are modified only for supported scalar fields: display name, max buckets, and op-mask. Capabilities are diffed using a generated `type=perm;` string. Quotas are always set with defaults of disabled, `-1` max size, and `-1` max objects unless specified. Key reconciliation then makes the RGW key set match the target set exactly by deleting extra keys, deleting keys whose secret values changed, and creating missing keys.

After the RGW user has reconciled, `.status.keys` is updated from the referenced Kubernetes Secret UIDs, names, namespaces, and resource versions. The generated credential Secret is then created or updated with `AccessKey`, `SecretKey`, `Endpoint`, and optionally `SSLCertSecretName`, and an owner reference to the user CR. Final status is set to Ready with the observed generation.

Deletion uses the admin ops `RemoveUser` call. `admin.ErrNoSuchUser` is treated as success. Finalizer removal follows successful Ceph deletion. The generated Secret is not explicitly deleted here; Kubernetes owner-reference garbage collection is expected to clean it up.

## State and Persistence Behavior

Persistent Kubernetes state includes the `CephObjectStoreUser` finalizer, `.status.phase`, `.status.observedGeneration`, `.status.info.secretName`, `.status.keys`, and the generated `rook-ceph-object-user-<store>-<user>` Secret. Ceph persistent state includes RGW users, user capabilities, quotas, account association, op-mask, and S3 keys. Explicit key sources are external Kubernetes Secrets referenced by `spec.keys`; their UID/resourceVersion is copied into status after successful Ceph key reconciliation.

Ceph state is reconciled with a combination of admin ops API operations: `GetUser`, `CreateUser`, `ModifyUser`, `RemoveUserCap`, `AddUserCap`, `SetUserQuota`, `GetUser` for keys, `RemoveKey`, `CreateKey`, and `RemoveUser`. The generated Secret depends on `userConfig.Keys[0]`, so the Ceph key path must always leave at least one key in `userConfig.Keys`.

## Dependencies and Integration Points

The controller integrates with controller-runtime, Rook's `opcontroller` helpers, `object.InitializeObjectStoreContext`, go-ceph RGW admin ops, Rook status reporting, Kubernetes Secrets, Rook `CephCluster`, `CephObjectStore`, and optional `CephObjectStoreAccount` CRs. It depends on `opmask.FromSlice` to normalize the CR's `spec.opMask`. It uses `k8sutil` status constants and Secret type conventions, plus `controllerutil.SetControllerReference` for generated Secret ownership.

## Risks and Edge Cases

- `generateUserKeySpec` allocates `keys := make([]admin.UserKeySpec, len(user.Spec.Keys))` and then appends entries, leaving zero-value key specs before real key specs. That can produce unintended blank keys or API errors when explicit keys are used. The tests in this file do not directly cover `generateUserKeySpec`.
- `reconcileUserKeys` allocates `syncdKeys := make([]admin.UserKeySpec, len(targetKeys))` and appends matching keys, causing initial zero-value entries to be deleted from `targetMap`; this is mostly harmless but indicates the same length-vs-capacity pattern.
- `getObjectStore` lists all object stores and matches by name only, not namespace. In multi-namespace contexts this can select the wrong store if names collide.
- `generateCephUserSecret` always indexes `userConfig.Keys[0]`; a path that yields no keys will panic. The code defends against no live keys only when target keys are empty, but malformed explicit key paths remain risky.
- Capability comparison depends on stable caps ordering from the admin API. If Ceph returns caps in a different order than the desired string, unnecessary remove/add operations may occur.
- Account reference lookup is same namespace as the user even when `spec.clusterNamespace` points elsewhere; that appears intentional but is a contract to preserve.

## Test Signals

`controller_test.go` covers missing/unready cluster behavior, missing object store, missing RGW pods, successful user reconcile through a mocked admin ops client, cross-namespace user creation with `allowUsersInNamespaces`, status secret name generation, quota and capability updates, validation of IAM-compatible display names for account-linked users, account reference error/requeue/success cases, and scalar sync comparisons. The tests provide strong signals for readiness, account validation, quotas, caps, and basic Secret generation, but they do not directly verify explicit key-pair reconciliation, generated Secret owner reference behavior, Secret watch mapping, or deletion cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/user/controller_test.go

## Purpose

This file tests the `CephObjectStoreUser` controller and its helper functions. It uses fake Kubernetes clients, a fake Rook clientset, mock executors, and mocked RGW admin ops HTTP responses to verify readiness gating, successful RGW user creation/update, status info generation, validation, account reference resolution, and scalar user synchronization.

## Important Test Cases and Helpers

- `TestCephObjectStoreUserController` drives the controller's reconcile path through failure and success states.
- `TestBuildUpdateStatusInfo` verifies generated status info includes the expected credential Secret name.
- `TestCreateOrUpdateCephUser` exercises `createOrUpdateCephUser` and `generateUserConfig` for default users, max buckets, capabilities, user quotas, and combined quota/capability settings.
- `TestValidateUser` verifies standalone display names can contain spaces, while account-linked display names must match IAM-compatible characters.
- `TestResolveAccountRef` covers missing account, store mismatch, not-ready account, ready account, and ready account missing an account ID.
- `TestIsUserSync` verifies display name, max bucket, and op-mask comparisons.

## Control Flow and Test Setup

The main controller test starts with a `CephObjectStoreUser`, fake scheme registration, fake controller-runtime client, fake Rook clientset, and mock executor. It first verifies reconcile requeues without a cluster and with an unready cluster. It then provisions a monitor Secret and marks the cluster ready to test the missing object-store path. After adding a `CephObjectStore`, it tests the path where the RGW object exists but no RGW pod is running. The successful case creates an RGW pod and overrides `newMultisiteAdminOpsCtxFunc` to return a mocked admin ops client that accepts the expected user, quota, and caps HTTP calls.

The cross-namespace subtest sets `spec.clusterNamespace`, changes the user namespace, and toggles `allowUsersInNamespaces` to verify the controller allows or rejects users outside the object-store namespace. It also checks the behavior when no cluster exists in the user's own namespace.

`TestCreateOrUpdateCephUser` constructs a real go-ceph admin client backed by a mock HTTP transport and asserts the exact query strings produced for create/modify/quota/caps flows. The account and validation tests use fake CR clients and small in-memory CR instances rather than full reconcile.

## State and Persistence Signals

The tests observe `.status.phase`, generated `.status.info.secretName`, and account reference return values. They also verify generated bootstrap input data to the admin ops path indirectly through HTTP request query strings. The successful reconcile checks that the user CR reaches `Ready`. The cross-namespace case verifies the API-server state and the object-store allow-list are enough to accept users in another namespace.

## Dependencies and Integration Points

The tests rely on `github.com/ceph/go-ceph/rgw/admin`, fake controller-runtime clients, fake Rook/client-go clientsets, `exectest.MockExecutor`, `cephobject.MockClient`, Rook operator test helpers, Kubernetes `scheme.Scheme`, and fake event recorders. They also depend on HTTP query encoding produced by go-ceph, which makes the mocked admin ops cases sensitive to admin client behavior.

## Risks and Gaps

- `newMultisiteAdminOpsCtxFunc` is overridden globally and restored only implicitly by process lifetime, so additional tests in the same package could be order-sensitive if they rely on the default.
- Explicit `spec.keys` reconciliation is not covered, including Secret watch mapping, Secret deletion, `.status.keys`, and RGW key exact-match behavior.
- Deletion behavior is not tested in this file.
- Generated Secret contents and owner references are not asserted in the successful reconcile.
- The tests assert exact admin ops query strings, which catches regressions in desired parameters but can be brittle if go-ceph changes parameter ordering.

## Test Signals

The file gives strong confidence that common user reconcile paths reach the expected requeue or Ready results, that quota/capability admin ops calls are formed as expected, and that account-linked display-name constraints are enforced. It leaves key-management and deletion paths as notable untested surfaces.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask.go

## Purpose

This small helper package converts a `CephObjectStoreUser` operation-mask slice into the exact RGW admin API string format used for object-user op masks. It normalizes operation order to match radosgw-admin/admin API output.

## Important APIs, Types, and Functions

- `type OpMask struct` stores private booleans for `read`, `write`, and `delete`.
- `FromSlice(ops []cephv1.ObjectUserOpMask) (*OpMask, error)` parses a CRD enum slice into an `OpMask`.
- `(*OpMask).String() string` formats the mask as `"read, write, delete"`, any subset in read/write/delete order, or `"<none>"` when no operations are enabled.

## Control Flow

`FromSlice` rejects a nil slice, returns an empty mask for a zero-length slice, and sets booleans based on `slices.Contains` checks for `"read"`, `"write"`, and `"delete"`. It does not reject unknown entries; unknown values are ignored. `String` checks the empty mask first because RGW represents no permissions as `"<none>"`, then builds a string in fixed RGW order.

## State and Persistence Behavior

The package has no external state. Its output feeds `admin.User.OpMask` in the object user controller, which becomes persistent RGW user configuration through admin ops create/modify calls.

## Dependencies and Integration Points

It depends on the Ceph API type `cephv1.ObjectUserOpMask`, Go's `slices` and `strings` packages, and `pkg/errors`. The object user controller calls it when `spec.opMask` is explicitly set.

## Risks and Edge Cases

- Nil slices are treated as an error, but empty non-nil slices intentionally map to `"<none>"`. The controller distinguishes nil/unset from explicit empty, so this contract matters.
- Unknown operation values are ignored rather than rejected. This is probably acceptable because CRD enum validation should block invalid values, but direct Go callers would not get an error for unknown non-nil values.
- The private fields make construction outside the package impossible, which keeps callers on `FromSlice` but requires tests in-package for exact struct equality.

## Test Signals

`opmask_test.go` verifies all valid subsets, arbitrary input order, empty list behavior, and normalized string output. It does not test nil slices or unknown values.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask_test.go

## Purpose

This file tests the `opmask` helper's conversion and formatting behavior for RGW object-user operation masks.

## Important Test Cases

- `TestFromSlice` checks all read/write/delete subsets, confirms input order does not matter, and confirms an empty slice returns an empty mask.
- `TestString` checks all matching string outputs and the `"<none>"` representation for an empty mask.

## Control Flow and Test Setup

Both tests use table-driven subtests with `fmt.Sprintf` names and `testify/assert`. The tests are in the `opmask` package, so they can compare private `OpMask` fields directly.

## State and Persistence Signals

No external state is created. The tests validate the exact strings that will later be persisted into RGW user op-mask settings by the object user controller.

## Dependencies and Integration Points

The tests depend on `cephv1.ObjectUserOpMask`, `testify/assert`, and the local `FromSlice`/`String` APIs.

## Risks and Gaps

Nil input behavior is not tested even though `FromSlice` returns an error for nil. Unknown values are also untested. Those gaps are acceptable if CRD validation guarantees only valid enum values and the controller never passes nil when an explicit op-mask is set.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zone/controller.go

## Purpose

This file implements the `CephObjectZone` controller for RGW multisite zones. It waits for a ready `CephCluster` and a referenced `CephObjectZoneGroup`, validates pool specs, creates RGW zone pools and zone configuration, commits multisite config changes, updates status, and handles zone deletion including dependent object-store checks and optional pool preservation.

## Important APIs, Types, and Functions

- `ReconcileObjectZone` holds the controller-runtime client, scheme, clusterd context, cluster info/spec, operator manager context, and event recorder.
- `Add`, `newReconciler`, and `add` register a controller and watch `CephObjectZone` CRs.
- `Reconcile` wraps `reconcile` with panic recovery and result reporting.
- `reconcile` is the main state machine for finalizer setup, cluster readiness, cluster-info loading, validation, zonegroup lookup, deletion, creation/update, and status updates.
- `createorUpdateCephZone`, `createPoolsAndZone`, and `createZoneIfNotExists` create pools, create the RGW zone if missing, update endpoints when needed, configure shared pools/RADOS namespaces, and commit config.
- `getCephObjectZoneGroup` loads the referenced `CephObjectZoneGroup` CR and returns its realm.
- `reconcileCephZoneGroup` verifies the zonegroup exists in Ceph via `radosgw-admin zonegroup get`.
- `validateZoneCR` checks name, namespace, zonegroup, metadata pool spec, and data pool spec.
- `deleteCephObjectZone`, `deleteZone`, `removeZoneFromZonegroup`, `deleteZonePools`, and `decodePoolPrefixfromZone` implement deletion cleanup.

## Control Flow

Controller setup only watches `CephObjectZone` resources. During reconcile, a missing CR is ignored. Existing CRs receive a finalizer. Newly created resources get empty status. Cluster readiness is required before any Ceph operations. If a deleting zone's cluster is gone, the finalizer is removed without trying Ceph cleanup.

After cluster info loads, pool validation happens before zonegroup lookup. If the zonegroup CR is missing during deletion, the finalizer is removed to avoid blocking simultaneous multisite CR deletion. Otherwise the referenced zonegroup must exist and provides the realm name. Deleting zones call `deleteCephObjectZone`.

For normal reconcile, status is set to Reconciling. The controller verifies the zonegroup exists in Ceph, then builds an object context with realm, zonegroup, and zone. Pool config is validated and, unless shared-pool settings say no pool creation is needed, `object.CreateObjectStorePools` creates the metadata/data pools. The zonegroup config is fetched to determine whether a master zone exists. If the zone already exists, endpoint drift is checked and `object.JoinMultisite` updates custom endpoints when required. If the zone is missing, realm keys are loaded from Kubernetes Secrets and `radosgw-admin zone create` is run, adding `--master` if the zonegroup has no master zone and adding `--endpoints` for custom endpoints. Shared pool/RADOS namespace configuration then runs and RGW config changes are committed.

Deletion first checks whether the zone is present in the zonegroup and whether it is master. If present, `CephObjectZoneDependentStores` lists object stores that reference the zone and blocks deletion if any exist. Non-master zones are removed from their zonegroup and period updates are committed. Pool deletion is skipped when `spec.preservePoolsOnDelete` is true or both pool specs are empty. Otherwise the zone is fetched, its `domain_root` is parsed for the pool prefix, and `object.DeletePools` removes RGW pools. The zone is then deleted and the finalizer removed.

## State and Persistence Behavior

Kubernetes state includes the zone CR finalizer, `.status.phase`, `.status.observedGeneration`, and deletion-blocked conditions indirectly reported through the reporting package. Ceph state includes RGW pools, zone membership in a zonegroup, zone endpoints, shared-pool/RADOS namespace settings, and period commits. Pool deletion derives the RGW pool prefix from the live zone JSON rather than assuming the CR name.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `CephObjectZoneGroup`, pool validation, Rook object helpers, `radosgw-admin` through `object.RunAdminCommandNoMultisite`, cluster monitor Secrets for realm keys, status reporting, and dependent object-store discovery. Test override variables `createObjectStorePoolsFunc` and `commitConfigChangesFunc` allow unit tests to avoid real Ceph pool creation and commits.

## Risks and Edge Cases

- `decodePoolPrefixfromZone` splits `domain_root` on `.rgw.` and returns `s[0]` without checking the split length. Malformed JSON values could produce misleading prefixes.
- Master zone deletion cannot remove the zone from the zonegroup; the code still proceeds to pool and zone deletion. Master-zone semantics are sensitive and rely on underlying RGW behavior.
- Missing zonegroup during deletion removes the finalizer, which prevents stuck CRs but may leave Ceph-side zone state if the zonegroup CR was deleted before the zone.
- Endpoint updates only happen when the zone already exists and `ShouldUpdateZoneEndpointList` detects changes; other zone fields are not updated.
- Pool deletion is broad by prefix and must be correct to avoid deleting unrelated pools.

## Test Signals

`controller_test.go` covers requeue without a cluster, requeue with an unready cluster, requeue when the zonegroup CR is absent, and successful reconcile with mocked zonegroup/zone `radosgw-admin` outputs. `dependents_test.go` separately covers object-store dependent discovery. Deletion, endpoint update, shared-pool configuration, malformed zone JSON, and dependent-blocked deletion paths are not exercised in the main controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zone/controller_test.go

## Purpose

This file tests the `CephObjectZone` controller's readiness gating and successful zone creation path using fake Kubernetes clients and mocked Ceph command execution.

## Important Test Cases and Fixtures

- `zoneGroupGetJSON`, `zoneGetOutput`, and `zoneCreateJSON` model key `radosgw-admin` outputs for zonegroup and zone operations.
- `TestCephObjectZoneController` covers the full sequence of no cluster, unready cluster, missing `CephObjectZoneGroup`, and successful reconcile.
- Test overrides for `createObjectStorePoolsFunc` and `commitConfigChangesFunc` capture whether pool creation and config commit paths are reached.

## Control Flow and Test Setup

The test builds a `CephObjectZone` with metadata/data pools and a zonegroup reference, then wires a fake controller-runtime client, fake Rook clientset, mock executor, and event recorder. It first verifies reconcile requeues when no cluster exists, then with an unready cluster. After creating a monitor Secret and marking the cluster Ready, it verifies the missing zonegroup CR path requeues. The success path creates a `CephObjectZoneGroup` CR, provides mocked `zonegroup get` and `zone get` command outputs, runs reconcile, and asserts no requeue, Ready update through client state, and that pool creation and commit hooks were called.

## State and Persistence Signals

The test observes reconcile results and the fact that mocked pool creation/commit functions are invoked. It fetches the zone CR after success but primarily verifies successful completion rather than detailed `.status.phase` fields. Ceph persistence is represented only by expected command outputs from the mock executor.

## Dependencies and Integration Points

The test uses fake clients from controller-runtime and Rook, `exectest.MockExecutor`, Rook test clientsets, Kubernetes scheme registration, and a fake event recorder. It depends on global function variables in `controller.go` for test injection and restores them with deferred functions.

## Risks and Gaps

The test does not cover deletion, dependent blocking, pool-prefix decoding, custom endpoint update, shared-pool/no-pool paths, invalid pool specs, finalizer-only reconciliation, or the branch where a missing zone must be created. In the success case, mocked `zone get` returns success, so the create branch is effectively skipped even though `zoneCreateJSON` exists as a fixture.

## Test Signals

The file confirms the controller waits for cluster and zonegroup prerequisites and enters the pool/config commit path once prerequisites are available. It is a useful smoke test but not comprehensive for zone lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents.go

## Purpose

This helper finds Kubernetes resources that depend on a `CephObjectZone`, currently `CephObjectStore` CRs in the same namespace whose `spec.zone.name` matches the zone. It is used to block zone deletion while object stores still reference the zone.

## Important APIs and Functions

- `CephObjectZoneDependentStores(clusterdCtx, clusterInfo, zone, objContext) (*dependents.DependentList, error)` lists object stores and returns a `DependentList` of matching store names under kind `CephObjectStore`.

## Control Flow

The function builds a namespace/name for logging and error wrapping, initializes an empty dependent list, lists `CephObjectStores` in `zone.Namespace` using the Rook clientset and `clusterInfo.Context`, and iterates through the list. Stores with `store.Spec.Zone.Name == zone.Name` are added as dependents. Non-matching stores are logged as non-dependent. Any list error is wrapped with context and returned with the possibly empty list.

## State and Persistence Behavior

The function is read-only. It does not mutate Kubernetes or Ceph state. Its result affects deletion state through callers such as `deleteCephObjectZone`, which reports deletion-blocked conditions when dependents are present.

## Dependencies and Integration Points

It depends on the Rook typed clientset, `client.ClusterInfo.Context`, `object.Context` for the signature, `dependents.DependentList`, Rook controller namespace/name formatting, and logging. The `objContext` argument is not used by the function body, but callers already have it in deletion flows.

## Risks and Edge Cases

- Only same-namespace object stores are considered.
- Only `spec.zone.name` is checked; other possible implicit dependencies are not considered.
- The unused `objContext` parameter may indicate legacy API shape or future intended checks.
- The non-dependent debug log is executed for all stores, but the current code logs the non-dependent message even after dependent checks only in the `else` branch, so functional behavior is correct.

## Test Signals

`dependents_test.go` covers no stores, one matching store, one different-zone store, and multiple matching stores. It provides good confidence for the current dependency filter.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents_test.go

## Purpose

This file tests `CephObjectZoneDependentStores`, the helper that detects object stores blocking zone deletion.

## Important Test Cases

- No object stores exist, so the dependent list is empty.
- One object store references the zone, so that store appears under `CephObjectStore`.
- One object store references a different zone, so the dependent list remains empty.
- Multiple object stores reference the zone, so all matching names are returned.

## Control Flow and Test Setup

The test constructs a `CephObjectZone`, two `CephObjectStore` objects, a fake Rook clientset, a mock executor-backed clusterd context, and `client.AdminTestClusterInfo`. Each subtest creates a fresh context and populates the fake clientset as needed before calling `CephObjectZoneDependentStores`.

## State and Persistence Signals

All state is fake Kubernetes API state in the Rook clientset. Assertions inspect `deps.Empty()` and `deps.OfKind("CephObjectStore")`, which is the data the zone deletion path uses to decide whether finalizer removal is blocked.

## Dependencies and Integration Points

The test uses fake Rook clientsets, `object.NewContext`, `exectest.MockExecutor`, `testify/assert`, and Ceph API scheme registration. No real Ceph commands are executed.

## Risks and Gaps

The test does not cover list errors from the Rook clientset or cross-namespace stores. It mutates `objectStoreB.Spec.Zone.Name` in one subtest, so future test changes should avoid accidental state leakage by copying objects per subtest.

## Test Signals

The file gives direct confidence that the current deletion-blocking dependency lookup includes exactly same-namespace stores with matching `spec.zone.name`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zone/dependents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller.go

## Purpose

This file implements the `CephObjectZoneGroup` controller for RGW multisite zonegroups. It reconciles a zonegroup CR by waiting for a ready Ceph cluster, requiring a referenced `CephObjectRealm` CR and Ceph realm, creating the RGW zonegroup if missing, marking the first zonegroup as master when needed, and updating status.

## Important APIs, Types, and Functions

- `ReconcileObjectZoneGroup` holds the controller-runtime client, scheme, clusterd context, cluster info, and operator manager context.
- `Add`, `newReconciler`, and `add` register a controller and watch `CephObjectZoneGroup` CRs.
- `Reconcile` wraps `reconcile` with panic recovery and logging.
- `reconcile` fetches the CR, initializes status, waits for cluster readiness, ignores deletion, loads cluster info, validates the CR, reconciles realm prerequisites, creates the Ceph zonegroup, and marks Ready.
- `createCephZoneGroup` checks the current realm period, determines whether this should be the master zonegroup, checks for an existing zonegroup, and runs `radosgw-admin zonegroup create` if needed.
- `reconcileObjectRealm` verifies the Kubernetes `CephObjectRealm` exists.
- `reconcileCephRealm` verifies the Ceph realm exists via `radosgw-admin realm get`.
- `setFailedStatus` and `updateStatus` maintain status phase and observed generation.

## Control Flow

Controller setup watches only zonegroup CRs. Reconcile ignores not-found resources. Unlike zone and pool controllers, this file does not add a finalizer, and deletion simply returns success once cluster readiness allows the code to see the deleted object. If the cluster is absent and the zonegroup is deleting, the function also returns success.

For active resources, the controller loads cluster info, validates name/namespace/realm, sets Reconciling status, and requires both the Kubernetes realm CR and the live Ceph realm. Missing realm CR or live realm produces a 10-second requeue. `createCephZoneGroup` then reads the realm period with `period get`. If `master_zonegroup` is empty, the new zonegroup is created with `--master`. If `zonegroup get` succeeds, no update is performed. If it returns ENOENT, `zonegroup create` runs. Any other command failure is returned.

## State and Persistence Behavior

Kubernetes state is `.status.phase` and `.status.observedGeneration` on the zonegroup CR. No finalizer means the controller does not block deletion or perform Ceph-side deletion. Ceph state includes the RGW zonegroup resource under a realm and possibly the realm's master zonegroup designation.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `CephObjectRealm`, `object.NewContext`, `object.RunAdminCommandNoMultisite`, `decodeMasterZoneGroup`, `validateZoneGroup`, Rook status reporting, and `k8sutil` status constants. It is a prerequisite for `CephObjectZone`, which reads the zonegroup CR's realm and verifies the live Ceph zonegroup before creating zones.

## Risks and Edge Cases

- No finalizer or deletion cleanup exists for Ceph zonegroups, so deleting the CR does not delete live RGW zonegroup state.
- Existing zonegroups are not updated; reconciliation only creates missing zonegroups.
- If period JSON is malformed or missing `master_zonegroup`, the controller either errors or treats the zonegroup as master.
- Errors wrap `code` even in some branches where `exec.ExitStatus` may not have set a meaningful value.
- Status failures are reported for create errors, but missing realm prerequisites return errors/requeue without a failed status.

## Test Signals

`controller_test.go` covers missing cluster, unready cluster, missing `CephObjectRealm`, and success when Kubernetes and Ceph realm prerequisites exist. `zonegroup.go` helper behavior is not directly tested except through controller success. Deletion and create-on-missing-zonegroup branches are not deeply exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller_test.go

## Purpose

This file tests the `CephObjectZoneGroup` controller's prerequisite checks and successful reconcile path using fake clients and mocked `radosgw-admin` command outputs.

## Important Test Cases and Fixtures

- `realmGetJSON`, `periodGetJSON`, and `zoneGroupGetJSON` simulate Ceph realm, period, and zonegroup outputs.
- `TestCephObjectZoneGroupController` covers no cluster, unready cluster, ready cluster without `CephObjectRealm`, and successful reconcile when the realm CR and Ceph realm/period/zonegroup exist.

## Control Flow and Test Setup

The test creates a `CephObjectZoneGroup` referencing `realm-a`, fake controller-runtime and Rook clients, and a mock executor. It first verifies requeue without a cluster and with an unready cluster. It then creates monitor Secret data and marks the cluster Ready; with no `CephObjectRealm` CR, reconcile returns an error and requeue. The success case adds a `CephObjectRealm`, configures mocked command outputs for `zonegroup get`, `period get`, and `realm get`, and verifies reconcile completes without requeue.

## State and Persistence Signals

The test fetches the zonegroup CR after success but does not explicitly assert `.status.phase` or observed generation. Ceph state is represented by mock command output and does not verify the create branch because `zonegroup get` succeeds.

## Dependencies and Integration Points

The test uses fake controller-runtime clients, fake Rook clientsets, `exectest.MockExecutor`, Kubernetes scheme registration, and `cephclient.AdminTestClusterInfo`. It depends on command-argument inspection inside the mock executor to simulate Ceph state.

## Risks and Gaps

Deletion behavior, invalid CR validation, malformed period JSON, missing live Ceph realm with an existing realm CR, and zonegroup creation when `zonegroup get` returns ENOENT are not covered. Status assertions are light, so regressions in phase/observed-generation updates may not be caught here.

## Test Signals

The file confirms that the controller gates work on cluster readiness, Kubernetes realm presence, live Ceph realm presence, and existing zonegroup state. It is a good readiness smoke test but not a full lifecycle test.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/zonegroup.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/zonegroup.go

## Purpose

This helper file provides zonegroup-specific parsing and validation used by the `CephObjectZoneGroup` controller.

## Important APIs, Types, and Functions

- `masterZoneGroupType` models the `master_zonegroup` field from `radosgw-admin period get` JSON.
- `decodeMasterZoneGroup(data string) (string, error)` unmarshals period JSON and returns the master zonegroup ID/name field.
- `validateZoneGroup(u *cephv1.CephObjectZoneGroup) error` validates required CR fields: name, namespace, and `spec.realm`.

## Control Flow

`decodeMasterZoneGroup` unmarshals into a minimal struct and wraps JSON errors. Missing `master_zonegroup` naturally returns an empty string. `validateZoneGroup` performs sequential required-field checks and returns the first missing-field error.

## State and Persistence Behavior

The file has no state. `decodeMasterZoneGroup` influences whether a newly created Ceph zonegroup receives `--master`, which persists in Ceph multisite period/zonegroup configuration.

## Dependencies and Integration Points

It depends on Go `encoding/json`, `pkg/errors`, and `cephv1.CephObjectZoneGroup`. The controller calls both functions during active reconciliation.

## Risks and Edge Cases

- `decodeMasterZoneGroup` only extracts one field and cannot validate overall period structure.
- A period JSON with no `master_zonegroup` is indistinguishable from a valid period with an intentionally empty master; this is used by the controller to mark the first zonegroup master.
- `validateZoneGroup` does not validate that the referenced realm exists; that is handled by controller logic.

## Test Signals

There is no direct unit test for this helper file. `controller_test.go` indirectly exercises successful period decoding and validation in the happy path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/zonegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/operator.go -->
# sources/control-plane/rook/pkg/operator/ceph/operator.go

## Purpose

This file defines the top-level Ceph operator process lifecycle. It creates operator configuration, initializes the cluster controller, starts and restarts the CRD manager, responds to process signals, reloads configuration on SIGHUP, and decides whether the operator watches only its namespace or all namespaces.

## Important APIs, Types, and Functions

- Package globals include `ImmediateRetryResult`, `ShutdownSignals`, `opManagerContext`, `opManagerStop`, and `mgrCRDErrorChan`.
- `Operator` stores the shared clusterd context, registered custom resources, operator config, and cluster controller.
- `New(context, rookImage, serviceAccount)` constructs an operator with cluster CR resource registration and a `cluster.ClusterController`.
- `Run()` installs signal handling, starts the CRD manager, watches SIGHUP for config reload, watches manager errors, and exits on shutdown signals.
- `runCRDManager()` creates a new cancellable manager context, applies operator settings from ConfigMap, updates namespace watch scope, assigns the context to the cluster controller, starts the CRD manager goroutine, and logs goroutine count after one minute.
- `namespaceToWatch()` reads `ROOK_CURRENT_NAMESPACE_ONLY` from operator settings and sets `config.NamespaceToWatch` to the operator namespace or `corev1.NamespaceAll`.

## Control Flow

`New` sets `OperatorNamespace` from the pod namespace environment variable, stores the image/service account, and creates the cluster controller. `Run` creates a root process context bound to interrupt and SIGTERM. It starts the CRD manager once, then loops over three event sources: shutdown, SIGHUP reload, and CRD manager error. Shutdown cancels the manager and exits cleanly. SIGHUP cancels the current manager and starts a fresh one, which also cancels active orchestration through the shared `opManagerContext`. A manager error is wrapped and returned.

`runCRDManager` recreates the manager error channel and operator manager context every time it is called. It panics if operator settings cannot be loaded. It updates namespace scope before starting the manager, and sets `clusterController.OpManagerCtx` so background monitoring goroutines can stop with manager reload/shutdown.

## State and Persistence Behavior

The file manages in-memory process state only: contexts, cancel functions, error channels, namespace watch config, and cluster-controller context. It reads Kubernetes ConfigMap-backed operator settings through `k8sutil.ApplyOperatorSettingsConfigmap`, but does not persist Kubernetes objects itself.

## Dependencies and Integration Points

It integrates with `clusterd.Context`, the Ceph cluster controller, Rook controller config, `k8sutil` operator settings, process signals, controller-runtime reconcile result conventions, and Kubernetes namespace constants. The missing `startCRDManager` implementation is in another file and is the actual controller registration path.

## Risks and Edge Cases

- Package-level manager context globals make lifecycle state process-wide and require careful ordering; `Run` assumes `runCRDManager` has initialized `opManagerStop` before shutdown.
- `runCRDManager` panics on settings ConfigMap load failure instead of returning an error.
- SIGHUP reload cancels all orchestrations, which is intentional but disruptive.
- There is no explicit signal stop for the SIGHUP channel in this file.

## Test Signals

`operator_test.go` only tests `New`: non-nil operator, cluster controller, resources, context identity, and registration of the cluster resource. `Run`, signal handling, manager reload, and namespace watch selection are not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/operator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/operator_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/operator_test.go

## Purpose

This file smoke-tests construction of the top-level Ceph `Operator`.

## Important Test Cases

- `TestOperator` creates a fake Kubernetes clientset, wraps it in a `clusterd.Context`, calls `New`, and asserts the operator, cluster controller, resource list, and stored context are initialized correctly.
- It verifies the only registered resource is `opcontroller.ClusterResource`.

## Control Flow and Test Setup

The test uses `operator/test.New(t, 3)` to create a fake clientset and passes empty image/service-account values to `New`. It iterates over `o.resources` and fails if any resource name differs from the cluster resource name.

## State and Persistence Signals

No Kubernetes objects are created by the operator in this test. It validates in-memory constructor state only.

## Dependencies and Integration Points

The test depends on `clusterd.Context`, `opcontroller.ClusterResource`, Rook operator test helpers, and `testify/assert`.

## Risks and Gaps

The test does not cover `Run`, `runCRDManager`, SIGHUP reload, shutdown signals, settings ConfigMap loading, namespace watch selection, or controller manager startup. It is useful as a constructor regression test but does not validate operator runtime behavior.

## Test Signals

The file confirms that `New` wires the basic operator structure and resource list. Runtime lifecycle correctness must be inferred from other tests or integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/operator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/controller.go

## Purpose

This file implements the `CephBlockPool` controller. It reconciles block pool CRs into Ceph pools, initializes RBD pools, configures RBD per-image stats, manages RBD mirroring bootstrap and peer import, tracks mirroring health check goroutines, protects deletion when pools are non-empty or have RADOS namespace dependents, deletes pools and EC profiles, and maintains status.

## Important APIs, Types, and Functions

- `ReconcileCephBlockPool` stores the controller-runtime client/scheme, clusterd context, cluster info, mirror monitoring contexts, operator manager context, event recorder, and operator config.
- `blockPoolHealth` stores the internal monitoring context/cancel function and whether monitoring has started.
- `Add`, `newReconciler`, and `add` register the controller and watches for `CephBlockPool` CRs, monitor endpoint ConfigMap changes, and peer-token Secret changes.
- `Reconcile` wraps `reconcile` with panic recovery and result reporting.
- `reconcile` is the main state machine for finalizers, cluster readiness, deletion, validation, pool creation/update, stats config, mirroring, and status.
- `configurePoolMirroring` creates bootstrap peer Secrets, imports configured peer tokens, reconciles CSI pool ID maps, updates status, and starts/stops mirror monitoring.
- `handleDeletionBlocked` computes deletion-blocked conditions from RADOS namespace dependents and pool emptiness, optionally starts cleanup jobs for force-delete, and returns an error when deletion must remain blocked.
- `createPool` and `deletePool` wrap Ceph pool create/delete operations and RBD pool initialization / EC profile cleanup.
- `generateStatsPoolList` and `configureRBDStats` maintain the mgr/prometheus `rbd_stats_pools` mon config key.
- `cancelMirrorMonitoring`, `disableMirroring`, `isAnyRadosNamespaceMirrored`, and `canConfigurePoolMirroring` manage mirroring shutdown and constraints.

## Control Flow

Controller setup watches pool CRs directly. It also maps monitor endpoint ConfigMap changes to all pool CRs so bootstrap peer tokens can refresh when mon endpoints change, and maps peer-token Secret changes to all pool CRs using `WatchPeerTokenSecretPredicate`.

Reconcile ignores missing CRs but cancels mirror monitoring for the vanished pool to avoid leaked goroutines. Existing CRs get finalizers. New CRs with nil status are marked Progressing. Cluster readiness is required; if a deleting pool's cluster is gone, mirror monitoring is cancelled and the finalizer is removed without Ceph cleanup.

Once cluster info is loaded, deletion runs first. `handleDeletionBlocked` checks RADOS namespace dependents, pool presence, pool emptiness including namespace contents, and force-delete cleanup. If deletion is not blocked, mirror monitoring is cancelled, the Ceph pool is deleted, RBD stats config is updated to remove the pool, and the finalizer is removed.

For active pools, `validatePool` checks CR and pool-spec constraints. Uninitialized operator config errors produce a delayed requeue. The Ceph version is read from the cluster status into cluster info. `reconcileCreatePool` calls `createPool`, which defaults the application to `rbd`, calls `cephclient.CreatePool`, and runs `rbd pool init` for RBD pools. RBD stats config is then synchronized from all non-deleting pool CRs with `enableRBDStats`.

Mirroring is configured only for non-EC pools. When enabled, the controller creates a bootstrap peer Secret, sets Progressing status with the cluster's RBD mirror peer cephx status, imports any configured peer Secrets, updates the CSI peermap ConfigMap, marks Ready, and manages a mirror health checker goroutine unless mirror status checks are disabled or mirroring mode is `init-only`. When mirroring is disabled, it attempts to disable Ceph-side mirroring, marks Ready with an empty cephx peer token, cancels monitoring, and clears mirroring status.

`disableMirroring` refuses to disable if any RADOS namespace in the pool still has mirroring enabled. For image-mode mirroring it also refuses when mirrored images remain. It removes storage cluster peers and then disables pool mirroring.

## State and Persistence Behavior

Kubernetes state includes the pool CR finalizer, `.status.phase`, `.status.info` fields such as pool type/failure domain and mirroring bootstrap Secret name, `.status.poolID`, `.status.cephx.peerToken`, deletion-blocked conditions, generated bootstrap peer Secrets, cleanup Jobs, and CSI pool ID map ConfigMaps. In-memory state includes `blockPoolMirrorContexts`, keyed by namespace/name, to cancel or avoid duplicate health-check goroutines.

Ceph state includes pools, pool application metadata, RBD initialization state, EC profiles, mirroring mode/peers, mirrored image state, RADOS namespace mirroring, and mgr/prometheus `rbd_stats_pools` config. Deletion removes the pool if present and deletes EC profiles for EC pools.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `cephclient` pool/RBD/mirroring APIs, mon endpoint predicates, config mon store, cleanup-job creation, Rook status reporting, dependent detection in `dependents.go`, peer token import in `peers.go`, CSI peermap reconciliation, Kubernetes ConfigMaps/Secrets, and status helpers in `status.go`. It depends on `validate.go` for pool-spec validation.

## Risks and Edge Cases

- Watch handlers for ConfigMaps and Secrets map changes to all pools, which is simple but can cause broad reconcile storms in large namespaces.
- `handleDeletionBlocked` can start cleanup jobs on force-delete while still returning blocked if dependents or non-empty state remain; cleanup job idempotency is important.
- Mirroring disable is intentionally conservative; leftover namespace mirroring or image mirroring keeps mirroring enabled and logs warnings while reconcile can still mark Ready in the disabled spec path after warning.
- In-memory mirror monitoring contexts are process-local; operator restart relies on future reconciles to recreate health checking.
- `configureRBDStats` merges existing external pool names with Rook-managed pools. Bad existing config with names that should be removed only disappears if they match current deleted/disabled pools.
- EC pools skip mirroring entirely, so mirroring fields on EC specs will not be reconciled.

## Test Signals

`controller_test.go` covers pool creation, name overrides, deletion including EC profile cleanup, readiness gating, successful reconcile to Ready, mirroring enabled/disabled, peer-token Secret import success/failure, deletion blocking for non-empty pools and RADOS namespace dependents, RBD stats config merge/removal/deduplication/errors, mirror peer key rotation status, Ready status for replicated and EC pools, and EC mirroring exclusion. `dependents_test.go` covers RADOS namespace dependent discovery. Coverage is broad, though some goroutine lifecycle, cleanup job details, and watch mapping behavior are not deeply tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/controller_test.go

## Purpose

This file provides broad unit coverage for the `CephBlockPool` controller, including pool creation/deletion helpers, reconcile readiness, mirroring, deletion blocking, RBD stats config, status fields, and EC mirroring exclusions.

## Important Test Cases

- `TestCreatePool` verifies replicated, `.mgr`, and EC pool creation behavior and confirms `rbd pool init` runs only for RBD application pools.
- `TestCephPoolName` verifies default pool names and allowed spec name overrides like `.mgr` and `.nfs`.
- `TestDeletePool` verifies pool deletion, no-op deletion for absent pools, failure for non-empty pools, CRUSH rule deletion, and EC profile cleanup.
- `TestCephBlockPoolController` drives reconcile through missing cluster, unready cluster, ready cluster success, invalid mirroring config, mirroring bootstrap Secret creation, peer-token import failure/success, and mirroring-disabled behavior.
- `TestDeletionBlocked` verifies deletion-blocked conditions for missing pools, empty pools, non-empty pools, and RADOS namespace dependents.
- `TestIsAnyRadosNamespaceMirrored` checks namespace mirroring detection.
- `TestConfigureRBDStats` and `TestGenerateStatsPoolList` cover mgr/prometheus RBD stats pool-list merging, removal, deduplication, empty handling, and error behavior.
- `TestMirrorPeerKeyRotationStatus` verifies pool `.status.cephx.peerToken` tracks the cluster's RBD mirror peer cephx status.
- `TestCephBlockPoolControllerPoolReachesReady` verifies both replicated and EC pools reach Ready and have expected type info.
- `TestCanConfigurePoolMirroring` verifies EC pools are excluded from mirroring.

## Control Flow and Test Setup

Tests use `exectest.MockExecutor` to inspect and return Ceph/RBD command results, fake controller-runtime clients for CR state, fake Rook/client-go clientsets for typed resources and Secrets, and fake event recorders. Several tests create monitor Secrets to allow `LoadClusterInfo`. Mirroring tests set `POD_NAME` and `POD_NAMESPACE` and create pod/replicaset objects so owner-aware bootstrap Secret logic can run.

The reconcile test mutates the same pool object through multiple subtests, progressively enabling mirroring and peer imports. RBD stats tests replace the executor mid-test to simulate mon store success and failure. Deletion-blocking tests vary command outputs and fake RADOS namespace CRs to check condition updates.

## State and Persistence Signals

The tests observe pool `.status.phase`, `.status.info`, `.status.cephx.peerToken`, `.status.conditions`, generated peer-token Secrets, deleted-pool maps, deleted EC profile flags, and mon-store config values. Ceph persistence is modeled through command mocks and side-effect variables.

## Dependencies and Integration Points

The tests integrate with fake Kubernetes API schemes, Rook fake clientsets, Ceph API types, `cephclient.AdminTestClusterInfo`, mon store helpers, controller cleanup/mirroring helpers, and command-output fixtures. They depend on exact command argument ordering in several mock executors.

## Risks and Gaps

- Some subtests share mutated pool, client, and executor state, so future changes must be careful about ordering and reset behavior.
- Watch setup for ConfigMap/Secret events is not exercised.
- Mirror health goroutine lifecycle is mostly inferred, not deeply synchronized or inspected.
- Cleanup job creation on force-delete is not covered.
- Some mocks return generic successful output for commands they do not fully model, so certain failure branches remain uncovered.

## Test Signals

This is a high-signal test file for block-pool behavior. It validates many important lifecycle and status paths, especially deletion safety, RBD stats, and mirroring bootstrap. Remaining risk is mainly around asynchronous monitoring, watch fan-out, and cleanup job details.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/dependents.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/dependents.go

## Purpose

This helper finds Kubernetes resources that depend on a `CephBlockPool`, currently `CephBlockPoolRadosNamespace` CRs that reference the pool. The block pool controller uses it to block pool deletion when namespaces still exist.

## Important APIs and Functions

- `const radosNamespacesKeyName = "CephBlockPoolRadosNamespaces"` is the dependent kind key used in status and deletion messages.
- `cephBlockPoolDependents(clusterdCtx, clusterInfo, blockpool) (*dependents.DependentList, error)` lists RADOS namespace CRs and returns those whose `spec.blockPoolName` matches the pool name.

## Control Flow

The function creates an empty dependent list, lists `CephBlockPoolRadosNamespaces` in the pool namespace through the Rook clientset, and iterates through results. Matching namespaces are added using `cephv1.GetRadosNamespaceName`, which captures the user-visible namespace name. List failures are wrapped with context.

## State and Persistence Behavior

The function is read-only. Its returned `DependentList` is used by `handleDeletionBlocked` to create status conditions and prevent finalizer removal when namespace dependents exist.

## Dependencies and Integration Points

It depends on Rook typed clientsets, `client.ClusterInfo.Context`, `dependents.DependentList`, Rook controller namespace/name formatting, and logging. It is private to the pool package and called by `controller.go`.

## Risks and Edge Cases

- Only same-namespace `CephBlockPoolRadosNamespace` CRs are considered.
- The debug log currently says a namespace does not depend on the pool even after a matching namespace is added, because the log statement is outside the `if` block. This is a logging bug, not a functional dependency bug.
- If `GetRadosNamespaceName` behavior changes, deletion-blocked messages and emptiness checks may change.

## Test Signals

`dependents_test.go` covers no namespaces, a namespace for a different pool, and one matching namespace. It does not cover list errors or multiple matching namespaces.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/dependents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/dependents_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/dependents_test.go

## Purpose

This file tests `cephBlockPoolDependents`, the helper that detects RADOS namespace CRs blocking `CephBlockPool` deletion.

## Important Test Cases

- No namespaces returns an empty dependent list.
- A namespace whose `spec.blockPoolName` does not match the target pool returns an empty dependent list.
- A namespace whose `spec.blockPoolName` matches returns a non-empty dependent list.

## Control Flow and Test Setup

The test creates a fake Rook clientset-backed `clusterd.Context`, `client.AdminTestClusterInfo`, and `CephBlockPool` target. Each subtest creates RADOS namespace CRs in the fake typed clientset as needed and calls `cephBlockPoolDependents`.

## State and Persistence Signals

All state is fake Rook API state. Assertions use `deps.Empty()` to confirm what the deletion-blocking path would see.

## Dependencies and Integration Points

The test depends on the Ceph API scheme, fake Rook clientset, `client.AdminTestClusterInfo`, and `testify/assert`.

## Risks and Gaps

The helper-local `newClusterdCtx` ignores its variadic `objects` parameter, which is harmless because subtests explicitly create resources afterward. The test does not assert the exact dependent names, list error behavior, or multiple namespace handling.

## Test Signals

The file confirms the primary match/no-match behavior for pool RADOS namespace dependents, sufficient for basic deletion-blocking confidence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/dependents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/peers.go -->
# sources/control-plane/rook/pkg/operator/ceph/pool/peers.go

## Purpose

This file implements bootstrap peer import for RBD mirroring on `CephBlockPool`. It reads configured peer-token Secrets and imports each token into the Ceph pool's mirroring configuration.

## Important APIs and Functions

- `(*ReconcileCephBlockPool) reconcileAddBootstrapPeer(pool, namespacedName) (reconcile.Result, error)` is called from `configurePoolMirroring` when mirroring is enabled.

## Control Flow

If `pool.Spec.Mirroring.Peers` is nil, the function returns success without action. Otherwise it loops over `Peers.SecretNames`. For each Secret, it reads the Secret from `r.clusterInfo.Namespace` using the core clientset and the operator manager context. Missing or failed Secret reads return `opcontroller.ImmediateRetryResult`. Secret data is validated with `opcontroller.ValidatePeerToken`, and then imported with `client.ImportRBDMirrorBootstrapPeer`, passing pool name, direction, and token data.

## State and Persistence Behavior

Kubernetes Secret state is read-only. Ceph mirroring peer state is mutated by `ImportRBDMirrorBootstrapPeer`, which imports remote bootstrap tokens into the local pool's RBD mirroring config.

## Dependencies and Integration Points

The function depends on the pool controller's clusterd context and cluster info, Kubernetes Secrets, `opcontroller.ValidatePeerToken`, `client.ImportRBDMirrorBootstrapPeer`, Rook logging, and controller-runtime reconcile results. It is integrated into `controller.go` after the local bootstrap peer Secret is created.

## Risks and Edge Cases

- Secrets are always read from `r.clusterInfo.Namespace`, not necessarily `pool.Namespace`; for normal pool/cluster scope this should match, but it is an important namespace contract.
- All Secret read errors, including not-found, are treated as retryable failures.
- The function imports all listed Secrets on every reconcile; idempotency depends on Ceph import behavior.
- Direction is passed from `s.Data["direction"]`; validation must ensure it exists and is valid.

## Test Signals

`controller_test.go` indirectly covers missing peer Secret failure and existing peer Secret success through the full pool reconcile path. There is no direct unit test for this function with multiple peers, invalid token data, or import command failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/pool/peers.go -->
