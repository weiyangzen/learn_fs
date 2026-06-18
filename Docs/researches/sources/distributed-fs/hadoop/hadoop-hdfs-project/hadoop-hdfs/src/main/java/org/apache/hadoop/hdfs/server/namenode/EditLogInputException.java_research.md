# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogInputException.java

## Purpose
`EditLogInputException` is an `IOException` subtype that reports edit-log read failure while preserving how many edits were successfully loaded before the failure.

## Important APIs and Types
The constructor accepts message, cause, and `numEditsLoaded`. `getNumEditsLoaded` exposes that count.

## Control Flow
There is no additional control flow beyond normal exception construction and retrieval.

## State and Persistence
The exception carries transient failure context only. It is not persisted.

## Dependencies and Integration
Used by edit-log loading code to propagate partial-progress information up to callers that may decide recovery or failover behavior.

## Risks and Test Signals
Callers must inspect `getNumEditsLoaded`; otherwise partial replay context is lost. Tests should verify wrapping cause preservation, count propagation, and caller behavior when some edits were applied before failure.
