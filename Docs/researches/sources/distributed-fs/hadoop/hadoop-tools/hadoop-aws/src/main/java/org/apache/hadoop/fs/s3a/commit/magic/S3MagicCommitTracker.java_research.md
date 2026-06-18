# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/S3MagicCommitTracker.java

## Purpose
Magic commit tracker that persists commit metadata to S3. It writes a zero-byte magic marker at the original under-magic key and a serialized `SinglePendingCommit` at the pending metadata key.

## Important APIs, Types, And Functions
`aboutToComplete()` validates upload ID and parts, PUTs a marker with the final file length header, builds `SinglePendingCommit`, serializes it, and PUTs it to `pendingPartKey`. Private `upload()` wraps `WriteOperationHelper.putObject()` with retry translation and `COMMITTER_MAGIC_MARKER_PUT` duration tracking.

## Control Flow
On stream close, the marker is written first, then the commit metadata file. The method returns false to stop immediate MPU completion. Task commit later lists and loads `.pending` files from the magic attempt tree.

## State And Persistence
Persists the marker object and pending metadata object in S3. The pending metadata carries final key, upload ID, etags, length, bucket, URI, and IO statistics snapshot.

## Dependencies And Integration Points
Extends `MagicCommitTracker`; uses `WriteOperationHelper`, `PutObjectOptions`, `WriteObjectFlags`, `S3ADataBlocks`, `SinglePendingCommit`, and magic marker headers.

## Risks
If marker PUT succeeds but metadata PUT fails, an incomplete MPU and marker may remain until abort/cleanup. Marker length is carried in headers/xattrs and consumers must handle missing or unparsable values.

## Test Signals
Verify marker creation, pending metadata serialization, false completion return, retry/statistics tracking, failure after marker PUT, and later task commit loading of generated `.pending` files.
