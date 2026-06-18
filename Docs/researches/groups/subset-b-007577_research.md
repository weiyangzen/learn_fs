# Research report: subset-b-007577

This grouped report covers the S3A write, request API, audit, adapter, and authentication files assigned to `subset-b-007577`. Each section is source-path aligned for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperationHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperationHelper.java

## Purpose
`WriteOperationHelper` is the concrete internal S3A write facade behind `WriteOperations`. It centralizes low-level S3 write calls, multipart upload lifecycle calls, retry translation, audit span activation, and callback integration with `S3AFileSystem`.

## Important APIs and control flow
The class owns an `S3AFileSystem`, an `Invoker` configured with `S3ARetryPolicy`, the store bucket, statistics context, `RequestFactory`, and a current `AuditSpan`. `retry()` activates the span and delegates to `Invoker.retry`. `createPutObjectRequest()` builds put requests through `RequestFactory`. Multipart flow is split across `initiateMultiPartUpload()`, `newUploadPartRequestBuilder()`, `uploadPart()`, `completeMPUwithRetries()` or `commitUpload()`, and abort helpers. `finalizeMultipartUpload()` validates that at least one completed part exists, builds `CompleteMultipartUploadRequest`, and calls `WriteOperationHelperCallbacks.completeMultipartUpload()`. Direct PUT calls route through `owner.putObjectDirect()`. Revert deletes the committed object key through `owner.deleteObjectAtPath()`.

## State, dependencies, and integration
State is mostly immutable construction-time wiring, plus the mutable `auditSpan` reference that is activated and deactivated by `close()`. The class depends on AWS SDK v2 S3 request/response models, Hadoop retry annotations, `Invoker`, `RequestFactory`, `PutObjectOptions`, `DurationTrackerFactory`, and S3A callbacks. Integration points are `S3AFileSystem` owner methods, `WriteOperationHelperCallbacks` for upload part and complete MPU, and audit spans created through `AuditSpanSource`.

## Risks and test signals
Risk centers on idempotency flags for retried S3 mutations, completion with missing parts, abort semantics when uploads are already absent, and preserving audit span context around callbacks. Tests should cover retry callback increments, empty part-list rejection, abort-without-retry vs retry paths, request factory use, direct put duration tracking, and `close()` deactivating spans without swallowing write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperationHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperations.java

## Purpose
`WriteOperations` is the internal S3A interface for write-side store operations. It hides concrete `WriteOperationHelper` details from stream, commit, and multipart code while still exposing retry, audit span creation, direct PUT, MPU, abort, and write-counter operations.

## Important APIs and control flow
The interface extends `AuditSpanSource` and `Closeable`, so write clients can create spans and release helper-scoped span state. It defines generic `retry()`, `createPutObjectRequest()`, write success/failure hooks, `initiateMultiPartUpload()`, `completeMPUwithRetries()`, abort overloads, `abortMultipartUploadsUnderPath()`, `listMultipartUploads()`, `abortMultipartCommit()`, `newUploadPartRequestBuilder()`, `putObject()`, `revertCommit()`, `commitUpload()`, `uploadPart()`, `getConf()`, and `incrementWriteOperations()`.

## State, dependencies, and integration
There is no state in the interface, but its contract implies implementors must coordinate Hadoop `Configuration`, AWS SDK v2 S3 models, `PutObjectOptions`, `S3ADataBlocks.BlockUploadData`, `DurationTrackerFactory`, and `Invoker.Retried`. It is a Limited internal boundary used by S3A output streams and committer logic.

## Risks and test signals
The interface encodes retry expectations through annotations; implementation drift can cause unexpected duplicate writes or missing retry translation. Tests should use mocks/fakes implementing this interface to verify stream code calls MPU operations in the right order, propagates `IOException`, and closes helpers after completion or failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/AwsV1BindingSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/AwsV1BindingSupport.java

## Purpose
`AwsV1BindingSupport` isolates optional AWS SDK v1 credential-provider support. It is the sanctioned entry point for code that may need to instantiate v1 providers in an otherwise SDK v2 based S3A module.

## Important APIs and control flow
At class load, `SDK_V1_FOUND` is computed by attempting to load `com.amazonaws.auth.AWSCredentialsProvider` with this class loader. `isAwsV1SdkAvailable()` returns that cached probe result. `createAWSV1CredentialProvider()` rejects immediately with `InstantiationIOException.unavailable()` if v1 classes are missing; otherwise it delegates to `V1ToV2AwsCredentialProviderAdapter.create()`.

## State, dependencies, and integration
State is a static availability boolean. Dependencies include Hadoop `Configuration`, nullable filesystem URI, `InstantiationIOException`, and the adapter class. It is used by `CredentialProviderListFactory` after v2 reflection fails or when explicit v1 mappings require adaptation.

## Risks and test signals
Because availability is cached, classpath changes after class loading are not observed. Tests should cover v1 SDK absent/present behavior, exception kind on absence, and that callers never directly reference v1 classes outside the adapter package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/AwsV1BindingSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/V1ToV2AwsCredentialProviderAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/V1ToV2AwsCredentialProviderAdapter.java

## Purpose
This adapter wraps a v1 `com.amazonaws.auth.AWSCredentialsProvider` and exposes it as an AWS SDK v2 `AwsCredentialsProvider`, allowing legacy provider classes to be used by S3A during the SDK v2 migration.

## Important APIs and control flow
`resolveCredentials()` calls the wrapped v1 provider, converts v1 credentials to v2 credentials, and wraps v1 `SdkClientException` in Hadoop's `CredentialInitializationException`. `convertToV2Credentials()` maps session credentials to `AwsSessionCredentials`, anonymous credentials to v2 anonymous credentials, and other credentials to `AwsBasicCredentials`. `close()` propagates to `Closeable` or `AutoCloseable` providers. Static `create(conf, className, uri)` uses `S3AUtils.getInstanceFromReflection()` with constructors or `getInstance`.

## State, dependencies, and integration
The sole state is the wrapped v1 provider. The class depends on AWS SDK v1 and v2 auth APIs, `S3AUtils`, and `InstantiationIOException`. It is package-local behind `AwsV1BindingSupport` and used by credential-provider list construction.

## Risks and test signals
Credential conversion must preserve session tokens and anonymous semantics. Reflection errors need to retain the correct instantiation kind so v2/v1 fallback messages are accurate. Tests should cover conversion for basic, session, and anonymous credentials, close propagation, v1 exception wrapping, and reflection constructor precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/V1ToV2AwsCredentialProviderAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/package-info.java

## Purpose
This package descriptor documents the adapter package as the only permitted place for AWS SDK v1 credential-provider classes in S3A.

## Important APIs and control flow
There is no executable code. The package is marked `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`. The documentation states that instantiation must use reflection or be prepared for missing v1 SDK classes.

## State, dependencies, and integration
The package depends only on Hadoop audience/stability annotations. It integrates by setting architectural boundaries for `AwsV1BindingSupport` and `V1ToV2AwsCredentialProviderAdapter`.

## Risks and test signals
The risk is architectural leakage: new code importing v1 SDK classes outside this package would break deployments without the v1 SDK. Static analysis or dependency checks should enforce this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/PerformanceFlagEnum.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/PerformanceFlagEnum.java

## Purpose
`PerformanceFlagEnum` declares symbolic performance flags for S3A extension points and filesystem behavior toggles.

## Important APIs and control flow
The enum values are `Create`, `Delete`, `Mkdir`, and `Open`, with a note that additions should remain alphabetically ordered. There is no behavior beyond enum identity.

## State, dependencies, and integration
The enum is LimitedPrivate to S3A filesystem and extensions and unstable. It depends only on Hadoop annotations. Consumers can use it in `EnumSet` or configuration parsing for feature/performance modes.

## Risks and test signals
Risk is compatibility: renaming or reordering can affect serialized names or configuration parsing. Tests should verify parsing of all expected flag names and behavior when unknown flags are supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/PerformanceFlagEnum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/RequestFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/RequestFactory.java

## Purpose
`RequestFactory` is the S3A interface for constructing AWS SDK v2 S3 request builders. It is the audit-aware boundary through which S3A request creation should pass so requests can be prepared, annotated, and consistently configured.

## Important APIs and control flow
The interface exposes configuration accessors for encryption secrets, canned ACL, server-side encryption, content encoding, and storage class. It creates builders for copy, put object, directory marker, list multipart uploads, abort/start/complete MPU, head object/bucket, get object, upload part, list v1/v2, delete object, and bulk delete requests. Multipart start may throw `PathIOException` when MPU is disabled; upload part may throw when part numbers are invalid.

## State, dependencies, and integration
Implementations hold the mutable encryption-secret state and owner-specific request-preparation callback. Dependencies are AWS SDK v2 S3 model builders, `S3AEncryptionMethods`, delegation encryption secrets, `PutObjectOptions`, and Hadoop `PathIOException`. It integrates with write helpers, filesystem metadata paths, delete code, and auditing.

## Risks and test signals
The main risk is bypassing the factory, which loses audit headers or encryption/storage metadata. Builder reuse and mutable encryption settings also need care. Tests should assert every S3A request path uses this factory, encryption and ACL options are applied, MPU-disabled errors are raised, and delete/list/copy builders preserve key, bucket, metadata, and limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/RequestFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/UnsupportedRequestException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/UnsupportedRequestException.java

## Purpose
`UnsupportedRequestException` is a Hadoop `PathIOException` subclass used when S3A or its audit layer rejects an operation as unsupported for a specific path.

## Important APIs and control flow
It provides constructors for path plus cause, path plus error text, and path plus error text plus cause. There is no additional behavior.

## State, dependencies, and integration
The exception stores state inherited from `PathIOException`. It is used by `AuditIntegration.translateAuditException()` for `AuditOperationRejectedException` and may be used by request factory implementations.

## Risks and test signals
Tests should verify translated audit rejections preserve path, message, and cause. Since retry policy may treat exception types specially, changing its superclass would be a compatibility risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/UnsupportedRequestException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/package-info.java

## Purpose
This package descriptor defines `org.apache.hadoop.fs.s3a.api` as the home for interfaces implemented in S3A internals but exposed to S3A extensions without requiring access to `.impl` packages.

## Important APIs and control flow
There is no executable logic. The package is LimitedPrivate to extensions and unstable. The documentation explicitly warns that public extension points may change.

## State, dependencies, and integration
No state is present. Dependencies are Hadoop classification annotations. The package is an integration boundary for `RequestFactory`, performance flags, and request exceptions.

## Risks and test signals
Risk is accidental reliance by downstream extensions on unstable implementation details. Compatibility tests should focus on intended extension APIs rather than internal implementation classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSAuditEventCallbacks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSAuditEventCallbacks.java

## Purpose
`AWSAuditEventCallbacks` extends AWS SDK v2 `ExecutionInterceptor` with S3A audit-span identity and request-creation callbacks.

## Important APIs and control flow
Implementors provide `getSpanId()` and `getOperationName()`. The default `requestCreated(SdkRequest.Builder)` hook is invoked by `RequestFactoryImpl` after S3A creates a request; AWS-created requests do not trigger it. All `ExecutionInterceptor` lifecycle methods remain available through inheritance.

## State, dependencies, and integration
The interface has no state. It depends on AWS SDK `SdkRequest` and `ExecutionInterceptor`. It is implemented by audit managers and spans, allowing both manager-level dispatch and span-specific request annotation.

## Risks and test signals
Callbacks run inside request construction or SDK execution, so exceptions can affect IO paths. Tests should verify interrupts are preserved by implementations, request-created hooks do not perform remote work, and span IDs are non-empty and unique enough for correlation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSAuditEventCallbacks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSRequestAnalyzer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSRequestAnalyzer.java

## Purpose
`AWSRequestAnalyzer` converts AWS SDK S3 request objects into compact audit information: statistic verb, mutating/read flag, key or prefix, and approximate size/count.

## Important APIs and control flow
`analyze(SdkRequest)` uses an ordered `instanceof` chain for common S3 requests: MPU abort/complete/start/list/part, object delete/bulk delete/get/head/put, bucket-location probes, and list v1/v2. Unknown requests are treated as mutating with the Java class name. `isRequestNotAlwaysInSpan()` identifies SDK-generated or dependency-generated requests that may not be in a normal S3A span. `isRequestAuditedOutsideOfCurrentSpan()` checks AAL execution attributes. `isRequestMultipartIO()` identifies requests to reject when MPU is disabled. `RequestInfo` exposes verb, mutating flag, key, size, and string formatting.

## State, dependencies, and integration
Instances are stateless. The analyzer depends on AWS SDK S3 request classes, S3A statistics names, and AAL execution attribute constants. It is used by audit managers and logging auditors for log messages and policy decisions.

## Risks and test signals
The `GetObject` range-size parsing returns `end - start`, which may not match inclusive HTTP byte ranges. Unknown requests default to mutating, which is conservative but may overstate risk. Tests should cover every supported request type, empty bulk deletes, multipart predicates, AAL attribute detection, and malformed range headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSRequestAnalyzer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditFailureException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditFailureException.java

## Purpose
`AuditFailureException` is the base runtime/auth exception used when audit code fails or rejects a request.

## Important APIs and control flow
It extends `CredentialInitializationException`, with constructors for message and message plus cause. This places audit failures in an exception tree recognized by S3A exception translation.

## State, dependencies, and integration
State is inherited exception message/cause. It is thrown by audit spans and translated by `AuditIntegration` into `AccessDeniedException` or `UnsupportedRequestException`.

## Risks and test signals
Because it subclasses a credential initialization exception, retry and translation behavior depends on that hierarchy. Tests should verify audit exceptions raised inside AWS SDK interceptors are detected and translated consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditFailureException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditIntegration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditIntegration.java

## Purpose
`AuditIntegration` provides static glue for creating audit managers/auditors, attaching spans to AWS execution attributes, and translating audit-specific exceptions into Hadoop IO exceptions.

## Important APIs and control flow
`createAndStartAuditManager()` chooses `ActiveAuditManagerS3A` when auditing is enabled and `NoopAuditManagerS3A` otherwise, then initializes and starts the service. `createAndInitAuditor()` reflects the configured `OperationAuditor` class, defaulting to `LoggingAuditor`, and initializes it with `OperationAuditorOptions`. `retrieveAttachedSpan()` and `attachSpanToRequest()` read/write the internal execution attribute. `translateAuditException()` maps `AuditOperationRejectedException` to `UnsupportedRequestException`; other audit failures become `AccessDeniedException`. `maybeTranslateAuditException()` and `containsAuditException()` inspect direct and immediate-cause exceptions. `isRejectOutOfSpan()` reads the rejection flag.

## State, dependencies, and integration
The class is stateless. It depends on Hadoop configuration/service classes, AWS execution attributes, audit implementations, `IOStatisticsStore`, and `S3AInternalAuditConstants`. It is used during filesystem initialization and exception handling.

## Risks and test signals
Reflection failures must report the configured key/class clearly. Cause scanning is shallow and may miss deeply nested audit failures. Tests should cover enabled/disabled manager creation, custom auditor construction, span attribute round trip, exception translation paths, and reject-out-of-span configuration defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditManagerS3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditManagerS3A.java

## Purpose
`AuditManagerS3A` is the S3A service interface that binds audit spans to the AWS SDK and active thread context.

## Important APIs and control flow
The interface extends `Service`, `AuditSpanSource<AuditSpanS3A>`, `AWSAuditEventCallbacks`, and `ActiveThreadSpanSource<AuditSpanS3A>`. It exposes `getAuditor()`, `createExecutionInterceptors()`, `createTransferListener()`, `checkAccess()`, and `setAuditFlags()`. Implementations create SDK interceptors and transfer listeners that preserve audit context across AWS request execution.

## State, dependencies, and integration
No interface state exists. Dependencies include AWS SDK execution interceptors, transfer-manager progress listeners, Hadoop `Path`, `FsAction`, `S3AFileStatus`, and `AuditorFlags`. It integrates with S3A filesystem initialization, access checks, request factory callbacks, and SDK client construction.

## Risks and test signals
Incorrect interceptor ordering or transfer listener behavior can lose span context for multipart/copy operations. Tests should verify active span propagation, soft access checks, flags flowing to auditors, and mutable interceptor lists accepting configured extras.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditManagerS3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditOperationRejectedException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditOperationRejectedException.java

## Purpose
`AuditOperationRejectedException` marks an audit failure where the auditor deliberately rejects an operation as forbidden or unavailable.

## Important APIs and control flow
It extends `AuditFailureException` and provides message and message-plus-cause constructors. `AuditIntegration.translateAuditException()` treats this subclass specially and emits `UnsupportedRequestException`.

## State, dependencies, and integration
State is inherited exception data. It is used by `LoggingAuditor` when multipart requests are attempted while multipart uploads are disabled.

## Risks and test signals
Tests should ensure rejected audit operations translate to unsupported-request IO errors, not generic access-denied errors, and that rejected SDK interceptor exceptions increment audit failure counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditOperationRejectedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditSpanS3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditSpanS3A.java

## Purpose
`AuditSpanS3A` is the S3A-specific audit span interface, combining generic Hadoop `AuditSpan` lifecycle with AWS SDK audit callbacks.

## Important APIs and control flow
It declares no new methods, but implementors inherit span activation/deactivation and all `AWSAuditEventCallbacks`/`ExecutionInterceptor` hooks.

## State, dependencies, and integration
Implementing classes carry span identifiers, operation names, timestamps, referrer state, or delegate spans. It is the common type used by audit managers, request factory callbacks, execution attributes, and active-thread span sources.

## Risks and test signals
Because the interface conflates span lifecycle and AWS callbacks, implementations must be cheap and safe during SDK execution. Tests should cover activation/deactivation validity and no-op/default behavior for unused interceptor methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditSpanS3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditorFlags.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditorFlags.java

## Purpose
`AuditorFlags` defines dynamic flags that can be passed into audit managers and auditors.

## Important APIs and control flow
The only current value is `PermitOutOfBandOperations`, which tells auditors to allow operations outside an active span.

## State, dependencies, and integration
The enum has no state. It is consumed through `EnumSet<AuditorFlags>` by `AuditManagerS3A`, `OperationAuditor`, and `AbstractOperationAuditor`.

## Risks and test signals
Flag semantics override configuration in `AbstractOperationAuditor`. Tests should verify that setting `PermitOutOfBandOperations` disables reject-out-of-span behavior and that empty or missing flag sets do not cause null-pointer failures in auditor code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditorFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditor.java

## Purpose
`OperationAuditor` is the plugin interface for S3A audit services that create spans, expose IO statistics, and optionally enforce access checks.

## Important APIs and control flow
It extends `Service`, `IOStatisticsSource`, and `AuditSpanSource<AuditSpanS3A>`. Implementors initialize from `OperationAuditorOptions`, receive updated `AuditorFlags`, provide an unbonded span, produce an auditor ID, and may override `checkAccess()` and `noteSpanReferenceLost()`. The default access check permits access.

## State, dependencies, and integration
Implementations usually hold configuration, IO statistics, flags, span ID sources, and unbonded span state. It integrates through `AuditIntegration.createAndInitAuditor()` and `ActiveAuditManagerS3A`.

## Risks and test signals
Third-party auditors can affect filesystem operations if callbacks throw. Tests should cover lifecycle order, access-check behavior, IO statistics availability, and weak-reference span-loss notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditorOptions.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditorOptions.java

## Purpose
`OperationAuditorOptions` is a small builder-style value object used to initialize audit plugins without freezing constructor signatures.

## Important APIs and control flow
`builder()` returns a new mutable options object. `withConfiguration()` and `withIoStatisticsStore()` set fields and return `this`; getters expose both values.

## State, dependencies, and integration
State consists of a Hadoop `Configuration` and an `IOStatisticsStore`. It is created by `ActiveAuditManagerS3A` and passed to `OperationAuditor.init()`.

## Risks and test signals
The builder does not validate missing fields; `AbstractOperationAuditor` requires a non-null statistics store. Tests should verify required fields are set during manager initialization and external auditors remain binary-compatible as options are extended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditorOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3AAuditConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3AAuditConstants.java

## Purpose
`S3AAuditConstants` centralizes public/limited-private configuration keys and symbolic names for S3A auditing.

## Important APIs and control flow
Constants include `AUDIT_ENABLED`, default enabled state, audit service class key and default class names, deprecated v1 request handler key, v2 execution interceptor key, reject-out-of-span key, referrer header enable/filter keys, `INITIALIZE_SPAN`, `OUTSIDE_SPAN`, and the `UNAUDITED_OPERATION` log marker.

## State, dependencies, and integration
The class is a static constant holder with a private constructor. It is consumed by `AuditIntegration`, `ActiveAuditManagerS3A`, `LoggingAuditor`, and configuration docs/tests.

## Risks and test signals
Configuration-key changes are user-visible. Tests should validate defaults, deprecated handler warnings, referrer filtering, and reject-out-of-span behavior driven by these keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3AAuditConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogParser.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogParser.java

## Purpose
`S3LogParser` provides a named regular expression and ordered group list for parsing AWS S3 server access log lines.

## Important APIs and control flow
Private helpers build named regex groups for simple, date/time, number, and quoted fields. Public constants name every log field from owner through TLS and tail. `LOG_ENTRY_REGEXP` concatenates named groups in AWS log order, `AWS_LOG_REGEXP_GROUPS` exposes an immutable ordered list, and `LOG_ENTRY_PATTERN` is the compiled pattern.

## State, dependencies, and integration
The class is stateless apart from static constants. It depends on Java regex and collections and Hadoop classification annotations. It is intended for diagnostics/tests that need to parse S3 logs and correlate audit referrer data.

## Risks and test signals
S3 log formats can evolve; the tail group is designed as forward-compatible catch-all. Tests should parse representative log lines with quoted user-agent/referrer values, missing fields represented as `-`, unexpected tails, and group-order assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogVerbs.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogVerbs.java

## Purpose
`S3LogVerbs` names common operation strings seen in S3 server access logs.

## Important APIs and control flow
The final class exposes constants for delete, copy, bulk delete, get, head, ACL/logging/tagging policy operations, list, multipart start/part/complete/list/abort, put, public-access-block, and lifecycle expiration. It has no runtime behavior.

## State, dependencies, and integration
There is no state. These constants support audit/log parsing code and tests that compare parsed S3 log verbs without embedding string literals.

## Risks and test signals
AWS may add or rename log operation strings. Tests should check constants used in parser/audit tests match expected S3 log samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogVerbs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractAuditSpanImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractAuditSpanImpl.java

## Purpose
`AbstractAuditSpanImpl` is the base class for S3A audit span implementations, providing immutable span ID, timestamp, and operation name handling.

## Important APIs and control flow
Constructors set the span ID, timestamp (defaulting to `Time.now()`), and operation name. `getSpanId()`, `getOperationName()`, and `getTimestamp()` expose these values. Default `activate()` returns `this`. `close()` is final and delegates to `deactivate()`, enforcing try-with-resources semantics through the `AuditSpan` lifecycle.

## State, dependencies, and integration
State is immutable per span. Dependencies are `AuditSpanS3A`, Hadoop `AuditSpan`, and `Time`. It is extended by `LoggingAuditor.LoggingAuditSpan`, `WarningSpan`, `NoopSpan`, and `ActiveAuditManagerS3A.WrappingAuditSpan`.

## Risks and test signals
Subclasses must implement valid deactivation behavior because `close()` is final. Tests should verify timestamps are set, null span IDs fail, and try-with-resources calls subclass `deactivate()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractAuditSpanImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractOperationAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractOperationAuditor.java

## Purpose
`AbstractOperationAuditor` is the base service implementation for audit plugins. It manages initialization options, IO statistics, auditor IDs, span ID generation, and out-of-span rejection flags.

## Important APIs and control flow
`init(OperationAuditorOptions)` saves options/statistics and calls service `init(Configuration)`. `serviceInit()` reads reject-out-of-span configuration. `createSpanID()` combines the auditor UUID with a static counter. `setAuditFlags()` stores flags and calls `auditorFlagsChanged()`, which disables out-of-span rejection when `PermitOutOfBandOperations` is present.

## State, dependencies, and integration
State includes `IOStatisticsStore`, options, `AtomicBoolean rejectOutOfSpan`, a UUID-backed auditor ID, and current flags. It depends on `AuditIntegration`, `AuditorFlags`, `OperationAuditor`, and Hadoop service/config classes. Concrete implementations include `LoggingAuditor` and `NoopAuditor`.

## Risks and test signals
`auditorFlagsChanged()` assumes a non-null `EnumSet`; callers should not pass null. Static span counter is process-wide, which is fine for uniqueness but affects deterministic tests. Tests should cover reject flag defaults, flag override, ID uniqueness, and missing statistics validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/AbstractOperationAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/ActiveAuditManagerS3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/ActiveAuditManagerS3A.java

## Purpose
`ActiveAuditManagerS3A` is the active audit manager service. It creates the configured auditor, wraps auditor spans, tracks the active span per thread, attaches spans to AWS SDK execution attributes, and forwards SDK interceptor callbacks to the correct span.

## Important APIs and control flow
Lifecycle: `serviceInit()` builds `OperationAuditorOptions`, creates the configured auditor, and adds it as a child service. `serviceStart()` wraps the auditor's unbonded span. `createSpan()` requires the manager to be started, increments the audit span creation statistic, asks the auditor for a span, wraps it, and makes it current for the thread. `createExecutionInterceptors()` returns this manager plus any configured v2 interceptors, warning about deprecated v1 handlers. `beforeExecution()` increments request execution statistics, attaches the active span to `ExecutionAttributes`, and delegates. Later callbacks call `extractAndActivateSpanFromRequest()` to recover the attached span, switch thread context if it is a wrapper, and delegate to the span. `WrappingAuditSpan` forwards all AWS callbacks to the inner span and removes/prunes thread-map entries on deactivation.

## State, dependencies, and integration
State includes the configured `OperationAuditor`, `AWSRequestAnalyzer`, unbonded wrapper span, `WeakReferenceThreadMap`, prune countdown, and `IOStatisticsStore`. It integrates with AWS SDK `ExecutionInterceptor`, transfer-manager listeners, S3A statistics, audit constants, and configured external interceptors.

## Risks and test signals
Weak-reference tracking can lose spans if callers drop references early; `noteSpanReferenceLost()` is the signal. Missing or non-wrapper execution attributes fall back to thread span and log warnings. Tests should cover lifecycle ordering, span attach/retrieve across every interceptor callback, transfer listener context restoration, pruning, configured interceptor construction, audit failure counter increments, and disabled/deprecated handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/ActiveAuditManagerS3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/LoggingAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/LoggingAuditor.java

## Purpose
`LoggingAuditor` is the default audit plugin. It creates spans that log request execution and build an HTTP referrer audit header containing filesystem, user, job, span, path, thread, timestamp, and evaluated audit context fields.

## Important APIs and control flow
The constructor records filesystem ID and current user principal. `serviceInit()` adds job ID when present, reads referrer-header enable/filter settings, creates the `WarningSpan` for outside-span operations, and records whether multipart uploads are enabled. `createSpan()` builds and starts a `LoggingAuditSpan`. In `LoggingAuditSpan.modifyHttpRequest()`, the span may override span ID/operation from AAL execution attributes, attach GET range and delete-key-count attributes, build and store `lastHeader`, append the HTTP referrer header if enabled, debug-log analyzed request details, and reject multipart requests if MPU is disabled. `onExecutionFailure()` maps HTTP status codes to statistics. `WarningSpan` logs outside-span request creation/execution and can throw if rejection is enabled.

## State, dependencies, and integration
State includes global audit attributes, referrer filtering, header enablement, volatile `lastHeader` for tests, warning span, and MPU-enabled flag. Dependencies include AWS SDK request/http/interceptor APIs, Hadoop audit context/referrer builders, user identity, S3A constants, statistics mapping, and `AWSRequestAnalyzer`.

## Risks and test signals
The referrer can expose context unless filters are correct. Header mutation must not break signing, and AAL overrides mutate the span's header builder for that request path. Tests should verify header contents/filtering, disabled-header behavior, `lastHeader`, delete count/range attributes, outside-span rejection policy, multipart-disabled rejection, status-code statistic increments, and AAL span/operation override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/LoggingAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditManagerS3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditManagerS3A.java

## Purpose
`NoopAuditManagerS3A` is the no-op audit manager used before active audit setup, when auditing is disabled, or in tests.

## Important APIs and control flow
It implements `AuditManagerS3A` and `NoopSpan.SpanActivationCallbacks`. Initialization creates a child `NoopAuditor` with an empty IO statistics store. `getActiveAuditSpan()` returns `NoopSpan.INSTANCE`. `createSpan()` returns a no-op span. `createExecutionInterceptors()` returns an empty list and `createTransferListener()` returns an empty listener. `checkAccess()` delegates to the no-op auditor. Activation callback methods are no-ops except deactivation reactivates the unbonded span.

## State, dependencies, and integration
State includes a static started `NoopAuditor`, an instance auditor reference, and a UUID ID. It integrates wherever an `AuditManagerS3A` is required without adding SDK interceptors.

## Risks and test signals
One subtlety is `getAuditor()` returns the static auditor while `serviceInit()` adds a new child auditor, so tests should verify expected lifecycle and identity. Disabled auditing tests should assert no execution interceptors are installed and operations still get harmless spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditManagerS3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditor.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditor.java

## Purpose
`NoopAuditor` is an `OperationAuditor` implementation that creates `NoopSpan` instances and performs no audit logging or enforcement.

## Important APIs and control flow
Constructors create an unbonded no-op span and optionally retain activation callbacks. `createSpan()` returns a new `NoopSpan` with a generated span ID and paths. `getUnbondedSpan()` returns the unbonded span. `createAndStartNoopAuditor()` builds options with an empty IO statistics store, initializes, starts, and returns a no-op auditor.

## State, dependencies, and integration
State is the unbonded span and optional callbacks. It extends `AbstractOperationAuditor`, so it still has service lifecycle, IDs, flags, and IO statistics. It is used by `NoopAuditManagerS3A` and tests.

## Risks and test signals
Even no-op spans should have valid IDs when created through the auditor. Tests should verify activation callbacks fire, unbonded span is stable, and lifecycle methods match `OperationAuditor` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopAuditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopSpan.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopSpan.java

## Purpose
`NoopSpan` is a minimal `AuditSpanS3A` implementation with no direct audit side effects except optional activation/deactivation callbacks.

## Important APIs and control flow
The protected constructor stores span ID, operation name, paths, and callbacks. The singleton `INSTANCE` is a default no-op span. `activate()` and `deactivate()` notify callbacks when present and otherwise do nothing. `toString()` includes id, operation name, and paths.

## State, dependencies, and integration
State is immutable span metadata plus callback reference. It extends `AbstractAuditSpanImpl` and is produced by `NoopAuditor` and `NoopAuditManagerS3A`.

## Risks and test signals
The singleton has an empty span ID and `no-op` operation, so code requiring unique IDs should use auditor-created spans instead. Tests should cover callback invocation and harmless reuse of `INSTANCE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/NoopSpan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/S3AInternalAuditConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/S3AInternalAuditConstants.java

## Purpose
`S3AInternalAuditConstants` defines internal-only audit constants.

## Important APIs and control flow
The key constant is `AUDIT_SPAN_EXECUTION_ATTRIBUTE`, an AWS SDK `ExecutionAttribute<AuditSpanS3A>` used to attach a span to one request/response execution.

## State, dependencies, and integration
The class is a static holder. It depends on AWS SDK `ExecutionAttribute` and `AuditSpanS3A`. It is used by `AuditIntegration` and `ActiveAuditManagerS3A`.

## Risks and test signals
This attribute name is the cross-callback binding key. Tests should verify round-trip attachment and that external code does not rely on the internal constant as a stable public API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/S3AInternalAuditConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/package-info.java

## Purpose
This package descriptor marks `org.apache.hadoop.fs.s3a.audit.impl` as the internal implementation package for S3A auditing.

## Important APIs and control flow
There is no executable code. The package is annotated private and unstable, and documentation states it is not for extension use.

## State, dependencies, and integration
No state is present. Dependencies are Hadoop audience/stability annotations. Public extension contracts should live in `org.apache.hadoop.fs.s3a.audit`, not here.

## Risks and test signals
Downstream code depending on this package is brittle. Compatibility checks should focus on public audit interfaces while internal tests can freely exercise implementation details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/package-info.java

## Purpose
This package descriptor documents S3A auditing and tracing support as an extension-facing but unstable API.

## Important APIs and control flow
It states that audit services are instantiated during S3A filesystem initialization, selected by `S3AAuditConstants.AUDIT_SERVICE_CLASSNAME`, and must implement `OperationAuditor` to provide audit spans for public filesystem calls and related operations.

## State, dependencies, and integration
No runtime state exists. The package depends on Hadoop classification annotations and documents integration with `AuditSpan`, `OperationAuditor`, and S3A configuration.

## Risks and test signals
The package explicitly warns of instability as audit/tracing evolves. Extension compatibility tests should instantiate configured auditors and validate lifecycle and span creation rather than relying on implementation packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractAWSCredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractAWSCredentialProvider.java

## Purpose
`AbstractAWSCredentialProvider` is a base class for S3A credential providers that need the filesystem URI and Hadoop configuration in their constructor.

## Important APIs and control flow
The constructor stores nullable `URI` and `Configuration`. `getConf()` and `getUri()` expose them. The class implements AWS SDK v2 `AwsCredentialsProvider` but leaves `resolveCredentials()` to subclasses.

## State, dependencies, and integration
State is immutable URI/configuration references. Subclasses include profile and session credential providers. It integrates with `S3AUtils.getInstanceFromReflection()` constructor selection used by credential-provider factories.

## Risks and test signals
The configuration is stored by reference, not copied, so later mutations can be visible to subclasses. Tests should verify reflection can instantiate URI+Configuration providers and that null URIs are tolerated when documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractAWSCredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractSessionCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractSessionCredentialsProvider.java

## Purpose
`AbstractSessionCredentialsProvider` is a lazy, caching base class for providers that create full or session AWS credentials from Hadoop configuration.

## Important APIs and control flow
`init()` is synchronized and one-shot: if not initialized, it calls subclass `createCredentials(Configuration)` through `Invoker.once()`, stores credentials or initialization exception, and marks initialized in `finally`. `resolveCredentials()` triggers initialization, unwraps AWS SDK exceptions when possible, wraps other IO failures in `CredentialInitializationException`, and rejects null credentials. `hasCredentials()` and `getInitializationException()` expose test state. The nested `NoCredentials` class returns null keys to mean no credentials offered.

## State, dependencies, and integration
State includes volatile credentials, an `AtomicBoolean initialized`, and volatile initialization exception. It depends on AWS SDK `AwsCredentials`, Hadoop retry utilities, and `CredentialInitializationException`. It is extended by `MarshalledCredentialProvider` and similar session providers.

## Risks and test signals
Initialization is marked attempted even when credential creation fails; subsequent calls rethrow stored failure rather than retrying. Tests should cover lazy init, failure caching, SDK exception unwrapping, null credential rejection, and concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractSessionCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AssumedRoleCredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AssumedRoleCredentialProvider.java

## Purpose
`AssumedRoleCredentialProvider` obtains AWS credentials by assuming a configured IAM role through STS, using a separate credential-provider chain for the STS call.

## Important APIs and control flow
The constructor requires `fs.s3a.assumed.role.arn`, builds the base credential list from `ASSUMED_ROLE_CREDENTIALS_PROVIDER` while forbidding itself, derives or reads a sanitized session name, reads duration, optional scope-down policy, external ID, STS endpoint, and region, builds an `StsClient`, creates `StsAssumeRoleCredentialsProvider`, creates an `Invoker`, and calls `resolveCredentials()` to fail fast. `resolveCredentials()` retries raw STS provider resolution and wraps unexpected IO in `CredentialInitializationException`. `close()` closes the STS provider, base credential list, and STS client. `sanitize()` replaces characters outside AWS role-session safe set with `-`.

## State, dependencies, and integration
State includes role ARN, session name/duration, base credential list, STS client/provider, and retry invoker. Dependencies include AWS SDK STS/auth, S3A constants, `CredentialProviderListFactory`, `STSClientFactory`, `S3ARetryPolicy`, and UGI. It integrates as a credential provider class selectable in S3A configuration.

## Risks and test signals
Misconfigured role ARN, endpoint/region, forbidden recursive provider chains, and STS throttling are key risks. Tests should cover missing ARN, provider-list construction, session-name sanitization, policy/external ID propagation, fail-fast behavior, retry logging, and close propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AssumedRoleCredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AwsSignerInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AwsSignerInitializer.java

## Purpose
`AwsSignerInitializer` is an extension interface for custom AWS signer implementations that need per-store registration and unregistration hooks.

## Important APIs and control flow
`registerStore()` and `unregisterStore()` receive bucket name, store configuration, delegation-token provider, and store UGI. Implementations can maintain external signer state keyed by store identity.

## State, dependencies, and integration
The interface has no state. It depends on Hadoop `Configuration`, S3A filesystem concepts, delegation-token provider, and UGI. `CustomSdkSigner.Initializer` is a simple test implementation.

## Risks and test signals
Implementations must avoid leaking per-store state and must handle unregister even after partial initialization. Tests should verify custom signer initialization hooks are called with the expected bucket/config/user and that unregister runs on filesystem close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AwsSignerInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CredentialProviderListFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CredentialProviderListFactory.java

## Purpose
`CredentialProviderListFactory` constructs ordered S3A AWS credential-provider lists from configuration, default providers, explicit class mappings, and legacy v1-to-v2 mappings.

## Important APIs and control flow
`createAWSCredentialProviderList()` builds the standard chain: environment variables, `IAMInstanceCredentialsProvider`, simple credentials, and temporary credentials. `buildAWSProviderList()` loads configured class names or defaults, applies built-in v1 mappings and user-defined `AWS_CREDENTIALS_PROVIDER_MAPPING`, rejects forbidden class names after mapping, and tries to instantiate v2 providers by reflection. If v2 instantiation fails because the class is not a v2 provider and the v1 SDK is present, it attempts v1 instantiation through `AwsV1BindingSupport`; otherwise it rethrows. `loadAWSProviderClasses()` returns defaults when the configuration key is empty.

## State, dependencies, and integration
State is static maps and logging helpers. Dependencies include AWS SDK v2 credential providers, S3A credential-list classes, `S3AUtils`, `InstantiationIOException`, `AwsV1BindingSupport`, and Hadoop configuration. It integrates with filesystem initialization and assumed-role provider construction.

## Risks and test signals
Provider ordering is security-sensitive and behavior-sensitive. V1 fallback must distinguish "not implementation" from real construction errors. Tests should cover default chain, explicit empty/configured lists, user mappings, built-in v1 mappings, forbidden providers, v1 SDK absent/present fallback, and close behavior of the returned list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CredentialProviderListFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomHttpSigner.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomHttpSigner.java

## Purpose
`CustomHttpSigner` is a production test-support signer for the AWS SDK HTTP signer plugin path. It delegates to the standard AWS V4 HTTP signer while logging requests at TRACE.

## Important APIs and control flow
The constructor creates an `AwsV4HttpSigner` delegate. `sign()` logs the synchronous request and returns `delegateSigner.sign(request)`. `signAsync()` logs the async request and returns `delegateSigner.signAsync(request)`.

## State, dependencies, and integration
State is the delegate signer. Dependencies are AWS SDK HTTP auth signer interfaces and `AwsCredentialsIdentity`. It is enabled through S3A HTTP signer configuration for plugin mechanism tests.

## Risks and test signals
TRACE logging should not expose sensitive headers in normal log configurations. Tests should verify synchronous and async signing delegate correctly and that configuration can instantiate the class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomHttpSigner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomSdkSigner.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomSdkSigner.java

## Purpose
`CustomSdkSigner` is a test-support AWS SDK signer used to validate S3A custom signer configuration and special service signing behavior.

## Important APIs and control flow
The constructor increments an instantiation counter. `sign()` increments an invocation counter, parses the host, and delegates to `Aws4Signer` for KMS hosts or `AwsS3V4Signer` for S3 hosts. `parseBucketFromHost()` extracts the bucket-like prefix and rebuilds S3 access point/outposts/object-lambda hosts into an ARN form. Static getters expose counters and `description()`. Nested `Initializer` implements `AwsSignerInitializer` with debug logging for register/unregister.

## State, dependencies, and integration
State includes static counters and per-instance S3/AWS4 signer delegates. Dependencies include AWS SDK signers, ARN builder, execution attributes, Hadoop configuration, delegation-token provider, and UGI. It integrates with `fs.s3a.custom.signers` and signing algorithm configuration.

## Risks and test signals
`parseBucketFromHost()` assumes dotted host structure and does not support path-style access, so malformed hosts can fail. Tests should cover S3, KMS, access point/outposts/object-lambda hosts, counter increments, initializer calls, and client-side encryption/KMS signing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomSdkSigner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/IAMInstanceCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/IAMInstanceCredentialsProvider.java

## Purpose
`IAMInstanceCredentialsProvider` obtains credentials from AWS container metadata first and falls back to EC2 instance profile metadata. It is S3A's v2 replacement for legacy EC2/container provider wrappers.

## Important APIs and control flow
The constructor creates a `ContainerCredentialsProvider` with async refresh enabled. `resolveCredentials()` calls synchronized `getCredentials()` and converts `SdkClientException` into `NoAwsCredentialsException`, extracting embedded IO exceptions when available. `getCredentials()` first tries the current provider. On first failure from the container provider, it closes it, switches to `InstanceProfileCredentialsProvider` with async refresh and a five-minute stale time, and retries. Subsequent instance-profile failures are rethrown. `close()` closes the active HTTP credentials provider.

## State, dependencies, and integration
State is the mutable active `HttpCredentialsProvider` and boolean indicating whether it is still using container credentials. Dependencies include AWS SDK container/instance providers, S3A error translation, and auth exceptions. It is part of the standard credential provider chain.

## Risks and test signals
Fallback is one-way; a transient container metadata failure switches permanently to instance profile for that provider instance. Tests should cover container success, container failure then instance success, both failure with `NoAwsCredentialsException`, IO cause extraction, async refresh configuration, and close after fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/IAMInstanceCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialBinding.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialBinding.java

## Purpose
`MarshalledCredentialBinding` bridges AWS SDK credential objects and S3A's SDK-free `MarshalledCredentials` representation used in delegation tokens and credential propagation.

## Important APIs and control flow
`fromSTSCredentials()` copies STS access key, secret, session token, and expiration into `MarshalledCredentials`. `fromAWSCredentials()` copies v2 session credentials. `fromEnvironment()` reads AWS environment variable names into possibly incomplete credentials. `fromFileSystem()` loads access/secret/session values from S3A configuration and Hadoop credential providers after excluding incompatible providers. `toAWSCredentials()` validates required credential type, throws `NoAwsCredentialsException` for empty credentials, throws `NoAuthWithAWSException` for invalid shape, and returns either `AwsSessionCredentials` or `AwsBasicCredentials`. `requestSessionCredentials()` builds an STS client and requests temporary credentials with retry translation.

## State, dependencies, and integration
The class is stateless. It depends on AWS SDK auth/STS classes, `MarshalledCredentials`, S3A constants, `STSClientFactory`, `Invoker`, and Hadoop provider utilities. It integrates with delegation token bindings, session credential providers, and tests that need marshalled credentials without loading AWS SDK in token identifier classes.

## Risks and test signals
Keeping AWS SDK references out of `MarshalledCredentials` is intentional; moving conversion there would hurt deserialization. Tests should cover full/session/empty validation, environment loading, filesystem credential-provider lookup, STS region error logging, expiration conversion, and exception types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialBinding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialProvider.java

## Purpose
`MarshalledCredentialProvider` is an AWS credentials provider backed by a prebuilt `MarshalledCredentials` object, primarily for delegation-token bindings rather than direct user configuration.

## Important APIs and control flow
The constructor requires a component name, non-null filesystem URI, configuration, marshalled credentials, and required credential type. It extends `AbstractSessionCredentialsProvider`; `createCredentials()` converts the stored marshalled credentials through `MarshalledCredentialBinding.toAWSCredentials()`.

## State, dependencies, and integration
State includes the marshalled credentials, required type, and component name. It depends on `AbstractSessionCredentialsProvider`, `MarshalledCredentialBinding`, and S3A credential exceptions. It integrates with delegation token providers that need to expose token credentials to AWS SDK clients.

## Risks and test signals
The constructor deliberately rejects null URI to prevent accidental direct configuration misuse. Tests should cover full/session credential conversion, type mismatch errors, empty credential errors, lazy initialization inherited from the base class, and message component labeling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentials.java

## Purpose
`MarshalledCredentials` is a serializable, Hadoop `Writable` container for AWS access key, secret key, optional session token, role ARN, and expiration. It intentionally avoids AWS SDK types so token identifiers can be deserialized without AWS SDK classes.

## Important APIs and control flow
Constructors normalize null session token to empty. Getters/setters maintain non-null fields. `isEmpty()` requires both access and secret to be non-empty. `isValid(CredentialTypeRequired)` validates empty/full/session/any shapes. `write()` validates fields and serializes strings plus expiration. `readFields()` reads bounded-length strings and expiration. `validate()` throws `DelegationTokenIOException` on invalid shape. `setSecretsInConfiguration()` writes secrets into a Hadoop configuration. `toString()` avoids printing secrets while reporting type, validity, expiration, and role ARN.

## State, dependencies, and integration
State is the credential fields and expiration timestamp. Dependencies are Hadoop `Writable`, `Text`, `Configuration`, S3A constants/utilities, and delegation token IO exceptions. It is used by `MarshalledCredentialBinding`, delegation token code, and providers.

## Risks and test signals
This class handles secrets and must not leak values via `toString()`, logs, equality failures, or exception messages. Tests should cover serialization bounds, null rejection, all credential-type validations, empty semantics, expiration datetime conversion, configuration patching, and secret-free string output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAuthWithAWSException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAuthWithAWSException.java

## Purpose
`NoAuthWithAWSException` represents authentication failures that S3A retry policy should fail fast rather than repeatedly retrying credential acquisition.

## Important APIs and control flow
It extends `CredentialInitializationException` and provides message and message-plus-cause constructors. No additional behavior is added.

## State, dependencies, and integration
State is inherited exception message/cause. It is thrown by marshalled credential binding and extended by `NoAwsCredentialsException`.

## Risks and test signals
Retry policy behavior depends on this exception type. Tests should verify auth failures bypass unnecessary retries and translate into useful user-facing diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAuthWithAWSException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAwsCredentialsException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAwsCredentialsException.java

## Purpose
`NoAwsCredentialsException` is a specific no-credentials-found exception that subclasses `NoAuthWithAWSException` for retry and diagnostic handling.

## Important APIs and control flow
Constructors combine the credential provider name with a supplied or default message and optional cause. The default message constant is `No AWS Credentials`.

## State, dependencies, and integration
State is inherited exception data. It is thrown by IAM metadata credential resolution and marshalled credential conversion when no usable credentials are present.

## Risks and test signals
Provider names are part of the message, so tests should assert diagnostics identify the failing provider. Retry tests should ensure this exception is treated as non-recoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAwsCredentialsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/ProfileAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/ProfileAWSCredentialsProvider.java

## Purpose
`ProfileAWSCredentialsProvider` loads AWS credentials from an AWS shared credentials profile file using S3A configuration keys or AWS environment variables.

## Important APIs and control flow
`getCredentialsPath()` checks `fs.s3a.auth.profile.file`, then `AWS_SHARED_CREDENTIALS_FILE`, then defaults to `$HOME/.aws/credentials`. `getCredentialsName()` checks `fs.s3a.auth.profile.name`, then `AWS_PROFILE`, then `default`. The constructor builds a v2 `ProfileCredentialsProvider` with the selected profile file and name. `resolveCredentials()` delegates directly to that provider.

## State, dependencies, and integration
State is the wrapped `ProfileCredentialsProvider`; inherited state includes URI and configuration. Dependencies include AWS SDK profile credentials/profile file APIs, Apache Commons `SystemUtils`, and Hadoop annotations/configuration. It can be named in S3A credential-provider configuration.

## Risks and test signals
Profile files may be missing, malformed, or environment-dependent. Tests should cover configuration overriding environment, environment fallback, default path/name selection, profile resolution errors, and behavior on non-default filesystems/path formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/ProfileAWSCredentialsProvider.java -->
