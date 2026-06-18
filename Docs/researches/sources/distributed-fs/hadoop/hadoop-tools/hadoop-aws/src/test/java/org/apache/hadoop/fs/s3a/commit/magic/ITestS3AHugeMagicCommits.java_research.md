# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestS3AHugeMagicCommits.java

## Purpose
Scale test for writing a huge file through the magic committer and then explicitly committing the generated pending multipart upload. It validates magic pending metadata for multi-part files larger than one part.

## Important APIs, Types, and Functions
The class extends `AbstractSTestS3AHugeFiles`, is tagged `@ScaleTest`, and uses disk fast-upload buffering. It overrides `getPathOfFileToCreate()` to return the magic output file, requires multipart uploads, and overrides read/rename tests to skip them. Core test methods are `test_000_CleanupPendingUploads()`, `test_030_postCreationAssertions()`, and `test_800_DeleteHugeFiles()`.

## Control Flow and Behavior
`setup()` verifies magic commit support and constructs `finalDirectory`, `magicDir`, `jobDir`, `magicOutputFile`, `pendingDataFile`, and the final hugefile destination. Cleanup aborts pre-existing MPUs under the final directory. After file creation, `test_030_postCreationAssertions()` verifies the final file is absent, the pending file exists, the marker file is zero bytes with `XA_MAGIC_MARKER` encoding the real length, lists pending uploads, loads pending commits from the job directory, commits each through `CommitContext.commitOrFail()`, verifies no pending uploads remain, and then delegates normal huge-file assertions to the superclass.

## State, Persistence, and Dependencies
Persistent state includes large S3 multipart uploads, magic marker xattrs, `.pending` metadata, and final committed object data. It depends on S3A huge-file scale configuration, `CommitOperations`, `PendingSet`, `SinglePendingCommit`, `listMultipartUploads()`, audit spans, and S3A header extraction.

## Integration Points, Risks, and Test Signals
This test is expensive but high value for multi-part magic commits. It catches bugs in marker length encoding, pending set loading, commit threading, and MPU cleanup. Risks include stale uploads after interrupted scale runs, long execution time, and provider-specific listing/abort behavior.
