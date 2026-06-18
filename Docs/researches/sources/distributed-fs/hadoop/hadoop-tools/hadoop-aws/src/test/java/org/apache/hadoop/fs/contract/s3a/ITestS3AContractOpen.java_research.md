# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractOpen.java

Purpose: S3A open-file contract coverage plus S3A-specific `openFile()` validation.

Important APIs/types/functions: extends `AbstractContractOpenTest`; `areZeroByteFilesEncrypted()` returns true because S3A reports zero-byte files as encrypted. Adds `testOpenFileApplyReadBadName()` and `testOpenFileDirectory()`.

Control flow: bad-name test creates a zero-byte file, constructs a mismatched `FileStatus` with a `gopher://` path, and expects `IllegalArgumentException` from `openFile(...).withFileStatus(st2).build()`. Directory test mutates a file status to directory and expects `FileNotFoundException`.

State and persistence: creates files under method paths.

Dependencies and integration: `FileSystem.openFile()` builder, Hadoop `FileStatus`, contract open suite, and S3A status validation.

Risks: synthetic `FileStatus` construction must match constructor semantics; path scheme mismatch is deliberately artificial.

Test signals: integration coverage for open builder status/path validation and directory rejection.
