# Research: subset-b-000458

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec_test.go

## Purpose
`spec_test.go` is the deployment and service specification regression suite for the Ceph NVMe-oF gateway controller. It validates the Kubernetes objects produced by `ReconcileCephNVMeOFGateway.makeDeployment()` and `generateCephNVMeOFService()` without needing a live cluster or Ceph daemon. The tests protect the operator contract for pod labels, resources, service account, liveness probes, placement, host networking, ConfigMap references, init container setup, daemon container setup, image fallback, hostnames, and gateway ports.

## Important APIs, Types, and Functions
`newDeploymentSpecTest()` builds a fake controller-runtime client seeded with a `CephNVMeOFGateway`, a fake Kubernetes clientset, a mock executor, `ClusterInfo`, and a minimal `ClusterSpec`. `TestDeploymentSpec()` contains subtests for each supported deployment variant. Local helpers `assertEnvVar`, `assertEnvVarPresent`, `assertServicePort`, and `assertContainerPort` make targeted assertions against Kubernetes `EnvVar`, `ServicePort`, and `ContainerPort` slices. The test code exercises constants and functions defined in the production package, including `AppName`, `serviceAccountName`, `connectionConfigScript`, `instanceName`, `nvmeofIOPort`, `nvmeofGatewayPort`, `nvmeofMonitorPort`, and `nvmeofDiscoveryPort`.

## Control Flow, State, and Persistence
The suite constructs CR instances, invokes spec-generation functions, and inspects returned Kubernetes API objects in memory. There is no persistent cluster state, but the test verifies fields that become persisted cluster state when the controller applies them: Deployment annotations include the config hash, pod templates carry resource requests/limits and placement constraints, volumes reference the selected ConfigMap, services expose gateway ports, and host-network deployments use `DNSClusterFirstWithHostNet`. The image fallback test injects a mock executor result so `makeDeployment()` can discover an image from Ceph config when the CR omits one.

## Dependencies and Integration Points
The file depends on Rook's Ceph API types, fake Rook/client-go clients, controller-runtime fake clients, operator test helpers, mock exec, Ceph version metadata, and Kubernetes core API types. It integrates with the NVMe-oF reconciler's deployment/service builders and with shared Ceph label validation through `cephTest.AssertLabelsContainCephRequirements()`. `optest.NewPodTemplateSpecTester()` validates common pod-template conventions shared across Rook daemons.

## Risks
The tests are strong for object shape but do not validate Kubernetes admission behavior or runtime gateway readiness. Assertions depend on exact container names, port names, and generated labels, so intentional production renames need coordinated test updates. The image fallback mock only returns a happy-path string or empty value; it does not cover command errors or malformed image data. The invalid-hostname case only checks an underscore-based name and may not cover all Kubernetes hostname edge cases.

## Test Signals
Positive signals include coverage for default and custom liveness probes, default topology spread constraints, user placement override, host network behavior, custom ConfigMap refs, init container env/volume wiring, privileged daemon container setup, image fallback and failure, valid/invalid hostnames, service labels, and custom ports. Useful follow-up signals would include tests for executor error propagation in image discovery and any future TLS or multi-instance service behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/account.go

## Purpose
`account.go` provides thin, validation-focused wrappers around the go-ceph RGW Admin Ops account and user APIs. It is the object package's backend layer for creating, reading, modifying, and deleting RGW accounts and their account-root users.

## Important APIs, Types, and Functions
The account functions all accept a `context.Context` and an `*AdminOpsContext` containing a configured `*admin.API`. `GetAccount`, `CreateAccount`, `ModifyAccount`, and `DeleteAccount` wrap `AdminOpsClient.GetAccount`, `CreateAccount`, `ModifyAccount`, and `DeleteAccount`. `CreateAccountRootUser`, `GetAccountRootUser`, `ModifyAccountRootUser`, and `DeleteAccountRootUser` wrap the corresponding `admin.User` APIs. Validation rejects empty account IDs, account names, user IDs, or user account IDs before contacting RGW.

## Control Flow, State, and Persistence
Each function performs local argument validation, delegates exactly one Admin Ops request, wraps any error with object identity context, and returns the RGW response. Persistent state is entirely in RGW: account records, account names, user records, generated credentials, and account-root flags. The wrappers do not write Kubernetes status or Secrets; the account controller uses them to do that.

## Dependencies and Integration Points
The file depends on `github.com/ceph/go-ceph/rgw/admin` and `github.com/pkg/errors`. Its primary consumers are the `object/account` controller methods `reconcileAccount`, `deleteAccount`, and `reconcileRootUser`. It also relies on error identity from go-ceph, such as `admin.ErrNoSuchKey`, `admin.ErrAccountAlreadyExists`, and `admin.ErrNoSuchUser`, being preserved through `errors.Wrapf()` for controller comparisons.

## Risks
The wrappers assume `adminOpsContext` and `AdminOpsClient` are non-nil; callers must initialize them before use. `CreateAccountRootUser` requires `user.AccountID`, but `ModifyAccountRootUser` only validates `user.ID`, so accidental account reassignment constraints are left to RGW. User functions assume the go-ceph API maps RGW error codes consistently enough for controller idempotency logic.

## Test Signals
This file has no dedicated direct unit test in the requested set, but it is exercised indirectly by `object/account/controller_test.go` using `object.MockClient` and go-ceph `admin.New()`. Those tests verify successful account creation/update/deletion, not-found idempotency, account-conflict errors, root-user creation/update/deletion, and Secret reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/account/controller.go

## Purpose
`controller.go` implements the controller-runtime reconciler for `CephObjectStoreAccount` custom resources. It maps a Kubernetes CR to an RGW account, optionally creates or updates an account-root user, stores root user credentials in a Kubernetes Secret, persists account ownership state in CR status, and deletes only controller-owned RGW resources during finalization.

## Important APIs, Types, and Functions
`ReconcileObjectStoreAccount` holds the Kubernetes client, scheme, operator context, `AdminOpsContext`, cluster spec/info, manager context, and event recorder. `Add`, `newReconciler`, and `add` register the controller and watch `CephObjectStoreAccount` resources. `Reconcile` delegates to `reconcile` and reports status/events. Helpers define account identity and ownership: `getAccountName`, `getAccountID`, `getOrGenerateAccountID`, and `generateDeterministicAccountID`. Core backend operations are `reconcileAccount`, `persistAccountIDToStatus`, `deleteAccount`, `reconcileRootUser`, `reconcileRootUserSecret`, `deleteRootUserSecret`, `updateStatus`, and `updateStatusWithAccountID`.

## Control Flow, State, and Persistence
The reconcile path fetches the CR, adds a finalizer, initializes empty status, checks CephCluster readiness, loads `ClusterInfo`, initializes the object store Admin Ops context, and branches on deletion. On create/update, `reconcileAccount` derives the desired account ID from `spec.accountID`, status, or deterministically from the CR UID. If the account exists, it is modified only when `status.accountID` proves ownership. If it does not exist, the controller first writes `status.accountID` as a creation bookmark, then creates the RGW account. Root-user reconciliation creates or updates a user whose ID is the CR UID, with account-root and generate-key settings on create; if `spec.rootUser.skipCreate` is true, it deletes any prior root user and Secret. Successful reconciliation sets phase `Ready`, observed generation, account ID, and root Secret name. Deletion removes the root user, deletes the account only when status proves ownership, and removes the finalizer. Kubernetes persistence includes CR status, finalizers, events, and the root credential Secret; RGW persistence includes accounts, users, and generated access keys.

## Dependencies and Integration Points
The controller integrates with controller-runtime, Rook's Ceph API types, cluster readiness helpers, `object.InitializeObjectStoreContext`, go-ceph Admin Ops through the object wrapper functions, Rook status reporting, Kubernetes Events, and Secret owner references. It depends on `newMultisiteAdminOpsCtxFunc`, a package variable intentionally replaceable by tests. The root-user Secret uses labels derived from account/store/namespace and `k8sutil.RookType`.

## Risks
Ownership safety is intentionally conservative: existing RGW accounts without `status.accountID` proof are rejected or skipped on delete. That avoids deleting foreign accounts but means manual adoption through spec alone is unsupported. `generateDeterministicAccountID()` assumes a UID-like hex string and can fail for short or non-hex UIDs. `reconcileRootUserSecret()` indexes `user.Keys[0]` without checking key length, so unexpected Admin Ops responses without keys can panic. Root-user display names supplied by users are not truncated even though generated names are, leaving RGW to reject overlong custom names. Status updates are best-effort logging functions in some paths, so failures can leave backend resources created while CR status is stale; the pre-create bookmark reduces the most dangerous orphaning case.

## Test Signals
`controller_test.go` exercises missing and unready CephCluster handling, missing object store/RGW pod readiness, successful full reconcile through mocked Admin Ops HTTP, account naming and deterministic ID generation, ID precedence, crash recovery through status bookmarks, foreign-account refusal, account conflict errors, idempotent deletion, status updates, not-found reconcile, root-user skip behavior, root-user ID/display-name helpers, Secret naming, root-user creation, skip cleanup, and root-user update. Gaps include no direct test for empty `user.Keys`, finalizer removal after live deletion with mocked Admin Ops, and custom overlong root-user display names against RGW constraints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/account/controller_test.go

## Purpose
`controller_test.go` is the behavioral test suite for the `CephObjectStoreAccount` controller. It verifies readiness gates, account identity generation, ownership protections, crash-recovery bookmarking, deletion idempotency, status updates, root-user reconciliation, and Secret management using fake Kubernetes clients and mocked RGW Admin Ops HTTP responses.

## Important APIs, Types, and Functions
The file tests public reconcile entry points and package-private helpers: `Reconcile`, `reconcileAccount`, `deleteAccount`, `updateStatus`, `updateStatusWithAccountID`, `skipRootUserCreation`, `getRootUserID`, `getRootUserDisplayName`, `generateRootUserSecretName`, and `reconcileRootUser`. It uses `cephobject.MockClient` as the go-ceph HTTP client, fake controller-runtime clients, fake client-go clients, `events.NewFakeRecorder`, and a replaceable `newMultisiteAdminOpsCtxFunc`.

## Control Flow, State, and Persistence
The main controller test builds increasingly complete fake cluster state: an account CR, CephCluster readiness state, monitor Secret, CephObjectStore, and RGW pod. The success case replaces Admin Ops initialization with a mocked client that returns 404 for missing account/user, then returns account and root-user JSON for create calls. It verifies CR status becomes `Ready`, the deterministic account ID is recorded, and the root user Secret is created. Other tests isolate state transitions: pre-creation status bookmark writes, status-based ownership proof, deletion of user then account, skipped deletion when ownership proof is missing, and removal of root-user Secrets when `skipCreate` is enabled.

## Dependencies and Integration Points
The suite covers integration between the account controller, Rook cluster readiness helpers, object store context initialization, go-ceph Admin Ops request encoding, Kubernetes status subresources, fake Secrets, and root-user Secret owner-reference behavior. It depends on go-ceph translating mocked RGW error payloads into sentinel errors, preserving the same semantics production code uses.

## Risks
The tests are HTTP-mock based, so they validate controller decisions and go-ceph request paths but not a real RGW. Several tests mutate package-level state such as `newMultisiteAdminOpsCtxFunc` and the global log level; cleanup is present for the function override but this pattern can create ordering sensitivity if tests are parallelized. The success test reads `StringData` from fake Secrets, which is convenient but differs from how Kubernetes stores Secret `Data` after API-server processing. Error-path coverage is strong for account ownership, but weaker for malformed Admin Ops success responses.

## Test Signals
High-value signals include deterministic `RGW` account ID format and stability, spec/status account ID precedence, refusal to adopt foreign accounts, `AccountAlreadyExists` conflict messaging, crash recovery after a status bookmark, idempotent deletion for missing root users/accounts, skipped deletion for foreign spec IDs, observed-generation status writes, root-user display-name truncation for generated names, and Secret cleanup when root user creation is skipped.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/account/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/admin.go

## Purpose
`admin.go` centralizes object-store administration context and helpers. It builds RGW object contexts, creates Admin Ops API clients, runs `radosgw-admin` commands locally or through the command proxy, extracts JSON from noisy command output, commits multisite period changes idempotently, and retrieves or creates the RGW admin-ops user credentials.

## Important APIs, Types, and Functions
`Context` stores the operator context, cluster info, object store identity, endpoint, and multisite realm/zone metadata. `AdminOpsContext` embeds `Context` and adds TLS certs, admin keys, and `*admin.API`. `NewContext`, `NewMultisiteContext`, `GetAdminOpsEndpoint`, `UpdateEndpointForAdminOps`, and `NewMultisiteAdminOpsContext` initialize context and HTTP clients. `NewDebugHTTPClient` wraps an Admin Ops HTTP client and dumps requests/responses at trace level. `RunAdminCommandNoMultisiteWithTimeout` and `runAdminCommandWithTimeout` execute `radosgw-admin`. `CommitConfigChanges`, `periodWillChange`, and `toJsonPath` handle period diffing. `GetAdminOPSUserCredentials` handles external Secret lookup or local admin-ops user creation.

## Control Flow, State, and Persistence
Context creation reads the CephObjectStore advertise endpoint and multisite realm/zone values. Admin Ops client setup fetches or creates credentials, builds a TLS-capable HTTP client, and optionally wraps it for debug dumps. Command execution chooses Multus command-proxy execution when `clusterInfo.NetworkSpec.IsMultus()` is true; otherwise it finalizes Ceph command args and runs `radosgw-admin` from the operator. For Multus commands with `--infile=`, it copies the local file to the proxy container and schedules cleanup. JSON extraction strips surrounding log lines before unmarshalling. `CommitConfigChanges` runs `period get`, stages `period update`, diffs current versus staged JSON while ignoring always-changing period fields, and runs `period update --commit` only when meaningful differences remain. Persistent changes include RGW period commits and admin-ops user/credential creation; external credentials are persisted in a Kubernetes Secret outside this file.

## Dependencies and Integration Points
The file depends on go-ceph Admin Ops, Rook cluster/operator context, Ceph client command helpers, object-store multisite helpers, Kubernetes Secrets, TLS transport helpers, controller namespaced logging, `go-cmp`, and Kubernetes type metadata. It is used by bucket provisioning, account reconciliation, object-store reconcile paths, and bucket metadata/stat helpers.

## Risks
Debug HTTP dumps can expose credentials and response secrets when debug logging is enabled. `debugHTTPClient.Do()` closes the response body after dumping and returns the closed response, which is risky if callers expect to read it later. `extractJSON()` uses broad regular expressions and chooses the larger object/array match when both match, which can misidentify output containing multiple JSON values. `runAdminCommandWithTimeout()` uses exit-code heuristics for FIFO I/O retry and invalid flags; unknown exec errors are conservatively treated as FIFO candidates if exit code extraction fails. `GetAdminOPSUserCredentials()` dereferences `user.AccessKey` and `user.SecretKey` pointers without nil checks after user creation/get.

## Test Signals
`admin_test.go` covers JSON extraction for noisy object and array output, local versus Multus command execution selection, period commit/no-commit/error cases using real-world JSON samples, and Admin Ops endpoint selection for internal, external, TLS, and advertise endpoint configurations. Additional useful tests would cover debug HTTP client body reuse, `--infile` Multus copy/cleanup, FIFO retry branches, and nil credential pointers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin_mock.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/admin_mock.go

## Purpose
`admin_mock.go` defines a minimal mock HTTP client for tests that need to drive go-ceph RGW Admin Ops behavior without a live RGW endpoint.

## Important APIs, Types, and Functions
`MockClient` contains a single `MockDo MockDoType` field. `MockDoType` is a function type matching the `Do(*http.Request) (*http.Response, error)` method required by go-ceph's `admin.HTTPClient`. `(*MockClient).Do()` delegates every request to `MockDo`.

## Control Flow, State, and Persistence
The mock has no internal state beyond whatever the closure assigned to `MockDo` captures. Tests use that closure to inspect request methods, paths, and query strings and to return synthetic HTTP responses. No persistent state is written.

## Dependencies and Integration Points
The file depends only on `net/http`. It is used throughout the object account and bucket tests to construct `admin.New(endpoint, accessKey, secretKey, mockClient)`, letting tests exercise go-ceph request and error handling while controlling RGW responses.

## Risks
If `MockDo` is nil, calling `Do()` panics. The mock does not enforce response-body closing or thread safety. Because request assertions live in each test closure, missed paths can either panic or return nil responses depending on the test implementation.

## Test Signals
The mock is indirectly validated by many account and bucket tests that depend on it for account, user, quota, and bucket Admin Ops behavior. It has no standalone test, which is reasonable given its tiny surface.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin_mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/admin_test.go

## Purpose
`admin_test.go` validates the object admin helpers that parse command output, choose local versus Multus execution, decide whether RGW period changes need committing, and derive Admin Ops endpoints.

## Important APIs, Types, and Functions
The suite tests `extractJSON`, `RunAdminCommandNoMultisite`, `CommitConfigChanges`, and `GetAdminOpsEndpoint`. It defines large real-world period JSON constants representing first reconcile, staged update, second reconcile without changes, and second reconcile with endpoint changes. A mock executor records `period get`, `period update`, and `period update --commit` calls.

## Control Flow, State, and Persistence
`TestExtractJson` feeds invalid strings, noisy object output, multiline objects, arrays, and arrays of objects through the extractor. `TestRunAdminCommandNoMultisite` verifies normal network mode uses the operator executor and Multus mode routes to the remote command executor. `TestCommitConfigChanges` parameterizes command outputs and failures to assert when period update and commit commands are issued. `TestGetAdminOpsEndpoint` mutates `CephObjectStore` specs to check internal service URLs, external endpoint URLs, TLS cert requirements, and advertise endpoint precedence.

## Dependencies and Integration Points
The tests use Rook's mock executor, fake Kubernetes clients, Ceph object store API types, cluster info helpers, and assertion libraries. They encode integration assumptions between `CephObjectStore.GetAdvertiseEndpointUrl()`, Admin Ops connection setup, and the multisite period commit workflow.

## Risks
The period JSON constants are intentionally large and realistic, but they still represent a finite set of RGW output shapes. The Multus test only asserts that the remote path fails with a "no pods found" error, not that command arguments and file-copy cleanup are correct. Endpoint tests cover TLS configuration rules but not CA loading or actual HTTP connection behavior.

## Test Signals
Strong signals include no commit when only ignored period fields change, commit when endpoints or config are added/removed, errors on invalid JSON and failed commands, HTTPS preference when secure port and cert are present, rejection of secure port without cert, and advertise endpoint override of internal/external defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/admin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket.go

## Purpose
`bucket.go` exposes object package helpers for reading RGW bucket metadata and usage statistics through `radosgw-admin`, returning Rook-friendly bucket structs and RGW error codes.

## Important APIs, Types, and Functions
`ObjectBucketMetadata` stores owner and creation time. `ObjectBucketStats` stores total size and object count. `ObjectBucket` combines name, metadata, and stats. `rgwBucketStats` mirrors the subset of `bucket stats` JSON needed by Rook. `bucketStatsFromRGW()` sums usage categories. `GetBucketStats()`, `getBucketMetadata()`, and `GetBucket()` are the exported/internal lookup flow.

## Control Flow, State, and Persistence
`GetBucketStats()` runs `radosgw-admin bucket stats --bucket <name>` through `runAdminCommand`, treats `exit status 2` as not found, unmarshals usage, and sums all usage entries. `getBucketMetadata()` runs `metadata get bucket:<name>`, detects the RGW "can't get key" not-found text, extracts JSON, unmarshals owner and `creation_time`, and parses it using nanosecond UTC layout. `GetBucket()` first gets stats, then metadata, and maps not-found or unknown failures to RGW error codes. It only reads RGW state; it does not persist changes.

## Dependencies and Integration Points
The file depends on the admin command helpers in `admin.go`, JSON unmarshalling, time parsing, and package RGW error constants. It is useful to code paths that need bucket inspection without using S3 or go-ceph Admin Ops bucket APIs.

## Risks
Not-found detection is string based: `exit status 2` and "can't get key" could change across Ceph versions or localization. `getBucketMetadata()` reports command errors as "failed to list buckets", which is misleading for metadata get failures. The time layout requires a specific fractional UTC format. Stats summing assumes all usage categories should be aggregated and does not validate that returned bucket name matches the requested bucket.

## Test Signals
No direct test for this file is in the requested set. Related admin tests cover JSON extraction, but bucket-specific stats/metadata parsing, not-found mapping, date parsing, and multi-category summing would benefit from dedicated unit tests with mocked `runAdminCommand` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller.go

## Purpose
`controller.go` registers and runs Rook's Object Bucket Claim provisioner integration. It watches operator ConfigMaps and CephCluster creation events, loads cluster info, and starts the lib-bucket-provisioner controller with Rook's `Provisioner` implementation.

## Important APIs, Types, and Functions
`ReconcileBucket` stores the Kubernetes client, Rook context, cluster info, operator config, and manager context. `Add()` honors the `DisableOBCEnvVar` environment variable and registers the reconciler. `newReconciler()` constructs the reconciler. `add()` creates the controller and attaches ConfigMap and CephCluster watches with custom predicates. `Reconcile()` delegates to `reconcile()` with panic recovery. `reconcile()` performs cluster checks and starts `NewBucketController()`.

## Control Flow, State, and Persistence
On reconcile, the controller fetches the CephCluster named by the request. If missing, deleting, or under data-dir cleanup policy, it returns without action. Otherwise it loads cluster info from monitor Secrets and cluster spec. It creates a `Provisioner`, constructs a lib-bucket-provisioner controller using the operator kubeconfig, starts `RunWithContext()` in a goroutine, and immediately checks whether startup reported an error. The main persistent effect is not a Kubernetes object from this controller itself, but a long-running bucket controller that later creates/updates ObjectBucket resources and claim Secrets/ConfigMaps through the library.

## Dependencies and Integration Points
The file integrates controller-runtime, Rook operator readiness helpers, Ceph cluster info loading, the lib-bucket-provisioner, ConfigMap and CephCluster predicates, and the object bucket provisioner implementation. It also relies on manager reload behavior when the OBC watch namespace setting changes.

## Risks
Every successful reconcile starts a new goroutine running a bucket controller; without an explicit guard, repeated reconciles could start multiple controllers until the shared manager context is canceled. The startup error channel is unbuffered and only checked immediately, so later goroutine errors may block when sending if no receiver remains. The CephCluster watch only triggers on create, so changes after startup depend on manager reload or other external events. Tests intentionally cannot fully mock lib-bucket-provisioner internals.

## Test Signals
`controller_test.go` covers no-op behavior when no CephCluster exists and a nominal startup path with fake cluster info and a cancelable context. It does not assert duplicate-controller prevention, delayed goroutine errors, cleanup-policy skip behavior, or disable-env behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller_test.go

## Purpose
`controller_test.go` validates the high-level bucket controller reconcile behavior around CephCluster presence and provisioner startup.

## Important APIs, Types, and Functions
The suite tests `ReconcileBucket.Reconcile()` through two subtests. It builds fake controller-runtime clients, fake client-go clients, a `clusterd.Context`, `OperatorConfig`, `CephCluster`, monitor Secret, and lib-bucket-provisioner object types. It uses a dummy `rest.Config{}` because lib-bucket-provisioner expects a kubeconfig.

## Control Flow, State, and Persistence
The first subtest reconciles without a CephCluster and expects no error and no requeue. The second creates a CephCluster and monitor Secret, sets a fake kubeconfig, starts reconcile with a cancelable context, waits briefly for the bucket manager goroutine to start, and cancels the context. Persistent fake state includes the monitor Secret needed by `LoadClusterInfo`.

## Dependencies and Integration Points
The tests integrate controller-runtime fake clients, the Rook scheme, Kubernetes Secrets, lib-bucket-provisioner API types, and Rook cluster-info loading. Comments document why deeper mocking of lib-bucket-provisioner is difficult due to unexported internals.

## Risks
The "success" test mostly verifies no immediate error; it does not prove the bucket controller can list/watch resources against a real API server. It sleeps for two seconds, which can add test latency and still be timing-sensitive. The test does not cover environment-based disabling, cleanup policy skip, missing monitor Secret requeue semantics, duplicate CephCluster predicate behavior, or goroutine error handling.

## Test Signals
Useful current signals are that reconcile is inert when no cluster exists and that the startup path can be invoked with fake cluster credentials. Additional signals should assert no duplicate controllers across multiple reconciles and verify `ROOK_OBC_WATCH_OPERATOR_NAMESPACE` reload behavior through predicate tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/predicate.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/predicate.go

## Purpose
`predicate.go` defines event filters for the bucket provisioner controller watches. It limits ConfigMap and CephCluster events to the ones that should start or restart OBC watching.

## Important APIs, Types, and Functions
`rookOBCWatchOperatorNamespace` names the operator setting key `ROOK_OBC_WATCH_OPERATOR_NAMESPACE`. `cmPredicate()` returns typed predicate functions for ConfigMap create/update/delete/generic events. `cephClusterPredicate()` returns typed predicates for CephCluster events and uses `controller.DuplicateCephClusters()` to suppress duplicate clusters in a namespace.

## Control Flow, State, and Persistence
For ConfigMaps, create events are accepted only for the operator settings ConfigMap at generation 1. Update events compare the watched namespace setting; when it changes, the predicate logs and calls `controller.ReloadManager()` so the manager restarts and rebuilds watches. Update, delete, and generic events all return false. For CephClusters, create events reconcile only if there is no duplicate cluster; update, delete, and generic events return false. There is no direct persisted state, but `ReloadManager()` changes operator process lifecycle.

## Dependencies and Integration Points
The file depends on controller-runtime typed predicates/events, core ConfigMaps, Rook CephCluster types, and Rook controller helpers. It is wired by `bucket/controller.go` when registering watches.

## Risks
Only ConfigMap create and CephCluster create events enqueue reconciles. If the CephCluster transitions from not ready to ready after the initial create, the bucket controller relies on reconcile requeues from failed cluster-info loading or other paths, not this predicate's update handling. Calling `ReloadManager()` from a predicate is a broad side effect; changes to one ConfigMap setting restart the manager rather than just updating an informer. There are no direct tests for these predicates in the requested set.

## Test Signals
Coverage is indirect through bucket controller tests. Dedicated predicate tests should cover generation filtering, watch-namespace setting changes, manager reload call behavior through an injectable hook, duplicate CephCluster suppression, and false returns for updates/deletes/generic events.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner.go

## Purpose
`provisioner.go` implements the lib-bucket-provisioner `Provisioner` interface for Ceph RGW. It provisions new S3 buckets, grants access to existing buckets, deletes buckets, revokes access, composes `ObjectBucket` connection data, initializes object store/Admin Ops/S3 clients, and reconciles optional quotas, bucket policies, and lifecycle configuration from OBC additional config.

## Important APIs, Types, and Functions
`Provisioner` stores long-lived operator context and cluster info plus per-operation fields such as bucket name, object store name, endpoint, user name, access keys, TLS certs, Admin Ops client, and S3 agent. `additionalConfigSpec` holds parsed optional settings: user quota, bucket quota, bucket policy, lifecycle, and explicit bucket owner. Interface methods are `GenerateUserID`, `Provision`, `Grant`, `Delete`, and `Revoke`. Initialization and composition helpers include `initializeCreateOrGrant`, `initializeDeleteOrRevoke`, `composeObjectBucket`, `setObjectContext`, `populateDomainAndPort`, `setTlsCaCert`, `setAdminOpsAPIClient`, and `setS3Agent`. Additional-state constants and parsing helpers are defined in `util.go`, including `additionalConfigSpecFromMap()` and `quanityToInt64()`.

## Control Flow, State, and Persistence
`Provision()` parses additional config, initializes from the OBC StorageClass, gets or creates user credentials, creates or relinks the bucket, restricts generated users to one bucket, applies quotas/policy/lifecycle, and returns an ObjectBucket containing endpoint, credentials, and additional state. `Grant()` initializes similarly, verifies the target bucket exists, gets credentials for a generated or explicit user, restricts generated users to zero new buckets, applies additional settings, and either respects a user-managed bucket policy or injects an allow policy statement for the OBC user. `Delete()` initializes from the ObjectBucket, purges the bucket, and deletes the generated user when safe. `Revoke()` removes or denies policy access depending on bucket ownership, then deletes generated users. Persistent state spans RGW users, keys, bucket ownership links, bucket contents, quotas, bucket policies, lifecycle rules, and Kubernetes ObjectBucket connection/additional-state fields.

## Dependencies and Integration Points
The provisioner integrates lib-bucket-provisioner, Rook cluster context, CephObjectStore CRs, StorageClasses, go-ceph Admin Ops, AWS SDK v2 S3 APIs, object S3 agent helpers, TLS CA loading, object-store advertise endpoints, and OBC additional config gating through operator settings. It writes ObjectBucket state keys `cephUser`, `objectStoreName`, `objectStoreNamespace`, and optionally `bucketOwner`.

## Risks
Several methods use value receivers (`Provision`, `Grant`, `Delete`, `Revoke`), then pass `&p` into helpers, which isolates per-call mutation but can be confusing and may hide assumptions about long-lived fields. Many paths assume `user.Keys[0]` exists. `Revoke()` returns nil immediately when the bucket owner user is missing, which may skip deletion of the OBC-generated access user in that branch. Bucket policy and lifecycle operations use `context.TODO()` instead of cluster/operator contexts. Additional config can delete existing user or bucket quotas by setting no quota fields, which is intentional but operationally significant. Explicit `bucketOwner` disables user quota management and protects external users from deletion, but misconfiguration can grant access using a powerful existing user.

## Test Signals
`provisioner_test.go` covers endpoint parsing, quantity parsing, user quota diffing, bucket quota diffing, allowed additional config parsing, and disallowed advanced fields. `rgw-handlers_test.go` covers idempotent bucket deletion and generated-user detection. Missing signals include full `Provision`/`Grant`/`Delete`/`Revoke` integration with mocked S3 calls, bucket policy merge/drop behavior, lifecycle diffing, TLS CA paths, explicit bucket owner credential errors, and empty user key arrays.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner_test.go

## Purpose
`provisioner_test.go` validates key helper behavior in the RGW bucket provisioner: endpoint/domain resolution, quantity parsing, user quota reconciliation, bucket quota reconciliation, and parsing/allow-listing of OBC additional config.

## Important APIs, Types, and Functions
The suite tests `populateDomainAndPort`, `quanityToInt64`, `setUserQuota`, `setBucketQuota`, and `additionalConfigSpecFromMap`. It creates `Provisioner` instances with fake Rook and Kubernetes clients, fake CephObjectStore and Service resources, and go-ceph Admin Ops clients backed by `object.MockClient`. `numberOfCallsWithValue()` checks query-string fragments in recorded Admin Ops calls.

## Control Flow, State, and Persistence
Endpoint tests first fail missing/invalid endpoints, then accept `192.168.0.1:80`, then resolve a CephObjectStore service hostname when no StorageClass endpoint is provided. Quota tests mock Admin Ops `GET` responses for user or bucket quota state, call the setter, and verify whether a `PUT` was issued with expected query parameters. Additional config tests toggle `ROOK_OBC_ALLOW_ADDITIONAL_CONFIG_FIELDS` and `opcontroller.SetObcAllowAdditionalConfigFields()` to assert which keys are allowed and how values are parsed.

## Dependencies and Integration Points
The tests exercise go-ceph Admin Ops query encoding, Kubernetes `resource.ParseQuantity`, Rook object-store service endpoint logic, StorageClass parameter conventions, operator additional-config allow-list state, and AWS pointer helpers for expected int64 values.

## Risks
The file intentionally focuses on helper units and does not cover S3 policy/lifecycle APIs or the full provision/grant/delete/revoke flows. It uses global environment/operator allow-list state and resets it in most advanced-field subtests; this should not be parallelized casually. The test name and function are misspelled as `Quanity`, matching production code, which can make searchability worse but preserves current API names.

## Test Signals
Strong signals include quota no-op when live state already matches, disabling quotas when no config is provided, enabling and updating max object/size quotas, rejecting invalid quantities, resolving object store service hostnames, and enforcing additional config fields as disallowed by default except the baseline max quota keys when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/provisioner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers.go

## Purpose
`rgw-handlers.go` contains RGW-specific helper operations used by the bucket provisioner for user credential lookup/creation, bucket existence checks, deterministic OBC user naming, bucket deletion, generated-user deletion, and generated-user detection.

## Important APIs, Types, and Functions
The temporary `bucket` struct groups per-request provisioner state, lib-bucket options, and parsed additional config. `(*bucket).getUserCreds()` creates or reads the bucket user depending on whether `bucketOwner` is configured. `(*Provisioner).bucketExists()` wraps `AdminOpsClient.GetBucketInfo`. `createCephUser()` gets or creates an RGW user. `genUserName()` derives the current OBC user format from namespace, name, and UID. `deleteBucket()` purges buckets through Admin Ops. `deleteOBUser()` removes only generated users. `isObcGeneratedUser()` recognizes current and historical generated-user formats while respecting explicit bucket owners.

## Control Flow, State, and Persistence
For generated users, `getUserCreds()` calls `createCephUser()`, which first attempts `GetUser` and creates only on `ErrNoSuchUser`. For explicit `bucketOwner`, it only reads an existing user. Bucket deletion uses `RemoveBucket` with purge enabled and treats `ErrNoSuchBucket` as success. For `ErrNoSuchKey`, it checks `GetBucketInfo` to distinguish not-found from other failures. User deletion reconstructs an OBC identity from the ObjectBucket claim reference, restores `bucketOwner` from additional state if present, and deletes the user only if it matches generated formats. Persistent state changes are RGW user creation, user deletion, and bucket purge/delete.

## Dependencies and Integration Points
The helpers depend on go-ceph Admin Ops, lib-bucket-provisioner ObjectBucket/ObjectBucketClaim types, ObjectBucket additional state written by `composeObjectBucket`, and logging. They are called by `Provision`, `Grant`, `Delete`, and `Revoke`.

## Risks
Both credential paths assume `user.Keys[0]` exists. `createCephUser()` logs "successfully created" even when it found an existing user. `deleteOBUser()` intentionally logs delete failures as warnings and returns nil, which favors access revocation progress over strict cleanup but can leave stale generated users. Historical generated-user matching is broad (`obc-namespace-name` prefix and `ceph-user-...` regex), so a manually named user can be treated as generated unless `bucketOwner` is recorded. The current username format includes namespace/name without truncation, relying on RGW's high user-name limit.

## Test Signals
`rgw-handlers_test.go` validates idempotent bucket deletion for `NoSuchBucket`, the `NoSuchKey` compatibility path, error return when `NoSuchKey` is not actually not-found, and generated-user detection for current, old, very old, and explicit-bucketOwner cases. Missing signals include `getUserCreds()` with empty key arrays, create-user conflict behavior, and delete-user warning-only semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers_test.go

## Purpose
`rgw-handlers_test.go` tests RGW helper edge cases for bucket deletion idempotency and OBC-generated user detection.

## Important APIs, Types, and Functions
The file defines a small `statusError` implementing `ExitStatus()` to construct go-ceph admin errors with specific RGW codes. `TestDeleteBucket` exercises `deleteBucket()` using a fake Admin Ops client. `TestIsObcGeneratedUser` exercises `isObcGeneratedUser()` with current, historical, and explicit owner naming scenarios.

## Control Flow, State, and Persistence
`TestDeleteBucket` creates a mock Admin Ops HTTP client that returns `NoSuchBucket`, `NoSuchKey`, or other errors for bucket removal and sometimes bucket info. It asserts that missing buckets are treated as success and ambiguous `NoSuchKey` is checked through bucket info. `TestIsObcGeneratedUser` builds a provisioner with an object context, then passes synthetic OBCs and usernames through the detection helper. All state is in memory and captured in closures.

## Dependencies and Integration Points
The tests use go-ceph Admin Ops error decoding, the object `MockClient`, lib-bucket-provisioner OBC metadata, and Rook object contexts. They protect compatibility with older OBC user naming schemes that may still exist in upgraded clusters.

## Risks
The tests do not cover actual user deletion or credential lookup, only the detection logic used by deletion. The historical prefix and regex checks are deliberately permissive; tests document that behavior but cannot prevent accidental matches for manually named users unless `bucketOwner` is set. Mock HTTP paths must stay aligned with go-ceph's Admin Ops request paths.

## Test Signals
Useful signals include no error for missing buckets, correct fallback when Ceph returns `NoSuchKey` for missing buckets, error propagation when bucket info lookup fails, false for unrelated users, true for current generated names, true for old `obc-namespace-name...` names, true for very old `ceph-user-xxxxxxxx` names, and false when `bucketOwner` explicitly matches the username.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers_test.go -->
