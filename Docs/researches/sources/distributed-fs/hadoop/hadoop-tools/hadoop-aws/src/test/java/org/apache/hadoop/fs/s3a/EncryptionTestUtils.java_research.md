# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/EncryptionTestUtils.java

Purpose: static assertion helpers for S3A encryption tests.

Important APIs/types/functions: constants for AWS KMS, DSSE KMS, and SSE-C algorithm strings. `convertKeyToMd5(FileSystem)` decodes configured base64 customer key, MD5 hashes it, and base64 encodes the result. `assertEncrypted(S3AFileSystem, Path, S3AEncryptionMethods, String)` inspects `HeadObjectResponse` metadata for SSE-C, SSE-KMS, DSSE-KMS, or AES256. `validateEncryptionFileAttributes()` checks S3A xAttrs for encryption algorithm and optional KMS key id.

Control flow: `assertEncrypted()` switches on `S3AEncryptionMethods`, performing algorithm-specific metadata assertions.

State and persistence: stateless utility class.

Dependencies and integration: S3A internals metadata lookup, AWS SDK `HeadObjectResponse`, header-processing xAttr decoding, AssertJ, Commons Codec/Net Base64.

Risks: metadata expectations vary by store, encryption mode, and KMS key ARN form. SSE-C key MD5 requires the exact configured key.

Test signals: shared by server-side encryption tests and xAttr encryption checks.
