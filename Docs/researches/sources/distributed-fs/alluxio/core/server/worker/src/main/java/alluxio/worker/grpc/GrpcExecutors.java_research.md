# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcExecutors.java

## Purpose
`GrpcExecutors` defines shared executor pools for worker gRPC cache, read, serialized read-response, and write work. It also wraps each executor so authenticated client user context is transferred to worker threads.

## Important APIs, Types, and Functions
Static executors include `CACHE_MANAGER_EXECUTOR`, `BLOCK_READER_EXECUTOR`, `BLOCK_READER_SERIALIZED_RUNNER_EXECUTOR`, and `BLOCK_WRITER_EXECUTOR`. Pool sizes, queue types, and thread names come from worker network configuration. The static initializer registers executor metrics. `ImpersonateThreadPoolExecutor` overrides `execute` and `submit` variants to capture `AuthenticatedClientUser`, set it inside the worker thread, optionally increment `WORKER_ACTIVE_OPERATIONS`, and clean up thread-local state.

## Control Flow, State, and Persistence
This is process-global executor state. Cache manager work uses a bounded `UniqueBlockingQueue`; block reader and writer pools use `SynchronousQueue`; serialized read response has a small queue and caller-runs fallback. There is no durable persistence, but the pools gate all high-volume network IO concurrency.

## Dependencies and Integration Points
It integrates configuration properties, `MetricsSystem`, `ThreadFactoryUtils`, `AuthenticatedClientUser`, `DefaultBlockWorker.Metrics`, and gRPC read/write/cache handlers.

## Risks and Test Signals
Risks include rejected tasks under saturated synchronous pools, active-operation counter imbalance if unsupported executor APIs are used, static initialization using stale configuration, and thread-local impersonation leaks. Tests should verify user propagation, metric counters around success/failure, shutdown behavior, queue saturation, and unsupported `invokeAll`/`invokeAny` failure.
