# subset-b-000461 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/shared_pools_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/shared_pools_test.go

Purpose: this Go test file is the behavioral specification for object-store shared pool placement logic. It tests validation of `ObjectSharedPoolsSpec.PoolPlacements`, conversion of CRD placement specs into RGW zone placement-pool JSON, default-placement selection, zonegroup placement target reconciliation, and preservation/removal behavior when shared pools or custom placements change.

Important APIs and functions under test: `validatePoolPlacements`, `validatePoolPlacementStorageClasses`, `IsNeedToCreateObjectStorePools`, `getDefaultMetadataPool`, `toZonePlacementPool`, `toZonePlacementPools`, `adjustZoneDefaultPools`, `adjustZonePlacementPools`, `adjustZoneGroupPlacementTargets`, `createPlacementTargetsFromZonePoolPlacements`, and `getDefaultPlacementName`. The tested implementation is split mainly between `shared_pools.go` and `objectstore.go`, so this test file is an integration-style guard for code outside its own file.

Control flow and state behavior: the tests build table-driven `cephv1.ObjectSharedPoolsSpec` and JSON maps, call the transformation function, then compare the returned copy to expected JSON while asserting the input map was not mutated. `adjustZoneDefaultPools` test cases also use a mock Ceph executor so empty-pool checks can run without a real cluster. This matters because the production path can decide whether old RGW metadata pool names can be changed or deleted based on live Ceph pool contents.

Dependencies and integration points: the tests depend on `cephv1` object-store pool placement types, `clusterd.Context`, Ceph client test helpers, Rook exec mocks, `encoding/json`, `reflect`, and `testify/assert`. They model Ceph RGW zone and zonegroup config as generic JSON maps matching `radosgw-admin zone get` and zonegroup config structures, including `placement_pools`, `storage_classes`, `default_placement`, and metadata pools such as `domain_root`, `topics_pool`, and `account_pool`.

Risks documented by the tests: duplicate placement names, multiple defaults, reserved `default-placement` misuse, duplicate or reserved storage classes, partial shared-pool specs, legacy shared-pool compatibility, default placement overriding shared pools, Ceph v19 extra metadata pools, preserving `index_type` and `inline_data`, deleting obsolete placements, and sorted/deterministic storage-class target output. A notable residual risk is that most tests use hand-built JSON maps and fake empty-pool responses; real `radosgw-admin` output drift or non-empty-pool migration failures need broader integration coverage.

Test signals: coverage is broad and table-driven. It checks both positive and negative validation paths, JSON equality after transformations, non-mutation of source objects, and behavior with default and non-default placements. It does not execute the full object-store reconcile loop, so it validates transformation helpers more than Kubernetes/Ceph side effects.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/shared_pools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/spec.go

Purpose: this file builds the Kubernetes runtime spec for Ceph RGW object-store gateways. It creates Deployments, Pod templates, Services, EndpointSlices, probes, TLS/CA-bundle mounts, Vault-backed server-side encryption arguments, RGW command flags, DNS hosting arguments, and labels for `CephObjectStore` reconciliation.

Important APIs, types, and functions: key constants include service account/container names, SSE modes (`ssekms`, `sses3`), Vault paths, read-affinity values, and probe protocol/type constants. `rgwProbeConfig` feeds the embedded `rgw-probe.sh` template. Main methods include `createDeployment`, `makeRGWPodSpec`, `makeDaemonContainer`, `defaultReadinessProbe`, `defaultStartupProbe`, `endpointInfo`, `generateService`, `generateEndpoint`, `reconcileExternalEndpoint`, `reconcileService`, `CheckRGWKMS`, `CheckRGWSSES3Enabled`, `generateVolumeSourceWithTLSSecret`, `generateVolumeSourceWithCaBundleSecret`, `rgwTLSSecretType`, SSE option builders, `buildRGWConfigFlags`, `buildRGWEnableAPIsConfigVal`, `renderProbe`, `addDNSNamesToRGWServer`, and exported `GetHostnameFromEndpoint`.

Control flow: `createDeployment` calls `makeRGWPodSpec`, applies deployment labels, annotations, rolling-update strategy, replicas, and Ceph version labels. `makeRGWPodSpec` constructs init containers, the RGW daemon container, daemon volumes, optional ops-log/log-collector sidecars, host networking, TLS/cert volumes, CA bundle handling based on Ceph version, Vault token volumes/init containers, placement, anti-affinity, Multus annotations, and user-provided additional volume mounts. `makeDaemonContainer` builds the `radosgw` command line, default startup/readiness probes, TLS/CA mounts, Vault SSE flags, ops-log cleanup behavior, RGW config flags, DNS hosting flags, read-affinity flags, and finally user `RgwCommandFlags` so users can override earlier settings.

State and persistence behavior: this file does not persist CR status directly, but it writes desired Kubernetes state through generated Deployment/Service/EndpointSlice objects and may update old RGW ops-log settings in the Ceph monitor config store when the sidecar is absent. It reads Kubernetes Secrets for TLS and CA bundle type validation, reads CephObjectZone custom endpoints when DNS hosting uses a zone, and relies on `clusterConfig` state from the object-store reconciler.

Dependencies and integration points: it integrates with Rook Ceph config helpers (`cephconfig`), controller helpers for daemon flags/volumes/security contexts, Kubernetes core/apps/discovery APIs, KMS/Vault validation helpers, Ceph version gates, Multus networking, service-serving cert conventions, and `cephv1` object-store CRD methods such as `IsHostNetwork`, `IsTLSEnabled`, `GetServiceDomainName`, and advertise endpoint handling.

Risks: command-line argument ordering is important because user RGW flags intentionally override Rook-generated flags. Vault SSE paths are sensitive to token-vs-agent auth, secret-engine validation, and TLS secret keys. CA bundle behavior diverges before/after Ceph Tentacle. `addDNSNamesToRGWServer` performs strict DNS-1123 hostname validation and can reject uppercase/camel-case endpoints. Map iteration over user RGW flags is intentionally unordered among the added flags. Probe disabling depends on enabled API combinations; an API-only RGW without S3/Swift has no startup/readiness probe.

Test signals: `spec_test.go` covers pod specs, SSL cert mounts, store validation, probes, KMS/SSE-S3 validation and command flags, host networking, user RGW flags, DNS names, endpoint parsing, enabled API values, probe path selection, read affinity, and service labels. The implementation still relies on broader reconcile tests for actual Deployment/Service application to Kubernetes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/spec_test.go

Purpose: this large Go test suite validates `spec.go` behavior for RGW Kubernetes spec generation and related configuration helpers. It acts as a regression harness for pod shape, TLS/CA bundle handling, validation, probes, Vault-backed server-side encryption, RGW flags, DNS hosting, API enablement, read affinity, and generated Service labels.

Important fixtures and helpers: `configureSSEWithVaultAgent` and `configureSSE` populate `clusterConfig.store.Spec.Security` and create fake Vault token secrets. Most tests construct a `clusterConfig` with fake Kubernetes/Rook clients, Ceph cluster info, a stateless daemon data path map, and mock executors for Ceph commands.

Control flow under test: `TestPodSpecs` exercises `makeRGWPodSpec` and the pod-template tester suite, including anti-affinity and probe customization. `TestSSLPodSpec` checks TLS secret volume behavior. `TestValidateSpec` drives `ReconcileCephObjectStore.validateStore`. `TestDefaultProbes`, `Test_getRGWProbePathAndCode`, and `Test_buildRGWEnableAPIsConfigVal` cover probe rendering inputs and API-selection logic. `TestAWSServerSideEncryption`, `TestCheckRGWKMS`, and `TestCheckRGWSSES3Enabled` cover Vault KMS/SSE-S3 validation and generated RGW args. `TestRgwCommandFlags`, `TestAddDNSNamesToRGWPodSpec`, `TestGetHostnameFromEndpoint`, `TestRgwReadAffinity`, and `TestGenerateServiceLabels` cover user override flags, hosting endpoints, read-affinity version gates, and custom service labels.

State and persistence behavior: all state is fake/in-memory. The tests create Kubernetes Secrets and CephObjectZones in fake clients, exercise `makeDaemonContainer` and `makeRGWPodSpec`, and inspect generated container args, env, volume mounts, probes, service labels, and error results. They avoid real Kubernetes writes except fake-client object creation.

Dependencies and integration points: the tests use `cephv1` CRD structs, Rook fake clientsets, `clusterd.Context`, Ceph client and version test helpers, operator test utilities, fake exec, Kubernetes API types, `testify/assert`, and `reflect`/`slices` for comparison. They implicitly validate integration contracts with Vault constants, Ceph version gates, controller daemon helpers, and service DNS naming.

Risks and gaps: coverage is strong for deterministic helper output but weaker for live reconciliation side effects. Several tests reuse mutable `clusterConfig` state across subtests, so isolation depends on explicit reconfiguration. User RGW flags come from maps, so only element matching is appropriate. Endpoint parsing tests intentionally reject uppercase/camel-case DNS names under DNS-1123 rules; changes to Kubernetes validation semantics would affect expected results.

Test signals: this is a high-signal file for `spec.go`; failures usually indicate changed RGW pod contract, Ceph version behavior, Vault validation, command-line generation, or hosting endpoint validation. It also records important compatibility expectations, such as no liveness probe, host-network port selection, user flags appended last, and SSE-S3 agent auth rejecting `tokenSecretName`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/status.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/status.go

Purpose: this file manages `CephObjectStore` status updates and endpoint status-info construction. It turns reconcile outcomes into CR status phase, endpoint lists, selector strings, observed generation, replica counts, optional CephX daemon status, and user-facing endpoint info.

Important APIs and functions: `replicaCountNotAvailable` is a sentinel used to avoid overwriting replica count. `setFailedStatus` updates the object store to `ConditionFailure` and returns the original reconcile error wrapped with context. `updateStatus` performs the status write. `buildStatusInfo` builds the legacy/status `Info` map, primarily `endpoint` and sometimes `secureEndpoint`.

Control flow: `updateStatus` uses `retry.RetryOnConflict` to refetch the `CephObjectStore`, initialize status if absent, skip status mutation if the current phase is `Deleting`, set phase/info/replicas/selector/observed generation, recompute insecure and secure DNS endpoints from gateway ports, copy supplied CephX daemon status, and call `reporting.UpdateStatus`. Not-found resources are ignored because deletion is assumed. `buildStatusInfo` asks the CR for its advertise endpoint URL; an explicitly configured advertise endpoint takes precedence over service DNS endpoints and is the only endpoint reported.

State and persistence behavior: this code persists only the CR status subresource through the controller-runtime client and Rook reporting helper. It derives status endpoints from the current spec at update time, so gateway port changes are reflected whenever status is refreshed. It intentionally avoids changing status after a delete phase begins.

Dependencies and integration points: it integrates with `cephv1.ObjectStoreStatus`, Rook status reporting, controller labels via `getLabels`, endpoint builders such as `getAllDNSEndpoints`, `BuildDNSEndpoint`, and `GetStableDomainName`, Kubernetes conflict retry helpers, and `k8sutil.ObservedGenerationNotAvailable`.

Risks: status updates are best-effort but return errors after retries. If status is nil, endpoint slices are initialized empty; if ports are zero, endpoint slices are cleared. `buildStatusInfo` logs and continues if advertise endpoint URL construction fails, which can hide a validation gap but avoids breaking reconcile late. The delete-phase guard can leave stale status fields by design.

Test signals: `status_test.go` covers `buildStatusInfo` for HTTP, HTTPS, dual-port, and advertiseEndpoint cases. `updateStatus` and `setFailedStatus` do not have direct tests in this subset, so conflict handling, delete-phase preservation, CephX status copying, and endpoint slice recomputation rely on broader controller coverage or are residual risk.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/status_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/status_test.go

Purpose: this file tests `buildStatusInfo` for `CephObjectStore` endpoint reporting. It verifies how the status `Info` map chooses HTTP, HTTPS, dual-port, and explicitly advertised endpoints.

Important APIs and test cases: `TestBuildStatusInfo` builds a base `CephObjectStore` and mutates gateway ports and hosting advertise endpoint settings. It checks `endpoint` and `secureEndpoint` keys for regular service DNS output and for advertiseEndpoint override behavior.

Control flow and state behavior: each scenario deep-copies a base CR, sets `Spec.Gateway.Port`, `Spec.Gateway.SecurePort`, `SSLCertificateRef`, or `Spec.Hosting.AdvertiseEndpoint`, then calls `buildStatusInfo` and asserts exact URLs. There are no Kubernetes clients, no persisted status updates, and no reconcile loop.

Dependencies and integration points: the test uses `cephv1.CephObjectStore`, `cephv1.ObjectStoreHostingSpec`, `cephv1.ObjectEndpointSpec`, Kubernetes metadata, and `testify/assert`. Expected URLs encode the stable service DNS naming convention `rook-ceph-rgw-<store>.<namespace>.svc`.

Risks and gaps: this test does not cover `updateStatus`, not-found behavior, retry conflicts, delete-phase behavior, selector generation, endpoint slice arrays, replica counts, or CephX daemon status. It specifically guards the legacy info-map URL behavior, including the rule that an explicit advertise endpoint suppresses `secureEndpoint` even when both gateway ports are enabled.

Test signals: the file provides focused, stable regression signals for user-visible endpoint fields. Failures usually indicate a change in service DNS naming, advertiseEndpoint precedence, or HTTPS preference rules.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/topic/controller.go

Purpose: this file implements the controller-runtime reconciler for `CephBucketTopic`, which provisions and deletes RGW/SNS notification topics for object bucket notifications.

Important APIs, types, and functions: `ReconcileBucketTopic` stores the controller client, cluster context/info/spec, and operator manager context. `Add` and `add` register the controller, CR watch, Kafka Secret field index, and reverse Secret watch. `Reconcile` wraps `reconcile` with panic recovery and failure status updates. `reconcile` is the main lifecycle method. `createCephBucketTopic`, `deleteCephBucketTopic`, and `updateStatus` bridge to the provisioner and CR status.

Control flow: controller setup watches `CephBucketTopic` objects and indexes `spec.endpoint.kafka.secretNames` from `UserSecretRef` and `PasswordSecretRef`, compacting duplicate secret names. Secret changes or deletions enqueue all topics in the same namespace that reference the secret. Reconcile fetches the topic, adds a finalizer, waits for a ready `CephCluster` in `Spec.ObjectStoreNamespace`, loads cluster info, handles deletion by deleting the remote topic and removing the finalizer, validates the topic spec, marks status reconciling, calls the provisioner to create the topic, then records Ready with observed generation, ARN, and referenced secret status.

State and persistence behavior: Kubernetes state includes the `CephBucketTopic` finalizer and status fields `ARN`, `Phase`, `ObservedGeneration`, and referenced Secrets. Remote state is the RGW/SNS topic created/deleted by `provisioner.go`. Status update reads the latest CR, sorts referenced secrets by name for deterministic status, and writes through `reporting.UpdateStatus`. If reconcile returns an error, `Reconcile` sets failure status with unknown observed generation.

Dependencies and integration points: the controller integrates with controller-runtime manager/controller/source/handler/predicate APIs, Rook operator readiness helpers, Ceph cluster info loading, `cephv1.CephBucketTopic` validation, Kubernetes Secrets, Rook reporting, and the package-level `createTopicFunc`/`deleteTopicFunc` hooks used by tests.

Risks: the Secret field index only tracks secret names, not keys; namespace scoping is enforced in the list. Type asserting `r.(*ReconcileBucketTopic)` in the Secret watch assumes the registered reconciler is this concrete type. Status failures are logged and swallowed in `updateStatus`, so reconcile can complete even if status write fails. Deletion skips remote delete if the provisioner sees no ARN. Deleting a CR while its CephCluster is gone removes the finalizer without remote cleanup.

Test signals: `controller_test.go` covers no-cluster requeue, cluster-not-ready requeue, and successful create with a mocked provisioner/ARN. It does not cover Secret watch behavior, deletion/finalizer paths, invalid spec handling, failed provisioner status, referenced secret status sorting, or real SNS client creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/topic/controller_test.go

Purpose: this test file validates the basic `CephBucketTopic` reconcile flow for cluster readiness and successful topic creation. It uses fake clients and a mocked topic provisioner to avoid real RGW/SNS calls.

Important fixtures and functions: package-level variables define topic name, namespace, object store name, and a mock RGW admin user JSON payload. `TestCephBucketTopicController` creates a base `CephBucketTopic`, cluster info/spec, and reconcile request, then runs subtests for no `CephCluster`, not-ready `CephCluster`, and successful topic creation.

Control flow under test: the first subtest builds only the topic and expects reconcile to return a requeue result because no CephCluster is present. The second adds a CephCluster with empty readiness and also expects requeue. The third creates a Ready CephCluster, fake mon secret, fake CephObjectStore, overrides package-level `createTopicFunc` to return an expected ARN, runs reconcile, and verifies the topic status contains that ARN.

State and persistence behavior: state lives in controller-runtime fake clients, a fake Rook clientset, and fake Kubernetes clientsets. The successful path writes `CephBucketTopic.Status.ARN` through the reconciler. The test resets `createTopicFunc` with a defer to avoid leaking the mock.

Dependencies and integration points: it depends on `cephv1` CRDs, fake Rook clientsets, `clusterd.Context`, Ceph admin cluster info, Rook operator test clients, fake executor, Kubernetes Secrets, controller-runtime fake client, and `testify/assert`.

Risks and gaps: the test does not exercise controller registration, Secret indexing/watch enqueue behavior, finalizer add/remove edge cases, deletion, invalid topic specs, `deleteTopicFunc`, failure status updates, status observed generation, or referenced Kafka secret status. It also uses package-level mutable variables and function hooks, so future parallelization would need care.

Test signals: useful smoke coverage for readiness gating and create-status integration. A failure in the create subtest likely indicates changed cluster-info loading prerequisites, object-store lookup expectations, provisioner call contract, or status update behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner.go

Purpose: this file implements the RGW/SNS provisioning layer used by the `CephBucketTopic` controller. It creates AWS SNS clients pointed at Ceph RGW, builds topic attributes for HTTP/AMQP/Kafka endpoints, creates/deletes topics, validates provisioned topic ARNs, and resolves Kubernetes Secret values for Kafka credentials.

Important APIs, types, and functions: `provisioner` carries Kubernetes client, Rook cluster context, cluster info/spec, and operator context. `snsEndpointResolver` implements AWS SDK v2 endpoint resolution for a Ceph RGW endpoint. `createSNSClient` builds an SNS client using RGW admin ops credentials. `createTopicAttributes` maps `CephBucketTopic.Spec` into SNS attributes and returns referenced Secrets. Package variables `createTopicFunc` and `deleteTopicFunc` allow tests to replace network calls. `createTopic`, `deleteTopic`, `GetProvisioned`, and `getSecretValue` are the main operational functions.

Control flow: `createSNSClient` fetches the target `CephObjectStore`, creates an object context, gets admin ops credentials, configures HTTP timeout and optional TLS transport from the object store CA cert, enables verbose AWS SDK logging at debug level, and returns an SNS client with static credentials and custom endpoint. `createTopicAttributes` always sets `OpaqueData` and `persistent`, then fills endpoint-specific attributes. Kafka credential Secret refs are read from the topic namespace and injected into the Kafka URI basic auth, replacing any existing URI credentials. `createTopic` creates the SNS client, attributes, then calls `CreateTopic`. `deleteTopic` skips deletion without status ARN, otherwise calls `DeleteTopic` and ignores SNS not-found errors. `GetProvisioned` fetches a topic and validates that status has a parseable SNS ARN with a non-empty resource.

State and persistence behavior: remote state is the Ceph RGW SNS topic. Kubernetes state is read from `CephObjectStore`, `CephBucketTopic`, and referenced Secrets; this file itself does not write CR status. Kafka referenced Secrets are returned to the controller so status can record name, namespace, UID, and resourceVersion for dependency tracking.

Dependencies and integration points: it integrates with AWS SDK v2 SNS/ARN/credentials/endpoint APIs, Ceph object helpers (`NewMultisiteContext`, `GetAdminOPSUserCredentials`, TLS helpers, timeout/region constants), Rook clients, controller namespace-name logging, and Kubernetes Secret selectors.

Risks: Kafka URI parsing can fail and may include passphrases, so errors/logs must avoid leaking credentials; the code logs only redacted Kafka URIs. Secret refs are resolved in the topic namespace, not object-store namespace. Referenced Secrets are keyed by UID, so two refs to the same Secret collapse into one status entry. `deleteTopic` depends on status ARN; topics created remotely but never recorded in status will be leaked on CR deletion. `createSNSClient` depends on admin ops credentials and TLS CA availability.

Test signals: `provisioner_test.go` covers HTTP, AMQP, and Kafka attribute construction without Secret refs. Controller tests mock `createTopicFunc`. Gaps include SNS client creation, TLS transport, Kafka credential Secret injection, referenced Secret map content, delete not-found handling, and `GetProvisioned` ARN validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner_test.go

Purpose: this test file validates `createTopicAttributes` for the three supported Ceph bucket topic endpoint families: HTTP, AMQP, and Kafka.

Important test cases: `TestTopicAttributesCreation` defines common string constants and runs subtests for HTTP, AMQP, and Kafka. Each subtest creates a `CephBucketTopic` with endpoint-specific spec fields, calls `createTopicAttributes(provisioner{}, topic)`, and asserts the exact SNS attribute map.

Control flow and state behavior: no Kubernetes client or Secrets are used in these tests. The function is called with an empty provisioner because the covered cases do not require `getSecretValue`. The output map is checked for baseline `OpaqueData` and `persistent` plus endpoint-specific fields such as `push-endpoint`, `verify-ssl`, `cloudevents`, `amqp-exchange`, `amqp-ack-level`, `kafka-ack-level`, `use-ssl`, and `mechanism`.

Dependencies and integration points: the tests use `cephv1.CephBucketTopic`, endpoint spec structs, Kubernetes metadata, `capnslog` log configuration, `testify/assert`, and `testify/require`.

Risks and gaps: this file does not test Kafka `UserSecretRef` or `PasswordSecretRef`, URI credential replacement, referenced Secret return values, invalid Kafka URIs, opaque data non-empty values, persistent true, disable-verify-SSL variants, SNS client creation, topic creation/deletion, or `GetProvisioned`. Because `createTopicAttributes` returns a Secret map pointer, status dependency tracking remains mostly untested here.

Test signals: failures indicate a changed RGW/SNS attribute contract for endpoint provisioning. The tests are intentionally small and deterministic, making them useful for detecting accidental key renames or boolean formatting changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/user.go

Purpose: this file wraps `radosgw-admin` user operations for object-store users, especially the RGW admin ops user and dashboard-related user lifecycle. It converts Ceph RGW admin JSON into Rook `ObjectUser` values and maps command failures into small integer error codes.

Important APIs, types, and functions: error constants include `RGWErrorNone`, `RGWErrorUnknown`, `RGWErrorNotFound`, `RGWErrorBadData`, `RGWErrorParse`, and `ErrorCodeFileExists`. `ObjectUser` mirrors RGW user fields needed by Rook, including ID, display/email, access/secret keys, system/admin flags, max buckets, quota, and caps. Functions are `decodeUser`, `GetUser`, `CreateUser`, `CreateOrRecreateUserIfExists`, `ListUserBuckets`, and `DeleteUser`.

Control flow: `decodeUser` unmarshals Ceph `admin.User`, copies display/email/caps/max buckets/quota, extracts the first access/secret key, and errors if no key exists. `GetUser` runs `user info --uid`, treats "no user info saved" as not found, extracts JSON from command output, and decodes it. `CreateUser` validates non-empty user ID and required display name, builds `user create` args with optional email/system/admin caps/access/secret/force flags, uses a longer timeout for the admin ops user, maps EEXIST or known duplicate-output strings to `ErrorCodeFileExists`, maps duplicate email to bad data, maps initialization config errors to unknown, and decodes successful output. `CreateOrRecreateUserIfExists` deletes and recreates on file-exists. `DeleteUser` treats ENOENT as success and checks bucket lists before returning an error for users that still own buckets.

State and persistence behavior: all persistent state is external RGW user state changed by `radosgw-admin`. This file does not write Kubernetes resources directly. It relies on the object `Context` executor and command helpers for Ceph cluster access. Delete safety is conservative: if deletion fails and bucket listing shows buckets, the returned error includes that information.

Dependencies and integration points: it depends on `github.com/ceph/go-ceph/rgw/admin` structs, Rook command execution helpers (`runAdminCommand`, `runAdminCommandWithTimeout`, `extractJSON`), syscall exit codes, Rook exec timeout utilities, and logger helpers. It is used by object-store provisioning paths that need admin ops credentials and by dashboard user setup.

Risks: parsing is coupled to `radosgw-admin` output text and JSON shape. Only the first key is returned. Duplicate-user detection uses both exit code and string matching because Ceph behavior can vary. `CreateOrRecreateUserIfExists` deletes an existing user before recreating, which can disrupt users if called with the wrong ID. `DeleteUser` bucket-list checks can mask or reframe errors depending on list command success. The file has no direct tests in this subset.

Test signals: no mapped `user.go` unit test is included here. Existing indirect coverage appears through topic/controller tests that mock `user create` JSON for admin ops setup, but detailed user error mapping, delete behavior, bucket checks, and JSON decoding edge cases need separate tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/user.go -->
