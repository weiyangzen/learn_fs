# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRename.java

Purpose: S3A rename contract tests with object-store-specific expectations and copy-stat assertions.

Important APIs/types/functions: extends `AbstractContractRenameTest`; timeout is `S3A_TEST_TIMEOUT`. Overrides `testRenameDirIntoExistingDir()` to assert S3A returns false when renaming into a non-empty directory. Adds `testRenamePopulatesFileAncestors2()` and skips `testRenameFileUnderFileSubdir()`.

Control flow: the ancestor test creates nested source file data, captures `FILES_COPIED` and `FILES_COPIED_BYTES` metric diffs, renames `src` to `dest`, asserts one copied file and byte count, lists the tree, verifies contents, and validates ancestors moved.

State and persistence: creates source/destination directory trees and performs S3A rename, which is implemented as copy/delete.

Dependencies and integration: S3A metrics, contract rename utilities, and `S3ATestUtils.lsR`.

Risks: rename is non-atomic and copy-based; metrics are implementation-sensitive. Deep paths under files are allowed in S3A and skipped from strict contract expectations.

Test signals: integration coverage for rename rejection, ancestor materialization, data integrity, and copy counters.
