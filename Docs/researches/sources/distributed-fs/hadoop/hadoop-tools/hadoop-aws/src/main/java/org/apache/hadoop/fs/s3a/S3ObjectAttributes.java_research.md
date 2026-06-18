# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ObjectAttributes.java

## Purpose
`S3ObjectAttributes` is an immutable value holder for object metadata needed by streams and other S3A code without requiring a full file status object.

## Important APIs, Types, and Functions
The constructor captures bucket, Hadoop path, S3 key, server-side encryption algorithm/key, ETag, version id, and length. Getters expose each field.

## Control Flow and State
There is no control flow beyond construction and access. The class reduces constructor parameter sprawl in consumers such as `S3AInputStream`.

## State and Persistence Behavior
Instances are immutable references/values and persist no remote state. Encryption key material may be held in memory as a string.

## Dependencies and Integration Points
Dependencies include Hadoop `Path` and `S3AEncryptionMethods`. It integrates with stream setup, change detection, and file-status-derived paths that need bucket/key/length/encryption metadata.

## Risks and Test Signals
Risks include retaining sensitive SSE-C key strings, passing stale length/version metadata after object replacement, and no validation of required fields. Tests should verify field preservation, null-tolerant optional metadata behavior, and consumers' handling of version/ETag and encryption attributes.
