<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java

## Purpose
`SchedulerService` implements the background scheduler used by HttpFS services. It wraps scheduled work with server-status checks, instrumentation counters, timing, and error logging.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `scheduler`, depends on `Instrumentation`, and uses `threads` config defaulting to 5. `init` creates a `ScheduledThreadPoolExecutor`. `destroy` calls `shutdownNow` and waits up to about 30 seconds. `schedule(Callable, ...)` wraps callable execution in a `Runnable` and uses `scheduleWithFixedDelay`. `schedule(Runnable, ...)` adapts via `RunnableCallable`.

## Control Flow
For each scheduled tick, the wrapper retrieves `Instrumentation`, skips execution and increments `.skips` if server status is `HALTED`, otherwise increments `.execs`, starts a cron, calls the task, increments `.fails` on exception, and records timing in `finally`.

## State And Persistence
State is the scheduled executor service and queued tasks. Metrics are in instrumentation memory. No persistent state is written.

## Dependencies And Integration Points
It integrates with `InstrumentationService`, `RunnableCallable`, service lifecycle, and callers such as filesystem cache purging and instrumentation sampling.

## Risks
Tasks are scheduled with fixed delay, not fixed rate. Exceptions are swallowed after logging, so failing tasks continue to be rescheduled. `destroy` logs but does not restore interrupt status after catching `InterruptedException`. Scheduling after shutdown throws `IllegalStateException`.

## Test Signals
Tests should cover thread-count config, callable/runnable adaptation, halted-skip counters, execution/failure counters, cron recording, fixed-delay scheduling, and destroy timeout/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/scheduler/SchedulerService.java -->
