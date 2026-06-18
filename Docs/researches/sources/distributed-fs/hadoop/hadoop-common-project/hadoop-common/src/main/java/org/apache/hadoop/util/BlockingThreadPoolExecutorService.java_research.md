# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BlockingThreadPoolExecutorService.java

Purpose: `BlockingThreadPoolExecutorService` is a bounded executor wrapper that blocks task submission through `SemaphoredDelegatingExecutor` when active plus queued tasks reach a configured limit.

Important APIs and types: static `newInstance`, `newDaemonThreadFactory`, package-visible `getNamedThreadFactory`, testing `getActiveCount`, and `toString`. It wraps a fixed-size `ThreadPoolExecutor`.

Control flow: `newInstance` creates a queue sized `waitingTasks + activeTasks`, a fixed active-thread executor, daemon `SubjectInheritingThread`s, core timeout, and a rejection handler that logs unexpected rejections. The superclass controls permit acquisition/release around submissions.

State and persistence behavior: stores the delegate executor and inherited semaphore state. No persistence.

Dependencies and integration points: depends on Java executor primitives, Hadoop `SubjectInheritingThread`, and `SemaphoredDelegatingExecutor`. Used where Hadoop needs backpressure rather than unlimited queued work.

Risks: rejected executions are logged but not rethrown by the handler, though the semaphore should prevent them. Daemon threads will not keep the JVM alive. Misconfigured zero/negative counts are not validated here unless superclass/executor rejects them.

Test signals: cover blocking at permit limit, permit release on completion/failure, thread naming/daemon priority, queue sizing, timeout of idle core threads, and `toString` active count.
