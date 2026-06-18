<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java

## Purpose

`TopConf` centralizes NNTop configuration: enabled flag, reporting windows, and the special all-commands marker.

## Important APIs and types

- Public final `isEnabled`.
- Public static `ALL_CMDS = "*"`.
- Public final `int[] nntopReportingPeriodsMs`.
- Constructor reads `NNTOP_ENABLED_KEY` and `NNTOP_WINDOWS_MINUTES_KEY`.

## Control flow

The constructor parses trimmed minute strings, converts them to milliseconds with checked integer casts, and validates that each window is at least one minute.

## State and persistence behavior

Configuration is immutable after construction. It does not persist settings; it snapshots values from `Configuration`.

## Dependencies and integration points

Used by `TopAuditLogger`, `TopMetrics`, and `RollingWindowManager`. It depends on `DFSConfigKeys`, Guava `Ints.checkedCast`, and precondition checks.

## Risks and edge cases

Invalid numeric values, overflow beyond `int`, empty window lists, or sub-minute windows fail construction. Because windows are stored as `int` milliseconds, very large minute values are not accepted.

## Test signals

NameNode MXBean tests cover top-user windows, disabled state, and no-period behavior. Unit tests should also check parsing failures and one-minute minimum enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopConf.java -->
