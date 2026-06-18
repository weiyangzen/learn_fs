# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestEMRFSCompatibility.java

Purpose: verifies S3A compatibility with legacy S3N/EMRFS folder marker objects.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `testFileSystemOperationWithS3NFolderMarker()` creates a marker named with `S3N_FOLDER_SUFFIX`, lists the directory, renames the parent, and checks source/destination state.

Control flow: touches `src/subdir_$folder$` style marker, asserts listing `subdir` is empty, renames `src` to `dest`, then checks `dest/subdir` exists and `src` no longer exists.

State and persistence: creates a legacy folder marker and performs rename in the test bucket.

Dependencies and integration: S3A rename/list semantics and S3N folder marker constant.

Risks: marker compatibility is object-key-convention sensitive. Rename over markers depends on S3A marker filtering.

Test signals: integration coverage for legacy marker filtering and rename compatibility.
