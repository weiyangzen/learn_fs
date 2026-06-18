# Research: subset-b-007579

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/MagicCommitPaths.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/MagicCommitPaths.java

## Purpose
Utility methods for interpreting S3A "magic" committer paths. It treats a Hadoop `Path` as ordered URI path elements, detects the `__magic` prefix, separates parent and child components, honors the `__base` marker, and computes the final destination key for data written under magic task-attempt directories.

## Important APIs, Types, And Functions
`splitPathToElements()` validates absolute non-empty paths and returns path elements. `isMagicPath()`, `magicElementIndex()`, `magicPathParents()`, and `magicPathChildren()` locate the magic segment. `basePathChildren()` handles `CommitConstants.BASE`. `elementsToKey()`, `filename()`, `lastElement()`, and `finalDestination()` build S3 keys and final file destinations.

## Control Flow
Callers split the path, test whether it is magic, then call `finalDestination()`. For magic paths, final output is the magic path parent plus either all children under `__base` or just the last child filename, which discards job and task attempt path components. Non-magic paths are returned unchanged.

## State And Persistence
The class is stateless. It returns list views via `subList()` in some helpers, so callers must treat returned lists as immutable as documented.

## Dependencies And Integration Points
Used by `MagicCommitIntegration`, magic tracker utilities, and any S3A path-to-key logic that must map a magic write path to its true S3 object key. Depends on `CommitConstants.MAGIC_PATH_PREFIX`, `BASE`, and `InternalCommitterConstants.E_NO_MAGIC_PATH_ELEMENT`.

## Risks
Malformed magic paths fail with `IllegalArgumentException`; path shape changes must keep `__base` and child conventions aligned with MapReduce magic path construction. Because some returns are list views, accidental mutation by callers could corrupt derived path state.

## Test Signals
Cover root, relative, empty, non-magic, magic-without-child, magic-with-children, and magic-with-`__base` paths. Verify final key flattening and unflattening preserve expected partition paths and reject malformed inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/MagicCommitPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PathCommitException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PathCommitException.java

## Purpose
Small commit-specific exception type for path-scoped failures in S3A commit protocols. It keeps failures compatible with Hadoop `PathIOException` while giving committer code a clearer domain exception.

## Important APIs, Types, And Functions
`PathCommitException` extends `PathIOException` and offers constructors for string paths, `Path` instances, message-only errors, causes, and wrapped message-plus-cause failures.

## Control Flow
Committer code throws this when factory selection, destination conflict handling, validation wrapping, or commit operation conversion needs an `IOException` carrying the affected path.

## State And Persistence
No persistent state beyond the path, message, and cause stored by the superclass.

## Dependencies And Integration Points
Used by `S3ACommitterFactory`, staging committers, and `CommitOperations.makeIOE()` to normalize unexpected exceptions into Hadoop IO exceptions.

## Risks
Path may be empty when constructed from a null `Path`, so diagnostics depend on callers passing meaningful origin paths.

## Test Signals
Check message/path formatting for string and `Path` constructors and verify wrapped causes survive through `IOException` handling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PathCommitException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PutTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PutTracker.java

## Purpose
Base callback object attached to multipart output streams. The default implementation represents ordinary uploads where final multipart completion happens when the stream closes and output is immediately visible.

## Important APIs, Types, And Functions
`initialize()` returns whether MPU should start immediately; default false. `outputImmediatelyVisible()` defaults true. `aboutToComplete(uploadId, parts, bytesWritten, iostatistics)` defaults true, telling the stream to complete the MPU. `getDestKey()` returns the S3 key used by PUT/MPU operations.

## Control Flow
An output stream creates or receives a tracker, calls `initialize()` before upload setup, writes parts, then calls `aboutToComplete()` near close. Subclasses such as `MagicCommitTracker` override these hooks to delay final visibility and write commit metadata instead of completing the MPU.

## State And Persistence
Only stores `destKey`. It does not persist commit metadata or track upload parts itself.

## Dependencies And Integration Points
Integrated with S3A write streams and magic committer subclasses; consumes AWS SDK `CompletedPart` lists and optional `IOStatistics`.

## Risks
The default behavior is intentionally permissive. Any delayed-commit implementation must override both visibility and completion behavior consistently or files may become visible too early.

## Test Signals
Verify default trackers cause normal MPU completion, expose the original key, and report immediate visibility. Subclass tests should assert overridden return values drive stream close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/PutTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/S3ACommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/S3ACommitterFactory.java

## Purpose
MapReduce `PathOutputCommitter` factory for S3A. It selects the concrete S3A committer from configuration, falling back to the classic `FileOutputCommitter` when the file committer or an empty name is configured.

## Important APIs, Types, And Functions
`CLASSNAME` is the fully qualified factory name used in job configuration. `createTaskCommitter()` calls `chooseCommitterFactory()` and delegates to `DirectoryStagingCommitterFactory`, `PartitionedStagingCommitterFactory`, `MagicS3GuardCommitterFactory`, or test-only `StagingCommitterFactory`; unknown names raise `PathCommitException`.

## Control Flow
Selection first reads the resolved filesystem configuration, then lets the task/job configuration override `fs.s3a.committer.name`. Known committer names produce factory instances; `file` and empty produce null, triggering the standard file committer path and a warning about safety/performance.

## State And Persistence
Stateless. It relies on per-bucket configuration already resolved into the destination `S3AFileSystem` configuration.

## Dependencies And Integration Points
Connects Hadoop MapReduce output committer creation to S3A-specific committers. Depends on `AbstractS3ACommitterFactory`, committer name constants, and the destination `S3AFileSystem`.

## Risks
Misconfiguration silently falls back only for empty/file names; typos fail fast. The factory explicitly does not verify filesystem compatibility, so magic committer requirements are enforced later by the concrete committer.

## Test Signals
Exercise all configured names, task-config override precedence, unknown-name failures, logging of selected committers, and fallback behavior for empty/file committer names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/S3ACommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/ValidationFailure.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/ValidationFailure.java

## Purpose
Checked validation exception used by persisted commit data loaders and serializers. It is an `IOException` so invalid commit metadata flows through existing IO failure paths.

## Important APIs, Types, And Functions
`ValidationFailure(String, Object...)` formats messages. Static `verify(boolean, String, Object...)` throws `ValidationFailure` when a precondition is false.

## Control Flow
Persistent data classes call `verify()` during `validate()` and Java deserialization hooks. Failures abort loading, committing, or saving pending commit metadata.

## State And Persistence
No extra state beyond the formatted exception message.

## Dependencies And Integration Points
Used heavily by `SinglePendingCommit`, `PendingSet`, and `SuccessData`; those classes surface validation problems as IO failures to commit protocols.

## Risks
Validation messages use `String.format()`, so invalid format strings in callers would mask the original validation intent.

## Test Signals
Validate success/failure branches and ensure bad persistent data yields `ValidationFailure` rather than unchecked exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/ValidationFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PendingSet.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PendingSet.java

## Purpose
Persistent JSON/Java-serializable container for multiple `SinglePendingCommit` entries. It is the manifest that staging and magic task commits hand to the job committer for final multipart completion.

## Important APIs, Types, And Functions
`VERSION` is 3. `serializer()` returns a Jackson `JsonSerialization`. `load()` reads and validates a file. `add()` appends a single commit, aggregates its IO statistics into the set, and clears the child statistics. `validate()` checks version, map element types, commit element types, child validity, and duplicate destination keys.

## Control Flow
Task committers build a `PendingSet`, add all uploaded pending commits, attach task metadata in `extraData`, and save it. Job committers later load all sets, validate uniqueness, and commit or abort each entry.

## State And Persistence
Persists `version`, `jobId`, `commits`, `extraData`, and an `IOStatisticsSnapshot`. Duplicate destination detection is validation-only, not enforced at insertion time.

## Dependencies And Integration Points
Extends `PersistentCommitData`; contains `SinglePendingCommit`; used by `StagingCommitter`, `MagicS3GuardCommitter`, `CommitOperations.loadSinglePendingCommits()`, and `CommitContext` serializer pools.

## Risks
Duplicate destination keys fail at validation, so bad manifests can be written if callers bypass validation before save. `add()` clears child IO statistics after aggregation, which is intentional but can surprise code expecting child stats to remain.

## Test Signals
Round-trip empty and populated sets, duplicate-destination rejection, bad version rejection, extra-data type validation, IO statistics aggregation/clearing, and load failure handling in job commit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PendingSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PersistentCommitData.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PersistentCommitData.java

## Purpose
Base class for committer persistent formats. It standardizes validation, JSON serialization to bytes, save/load through Hadoop `FileSystem`, and `IOStatisticsSource` publication.

## Important APIs, Types, And Functions
Subclasses implement `validate()`, `toBytes()`, and `save()`. Static `load(fs, status, serializer)` deserializes and validates. `saveFile()` builds a recursive overwrite `createFile()` operation and sets `FS_S3A_CREATE_PERFORMANCE`; `saveToStream()` writes serialized bytes and returns stream IO statistics.

## Control Flow
Commit data subclasses call `saveFile()` from their `save()` implementations. Job and task committers call type-specific `load()` methods or base `load()` when iterating manifests.

## State And Persistence
The base class has no instance fields. It defines a common version constant for subclasses that use it and marks the hierarchy `Serializable`.

## Dependencies And Integration Points
Used by `SinglePendingCommit`, `PendingSet`, and `SuccessData`; depends on Hadoop `JsonSerialization`, `FSDataOutputStreamBuilder`, and S3A create-performance option.

## Risks
`saveToStream()` writes serializer bytes directly without calling `validate()` itself; subclasses must perform preflight validation in `toBytes()` or before invoking save. Performance mode intentionally skips some S3A safety checks.

## Test Signals
Verify save/load round trips on local and S3A filesystems, IO statistics propagation, overwrite behavior, recursive creation, and invalid data rejection after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/PersistentCommitData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SinglePendingCommit.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SinglePendingCommit.java

## Purpose
Persistent representation of one uncommitted multipart upload. It records enough S3 state for a later job committer to complete or abort an MPU after task output has been staged.

## Important APIs, Types, And Functions
Fields include version, source filename, destination URI, upload ID, bucket, destination key, timestamps, job/task IDs, notes, ordered `UploadEtag` list, extra data, IO statistics, and length. `load()` deserializes and validates. `touch()` sets timestamps. `bindCommitData()` converts ordered AWS `CompletedPart` values to `UploadEtag`s and verifies part numbering. `destinationPath()` reconstructs the Hadoop destination path.

## Control Flow
Magic trackers and staging uploads create an instance after MPU parts are uploaded, bind part metadata, save it directly or inside a `PendingSet`, then return false from the tracker or defer final commit. Job commit later calls `CommitOperations.commit()` with this object.

## State And Persistence
All fields except the processing-oriented `filename` are persistent JSON/Java-serialized metadata. Validation requires non-empty bucket, destination key, upload ID, nonnegative length, valid URI, non-null etag list, and string-only extra-data maps.

## Dependencies And Integration Points
Extends `PersistentCommitData`, implements `Iterable<UploadEtag>`, integrates with AWS SDK `CompletedPart`, `CommitOperations.toPartEtags()`, `PendingSet`, magic trackers, and staging committers.

## Risks
Correct part ordering is critical; S3 completion will fail or corrupt semantics if etags are missing or out of order. URI parsing failures are surfaced as validation failures. The `filename` value is runtime diagnostic state and should not be trusted from persisted content.

## Test Signals
Round-trip JSON and Java serialization, invalid version/URI/upload ID/etag cases, checksum retention through `UploadEtag`, zero-length one-part uploads, and commit/abort flows using loaded instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SinglePendingCommit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SuccessData.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SuccessData.java

## Purpose
JSON format written to `_SUCCESS` by S3A committers. It identifies the committer, job, host, committed filenames, metrics, diagnostics, state, stage, and IO statistics, and is intended to remain compatible with the manifest committer success format.

## Important APIs, Types, And Functions
`VERSION` is 1 and `NAME` embeds the format identity. `validate()` requires the exact name. `save()` forces the name before writing. `load()` reads and validates. `dumpMetrics()`, `dumpDiagnostics()`, and `joinMap()` produce sorted text reports. `recordJobFailure()` marks failure and stores exception text plus stack trace.

## Control Flow
After successful job commit, `CommitOperations.createSuccessMarker()` may add filesystem metrics and save `SuccessData` to output `_SUCCESS`. Abort or diagnostic paths may write failure summaries elsewhere.

## State And Persistence
Persists public-facing JSON fields: success flag, timestamp/date, hostname, committer, description, job ID and source, metrics, diagnostics, filenames, IO statistics, state, and stage.

## Dependencies And Integration Points
Extends `PersistentCommitData`; used by committers and tests to distinguish S3A committers from classic zero-length `_SUCCESS` markers.

## Risks
The JSON format is compatibility-sensitive. Large jobs intentionally cap filename lists elsewhere, so consumers must not infer complete output inventory from this file.

## Test Signals
Read classic empty marker versus loadable `SuccessData`, validate incompatible names, ensure sorted metric/diagnostic dumps, verify failure diagnostics capture exceptions, and confirm manifest-format compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SuccessData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/UploadEtag.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/UploadEtag.java

## Purpose
Serializable storage for the ETag and optional checksum associated with one completed multipart-upload part.

## Important APIs, Types, And Functions
Fields are `etag`, `checksumAlgorithm`, and `checksum`. `fromCompletedPart()` extracts ETag plus the first matching checksum in CRC32, CRC32C, SHA1, SHA256 order of checks. `toCompletedPart()` rebuilds an AWS SDK `CompletedPart` for a supplied part number.

## Control Flow
`SinglePendingCommit.bindCommitData()` converts uploaded `CompletedPart` responses into `UploadEtag`s. Final commit converts them back through `CommitOperations.toPartEtags()` before `CompleteMultipartUpload`.

## State And Persistence
Each instance is Java-serializable and JSON-friendly. Only one checksum algorithm/value pair is stored even though `CompletedPart` can expose multiple checksum fields.

## Dependencies And Integration Points
Integrates with AWS SDK `CompletedPart` and `ChecksumAlgorithm`; used only through persistent commit metadata.

## Risks
If AWS returns multiple checksum fields, later checks overwrite earlier ones in `fromCompletedPart()`. Unknown checksum algorithm strings are ignored when rebuilding `CompletedPart`, retaining only the ETag.

## Test Signals
Round-trip each supported checksum type, null-checksum parts, invalid/unknown algorithm handling, and preservation of part numbering assigned by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/UploadEtag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/package-info.java

## Purpose
Package documentation and stability annotations for committer persistent data formats.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit.files` as private and unstable. The Javadoc identifies `PersistentCommitData` as the common base and describes single pending commits, multiple-file pending sets, and `_SUCCESS` summary data.

## Control Flow
No executable control flow.

## State And Persistence
Documents the JSON formats that become part of commit state exchange between tasks and job committers, and the visible `SuccessData` marker after completion.

## Dependencies And Integration Points
References `PersistentCommitData` and `SuccessData`, including compatibility with manifest committer success data.

## Risks
The package is marked unstable, but some JSON payloads are effectively interoperable with other committers; changes should preserve expected compatibility where documented.

## Test Signals
Javadoc/package annotation checks and compatibility tests around `SuccessData` and pending metadata formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/AuditContextUpdater.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/AuditContextUpdater.java

## Purpose
Thread-local audit context helper for commit operations. It attaches MapReduce job and task-attempt identifiers to the current S3A audit context and removes them when work completes.

## Important APIs, Types, And Functions
Constructors accept a `JobContext` or explicit job ID. `updateCurrentAuditContext()` sets or removes job/task keys on `CommonAuditContext.currentAuditContext()`. `resetCurrentAuditContext()` clears both fields.

## Control Flow
`CommitContext` creates an updater, applies it to the caller thread, and wraps worker-thread submissions so each task updates audit context before running and resets it afterward.

## State And Persistence
Stores immutable `jobId` and optional `taskAttemptId`. No persistent state; all effects are thread-local audit attributes.

## Dependencies And Integration Points
Depends on Hadoop audit constants, `CommonAuditContext`, MapReduce job/task contexts, and `CommitConstants.PARAM_TASK_ATTEMPT_ID`.

## Risks
Correct reset is important in thread pools; leaked audit attributes would misattribute later filesystem operations. The class removes task-attempt ID using the committer constant key, so key consistency with audit constants matters.

## Test Signals
Verify job-only, task-attempt, null-job, update, reset, and worker-thread wrapping behavior in `CommitContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/AuditContextUpdater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitContext.java

## Purpose
Closeable execution context for task and job commit operations. It owns commit-operation callbacks, serializer pools, optional worker thread pools, job identity, audit context propagation, and IO statistics context sharing.

## Important APIs, Types, And Functions
Constructors bind real `JobContext` or testing configuration. `commitOrFail()`, `commit()`, `abortSingleCommit()`, `revertCommit()`, and `abortMultipartCommit()` delegate to `CommitOperations`. `getOuterSubmitter()` and `getInnerSubmitter()` expose `TaskPool` submitters. Serializer accessors provide per-thread `JsonSerialization` instances backed by `WeakReferenceThreadMap`.

## Control Flow
Construction computes job ID, decides whether to collect IO statistics, updates the current audit context, and creates the outer pool when thread count is nonzero. Inner pool is lazy. Submitted work is wrapped to update/reset audit context. `close()` shuts down pools and resets the caller audit context.

## State And Persistence
Holds runtime-only thread pools, serializers, configuration, job ID, audit updater, and shared `IOStatisticsContext`. No commit data is persisted here; it coordinates persisted `PendingSet` and `SinglePendingCommit` serializers.

## Dependencies And Integration Points
Used by `AbstractS3ACommitter`, `CommitOperations`, magic and staging committers, Hadoop `TaskPool`, S3A audit context, and IO statistics collection.

## Risks
Thread counts can be negative to mean CPU multiples; zero disables pools. Callers must close contexts to avoid leaked audit context and executors. Weak serializer references can be recreated, so serializers must remain stateless.

## Test Signals
Exercise zero, positive, and negative thread counts; close idempotence; audit propagation in worker threads; IO statistics reset/switch; serializer availability; and delegated commit/abort methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitOperations.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitUtilsWithMR.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitUtilsWithMR.java

## Purpose
MapReduce-dependent committer utility methods. It isolates MR imports from lower-level S3A filesystem code and builds standard magic/temp job and task attempt paths.

## Important APIs, Types, And Functions
`getMagicJobAttemptsPath()`, `getMagicJobAttemptPath()`, `getMagicTaskAttemptsPath()`, `getMagicTaskAttemptPath()`, and `getBaseMagicTaskAttemptPath()` construct magic paths. `getTempJobAttemptPath()` and `getTempTaskAttemptPath()` construct non-magic temp paths. `getAppAttemptId()`, `jobIdString()`, `jobName()`, and `getConfigurationOption()` provide MR metadata and job-over-filesystem config precedence.

## Control Flow
Magic committers call these helpers during setup, task path resolution, task commit, and cleanup. Configuration lookup first checks the job context, then the resolved filesystem config, then default.

## State And Persistence
Stateless. It defines path layout conventions that determine where pending commit metadata and temporary task data persist.

## Dependencies And Integration Points
Used by `MagicS3GuardCommitter`, staging conflict resolution, and committer setup code; depends on MapReduce `JobContext`, `TaskAttemptContext`, and constants from S3A commit packages.

## Risks
Any path layout change must stay compatible with `MagicCommitPaths` and `MagicCommitTrackerUtils`. Incorrect app-attempt IDs can mix attempts or leave stale manifests.

## Test Signals
Verify generated magic and temp paths for app attempt IDs, UUID validation, job/task ID string fallbacks, and configuration precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/CommitUtilsWithMR.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/package-info.java

## Purpose
Package documentation for committer implementation classes that depend on MapReduce.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit.impl` private and unstable. The Javadoc warns these classes must not be referenced by production S3A filesystem code except through job/task committer paths.

## Control Flow
No executable control flow.

## State And Persistence
No state. It documents a dependency boundary rather than persistent data.

## Dependencies And Integration Points
Applies to `CommitOperations`, `CommitContext`, `CommitUtilsWithMR`, and audit support classes that integrate S3A committers with MapReduce.

## Risks
Violating the package boundary can accidentally make core S3A code require MapReduce classes on the classpath.

## Test Signals
Classpath/minimal-dependency tests should verify core S3A filesystem code does not load this package outside committer usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/InMemoryMagicCommitTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/InMemoryMagicCommitTracker.java

## Purpose
Magic commit tracker variant that stores pending commit metadata in process memory rather than writing `.pending` metadata objects to S3.

## Important APIs, Types, And Functions
Static concurrent maps store task-attempt ID to `SinglePendingCommit` list, path to bytes written, and task-attempt ID to written paths. `aboutToComplete()` validates MPU inputs, builds a `SinglePendingCommit`, snapshots IO statistics, extracts the task attempt ID from the magic path, and stores metadata in those maps. Static getters expose the maps for task commit/abort cleanup.

## Control Flow
The output stream calls `aboutToComplete()` near close. The method records metadata and returns false, preventing immediate MPU completion. `MagicS3GuardCommitter.loadPendingCommitsFromMemory()` later removes and consumes the entries.

## State And Persistence
All state is static and process-local. Nothing is persisted to S3 until the task committer writes a `PendingSet`; data is removed when a task commits or aborts.

## Dependencies And Integration Points
Extends `MagicCommitTracker`, uses `SinglePendingCommit`, `IOStatisticsSnapshot`, and `MagicCommitTrackerUtils.extractTaskAttemptIdFromPath()`. Enabled by `fs.s3a.committer.magic.track.commits.in.memory`.

## Risks
Because metadata is in-memory, it is unsuitable across process loss or task commit in a different JVM. Static maps can leak if abort/commit cleanup is missed. Task-attempt extraction is path-shape sensitive.

## Test Signals
Test close-time metadata creation, map cleanup on commit and abort, zero/missing parts rejection, process-local failure assumptions, and concurrent writes from multiple files in one task.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/InMemoryMagicCommitTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTracker.java

## Purpose
Abstract `PutTracker` base for magic commits. It redirects stream close behavior so uploaded MPU parts are not made visible until the job committer completes them.

## Important APIs, Types, And Functions
Stores the original under-magic key, final destination key, pending metadata key, nominal path, bucket, `WriteOperationHelper`, and `PutTrackerStatistics`. `initialize()` returns true to start MPU immediately. `outputImmediatelyVisible()` returns false. `aboutToComplete()` remains abstract for S3-backed and in-memory metadata implementations.

## Control Flow
Created by S3A magic integration when a write targets a magic path. The stream uploads MPU parts to the final destination key, then the concrete tracker saves pending commit metadata and returns false so normal completion is skipped.

## State And Persistence
Holds runtime metadata required by subclasses. Persistence is delegated to `S3MagicCommitTracker` or `InMemoryMagicCommitTracker`.

## Dependencies And Integration Points
Extends `PutTracker`; uses S3A write helpers and statistics. It must not import MapReduce types, keeping filesystem write paths independent of MR.

## Risks
Subclasses must always record enough metadata for later completion; returning the wrong boolean can expose objects early or lose commit data.

## Test Signals
Verify delayed visibility, immediate MPU initialization, correct destination key selection, and subclass behavior for metadata persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTrackerUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTrackerUtils.java

## Purpose
Small utility class for magic commit tracker configuration and task-attempt ID extraction.

## Important APIs, Types, And Functions
`extractTaskAttemptIdFromPath()` splits a magic path, takes children under the magic segment, validates a minimum size, and returns the expected task attempt element. `isTrackMagicCommitsInMemoryEnabled()` and `isCleanupMagicCommitterEnabled()` read magic committer booleans from configuration.

## Control Flow
In-memory trackers call the extractor at stream close; magic committers call the config helpers during load/abort and cleanup.

## State And Persistence
Stateless. It determines whether metadata is persisted to S3 or held in memory by other classes.

## Dependencies And Integration Points
Depends on `MagicCommitPaths` and `CommitConstants`; used by `InMemoryMagicCommitTracker` and `MagicS3GuardCommitter`.

## Risks
The extractor checks `size() >= 3` but reads index 3, so very short malformed child lists can still fail with an index error. It is tightly coupled to `CommitUtilsWithMR` magic path layout.

## Test Signals
Validate path extraction for current magic task paths, malformed path rejection, and both configuration flags with explicit and default values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTrackerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitter.java

## Purpose
MapReduce committer for S3A magic paths. Tasks write directly to final S3 keys as incomplete MPUs while metadata is recorded under magic paths or in memory; job commit completes the MPUs after all tasks succeed.

## Important APIs, Types, And Functions
`NAME` is `magic`. Constructor sets the task work path and verifies magic output support. `requiresDelayedCommitOutputInFileSystem()` returns true. `setupJob()` creates the magic job path. `listPendingUploadsToCommit()` lists `.pendingset` files in the job attempt directory. `commitTask()` calls `innerCommitTask()`, deletes task attempt paths, and updates statistics. `loadPendingCommits()` selects S3-backed or in-memory metadata loading.

## Control Flow
Task commit loads all pending single commits, patches job/task IDs, aggregates IO stats, saves a single task `PendingSet` under the job attempt path, and aborts loaded pending uploads if saving fails. Job commit uses the superclass flow with `listPendingUploadsToCommit()`. Abort loads pending metadata from memory or S3 and aborts all MPUs, then deletes the attempt path.

## State And Persistence
Persistent state consists of magic directories, task `.pending` files or in-memory maps, job-attempt `.pendingset` files, and optional cleanup of magic/temp directories. Runtime state is mostly inherited from `AbstractS3ACommitter`.

## Dependencies And Integration Points
Uses `CommitOperations`, `CommitContext`, `PendingSet`, `SinglePendingCommit`, `CommitUtilsWithMR`, magic tracker utils, S3A delete/list helpers, and MapReduce contexts.

## Risks
Correctness depends on all task metadata being loadable before job commit. In-memory tracking is process-local. Cleanup is configurable and must not delete unrelated outputs. Failure while saving the task `PendingSet` must abort known MPUs to avoid leaked uploads.

## Test Signals
Exercise S3-backed and in-memory modes, task commit with multiple files, metadata load failure rollback, abortTask from same and different contexts, job pending listing, cleanup enabled/disabled, and verification that final objects appear only after job commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitterFactory.java

## Purpose
Factory for creating `MagicS3GuardCommitter` instances when the S3A committer name is `magic`.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` constructs and returns a new `MagicS3GuardCommitter`.

## Control Flow
Called by `S3ACommitterFactory` after config selection. The concrete committer constructor performs magic-path capability checks.

## State And Persistence
Stateless factory; no persistent data.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory` and integrates with MapReduce `PathOutputCommitter` creation.

## Risks
No compatibility validation happens here; failures surface during committer construction/setup if magic commit support is disabled.

## Test Signals
Verify factory class name, returned committer type, propagation of constructor failures, and selection through `S3ACommitterFactory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/S3MagicCommitTracker.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/S3MagicCommitTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/package-info.java

## Purpose
Package documentation and annotations for magic committer support.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit.magic` private and unstable. The package Javadoc identifies it as the magic committer and support package.

## Control Flow
No executable control flow.

## State And Persistence
No direct state; documents the package containing magic pending metadata and delayed MPU completion logic.

## Dependencies And Integration Points
Applies to `MagicS3GuardCommitter`, magic tracker implementations, and magic tracker utilities.

## Risks
The unstable/private annotation gives implementation freedom, but external jobs may depend on behavior through configuration and persisted metadata.

## Test Signals
Package-level API/stability checks and committer integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/package-info.java

## Purpose
Package documentation for S3A analytics-job commit support.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit` private and unstable. The Javadoc summarizes the package as support for committing analytics job output directly to S3.

## Control Flow
No executable control flow.

## State And Persistence
No state. It scopes core committer APIs, factories, exceptions, path utilities, and base tracker behavior.

## Dependencies And Integration Points
Applies to public-facing committer selection and shared commit utilities used by magic and staging subpackages.

## Risks
Private/unstable status means direct external code should avoid linking to internals, but configuration names and persisted behavior remain operational contracts.

## Test Signals
Package annotation checks and integration tests through configured committers rather than direct package API use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/ConflictResolution.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/ConflictResolution.java

## Purpose
Enum defining destination conflict policies for staging committers.

## Important APIs, Types, And Functions
Values are `FAIL`, `APPEND`, and `REPLACE`. `FAIL` rejects existing data, `APPEND` allows merging new files, and `REPLACE` deletes existing destination data at the appropriate job/partition scope.

## Control Flow
`StagingCommitter.getConflictResolutionMode()` parses config into this enum. Directory and partitioned committers switch on it during setup, task commit, and job pre-commit.

## State And Persistence
No persistent state; selected mode is cached by `StagingCommitter`.

## Dependencies And Integration Points
Used by `DirectoryStagingCommitter` and `PartitionedStagingCommitter` to decide fail/append/replace behavior.

## Risks
Unknown configuration strings fail via `valueOf()`. Semantics differ by committer: directory replace deletes whole output path, partitioned replace deletes touched partitions only.

## Test Signals
Validate config parsing, unknown value failure, and behavior for all three modes in directory and partitioned committers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/ConflictResolution.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitter.java

## Purpose
Staging committer variant that applies conflict resolution at the whole output directory level.

## Important APIs, Types, And Functions
`NAME` is `directory`. `setupJob()` checks the destination path and conflict policy before delegating to base setup. `preCommitJob()` delegates pending-file validation to the base class, then deletes the output directory only for `REPLACE`.

## Control Flow
During setup, an existing non-directory path always fails. Existing directories fail in `FAIL` mode and are permitted in `APPEND` or `REPLACE`. During pre-commit, `REPLACE` recursively deletes the output path after all task output has succeeded and before final MPU completion.

## State And Persistence
Uses inherited staging state: local task work directories, cluster pending sets, and pending MPUs. It adds no new persistent fields.

## Dependencies And Integration Points
Extends `StagingCommitter`; uses destination `FileSystem`, `ConflictResolution`, and inherited `ActiveCommit` job pre-commit flow.

## Risks
Whole-directory replacement is broad; deleting output during pre-commit must happen only after task success. `FAIL` only checks at setup, so concurrent external writes after setup are not rechecked here.

## Test Signals
Existing absent/file/directory destinations, all conflict policies, replace deletion timing, append preservation, and final job commit after replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitterFactory.java

## Purpose
Factory for the directory staging committer.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` returns a new `DirectoryStagingCommitter`.

## Control Flow
Selected by `S3ACommitterFactory` when `fs.s3a.committer.name` is `directory`.

## State And Persistence
Stateless factory.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory` and integrates MapReduce output committer creation with `DirectoryStagingCommitter`.

## Risks
No extra validation here; all conflict and path validation is deferred to the concrete committer.

## Test Signals
Factory class name, returned type, constructor failure propagation, and selection from top-level committer factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitter.java

## Purpose
Staging committer variant that applies conflict resolution at partition-directory granularity. It is designed for partitioned table writes where only touched partitions should be checked or replaced.

## Important APIs, Types, And Functions
`NAME` is `partitioned`. `commitTaskInternal()` computes touched partitions from task output and fails early in `FAIL` mode if corresponding destination partitions already exist. `preCommitJob()` handles job-side policy; `replacePartitions()` reloads all pending sets to identify destination parents and delete them in parallel.

## Control Flow
Task commit identifies partitions relative to the local attempt path before staging uploads. In `FAIL` mode it probes each destination partition before delegating to base upload/pending-set creation. In job pre-commit, `REPLACE` scans pending manifests, builds a concurrent set of partition paths, deletes those partitions, and skips the normal pending-file precheck because manifests were already loaded.

## State And Persistence
No new persistent fields. It consumes `PendingSet` and `SinglePendingCommit.destinationPath()` to discover partition parents.

## Dependencies And Integration Points
Extends `StagingCommitter`; uses `Paths.getPartitions()`, `PersistentCommitData.load()`, `TaskPool`, and destination/source filesystems.

## Risks
Partition replacement requires rereading all pending files and can be expensive. Root-table files map to a special partition token. Destination existence checks during task commit can race with other writers.

## Test Signals
Task outputs in root and nested partitions, FAIL/APPEND/REPLACE modes, partition deletion set correctness, parallel load/delete failures, and preservation of untouched partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitterFactory.java

## Purpose
Factory for the partitioned staging committer.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` constructs `PartitionedStagingCommitter`.

## Control Flow
Selected by `S3ACommitterFactory` when the configured committer name is `partitioned`.

## State And Persistence
Stateless factory.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory`; connects MapReduce task committer creation to partition-aware staging logic.

## Risks
No factory-level validation of partition configuration or destination path; errors occur in committer setup/commit.

## Test Signals
Factory class name, returned committer type, propagation of constructor failures, and top-level selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/Paths.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/Paths.java

## Purpose
Path utility class for staging committers. It handles unique filename generation, local task temp directories, cluster staging upload directories, relative paths, and partition detection.

## Important APIs, Types, And Functions
`addUUID()` inserts job UUIDs before filename extensions unless already present. `getRelativePath()`, `getParent()`, and `path()` build path strings. `getLocalTaskAttemptTempDir()` allocates and caches local work dirs. `tempDirForStaging()`, `getMultipartUploadCommitsDirectory()`, and `getStagingUploadsParentDirectory()` build cluster manifest directories. `getPartitions()` derives touched partition names from task output.

## Control Flow
Staging committers create local attempt paths under allocated buffer dirs, write pending manifests under `$temp/$user/$uuid/staging-uploads`, and compute final S3 keys from relative local paths. Partitioned committers use `getPartitions()` before upload conflict checks.

## State And Persistence
Maintains a static Guava cache of temp folders keyed by UUID plus task attempt ID. Persistent paths are staging-upload directories in the cluster filesystem and local work directories.

## Dependencies And Integration Points
Depends on Hadoop `LocalDirAllocator`, local filesystem, `UserGroupInformation`, MapReduce attempt IDs, and staging constants.

## Risks
`clearTempFolderInfo()` invalidates by attempt ID while cache keys include UUID plus attempt ID, so tests should verify cleanup expectations. Relative path derivation assumes outputs are under the attempt path. UUID insertion can interact with filenames containing the UUID in parent directories.

## Test Signals
UUID insertion before extensions, local temp allocation/cache reset, cluster staging path construction, partition extraction including root outputs, directory-output rejection, and relative path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/Paths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitter.java

## Purpose
Base implementation for S3A staging committers. Tasks write to local filesystem work directories, task commit uploads files as incomplete MPUs and writes pending manifests to a cluster filesystem, and job commit completes the MPUs.

## Important APIs, Types, And Functions
Constructor configures multipart size, unique filenames, local work path, wrapped `FileOutputCommitter`, commit manifest directory, S3 key prefix, and conflict mode. Key methods include `setupJob()`, `setupTask()`, `needsTaskCommit()`, `commitTask()`, `commitTaskInternal()`, `abortTask()`, `listPendingUploadsToCommit()`, `listPendingUploadsToAbort()`, `cleanup()`, and `preCommitJob()`.

## Control Flow
Task setup creates local and wrapped-committer attempt paths. `needsTaskCommit()` lists local output. `commitTaskInternal()` lists output files, computes relative paths and final S3 keys, uploads each local file through `CommitOperations.uploadFileToPendingCommit()`, builds a `PendingSet`, optionally aggregates IO statistics, saves the manifest to the wrapped committer task path, aborts successfully staged MPUs on failure, commits the wrapped task, and deletes local output. Job abort lists pending manifests and aborts MPUs.

## State And Persistence
Runtime state includes output path, local work path, upload part size, unique filename flag, conflict mode, S3 key prefix, and wrapped committer. Persistent state includes local task files, cluster `.pendingset` manifests, and S3 incomplete MPUs.

## Dependencies And Integration Points
Extends `AbstractS3ACommitter`; wraps `FileOutputCommitter` algorithm 1; uses `CommitOperations`, `CommitContext`, `PendingSet`, `Paths`, S3A filesystem helpers, and MapReduce contexts.

## Risks
Local files are host-local; abort from a different host may not clean them. Failure after MPU upload but before manifest save must abort staged commits. Unique filename mode affects final key stability. Cleanup deletes destination `__temporary`, which is risky when multiple jobs share output paths.

## Test Signals
Task commit with zero, one, and many files; failed upload and manifest save cleanup; unique filename on/off; local work cleanup; job abort cleanup; wrapped committer behavior; IO stats aggregation; and conflict-mode delegation to subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterConstants.java

## Purpose
Constants used by staging committers for temporary directories and partition naming.

## Important APIs, Types, And Functions
`FILESYSTEM_TEMP_PATH` defaults cluster staging to `tmp/staging`. `TABLE_ROOT` names root-table output as a synthetic partition. `STAGING_UPLOADS` names the directory holding pending upload manifests.

## Control Flow
`Paths` uses these constants while building staging upload directories and partition sets.

## State And Persistence
No runtime state. The constants shape persistent staging paths and pending-manifest locations.

## Dependencies And Integration Points
Used by `Paths`, `StagingCommitter`, and partitioned conflict resolution.

## Risks
Changing names breaks cleanup and discovery of existing staging manifests. `TABLE_ROOT` must not collide with real partition handling assumptions.

## Test Signals
Path construction and partition extraction tests should assert these constant values where behavior depends on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterFactory.java

## Purpose
Factory for the base staging committer, primarily for internal tests rather than production use.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` returns `StagingCommitter`.

## Control Flow
Selected only through the internal committer name handled by `S3ACommitterFactory`.

## State And Persistence
Stateless.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory`; creates the non-partitioned, non-directory-conflict-specialized staging committer.

## Risks
Base staging committer has no production conflict-resolution specialization, so accidental production use can miss desired directory/partition semantics.

## Test Signals
Factory selection through internal name, returned type, and constructor failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/package-info.java

## Purpose
Package documentation and annotations for staging committers.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit.staging` private and unstable. Javadoc identifies the package as containing staging committers.

## Control Flow
No executable control flow.

## State And Persistence
No direct state; package contents manage local task staging, cluster pending manifests, and delayed MPU completion.

## Dependencies And Integration Points
Applies to base, directory, partitioned staging committers and their factories/utilities.

## Risks
Private/unstable status does not remove the need for compatibility in configured committer behavior and pending manifest interoperability.

## Test Signals
Package annotation checks plus staging committer integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSCannedACL.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSCannedACL.java

## Purpose
SDK migration enum mapping legacy AWS canned ACL names used by Hadoop configuration/code to the string values expected by AWS SDK v2/S3.

## Important APIs, Types, And Functions
Enum values include `Private`, `PublicRead`, `PublicReadWrite`, `AuthenticatedRead`, `AwsExecRead`, `BucketOwnerRead`, `BucketOwnerFullControl`, and `LogDeliveryWrite`. `toString()` returns the wire/config value such as `private` or `bucket-owner-full-control`.

## Control Flow
No complex control flow; callers select an enum and serialize it through `toString()`.

## State And Persistence
Each enum stores a fixed string value. No mutable or persistent state.

## Dependencies And Integration Points
Used by S3A request construction where canned ACL configuration must be translated to AWS headers or SDK values.

## Risks
AWS canned ACL string values are compatibility-sensitive. Missing new ACLs or typo changes would break object ACL configuration.

## Test Signals
Assert all enum `toString()` values match AWS S3 canned ACL names and verify configuration parsing/request construction uses the expected string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSCannedACL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSClientConfig.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSClientConfig.java

## Purpose
Central builder utilities for AWS SDK v2 client configuration in S3A. It configures request timeouts, user agent, custom headers, signer overrides, retry policy, sync/async HTTP clients, proxy settings, and per-request timeout overrides.

## Important APIs, Types, And Functions
`createClientConfigBuilder()` initializes `ClientOverrideConfiguration`. `createHttpClientBuilder()` configures Apache HTTP; `createAsyncHttpClientBuilder()` configures Netty async HTTP. `createRetryPolicyBuilder()` uses adaptive retry mode. `createProxyConfiguration()` and `createAsyncProxyConfiguration()` build sync/async proxy config with credential validation. `createApiConnectionSettings()` and `createConnectionSettings()` derive validated timeout settings. `setRequestTimeout()` patches individual AWS requests.

## Control Flow
Client config creation applies request timeout, user agent, custom service headers, generic signer override, then service-specific signer override. HTTP client creation reads common connection settings and maps them onto Apache or Netty builders. Proxy creation handles host/port/default-port combinations and rejects username/password mismatches or port-without-host.

## State And Persistence
Only mutable static state is `minimumOperationDuration`, test-adjustable and resettable. All builders are runtime configuration objects; no persistent state.

## Dependencies And Integration Points
Used by S3A client factories and AWS service clients. Depends on Hadoop `Configuration`, S3A constants, `S3AUtils`, `SignerFactory`, `NetworkBinding`, AWS SDK v2 client/http/retry APIs, and Hadoop `VersionInfo`.

## Risks
Timeout minimums can affect production latency if test overrides leak. Proxy logging at debug includes password values. Service-specific signer overrides supersede generic signer settings. Async proxy lacks NTLM support noted by TODO.

## Test Signals
Cover timeout minimum enforcement/reset, sync and async builder mappings, retry count bounds, proxy host/port/default behavior, credential mismatch failures, custom header parsing, generic and service-specific signer precedence, user-agent prefix, and per-request timeout override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSHeaders.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSHeaders.java

## Purpose
Central constant interface for HTTP and S3-specific header names used by S3A.

## Important APIs, Types, And Functions
Defines standard headers such as `Content-Length`, `Content-Type`, `ETag`, `If-Match`, and `Range`; S3 headers such as version ID, storage class, archive status, server-side encryption, requester pays, replication status, object lock fields; and client-side encryption metadata headers such as material description, wrapping algorithm, CEK algorithm, and unencrypted content length.

## Control Flow
No executable control flow; consumers reference string constants when building requests or processing responses.

## State And Persistence
No state. Header strings shape persisted object metadata and request/response interpretation.

## Dependencies And Integration Points
Used by S3A request factories, encryption support, header processing, object status extraction, and conditional/ranged operations.

## Risks
Header spelling and casing are compatibility-sensitive. Deprecated encryption headers remain for legacy envelope encryption behavior and should not be removed without migration coverage.

## Test Signals
Request/response tests should assert expected headers for range reads, versioned objects, encryption, requester-pays, storage class, restore/archive status, object lock, and client-side encryption metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSHeaders.java -->
