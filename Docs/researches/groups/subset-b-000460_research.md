# subset-b-000460 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller.go

Purpose: implements a controller-runtime reconciler that treats `bucket-notification-*` labels on `ObjectBucketClaim` resources as the desired bucket notification set for the backing Ceph RGW bucket.

Important APIs/types: `ReconcileOBCLabels`, `obcPredicate`, `addOBCLabelReconciler`, `Reconcile`, `reconcile`, and `addNewNotification`. Constants define the notification label prefix and the expected ceph bucket provisioner labels. The code uses helper functions from the notification controller file, including `getCephObjectStoreName`, `getReadyCluster`, and `validateObjectStoreName`, plus requeue constants for object bucket, topic, notification, and delete readiness.

Control flow: the predicate reconciles creates/deletes and updates where labels or `Spec.ObjectBucketName` change, while respecting `do_not_reconcile` on updates. Reconcile fetches the OBC, ignores not-found and deleted objects, requeues until the OBC has produced an object bucket name, fetches the `ObjectBucket`, ignores non-Ceph provisioned buckets, derives the object store, loads ready Ceph cluster state, and builds a notification `provisioner`. It lists existing RGW notification IDs, extracts desired IDs from OBC labels where key suffix and value match, deletes existing IDs absent from labels, then attempts to add each desired notification by fetching `CephBucketNotification`, resolving its `CephBucketTopic`, validating object store identity, and calling the S3 provisioning path.

State and persistence: desired state is encoded in OBC labels; actual state is in RGW bucket notification configuration; dependent state is in `ObjectBucket`, `CephBucketNotification`, `CephBucketTopic`, and `CephCluster` objects. The controller emits Kubernetes events via the recorder and returns requeue results for eventual consistency.

Dependencies and integration points: integrates kube-object-storage OBC/OB CRDs, Rook Ceph CRDs, object bucket helpers, topic status ARN lookup, controller-runtime watches, Rook cluster readiness loading, and notification S3 provisioning/deletion functions that are overrideable in tests.

Risks: label parsing is intentionally strict but order over map iteration is nondeterministic; create errors stop the loop after prior deletes may already have occurred; delete failures are aggregated only as a retry boolean; `strings.Contains` provisioner matching could match unexpected provisioner strings; missing object store/topic readiness is handled by requeue but still reports errors for some not-ready paths.

Test signals: `obc_label_controller_test.go` exercises missing OB, not-ready bucket, missing notification/topic, successful single and multiple creates, deletes for absent labels, mixed delete/create, and ignoring OBCs from another provisioner. Tests use overrideable notification functions and fake clients.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller_test.go

Purpose: verifies the OBC label notification controller behavior using fake Kubernetes objects and mocked notification operations.

Important APIs/types: helper constructors `createOBResources`, `createBucketNotification`, and `setNotificationLabels`; main test `TestCephBucketNotificationOBCLabelController`; test constants for alternate provisioner identity. The test relies on package-level test hooks such as `getAllNotificationsFunc`, `createNotificationFunc`, and `deleteNotificationFunc` configured by shared `mockSetup`/`resetValues` helpers elsewhere in the package.

Control flow: each subtest builds a runtime object set containing a ready `CephCluster`, OBC/OB objects, optional notification CRs, and optional topic CRs. It invokes `testOBCLabelReconciler`, then asserts reconcile result, error presence, whether notification listing was called, and created/deleted notification ID slices. Cases cover waiting for an object bucket name, missing object bucket, missing notification CR, missing topic ARN, successful provisioning, already existing labels, removing labels, multiple labels, simultaneous stale and new IDs, and non-Ceph provisioner filtering.

State and persistence: all state is in fake API objects and in-memory test globals for created/deleted notifications and event capture. The test intentionally mutates a shared OBC from pending to bound before later cases, mirroring controller readiness progression.

Dependencies and integration points: depends on kube-object-storage API types, Rook Ceph CRDs, fake runtime object clients, the topic status ARN contract, and event verification helpers from the notification test suite.

Risks: tests validate high-level reconcile outcomes but not actual AWS/Ceph request serialization, label map iteration order, duplicate labels, or mismatched label key/value warning behavior. Shared mutable objects and globals require `resetValues` to avoid test coupling.

Test signals: strong unit coverage exists for the label-to-notification diff and readiness paths. The main missing signal is direct coverage of predicate behavior and delete failure retry behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/provisioner.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/notification/provisioner.go

Purpose: adapts Rook/Ceph object-store context into AWS SDK S3 operations for bucket notification creation, listing, and deletion.

Important APIs/types: `provisioner`, `getUserCredentials`, `newS3Agent`, `createS3FilterRules`, `createS3Filter`, `createS3Events`, `createNotification`, `getAllRGWNotifications`, and `deleteNotification`. Package-level variables allow the create/list/delete functions to be replaced in tests.

Control flow: `newS3Agent` retrieves the `CephObjectStore`, builds a multisite object context, creates an Admin Ops context, fetches the bucket owner user's RGW credentials, optionally obtains TLS CA/insecure settings, and returns an `object.S3Agent`. Create builds a `PutBucketNotificationConfigurationInput` with one topic configuration whose ID is the notification CR name, events default to object-created and object-removed wildcards when unspecified, and filters are translated from Rook CRD key rules. List calls `GetBucketNotificationConfiguration` and returns topic configuration IDs. Delete delegates to the custom Ceph S3 extension in `s3ext.go`.

State and persistence: reads Kubernetes `CephObjectStore`; reads Ceph RGW user credentials through Admin Ops; writes bucket notification configuration through S3 APIs; deletes notification state through a manually signed Ceph extension request. It does not store local state.

Dependencies and integration points: depends on AWS SDK v2 S3 types, go-ceph RGW admin user data, Rook object context/Admin Ops helpers, bucket owner metadata from `ObjectBucket.Spec.AdditionalState`, topic ARNs from notification controller flow, and TLS helper `GetTlsCaCert`.

Risks: `getUserCredentials` assumes `u.Keys[0]` exists; `createNotification` submits a configuration containing only one topic configuration and may replace preexisting configurations depending on RGW semantics; list dereferences `tc.Id`; delete uses `context.TODO()` instead of the operator manager context. Defaulting empty event lists to both create/remove events is significant and should remain explicit in CRD docs.

Test signals: direct unit tests are primarily through the OBC label controller's function overrides. There is no focused test here for credential edge cases, filter/event conversion, preservation of multiple topic configurations, or TLS S3 agent creation through the provisioner.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/provisioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/s3ext.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/notification/s3ext.go

Purpose: implements Ceph RGW's non-standard S3 DELETE notification endpoint using AWS SDK v2 credentials, endpoint configuration, and SigV4 signing.

Important APIs/types: `DeleteBucketNotificationRequestInput`, its `validate` method, `emptyPayloadSHA256`, and `DeleteBucketNotification`.

Control flow: the delete helper defaults nil input, validates that `Bucket` is non-empty, derives the base endpoint from `client.Options().BaseEndpoint`, builds `DELETE /<bucket>?notification` or `DELETE /<bucket>?notification=<id>`, adds the empty payload hash and optional expected-owner header, retrieves credentials from the S3 client's credential provider, signs the HTTP request with SigV4 for service `s3`, sends it through the SDK-configured HTTP client, and treats any HTTP status >=300 as an error with response body included.

State and persistence: no local state. It deletes RGW bucket notification configuration server-side.

Dependencies and integration points: depends on the AWS SDK v2 S3 client options for endpoint, region, credentials, and HTTP client. It is called by `deleteNotification` in `provisioner.go`.

Risks: notification IDs are interpolated into the query string without URL escaping; empty or nil `BaseEndpoint` can produce malformed URLs; response body is read into memory for error paths; signing time uses `time.Now()` directly; expected bucket owner is supported but caller currently does not pass it. Because this is outside the AWS modeled API, SDK behavior changes around `BaseEndpoint` or signing options can break it.

Test signals: no dedicated tests in the listed subset. Coverage is indirect through mocked delete paths in controller tests, so real request construction, signing, escaping, and HTTP status handling are not locked down here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/s3ext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/objectstore.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/objectstore.go

Purpose: central object-store operations for Rook's Ceph RGW operator: realm/zone lifecycle, pool creation/deletion, multisite endpoint membership, shared-pool zone JSON configuration, realm key secret helpers, dashboard RGW API user management, and utility validation.

Important APIs/types: JSON structs `idType`, `zoneGroupType`, `zoneType`, `realmType`; lifecycle functions `deleteRealmAndPools`, `removeObjectStoreFromMultisite`, `deleteSingleSiteRealmAndPools`, `configureObjectStore`, `createNonMultisiteStore`, `JoinMultisite`, `createSystemUser`; pool functions `CreateObjectStorePools`, `DeletePools`, `missingPools`, `poolsExistForNonRawOps`, `ConfigureSharedPoolsForZone`, `sharedPoolsExist`; helpers `GetRealmKeySecret`, `GetRealmKeyArgs`, `DecodeZoneGroupConfig`, `ShouldUpdateZoneEndpointList`, `ValidateObjectStorePoolsConfig`, `InitializeObjectStoreContext`.

Control flow: non-multisite setup creates realm, zonegroup, and zone if absent, configures shared pools, then commits period/config changes. Multisite setup adjusts endpoint membership for zones and zonegroups when sync traffic is enabled/disabled, commits changes, and creates a realm system user only on master zone/master zonegroup. Deletion removes endpoints from multisite or removes single-site realm/zone/zonegroup and optionally pools. Pool creation builds metadata/root/data pools, optionally concurrently unless operator resource limits are configured. Shared-pool configuration validates pool existence, reads zone and zonegroup JSON, rewrites default/internal pools and placement pools, compares deep copies, writes changed JSON through `radosgw-admin zone/zonegroup set`, and leaves existing non-empty old pools unmapped to avoid data loss.

State and persistence: persists Ceph realms, zonegroups, zones, periods, pools, erasure-code profiles, dashboard module settings, RGW users, and Kubernetes realm-key Secrets. Temporary files are used for zone/zonegroup JSON updates. Endpoint state is persisted in radosgw-admin JSON.

Dependencies and integration points: heavy integration with `cephclient`, Rook `clusterd.Context`, controller-runtime clients, Kubernetes CoreV1 Secrets, Rook Ceph CRDs, Admin Ops/user helpers, `RunAdminCommandNoMultisite`/`runAdminCommand`, shared-pool JSON helper functions in `shared_pools.go`, RGW deployment logic in `rgw.go`, and bucket provisioner environment settings.

Risks: many paths interpret command exit codes and command output, so Ceph CLI changes are high risk. Concurrency in pool creation/deletion depends on closure correctness and operator resources. Some deletion paths are best-effort and log warnings rather than failing. Shared-pool JSON mutation must track evolving Ceph fields; unknown pool fields are only warned. `configureObjectStore` has nuanced endpoint logic around `DisableMultisiteSyncTraffic`. Dashboard secret setting uses a goroutine because of historical hangs, making completion asynchronous.

Test signals: `objectstore_test.go` covers realm configuration idempotency/error branches, shared-pool zone updates, deletion pool/root-pool behavior, provisioner naming, dashboard credentials, realm-key secret decoding, endpoint list comparison, pool config validation, and shared-pool existence. Gaps remain around live Ceph/RGW integration, command output format drift, and asynchronous dashboard secret-setting failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/objectstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/objectstore_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/objectstore_test.go

Purpose: broad unit test coverage for object-store lifecycle helpers, shared-pool configuration, realm key secret handling, endpoint comparison, dashboard user management, and object pool validation.

Important APIs/tests: `TestReconcileRealm`, `TestConfigureStoreWithSharedPools`, `TestDeleteStore`, `TestGetObjectBucketProvisioner`, `TestCheckDashboardUser`, `TestDashboard`, `Test_createMultisite`, `Test_createMultisiteConfigurations`, `TestGetRealmKeySecret`, `TestGetRealmKeyArgsFromSecret`, `TestGetRealmKeyArgs`, `TestUpdateZoneEndpointList`, `TestListsAreEqual`, `TestValidateObjectStorePoolsConfig`, and `Test_sharedPoolsExist`. Large JSON constants model RGW zone and zonegroup command output.

Control flow: tests use `exectest.MockExecutor` to assert specific `ceph`/`radosgw-admin` commands and return synthetic JSON or exit codes. Shared-pool tests read the temp `--infile` JSON written by production code to validate persistence flow. Multisite tests table-drive which realm/zonegroup/zone resources already exist or fail creation, then assert which command branches and commit calls happened. Endpoint and pool validation tests table-drive many list and spec combinations.

State and persistence: test state is in mocked command responses, fake Kubernetes clients/secrets, environment variables, temp config dirs, and booleans counting command calls. It validates deletion counters for pools, root pool, CRUSH rules, and erasure-code profiles.

Dependencies and integration points: covers interactions with `cephclient`, mocked executor exit codes, Kubernetes fake CoreV1 secrets, Rook test clients, Ceph version gates, environment settings `ROOK_OBC_WATCH_OPERATOR_NAMESPACE` and `ROOK_OBC_PROVISIONER_NAME_PREFIX`, and shared-pool JSON helpers.

Risks: tests encode exact command shapes and JSON samples, which is useful but can become brittle when Ceph CLI schemas evolve. Some assertions verify error string fragments with formatting oddities. Integration behavior with real Ceph daemons, concurrent pool creation, and asynchronous dashboard secret update is not exercised.

Test signals: strong regression signal for many edge cases: root pool deletion only for last store, shared pools missing each required pool, duplicate placement names, endpoint ordering, secret key missing messages, and provisioner prefix validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/objectstore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/policy.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/policy.go

Purpose: provides a small S3 bucket-policy model and fluent helpers for constructing, reading, modifying, and applying bucket policies through `S3Agent`.

Important APIs/types: `action` constants for many S3 actions; `AllowedActions`; `effect`; `PolicyStatement`; `BucketPolicy`; `NewBucketPolicy`; `S3Agent.PutBucketPolicy`; `S3Agent.GetBucketPolicy`; `BucketPolicy.ModifyBucketPolicy`; `BucketPolicy.DropPolicyStatements`; `NewPolicyStatement`; fluent methods `WithSID`, `ForPrincipals`, `ForResources`, `ForSubResources`, `Allows`, `Denies`, and `Actions`.

Control flow: construction copies passed statements into a versioned policy. Put marshals the policy to JSON and sends `PutBucketPolicy` with `ConfirmRemoveSelfBucketAccess=false`. Get fetches policy JSON and unmarshals it into the local struct. Modify replaces the entire statement slice with the supplied statements. Drop removes the first matching statement for each SID. Fluent statement methods append AWS-style ARNs for Ceph users and buckets, set allow/deny only if no effect is already set, and set actions.

State and persistence: policy state exists in memory until pushed; `PutBucketPolicy` persists to RGW/S3 bucket policy; `GetBucketPolicy` reads persisted policy. No Kubernetes state is touched.

Dependencies and integration points: depends on `S3Agent` from `s3-handlers.go`, AWS SDK v2 S3 policy APIs, and Kubernetes JSON helpers. It is likely used by bucket/user controllers to grant access.

Risks: JSON marshal error is ignored; `GetBucketPolicy` assumes `out.Policy` is non-nil; `DropPolicyStatements` removes only the first statement for a SID per requested SID; `Allows` and `Denies` are first-writer-wins, so callers cannot change an existing effect through chaining. The `Principal` comment spells "Principle" in constants but the JSON key is correct.

Test signals: `policy_test.go` specifically locks down the newer replace-not-merge behavior of `ModifyBucketPolicy`, including duplicate SID replacement and preserving passed statement order.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/policy_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/policy_test.go

Purpose: focused unit tests for `BucketPolicy.ModifyBucketPolicy`.

Important APIs/tests: `TestModifyBucketPolicy` has subtests for duplicate SID replacement, full statement replacement, and preserving the order of newly supplied statements.

Control flow: each subtest builds a `BucketPolicy` with one or more `PolicyStatement`s using fluent helpers, calls `ModifyBucketPolicy`, then asserts statement count, SID, and effect.

State and persistence: all state is in memory. No S3 calls or serialization paths are invoked.

Dependencies and integration points: uses the policy builder API in `policy.go` and `stretchr/testify/assert`.

Risks: the test only covers modify semantics. It does not cover JSON shape, ARN formatting, put/get S3 integration, `DropPolicyStatements`, or first-writer-wins behavior in `Allows`/`Denies`.

Test signals: the file clearly documents intended behavior after a semantic change: modification replaces the statement list, rather than merging by SID.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/realm/controller.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/realm/controller.go

Purpose: controller-runtime reconciler for `CephObjectRealm` CRs, responsible for creating local realms, pulling remote realms, generating realm access keys, setting default realm when requested, and updating status.

Important APIs/types: `ReconcileObjectRealm`, `Add`, `newReconciler`, `add`, `Reconcile`, `reconcile`, `pullCephRealm`, `createCephRealm`, `createRealmKeys`, `validateRealmCR`, `setFailedStatus`, and `updateStatus`. Constants define controller name and generated key lengths.

Control flow: the controller watches `CephObjectRealm` resources with Rook's standard predicate. Reconcile fetches the CR, initializes empty status, checks CephCluster readiness, ignores deletes when appropriate, loads cluster info, validates name/namespace, marks reconciling, then either pulls a realm from `Spec.Pull.Endpoint` using the realm key Secret or creates keys and creates the realm if absent. If `Spec.DefaultRealm` is set, it calls `object.SetDefaultRealm`. Success updates status to Ready with observed generation; failures on key/realm creation set failed status.

State and persistence: persists Kubernetes Secret `<realm>-keys` with `access-key` and `secret-key`, owner-referenced to the realm; persists Ceph realm state through `radosgw-admin realm create` or `realm pull`; updates CR status phase and observed generation; may set Ceph default realm.

Dependencies and integration points: depends on Rook cluster readiness/load helpers, `mgr.GeneratePassword`, object package realm key helpers, `RunAdminCommandNoMultisite`, status reporting, fake recorder events, Kubernetes CoreV1 Secrets, and controller-runtime clients.

Risks: generated keys are base64-encoded before storing and then used as command args; this is an intentional contract but easy to misunderstand. Pull mode requires the key Secret to preexist and requeues if missing. `createCephRealm` depends on ENOENT exit-code detection. Status updates refetch the object and can fail silently with logs. Default realm behavior depends on Ceph support in the object package.

Test signals: `controller_test.go` covers no-cluster and not-ready requeues, successful reconcile with ready cluster, pull realm, create realm keys, create realm, idempotent key creation, and failure when an existing key Secret lacks required data.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/realm/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/realm/controller_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/realm/controller_test.go

Purpose: tests `CephObjectRealm` reconciliation and key/realm helper behavior with fake clients and mocked executor responses.

Important APIs/tests: `TestCephObjectRealmController`, `TestPullCephRealm`, `TestCreateRealmKeys`, `TestCreateCephRealm`, `getObjectRealmAndReconcileObjectRealm`, and `TestReconcileObjectRealm_createRealmKeys`.

Control flow: the main controller test first reconciles without a ready CephCluster and expects requeues, then adds a ready cluster plus mon secret and mocked `realm get` output to verify successful reconciliation. Pull testing creates a `<realm>-keys` Secret and calls `pullCephRealm`. Key creation tests call `createRealmKeys` directly and validate idempotency across repeated reconciles. A negative subtest checks that an existing Secret missing `secret-key` fails with the expected guidance.

State and persistence: uses fake controller-runtime clients for CRs, fake CoreV1 clients for Secrets, a fake event recorder, and mocked command output for Ceph status and realm operations.

Dependencies and integration points: integrates Rook fake clientsets, Kubernetes scheme registration for Ceph types, `exectest.MockExecutor`, `cephclient.AdminTestClusterInfo`, and Rook test helpers.

Risks: real command-line error branches and default realm behavior are only lightly covered. The test uses package-global scheme registration and globals for realm names, which can couple tests if expanded carelessly.

Test signals: coverage is strongest for readiness gating and Secret idempotency. It documents that malformed existing Secrets fail rather than being overwritten.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/realm/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw-probe.sh -->
## sources/control-plane/rook/pkg/operator/ceph/object/rgw-probe.sh

Purpose: templated bash probe script for RGW startup/readiness checks that provides custom treatment for RGW throttling and misconfiguration responses.

Important APIs/variables: template variables `ProbeType`, `Port`, `Protocol`, and `Path`; constants `USAGE_ERR_CODE=125`, `PROBE_ERR_CODE=124`, `STARTUP_TYPE`, `READINESS_TYPE`, `RGW_RATE_LIMITING_RESPONSE=503`, and `RGW_MISCONFIGURATION_RESPONSE=500`; helper function `check`.

Control flow: builds `RGW_URL` against `0.0.0.0`, uses `curl --insecure --silent --output /dev/stderr --write-out '%{response_code}'`, exits with curl's error code if curl cannot reach RGW, treats HTTP 200-399 as success, treats 503 as success to avoid cascading readiness removal during S3 slow-down throttling, treats HTTP 500 as startup failure but readiness success with a warning, and treats all other HTTP statuses as probe failure with code 124.

State and persistence: stateless; writes diagnostics to stderr/stdout and returns exit codes for Kubernetes probes.

Dependencies and integration points: depends on bash, curl, Kubernetes probe execution, and Rook templating that fills the probe type, port, protocol, and path. It is consumed by RGW deployment generation.

Risks: `0.0.0.0` assumes local pod listener behavior; 500 readiness success trades availability for potentially serving broken endpoints; the 503 path has `2>/dev/stderr`, which is unusual redirection syntax and likely intended to write to stderr; `PROBE_TYPE` validation only happens in the 500 branch.

Test signals: no direct test file in this subset. Behavior should be validated through rendered deployment/probe tests or shell-level tests if changed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw-probe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/rgw.go

Purpose: manages RGW Kubernetes deployment lifecycle and supporting CephX/config artifacts for a `CephObjectStore`, plus DNS/TLS helper functions for object-store access.

Important APIs/types: `clusterConfig`, `rgwConfig`, `createOrUpdateStore`, `startRGWPods`, `deleteStore`, `deleteRgwCephObjects`, `instanceName`, `storeLabelSelector`, `validateStore`, `generateSecretName`, `EmptyPool`, `GetStableDomainName`, `getAllDomainNames`, `getAllDNSEndpoints`, `ParseDomainName`, `BuildDNSEndpoint`, `GetTlsCaCert`, and `genObjectStoreHTTPClient`.

Control flow: `createOrUpdateStore` starts RGW pods, creates a multisite context, and enables/disables dashboard integration according to cluster and store settings. `startRGWPods` normalizes gateway instances, checks skip-reconcile labels, generates one RGW deployment/keyring/config set, applies mon config flags, creates or updates the deployment with owner refs and keyring resource-version annotations, generates mime types, and cleans up extra deployments/secrets/Ceph objects if scaling down. `deleteStore` removes RGW CephX/config artifacts, disables dashboard, and calls realm/pool deletion if a multisite context can be built. TLS helpers load certs from referenced Secrets or service-serving CA files.

State and persistence: persists Kubernetes Deployments and Secrets, CephX auth users, centralized mon config, mime type config, dashboard RGW settings, and object-store realm/pool cleanup through objectstore helpers. Reads TLS cert data from Kubernetes Secrets or filesystem.

Dependencies and integration points: integrates deployment generation methods in the same package, Ceph mon deployment update helper, keyring annotations, Rook config and owner refs, Kubernetes apps/core clients, object context creation, dashboard helpers in `objectstore.go`, and S3/Admin Ops HTTP client setup.

Risks: current code forces a single deployment (`desiredRgwInstances := 1`) while gateway instances are used as replica count elsewhere, so scale semantics are subtle. Deletion is best-effort and logs many failures. TLS behavior depends on Secret type/key conventions and optional `insecureSkipVerify`. `createOrUpdateStore` logs and returns nil if `NewMultisiteContext` fails after pods start, which can hide dashboard setup failure.

Test signals: `rgw_test.go` covers deployment creation, basic create/update with and without Keystone/S3 settings, keyring secret naming, empty pool detection, DNS endpoint construction, and TLS CA Secret behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/rgw_test.go

Purpose: unit tests for RGW deployment creation and helper functions in `rgw.go`.

Important APIs/tests: `TestStartRGW`, `validateStart`, `TestCreateObjectStore`, `simpleStore`, `TestCreateObjectStoreWithKeystoneAndS3`, `simpleStoreWithKeystoneAndS3`, `TestGenerateSecretName`, `TestEmptyPoolSpec`, `TestBuildDomainNameAndEndpoint`, and `TestGetTlsCaCert`.

Control flow: tests create fake Kubernetes clients and mocked Ceph executors, invoke `startRGWPods` or `createOrUpdateStore`, and assert deployment presence or absence of undesired command flags. TLS tests table through no cert ref, missing Secret, unknown Secret type, Opaque missing key, Opaque with `cert`, and later TLS Secret cases in the same file.

State and persistence: uses fake apps/core clients for Deployments and Secrets, temp config dirs, mocked Ceph command output, and in-memory stores.

Dependencies and integration points: covers integration with Rook deployment generation, keyring generation, Ceph config setting, Kubernetes Secret type handling, DNS endpoint helpers, and object-store specs with Keystone/S3 auth options.

Risks: tests do not deeply inspect generated pod templates, probe scripts, service resources, replica semantics, or deletion paths. They rely on mocked command responses and do not validate live Ceph behavior.

Test signals: good signal for basic deployment creation, helper formatting, and TLS error messages. Changes to cert key names, endpoint URL formatting, or keyring secret naming should fail here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/rgw_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers.go

Purpose: wraps AWS SDK v2 S3 client creation and common bucket/object operations for Ceph RGW.

Important APIs/types: `rookLogger`, `CephRegion`, `S3Agent`, `NewS3Agent`, `CreateBucket`, `createBucket`, `PutObjectInBucket`, `GetObjectInBucket`, `DeleteObjectInBucket`, and `BuildTransportTLS`.

Control flow: `NewS3Agent` configures static credentials, region `us-east-1`, retry settings, optional signing debug logging, path-style addressing, endpoint parsing with inferred `http`/`https` scheme based on TLS inputs, and an HTTP client with optional TLS transport. Bucket create treats already-exists/already-owned errors as success. Object put/get/delete call AWS SDK methods with `context.TODO`; delete treats missing bucket/key as success. TLS transport builds a system cert pool, appends provided PEM bytes if present, and honors insecure skip verify.

State and persistence: S3 operations persist buckets and objects in RGW. The agent itself stores only the SDK client.

Dependencies and integration points: used by notification provisioning, bucket policy helpers, bucket provisioning logic, and object-store HTTP client generation. Depends on AWS SDK v2, static credential provider, Go TLS/x509, and Rook's package logger.

Risks: uses `context.TODO` for all operations; `GetObjectInBucket` does not close `result.Body`; invalid PEM append result is ignored; custom `http.Client` bypasses TLS transport setup even when TLS args are provided; endpoint parsing treats parse errors or missing schemes by prepending inferred scheme. Returning `"ERROR_ OBJECT NOT FOUND"` with an error is a legacy oddity.

Test signals: `s3-handlers_test.go` covers endpoint scheme inference, debug log mode, insecure/secure TLS transport configuration, custom HTTP client preservation, and host:port/full URL handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers_test.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers_test.go

Purpose: tests S3 client construction behavior in `NewS3Agent`.

Important APIs/tests: `TestNewS3Agent` with subtests for no TLS/debug, debug logging, insecure TLS without cert, secure TLS with cert, insecure TLS with cert, custom HTTP client, host:port endpoint with TLS, host:port endpoint without TLS, and full URL endpoint.

Control flow: each subtest constructs an agent with different flags and asserts the SDK client's `BaseEndpoint`, `ClientLogMode`, and HTTP transport/TLS settings. The custom client case verifies transport tuning survives construction.

State and persistence: no external state; no real S3 calls are made.

Dependencies and integration points: depends on AWS config values exposed through SDK client options, Go `http.Transport`, and `testify/assert`.

Risks: tests use arbitrary `tlsCert` bytes, so they verify transport wiring but not PEM parsing success. They do not cover bucket/object method behavior, retries, credentials, or path-style setting.

Test signals: strong signal for endpoint normalization and TLS mode selection, which are critical for RGW internal clients and notification provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/shared_pools.go -->
## sources/control-plane/rook/pkg/operator/ceph/object/shared_pools.go

Purpose: transforms `ObjectSharedPoolsSpec` and placement specs into Ceph RGW zone and zonegroup JSON updates that allow object stores to share data/metadata pools with namespaced RADOS layouts.

Important APIs/types: `IsNeedToCreateObjectStorePools`, `validatePoolPlacements`, `validatePoolPlacementStorageClasses`, `adjustZonePlacementPools`, `getDefaultPlacementName`, `getDefaultMetadataPool`, `toZonePlacementPools`, `toZonePlacementPool`, `adjustZoneGroupPlacementTargets`, `createPlacementTargetsFromZonePoolPlacements`, `getZoneJSON`, `getZoneGroupJSON`, `updateZoneJSON`, `updateZoneGroupJSON`, and structs `ZonegroupPlacementTarget`, `ZonePlacementPool`, `ZonePlacementPoolVal`, `ZonePlacementStorageClass`.

Control flow: validation enforces one default placement, unique placement names, reserved `default-placement` semantics, and unique non-reserved storage class names. Zone placement adjustment deep-copies zone JSON, converts desired spec placements to RGW JSON, updates existing placements, preserves or mirrors `default-placement` for Ceph workarounds, removes placements not in spec, adds missing placements, sorts them for stable comparison with `radosgw-admin`, and writes them back. Zonegroup adjustment sets the default placement, derives placement targets/storage classes from zone placements, updates/removes/adds targets, and writes back. Get/update helpers call `radosgw-admin zone/zonegroup get/set`, writing JSON to temporary files under `ConfigDir`.

State and persistence: reads and writes Ceph zone and zonegroup JSON; temporary config files are created with mode 0600 and removed after command execution. It does not directly create pools; it assumes `objectstore.go` has verified referenced pools exist.

Dependencies and integration points: called by `ConfigureSharedPoolsForZone` in `objectstore.go`; depends on JSON helper functions such as `getObjProperty`, `updateObjProperty`, `deepCopyJson`, `toObj`, and `castJson` elsewhere in the package; integrates with Ceph `radosgw-admin` command semantics and known tracker workarounds for `inline_data` and default placement handling.

Risks: this code is sensitive to Ceph JSON schema changes and type assertions from generic `map[string]interface{}`. It deliberately preserves `default-placement` for a Ceph issue, which can surprise users expecting removal. Storage class data pool namespace for extra classes is based on storage class name rather than placement name. Update helpers require non-empty realm/zone/zonegroup context and writable config dir.

Test signals: shared-pool behavior is covered indirectly in `objectstore_test.go` for no-op, default shared pools, new default placement, already-set pools, extra placement, validation errors, and missing referenced pools. Direct tests for malformed zone JSON and helper type failures are limited.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/shared_pools.go -->
