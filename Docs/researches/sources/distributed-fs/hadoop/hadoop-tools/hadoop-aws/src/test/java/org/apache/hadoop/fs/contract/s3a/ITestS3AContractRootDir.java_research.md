# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRootDir.java

Purpose: binds root-directory contract tests to S3A bucket roots.

Important APIs/types/functions: extends `AbstractContractRootDirectoryTest`; setup calls `maybeSkipRootTests(conf)` after superclass setup. `getFileSystem()` narrows to `S3AFileSystem`. `testRmNonEmptyRootDirNonRecursive()` is disabled because S3 returns false for non-recursive root removal.

Control flow: inherited tests run unless root tests are disabled by configuration; one incompatible inherited test is explicitly disabled.

State and persistence: root operations may touch bucket root and therefore are guarded.

Dependencies and integration: S3A root-test skip utility and contract root suite.

Risks: root tests can be destructive or expensive against real buckets, making skip configuration important.

Test signals: integration coverage for safe root-directory operations with one known S3 behavior disabled.
