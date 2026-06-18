# subset-b-007586 Research

Grouped source research for Hadoop S3A unbuffering, encryption configuration, change tracking, SSL binding, AWS credential adapters, auditing, assumed-role authorization, custom signing, JCEKS storage, restricted read behavior, and credential marshalling tests. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AUnbuffer.java

## Purpose

`TestS3AUnbuffer.java` is a mock-based unit test for the S3A input stream `unbuffer()` contract. It verifies that calling `FSDataInputStream.unbuffer()` on a stream opened from S3A closes the underlying AWS SDK `ResponseInputStream<GetObjectResponse>` object stream, not only Hadoop's wrapper layer.

## Important APIs, Types, and Functions

The single test method, `testUnbuffer()`, extends `AbstractS3AMockTest` and uses the mocked `s3` client and `fs` filesystem. It builds `HeadObjectResponse` and `GetObjectResponse` values, wraps a Mockito `InputStream` in `AbortableInputStream`, then in `ResponseInputStream<GetObjectResponse>`, and opens the path through `fs.open()`.

## Control Flow

The test installs `headObject` metadata for `getFileStatus()`, installs `getObject` data for `open()`, reads from the stream to force the S3 object stream into use, then calls `stream.unbuffer()`. Finally it verifies `objectStream.close()` was invoked at least once.

## State and Persistence Behavior

All state is in-memory Mockito state. There is no S3 persistence; metadata and object streams are synthetic. The important lifecycle state is that the active S3 object stream transitions from open to closed when Hadoop's unbuffer hook is called.

## Dependencies and Integration Points

The test integrates Hadoop `FSDataInputStream`, S3A stream construction, AWS SDK v2 S3 response streams, and Mockito. It explicitly skips when the analytics accelerator is enabled because that stream implementation does not support unbuffer.

## Risks and Edge Cases

The test depends on mocked end-of-stream reads and does not validate byte-range or partial-read cleanup. Its main regression target is resource leakage: if unbuffer stops propagating to the AWS stream, HTTP connections can stay held.

## Test Signals

Strong signal is `verify(objectStream, atLeast(1)).close()`. Supporting signals are successful mocked open/read and the analytics accelerator skip guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AUnbuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AccessGrantConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AccessGrantConfiguration.java

## Purpose

`TestS3AccessGrantConfiguration.java` validates that S3 Access Grants configuration controls whether S3 clients are built with the Access Grants identity provider. It covers both synchronous and asynchronous S3 clients.

## Important APIs, Types, and Functions

The key constant is `S3_ACCESS_GRANTS_EXPECTED_CREDENTIAL_PROVIDER_CLASS`, bound to `S3AccessGrantsIdentityProvider`. `testS3AccessGrantsEnabled()` and `testS3AccessGrantsDisabled()` drive the behavior through `AWS_S3_ACCESS_GRANTS_ENABLED`. Helpers create a `DefaultS3ClientFactory`, build `S3ClientCreationParameters`, and inspect `AwsClient.serviceClientConfiguration().credentialsProvider()`.

## Control Flow

Each test builds a configuration, creates either an async or sync AWS client, reads the client's configured credentials provider class name, and asserts equality or inequality with the Access Grants provider depending on whether the feature is enabled.

## State and Persistence Behavior

The only durable state is `Configuration` key/value content. Client instances are transient and are not connected to a real bucket for these assertions.

## Dependencies and Integration Points

This tests S3A's `DefaultS3ClientFactory` integration with the AWS SDK Access Grants plugin and the `AWS_S3_ACCESS_GRANTS_ENABLED` option. It also protects parity between sync and async client creation paths.

## Risks and Edge Cases

The test only checks the top-level credentials provider class, not a full request. A future provider wrapper could make the class-name check too strict even if behavior remains correct.

## Test Signals

Signals are provider class equality when explicitly enabled and non-equality for default and explicit disabled configurations across both client types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AccessGrantConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestSSEConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestSSEConfiguration.java

## Purpose

`TestSSEConfiguration.java` is a focused unit test suite for S3A encryption configuration parsing, key lookup, credential-provider override behavior, and encryption-context validation.

## Important APIs, Types, and Functions

The tests exercise `S3AUtils.getEncryptionAlgorithm()`, `getS3EncryptionKey()`, `lookupPassword()`, `S3AEncryptionMethods.getMethod()`, and `S3AEncryption.getS3EncryptionContext()`. Helpers `buildConf()`, `confWithProvider()`, `addFileProvider()`, and `setProviderOption()` construct empty configurations and temporary JCEKS credential providers. Constants include `S3_ENCRYPTION_ALGORITHM`, `S3_ENCRYPTION_KEY`, `S3_ENCRYPTION_CONTEXT`, `SECRET_KEY`, and the bucket-specific `fs.s3a.bucket.<bucket>.*` pattern.

## Control Flow

The suite builds small configurations for each encryption mode, calls the parser or secret lookup path, and asserts either selected `S3AEncryptionMethods` or expected exceptions. Credential-provider tests write secrets into a temporary provider and verify those secrets override plain configuration entries, including bucket-scoped entries.

## State and Persistence Behavior

Most state is configuration-only. Credential provider tests persist temporary secret entries in a JCEKS file under JUnit `@TempDir`; the file is test-scoped and flushed through `CredentialProvider.flush()`.

## Dependencies and Integration Points

This is tied to S3A encryption constants, Hadoop credential provider APIs, `ProviderUtils`, and the newer S3A encryption helper class. It also covers backward-compatible deprecated encryption option cleanup through unset calls.

## Risks and Edge Cases

Key validation differs by algorithm: SSE-C requires a key, SSE-S3 rejects keys, SSE-KMS accepts keys and contexts, and client-side methods must be marked non-server-side. Invalid encryption context strings must fail during split validation.

## Test Signals

Signals include exception substrings for missing SSE-C key, SSE-S3 key misuse, unknown algorithms, and invalid contexts; exact method equality for SSE-C, SSE-KMS, CSE-KMS, CSE-CUSTOM, and NONE; and provider-overrides-configuration assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestSSEConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestStreamChangeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestStreamChangeTracker.java

## Purpose

`TestStreamChangeTracker.java` verifies `ChangeTracker`, the S3A component that detects object changes during stream reads and copy operations using ETag or VersionId constraints.

## Important APIs, Types, and Functions

Tests create policies through `ChangeDetectionPolicy.createPolicy(mode, source, requireVersion)` and instantiate `ChangeTracker` with `CountingChangeTracker` and `S3ObjectAttributes`. The suite exercises `maybeApplyConstraint()` on `GetObjectRequest.Builder` and `CopyObjectRequest.Builder`, `processResponse()` for GET and COPY responses, and `processException()` for S3 precondition failures.

## Control Flow

Client-mode tests observe first response revision IDs, then feed mismatching responses and expect `RemoteFileChangedException`. Server-mode tests verify request constraints are applied after a revision is known and that null/precondition failure responses are treated as server-reported changes. Required-version tests expect `NoVersionAttributeException` when the selected revision source is missing.

## State and Persistence Behavior

The tracker retains a current revision ID and mismatch count in memory. `CountingChangeTracker` records mismatch events for statistics. No external state is persisted.

## Dependencies and Integration Points

The suite covers AWS SDK v2 S3 GET/COPY models, S3A `S3ObjectAttributes`, Hadoop `PathIOException`, `RemoteFileChangedException`, and HTTP 412 precondition translation.

## Risks and Edge Cases

Risks include silent stale reads when constraints are not applied, over-strict behavior against endpoints without version IDs, and missed copy failures due to SDK exception shape. Warning mode is intentionally one-shot to avoid repeated mismatch noise.

## Test Signals

Signals are applied-constraint booleans, stored revision IDs, exact mismatch counts, and expected exceptions for version absence, revision mismatch, and 412 precondition failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestStreamChangeTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestWildflyAndOpenSSLBinding.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestWildflyAndOpenSSLBinding.java

## Purpose

`TestWildflyAndOpenSSLBinding.java` validates S3A network binding for SSL channel modes, especially graceful downgrade behavior when WildFly OpenSSL classes or native libraries are unavailable.

## Important APIs, Types, and Functions

The suite tests `NetworkBinding.bindSSLChannelMode(Configuration, ApacheHttpClient.Builder)` with `DelegatingSSLSocketFactory.SSLChannelMode` values `Default`, `OpenSSL`, `Default_JSSE`, and `Default_JSSE_with_GCM`. `setup()` detects `org.wildfly.openssl.OpenSSLProvider` on the classpath.

## Control Flow

Each test resets the default socket factory, sets `SSL_CHANNEL_MODE`, invokes the binding helper, and inspects the resulting `DelegatingSSLSocketFactory` channel mode. Assumptions split WildFly-present and WildFly-absent paths.

## State and Persistence Behavior

The test mutates global `DelegatingSSLSocketFactory` default state and resets it before each bind. Configuration state is local and no network calls are made.

## Dependencies and Integration Points

This covers Apache AWS SDK HTTP client setup, Hadoop SSL socket factory selection, and optional WildFly OpenSSL provider discovery.

## Risks and Edge Cases

Global socket-factory state makes reset behavior critical. The OpenSSL outcome is environment-sensitive: WildFly classes may exist without native OpenSSL loading successfully.

## Test Signals

Signals include `IllegalArgumentException` for an unknown mode, `NoClassDefFoundError` when OpenSSL is requested without WildFly, downgrade from `Default` to `Default_JSSE` without WildFly, and exact JSSE/GCM mode preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestWildflyAndOpenSSLBinding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/adapter/TestV1CredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/adapter/TestV1CredentialsProvider.java

## Purpose

`TestV1CredentialsProvider.java` verifies S3A compatibility with legacy AWS SDK v1 credential-provider declarations while producing AWS SDK v2 credential providers for the modern client stack.

## Important APIs, Types, and Functions

The tests drive `CredentialProviderListFactory.createAWSCredentialProviderList()` with `AWS_CREDENTIALS_PROVIDER`. `testV1V2Mapping()` checks known v1 provider class-name aliases map to v2/provider equivalents. `testV1Wrapping()` verifies arbitrary v1 providers are wrapped by `V1ToV2AwsCredentialProviderAdapter`. Nested classes model v1 providers with default constructor, `Configuration` constructor, and failing static factory method.

## Control Flow

Configuration strings are built as comma-separated provider class names. The factory creates `AWSCredentialProviderList`, then `assertCredentialProviders()` walks provider instances in order and checks assignability.

## State and Persistence Behavior

State is limited to configuration and instantiated provider lists. No credentials are resolved from real external sources in these tests.

## Dependencies and Integration Points

This bridges `com.amazonaws.auth.AWSCredentialsProvider` from SDK v1 with `software.amazon.awssdk.auth.credentials.AwsCredentialsProvider` from SDK v2, including S3A aliases for anonymous, environment, and IAM/container credentials.

## Risks and Edge Cases

Compatibility risks are ordering changes, alias regressions, and recursive/fallback instantiation hiding a real provider construction error.

## Test Signals

Signals are ordered provider class checks and propagation of `InstantiationIOException` containing the simulated `ClassNotFoundException` text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/adapter/TestV1CredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AbstractAuditingTest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AbstractAuditingTest.java

## Purpose

`AbstractAuditingTest.java` is the shared unit-test base for S3A audit-manager and auditor tests. It creates an audit manager, request factory, and IOStatistics store, then provides helpers to synthesize AWS SDK request callback sequences.

## Important APIs, Types, and Functions

Subclasses implement `createConfig()`. `setup()` creates a `RequestFactoryImpl` and starts an `AuditManagerS3A` through `AuditIntegration.createAndStartAuditManager()`. Helpers include `head()`, `get(range)`, `headForBulkDelete()`, `span()`, `activeSpan()`, `assertHeadUnaudited()`, and counter checks for `AUDIT_FAILURE` and `AUDIT_REQUEST_EXECUTION`.

## Control Flow

Request helpers construct S3 request builders, notify the manager through `requestCreated()`, build `InterceptorContext` and `ExecutionAttributes`, then run `beforeExecution()` and `modifyHttpRequest()` to simulate AWS SDK interceptor flow without performing network I/O.

## State and Persistence Behavior

The base owns a per-test `IOStatisticsStore`, `RequestFactory`, and audit manager. Teardown stops the manager quietly. Audit span state is thread-local/manager-local, not persisted.

## Dependencies and Integration Points

It ties together audit manager lifecycle, AWS SDK v2 interceptors, S3 request builders, Hadoop audit spans, and S3A statistics counters.

## Risks and Edge Cases

If the simulated callback order diverges from the AWS SDK flow, tests could miss integration regressions. The base deliberately exposes helpers for HEAD, GET with Range, and bulk delete to reduce that risk.

## Test Signals

Subclasses rely on active-span identity, generated referrer headers, expected audit exceptions, and IOStatistics counter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AbstractAuditingTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AccessCheckingAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AccessCheckingAuditor.java

## Purpose

`AccessCheckingAuditor.java` is a controllable no-op auditor used by access-check integration tests. It lets tests switch `checkAccess()` between allow and deny outcomes.

## Important APIs, Types, and Functions

The class extends `NoopAuditor`, exposes class name constant `CLASS`, stores an `accessAllowed` boolean, provides `setAccessAllowed(boolean)`, and overrides `checkAccess(Path, S3AFileStatus, FsAction)`.

## Control Flow

`checkAccess()` logs the path and current allow flag, then returns that flag. It does not inspect path, status, or requested action beyond logging.

## State and Persistence Behavior

The only mutable state is the in-memory `accessAllowed` flag on the auditor instance. It is not synchronized, which is acceptable for single-test control but important if reused concurrently.

## Dependencies and Integration Points

It integrates with S3A `S3AFileSystem.access()` through the audit access-check callback and with `ITestAuditAccessChecks`.

## Risks and Edge Cases

Because all paths share one flag, it cannot validate path-specific or action-specific authorization. It is a test double for control flow, not a policy model.

## Test Signals

Downstream signals are access success when true and `AccessControlException` plus audit failure metrics when false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AccessCheckingAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AuditTestSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AuditTestSupport.java

## Purpose

`AuditTestSupport.java` centralizes test helpers for S3A auditing configuration, statistics, and assumptions.

## Important APIs, Types, and Functions

It exposes `NOOP_SPAN`, `noopAuditor()`, `noopAuditConfig()`, `loggingAuditConfig()`, `enableLoggingAuditor()`, `createIOStatisticsStoreForAuditing()`, `resetAuditOptions()`, and `requireOutOfSpanOperationsRejected()`.

## Control Flow

Configuration helpers construct or patch `Configuration` objects with audit service class names, enable flags, and out-of-span rejection. Statistics helper builds an `IOStatisticsStore` with audit and HTTP response counters. `requireOutOfSpanOperationsRejected()` skips tests if the filesystem audit manager is configured not to reject out-of-span calls.

## State and Persistence Behavior

The class has no instance state. It creates fresh configurations and stores, and mutates configurations passed to reset/enable methods.

## Dependencies and Integration Points

It integrates with `NoopAuditManagerS3A`, `NoopAuditor`, S3A audit constants, `S3ATestUtils.removeBaseAndBucketOverrides()`, IOStatistics binding, and AssertJ assumptions.

## Risks and Edge Cases

Reset coverage must stay aligned with audit options; omitted options can leak bucket-specific settings into tests. The no-op span is reusable and intentionally shared.

## Test Signals

Signals are consistent audit configs, wired statistics counters, and accurate skip behavior for out-of-span rejection dependent tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AuditTestSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditAccessChecks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditAccessChecks.java

## Purpose

`ITestAuditAccessChecks.java` is an S3A integration-cost test proving `S3AFileSystem.access()` delegates to the configured auditor and reports correct metrics for allowed, denied, and missing paths.

## Important APIs, Types, and Functions

It extends `AbstractS3ACostTest`, configures `AccessCheckingAuditor`, retrieves it from the filesystem in `setup()`, and tests file, directory, root, denied file, denied directory, and missing-path access cases. The local `access()` helper invokes `fs.access(path, FsAction.ALL)`.

## Control Flow

Allowed tests create a file/directory and verify access succeeds with expected metadata/list probes. Denied tests first create the target, switch the auditor to deny, and expect `AccessControlException` after existence probing. Missing-path access expects `FileNotFoundException` before the auditor denial is applied.

## State and Persistence Behavior

The test creates real S3 paths through the contract filesystem. Mutable auditor state controls authorization. Metrics are live filesystem IOStatistics.

## Dependencies and Integration Points

This validates `S3AFileSystem.access()`, audit access-check callback flow, `AccessCheckingAuditor`, cost validation helpers, and S3A statistic names.

## Risks and Edge Cases

Access checks are expected after status probing, so denial costs differ for file and directory targets. Missing paths must remain FNFE, not access denied.

## Test Signals

Signals include `INVOCATION_ACCESS`, `AUDIT_ACCESS_CHECK_FAILURE`, `AUDIT_REQUEST_EXECUTION`, `STORE_IO_REQUEST`, and operation-cost probes for file, directory, and root status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditAccessChecks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManager.java

## Purpose

`ITestAuditManager.java` verifies audit request execution in a real S3A filesystem, including rejection of out-of-span S3 calls and loading of extra AWS SDK execution interceptors.

## Important APIs, Types, and Functions

The test enables the logging auditor, sets `AUDIT_EXECUTION_INTERCEPTORS` to `SimpleAWSExecutionInterceptor.CLASS`, and intentionally sets invalid legacy request handlers. `testInvokeOutOfSpanRejected()` exercises `WriteOperationHelper.listMultipartUploads()`. `testExecutionInterceptorBinding()` executes `fs.listStatus("/")`.

## Control Flow

The first test closes a span so the writer holds an invalid span, expects an `AccessDeniedException` wrapping `AuditFailureException`, verifies audit counters increased, then permits out-of-band operations and retries. The second records interceptor invocation count, performs a listing, and asserts the custom interceptor ran with the filesystem configuration.

## State and Persistence Behavior

Audit flags can be changed at runtime through `setAuditFlags()`. Counter state lives in filesystem IOStatistics. `SimpleAWSExecutionInterceptor` records static invocation/config state.

## Dependencies and Integration Points

It integrates S3A write helpers, logging audit manager, AWS SDK interceptor extension loading, and IOStatistics counters.

## Risks and Edge Cases

The test is sensitive to configurations that disable out-of-span rejection, so it uses an assumption guard. Invalid request-handler config should not prevent execution-interceptor loading.

## Test Signals

Signals are increasing `AUDIT_REQUEST_EXECUTION` and `AUDIT_FAILURE` counters, an access-denied exception with unaudited-operation text, and custom interceptor invocation/config capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManagerDisabled.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManagerDisabled.java

## Purpose

`ITestAuditManagerDisabled.java` verifies that setting `AUDIT_ENABLED=false` produces a no-op audit manager and stable no-op spans in an S3A filesystem.

## Important APIs, Types, and Functions

The test extends `AbstractS3ACostTest`, resets audit options, disables auditing, then asserts the filesystem audit manager is `NoopAuditManagerS3A`. It also compares spans returned by `fs.createSpan()` with `AuditTestSupport.NOOP_SPAN`.

## Control Flow

Filesystem construction uses the disabled audit configuration. Tests retrieve the manager and create two spans, expecting the no-op singleton span in both cases.

## State and Persistence Behavior

No real audit span state should be stored. All spans are the shared no-op span, so there is no per-operation lifecycle state.

## Dependencies and Integration Points

This covers S3A filesystem startup, audit manager selection, and no-op span behavior.

## Risks and Edge Cases

Any accidental creation of active audit managers when disabled would introduce overhead and possibly referrer headers or rejection behavior into disabled deployments.

## Test Signals

Signals are manager class identity and object identity of all created spans with `NOOP_SPAN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManagerDisabled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/MemoryHungryAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/MemoryHungryAuditor.java

## Purpose

`MemoryHungryAuditor.java` is a deliberately large test auditor used to expose memory leaks in active audit-manager thread/span tracking.

## Important APIs, Types, and Functions

It extends `AbstractOperationAuditor`, publishes class name `NAME`, allocates `MANAGER_SIZE` bytes per auditor and `SPAN_SIZE` bytes per span, counts instances and spans, overrides `createSpan()`, `getUnbondedSpan()`, and `noteSpanReferenceLost()`, and defines nested `MemorySpan`.

## Control Flow

Each created span increments `spanCount` and returns a new `MemorySpan`. `getUnbondedSpan()` lazily creates one unbonded span. `MemorySpan.activate()` returns itself and `deactivate()` is intentionally empty, leaving manager-side map behavior as the test focus.

## State and Persistence Behavior

State is intentionally memory-heavy: per-auditor byte array, per-span byte array, static instance counter, instance span counter, and cached unbonded span.

## Dependencies and Integration Points

It integrates with `ActiveAuditManagerS3A` leak tests and the `AbstractAuditSpanImpl` contract.

## Risks and Edge Cases

Because it consumes tens of MB across many managers, test parameters must remain bounded. It is not suitable for general audit tests or production use.

## Test Signals

Signals are heap pressure, instance/span counts, and whether weak-reference pruning frees manager/span references before out-of-memory conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/MemoryHungryAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/SimpleAWSExecutionInterceptor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/SimpleAWSExecutionInterceptor.java

## Purpose

`SimpleAWSExecutionInterceptor.java` is a test AWS SDK v2 `ExecutionInterceptor` used to verify dynamic interceptor loading and configuration injection through S3A auditing setup.

## Important APIs, Types, and Functions

The class extends `Configured`, implements `ExecutionInterceptor`, exposes class name `CLASS`, keeps static `AtomicLong INVOCATIONS`, and static `Configuration staticConf`. `beforeExecution()` increments the counter and captures `getConf()`.

## Control Flow

When an AWS SDK request reaches `beforeExecution()`, the interceptor records that it was invoked and stores the configured Hadoop `Configuration`.

## State and Persistence Behavior

State is process-static and persists across test methods unless explicitly accounted for. Tests compare deltas rather than assuming zero.

## Dependencies and Integration Points

It integrates with `AUDIT_EXECUTION_INTERCEPTORS`, `AuditManagerS3A.createExecutionInterceptors()`, and real S3 request execution in audit manager tests.

## Risks and Edge Cases

Static state can leak across tests, so assertions must use base counts. It does not validate request contents; it only proves invocation and configuration binding.

## Test Signals

Signals are an increased invocation count and `staticConf` identity matching the filesystem configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/SimpleAWSExecutionInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditIntegration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditIntegration.java

## Purpose

`TestAuditIntegration.java` unit-tests S3A audit integration points that are independent of a live S3 filesystem: exception translation, auditor instantiation, manager lifecycle, interceptor creation, and span attachment.

## Important APIs, Types, and Functions

It exercises `S3AUtils.translateException()`, `S3ARetryPolicy`, `AuditIntegration.createAndInitAuditor()`, `createAndStartAuditManager()`, `stubAuditManager()`, `attachSpanToRequest()`, and `retrieveAttachedSpan()`. It also checks `AUDIT_SPAN_EXECUTION_ATTRIBUTE`.

## Control Flow

Tests translate audit exceptions and inspect resulting types/retry decisions. Auditor tests create no-op or logging auditors, assert service states, close managers, and verify lifecycle propagation. Interceptor tests simulate the basic AWS SDK callback sequence and ensure an invalid span is attached when no active span exists.

## State and Persistence Behavior

The class owns an IOStatistics store. Manager/auditor state follows Hadoop service lifecycle and is explicitly closed or checked for stopped state.

## Dependencies and Integration Points

This covers audit integration factory methods, Hadoop service state, AWS SDK v2 interceptors, request factory builders, retry policy behavior, and span execution attributes.

## Risks and Edge Cases

Misclassification of audit failures can cause wrong retry behavior or wrong public exception type. Interceptor sequence tests are synthetic but cover key transition points.

## Test Signals

Signals include `AccessDeniedException` translation, fail-fast retry decision for unsupported audit operation, service started/stopped assertions, interceptor list size/type, and span identity round trip through execution attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditSpanLifecycle.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditSpanLifecycle.java

## Purpose

`TestAuditSpanLifecycle.java` verifies basic audit span lifecycle semantics for the no-op audit manager path created through the shared auditing test base.

## Important APIs, Types, and Functions

The class extends `AbstractAuditingTest`, uses `noopAuditConfig()`, captures the initial reset span in `setup()`, and tests `createSpan()`, `activate()`, `close()`, `deactivate()` semantics through the `AuditSpan` interface.

## Control Flow

Tests create one or more spans, assert the latest span becomes active, reactivate earlier spans, close active and inactive spans, and confirm the reset/unbonded span is restored where expected.

## State and Persistence Behavior

Span state is thread-bound through the manager. The initial reset span is invalid and should remain active when no valid span is bound.

## Dependencies and Integration Points

This validates `AuditManagerS3A` span management, `AuditSpan` validity, execution interceptor creation, and manager stop behavior.

## Risks and Edge Cases

Incorrect deactivation could leave stale spans active or allow the reset span to be closed. The tests specifically guard inactive-span close and reset-span close behavior.

## Test Signals

Signals are active span object identity, validity predicates, non-empty interceptor lists, and successful manager stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestAuditSpanLifecycle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestHttpReferrerAuditHeader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestHttpReferrerAuditHeader.java

## Purpose

`TestHttpReferrerAuditHeader.java` validates construction, filtering, parsing, and resilience of S3A audit referrer headers generated by the logging auditor.

## Important APIs, Types, and Functions

It extends `AbstractAuditingTest`, configures `loggingAuditConfig()` plus `REFERRER_HEADER_FILTER`, and uses `LoggingAuditor`, `HttpReferrerAuditHeader`, `CommonAuditContext`, `S3LogParser`, and `ReferrerExtractor`. Tests cover HEAD, GET with and without Range, bulk delete, complex paths, AWS access log parsing, quote stripping, and failing audit-context suppliers.

## Control Flow

Request helpers run through the audit manager, then tests extract the `Referer` header, parse query parameters, and compare operation, paths, principal, filesystem id, span id, timestamp, thread IDs, range, and delete-key count. Filtering tests add dynamic attributes and confirm filtered keys are omitted.

## State and Persistence Behavior

The logging auditor stores the last header. Audit spans keep timestamps stable across header building. `CommonAuditContext` is mutated in the resilience test and cleaned up in `finally`.

## Dependencies and Integration Points

This is the main audit-header integration point across S3A audit constants, Hadoop common audit context, AWS SDK HTTP request mutation, S3 server access log regex parsing, and user identity lookup.

## Risks and Edge Cases

Headers must survive spaces, colons, URI escaping, quoted AWS log fields, optional Range, bulk delete metadata, and exceptions thrown by context callbacks. Filter leakage could expose sensitive attributes.

## Test Signals

Signals are header presence, single header value, exact query parameter comparisons, filtered-key absence, regex match against a real log sample, range/delete-key fields, and blank referrer on callback failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestHttpReferrerAuditHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestLoggingAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestLoggingAuditor.java

## Purpose

`TestLoggingAuditor.java` validates logging-auditor span behavior, out-of-span rejection, permitted out-of-span request types, transfer listener span propagation, span IDs, and HTTP response statistic extraction.

## Important APIs, Types, and Functions

It uses `LoggingAuditor`, `AuditManagerS3A`, AWS SDK request models such as `UploadPartCopyRequest`, `GetBucketLocationRequest`, and `CompleteMultipartUploadRequest`, `TransferListener`, and failure contexts created with `DefaultFailedExecutionContext`.

## Control Flow

The main span test creates a span, successfully issues a HEAD, deactivates/close spans and expects unaudited HEAD failures, then reactivates spans to allow requests again. Transfer tests create listeners inside/outside spans and verify callback activation. Error tests feed synthetic 400/500 HTTP responses into span failure handling.

## State and Persistence Behavior

Active span state is thread-local/manager-local. IOStatistics counters record audit request execution/failure and HTTP response class counters.

## Dependencies and Integration Points

The suite covers logging auditor, AWS SDK execution failure handling, transfer manager listener integration, and the audit manager's allowlist for background transfer requests.

## Risks and Edge Cases

Transfer-manager background threads require selected operations outside normal spans. Overly strict rejection would break uploads/copies; overly loose handling would hide unaudited user requests.

## Test Signals

Signals include audit execution/failure counter deltas, successful allowlisted request callbacks outside spans, active span restoration through transfer listener, distinct span IDs, and `HTTP_RESPONSE_400`/`HTTP_RESPONSE_500` counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestLoggingAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/ReferrerExtractor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/ReferrerExtractor.java

## Purpose

`ReferrerExtractor.java` is a tiny test-only helper that exposes `LoggingAuditor.getReferrer()` behavior to tests despite package/private span wrapping details.

## Important APIs, Types, and Functions

The class has a private constructor and one static method, `getReferrer(LoggingAuditor auditor, AuditSpanS3A span)`, returning `HttpReferrerAuditHeader`.

## Control Flow

The helper checks whether the supplied span is an `ActiveAuditManagerS3A.WrappingAuditSpan`; if so, it unwraps to the inner span before delegating to `auditor.getReferrer()`. Otherwise it passes the span through directly.

## State and Persistence Behavior

The class is stateless. It only exposes existing span/auditor state.

## Dependencies and Integration Points

It integrates tests in the public audit package with implementation classes in `audit.impl`, especially logging-auditor referrer generation and active-manager wrapping.

## Risks and Edge Cases

Passing a span from a different auditor implementation can raise `ClassCastException`, as documented. This is acceptable because it is a narrow test helper.

## Test Signals

The main signal is `TestHttpReferrerAuditHeader.testSpanResilience()`, which obtains a referrer from a wrapped logging span and verifies failure-resilient header building.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/ReferrerExtractor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/TestActiveAuditManagerThreadLeakage.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/TestActiveAuditManagerThreadLeakage.java

## Purpose

`TestActiveAuditManagerThreadLeakage.java` stress-tests `ActiveAuditManagerS3A` weak-reference span tracking to prevent thread-local memory leaks described by HADOOP-18091.

## Important APIs, Types, and Functions

The class creates `ActiveAuditManagerS3A` with `MemoryHungryAuditor`, inspects `WeakReferenceThreadMap`, uses `PRUNE_THRESHOLD`, and creates spans from fixed thread pools. Key tests are `testSpanMapClearedInServiceStop()`, `testMemoryLeak()`, `testRegularPruning()`, and `testSpanDeactivationRemovesEntryFromMap()`.

## Control Flow

The leak test repeatedly creates managers on a short-lived executor, has long-lived worker threads create spans, forces GC, probes weak map entries, verifies dereferenced entries are pruned, and keeps weak references to managers to confirm some are garbage collected. Other tests check stop clears the map, periodic pruning occurs, and deactivation removes entries.

## State and Persistence Behavior

State is intentionally heap-heavy and weak-reference-based: manager list, worker thread pool, active span map entries keyed by thread ID, pruning count, and weak manager references.

## Dependencies and Integration Points

It validates the active audit manager's lifecycle, weak map cleanup, memory-heavy auditor behavior, and span activation/deactivation interactions.

## Risks and Edge Cases

The test is timing/GC-sensitive and uses large constants. It avoids creating spans in the JUnit thread because those references would live for the JVM duration.

## Test Signals

Signals are span map size zero after stop, nonzero prune count, nonzero garbage-collected managers, exact periodic pruning count, and map-key presence transitions after deactivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/TestActiveAuditManagerThreadLeakage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumeRole.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumeRole.java

## Purpose

`ITestAssumeRole.java` is the main integration suite for S3A assumed-role authentication and session policy enforcement. It validates credential-provider creation, invalid configurations, restricted read/write policies, commit operations, partial deletes, bulk delete behavior, retry callbacks, and bucket-location denial handling.

## Important APIs, Types, and Functions

The class uses `AssumedRoleCredentialProvider`, `RoleTestUtils`, `RoleModel`, `RolePolicies`, `CommitOperations`, `BulkDelete`, `S3GuardTool.BucketInfo`, and S3A contract helpers. Helpers include `createValidRoleConf()`, `createAssumedRoleConfig()`, `assertCommitAccessDenied()`, `writeCSVData()`, `executePartialDelete()`, `executeBulkDeleteOnReadOnlyFiles()`, and `bindReadOnlyRolePolicy()`.

## Control Flow

Setup skips if no assumed-role ARN exists and disables S3 Express create-session. Early tests create providers and filesystems or expect failures for missing/bad ARN, malformed policies, forbidden nested assumed roles, bad inner credentials, invalid session names, and illegal durations. Policy tests bind inline STS session policies and run real S3 operations to confirm reads, writes, deletes, multipart uploads, commits, bulk deletes, and bucket-location calls succeed or fail as intended.

## State and Persistence Behavior

The suite creates real S3 objects/directories, temporary local files for commit uploads, role-backed `S3AFileSystem` instances, and session credentials from STS. `roleFS` is closed in teardown. Progress state is tracked by `ProgressCounter`.

## Dependencies and Integration Points

This integrates S3A credential provider factory, STS assume-role API, AWS IAM policy JSON generation, S3A filesystem operations, commit protocol files, bulk delete API, S3Guard bucket-info command, KMS/S3 Express policy statements, and S3A error translation.

## Risks and Edge Cases

The tests depend on external AWS configuration and permissions. S3 Express has different permission granularity, so partial path restrictions are skipped. Inline policies can override role permissions completely; delete behavior must handle partial failures without hiding access-denied paths.

## Test Signals

Signals include successful credential resolution, expected `StsException`, `AWSBadRequestException`, `InstantiationIOException`, and `AccessDeniedException` paths; actual allowed filesystem operations; progress counts for uploads; access-denied commit results; bulk delete per-path error entries; and `LOCATION_UNKNOWN` fallback when bucket location is forbidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumeRole.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumedRoleCommitOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumedRoleCommitOperations.java

## Purpose

`ITestAssumedRoleCommitOperations.java` runs the generic S3A commit-operation integration tests under an assumed role restricted to a specific directory.

## Important APIs, Types, and Functions

The class extends `ITestCommitOperations`, overrides `createConfiguration()`, `setup()`, `teardown()`, `getFileSystem()`, and `path(String)`. It uses `newAssumedRoleConfig()`, `bindRolePolicyStatements()`, S3 bucket-read policy statements, KMS statements, and `S3_PATH_RW_OPERATIONS` for a restricted directory.

## Control Flow

Setup creates a restricted directory under the full filesystem, builds an assumed-role configuration, attaches a policy allowing bucket reads and read/write only under that directory, then opens `roleFS`. Superclass tests call `getFileSystem()` and `path()`, so they operate through the restricted role and within the allowed path.

## State and Persistence Behavior

The test owns a role filesystem and restricted path. The superclass creates commit-operation objects and S3 artifacts. `roleFS` is closed in teardown and nulled so superclass teardown can use the full filesystem.

## Dependencies and Integration Points

This connects the commit operation test suite with assumed-role credentials and policy scoping, including S3 Express and KMS policy helpers.

## Risks and Edge Cases

Startup has to avoid returning `null` from `getFileSystem()` before `roleFS` is initialized. Path override must keep all inherited tests inside the restricted directory.

## Test Signals

Signals come from the inherited commit-operation assertions, now executed with assumed-role access boundaries. Successful inherited tests prove the minimal policy supports commit operations under the allowed directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumedRoleCommitOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestCustomSigner.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestCustomSigner.java

## Purpose

`ITestCustomSigner.java` integration-tests the legacy/custom S3 signer SPI with AWS SDK v2, including signer initialization, per-UGI store registration, request signing, and cleanup for both bulk-delete and simple-delete modes.

## Important APIs, Types, and Functions

The parameterized class configures `CUSTOM_SIGNERS` and `SIGNING_ALGORITHM_S3`. Nested `CustomSigner` extends `AbstractAwsS3V4Signer`, implements `Signer` and `Configurable`, tracks instantiation/invocation counts, delegates S3 requests to `AwsS3V4Signer`, and delegates KMS requests to `Aws4Signer`. Nested `CustomSignerInitializer` implements `AwsSignerInitializer` and tracks registered stores by bucket and `UserGroupInformation`.

## Control Flow

Each parameterized run opens two filesystems under different UGIs with different test identifiers, performs mkdir/list/touch/delete and optional magic-commit operations, and verifies signer invocation, configuration injection, and initializer store lookup. Closing each filesystem must unregister its store.

## State and Persistence Behavior

Static counters and store maps persist within the class and are reset in setup. Real S3 paths are created. Filesystems are closed per UGI in teardown to release cached state.

## Dependencies and Integration Points

This covers S3A custom signer registration, signer initializer lifecycle, UGI isolation, path-style bucket handling, AWS SDK v2 signer delegation, checksum configuration, magic committer behavior, and multi-delete toggling.

## Risks and Edge Cases

Bucket parsing differs for path-style access and KMS endpoints. Checksum headers can break custom signing, so checksum algorithms and validation are disabled. Store registration must be exact to avoid leaking UGI/bucket mappings.

## Test Signals

Signals are increased signer instantiation/invocation counts, captured store value/config identifier, `CustomSigner.getLastConfiguration()` identity, store-map size transitions from 2 to 1 to 0, and successful filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestCustomSigner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestHttpSigner.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestHttpSigner.java

## Purpose

`ITestHttpSigner.java` integration-tests the newer HTTP signer SPI by enabling a custom HTTP signer class and running normal S3A operations under two different UGIs.

## Important APIs, Types, and Functions

The class configures `HTTP_SIGNER_ENABLED`, `HTTP_SIGNER_CLASS_NAME`, and removes custom S3 signer overrides. It uses `CustomHttpSigner`, `UserGroupInformation.doAs()`, `disableFilesystemCaching()`, and standard S3A file operations.

## Control Flow

Setup determines endpoint and region from the active filesystem. The test creates separate configurations for two identifiers, opens a filesystem under each UGI, creates directories/files, lists status, deletes and recreates files, and optionally exercises magic-commit cleanup/rename/delete paths.

## State and Persistence Behavior

Each test creates real S3 paths and two UGI-scoped filesystems. Teardown closes all filesystems for both UGIs.

## Dependencies and Integration Points

This covers S3A HTTP signer plugin loading, region propagation, UGI-specific filesystem instances, and interaction with normal filesystem and magic committer operations.

## Risks and Edge Cases

The class validates operation success rather than inspecting signer internals, so it primarily detects gross signer wiring failures. Region discovery can make a real S3 call.

## Test Signals

Signals are successful filesystem creation and S3 operations under both UGIs with the custom HTTP signer enabled and no filesystem caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestHttpSigner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestJceksIO.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestJceksIO.java

## Purpose

`ITestJceksIO.java` verifies that Hadoop credential-provider JCEKS files can be listed, created, and deleted through `jceks://s3a@...` provider URIs backed by S3A.

## Important APIs, Types, and Functions

The test uses `CredentialShell`, `HADOOP_SECURITY_CREDENTIAL_PROVIDER_PATH`, `S3A_SECURITY_CREDENTIAL_PROVIDER_PATH`, and helper `toJceksProvider(Path)`. It captures stdout/stderr in setup and restores them in teardown. `closeAllFilesystems()` runs after all tests to clean up credential-provider filesystem instances.

## Control Flow

`testListMissingJceksFile()` runs `credential list` against a missing keystore and expects success. `testCredentialSuccessfulLifecycle()` runs `create`, verifies the keystore is an S3A file, runs `list`, runs `delete`, then lists again and checks the alias is absent.

## State and Persistence Behavior

The suite creates an actual JCEKS keystore object in S3 under the test path. It manipulates process stdout/stderr and closes output streams. Filesystem caching is disabled for new shell configurations.

## Dependencies and Integration Points

This covers Hadoop CredentialShell, S3A filesystem-as-credential-store transport, credential provider path configuration, and cleanup of UGI filesystem caches.

## Risks and Edge Cases

Credential providers can leak filesystem instances. The test also depends on CLI output text, which can be brittle if CredentialShell messages change.

## Test Signals

Signals are zero CredentialShell return codes, expected create/delete/list output text, keystore existence through `assertIsFile()`, and absence of the deleted credential in final list output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestJceksIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestRestrictedReadAccess.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestRestrictedReadAccess.java

## Purpose

`ITestRestrictedReadAccess.java` is a bundled integration scenario for S3A behavior when an assumed-role client has write/list permissions but no GET/read access under a subtree.

## Important APIs, Types, and Functions

It uses `newAssumedRoleConfig()`, `bindRolePolicyStatements()`, `LocatedFileStatusFetcher`, `globStatus()`, `lsR()`, S3A metric diffs, and helpers `fileNotFound()`, `accessDenied()`, `globFS()`, and several `check*` methods. `testNoReadAccess()` orchestrates setup and all checks.

## Control Flow

`initNoReadAccess()` creates a directory tree with files and binds an assumed-role policy denying `S3_ALL_GET` under `noReadDir` while allowing other operations. Checks then cover status/list/open/read, glob expansion, single-thread and multi-thread located status fetching, nonexistent path handling, and delete cleanup.

## State and Persistence Behavior

The test creates real S3 directories/files through the full filesystem and a restricted role-backed filesystem. Shared fields store all paths, role configuration, and `readonlyFS`, which is closed in teardown.

## Dependencies and Integration Points

This integrates assumed-role policy enforcement with S3A status algorithms, globbing, recursive listing, MapReduce input listing, access-denied translation, object metadata/list metrics, and delete behavior.

## Risks and Edge Cases

S3A status resolution may use HEAD, LIST, or marker probes, so read denial does not uniformly fail every operation. A single bundled test reduces setup cost but one early failure skips later checks.

## Test Signals

Signals include allowed LIST-based directory operations, access denied for file HEAD/open/read, glob result counts, located-file status path sets, `InvalidInputException` text for missing and zero-match paths, and expected delete/FNFE outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestRestrictedReadAccess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ProgressCounter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ProgressCounter.java

## Purpose

`ProgressCounter.java` is a small `Progressable` test helper for asserting progress callback counts during S3A commit/upload operations.

## Important APIs, Types, and Functions

The class implements `Progressable`, stores an `AtomicLong count`, increments it in `progress()`, exposes `getCount()`, and provides `assertCount(String, int)`.

## Control Flow

Any caller passes the instance as a progress callback. Each callback increments the counter atomically. Tests query or assert the final count after upload attempts.

## State and Persistence Behavior

State is a thread-safe in-memory counter. It is not resettable except by creating a new instance.

## Dependencies and Integration Points

It integrates with Hadoop progress callback APIs and S3A commit operation tests, especially assumed-role commit restrictions.

## Risks and Edge Cases

Atomicity allows parallel callbacks, but assertions use integer expected values. If upload implementations change callback frequency, tests may need adjustment.

## Test Signals

Signals are exact progress counts, such as zero after a forbidden upload initiation and one-per-successful pending commit upload in commit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ProgressCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/RoleTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/RoleTestUtils.java

## Purpose

`RoleTestUtils.java` provides shared helpers and constants for S3A assumed-role authorization tests.

## Important APIs, Types, and Functions

It defines example role ARN, reusable deny/allow statements, `RESTRICTED_POLICY`, and helper methods `bindRolePolicy()`, `bindRolePolicyStatements()`, `assertDeleteForbidden()`, `assertTouchForbidden()`, `newAssumedRoleConfig()`, `forbidden()`, `probeForAssumedRoleARN()`, `assertCredentialsEqual()`, and `touchFiles()`.

## Control Flow

Policy helpers serialize `RoleModel.Policy` objects to JSON and bind them into `ASSUMED_ROLE_POLICY`. `newAssumedRoleConfig()` copies a source configuration, removes conflicting bucket/base overrides, sets `AssumedRoleCredentialProvider`, ARN, session name/duration, disables bucket probing, create-session, and filesystem caching.

## State and Persistence Behavior

The class is stateless except for a static `RoleModel` serializer. It mutates configurations passed by callers and creates S3 files through helper calls when requested.

## Dependencies and Integration Points

It integrates role model/policy DSL, S3A constants, delegation token options, S3 Express create-session toggles, filesystem caching, and test exception helpers.

## Risks and Edge Cases

Secret comparisons deliberately avoid printing secret keys. Configuration reset lists must remain aligned with S3A auth features to avoid inherited overrides invalidating role tests.

## Test Signals

Downstream signals are JSON policy text bound into configs, skipped tests when ARN is absent, expected access-denied exceptions, safe credential equality checks, and batches of touched test files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/RoleTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestIAMInstanceCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestIAMInstanceCredentialsProvider.java

## Purpose

`TestIAMInstanceCredentialsProvider.java` unit-tests S3A's IAM/container instance credentials provider without requiring the test host to be EC2 or a container.

## Important APIs, Types, and Functions

The class uses `IAMInstanceCredentialsProvider`, `AwsCredentials`, and `NoAwsCredentialsException`. It defines expected disabled-IMDS text and tests provider close and credential resolution.

## Control Flow

The close test constructs and closes the provider. The instantiation test tries `resolveCredentials()`: if credentials are available, it asserts a nonblank access key and repeats resolution; if not, it verifies fallback state and that the cause is either an `IOException` or an IMDS-disabled message.

## State and Persistence Behavior

Provider state is external-environment dependent: it may select container or EC2 metadata providers. No credentials are persisted by the test.

## Dependencies and Integration Points

This covers S3A's wrapper around AWS SDK metadata credential providers and environment/system-property handling for disabled IMDS resolution.

## Risks and Edge Cases

Outcome varies by host. The test intentionally accepts both in-EC2/container success and non-EC2 failure paths while still checking provider fallback semantics.

## Test Signals

Signals are successful close, nonblank access key when credentials exist, provider not using container provider on generic failure, and acceptable exception cause classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestIAMInstanceCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestMarshalledCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestMarshalledCredentials.java

## Purpose

`TestMarshalledCredentials.java` unit-tests serialization and provider behavior for S3A marshalled AWS credentials and encryption secrets.

## Important APIs, Types, and Functions

Setup creates `MarshalledCredentials` with access key, secret key, session token, role ARN, expiration, and bucket URI. Tests use `S3ATestUtils.roundTrip()`, `EncryptionSecrets`, `MarshalledCredentialProvider`, `MarshalledCredentials.CredentialTypeRequired`, and `NoAuthWithAWSException`.

## Control Flow

Round-trip tests serialize and deserialize full credentials, credentials without session data, and encryption secrets, then assert equality and individual fields. Provider tests construct a provider with session-only requirements and resolve AWS credentials, then construct a mismatched full-only provider and expect failure only when credentials are resolved.

## State and Persistence Behavior

State is in-memory serializable test data. No secret values are externalized beyond the test round-trip helper.

## Dependencies and Integration Points

This covers S3A credential marshalling, delegation encryption secret marshalling, AWS SDK v2 credential resolution, and provider validation of required credential type.

## Risks and Edge Cases

Credential mismatch should be lazy until `resolveCredentials()`, and null bucket URIs should fail fast. Tests must avoid leaking secret material in assertion output.

## Test Signals

Signals are object equality after round trips, exact field equality, successful session credential resolution, `NoAuthWithAWSException` for type mismatch, and `NullPointerException` for null URI construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestMarshalledCredentials.java -->
