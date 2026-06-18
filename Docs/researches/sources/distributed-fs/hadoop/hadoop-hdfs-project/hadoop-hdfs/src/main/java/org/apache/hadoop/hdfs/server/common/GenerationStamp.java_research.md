<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java

## Purpose

`GenerationStamp` is the sequential-number primitive for HDFS block generation stamps.

## Important APIs and types

It extends `SequentialNumber`, defines `LAST_RESERVED_STAMP = 1000L`, and initializes new instances to that reserved value.

## Control flow

The class delegates all increment/skip behavior to `SequentialNumber`. Allocation code uses it as the cursor for new generation stamps.

## State and persistence behavior

The current value is mutable state inherited from `SequentialNumber` and is persisted indirectly as part of namespace/storage metadata managed elsewhere.

## Dependencies and integration points

It integrates with block allocation, block recovery, generation-stamp validation, and `HdfsServerConstants.RESERVED_LEGACY_GENERATION_STAMPS`.

## Risks and edge cases

Correctness depends on external synchronization and persistence of the cursor. Starting at the reserved value prevents allocation of low reserved stamps but callers must use the next-value semantics correctly.

## Test signals

Tests should verify initial value, sequential advancement, skip behavior, persistence restore through BlockIdManager/storage, and recovery generation-stamp ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java -->
