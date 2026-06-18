<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java

## Purpose

`RollingWindowManager` manages all rolling windows for one NNTop reporting period. It records counts by command and user, snapshots ranked top users per operation, and synthesizes an all-commands aggregate.

## Important APIs and types

- `recordMetric(time, command, user, delta)` updates one command/user window.
- `snapshot(time)` returns a `TopWindow`.
- Public snapshot DTOs: `TopWindow`, `Op`, and `User`.
- Internal `RollingWindowMap` maps user names to `RollingWindow`; `metricMap` maps command names to those maps.
- Internal `UserCounts` aggregates duplicate user counts and totals.

## Control flow

Construction validates bucket count, divisibility, and top-user count. Recording creates command and user windows with `putIfAbsent` and increments the chosen window. Snapshot iterates all commands, calculates top user counts for each command, removes zero-sum user windows as garbage collection, adds non-empty operations, then builds an `ALL_CMDS` op by retaining totals for users that appeared in per-op top lists.

## State and persistence behavior

State is in-memory and concurrent through `ConcurrentHashMap` plus thread-safe `RollingWindow`. Expired user windows are removed during snapshot. There is no durable state.

## Dependencies and integration points

Used by `TopMetrics`. Depends on `TopConf.ALL_CMDS`, `DFSConfigKeys`, and `RollingWindow`.

## Risks and edge cases

`Op.compareTo` and `equals` compare only total counts, while `hashCode` uses operation type; this is inconsistent for general sets/maps but current usage is list sorting. `User.compareTo` ranks by count only, so equal counts have unspecified ordering. The all-commands aggregate includes only users that were top users for some operation, not all users in the window.

## Test signals

`TestRollingWindowManager` should verify ranking, top-user limits, all-command synthesis, zero-window garbage collection, invalid configuration, and concurrent recording. NameNode MXBean top-user tests are end-to-end signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindowManager.java -->
