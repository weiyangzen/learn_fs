# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitOperations.java

## Purpose
Implementation of storage-level operations needed by S3A committers: complete pending MPUs, load pending metadata, abort MPUs, stage local files as MPUs, create `_SUCCESS`, revert commits, and collect statistics.

## Important APIs, Types, And Functions
`toPartEtags()` converts persistent `UploadEtag`s to AWS `CompletedPart`s. `commit()` validates a `SinglePendingCommit`, calls `innerCommit()`, records statistics, and returns `MaybeIOE`; `commitOrFail()` rethrows. `loadSinglePendingCommits()` lists and loads `.pending` files in parallel. `abortAllSinglePendingCommits()`, `abortSingleCommit()`, and `abortMultipartCommit()` cancel work. `uploadFileToPendingCommit()` initiates MPU, uploads parts using restartable `UploadContentProviders`, and returns a pending commit. `createSuccessMarker()` writes `SuccessData`.

## Control Flow
Task-side staging calls `uploadFileToPendingCommit()`: initiate MPU, build commit metadata, compute part count, upload each part, bind etags, and abort the MPU on failure. Job-side commit loads pending sets/files, calls `commit()` for each pending entry, and may revert or abort on failure. Abort paths list pending files or S3 multipart uploads and cancel them.

## State And Persistence
Holds destination `S3AFileSystem`, `WriteOperations`, and `CommitterStatistics`. It reads/writes `SinglePendingCommit`, `PendingSet`, and `SuccessData` but does not own their lifecycle after returning.

## Dependencies And Integration Points
Central integration point for S3A write helper APIs, AWS SDK MPU objects, Hadoop filesystem listing/deletion, `TaskPool`, IO statistics tracking, and committer statistics symbols.

## Risks
Upload part sizing must respect S3 part-count limits; failures must abort initiated MPUs to avoid leaks. Pending-file load failures are collected and must trigger aborts upstream. `MaybeIOE` preserves first failure behavior, so multi-file commit callers must decide rollback policy.

## Test Signals
Unit and integration coverage should include successful MPU commit, failed part upload cleanup, too-many-parts rejection, empty file upload, pending-file load failures, abort listing, success marker metrics, magic file length xattr extraction, and statistics counters.
