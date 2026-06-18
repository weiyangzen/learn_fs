# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SemaphoredDelegatingExecutor.java

## Purpose
`SemaphoredDelegatingExecutor` wraps an `ExecutorService` so task submission blocks when a configured number of queued/running tasks is reached. It isolates semaphore backpressure from concrete thread-pool implementation.

## Important APIs, Types, And Functions
The class extends Guava `ForwardingExecutorService`. Important APIs are constructors, `submit` overloads, `execute`, `getAvailablePermits`, `getWaitingCount`, `getPermitCount`, and wrappers `RunnableWithPermitRelease` and `CallableWithPermitRelease`.

## Control Flow
Each `submit` acquires a semaphore permit while tracking acquisition duration, then delegates a wrapper task that releases the permit in `finally`. Interrupted acquisition returns an immediate failed future for `submit`. `execute` also acquires, but if interrupted it only restores interrupt state and still delegates a wrapped command. Bulk invoke methods are explicitly unimplemented.

## State And Persistence
State is an in-memory semaphore, delegate executor, permit count, and duration tracker factory. No persistence exists.

## Dependencies And Integration Points
It depends on shaded Guava forwarding/futures, Java concurrency, Hadoop IO statistics duration tracking, and store statistic name `ACTION_EXECUTOR_ACQUIRED`.

## Risks
The `execute` interruption path can submit without a permit and later release one, increasing permit count incorrectly. Delegate rejection after acquiring a permit can leak a permit because wrapping happens before delegate execution but no rejection cleanup exists. `invokeAll`/`invokeAny` throw runtime exceptions.

## Test Signals
Tests should cover blocking at permit limits, permit release after success/failure, interrupted submit behavior, interrupted execute permit accounting, delegate rejection, fairness mode, duration metric emission, and unsupported bulk operations.
