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
