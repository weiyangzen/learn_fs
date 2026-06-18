# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlocksize.java

Purpose: validates S3A block-size configuration as exposed through file status and listings.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `testBlockSize()` checks default block size, updates `FS_S3A_BLOCK_SIZE`, creates a file, checks `getFileStatus()` and `listStatus()` block size. `testRootFileStatusHasBlocksize()` checks root status has nonnegative block size.

Control flow: after changing conf in the live FS, the test writes a file under a directory, then scans the listing to find and assert that file's block size.

State and persistence: writes one file and mutates FS configuration for the test.

Dependencies and integration: S3A block-size constant, `FileStatus`, and contract test utilities.

Risks: changing conf on an initialized FS assumes block-size lookup reads current config dynamically.

Test signals: integration coverage for block size propagation through status APIs.
