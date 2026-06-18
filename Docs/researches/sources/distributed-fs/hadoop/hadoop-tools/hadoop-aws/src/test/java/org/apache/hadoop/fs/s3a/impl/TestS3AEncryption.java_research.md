# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AEncryption.java

## Purpose
`TestS3AEncryption` validates parsing and encoding of S3 encryption context configuration, including per-bucket override precedence and base64 JSON output.

## Important APIs, Types, and Functions
- Tests `S3AEncryption.getS3EncryptionContext()` and `getS3EncryptionContextBase64Encoded()`.
- Uses global `S3_ENCRYPTION_CONTEXT` and bucket-scoped `fs.s3a.bucket.<bucket>.encryption.context` configuration keys.
- Uses Jackson `ObjectMapper` to parse decoded JSON context into a map.

## Control Flow
The per-bucket test sets both global and bucket contexts and expects the bucket-specific value. The global test requests another bucket and expects the trimmed global value. The unset test expects an empty string. The base64 test encodes the global context, decodes it, parses JSON, and verifies key/value pairs.

## State and Persistence Behavior
All state is in in-memory `Configuration` and decoded strings. No S3 or file I/O occurs.

## Dependencies and Integration Points
The test integrates S3A encryption context parsing, Hadoop bucket-option precedence, Apache Commons Base64 decoding, and Jackson JSON parsing.

## Risks and Edge Cases
Context parsing assumes comma-separated `key=value` pairs. More complex values or escaping rules would need additional tests.

## Test Signals
Passing confirms encryption context lookup precedence, trimming, empty default behavior, and base64 JSON encoding for AWS request use.
