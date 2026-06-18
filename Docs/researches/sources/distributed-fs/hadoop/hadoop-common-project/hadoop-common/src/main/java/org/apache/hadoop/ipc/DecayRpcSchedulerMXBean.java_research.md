# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcSchedulerMXBean.java

## Purpose

`DecayRpcSchedulerMXBean` is the JMX management contract for `DecayRpcScheduler` metrics.

## Important APIs, control flow, and state

The interface exposes scheduling decision JSON, call-volume JSON, unique identity count, total call volume, average response time per priority, and completed response counts from the last window. It has no implementation state.

## Dependencies and integration points

`DecayRpcScheduler` implements it directly, and `DecayRpcScheduler.MetricsProxy` registers an MBean per namespace while delegating to the active scheduler through a weak reference.

## Risks and test signals

The JSON-returning methods can return error strings when serialization fails, so JMX clients should not assume valid JSON unconditionally. Proxy default values are returned when the delegate is gone. `TestDecayRpcScheduler` and metrics2 tests are the relevant signals.
