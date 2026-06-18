# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBpServiceActorScheduler.java

## Purpose
This file unit-tests `BPServiceActor.Scheduler`, which controls when DataNode actors send heartbeats, lifelines, full block reports, and outlier reports to a NameNode.

## Important APIs, Types, and Functions
- `BPServiceActor.Scheduler` is constructed with heartbeat, lifeline, block report, and outlier report intervals.
- Methods under test include `isHeartbeatDue`, `scheduleNextHeartbeat`, `scheduleHeartbeat`, `scheduleBlockReport`, `scheduleNextBlockReport`, `forceFullBlockReportNow`, `scheduleNextLifeline`, `getLifelineWaitTime`, `isOutliersReportDue`, and `scheduleNextOutlierReport`.
- `makeMockScheduler` spies on the scheduler and stubs `monotonicNow`.
- `getTimestamps` supplies boundary and random timestamps including zero, min/max long, near-overflow, positive random, and negative random values.

## Control Flow and Behavior
Every test iterates across timestamp values to detect overflow and sign bugs. Initial state should make heartbeat and block report due. Immediate block report scheduling sets next report time to now, while delayed scheduling chooses a random-ish time before the full delay bound. `scheduleNextBlockReport` is tested for both reset and non-reset modes and for reports delayed past their scheduled time. Heartbeat scheduling is checked to avoid immediate storms after delayed processing. Lifeline scheduling validates due state and nonnegative wait time. Outlier report scheduling validates interval gating.

## State and Persistence
The scheduler is in-memory only. It mutates next heartbeat, lifeline, block report, and outlier report times plus `resetBlockReportTime`.

## Dependencies and Integration Points
The test depends on Mockito spies, AssertJ/JUnit assertions, `Time.monotonicNow`, and `BPServiceActor.Scheduler`. It does not start a DataNode or cluster.

## Risks and Edge Cases
The suite targets arithmetic overflow, negative monotonic values in unit tests, heartbeat storms after delayed processing, forced block report re-scheduling drift, and lifeline wait time under a current time beyond the scheduled time.

## Test Signals
Signals are exact or bounded next-time calculations, due/not-due booleans, modulo alignment for delayed block reports, and nonnegative lifeline wait values.
