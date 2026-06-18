# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamCallbacks.java

## Purpose
`ObjectInputStreamCallbacks` defines the operations an object input stream needs from the S3A store/filesystem: building GET requests, executing GETs, submitting async work, and closing associated context.

## Important APIs and Types
It extends `Closeable`. Methods are `newGetRequestBuilder(String key)`, `getObject(GetObjectRequest)`, and `<T> CompletableFuture<T> submit(CallableRaisingIOE<T> operation)`.

## Control Flow
Streams use `newGetRequestBuilder()` to create request builders with common request factory settings, `getObject()` to execute reads with encryption-aware client selection, and `submit()` for background work such as stream draining. `ObjectInputStream.close()` calls `callbacks.close()`.

## State and Persistence
The interface has no state. Implementations may hold audit spans, clients, and per-stream resources. GET calls read persistent object data; submit can run cleanup operations.

## Dependencies and Integration Points
It depends on AWS SDK get request/response types, S3A retry annotations, and Hadoop functional callable utilities. It is implemented by S3A stream callback classes outside this subset.

## Risks and Edge Cases
Implementations must be close-safe and preserve audit/encryption semantics. Async operations must complete futures with exceptions reliably. GET execution behavior differs when client-side encryption is enabled.

## Test Signals
Tests should validate GET request construction, encrypted vs unencrypted GET paths, async drain submission, callback close idempotence, and exception propagation from submitted operations.
