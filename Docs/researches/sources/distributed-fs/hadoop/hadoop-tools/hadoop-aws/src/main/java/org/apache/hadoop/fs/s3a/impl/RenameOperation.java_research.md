# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RenameOperation.java

## Purpose
`RenameOperation` implements S3A rename as a copy-then-delete workflow. It supports file renames, recursive directory renames, directory-marker handling, batched source deletion, bounded parallel copy submission, and optional abort of pending multipart uploads under renamed directory prefixes.

## Important APIs and Types
- Constructor captures source/destination paths and keys, source/destination statuses, `OperationCallbacks`, delete page size, and upload purge policy.
- `execute()` runs the operation once and returns copied byte count.
- `renameFileToDest()` handles single-file source rename, including `rename(file, dir)` semantics.
- `recursiveDirectoryRename()` lists source tree entries, copies files and leaf markers, queues deletes, and waits on copy/delete batches.
- `initiateCopy()` submits copy tasks into the store executor while preserving audit span.
- `getUploadsAborted()` reports optional multipart upload abort count after successful directory rename.

## Control Flow
For file sources, it builds source attributes/read context, adjusts destination under an existing directory if needed, copies the source object, increments byte count, deletes the source object, and returns the actual destination path. For directory sources, it normalizes source/destination keys with trailing slashes, rejects destination inside source, optionally starts async multipart upload abort under the source prefix, removes an empty destination marker, lists source files and directory markers recursively, tracks markers with `DirMarkerTracker`, copies files to corresponding destination keys, queues copied sources for batched deletion, and triggers batch waits when active copies reach `RENAME_PARALLEL_LIMIT` or queued deletes reach `pageSize`. After iteration, it copies only leaf directory markers, deletes remaining sources, waits for upload purge, and calls `finishRename()`.

## State and Persistence
Operation-local mutable state includes `bytesCopied`, `activeCopies`, `keysToDelete`, and `uploadsAborted`. Persistent effects are S3 COPY operations, source object deletes, destination marker deletion, source marker cleanup, and optional multipart upload aborts. The operation is guarded by `executeOnlyOnce()`.

## Dependencies and Integration Points
It extends `ExecutingStoreOperation<Long>` and depends on `StoreContext`, `OperationCallbacks`, `DirMarkerTracker`, `S3ALocatedFileStatus`, `S3ObjectAttributes`, `S3AReadOpContext`, AWS `ObjectIdentifier`, `SdkException`, and auditing helper `callableWithinAuditSpan`. It integrates with S3A listing, copy, delete, and marker policy code.

## Risks and Edge Cases
S3 rename is not atomic; failures may leave copied destination objects and undeleted sources. The code waits for active copies before deleting queued sources, but bytes copied for directory files adds `sourceStatus.getLen()` rather than each child length, which is suspicious for metrics. Marker handling intentionally does not copy non-leaf markers. Root/key normalization and destination-under-source validation are critical. Exception conversion must preserve S3 service failure semantics. Optional multipart upload purge runs concurrently and failures are ignored through `waitForCompletionIgnoringExceptions()`.

## Test Signals
Tests should cover file-to-file, file-to-directory, directory-to-directory, destination inside source rejection, delete pagination, active copy batching, marker deletion/copy rules, empty destination marker removal, upload purge enabled/disabled, exception conversion, and audit-span propagation to copy workers.
