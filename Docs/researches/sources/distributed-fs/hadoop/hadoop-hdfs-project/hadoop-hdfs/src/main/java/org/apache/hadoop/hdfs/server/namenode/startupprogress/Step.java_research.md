<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java

## Purpose

`Step` identifies a granular startup task within a phase, optionally by step type, file name, and file size. It is used as the key for per-step tracking.

## Important APIs and types

- Constructors support type-only, file-only, file+size, type+file, and type+file+size forms.
- Fields are immutable: `file`, `size`, `type`, and a generated `sequenceNumber`.
- Implements `Comparable<Step>` for sorted display by file and then sequence number.
- `equals`/`hashCode` use file, size, and type, not sequence number.

## Control flow

Each new instance receives a monotonically increasing process-local sequence number. Concurrent maps use equality/hash for key identity, while `StartupProgressView.getSteps` sorts retained keys with `compareTo` for display ordering.

## State and persistence behavior

State is immutable after construction. `SEQUENCE` is static in-memory state and is not persisted; it only stabilizes ordering among runtime-created step objects.

## Dependencies and integration points

Used by `StartupProgress` callers to identify work such as loading a file or processing inode/delegation-token sections. Depends on Commons Lang builders and `StepType`.

## Risks and edge cases

`compareTo` and `equals` are inconsistent because sequence number participates only in ordering. This is tolerable for display sorting but can be surprising in sorted collections. Null files are allowed and comparison behavior depends on Commons Lang handling.

## Test signals

Tests should cover equality, hash behavior, ordering, constructor metadata, and use as a key in startup progress counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Step.java -->
