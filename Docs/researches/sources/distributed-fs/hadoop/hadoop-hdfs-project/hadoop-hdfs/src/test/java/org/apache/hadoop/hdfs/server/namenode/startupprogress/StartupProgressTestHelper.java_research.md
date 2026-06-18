# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressTestHelper.java

## Purpose
`StartupProgressTestHelper` provides shared helper methods for startup progress tests. It creates repeatable running and final progress states and supplies a counter increment helper.

## Important APIs, Types, and Functions
The helper uses `StartupProgress`, `StartupProgress.Counter`, `Phase`, `Step`, and `StepType` constants. Public methods are `incrementCounter`, `setStartupProgressForRunningState`, and `setStartupProgressForFinalState`.

## Control Flow
`incrementCounter` obtains the counter for a phase/step and calls `increment` `delta` times. `setStartupProgressForRunningState` completes `LOADING_FSIMAGE` with an `INODES` step at 100/100, then starts `LOADING_EDITS` for a file step with total 200 and count 100, leaving that phase running. `setStartupProgressForFinalState` completes all four startup phases: loading fsimage, loading edits, saving checkpoint, and safemode, each with a deterministic count/total.

## State and Persistence Behavior
The helper mutates only in-memory `StartupProgress` state. There is no external persistence.

## Dependencies and Integration Points
It is used by `TestStartupProgress` and `TestStartupProgressMetrics` to avoid duplicating long setup sequences and to keep expected counts/percentages consistent.

## Risks and Edge Cases
Because it increments counters one by one, large deltas can be slower than direct setting, but current deltas are small. The helper encodes expected phase totals that metrics tests depend on, so changes here affect percentage expectations.

## Test Signals
The helper itself has no assertions. Its signal is indirect through tests that consume the generated running/final states.
