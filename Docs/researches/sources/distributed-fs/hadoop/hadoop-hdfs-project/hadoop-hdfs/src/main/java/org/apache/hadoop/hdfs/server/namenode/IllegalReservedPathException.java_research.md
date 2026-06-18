<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java

## Purpose

`IllegalReservedPathException` signals that an FSImage contains a reserved path name when upgrading from software that did not reserve those names to software that does.

## Important APIs and Types

The class is a private `IOException` subclass with constructors for message-only and message-with-cause forms.

## Control Flow, State, and Persistence

It carries no state beyond the exception message and optional cause. Its significance is in upgrade/load control flow: throwing it blocks unsafe namespace loading when reserved path invariants would be violated.

## Dependencies and Integration Points

It integrates with FSImage upgrade and reserved path validation code. Callers can handle it as an `IOException` while preserving a more specific reason for diagnostics.

## Risks and Test Signals

Risks are mostly diagnostic. Tests should cover image load or upgrade paths with illegal reserved names and ensure the specific exception and message make the offending condition clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java -->
