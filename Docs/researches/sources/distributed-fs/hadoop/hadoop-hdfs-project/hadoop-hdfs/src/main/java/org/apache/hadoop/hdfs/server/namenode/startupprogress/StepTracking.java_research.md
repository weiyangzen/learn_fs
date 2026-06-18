<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java

## Purpose

`StepTracking` is the mutable internal record for one startup step. It stores begin/end time, an atomic progress count, and an optional total.

## Important APIs and types

- Extends `AbstractTracking`.
- `AtomicLong count` supports concurrent increments.
- `total` uses `Long.MIN_VALUE` as undefined.
- `clone()` deep-copies the atomic count value and timing/total fields.

## Control flow

`StartupProgress` initializes `StepTracking` lazily, increments `count` through returned counters, and updates timing/total fields through step APIs. `StartupProgressView` reads cloned copies.

## State and persistence behavior

State is in-memory only. Count updates are atomic; total and timestamps are plain fields intended for low-contention instrumentation.

## Dependencies and integration points

Used inside `PhaseTracking.steps` and interpreted by `StartupProgressView` for counts, totals, elapsed time, and percent complete.

## Risks and edge cases

Undefined totals turn into zero for view APIs, making percent complete zero unless a positive total is set or the phase completes. Plain begin/end/total fields can be overwritten by last writer.

## Test signals

Startup progress tests should verify atomic counter behavior, clone isolation, total handling, and phase-complete percent override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StepTracking.java -->
