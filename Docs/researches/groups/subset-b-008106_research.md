<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerProtocolServerSideTranslatorPB.java

Purpose: Server-side protobuf translator for the OM RPC protocol. It accepts `OMRequest` messages from `OzoneManagerProtocolPB`, runs request/response feature validation, dispatches read and write paths, records protocol metrics, and converts leader/read-consistency decisions into normal responses or `ServiceException`s.

Important APIs/types/functions: The class implements `OzoneManagerProtocolPB` and owns an `OzoneProtocolMessageDispatcher`, `RequestValidations`, `OzoneManagerRatisServer`, `RequestHandler`, and `OMPerformanceMetrics`. `submitRequest` is the RPC entry point. `processRequest` adds OM lock timing into Hadoop IPC `ProcessingDetails`. `internalProcessRequest` handles S3 auth, read/write routing, retry-cache lookup, and OM execution submission. `submitReadRequestToOM` and its helper methods implement default, local-lease, leader-only linearizable, and allow-follower linearizable read policies. `allowFollowerReadLocalLease` checks follower role info, leader RPC lease age, and commit-index lag.

Control flow: Incoming requests are first validated by annotation-driven validators loaded from `org.apache.hadoop.ozone` with version and metadata context. The dispatcher then calls `processRequest`. Read-only requests bypass Ratis writes and choose either local handler execution or `omExecutionFlow.submit(request, false)` depending on hint, raft role, and linearizable-read configuration. Mutating requests verify S3 credentials when present, otherwise check leader status, consult the Ratis retry cache, remember `lastRequestToSubmit`, and submit to the OM execution flow as a write.

State and persistence behavior: This translator does not persist OM metadata directly. It manipulates per-thread S3 auth context with `OzoneManager.setS3Auth`, updates metrics counters for read paths, stores the last submitted request for tests, and relies on Ratis/OM execution to persist writes. It warns when serialized `OMResponse` size exceeds half of `ipc.maximum.response.length`.

Dependencies and integration points: Integrates Hadoop IPC, Ratis leader/read-index state, OM request validation aspects, S3 credential validation, retry-cache handling, OM metrics, and `OzoneManagerRequestHandler`. `PrepareStatus` is a special local read that is served regardless of leadership for compatibility.

Risks: Read consistency is configuration-sensitive; local-lease reads can intentionally allow stale data if log or time limits are loose. S3 auth path skips a second leader check after credential validation, so `S3SecurityUtil` leader-error propagation is part of correctness. Large responses are only logged, not rejected. Unknown raft statuses map to internal errors.

Test signals: Visible-for-testing methods expose `processRequest`, `logLargeResponseIfNeeded`, and `getLastRequestToSubmit`. Related tests should cover read-hint routing, follower local-lease metrics, leader-not-ready exceptions, S3-auth failures, retry-cache returns, response validation, and lock timing propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerRequestHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerRequestHandler.java

Purpose: Central OM request handler used by the translator and OM state machine to turn protobuf `OMRequest`s into protobuf read responses or `OMClientResponse`s for write transactions. It is the large dispatch bridge between protocol messages and `OzoneManager` service APIs.

Important APIs/types/functions: Implements `RequestHandler`. `handleReadRequest` switches on `Type` for volume, bucket, key, ACL, DB update, service list, file status, multipart, tenant, snapshot, safe mode, quota repair, tagging, compaction, leadership transfer, and diagnostic requests. `handleWriteRequestImpl` creates an `OMClientRequest` through `OzoneManagerRatisUtils.createClientRequest`, calls `validateAndUpdateCache`, and emits audit logs. Static `@RequestFeatureValidator` methods reject responses older clients cannot understand, especially EC replication and non-legacy bucket layouts. `limitListSize` bounds list operations by OM config.

Control flow: Read handling constructs a base `OMResponse.Builder`, dispatches the specific request to a private method, sets the matching response submessage, and marks success. `IOException`s are converted to protobuf statuses via `exceptionToResponseStatus`. Write handling optionally pauses through a test `FaultInjector`, constructs the typed write request, validates and updates the OM cache under execution context term/index, logs success or failure audit events, then returns the response for double-buffering by the interface default method.

State and persistence behavior: The handler mostly delegates persistence to `OzoneManager`, manager classes, and write request classes. Direct state is limited to `impl` and optional `FaultInjector`. It reads DB update batches, metadata records, multipart state, snapshot diff jobs, open keys, quota repair state, and service certificates. Write requests mutate OM caches and are later persisted through the double buffer/Ratis apply pipeline.

Dependencies and integration points: Tightly coupled to `OzoneManager`, `OMClientRequest`, OM metadata helpers, generated protobuf types, upgrade layout annotations, request validation aspects, snapshot APIs, Ratis leadership transfer, Ranger background sync, and audit logging. `aop.xml` weaves this class so `@DisallowedUntilLayoutVersion` and snapshot feature annotations take effect.

Risks: The switch is broad and easy to desynchronize from proto enum additions. After the switch, `setSuccess(true)` is unconditional for recognized commands unless an exception occurs, so private helpers must throw on semantic failure. Older-client validators must clear incompatible response bodies or clients may misinterpret EC/non-legacy data. `limitListSize` silently clamps requested counts. The TODO about read response ser/de highlights duplicated conversion surfaces.

Test signals: Coverage should verify every read command mapping, exception-to-status conversion, feature validators for EC and bucket layouts, multipart replication config encoding, snapshot layout gating, list-size clamping, audit logging on write failure, and double-buffer exclusion for `Prepare`. Existing adjacent tests exercise bucket writes, key table scans, gRPC startup, and lock metrics rather than this entire switch directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OzoneManagerRequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java

Purpose: Interface defining the OM request-handling contract shared by the server-side translator, non-HA execution, and HA Ratis state machine apply path.

Important APIs/types/functions: Declares `handleReadRequest(OMRequest)`, `validateRequest(OMRequest)`, and `handleWriteRequestImpl(OMRequest, ExecutionContext)`. The default `handleWriteRequest` wraps `handleWriteRequestImpl`, adds the returned `OMClientResponse` to `OzoneManagerDoubleBuffer` at the current term/index, and skips that add for `Type.Prepare`.

Control flow: Implementations provide direct read handling and write validation/cache mutation. Callers use the default method when they also need to enqueue the response for asynchronous metadata persistence. The prepare special case avoids double-buffering because prepare has distinct durability/coordination semantics.

State and persistence behavior: The interface owns no state. Its default method is a persistence integration point: it determines whether a write response is handed to the double buffer for later flush to OM DB.

Dependencies and integration points: Depends on protobuf request/response types, `ExecutionContext`, `OMClientResponse`, `OMException`, and `OzoneManagerDoubleBuffer`. `OzoneManagerRequestHandler` is the concrete implementation in this subset.

Risks: Any implementation that bypasses the default method must replicate double-buffer semantics. The `Prepare` exception is protocol-sensitive and should remain aligned with OM state-machine handling.

Test signals: Tests should check writes are enqueued with the exact Ratis term/index except prepare, and that `validateRequest` rejects malformed requests before they reach Ratis.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java

Purpose: Package documentation for OM protocol buffer translators.

Important APIs/types/functions: No executable APIs. The package contains the translator and handler classes that adapt protobuf OM protocol messages to `OzoneManager` operations.

Control flow: Not applicable.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the namespace used by the OM RPC protocol bridge. Aspect weaving in resources targets classes in this package.

Risks: Minimal. The package comment is terse and does not describe read/write/Ratis responsibilities.

Test signals: None directly; package-level behavior is covered by translator and request-handler tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java

Purpose: Package-private utility for AWS Signature Version 4 validation used by Ozone S3 authentication.

Important APIs/types/functions: `hash(String)` returns a SHA-256 hex digest. `validateRequest(String strToSign, String signature, String userKey)` derives the AWS V4 signing key and compares the expected HMAC hex string. `getSigningKey` parses date, region, and service from the credential-scope line of the string-to-sign. `sign` uses a per-thread cached `Mac` for `HmacSHA256`.

Control flow: Validation splits `strToSign`, derives `kDate`, `kRegion`, `kService`, and final `aws4_request` key using chained HMAC operations, signs the full string-to-sign, hex-encodes it, and compares it to the request signature.

State and persistence behavior: No persistence. State is a `ThreadLocal<Mac>` cache to reduce allocation while keeping `Mac` instances thread-confined.

Dependencies and integration points: Used by `OzoneDelegationTokenSecretManager.validateS3AuthInfo`; reachable from `S3SecurityUtil` through delegation-token password retrieval. Depends on Kerby `Hex`, Hadoop `StringUtils`, JCA `MessageDigest`, and `Mac`.

Risks: The string-to-sign parsing assumes AWS V4 layout and does no length validation before indexing. Signature comparison uses ordinary string equality rather than constant-time comparison. Debug logging of signing key material is guarded by debug level but still sensitive if enabled.

Test signals: Tests should include valid AWS V4 signatures, malformed string-to-sign values, wrong secret/region/service/date cases, concurrent validation to exercise the thread-local `Mac`, and hash formatting with leading zeros.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java

Purpose: OM-specific certificate client built on `DefaultCertificateClient`. It creates certificate signing requests for OM nodes and asks SCM security service for OM certificate chains.

Important APIs/types/functions: Constructor wires `SecurityConfig`, SCM security translator, `OMStorage`, OM details proto, service ID, SCM ID, certificate ID save callback, and shutdown callback into the base client. `configureCSRBuilder` fills CA=false, current key pair, security config, SCM ID, cluster ID, subject, and optional service name. `sign` calls `getOMCertChain(omInfo, encodedCSR)`. `getLogger` returns the class logger.

Control flow: CSR creation starts from the base builder. If DNS names are available, subject becomes current short user plus hostname; otherwise it uses only hostname to avoid IP-only alt-name validation issues. The request is then logged and later submitted to SCM for signing.

State and persistence behavior: Holds service ID, SCM ID, cluster ID, and OM details. Certificate/key persistence is inherited from `DefaultCertificateClient` and callbacks backed by OM storage.

Dependencies and integration points: Integrates OM identity from `OMStorage`, SCM security protocol, HDDS certificate utilities, `UserGroupInformation`, and service-name support for HA. It participates in secure OM startup and certificate renewal flows.

Risks: Subject construction depends on current OS/Kerberos user and DNS-name detection. Empty service ID omits service-name SAN data, which may matter in HA/service-address validation. SCM signing failures surface as IO/security exceptions during startup or renewal.

Test signals: Tests should verify CSR fields for DNS and IP-only cases, service-name inclusion, cluster/SCM IDs, key pair wiring, and that `sign` calls SCM with OM details and encoded CSR.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java

Purpose: OM delegation-token secret manager. It creates, verifies, renews, cancels, loads, and expires Ozone delegation tokens, while also validating S3 authentication pseudo-tokens through S3 secrets.

Important APIs/types/functions: Extends `OzoneSecretManager<OzoneTokenIdentifier>`. Builder configures token lifetimes, service, certificate client, secret-key client, S3 secret manager, OM service ID, and OM instance. `createToken` signs identifiers with SCM managed secret keys when the layout feature allows it, otherwise with OM certificate private key. `renewToken`, `cancelToken`, `retrievePassword`, `validateToken`, `verifySignature`, `validateS3AuthInfo`, `loadTokenSecretState`, `addPersistedDelegationToken`, `start`, `stop`, and `removeExpiredToken` form the main lifecycle.

Control flow: Construction loads persisted token renew dates from `OzoneSecretStore` into `currentTokens`. Token creation stamps issue/max dates, sequence number, master key ID, OM service ID, and signing metadata. `retrievePassword` first requires the OM to be leader/ready, then either validates S3 signature or checks token cache expiry and signature. Renewal enforces max date and exact renewer. Cancel enforces owner/renewer authorization but leaves actual removal to higher-level OM request flow. A daemon periodically removes expired tokens from memory and the OM DB.

State and persistence behavior: Maintains `currentTokens` as a `ConcurrentHashMap` of identifiers to renew date/password/tracking info. `OzoneSecretStore` persists renew dates in the delegation token table. Sequence number state is inherited from the base manager. Expiration cleanup mutates both cache and persisted table under `noInterruptsLock`.

Dependencies and integration points: Integrates OM leadership checks, OM layout features, SCM symmetric secret keys, OM X509 certificate client, S3 secret manager, `OzoneSecretStore`, Hadoop `Token`, and Kerberos-name short-name authorization. It is called by `S3SecurityUtil` and normal token-authentication paths.

Risks: Followers reject all token password retrieval to avoid stale token acceptance, which affects failover/read behavior. During upgrade, RSA-signed and symmetric-key-signed tokens coexist; missing secret keys can invalidate unexpired tokens and expired persisted tokens are opportunistically deleted. Signature verification logs sensitive identifiers. `cancelToken` only validates and returns the ID; callers must persist removal. The remover exits the JVM on unexpected exceptions.

Test signals: Strong tests should cover symmetric and RSA signing, persisted-token reload, missing secret key handling, expiration cleanup, renewal authorization, cancel authorization, leader-not-ready wrapping, S3 owner/access-id mismatch, invalid AWS signatures, and upgrade transition token compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java

Purpose: Persistence adapter for OM delegation-token secret state.

Important APIs/types/functions: `OzoneManagerSecretState<T>` wraps a map from token identifier to renew date. `loadState` creates a state object and populates it through `loadTokens`. `storeToken`, `updateToken`, and `removeToken` write to or delete from `OMMetadataManager.getDelegationTokenTable`. `loadTokens` iterates the full token table.

Control flow: Store/update put the identifier and renew date into the delegation token table. Removal deletes by identifier. Loading seeks the table iterator to first entry and copies each key/value into the in-memory state map, returning a count for logging.

State and persistence behavior: The class persists token renew dates in OM metadata DB. It keeps only an `OMMetadataManager` reference; loaded state is returned to the secret manager.

Dependencies and integration points: Used by `OzoneDelegationTokenSecretManager` at startup and during token mutation/expiration cleanup. Depends on the OM DB table abstraction and token identifier serialization/comparison.

Risks: The generic state type is raw in `loadState`, so compile-time type checking is weak. Full-table loading can be expensive with many tokens. IOException logging includes token details and then rethrows, preserving failure semantics.

Test signals: Tests should verify put/update/delete table calls, complete iterator loading, behavior on table IO failures, and that loaded state keys match serialized/deserialized token identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OzoneSecretStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java

Purpose: Utility for constructing and validating OM-side S3 authentication information embedded in `OMRequest`.

Important APIs/types/functions: `validateS3Credential(OMRequest, OzoneManager)` checks security enablement, constructs an `OzoneTokenIdentifier` of type `S3AUTHINFO`, and delegates signature verification to `ozoneManager.getDelegationTokenMgr().retrievePassword`. `constructS3Token` copies string-to-sign, signature, AWS access ID, and owner into the token identifier.

Control flow: If security is disabled, validation is a no-op. If enabled, invalid signatures become `OMException` with `INVALID_TOKEN`. Leader/not-ready errors wrapped as `SecretManager.InvalidToken` causes are rethrown as `ServiceException` to trigger normal client failover behavior.

State and persistence behavior: No persistence. It builds a transient token identifier and relies on delegation token/S3 secret managers for secret lookup and signature validation.

Dependencies and integration points: Called by `OzoneManagerProtocolServerSideTranslatorPB` before S3-authenticated requests proceed. Integrates generated S3 auth protobuf, OM leader status, `OzoneDelegationTokenSecretManager`, and AWS V4 validation indirectly.

Risks: Error logging includes the constructed S3 token on signature failures. Cause checks compare exact exception classes rather than `instanceof`. Missing or malformed S3 auth fields are not locally validated here and depend on deeper validation.

Test signals: Tests should exercise security-disabled no-op, valid signature pass-through, invalid signature status/message, leader-not-ready conversion to `ServiceException`, and token construction fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/S3SecurityUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java

Purpose: Factory for OM and snapshot access authorizers based on OM configuration.

Important APIs/types/functions: `forOM` creates an authorizer for the live OM managers. `forSnapshot` returns a fresh authorizer for snapshot managers when the active authorizer is native, otherwise reuses the configured non-native authorizer. `createImpl` chooses no-op, native, custom `OzoneManagerAuthorizer`, plain custom `IAccessAuthorizer`, or `SharedTmpDirAuthorizer`. `authorizerClass` reads `OZONE_ACL_AUTHORIZER_CLASS`.

Control flow: If ACLs are disabled or the configured class is `OzoneAccessAuthorizer`, it returns the singleton no-op authorizer. Native authorizer is configured with OM managers. Custom OM-aware authorizers receive `configure`. For other custom authorizers, the factory optionally wraps them with native handling for OFS shared tmp when that feature is enabled.

State and persistence behavior: No persistence. It creates or reuses authorizer instances and logs the selected class.

Dependencies and integration points: Integrates `OzoneManager`, `OmSnapshot`, key/prefix managers, ACL config, reflection-based instantiation, and shared tmp directory policy.

Risks: Reflection errors surface during OM startup/configuration. Reusing non-native authorizers for snapshots assumes they can handle snapshot contexts. Shared tmp wrapping changes behavior only for non-native authorizers, so native/custom parity depends on config.

Test signals: Tests should cover ACL-disabled no-op, native configuration, custom `OzoneManagerAuthorizer` configuration, plain custom wrapping when shared tmp is enabled, and snapshot authorizer reuse versus recreation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java

Purpose: OM-specific extension of `IAccessAuthorizer` for authorizers that need OM manager dependencies.

Important APIs/types/functions: Declares `configure(OzoneManager om, KeyManager km, PrefixManager pm)` returning an `OzoneManagerAuthorizer`.

Control flow: The factory detects implementations of this interface and calls `configure` after reflective construction. Native authorizer implements this path.

State and persistence behavior: No state in the interface. Implementations may retain manager references to read ACL metadata.

Dependencies and integration points: Depends on `OzoneManager`, `KeyManager`, and `PrefixManager`. Used by `OzoneAuthorizerFactory`.

Risks: Implementations must be safe to configure once and then use concurrently. Returning the wrong instance or failing to retain dependencies will break access checks at runtime.

Test signals: Factory tests should verify `configure` is invoked and its returned instance is used.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java

Purpose: Native OM ACL authorizer that evaluates Ozone volume, bucket, key, and prefix ACLs using OM manager metadata and admin/blacklist predicates.

Important APIs/types/functions: Implements `OzoneManagerAuthorizer`. `checkAccess(IOzoneObj, RequestContext)` is the core evaluator. `configure` wires volume, bucket, key, prefix managers and OM predicate methods. Setters allow tests to replace admin and blacklist checks. `isNative` returns true.

Control flow: `checkAccess` requires `OzoneObjInfo` and `RequestContext`, denies fully blacklisted users and read-blacklisted users for read/list ACLs, allows admins, allows read-only admins for read/list ACLs, allows owner access, handles list-all-volumes via config, computes parent ACL rights, then checks managers based on resource type. Volume creation is denied unless admin. Bucket/key/prefix creation skips checking the object being created but still checks parent access.

State and persistence behavior: The authorizer itself persists nothing. It reads ACL state through manager `checkAccess` calls and uses OM config for list-all-volumes permission.

Dependencies and integration points: Integrates with `VolumeManager`, `BucketManager`, `KeyManager`, `PrefixManager`, `OzoneAclUtils.getParentNativeAcl`, `OzoneAdmins`, `OzoneBlacklist`, and OM user predicates.

Risks: Owner bypass uses short username equality with `ownerName`; mismatches in Kerberos principal normalization can change access. CREATE semantics deliberately skip child object checks, so parent checks are critical. Non-`OzoneObjInfo` objects fail with `INVALID_REQUEST`. `allowListAllVolumes` can expose volume listing broadly if configured.

Test signals: Tests should cover blacklist precedence over admin-like rights, read-only admin scope, owner bypass, list-root behavior, create versus non-create access for each resource type, parent ACL requirements, and invalid object types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java

Purpose: Hybrid authorizer that forces OFS shared temporary bucket access checks through native ACLs while delegating all other objects to a configured custom authorizer.

Important APIs/types/functions: Constructor accepts an `OzoneNativeAuthorizer` and a delegate `IAccessAuthorizer`. `checkAccess` checks nulls, detects `OzoneObjInfo`, calls `OFSPath.isSharedTmpBucket`, and chooses native or delegate authorizer.

Control flow: For shared tmp bucket objects, access is evaluated by the native authorizer. For non-shared-tmp objects or non-`OzoneObjInfo` implementations, the configured authorizer handles the request.

State and persistence behavior: No persistence. Holds two authorizer references.

Dependencies and integration points: Created by `OzoneAuthorizerFactory` when a non-native authorizer is configured and shared tmp support is enabled. Depends on `OFSPath` shared tmp detection.

Risks: Shared tmp detection only runs for `OzoneObjInfo`; custom `IOzoneObj` implementations bypass the native special case. The wrapper assumes the native authorizer has been configured with the same OM managers.

Test signals: Tests should verify native delegation for shared tmp, custom delegation for ordinary buckets/keys, null argument failures, and behavior for non-`OzoneObjInfo` objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java

Purpose: Package documentation for OM native ACL implementation classes.

Important APIs/types/functions: No executable APIs. The package contains authorizer factory, native authorizer, OM authorizer extension, and shared tmp wrapper.

Control flow: Not applicable.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the namespace for OM ACL authorization implementations used by OM and snapshots.

Risks: Minimal; package description is broad and does not capture custom authorizer or shared tmp behavior.

Test signals: None directly; behavior is covered through authorizer classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/package-info.java

Purpose: Package documentation for OM security-related classes.

Important APIs/types/functions: No executable APIs. The package contains S3 auth utilities, delegation token secret management, certificate client, and secret-store persistence.

Control flow: Not applicable.

State and persistence behavior: No state or persistence in this file.

Dependencies and integration points: Documents the security namespace used by OM startup, token authentication, S3 gateway authentication, and certificate management.

Risks: Minimal; the package comment is too short to guide maintainers through token/certificate/S3 boundaries.

Test signals: None directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml

Purpose: AspectJ weaving descriptor for OM layout-feature and snapshot-feature enforcement.

Important APIs/types/functions: Registers `OMLayoutFeatureAspect` and `RequireSnapshotFeatureStateAspect`. The weaver includes `org.apache.hadoop.ozone.protocolPB.OzoneManagerRequestHandler` and `OzoneManagerProtocolServerSideTranslatorPB`.

Control flow: At build/runtime weaving time, AspectJ applies advice around annotated methods in the included classes, such as methods marked with `@DisallowedUntilLayoutVersion` or snapshot feature-state annotations.

State and persistence behavior: No runtime state or persistence itself. It affects whether feature-gated methods execute based on OM layout/snapshot state.

Dependencies and integration points: Couples the protocol handler package to upgrade layout and snapshot feature enforcement. Comments note the include list is manually maintained and should include classes with feature annotations.

Risks: If a new annotated class or method is not matched by the include patterns, feature gates may silently not apply. Verbose weave output can affect logs. The manual include list must track refactors.

Test signals: Upgrade/snapshot tests should fail if gated APIs execute before layout finalization or when snapshot feature state disallows them. Build logs can confirm weaving of both protocol classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js

Purpose: AngularJS module for the Ozone Manager web UI pages covering OM metrics, snapshots, Ratis events, overview, and deletion metrics/configuration.

Important APIs/types/functions: Defines module `ozoneManager` with dependencies `ozone` and `nvd3`. Routes map `/metrics/ozoneManager`, `/snapshots`, `/ratis_events`, and `/metrics/deletion` to components. Components include `omSnapshots`, `ratisEvents`, `omMetrics`, `omOverview`, and `omDeletion`. Helpers format bytes and elapsed milliseconds, paginate/sort snapshot diff jobs, and filter ignored JMX keys.

Control flow: Components issue `$http.get` calls to OM servlet endpoints: `jmx` queries for OMMetrics, OmSnapshotInternalMetrics, SnapshotDiffManager, Ratis metrics, deletion metrics, and performance metrics; `snapshotList` for selected volume/bucket snapshots; and `conf?cmd=getPropertyByTag&tags=DELETION` for deletion configs. Results are transformed into controller fields consumed by templates.

State and persistence behavior: No server persistence. Client-side state includes metric arrays, selected pagination fields on `$scope`, snapshot lists, Ratis event arrays, deletion configs, and current role/metrics snapshots.

Dependencies and integration points: Integrates OM webapp templates, JMX servlet output shapes, config servlet output, NVD3 pie charts, D3 formatting, and Angular route/component infrastructure.

Risks: Several handlers assume `result.data.beans[0]` exists; empty JMX responses can break components. Query strings are built by concatenating volume/bucket without encoding. Snapshot diff pagination mixes numeric strings and numbers. Some functions are duplicated across components. Ratis event parsing assumes `timestamp|description` lines.

Test signals: UI tests should mock empty and populated JMX/config responses, verify snapshot list error handling, pagination with `All` and numeric sizes, metric grouping of `Num*Fails`, deletion config sorting, and safe rendering when Ratis or deletion beans are absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/webapps/ozoneManager/ozoneManager.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java

Purpose: Test utility that creates a lightweight local OM, exposes its managers, and supplies an RPC write client for unit/integration-style OM tests.

Important APIs/types/functions: Constructors accept `OzoneConfiguration` and optional SCM block/container clients. Getters expose `OzoneManagerProtocol`, `OzoneManager`, `KeyManager`, `OMMetadataManager`, `VolumeManager`, `BucketManager`, `PrefixManager`, SCM block client, and `OzoneClient`. `kmsProviderInit` injects a mock KMS provider. `stop` closes the RPC client and stops OM.

Control flow: The constructor sets SCM client address, mini-cluster metrics mode, initializes `OMStorage`, enables test secure OM flag, creates OM, extracts internal managers with whitebox utilities, replaces SCM clients and block token secret manager, starts OM, waits for Ratis leader-ready status, creates an RPC client, and captures manager references.

State and persistence behavior: Initializes an OM metadata directory from the supplied config and mutates OM internals for tests. It does not clean the metadata directory itself beyond caller temp-dir lifecycle. It owns resources that must be stopped.

Dependencies and integration points: Used by bucket-manager tests and other OM tests needing a real OM without a full cluster. Depends on `ScmBlockLocationTestingClient`, mocked `StorageContainerLocationProtocol`, whitebox state mutation, Ratis readiness, and `OzoneClientFactory`.

Risks: Whitebox field names make the utility brittle to OM internals. It sets global/static test flags and metrics mini-cluster mode. `cleanup` in some tests stops OM directly rather than calling `stop`, which can leak RPC client resources. Waiting only 10 seconds for leader readiness can be timing-sensitive.

Test signals: Tests using this helper verify real OM manager behavior through RPC while keeping SCM fake. Failures often indicate OM startup, Ratis readiness, manager injection, or cleanup issues rather than the target test alone.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/OmTestManagers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java

Purpose: Fake `ScmBlockLocationProtocol` for OM tests. It allocates synthetic blocks and simulates delete-block success/failure patterns without a real SCM.

Important APIs/types/functions: Constructor sets cluster ID, SCM ID, and delete failure frequency. `allocateBlock` returns one `AllocatedBlock` with a random datanode, standalone ONE open pipeline, and time-based container/local IDs. `deleteKeyBlocks` processes `DeletedBlock`s into `DeleteBlockGroupResult`s. `processBlock` applies success/all-fail/every-Nth-fail behavior. `getScmInfo`, `getNetworkTopology`, `getNumberOfDeletedBlocks`, `addSCM`, `sortDatanodes`, and `close` complete the protocol.

Control flow: Allocation ignores requested count and returns a singleton block. Delete calls increment a call counter per block, choose success or `unknownFailure`, and increment `numBlocksDeleted` only on success. Blank IDs are replaced with random UUIDs.

State and persistence behavior: No persistence. Maintains counters for current delete call and number of pseudo-deleted blocks.

Dependencies and integration points: Used by `OmTestManagers` and delete/key tests. Integrates HDDS block, pipeline, datanode, topology, and Ozone delete result helper classes.

Risks: `allocateBlock` ignores `num`, requested replication config, owner, excludes, and client machine; it is only valid for tests that need any block. `sortDatanodes` returns null, which can break code paths expecting sorted nodes. Time-based IDs can collide in extremely tight loops. Failure frequency applies per block, not per request group.

Test signals: Tests should assert delete count behavior for frequency 0, 1, and N; allocation shape; SCM info propagation; and that callers do not rely on unsupported methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java

Purpose: Unit tests for `AuthorizerLockImpl`, the multitenant authorizer lock abstraction backed by stamped locking semantics.

Important APIs/types/functions: Tests call `tryReadLock`, `unlockRead`, `tryWriteLock`, `unlockWrite`, `tryWriteLockInOMRequest`, `unlockWriteInOMRequest`, `isWriteLockHeldByCurrentThread`, `tryWriteLockThrowOnTimeout`, `tryOptimisticReadThrowOnTimeout`, and `validateOptimisticRead`.

Control flow: `testStampedLockBehavior` validates normal unlock, bad stamp exceptions, concurrent read locks, write exclusion while reads are held, write exclusivity, and read exclusion while write is held. Other tests verify write lock can be released by another thread for OM request flow, follower-side unlock without prior lock does not throw, thread-local write lock detection only tracks OM-request write locks, and optimistic reads remain valid across reads but fail or invalidate across writes.

State and persistence behavior: No persistence. Tests observe in-memory lock stamps, timeout results, and thread-local lock-held state.

Dependencies and integration points: Protects behavior used by OM multitenancy authorizer update paths where preExecute and validate/update phases may happen on different threads or leaders/followers.

Risks: Tests use short timeout values and thread start without join in one case, so rare scheduling issues could hide release timing. They do not test high contention or interruption behavior.

Test signals: Passing confirms stamped-lock semantics, graceful follower unlock, OM-request thread-local tracking, and optimistic-read invalidation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java

Purpose: Tests core `BucketManagerImpl` behavior through a real test OM and RPC write client.

Important APIs/types/functions: Uses `OmTestManagers`, `OzoneManagerProtocol`, `BucketManager`, `OMMetadataManager`, `OmBucketInfo`, `OmBucketArgs`, `OmVolumeArgs`, `OmKeyArgs`, `OpenKeySession`, bucket encryption helpers, EC/default replication configs, and `OMRequestTestUtils.addBucketToOM`.

Control flow: Setup creates a temp OM. Helpers create sample volumes and direct bucket DB entries. Tests cover bucket creation without volume, encrypted bucket creation with mocked KMS metadata, normal creation, duplicate creation, invalid bucket lookup, `getBucketInfo` volume/bucket error paths, storage type update, versioning update, delete bucket, non-empty bucket deletion after opening/committing keys, and linked bucket resolution across a two-hop link chain.

State and persistence behavior: Mutates real OM metadata through RPC and direct test utility writes. Validates bucket table state, encryption key info, storage type, versioning, delete removal, key/open-key state effects on bucket emptiness, and resolved link-bucket inherited properties.

Dependencies and integration points: Integrates OM startup, write-client protocol, volume/bucket/key managers, KMS provider injection, SCM block fake, bucket layout, quotas, replication, metadata, and link bucket resolution.

Risks: Tests mix RPC operations and direct metadata insertion, which can bypass validation/cache paths. Cleanup stops OM directly and may not close the RPC client. Assertions depend on exact exception messages. Link-bucket test exercises info resolution but not cyclic links or missing targets.

Test signals: Passing confirms major bucket CRUD/property behaviors, encrypted bucket metadata preservation, non-empty delete protection, and link resolution of target bucket properties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java

Purpose: Unit test for bucket utilization metrics emission from OM bucket metadata.

Important APIs/types/functions: Mocks `OMMetadataManager.getBucketIterator`, `MetricsCollector`, and `MetricsRecordBuilder`. Uses `BucketUtilizationMetrics` and `BucketMetricsInfo` metric/tag descriptors. `createMockEntry` builds cache entries containing mocked `OmBucketInfo`.

Control flow: The test creates two bucket cache entries, one with a finite byte quota and one with `QUOTA_RESET`. It configures iterator and metrics builder mocks, calls `getMetrics`, and verifies tags and gauges emitted for volume, bucket, used bytes, snapshot used bytes, quota bytes, quota namespace, and available bytes.

State and persistence behavior: No persistence. It simulates cache-backed bucket metadata and observes metric builder calls. Available bytes are expected to be quota minus used minus snapshot for finite quota, and `QUOTA_RESET` for reset quota.

Dependencies and integration points: Protects integration between OM metadata iteration and Hadoop Metrics2 export for per-bucket utilization.

Risks: Mock-based verification checks calls but not final metrics records as a metrics system would expose them. It covers two buckets and quota reset but not deleted/null cache values or negative availability.

Test signals: Passing means metric collection iterates buckets and emits expected tags/gauges for normal and unlimited quotas.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java

Purpose: Unit tests for `KeyInputStream` reading across multiple `BlockInputStream`s.

Important APIs/types/functions: Creates five anonymous `BlockInputStream` instances backed by 100-byte slices of a random 500-byte string. Tests use `KeyInputStream.read`, `getCurrentStreamIndex`, and `getRemainingOfIndex`.

Control flow: `testReadGroupInputStream` reads 500 bytes in one call and asserts the full string. `testErrorReadGroupInputStream` reads 340 bytes, checks stream index and remaining bytes in the fourth stream, then reads beyond EOF request size and verifies only remaining 160 bytes are returned, followed by `-1` EOF.

State and persistence behavior: No persistence. Anonymous streams track a local `pos` and byte-array input cursor.

Dependencies and integration points: Tests client-side read composition across block streams, using `OzoneClientConfig` with checksum verification enabled. The custom streams bypass real datanodes and checksums.

Risks: The anonymous `read(byte[],off,len)` increments `pos` by `readLen` even if EOF returned `-1`, though fixed 100-byte slices avoid that path in normal reads. Random ASCII content can include edge characters but is compared as UTF-8. Seek behavior is unsupported and untested.

Test signals: Passing confirms sequential multi-block reads, partial reads across block boundaries, current stream accounting, remaining-byte accounting, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java

Purpose: Smoke test for `GrpcOzoneManagerServer` startup and shutdown.

Important APIs/types/functions: Mocks `OzoneManager`, obtains `OzoneManagerProtocolServerSideTranslatorPB`, delegation token manager, and certificate client from the mock, constructs `GrpcOzoneManagerServer`, then calls `start` and `stop`.

Control flow: The test creates default config and mock dependencies, starts the server inside a try block, and always stops it in `finally`.

State and persistence behavior: No OM persistence. It opens and closes server resources allocated by `GrpcOzoneManagerServer`.

Dependencies and integration points: Exercises gRPC OM server constructor/start/stop plumbing with protocol translator and security dependencies, but all OM dependencies are Mockito defaults unless explicitly stubbed elsewhere.

Risks: Because the OM mock is not stubbed, null translator/token/cert dependencies may be accepted by the server path under test; this is a lifecycle smoke test, not functional RPC coverage. It does not verify bound port, service registration, auth, or request handling.

Test signals: Passing indicates the gRPC server can tolerate the constructed dependency set and stop cleanly after start.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java

Purpose: Parameterized unit tests for `KeyManagerImpl` table-scanning helpers used to fetch deleted keys, renamed keys, and deleted directories.

Important APIs/types/functions: `getTableIteratorParameters` defines combinations of volume/bucket filters, start offsets, result limits, and expected exceptions. `mockTableIterator` builds sorted synthetic table keys and configures `Table.iterator(startKey)` with `MapBackedTableIterator`. Tests call `getDeletedKeyEntries`, `getRenamesKeyEntries`, and `getDeletedDirEntries` on a `KeyManagerImpl` with mocked metadata manager tables.

Control flow: Each parameterized test builds a table with deterministic `/volumeNN/bucketNN/keyNN` style keys, applies optional volume/bucket/start filters and a predicate, computes expected limited results, then compares the helper result or expects an exception for invalid volume/bucket filter combinations.

State and persistence behavior: No real persistence. Uses in-memory `TreeMap` and mocked OM DB tables to simulate ordered RocksDB iteration.

Dependencies and integration points: Protects key-manager scanning over `DELETED_TABLE`, `SNAPSHOT_RENAMED_TABLE`, and `DELETED_DIR_TABLE`, plus metadata manager bucket-prefix calculation. These helpers feed deletion/snapshot maintenance workflows.

Risks: The expected data generation mirrors implementation assumptions about key formatting, so shared mistakes in prefix format could pass. It covers iterator order and limits but not real RocksDB iterator resource handling. Deleted-dir tests force `startVolumeNumber` null, so start-key pagination for that path is narrower.

Test signals: Passing confirms filtered table scans honor volume/bucket constraints, start offsets, predicates, limits, value conversion for repeated deleted keys, and invalid filter validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->
