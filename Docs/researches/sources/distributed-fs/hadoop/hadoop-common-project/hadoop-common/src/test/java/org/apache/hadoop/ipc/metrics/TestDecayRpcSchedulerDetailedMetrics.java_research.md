# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestDecayRpcSchedulerDetailedMetrics.java

## Purpose

`TestDecayRpcSchedulerDetailedMetrics` ensures `DecayRpcScheduler` registers and unregisters its detailed metrics source with the default metrics system.

## Important APIs, Types, And Functions

The test constructs `DecayRpcScheduler(4, "ipc.8020", conf)`, obtains `scheduler.getDecayRpcSchedulerDetailedMetrics()`, queries `DefaultMetricsSystem.instance().getSource(metrics.getName())`, and calls `scheduler.stop()`.

## Control Flow

After scheduler construction, the detailed metrics source must be visible in the metrics system. After `stop()`, the source must be absent.

## State And Persistence Behavior

State lives in the singleton/default metrics system registry and the scheduler instance. No durable state is written.

## Dependencies And Integration Points

This file integrates IPC scheduler metrics with Hadoop metrics2 `DefaultMetricsSystem`. It is a lifecycle guard for avoiding leaked metrics sources between schedulers/tests.

## Risks And Test Signals

Risks include duplicate/leaked source names, missing registration, or failure to unregister on stop. Signals are `assertNotNull` before stop and `assertNull` after stop.
