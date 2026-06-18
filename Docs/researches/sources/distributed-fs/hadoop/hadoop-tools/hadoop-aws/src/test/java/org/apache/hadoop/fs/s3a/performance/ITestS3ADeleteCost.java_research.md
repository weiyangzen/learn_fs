# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ADeleteCost.java

Purpose: integration cost tests for S3A delete and directory-marker cleanup behavior, focusing on request counts and marker state after deleting files and deep directory trees.

Important APIs/types/functions: `ITestS3ADeleteCost` extends `AbstractS3ACostTest`; it uses `verifyMetrics`, `verifyInnerGetFileStatus`, `assertEmptyDirStatus`, `getDeleteMarkerStatistic`, `directoriesInPath`, `verifyNoListing`, and statistics such as `OBJECT_METADATA_REQUESTS`, `OBJECT_LIST_REQUEST`, `OBJECT_DELETE_REQUEST`, `OBJECT_DELETE_OBJECTS`, `DIRECTORIES_CREATED`, `DIRECTORIES_DELETED`, `FILES_DELETED`, and `FAKE_DIRECTORIES_DELETED`.

Control flow: file-delete tests create directories/files, delete one target, then assert file deletion counters and parent directory status. Deep-marker tests create sibling state to avoid parent recreation ambiguity, create nested directories, delete the parent recursively, assert delete-object count, verify no listings remain, and recreate the parent. File-creation marker tests ensure creating a file inside an existing deep marker tree does not delete parent markers.

State and persistence: creates and removes real objects and markers in the test bucket. Teardown explicitly deletes the test directory before superclass teardown to avoid audit failures from leftover markers.

Dependencies/integration: S3A delete implementation, bulk-versus-single marker delete accounting, directory marker statistics, S3A file status `Tristate`, and listing failure behavior.

Risks: exact counters vary with bulk delete configuration; marker recreation/deletion can be affected by sibling objects and store behavior.

Test signals: exact metric diffs, object/delete counters, empty-dir status after file removal, `FileNotFoundException` for removed listings, and successful parent recreation.
