<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java

## Purpose
`Instrumentation` is the internal service interface for counters, timing samples, variables, samplers, and snapshot export used by HttpFS services.

## Important APIs, Types, And Functions
Nested `Cron` supports `start()` and `stop()` timing. Nested `Variable<T>` supplies dynamic values. Methods create crons, increment counters, add completed crons, add variables, add one-second samplers, and return `Map<String, Map<String, ?>> getSnapshot()`.

## Control Flow
`FileSystemAccessService` creates a cron around executor calls and registers unmanaged filesystem variables/samplers. `SchedulerService` instruments scheduled task executions/failures/skips. `HttpFSServer` exposes snapshots through the admin-only `INSTRUMENTATION` operation.

## State And Persistence
The interface has no state; implementation stores in-memory metrics. Snapshots are live maps, not persisted.

## Dependencies And Integration Points
Implemented by `InstrumentationService` and depended on by scheduler/filesystem services and the REST instrumentation endpoint.

## Risks
Snapshot value types are heterogeneous and JSON serialization depends on implementation wrappers. Callers must stop crons before adding them.

## Test Signals
Tests should assert counter increments, cron timings, variable sampling, scheduler integration, and snapshot serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Instrumentation.java -->
