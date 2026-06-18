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
