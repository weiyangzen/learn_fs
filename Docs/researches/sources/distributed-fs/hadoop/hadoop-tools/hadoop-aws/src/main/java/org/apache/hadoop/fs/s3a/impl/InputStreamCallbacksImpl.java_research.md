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
