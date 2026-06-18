# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PeriodicService.java

## Purpose
`PeriodicService` is a reusable `AbstractService` base class for router subsystems that execute a task repeatedly with fixed delay, such as NameNode heartbeat, router heartbeat, safemode checks, and quota updates.

## Important APIs, Types, And Functions
- Constructors set a service name and interval, defaulting to one minute.
- `setIntervalMs` changes the interval before the service starts and throws `ServiceStateException` if called after start.
- `serviceStart` and `serviceStop` start and stop periodic execution.
- `startPeriodic` creates the runnable wrapper, sets `isRunning`, and schedules it with fixed delay.
- `stopPeriodic` clears `isRunning` and shuts down the scheduler.
- `periodicInvoke()` is the abstract hook implemented by subclasses.
- Protected counters expose run count, error count, and last successful update time.

## Control Flow
`serviceStart` delegates to `startPeriodic`, which first calls `stopPeriodic`, then schedules a runnable with initial delay zero. The runnable checks `isRunning`, calls `periodicInvoke`, increments `runCount`, and records `lastRun`; any exception increments `errorCount` and is logged without stopping future executions.

## State And Persistence
State is in-memory only: interval, scheduler, running flag, run/error counters, and last-run timestamp. It has no external persistence. The scheduler is constructed once in the constructor and shut down on stop.

## Dependencies And Integration Points
It depends on Hadoop service lifecycle APIs, Java scheduled executors, Guava `ThreadFactoryBuilder`, and Hadoop `Time`. Router periodic services subclass it to inherit consistent lifecycle and metric-like counters.

## Risks And Edge Cases
Because the scheduler is shut down in `stopPeriodic`, calling `startPeriodic` after a full stop on the same instance may fail because the executor cannot accept new tasks. Counters are not atomic; they are adequate for approximate service inspection but not strict concurrent accounting. Long-running `periodicInvoke` calls delay the next tick because scheduling is fixed-delay.

## Test Signals
Coverage is indirect through lifecycle tests for subclasses, especially `TestRouterNamenodeHeartbeat`, `TestRouterSafemode`, router heartbeat tests, and quota update tests. Unit tests should assert exception isolation and interval immutability after start.
