# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/executor/ExecutorServiceBuilder.java

## Purpose
`ExecutorServiceBuilder` constructs configured RPC executor services for master, job master, and worker processes.

## Important APIs, Types, And Functions
`buildExecutorService` reads per-host configuration templates, validates keepalive and fork-join parameters, creates either Alluxio's JSR `ForkJoinPool` or a Java `ThreadPoolExecutor`, and wraps it in `AlluxioExecutorService`. `RpcExecutorHost` maps enum values to configuration prefixes.

## Control Flow, State, Dependencies, Risks, And Tests
The builder first resolves executor type, shared pool sizes, and thread naming. FJP mode reads parallelism, min-runnable, and async mode; TPE mode selects linked, bounded linked, array, or synchronous queues and applies core-thread timeout. State is runtime thread/queue state, not persistent. Dependencies include `Configuration`, `PropertyKey.Template`, `ThreadFactoryUtils`, `ForkJoinPool`, queue enums, and metrics counters. Risks include bad configuration causing startup failure, bounded queue sizing tied to max pool size, and an error message referencing master max pool for all hosts. Tests should cover every executor type/queue type, invalid values, thread naming, counter wrapping, and host prefix strings.
