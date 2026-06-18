<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java

## Purpose

`StorageErrorReporter` is a callback interface for journal/storage components to report errors on underlying files without creating circular dependencies.

## Important APIs and types

It declares one method, `reportErrorOnFile(File f)`.

## Control flow

Implementations receive error reports from components such as `JournalManager` and decide how to mark the storage directory failed, degrade service, or surface diagnostics.

## State and persistence behavior

The interface owns no state. Implementations may mutate storage health state in memory and may indirectly affect persisted storage availability.

## Dependencies and integration points

It depends on `File` and is documented for use by NameNode journal managers and storage owners.

## Risks and edge cases

The interface does not define severity, exception cause, or retryability. Callers must choose the correct file path to let implementations map it to a storage directory.

## Test signals

Tests should cover journal-manager error callbacks, storage-directory failure mapping, repeated reports, and behavior for files outside known storage roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java -->
