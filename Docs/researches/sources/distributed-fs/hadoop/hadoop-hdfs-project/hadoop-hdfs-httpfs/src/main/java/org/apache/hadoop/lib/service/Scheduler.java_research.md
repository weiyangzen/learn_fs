<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java

## Purpose
`Scheduler` is the service interface for running repeated background tasks inside the HttpFS server.

## Important APIs, Types, And Functions
It declares two overloads: `schedule(Callable<?> callable, long delay, long interval, TimeUnit unit)` and `schedule(Runnable runnable, long delay, long interval, TimeUnit unit)`.

## Control Flow
Services use it in `postInit` after dependencies exist. `FileSystemAccessService` schedules cache purging; `InstrumentationService` schedules one-second sampler updates. `SchedulerService` implements fixed-delay execution with instrumentation.

## State And Persistence
The interface has no state. Scheduled task state is implementation-owned and in memory.

## Dependencies And Integration Points
It depends on Java concurrency types and is implemented by `SchedulerService`.

## Risks
Fixed-delay semantics and shutdown behavior are implementation choices. Callers need idempotent tasks because failures are logged/instrumented but scheduling continues.

## Test Signals
Tests should verify callable/runnable scheduling, delay/interval forwarding, behavior under halted server status, and shutdown rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Scheduler.java -->
