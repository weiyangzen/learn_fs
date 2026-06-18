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
