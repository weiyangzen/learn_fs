# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AFSMainOperations.java

Purpose: Runs Hadoop `FSMainOperationsBaseTest` against S3A, with S3-specific exclusions and overwrite behavior adjusted for create-performance mode.

Important APIs/types/functions: `FSMainOperationsBaseTest`, `S3AContract`, `S3ATestUtils.createTestPath()`, `setPerformanceFlags()`, and `isCreatePerformanceEnabled()`.

Control flow: constructor passes a stable S3A base path. `createFileSystem()` creates and initializes an `S3AContract`. Tests for unreadable dirs and raw local copy are disabled because S3A lacks POSIX permissions or setup is broken. Block write/read/delete tests call the superclass. `testOverwrite()` runs the superclass and swallows the assertion only when create-performance mode is enabled.

State and persistence: inherited tests create remote objects under `/ITestS3AFSMainOperations`. The `contract` field owns the test filesystem instance.

Dependencies and integration points: Hadoop main filesystem operation contract, S3A contract implementation, and create-performance feature behavior.

Risks: superclass assumptions may not match object-store semantics; create-performance mode changes overwrite semantics enough to require conditional handling; disabled tests reduce permission coverage.

Test signals: broad compatibility signal for common FileSystem operations on S3A.
