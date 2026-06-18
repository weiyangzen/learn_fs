# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ARenameCost.java

Purpose: integration cost tests for S3A file rename and root-file delete/rename behavior.

Important APIs/types/functions: `ITestS3ARenameCost` extends `AbstractS3ACostTest`; it uses `OperationCost.RENAME_SINGLE_FILE_DIFFERENT_DIR`, `RENAME_SINGLE_FILE_SAME_DIR`, `GET_FILE_STATUS_FNFE`, `COPY_OP`, `FILE_STATUS_FILE_PROBE`, and metrics including `OBJECT_COPY_REQUESTS`, `OBJECT_DELETE_REQUEST`, `OBJECT_DELETE_OBJECTS`, `FILES_DELETED`, and directory-marker counters.

Control flow: different-directory rename creates a deep source directory with a second sibling source file so the parent should remain, creates destination parents, renames one file, then verifies request-cost and namespace outcomes. Same-directory rename verifies a lower-cost copy/delete path. Root rename/delete use UUID root paths and `finally` cleanup to assert no parent directory marker operations happen at root.

State and persistence: creates real S3A files/directories and performs copy/delete-based rename. Root tests deliberately write to `/src-uuid` and `/dest-uuid` to avoid parallel collision.

Dependencies/integration: S3A rename implementation, copy metadata read cost, directory-marker recreation/deletion logic, and metric validator helpers.

Risks: exact costs depend on status-probe sequence and marker policy; root path tests must clean up even on assertion failure.

Test signals: exact metric diffs, successful rename boolean, file/directory existence checks, and absence of source paths after rename.
