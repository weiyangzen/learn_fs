<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java

## Purpose

`IncorrectVersionException` reports incompatible software, protocol, or storage layout versions.

## Important APIs and types

It extends `IOException` and provides constructors for arbitrary messages, daemon version compatibility, and layout-version mismatch. The daemon constructor formats minimum/reported remote daemon versions; layout constructors format reported and expected numeric versions.

## Control flow

Storage and protocol code throw it when an external version is too old, too new, or otherwise unexpected for the current application.

## State and persistence behavior

The exception is message-only. It is not persisted, but it frequently guards persisted layout metadata parsing.

## Dependencies and integration points

It integrates with `StorageInfo.setLayoutVersion`, startup compatibility checks, inter-daemon compatibility checks, and layout-version upgrade/downgrade validation.

## Risks and edge cases

The numeric layout constructor names are easy to confuse because one overload takes current then reported and delegates to reported/expected ordering. Tests should assert final messages rather than assuming parameter names.

## Test signals

Tests should cover future layout detection, old daemon version messages, null `ofWhat` formatting, and caller mapping to startup failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java -->
