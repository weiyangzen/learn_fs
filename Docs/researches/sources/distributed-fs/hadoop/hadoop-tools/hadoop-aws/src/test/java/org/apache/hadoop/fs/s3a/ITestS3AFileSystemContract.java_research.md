# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFileSystemContract.java

Purpose: Live S3A implementation of Hadoop `FileSystemContractBaseTest`, with S3-specific rename and overwrite expectations.

Important APIs/types/functions: `FileSystemContractBaseTest`, `S3ATestUtils.createTestFileSystem()`, `setPerformanceFlags()`, `TestName`, `rename()`, `createFile()`, and `LambdaTestUtils.intercept()`.

Control flow: `setUp()` names the test thread, creates a test filesystem, and computes a qualified base path. Several inherited tests are skipped or adapted: mkdirs umask unsupported, rename into nonexistent directories does not fail on S3A, rename directory onto existing dir is validated for nested children, directory-to-file and file-to-file rename expect `FileAlreadyExistsException`, and missing-source rename expects `FileNotFoundException`.

State and persistence: remote test data under `s3afilesystemcontract`; base class manages cleanup. Method name extension aids logging/thread naming.

Dependencies and integration points: Hadoop FS contract, S3A rename/copy/delete semantics, and create-performance mode.

Risks: object-store rename is non-atomic copy/delete and differs from POSIX; superclass behavior can conflict with S3A semantics; overwrite handling conditionally tolerates create-performance differences.

Test signals: broad compatibility coverage for classic filesystem contract behavior that S3A chooses to support.
