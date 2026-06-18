# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OperationCallbacks.java

## Purpose
`OperationCallbacks` defines the filesystem callbacks needed by store operations such as `RenameOperation` and `DeleteOperation`, allowing those operations to be tested and executed without tight direct coupling to the full `S3AFileSystem`.

## Important APIs and Types
The interface exposes callbacks for object attribute construction, read context creation, rename completion cleanup, single-object delete, recursive listing including directory markers, object copy, bulk key removal, object listing, and optional multipart-upload abortion under a prefix. Retry annotations document expected retry/translation behavior.

## Control Flow
Implementations are invoked by higher-level operations in copy/list/delete sequences. `RenameOperation` uses attributes/read contexts before copy, queues deletes through `removeKeys()`, and calls `finishRename()` once the destination has been created. The default `abortMultipartUploadsUnderPrefix()` returns zero so implementations opt in to upload purging.

## State and Persistence
The interface stores no state, but implementations perform persistent object-store mutations: delete, copy, bulk delete, directory marker cleanup, and multipart upload aborts.

## Dependencies and Integration Points
It uses AWS SDK v2 `CopyObjectResponse`, `ObjectIdentifier`, and `AwsServiceException`, plus Hadoop `Path`, `RemoteIterator`, S3A statuses, `S3ObjectAttributes`, and `S3AReadOpContext`. It is the main seam between store operations and concrete filesystem behavior.

## Risks and Edge Cases
Misimplemented callbacks can break rename atomicity expectations because S3A rename is copy-then-delete. `removeKeys()` must handle empty lists, root delete protection, and partial failures. Listing must include directory markers when requested or marker cleanup will be incorrect. Default multipart abort no-op means callers must explicitly configure implementations for purging pending uploads.

## Test Signals
Mock callback tests should assert call order during rename, correct copy source attributes, delete batching, marker listing behavior, translated exception paths, and multipart abort counts when enabled or disabled.
