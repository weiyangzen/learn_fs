# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlluxioExecutorService.java

## Purpose
`AlluxioExecutorService` wraps an `ExecutorService` to expose RPC queue/active/pool metrics and optionally warn about active operations during shutdown.

## Important APIs, Types, And Functions
`getRpcQueueLength`, `getActiveCount`, and `getPoolSize` support `ThreadPoolExecutor` and Alluxio `ForkJoinPool`. All standard `ExecutorService` methods delegate, except `invokeAny` variants throw unsupported. Submission and execution methods briefly increment/decrement an optional `Counter`.

## Control Flow, State, Dependencies, Risks, And Tests
The wrapper does not own persistence; it exposes live executor state. Dependencies are Java executor APIs, Alluxio `ForkJoinPool`, Dropwizard `Counter`, and logging. A key risk is that the counter measures submission calls, not task lifetime, because it is decremented immediately after delegation; shutdown warnings may therefore not reflect active queued/running RPCs unless the counter has separate external tracking. Unsupported executor types throw for metric methods. Tests should cover metric delegation for both executor classes, shutdown warnings, counter behavior, and unsupported `invokeAny`.
