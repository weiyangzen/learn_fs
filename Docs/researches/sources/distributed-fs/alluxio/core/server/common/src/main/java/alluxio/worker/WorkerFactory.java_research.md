# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerFactory.java

## Purpose
`WorkerFactory` is the extension point for conditionally creating worker components.

## Important APIs, Types, and Functions
It defines `isEnabled()` and `create(WorkerRegistry, UfsManager)`.

## Control Flow, State, and Persistence
Implementations decide whether a worker should be created and build it using the shared registry and UFS manager. The interface itself has no state.

## Dependencies and Integration Points
It depends on `Worker`, `WorkerRegistry`, and `UfsManager`. Worker process bootstrapping uses factories to assemble enabled worker services.

## Risks and Test Signals
Risks include factories reporting enabled but failing during creation, registry dependency assumptions, and UFS manager sharing. Signals are enabled/disabled factory selection and created worker registration.
