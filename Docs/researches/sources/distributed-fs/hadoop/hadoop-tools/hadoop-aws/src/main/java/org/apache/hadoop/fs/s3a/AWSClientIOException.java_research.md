# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSClientIOException.java

Purpose: base IOException wrapper for AWS SDK `SdkException` instances.

Important APIs/types: constructor validates non-null operation and cause; `getCause()` narrows the type to `SdkException`; `getMessage()` returns `<operation>: <cause message>`; `retryable()` delegates to the SDK exception; `getOperation()` exposes the operation.

Control flow: constructed by S3A exception translation, then inspected by retry policy and callers. It does not retry by itself.

State and persistence behavior: immutable operation string and Throwable cause.

Dependencies and integration points: depends on AWS SDK v2 `SdkException`, Hadoop `Preconditions`, and Java `IOException`. It is the superclass for service-specific wrappers.

Risks: message formatting depends on non-null cause message; retry decisions reflect SDK metadata unless subclasses override.

Test signals: unit tests should verify null argument rejection, message formatting, cause narrowing, and retryable delegation.
