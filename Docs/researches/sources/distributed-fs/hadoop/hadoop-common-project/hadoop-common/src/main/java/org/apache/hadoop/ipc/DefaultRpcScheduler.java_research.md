# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultRpcScheduler.java

## Purpose

`DefaultRpcScheduler` is a no-op scheduler implementation used when priority scheduling is disabled or unnecessary.

## Important APIs, control flow, and state

`getPriorityLevel()` always returns 0, `shouldBackOff()` always returns false, `addResponseTime()` does nothing, `stop()` does nothing, and the constructor ignores priority levels, namespace, and configuration. There is no state.

## Dependencies and integration points

It implements `RpcScheduler` and can be constructed reflectively by `CallQueueManager` using the `(int, String, Configuration)` signature.

## Risks and test signals

All calls share one priority level from the scheduler's perspective, so any priority queue beneath it receives no scheduler-driven differentiation. `TestCallQueueManager.testSchedulerWithoutFCQ()` and server default queue configurations are the relevant signals.
