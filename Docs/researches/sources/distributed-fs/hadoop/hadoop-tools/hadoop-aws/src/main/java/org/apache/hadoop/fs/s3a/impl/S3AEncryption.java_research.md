# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AEncryption.java

## Purpose
`S3AEncryption` provides utilities for retrieving and encoding SSE-KMS encryption context configuration for S3A.

## Important APIs and Types
`getS3EncryptionContext(bucket, conf)` looks up per-bucket then global `S3_ENCRYPTION_CONTEXT` secrets. `getS3EncryptionContextBase64Encoded(bucket, conf, propagateExceptions)` parses key-value context strings, serializes them as JSON, and Base64-encodes the UTF-8 JSON.

## Control Flow
The lookup first asks `S3AUtils.lookupBucketSecret()`, then global `S3AUtils.lookupPassword()`. Base64 encoding returns empty string for blank or empty parsed values. IO failures are either propagated or logged and converted to empty string depending on `propagateExceptions`.

## State and Persistence
The class is stateless. It reads configuration/credential provider state and returns strings used in future S3 requests.

## Dependencies and Integration Points
It depends on Jackson `ObjectMapper`, Apache commons Base64/StringUtils, Hadoop `Configuration`, and S3A secret lookup utilities. The output integrates with encryption secret setup and request builders for KMS encryption context.

## Risks and Edge Cases
Malformed key-value context strings may parse to empty or throw depending on helper behavior. Suppressing IO exceptions can silently omit encryption context, which may affect access policies. Base64 JSON key order follows map serialization and should not be assumed stable unless the parser returns ordered maps.

## Test Signals
Tests should cover per-bucket override precedence, global fallback, blank/empty values, valid multi-entry encoding, IO exception propagation vs warning path, and bad context parsing.
