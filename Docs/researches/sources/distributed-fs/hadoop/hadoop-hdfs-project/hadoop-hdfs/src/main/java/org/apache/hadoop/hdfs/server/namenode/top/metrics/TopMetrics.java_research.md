<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java

## Purpose

`TopMetrics` is the metrics-facing interface for NNTop. It accepts audit events, records per-command/per-user counts into rolling windows, exposes JSON-friendly top windows, and publishes flattened counters through Metrics2.

## Important APIs and types

- `rollingWindowManagers` maps reporting periods to `RollingWindowManager`.
- `report(...)` variants normalize audit events down to user and command.
- `getTopWindows()` returns `RollingWindowManager.TopWindow` snapshots for all configured windows.
- Implements `MetricsSource.getMetrics`.
- Metric names are built from operation type, total count, user, and count.

## Control flow

The constructor logs relevant NNTop configuration and creates one `RollingWindowManager` per reporting period. Each report trims the authentication method from the username and records a delta of one in every window manager. Metrics polling skips output when disabled; otherwise it snapshots windows and emits total operation counts plus top-user counts.

## State and persistence behavior

State is in-memory rolling-window data held by `RollingWindowManager`s. Nothing is persisted; old entries age out as windows expire and snapshots garbage-collect zero-sum user windows.

## Dependencies and integration points

Feeds from `TopAuditLogger` and exports to Metrics2 and FSNamesystem MBean JSON (`getTopWindows`). It depends on `UserGroupInformation.trimLoginMethod`, `Time.monotonicNow`, and the rolling-window package.

## Risks and edge cases

User and operation names are embedded in metric names; whitespace is removed from op names but user names are not similarly sanitized. Metrics source disablement affects Metrics2 output but `getTopWindows` can still return snapshots. High cardinality users/operations can grow memory until windows age out.

## Test signals

`TestTopMetrics`, `TestNameNodeMXBean.testTopUsers*`, and rolling-window tests cover top aggregation, disabled metrics source behavior, configured periods, and user ranking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/metrics/TopMetrics.java -->
