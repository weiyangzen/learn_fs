# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PersistJob.java

## Purpose
`PersistJob` is a value object representing an async persist job for one file. It tracks the file id, display URI, job id, temporary UFS path, retry timer, and cancellation state.

## Important APIs, types, and functions
The constructor initializes immutable job identity fields and sets `CancelState.NOT_CANCELED`. Getters expose file id, URI, job id, temp UFS path, timer, and cancel state. `setCancelState` mutates cancellation state. The nested `CancelState` enum has `NOT_CANCELED`, `TO_BE_CANCELED`, and `CANCELING`. `equals`, `hashCode`, and `toString` are implemented with Guava helpers.

## Control flow
The class has no job execution logic. Async persistence managers update cancellation state and use the timer to decide retries.

## State and persistence behavior
The object is in-memory and not thread-safe. It represents master scheduling state; any durable persistence of async persist state must happen in surrounding master code.

## Dependencies and integration points
It depends on `AlluxioURI` and `ExponentialTimer`. It integrates with async persist scheduling, worker polling, and retry/cancel code in the file-system master.

## Risks
The URI can be stale and is documented for logging only. Including mutable `ExponentialTimer` and mutable cancel state in equality/hash code can be dangerous if instances are used as map keys or set members. Concurrent access needs external synchronization.

## Test signals
Unit tests should cover equality/toString, cancel-state transitions, and scheduler behavior that uses timers and temp UFS paths. Integration tests should ensure stale URI does not drive correctness decisions.
