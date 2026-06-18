# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RequestFactoryImpl.java

## Purpose
`RequestFactoryImpl` is the central AWS SDK v2 S3 request builder for S3A. It attaches bucket, ACL, storage class, content encoding, checksums, encryption parameters, conditional write headers, upload timeouts, and audit/request preparation callbacks consistently across S3 operations.

## Important APIs and Types
It implements `RequestFactory` with builders for copy, put, directory marker put, multipart list/abort/create/complete/upload part, head object/bucket, get object, list objects v1/v2, single delete, and bulk delete. It exposes encryption and configuration accessors, `setEncryptionSecrets()`, and a nested `RequestFactoryBuilder`. The nested `PrepareRequest` callback lets audit/request preparation mutate every builder before use.

## Control Flow
Every public builder method constructs an AWS SDK request builder, sets common bucket/key values, applies operation-specific fields, calls encryption helper methods where needed, and returns `prepareRequest(builder)`. Copy requests clone metadata from source HEAD, use `MetadataDirective.REPLACE`, propagate source KMS key when present, otherwise apply filesystem encryption settings. PUT and multipart create requests attach metadata headers, ACL, storage class, content encoding, checksum algorithm, and encryption settings. Conditional overwrite options become `If-None-Match` or `If-Match` override headers. Upload-part requests validate upload id, part number, size, part-count limit, optional last-part marker, SSE-C parameters, timeout, and checksum. Complete multipart optionally includes conditional headers and SSE-C headers when checksums are used.

## State and Persistence
The factory stores mostly immutable configuration but `encryptionSecrets` is mutable through `setEncryptionSecrets()`, allowing token or encryption state refresh. It does not execute requests; it shapes all later persisted S3 mutations and reads.

## Dependencies and Integration Points
It depends heavily on AWS SDK v2 S3 model builders, `EncryptionSecrets`, `EncryptionSecretOperations`, `S3AEncryptionMethods`, `HeaderProcessing`, `AWSClientConfig.setRequestTimeout`, `WriteObjectFlags`, and S3A constants. It is used by `S3AStoreImpl`, write operations, stream callbacks, and listing/delete code.

## Risks and Edge Cases
Incorrect encryption parameter selection can make objects unreadable or copy operations fail, especially SSE-C and KMS context handling. Mutable `encryptionSecrets` may be a concurrency concern if changed while requests are being built. Multipart upload disabled causes `PathIOException` at create time. Part count limit is test-tunable and must be enforced. Conditional overwrite headers must be sent on both PUT and complete-multipart paths. Directory markers intentionally omit content encoding and upload timeout.

## Test Signals
Tests should inspect built requests for each encryption mode (`SSE_S3`, `SSE_KMS`, `DSSE_KMS`, `SSE_C`, CSE, none), content encoding, checksum, ACL, storage class, conditional headers, request timeout, multipart disabled errors, part-count limit errors, bulk delete quiet flag behavior, and invocation of `PrepareRequest`.
