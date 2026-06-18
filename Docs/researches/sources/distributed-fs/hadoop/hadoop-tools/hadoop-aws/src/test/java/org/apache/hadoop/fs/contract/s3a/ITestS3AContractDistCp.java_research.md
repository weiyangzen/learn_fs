# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDistCp.java

Purpose: validates DistCp behavior against S3A, especially direct-write behavior that avoids rename-heavy commit flows.

Important APIs/types/functions: extends `AbstractContractDistCpTest`; configures multipart size to `MULTIPART_MIN_SIZE` and `FAST_UPLOAD_BUFFER_DISK`; returns `shouldUseDirectWrite() == true`; uses scale-test timeout. `getRenameOperationCount()` reads `OP_RENAME` from storage statistics.

Control flow: `testDistCpWithIterator()` records rename count, runs superclass direct-write test, and asserts no rename increase. `testNonDirectWrite()` expects exactly two renames. Update/check-file skip delegates to superclass.

State and persistence: writes DistCp source/destination paths and reads FS storage statistics.

Dependencies and integration: integrates Hadoop DistCp contract tests, S3A multipart upload configuration, disk buffering, and storage statistics.

Risks: rename counts are implementation-sensitive. Disk buffering is chosen for scalability and may behave differently from array/bytebuffer buffering.

Test signals: integration coverage for DistCp direct-write/no-rename and non-direct-write rename behavior.
