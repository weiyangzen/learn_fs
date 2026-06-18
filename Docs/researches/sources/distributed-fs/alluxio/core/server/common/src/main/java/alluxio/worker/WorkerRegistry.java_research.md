# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/WorkerRegistry.java

## Purpose
`WorkerRegistry` is the worker-specific typed registry for `Worker` instances started with a `WorkerNetAddress`.

## Important APIs, Types, and Functions
It extends `Registry<Worker, WorkerNetAddress>` and defines only a public constructor.

## Control Flow, State, and Persistence
All ordering, dependency, start, stop, and lookup behavior comes from the generic `Registry` base class. This subclass contributes type binding only.

## Dependencies and Integration Points
It depends on `Registry`, `Worker`, and `WorkerNetAddress`. Worker factories and worker process bootstrap code use it to manage worker services.

## Risks and Test Signals
Risks mirror the base registry: dependency cycles, missing services, and startup/shutdown order. Signals can follow `RegistryTest` patterns with worker types.
