<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java

## Purpose

`RollingWindow` tracks event counts over a fixed time interval using a ring of buckets. It supports concurrent increments and approximate rolling sums with bounded memory.

## Important APIs and types

- Constructor accepts `windowLenMs` and bucket count.
- `incAt(long time, long delta)` records an event count at a timestamp.
- `getSum(long time)` returns the sum of non-stale buckets.
- Nested `Bucket` holds atomic value and update time with synchronized stale reset.

## Control flow

`incAt` maps event time to a bucket by modulo window length. If the bucket's update time is outside the current rolling window, `safeReset` clears it and updates its timestamp; then the delta is atomically added. `getSum` iterates buckets and includes only non-stale values for the requested time.

## State and persistence behavior

All state is in-memory. Bucket values and update times are atomic; reset is synchronized per bucket to avoid losing concurrent updates during rollover. Counts expire by staleness rather than background cleanup.

## Dependencies and integration points

Used by `RollingWindowManager` per operation/user. Depends on SLF4J for debug logging and Java atomics.

## Risks and edge cases

The constructor contains a redundant-looking `this.bucketSize % bucketSize` check that always evaluates to zero; real validation is in `RollingWindowManager`. Out-of-order event times are tolerated only within the documented buffering-delay assumption. Bucket granularity trades memory for accuracy, and stale detection uses event/current times supplied by callers.

## Test signals

`TestRollingWindow` should cover bucket rollover, concurrent increments, out-of-order events within the window, stale bucket exclusion, and boundary times at exact window length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/window/RollingWindow.java -->
