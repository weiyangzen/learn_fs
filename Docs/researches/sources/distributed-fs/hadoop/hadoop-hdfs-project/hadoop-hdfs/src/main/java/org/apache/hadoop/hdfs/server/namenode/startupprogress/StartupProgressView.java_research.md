<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java

## Purpose

`StartupProgressView` is an immutable read snapshot of NameNode startup progress. It provides aggregate and per-phase/step status, counts, totals, elapsed times, percent complete, and metadata without being affected by later updates.

## Important APIs and types

- Query APIs include `getCount`, `getTotal`, `getElapsedTime`, `getPercentComplete`, `getStatus`, `getFile`, `getSize`, `getPhases`, and `getSteps`.
- Constructor clones all `PhaseTracking` records from `StartupProgress`.
- `getElapsedTime(AbstractTracking...)` and `getBoundedPercent` implement common calculations.

## Control flow

The constructor deep-clones phase and step tracking data. Aggregate count/total methods iterate steps. Overall elapsed time spans `LOADING_FSIMAGE` begin to `SAFEMODE` end/current time. Overall percent complete returns `1.0` once safemode is complete; otherwise it averages all phase percentages equally.

## State and persistence behavior

The view owns a private `HashMap<Phase, PhaseTracking>` clone. It is read-only by convention and has no persistent state. Time-dependent elapsed values for running phases still use `Time.monotonicNow`, so elapsed time can increase even though underlying begin/end data is frozen.

## Dependencies and integration points

Used by startup progress servlets/UI and `StartupProgressMetrics`. It depends on `Phase`, `Step`, `StepTracking`, `Status`, and `Time`.

## Risks and edge cases

- Equal-weight aggregate percent is approximate and can misrepresent startup phases with very different durations.
- Running elapsed time is not fully immutable because it is calculated against current monotonic time.
- `getSteps` sorts by `Step.compareTo`; sequence-number ordering depends on the specific step object retained in the map.
- Undefined totals/sizes are normalized differently: totals become zero, sizes can remain `Long.MIN_VALUE`.

## Test signals

Startup progress tests should check snapshot isolation, bounded percent values, complete safemode behavior, pending/running/complete elapsed calculations, and step ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressView.java -->
