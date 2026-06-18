# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/api/RequestFactory.java

## Purpose
`RequestFactory` is the S3A interface for constructing AWS SDK v2 S3 request builders. It is the audit-aware boundary through which S3A request creation should pass so requests can be prepared, annotated, and consistently configured.

## Important APIs and control flow
The interface exposes configuration accessors for encryption secrets, canned ACL, server-side encryption, content encoding, and storage class. It creates builders for copy, put object, directory marker, list multipart uploads, abort/start/complete MPU, head object/bucket, get object, upload part, list v1/v2, delete object, and bulk delete requests. Multipart start may throw `PathIOException` when MPU is disabled; upload part may throw when part numbers are invalid.

## State, dependencies, and integration
Implementations hold the mutable encryption-secret state and owner-specific request-preparation callback. Dependencies are AWS SDK v2 S3 model builders, `S3AEncryptionMethods`, delegation encryption secrets, `PutObjectOptions`, and Hadoop `PathIOException`. It integrates with write helpers, filesystem metadata paths, delete code, and auditing.

## Risks and test signals
The main risk is bypassing the factory, which loses audit headers or encryption/storage metadata. Builder reuse and mutable encryption settings also need care. Tests should assert every S3A request path uses this factory, encryption and ACL options are applied, MPU-disabled errors are raised, and delete/list/copy builders preserve key, bucket, metadata, and limits.
