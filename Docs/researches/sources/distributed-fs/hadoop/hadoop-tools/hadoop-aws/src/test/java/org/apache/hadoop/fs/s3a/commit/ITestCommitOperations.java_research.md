# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperations.java

## Purpose
Integration tests for the low-level S3A magic commit binding and `CommitOperations` behavior. The suite verifies magic path detection, marker/pending metadata creation, single and bulk multipart commit, abort/revert handling, upload-from-local staging, committer factory selection, and the distinction between normal and magic output streams.

## Important APIs, Types, and Functions
The class extends `AbstractCommitITest` and binds the S3A committer factory to `COMMITTER_NAME_MAGIC` in `createConfiguration()`. `setup()` closes cached filesystems, requires multipart uploads, verifies a magic-capable S3A filesystem, and resets a `ProgressCounter`. Helper methods include `newCommitOperations()`, `makeMagic(Path)`, `createCommitAndVerify()`, `commit()`, `commitOrFail()`, and `validatePendingCommitData()`. The test directly uses `MagicCommitIntegration`, `MagicCommitTracker`, `CommitOperations`, `CommitContext`, `SinglePendingCommit`, `UploadEtag`, `FSDataOutputStreamBuilder`, and `PathOutputCommitterFactory`.

## Control Flow and Behavior
Magic path tests build paths under `__magic/<job-id>/...`, split and reconstruct path elements through `MagicCommitPaths`, and assert that `MagicCommitIntegration.createTracker()` returns `MagicCommitTracker` only for real magic destinations. Commit tests write empty and small files to magic paths, verify zero-byte marker headers plus `.pending` JSON, load `SinglePendingCommit`, and complete it through `CommitContext.commitOrFail()`. Abort tests call `abortAllSinglePendingCommits()` or `abortPendingUploadsUnderPath()` and verify pending metadata and destination files are absent. Upload tests use `uploadFileToPendingCommit()` against local temp files, check progress callbacks, then complete the pending MPU. Bulk commit tests reuse one `CommitContext` for multiple pending commits and verify parent/subdirectory materialization.

## State, Persistence, and Dependencies
State is persisted in S3 as marker files and `.pending` JSON sidecars containing timestamps, destination keys, upload IDs, and `UploadEtag` part lists. Local temp files are used as upload sources. The suite depends on real S3A multipart upload support, commit constants such as `MAGIC_PATH_PREFIX`, `BASE`, `PENDING_SUFFIX`, S3A stream capability `STREAM_CAPABILITY_MAGIC_OUTPUT`, and test helpers from `ContractTestUtils`, `S3ATestUtils`, and `CommitterTestHelper`.

## Integration Points, Risks, and Test Signals
This is a high-signal integration suite for regressions in magic commit path parsing, pending metadata serialization, marker header handling, factory binding, upload abort cleanup, and local-to-S3 staged commit. Risks include dependence on S3 semantics, storage-class differences such as S3 Express directory visibility, stale pending uploads after interrupted runs, and behavior changes in multipart commit retry semantics. Passing tests demonstrate that magic writes remain invisible until committed and that normal S3A streams are not accidentally treated as magic output.
