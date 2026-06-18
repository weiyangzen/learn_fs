# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEC.java

Purpose: Parameterized SSE-C integration suite, run with analytics accelerator enabled and disabled, focusing on wrong-key behavior for reads, metadata/status, rename, delete, checksum, and listing.

Important APIs/types/functions: extends `AbstractTestS3AEncryption`; uses `S3AEncryptionMethods.SSE_C`, `Constants.S3_ENCRYPTION_KEY`, `ETAG_CHECKSUM_ENABLED`, `S3AContract`, `ContractTestUtils.verifyFileContents()`, `listFiles()`, `listStatus()`, `getFileChecksum()`, and helper `createNewFileSystemWithSSECKey()`.

Control flow: configuration removes encryption overrides, sets SSE-C key A, enables etag checksums, and optionally enables analytics accelerator. Setup skips root-style tests and non-AWS-hosted stores. Tests write with key A, then create `fsKeyB` with a different key and assert AWS 403 translated to `AccessDeniedException` for decrypting reads, file metadata, file delete, and checksum. Directory listing/status and recursive directory deletion are expected to work even with wrong or no key because LIST does not require object decryption.

State and persistence: maintains `fsKeyB` as a secondary filesystem closed in teardown; writes encrypted objects and directories. Test constants are fixed base64 SSE-C keys.

Dependencies and integration points: AWS SSE-C semantics, S3A encryption headers on read/write/copy/delete, list-before-head optimizations, ETag checksum behavior, analytics accelerator path, and contract-created alternate filesystems.

Risks: live AWS-only behavior; alternate object stores may differ; 403 message matching is brittle; directory marker/list optimizations are subtle and can change status behavior; analytics accelerator can alter stream path.

Test signals: strong coverage for SSE-C access boundaries and for S3A logic that must avoid unnecessary HEAD/decrypt operations on directories while still failing correctly for encrypted files.
