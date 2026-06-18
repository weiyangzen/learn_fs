# subset-b-007580 Research

Grouped source research for Hadoop S3A implementation operation scaffolding, bulk/delete flows, client-side encryption, change tracking, metadata headers, client management, and networking helpers. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java

## Purpose

`AbstractStoreOperation` is the small base class for S3A store-side operation objects. It gives operations a common `StoreContext` reference and captures the active `AuditSpan` at construction time so later worker-thread execution can reactivate the same audit context.

## Important APIs, Types, and Functions

The class exposes protected constructors accepting a nullable `StoreContext`, optionally with an explicit `AuditSpan`. Public accessors are `getStoreContext()`, `getAuditSpan()`, and `activateAuditSpan()`.

## Control Flow

Construction pulls `storeContext.getActiveAuditSpan()` when a context is supplied. `activateAuditSpan()` is a null-tolerant guard that calls `AuditSpan.activate()` only when an audit span was captured.

## State and Persistence Behavior

State is immutable after construction: one context reference and one audit-span reference. There is no persistence, synchronization, or close behavior.

## Dependencies and Integration Points

It depends on `StoreContext` and Hadoop audit spans. It is extended by higher-level operation classes such as delete, mkdir, bulk delete, header processing, and executing operations.

## Risks and Edge Cases

The context may be null, so subclasses that assume a non-null store context must enforce that themselves. Capturing the span early is deliberate; failing to use this base in asynchronous operations can lose audit attribution.

## Test Signals

Tests should verify null-context construction, audit-span capture from a mock context, explicit-span construction, and that `activateAuditSpan()` is no-op when the span is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java

## Purpose

`ActiveOperationContext` carries per-operation metadata: an opaque operation id and the `S3AStatisticsContext` used to publish metrics for the active S3A operation.

## Important APIs, Types, and Functions

The constructor requires an operation id and non-null statistics context. `getOperationId()`, `getS3AStatisticsContext()`, and `toString()` expose the fields. `newOperationId()` increments a static `AtomicLong`.

## Control Flow

Callers allocate operation ids through the static counter, then construct an instance with instrumentation. There is no lifecycle beyond object creation and read access.

## State and Persistence Behavior

The operation id and statistics context are final. The only mutable state is the process-local static counter; ids are unique within a JVM but are not persisted or globally unique.

## Dependencies and Integration Points

It depends on `S3AStatisticsContext` and is intended for S3A operation tracing/logging and metric routing.

## Risks and Edge Cases

`newOperationId()` is protected, so only package/subclass code can generate ids. Counter overflow is theoretically possible in very long-lived processes, though unlikely. The `toString()` omits statistics context intentionally.

## Test Signals

Unit tests can assert null statistics rejection, monotonically increasing ids, getter behavior, and stable `toString()` formatting for logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AwsSdkWorkarounds.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AwsSdkWorkarounds.java

## Purpose

`AwsSdkWorkarounds` centralizes AWS SDK logging or behavior workarounds that must run before client creation. In this snapshot the workaround hooks are mostly placeholders.

## Important APIs, Types, and Functions

It defines the transfer manager logger name `TRANSFER_MANAGER`, `prepareLogging()`, and package-private `restoreNoisyLogging()` for tests.

## Control Flow

`prepareLogging()` emits a trace message and returns true. `restoreNoisyLogging()` also returns true without currently changing logger configuration.

## State and Persistence Behavior

The class is stateless and final. It does not persist or cache configuration.

## Dependencies and Integration Points

It depends on SLF4J and Hadoop `VisibleForTesting`. Client manager or factory code can call it before constructing AWS SDK v2 clients.

## Risks and Edge Cases

Because methods currently always return true, callers should not interpret the return value as proof that logging levels changed. Future workarounds need to preserve test restoration semantics.

## Test Signals

Tests should cover idempotent invocation, logger-name constants used by client setup, and restoration behavior if future code adds actual log-level mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AwsSdkWorkarounds.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java

## Purpose

`BaseS3AFileSystemOperations` implements `S3AFileSystemOperations` for normal, non-client-side-encrypted S3A filesystems.

## Important APIs, Types, and Functions

It implements `getObject()`, `setCSEGauge()`, `getClientSideEncryptionMaterials()`, `getS3ClientFactory()`, `getUnencryptedS3ClientFactory()`, and `getS3ObjectSize()`.

## Control Flow

Reads go through `store.getOrCreateS3Client().getObject(request)`. The CSE gauge is set to 0. Client factory selection reads `fs.s3a.s3.client.factory.impl` with the default factory fallback and instantiates it through `ReflectionUtils`. Object size is returned unchanged.

## State and Persistence Behavior

The class holds no state. All behavior is derived from method arguments and Hadoop configuration.

## Dependencies and Integration Points

It integrates with `S3AStore`, `RequestFactory`, AWS SDK `GetObjectRequest`, `HeadObjectResponse`, `S3ClientFactory`, and filesystem IO statistics gauges.

## Risks and Edge Cases

Returning null CSE materials and null unencrypted factory is part of the non-CSE contract; callers must branch on operation implementation rather than dereference blindly. Factory reflection can surface configuration class errors.

## Test Signals

Tests should verify plain client usage, gauge value 0, configured factory instantiation, null CSE materials, null unencrypted factory, and unchanged object length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java

## Purpose

`BulkDeleteOperation` adapts Hadoop `BulkDelete` to S3A by validating paths under a base path, converting them to S3 object identifiers, and returning per-path delete failures.

## Important APIs, Types, and Functions

The class implements `pageSize()`, `basePath()`, `bulkDelete(Collection<Path>)`, and `close()`. Its nested `BulkDeleteOperationCallbacks` performs the actual S3 delete and returns key/error pairs.

## Control Flow

`bulkDelete()` requires the path collection to be non-null and no larger than the configured page size. Each path must be absolute and under `basePath`; it is converted with `StoreContext.pathToKey()`. Callback key failures are mapped back to qualified Hadoop paths with `keyToPath()`.

## State and Persistence Behavior

State is immutable after construction: callbacks, base path, and page size plus inherited context/span. No data is persisted and `close()` is empty.

## Dependencies and Integration Points

It depends on `BulkDeleteUtils.validatePathIsUnderParent`, AWS `ObjectIdentifier`, S3A `StoreContext`, retry annotations, and callback implementations backed by `S3AStore`.

## Risks and Edge Cases

Validation is strict: relative paths, paths outside the base, and oversized batches fail before S3 calls. Empty batches are delegated as an empty object list, with callback behavior expected to be safe.

## Test Signals

Cover base-path rejection, page-size enforcement, absolute-path validation, key/path round trips, callback error mapping, empty input, and captured audit span propagation through the callback implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java

## Purpose

`BulkDeleteOperationCallbacksImpl` is the concrete S3A store-backed callback for `BulkDeleteOperation`.

## Important APIs, Types, and Functions

It implements `bulkDelete(List<ObjectIdentifier>)` and has a private `deleteSingleObject(String)` helper. Constructor state includes the store, log path, page size, and audit span.

## Control Flow

The callback activates the audit span, checks the batch size, returns immediately for zero keys, and uses single-object delete for one key. Multi-key deletes build a bulk delete request via the store request factory and call `store.deleteObjects()` through `Invoker.once`; returned S3 errors are converted to key/string pairs. Single-object access-denied failures are returned as per-key errors rather than thrown.

## State and Persistence Behavior

The class is stateless apart from constructor fields. It does not persist delete state; S3 object deletion is the external side effect.

## Dependencies and Integration Points

It integrates with `S3AStore`, request factories, AWS `DeleteObjectsResponse`, `S3Error`, `ObjectIdentifier`, audit spans, and Hadoop retry translation.

## Risks and Edge Cases

Single-object and multi-object error semantics differ: access denied on a single delete is returned as an item failure, while other IO failures propagate. Page-size checks duplicate the public operation's check and protect direct callback use.

## Test Signals

Tests should cover zero, one, and many keys; access-denied single delete; returned multi-delete errors; page overflow; span activation; and request factory invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java

## Purpose

`BulkDeleteRetryHandler` records statistics and throttle logging when bulk delete operations are retried.

## Important APIs, Types, and Functions

It exposes `bulkDeleteRetried(DeleteObjectsRequest, Exception)`, protected `incrementStatistic()` overloads, and private helpers `onDeleteThrottled()` and `isSymptomOfBrokenConnection()`.

## Control Flow

On retry, throttling exceptions update throttled counters and quantiles by the number of keys in the request. XML parse failures wrapped as `AWSClientIOException`/`SdkClientException` are treated as broken-connection symptoms and counted as throttling. Other failures increment ignored-error statistics.

## State and Persistence Behavior

The handler stores references to the context instrumentation and storage statistics. It does not persist retry history.

## Dependencies and Integration Points

It depends on S3A statistics, S3A throttle exception predicates, AWS `DeleteObjectsRequest`, and the dedicated throttle logger.

## Risks and Edge Cases

`onDeleteThrottled()` assumes the request has at least one key because it logs first and last keys. Broken-connection detection relies on exception type and message text containing `Failed to parse XML document`.

## Test Signals

Exercise throttled exceptions, XML parse broken-connection symptoms, generic exceptions, statistic increments by key count, quantile updates, and empty-request behavior if reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java

## Purpose

`CSEMaterials` is a mutable value holder for client-side encryption material selection.

## Important APIs, Types, and Functions

The nested `CSEKeyType` enum distinguishes `KMS` and `CUSTOM`. Fluent setters include `withKmsKeyId()`, `withCustomCryptographicClassName()`, `withConf()`, and `withCSEKeyType()`. Getters expose KMS key id, custom keyring class, configuration, and selected key type.

## Control Flow

Callers build an instance by chaining setters after `CSEUtils` determines the configured encryption method. `EncryptionS3ClientFactory` later reads the selected key type to build KMS or custom keyrings.

## State and Persistence Behavior

The object stores mutable fields in memory only. It does not clone the Hadoop `Configuration`, so callers share the same configuration reference.

## Dependencies and Integration Points

It depends on Hadoop `Configuration` and integrates with `CSEUtils` and `EncryptionS3ClientFactory`.

## Risks and Edge Cases

Fields can be left unset if callers skip validation, so downstream factory code must still check required fields. Mutability makes reuse across filesystems risky if a caller changes fields after client creation starts.

## Test Signals

Tests should cover fluent method chaining, both key types, retention of configuration references, and downstream rejection of missing custom class or KMS key where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java

## Purpose

`CSES3AFileSystemOperations` implements S3A filesystem operation hooks when AWS client-side encryption is enabled with the modern encryption client.

## Important APIs, Types, and Functions

It overrides object read, CSE gauge setting, encryption material lookup, S3 client factory selection, unencrypted factory selection, and S3 object size calculation.

## Control Flow

Reads use the encrypted S3 client returned by `store.getOrCreateS3Client()`. The CSE gauge is set to 1. Materials are delegated to `CSEUtils`. The encrypted client factory is `EncryptionS3ClientFactory`. `getS3ObjectSize()` subtracts the fixed CSE padding length when the result remains non-negative.

## State and Persistence Behavior

The class is stateless. External effects are client selection, reads, and metric gauge mutation.

## Dependencies and Integration Points

It integrates with `S3AStore`, `EncryptionS3ClientFactory`, `CSEUtils`, AWS SDK responses, and S3A IO statistics.

## Risks and Edge Cases

Padding subtraction is a simple compatibility rule and can be wrong for objects not produced by the expected encryption mode. Returning null unencrypted factory is correct for non-V1 compatibility but must be handled by callers.

## Test Signals

Verify encrypted client factory selection, gauge value 1, material lookup for KMS/custom methods, object read routing, and size handling below/equal/above the padding length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java

## Purpose

`CSEUtils` provides helpers for S3 client-side encryption detection, encrypted object length calculation, and material construction from configuration.

## Important APIs, Types, and Functions

Key methods are `isCSEEnabled(String)`, `isObjectEncrypted(S3AStore,String)`, `getUnencryptedObjectLength(...)`, and `getClientSideEncryptionMaterials(Configuration,String,S3AEncryptionMethods)`.

## Control Flow

Encryption is detected by configured method or by object metadata containing the crypto CEK algorithm header. Length calculation returns raw content length for unencrypted objects, uses `x-amz-unencrypted-content-length` metadata when present, and otherwise performs a ranged GET of the final CSE padding block to derive plaintext length. Material construction selects KMS key id from bucket-aware config for `CSE_KMS` or a custom keyring class for `CSE_CUSTOM`.

## State and Persistence Behavior

The utility is stateless. It issues HEAD and range GET calls through `S3AStore` and closes streams used for length probing.

## Dependencies and Integration Points

It depends on S3A encryption constants, AWS metadata headers, `S3AStore.headObject()`, `getRangedS3Object()`, Hadoop configuration helpers, and `CSEMaterials`.

## Risks and Edge Cases

Length derivation has several failure modes: absent metadata, short encrypted objects, parsing errors, and range GET behavior against non-AWS stores. `isObjectEncrypted()` performs an extra HEAD even if a caller already has metadata.

## Test Signals

Cover CSE_KMS/CSE_CUSTOM detection, unencrypted object fast path, metadata length parsing, missing metadata fallback, final-block range reads, invalid metadata values, custom class configuration, and bucket-specific KMS key lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java

## Purpose

`CSEV1CompatibleS3AFileSystemOperations` extends modern CSE behavior with compatibility for objects written by older client-side encryption clients.

## Important APIs, Types, and Functions

It overrides `getObject()`, `getUnencryptedS3ClientFactory()`, and `getS3ObjectSize()`.

## Control Flow

Before a GET, it checks `CSEUtils.isObjectEncrypted()`. Encrypted objects use the encrypted client path inherited from `CSES3AFileSystemOperations`; unencrypted objects use `store.getOrCreateUnencryptedS3Client()`. Object length is delegated to `CSEUtils.getUnencryptedObjectLength()`. The unencrypted client factory is the configured/default S3 client factory.

## State and Persistence Behavior

The class is stateless. It introduces extra HEAD calls and may choose between two client instances per request.

## Dependencies and Integration Points

It integrates with `S3AStore`, configured S3 client factories, `CSEUtils`, AWS GET/HEAD models, and compatibility settings for CSE V1 data.

## Risks and Edge Cases

Per-read encryption detection adds latency. Misclassified metadata can route reads through the wrong client. The unencrypted client factory must be available when V1 compatibility is enabled.

## Test Signals

Tests should cover encrypted and unencrypted object reads, unencrypted factory selection, length derivation through CSEUtils, metadata lookup failures, and dual-client lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java

## Purpose

`CallableSupplier` bridges checked-exception `Callable` work into `CompletableFuture.supplyAsync()` while preserving S3A audit span activation and converting checked failures into future-compatible runtime wrappers.

## Important APIs, Types, and Functions

It implements `Supplier<T>`. Static helpers include `submit(Executor, Callable)`, `submit(Executor, AuditSpan, Callable)`, `waitForCompletion(List<CompletableFuture<T>>)`, `waitForCompletion(CompletableFuture<T>)`, `waitForCompletionIgnoringExceptions()`, and `maybeAwaitCompletion()`.

## Control Flow

`get()` activates the audit span, calls the callable, rethrows runtime exceptions, wraps IOExceptions in `UncheckedIOException`, and wraps other exceptions as IOExceptions inside `UncheckedIOException`. Waiting helpers join futures, unwrap completion failures through `FutureIO.raiseInnerCause()`, and optionally ignore exceptions.

## State and Persistence Behavior

Each instance stores one callable and optional audit span. There is no persistence. Futures represent asynchronous state owned by callers.

## Dependencies and Integration Points

It is used by copy, delete, and other operations that submit audit-aware async work. It depends on `DurationInfo`, `AuditSpan`, and Hadoop future utilities.

## Risks and Edge Cases

`waitForCompletion(CompletableFuture)` does not accept null, while `maybeAwaitCompletion()` does. Cancellation becomes an IOException. Non-IO checked exceptions lose their original checked type.

## Test Signals

Cover successful calls, span activation, runtime exception propagation, IOException unwrapping from futures, cancellation behavior, empty list waiting, ignored exception path, and null future handling in `maybeAwaitCompletion()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java

## Purpose

`ChangeDetectionPolicy` defines how S3A detects remote object changes during reads, copies, and metadata checks.

## Important APIs, Types, and Functions

The `Source` enum selects `ETag`, `VersionId`, or `None`; `Mode` selects `Client`, `Server`, `Warn`, or `None`. Public factories are `getPolicy(Configuration)` and `createPolicy(...)`. Abstract methods extract revision ids and apply request constraints. Nested policy classes implement ETag, version-id, and no-op behavior.

## Control Flow

Configuration strings are normalized to lower case and unknown values fall back to defaults with warnings. Server mode applies `If-Match`, copy-source-if-match, or version-id constraints depending on source. `onChangeDetected()` either ignores, warns once, or returns a `RemoteFileChangedException`.

## State and Persistence Behavior

Policy instances are immutable: mode, require-version flag, and a `LogExactlyOnce` warning helper. There is no persisted state.

## Dependencies and Integration Points

It depends on AWS SDK request/response builders, `S3ObjectAttributes`, S3A change-detection constants, `RemoteFileChangedException`, and logging.

## Risks and Edge Cases

ETag can change across multipart/encrypted copies and may not be a stable content checksum. Version id requires bucket versioning. Warn mode only logs first mismatch per stream statistics count. Unknown config silently falls back after logging.

## Test Signals

Test config parsing, each source/mode pair, request constraints, missing version handling, no-op policy behavior, warn-once semantics, and exception content on client/server mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeDetectionPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java

## Purpose

`ChangeTracker` tracks a single object's selected revision id while an S3A stream or copy operation progresses and enforces the configured `ChangeDetectionPolicy`.

## Important APIs, Types, and Functions

It exposes `getRevisionId()`, `getSource()`, `maybeApplyConstraint()` overloads for GET/COPY/HEAD builders, `processResponse()` for GET and COPY responses, `processException()`, and metadata processors for HEAD/GET responses.

## Control Flow

The constructor seeds `revisionId` from initial object attributes. Server-mode constraints are applied only when a revision id is known. Response processing pins the first available revision id, throws if required versions are absent, and on mismatches delegates to policy handling while incrementing mismatch statistics. HTTP 412 SDK exceptions become `RemoteFileChangedException`.

## State and Persistence Behavior

The tracker stores mutable in-memory `revisionId` plus references to policy, URI, and statistics. It is per-stream/per-operation, not persisted.

## Dependencies and Integration Points

It integrates with S3A input streams, copy flows, `ChangeTrackerStatistics`, AWS SDK responses/builders/exceptions, and `NoVersionAttributeException`.

## Risks and Edge Cases

If no initial revision is known, the first response becomes authoritative. Null GET responses with an expected revision are treated as remote changes. Copy responses cannot prove equality of source and destination revision.

## Test Signals

Cover initial revision seeding, server constraints, first-response pinning, ETag/version mismatch, warn mode counters, missing required versions, 412 exception translation, null GET responses, and copy response validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChangeTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java

## Purpose

`ChecksumSupport` parses S3A checksum algorithm configuration and limits it to algorithms supported by the connector.

## Important APIs, Types, and Functions

Constants define configuration strings `NONE`, `CRC32C`, and `CRC64NVME`. `getChecksumAlgorithm(Configuration)` returns an AWS SDK `ChecksumAlgorithm` or null.

## Control Flow

The helper reads `fs.s3a.create.checksum.algorithm`, returns null for unset or `NONE`, converts the string to an AWS enum value, and rejects unsupported values with an argument check.

## State and Persistence Behavior

The class is stateless. The supported algorithm set is a static immutable set.

## Dependencies and Integration Points

It depends on Hadoop configuration, S3A constants, Guava immutable sets, AWS SDK checksum enums, and `Preconditions`.

## Risks and Edge Cases

String parsing is case-sensitive to AWS enum conversion. Unsupported algorithms fail early, which is preferable to creating requests S3A cannot reason about. Null return means no checksum selection.

## Test Signals

Test unset, `NONE`, supported CRC32C/CRC64NVME values, invalid enum strings, valid AWS enum values that are intentionally unsupported, and request-building integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java

## Purpose

`ClientManager` defines the lifecycle and lazy-access contract for S3A AWS SDK clients.

## Important APIs, Types, and Functions

It extends Hadoop `Service` and declares getters for transfer manager, sync S3 client, async client, unencrypted S3 client, and unchecked variants.

## Control Flow

Implementations are expected to create clients lazily, translate checked creation failures to `IOException`, and provide unchecked wrappers where required by callback APIs.

## State and Persistence Behavior

As an interface it has no state. Implementations own client references and service lifecycle.

## Dependencies and Integration Points

It integrates `S3Client`, `S3AsyncClient`, `S3TransferManager`, Hadoop service lifecycle, and CSE/V1 compatibility paths needing an unencrypted client.

## Risks and Edge Cases

Unchecked async getter naming returns `S3Client` in this source, so callers must follow the exact declared contract. Service shutdown must close any clients created lazily.

## Test Signals

Implementation tests should assert lazy creation, repeated getter identity, checked/unchecked error conversion, unencrypted-client behavior, transfer manager creation, and cleanup on service stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java

## Purpose

`ClientManagerImpl` is the default lazy lifecycle manager for sync, async, unencrypted, and transfer-manager AWS clients used by S3A.

## Important APIs, Types, and Functions

It stores configured client factories, creation parameters, a duration tracker, and `LazyAutoCloseableReference` wrappers. Public methods implement all `ClientManager` getters, `getUri()`, `serviceStop()`, and `toString()`.

## Control Flow

Constructor wires lazy references to callable factory methods. Getters are synchronized, check the service is not closed, and create clients on first use while tracking creation duration. Transfer manager creation forces async client creation. `serviceStop()` closes all created resources asynchronously and waits for all close futures.

## State and Persistence Behavior

State is in-memory client references and service state. Lazy references close only if created. No client metadata is persisted.

## Dependencies and Integration Points

It depends on `S3ClientFactory`, AWS sync/async clients, `S3TransferManager`, Hadoop `AbstractService`, IO statistics duration tracking, and lazy-close utilities.

## Risks and Edge Cases

Null unencrypted factory is allowed until the unencrypted client is requested. Close failures are awaited together. Synchronization serializes lazy creation and protects closed-state checks.

## Test Signals

Test lazy creation order, transfer-manager dependency on async client, close of only created resources, closed-service rejection, checked and unchecked getter failure paths, duration tracking, and CSE unencrypted factory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java

## Purpose

`ConfigurationHelper` centralizes duration parsing and minimum-duration enforcement for S3A configuration keys.

## Important APIs, Types, and Functions

It exposes `getDuration()`, `setDurationAsSeconds()`, `setDurationAsMillis()`, and `enforceMinimumDuration()`.

## Control Flow

`getDuration()` reads a duration with units from `Configuration.getTimeDuration()`, converts it to a requested `TimeUnit`, wraps it as `Duration`, and enforces a minimum. Setters write seconds or milliseconds with explicit suffixes. Minimum enforcement logs a warning once when a configured value is too low.

## State and Persistence Behavior

The class is stateless except for a static `LogExactlyOnce` used to avoid repeated warnings. Setters mutate the supplied configuration.

## Dependencies and Integration Points

It depends on Hadoop `Configuration`, Java `Duration`, time units, and S3A logging. It is used by configuration initialization code that needs stable lower bounds.

## Risks and Edge Cases

Duration conversion can truncate depending on unit. Values below minimum are silently raised after a warning. The static warning helper may suppress later warnings for different keys.

## Test Signals

Test default values, explicit unit parsing, second/millisecond setters, minimum clamping, warning-once behavior, and unit conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigureShadedAWSSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigureShadedAWSSocketFactory.java

## Purpose

`ConfigureShadedAWSSocketFactory` adapts Hadoop's SSL channel mode configuration to the shaded AWS SDK Apache HTTP client.

## Important APIs, Types, and Functions

It implements `NetworkBinding.ConfigureAWSSocketFactory` and its `configureSocketFactory(ApacheHttpClient.Builder, SSLConnectionSocketFactory)` method.

## Control Flow

The implementation simply calls `httpClientBuilder.socketFactory(socketFactory)`, binding the chosen SSL socket factory into the AWS SDK HTTP client builder.

## State and Persistence Behavior

The class is stateless and has no persistence.

## Dependencies and Integration Points

It depends on AWS SDK shaded Apache HTTP client classes and is reflectively loaded by `NetworkBinding`.

## Risks and Edge Cases

The class name is hard-coded in `NetworkBinding`; relocation or shading changes can break reflective loading. If AWS SDK HTTP builder APIs change, compilation catches it.

## Test Signals

Tests should verify reflective loading through `NetworkBinding`, socket factory assignment to the builder, and graceful behavior when SSL channel mode uses default JSSE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigureShadedAWSSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java

## Purpose

`ContextAccessors` defines S3A filesystem-level services exposed to `StoreContext` without giving store operations a direct filesystem reference.

## Important APIs, Types, and Functions

It declares path/key conversion, temp-file creation, bucket-location lookup, path qualification, active audit span lookup, and request factory access.

## Control Flow

Implementations must translate exceptions and provide the filesystem's authoritative behavior. Operation classes call these methods through `StoreContext` to avoid coupling to `S3AFileSystem`.

## State and Persistence Behavior

The interface has no state. Implementations may rely on filesystem state such as URI, working directory, region cache, and thread-local audit spans.

## Dependencies and Integration Points

It integrates with `Path`, Java `File`, S3A request factories, audit spans, retry annotations, and bucket-region discovery.

## Risks and Edge Cases

The active audit span is thread-local and must be captured before asynchronous handoff. Bucket location may fail with access denied. Path/key conversion must preserve root handling as empty key.

## Test Signals

Use mock implementations to test store operations. Cover root key conversion, relative path qualification, temp-file failures, access-denied bucket location, request factory retrieval, and audit-span capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java

## Purpose

`CopyFromLocalOperation` implements S3A's local filesystem copy/upload workflow for files and directories, including empty-directory preservation and optional source deletion.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Void>`. Key methods are `execute()`, `uploadSourceFromFS()`, `submitUpload()`, `submitCreateEmptyDir()`, source/destination checks, `getFinalPath()`, and the `CopyFromLocalOperationCallbacks` interface.

## Control Flow

Execution resolves the local source file, probes destination status, adjusts destination when copying a directory into an existing directory, validates source and overwrite semantics, then scans local files and directories. It uploads the five largest files first, shuffles remaining files, creates markers for empty directories, waits for all submitted futures, and optionally deletes the local source.

## State and Persistence Behavior

Operation state includes source, mutable destination, destination status, flags, callbacks, and a one-thread throttled executor. External side effects are S3 uploads/marker creation and optional local deletion.

## Dependencies and Integration Points

It depends on local filesystem callbacks, S3A store context executors, audit-span-wrapped futures, Hadoop `RemoteIterator`, and `CallableSupplier`.

## Risks and Edge Cases

Destination URI relativization can fail if source and listed paths do not share a URI base. Empty-directory detection depends on traversal order. Upload failures surface only when waiting for futures; source deletion happens only after uploads complete.

## Test Signals

Cover file-to-file, file-to-dir, dir-to-new-dir, dir-to-existing-dir, overwrite rejection, source missing, empty directory creation, nested empty directories, upload failure, delete-source success/failure, and audit span use in async uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java

## Purpose

`CreateFileBuilder` implements S3A's builder API for file creation and translates builder options into S3A write flags, headers, and conditional overwrite metadata.

## Important APIs, Types, and Functions

It extends `FSDataOutputStreamBuilder`. Public APIs are `build()`, `withFlags()`, `getFlags()`, callback `createFileFromBuilder()`, and value type `CreateFileOptions` with flag/header/etag accessors.

## Control Flow

`build()` separates mandatory header keys from other mandatory keys, rejects unknown mandatory options, extracts create headers from `fs.s3a.create.header.*`, maps content type into an S3 header, rejects append, validates create/overwrite flags, derives `WriteObjectFlags`, validates conditional overwrite etag when enabled, and calls the callback.

## State and Persistence Behavior

The builder stores superclass options and callbacks. `CreateFileOptions` is immutable by reference except the header map is not defensively copied. No persistence occurs here.

## Dependencies and Integration Points

It integrates with Hadoop `FileSystem.createFile()`, `CreateFlag`, S3A create option constants, `WriteObjectFlags`, and the S3A output stream creation path.

## Risks and Edge Cases

Header mandatory keys are exempted from unknown-key rejection. Empty etag with conditional-etag flag fails fast. Append is unsupported. Mutable headers map can be changed if retained by callers.

## Test Signals

Test mandatory key validation, create headers, content type, recursive/performance/multipart flags, conditional overwrite with and without etag, append rejection, no create/overwrite rejection, `withFlags()` mapping, and callback option contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java

## Purpose

`DeleteOperation` implements S3A file and directory deletion, including recursive tree deletion, directory marker handling, batched multi-delete, and optional multipart upload purge.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Boolean>`. Key methods are `execute()`, `deleteDirectoryTree()`, `queueForDeletion()`, `submitNextBatch()`, `deleteObjectAtPath()`, `submitDelete()`, and `asyncDeleteAction()`.

## Control Flow

`execute()` enforces single execution, classifies the pre-fetched status, refuses root deletion, rejects non-recursive deletion of non-empty directories, deletes empty directory markers directly, or lists and batches recursive children. Directory-tree deletion can concurrently abort uploads under the prefix, lists files and markers, submits one delete batch at a time, waits for prior batches before submitting the next, and splits file objects from directory markers for callback statistics.

## State and Persistence Behavior

Mutable state tracks current batch keys, pending delete future, deleted-file count, and optional aborted-upload count. Side effects are S3 object deletes and optional multipart upload aborts.

## Dependencies and Integration Points

It uses `OperationCallbacks`, S3A statuses, `CallableSupplier`, audit spans, S3 `ObjectIdentifier`, throttled executors, and S3A constants for max delete entries.

## Risks and Edge Cases

The operation requires directory emptiness to be known. Only one delete batch runs at a time to reduce recovery complexity. `filesDeleted` is incremented before async delete completion, so failed operations can leave counters ahead of actual S3 state.

## Test Signals

Cover root deletion, file deletion, empty directory deletion, recursive and non-recursive directory cases, page-size batching, previous-batch failure propagation, upload purge success/failure, marker/file split, and single-execute enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java

## Purpose

`DirMarkerTracker` tracks directory markers encountered during sorted S3 listings and identifies which markers are leaf markers versus surplus parent markers.

## Important APIs, Types, and Functions

Important methods are `markerFound()`, `fileFound()`, `pathFound()`, `removeParentMarkers()`, getters for leaf/surplus maps and counters, plus nested immutable `Marker`.

## Control Flow

When a marker is found it is first recorded as a candidate leaf, then all parent markers of that path are removed as surplus. When a file is found, parent markers are similarly removed. A cached `lastDirChecked` avoids rescanning the same parent for many siblings.

## State and Persistence Behavior

State is in-memory maps of leaf and optionally surplus markers, the base path, last checked directory, and counters. Nothing is persisted.

## Dependencies and Integration Points

It depends on Hadoop `Path` and `S3ALocatedFileStatus`. Rename, listing, auditing, and directory-marker cleanup code can use it while traversing list results.

## Risks and Edge Cases

The logic assumes listing order is alphanumeric with parents before children. If callers feed unsorted paths, leaf/surplus classification can be wrong. Recording surplus markers can consume memory in huge trees.

## Test Signals

Test parent marker removal, leaf marker preservation, surplus recording enabled/disabled, repeated sibling scan optimization, root/null parent handling, counters, and version id exposure from marker status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DirMarkerTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java

## Purpose

`EncryptionS3ClientFactory` creates AWS S3 encryption clients for S3A client-side encryption and wraps underlying standard sync/async clients.

## Important APIs, Types, and Functions

It extends `DefaultS3ClientFactory`. Overridden methods are `createS3Client()` and `createS3AsyncClient()`. Helpers include encryption-client availability checks, `createS3EncryptionClient()`, `createS3AsyncEncryptionClient()`, `createKmsKeyring()`, `getKeyringProvider()`, and `getCustomKeyringProviderClass()`.

## Control Flow

Creation first verifies the encryption client class is on the classpath. Sync client creation initializes both wrapped sync and async clients, then builds an `S3EncryptionClient` with legacy unauthenticated/rapping modes enabled. KMS materials build a KMS client using credential, KMS region, S3 region, or endpoint fallback. Custom materials reflectively instantiate a `Keyring` class. Async encryption client creation wraps the previously initialized async client.

## State and Persistence Behavior

The factory stores wrapped sync and async clients in fields during creation. The encryption-client availability flag is cached in a lazy atomic reference. No persistent state is written.

## Dependencies and Integration Points

It depends on AWS Encryption SDK S3 classes, AWS KMS, S3A `S3ClientCreationParameters`, `CSEMaterials`, Hadoop reflection, and instantiation IO errors.

## Risks and Edge Cases

Async encrypted client creation requires `s3AsyncClient` to have been initialized, making call order important. Missing encryption classes fail with `InstantiationIOException.unavailable()`. Custom keyring reflection supports a test-specific constructor fallback and can hide original errors inside RuntimeException/IOException.

## Test Signals

Cover missing encryption client class, KMS keyring region and endpoint fallback, custom keyring success/failure, sync-before-async creation order, legacy mode flags, credential propagation, and close lifecycle through `ClientManagerImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ErrorTranslation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ErrorTranslation.java

## Purpose

`ErrorTranslation` isolates AWS SDK exception translation helpers that supplement S3A's larger exception translation logic.

## Important APIs, Types, and Functions

It exposes `isUnknownBucket()`, `isObjectNotFound()`, `maybeProcessEncryptionClientException()`, `maybeExtractIOException()`, and testing-visible `maybeExtractChannelException()`. Nested `AwsErrorCodes` defines `NoSuchBucket`.

## Control Flow

404 service exceptions are split into unknown-bucket versus object-not-found by AWS error code. Encryption client wrapper exceptions are detected by class-name text and unwrapped to an inner `SdkException` or `AwsServiceException` when present. IO extraction walks to the innermost cause, maps HTTP no-response/OpenSSL closed-channel symptoms to `HttpChannelEOFException`, or reflectively recreates the innermost IOException type with the outer exception as cause.

## State and Persistence Behavior

The class is stateless.

## Dependencies and Integration Points

It depends on AWS SDK exception types, Hadoop `PathIOException`, `HttpChannelEOFException`, and S3A HTTP status constants.

## Risks and Edge Cases

Class-name and message-string matching is brittle but avoids direct dependencies on shaded/unshaded classes. `maybeExtractChannelException()` assumes `thrown.getMessage()` is non-null for OpenSSL matching. Reflection fallback may lose exact exception type.

## Test Signals

Test bucket/object 404 distinction, encryption client unwrapping shapes, nested IOException extraction, no-response exception class names, OpenSSL message mapping, null input, and constructor-missing fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ErrorTranslation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java

## Purpose

`ExecutingStoreOperation` is a base class for S3A operations that can be submitted as `CallableRaisingIOE` and must execute at most once.

## Important APIs, Types, and Functions

It extends `AbstractStoreOperation`, implements `CallableRaisingIOE<T>`, provides final `apply()`, abstract `execute()`, and protected `executeOnlyOnce()`.

## Control Flow

`apply()` delegates to `execute()`. Subclasses are required to call `executeOnlyOnce()` at the start of `execute()`. That method atomically flips an `AtomicBoolean`, rejects re-entry, and activates the captured audit span.

## State and Persistence Behavior

State is the inherited context/span and one atomic executed flag. There is no persistence.

## Dependencies and Integration Points

It integrates with Hadoop functional utilities, audit spans, and operations such as delete, mkdir, content summary, and copy-from-local.

## Risks and Edge Cases

The single-execution contract is cooperative: subclasses must call `executeOnlyOnce()`. If they omit it, re-entry is not prevented and audit span activation is not guaranteed.

## Test Signals

Test `apply()` delegation, second-execution rejection in subclasses that call `executeOnlyOnce()`, audit activation, and concurrent double invocation against a test subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java

## Purpose

`GetContentSummaryOperation` computes S3A content summaries optimized for object-store listings and exposes IO statistics for the listing work.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<ContentSummary>` and implements `IOStatisticsSource`. Key methods are `execute()`, `getDirSummary()`, `buildDirectorySet()`, `probePathStatusOrNull()`, and callback methods for status probes and recursive listings.

## Control Flow

Execution first probes for a file; files return a one-file summary. Directories are recursively listed. The operation counts file lengths and file count, tracks all inferred ancestor directories in sets, aggregates iterator IO statistics, and returns a `ContentSummary` with directory count equal to base directory plus inferred directories.

## State and Persistence Behavior

State includes target path, callbacks, and an `IOStatisticsSnapshot` aggregated during execution. No persisted state is written.

## Dependencies and Integration Points

It depends on S3A status/listing callbacks, `S3ALocatedFileStatus`, Hadoop `ContentSummary`, and IO statistics retrieval from iterators.

## Risks and Edge Cases

It only probes file status initially; missing paths fall through to directory listing, which must raise not found. Directory inference is needed because S3 may not store every ancestor marker. Large trees can grow the directory sets substantially.

## Test Signals

Cover file summary, empty directory, nested directories without markers, explicit directory markers, missing path, iterator IO stats aggregation, duplicate sibling parent optimization, and recursive listing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java

## Purpose

`HeaderProcessing` implements S3A extended-attribute reads backed by S3 object and bucket headers, and provides metadata cloning for copy operations.

## Important APIs, Types, and Functions

It defines many `header.*` XAttr names, content-type constants, `getXAttr()`, `getXAttrs()` overloads, `listXAttrs()`, `encodeBytes()`, `decodeBytes()`, `extractXAttrLongValue()`, and static `cloneObjectMetadata()`.

## Control Flow

Header retrieval converts the path to an S3 key. Root uses `HeadBucket` and synthesizes content length zero. Non-root uses `HeadObject`, retrying with a trailing slash when the bare key is not found. User metadata is prefixed with the XAttr header prefix, standard HTTP/AWS fields are added when non-null, and public XAttr methods filter or return the resulting map. Metadata cloning copies selected HTTP/SSE headers and user metadata except the magic-marker header.

## State and Persistence Behavior

The operation stores callbacks and inherited context/span. It does not persist data; it reads S3 metadata and returns encoded byte arrays.

## Dependencies and Integration Points

It integrates with S3A xattr APIs, S3 HEAD bucket/object responses, statistics duration tracking, AWS header constants, and rename/copy metadata handling.

## Risks and Edge Cases

Directory fallback relies on appending `/` after not found. Header names are case-sensitive after mapping. Copy metadata can miss newly added SDK fields if not updated. `extractXAttrLongValue()` logs and returns empty on invalid or negative numbers.

## Test Signals

Test root bucket headers, file and directory marker metadata, user metadata prefixing, selected header encoding, named XAttr filtering, content-range extraction from HTTP headers, long parsing, and magic-marker exclusion during clone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InputStreamCallbacksImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InputStreamCallbacksImpl.java

## Purpose

`InputStreamCallbacksImpl` supplies S3A object input stream code with request construction, object GET execution, async submission, and audit-span handling.

## Important APIs, Types, and Functions

It implements `ObjectInputStreamCallbacks` with `close()`, `newGetRequestBuilder()`, `getObject()`, and `submit(CallableRaisingIOE<T>)`.

## Control Flow

Request builders come from `store.getRequestFactory().newGetObjectRequestBuilder(key)`. `getObject()` activates the audit span and delegates the actual GET to the configured `S3AFileSystemOperations`, which may be base, CSE, or compatibility behavior. Async submissions wrap callable work in the same audit span and use the supplied thread pool.

## State and Persistence Behavior

State includes audit span, store, filesystem operation strategy, and thread pool. `close()` currently has no cleanup behavior.

## Dependencies and Integration Points

It integrates S3A stream factories with `S3AStore`, `S3AFileSystemOperations`, AWS `GetObjectRequest`, `ResponseInputStream`, and `CallableSupplier`.

## Risks and Edge Cases

Correct behavior depends on the chosen filesystem operations object; CSE compatibility can alter client selection and object size behavior. `close()` not shutting down the thread pool assumes ownership remains elsewhere.

## Test Signals

Test request builder creation, base and CSE GET routing, audit span activation for sync and async operations, exception propagation through submitted futures, and no-op close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InputStreamCallbacksImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java

## Purpose

`InstantiationIOException` is a `PathIOException` subtype used when S3A cannot instantiate configured classes such as providers, factories, or optional components.

## Important APIs, Types, and Functions

The `Kind` enum categorizes abstract class, constructor failure, instantiation failure, not-implementing, unavailable, and unsupported-constructor cases. Static factory methods build typed exceptions with consistent messages.

## Control Flow

Callers use static helpers such as `isAbstract()`, `isNotInstanceOf()`, `unavailable()`, `unsupportedConstructor()`, and `instantiationException()` to include URI, class name, configuration key, and cause. Getters expose kind, class name, and key.

## State and Persistence Behavior

The exception stores final kind/class/key fields plus inherited path, message, and cause. There is no persistence beyond exception serialization inherited from `Throwable`.

## Dependencies and Integration Points

It depends on Hadoop `PathIOException` and is used by reflection-heavy S3A configuration and optional component loading, including encryption client availability.

## Risks and Edge Cases

Messages are operationally important because they often surface configuration mistakes. Incorrect kind selection can mislead diagnostics. Class names and keys may be null for unavailable optional modules.

## Test Signals

Test each factory method's kind, message content, path/URI formatting, cause preservation, class/key getters, and behavior for missing optional encryption classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java

## Purpose

`InternalConstants` collects private S3A implementation constants that are not stable public API.

## Important APIs, Types, and Functions

It defines delete idempotency, buffer sizes, rename/delete/upload limits, default block size, HTTP status codes, log names, S3A open/create option key sets, CSE padding length, access point messages, dynamic capabilities, AWS auth scheme name, and error-code strings.

## Control Flow

The class has static initialization for immutable open-file and create-file key sets and dynamic capability lists. There are no methods beyond the private constructor.

## State and Persistence Behavior

All state is static constants or immutable collections. No runtime mutation or persistence occurs.

## Dependencies and Integration Points

It is referenced across S3A operations for max multi-delete size, CSE length adjustment, status-code translation, capability reporting, create/open option validation, logging, and upload limits.

## Risks and Edge Cases

Because these constants are internal, external code should not depend on them. Changing limits such as `MAX_ENTRIES_TO_DELETE`, `RENAME_PARALLEL_LIMIT`, or CSE padding affects request batching and compatibility. Capability lists must stay aligned with actual feature support.

## Test Signals

Tests should assert option-key validation uses these sets, max delete limit matches S3 request constraints, dynamic capability reporting contains expected entries, and status-code constants match translation code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java

## Purpose

`ListingOperationCallbacks` defines the filesystem callbacks needed by S3A listing implementations.

## Important APIs, Types, and Functions

It declares async list initiation and continuation, located-status conversion, list-request construction, default block-size lookup, S3 object size lookup, and max-key retrieval.

## Control Flow

Listing code uses `createListObjectsRequest()` to build an audited request, submits it through `listObjectsAsync()`, follows pages through `continueListObjectsAsync()`, and converts returned S3 objects/statuses through the remaining callbacks.

## State and Persistence Behavior

The interface has no state. Implementations may update metrics through `DurationTrackerFactory` and audit spans.

## Dependencies and Integration Points

It connects listing code with AWS S3 list request/result abstractions, S3A status objects, block location synthesis, CSE-aware object size calculation, and max listing page size configuration.

## Risks and Edge Cases

Failures surface asynchronously from returned futures. Object size may require metadata or CSE calculations and can throw IOException. Audit spans must be passed into async requests.

## Test Signals

Mock callback tests should cover initial and continued listings, future failure propagation, status-to-located-status conversion, max-key configuration, default block-size lookup, and encrypted object size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ListingOperationCallbacks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java

## Purpose

`MkdirOperation` creates S3A directory markers while validating that no file blocks the target path or closest ancestor, with special handling for magic committer paths and performance mode.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Boolean>`. Important methods are `execute()`, `verifyFileStatusOfClosestAncestor()`, `probePathStatusOrNull()`, `getPathStatusExpectingDir()`, and `MkdirCallbacks`.

## Control Flow

Root returns true. The target is probed first as a directory, and as a file unless it is a magic path. Existing directories return true; existing files fail. Magic paths create the marker without ancestor checks. Normal mode walks parents until it finds an existing directory or file, ignoring access-denied failures during parent checks. Finally it calls `createFakeDirectory()`.

## State and Persistence Behavior

State includes target directory, callbacks, performance flag, and magic-path flag. The external side effect is writing a directory marker object.

## Dependencies and Integration Points

It depends on S3A status probes, directory marker creation callbacks, retry translation, and S3A magic committer path semantics.

## Risks and Edge Cases

Performance mode can skip detection of blocking ancestor files. Magic paths intentionally avoid ancestor validation. Access denied while checking parents is logged and ignored, allowing mkdir to continue.

## Test Signals

Cover root, existing directory, existing file, missing target with existing ancestor, blocking ancestor file, magic path, performance mode, access-denied parent probe, directory-first probe ordering, and marker creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java

## Purpose

`MultiObjectDeleteException` represents S3 multi-object delete responses that returned per-object failures despite an HTTP 200 status.

## Important APIs, Types, and Functions

It extends AWS `S3Exception`, stores a list of `S3Error`, exposes `errors()`, `translateException(String)`, and static `errorToString(S3Error)`.

## Control Flow

Construction builds an S3Exception with status 200, synthetic error code, service name, and a message summarizing the error count. Translation inspects contained errors: access denied failures produce an `AccessDeniedException`; otherwise a general `AWSS3IOException` is returned. Each error can be formatted with key, version id, code, and message.

## State and Persistence Behavior

The error list is stored in memory. There is no persistence.

## Dependencies and Integration Points

It integrates AWS SDK S3 error models with S3A exception translation and bulk-delete/remove-keys flows.

## Risks and Edge Cases

HTTP 200 does not mean success for multi-delete. Mixed errors are collapsed to one translated IOException, so callers needing per-key detail must inspect `errors()`. Error lists should be treated as immutable by callers but are not defensively copied here.

## Test Signals

Test construction message/status/code, access-denied translation, non-access-denied translation, mixed error behavior, formatting with and without version id, and preservation of all S3 errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java

## Purpose

`NetworkBinding` contains network-related S3A helpers for SSL channel binding, AWS endpoint recognition, bucket-region normalization, and DNS lookup logging.

## Important APIs, Types, and Functions

It exposes `bindSSLChannelMode(Configuration, ApacheHttpClient.Builder)`, `isAwsEndpoint(String)`, `fixBucketRegion(String)`, and `logDnsLookup(Configuration)`. It reflectively loads `ConfigureShadedAWSSocketFactory`.

## Control Flow

SSL binding reads the configured SSL channel mode and, when not default, creates an SSL socket factory and applies it to the AWS Apache HTTP builder through the reflected adapter. Endpoint recognition checks host suffixes for AWS patterns. Region normalization maps null/empty and legacy `US` to the expected region string. DNS logging emits resolver information when enabled.

## State and Persistence Behavior

The class is stateless. It mutates the supplied HTTP client builder when custom SSL mode is configured.

## Dependencies and Integration Points

It depends on Hadoop network/SSL utilities, AWS SDK Apache HTTP builder classes, S3A configuration constants, and the shaded socket factory adapter.

## Risks and Edge Cases

Reflective adapter loading can fail if shading or class names change. Endpoint suffix checks can misclassify nonstandard S3-compatible endpoints. Region normalization must preserve AWS SDK expectations.

## Test Signals

Test default and custom SSL modes, reflective adapter failure, AWS and non-AWS endpoint strings, null/empty/`US` region normalization, and DNS logging when enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java -->
