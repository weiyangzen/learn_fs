# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/AbstractWorker.java

## Purpose
`AbstractWorker` is the base class for Alluxio workers, centralizing executor-service lifecycle management.

## Important APIs, Types, and Functions
It stores an `ExecutorServiceFactory` and an `ExecutorService`, exposes protected `getExecutorService()`, and implements `start(WorkerNetAddress)`, `stop()`, and `close()`.

## Control Flow, State, and Persistence
`start()` asserts the executor has not already been created and obtains one from the factory. `stop()` calls `shutdownNow()`, waits up to ten seconds, logs timeout or interruption, restores interrupt status, and clears the executor in a `finally` block. `close()` delegates to `stop()`. It has no persistence.

## Dependencies and Integration Points
It depends on the `Worker` interface, `ExecutorServiceFactory`, `WorkerNetAddress`, Guava `Preconditions`, and Java executor APIs. Concrete workers subclass it and use the executor for internal tasks.

## Risks and Test Signals
Risks include not being thread-safe, abrupt `shutdownNow()` interrupting tasks, and `getExecutorService()` returning null before start or after stop. Signals are start/stop idempotency expectations, executor factory invocation, timeout logging, and close delegation.
