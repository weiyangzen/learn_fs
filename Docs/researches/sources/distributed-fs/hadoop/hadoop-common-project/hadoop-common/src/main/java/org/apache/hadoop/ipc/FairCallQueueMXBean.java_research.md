# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/FairCallQueueMXBean.java

## Purpose
This interface is the JMX management contract for `FairCallQueue`. It exposes per-priority queue size, per-priority overflow counters, and a revision counter for detecting queue replacement.

## Important APIs, Types, and Functions
`getQueueSizes()` returns an array indexed by priority level. `getOverflowedCalls()` returns the accumulated overflow count for each subqueue. `getRevision()` is incremented by `FairCallQueue.MetricsProxy` whenever a new queue delegate is installed for the namespace.

## Control Flow
There is no implementation flow in this file. Calls are served by `FairCallQueue.MetricsProxy`, which resolves the current queue through a weak reference and returns empty arrays if no live delegate remains.

## State and Persistence Behavior
The interface declares no state. Runtime state comes from the implementing metrics proxy and underlying `FairCallQueue`.

## Dependencies and Integration Points
It is registered as `Hadoop:service=<ns>,name=FairCallQueue` by `MBeans.register` and feeds Hadoop metrics records. `TestFairCallQueue` validates MBean access and metrics values.

## Risks and Test Signals
The main compatibility risk is changing array ordering or semantics. Tests should verify the exposed arrays match subqueue priority order and that `getRevision` changes after queue replacement.
