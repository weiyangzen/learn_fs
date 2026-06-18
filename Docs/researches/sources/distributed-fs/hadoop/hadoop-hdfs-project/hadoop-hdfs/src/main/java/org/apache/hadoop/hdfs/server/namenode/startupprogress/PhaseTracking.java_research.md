<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java

## Purpose

`PhaseTracking` is the mutable internal record for one startup phase. It stores phase-level file/size metadata and a concurrent map of runtime-created steps.

## Important APIs and types

- Extends `AbstractTracking`.
- Fields: `file`, `size`, and `ConcurrentMap<Step, StepTracking> steps`.
- `clone()` deep-copies phase timing, metadata, and each step's `StepTracking`.
- `toString()` uses `ToStringBuilder` for diagnostics.

## Control flow

`StartupProgress` mutates this record when phases begin/end or when phase file/size metadata is set. `StartupProgressView` clones it to create an immutable snapshot for readers.

## State and persistence behavior

All state is in-memory. The step map is concurrent to allow multiple startup threads to record progress without central locking. Cloning isolates readers from later mutations.

## Dependencies and integration points

Depends on `Step`, `StepTracking`, `ConcurrentHashMap`, and Commons Lang string building. It is package-private and only used inside the startup-progress package.

## Risks and edge cases

The `file` and `size` fields are not atomic as a pair, so live mutable reads could be inconsistent; callers should use `StartupProgressView`. Step key equality ignores sequence number, while ordering uses sequence number, so duplicate logical steps are collapsed in the map but sorted by the retained key.

## Test signals

Tests should exercise snapshot immutability, concurrent step creation, phase metadata propagation, and deterministic step iteration from a cloned view.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/PhaseTracking.java -->
