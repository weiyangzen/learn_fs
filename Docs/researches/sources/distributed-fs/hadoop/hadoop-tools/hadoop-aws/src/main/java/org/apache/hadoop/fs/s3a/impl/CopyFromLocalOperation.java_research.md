<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java

## Purpose

`CopyFromLocalOperation` implements S3A's local filesystem copy/upload workflow for files and directories, including empty-directory preservation and optional source deletion.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Void>`. Key methods are `execute()`, `uploadSourceFromFS()`, `submitUpload()`, `submitCreateEmptyDir()`, source/destination checks, `getFinalPath()`, and the `CopyFromLocalOperationCallbacks` interface.

## Control Flow

Execution resolves the local source file, probes destination status, adjusts destination when copying a directory into an existing directory, validates source and overwrite semantics, then scans local files and directories. It uploads the five largest files first, shuffles remaining files, creates markers for empty directories, waits for all submitted futures, and optionally deletes the local source.

## State and Persistence Behavior

Operation state includes source, mutable destination, destination status, flags, callbacks, and a one-thread throttled executor. External side effects are S3 uploads/marker creation and optional local deletion.

## Dependencies and Integration Points

It depends on local filesystem callbacks, S3A store context executors, audit-span-wrapped futures, Hadoop `RemoteIterator`, and `CallableSupplier`.

## Risks and Edge Cases

Destination URI relativization can fail if source and listed paths do not share a URI base. Empty-directory detection depends on traversal order. Upload failures surface only when waiting for futures; source deletion happens only after uploads complete.

## Test Signals

Cover file-to-file, file-to-dir, dir-to-new-dir, dir-to-existing-dir, overwrite rejection, source missing, empty directory creation, nested empty directories, upload failure, delete-source success/failure, and audit span use in async uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CopyFromLocalOperation.java -->
