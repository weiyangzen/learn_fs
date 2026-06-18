<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java

## Purpose

`DeleteOperation` implements S3A file and directory deletion, including recursive tree deletion, directory marker handling, batched multi-delete, and optional multipart upload purge.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Boolean>`. Key methods are `execute()`, `deleteDirectoryTree()`, `queueForDeletion()`, `submitNextBatch()`, `deleteObjectAtPath()`, `submitDelete()`, and `asyncDeleteAction()`.

## Control Flow

`execute()` enforces single execution, classifies the pre-fetched status, refuses root deletion, rejects non-recursive deletion of non-empty directories, deletes empty directory markers directly, or lists and batches recursive children. Directory-tree deletion can concurrently abort uploads under the prefix, lists files and markers, submits one delete batch at a time, waits for prior batches before submitting the next, and splits file objects from directory markers for callback statistics.

## State and Persistence Behavior

Mutable state tracks current batch keys, pending delete future, deleted-file count, and optional aborted-upload count. Side effects are S3 object deletes and optional multipart upload aborts.

## Dependencies and Integration Points

It uses `OperationCallbacks`, S3A statuses, `CallableSupplier`, audit spans, S3 `ObjectIdentifier`, throttled executors, and S3A constants for max delete entries.

## Risks and Edge Cases

The operation requires directory emptiness to be known. Only one delete batch runs at a time to reduce recovery complexity. `filesDeleted` is incremented before async delete completion, so failed operations can leave counters ahead of actual S3 state.

## Test Signals

Cover root deletion, file deletion, empty directory deletion, recursive and non-recursive directory cases, page-size batching, previous-batch failure propagation, upload purge success/failure, marker/file split, and single-execute enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/DeleteOperation.java -->
