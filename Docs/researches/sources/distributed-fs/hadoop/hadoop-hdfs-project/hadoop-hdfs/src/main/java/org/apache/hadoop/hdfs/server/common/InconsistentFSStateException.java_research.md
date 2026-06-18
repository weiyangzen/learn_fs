<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java

## Purpose

`InconsistentFSStateException` is thrown when an HDFS storage directory is in an unrecoverable or incompatible filesystem state.

## Important APIs and types

The constructors accept a `File` directory and description, with an overload that appends a stringified cause. Messages include the canonical path when available and fall back to `File.getPath`.

## Control flow

Storage analysis and property-reading code throw this exception for missing `VERSION` fields, incompatible namespace/cluster IDs, invalid directory transition combinations, and non-empty current directories during format checks.

## State and persistence behavior

The exception has no mutable state beyond its message. It describes persistent local storage state but does not modify it.

## Dependencies and integration points

It integrates with `Storage`, `StorageInfo`, NameNode/DataNode startup, upgrade/rollback/checkpoint recovery, and format confirmation paths.

## Risks and edge cases

Cause details are flattened into the message rather than passed as a throwable cause. Canonical path resolution failure is silently ignored.

## Test signals

Tests should assert message content for missing files/properties, incompatible namespace/cluster IDs, bad temp directory combinations, and canonical-path fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java -->
