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
