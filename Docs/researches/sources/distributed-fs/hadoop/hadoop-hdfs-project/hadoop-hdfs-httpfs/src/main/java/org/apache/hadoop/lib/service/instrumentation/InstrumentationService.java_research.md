<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java

## Purpose
`InstrumentationService` is the in-memory implementation of the instrumentation interface. It tracks counters, timer rings, dynamic variables, rolling samplers, JVM/process information, and returns a snapshot map for the admin endpoint.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `instrumentation`; `timers.size` controls timer ring length. Internal maps are grouped by metric group/name. `getToAdd` lazily creates group maps and metric holders under locks. Nested `Cron` tracks own and total elapsed time. `Timer` stores ring buffers for own/total durations and exports last/average values as JSON. `VariableHolder` and `Sampler` implement JSON-aware wrappers. `SamplersRunnable` samples registered variables every second.

## Control Flow
`init` creates locks/maps, installs OS env, system properties, JVM memory variables, and exposes all categories in a linked snapshot map. `postInit` schedules the sampler runnable if a scheduler service is available. Callers use `incr`, `createCron`/`addCron`, `addVariable`, and `addSampler`; snapshots are returned directly to `HttpFSServer` instrumentation responses.

## State And Persistence
All state is process-local memory. The snapshot includes live environment and system property maps, counters, timers, variables, and samplers. Sampler windows roll in arrays and maintain an atomic sum.

## Dependencies And Integration Points
It depends on `Scheduler`, JSON-simple interfaces, Hadoop `Time`, and the service framework. It is consumed by `FileSystemAccessService`, `SchedulerService`, and the admin REST endpoint.

## Risks
`Timer.getValues` assumes at least one cron has been added; with `last == -1`, direct serialization could index invalid arrays. `addSampler` can add the same sampler object multiple times if called repeatedly for the same group/name. Snapshot exposes environment and system properties, so the admin endpoint must remain restricted. Variable callbacks can throw during JSON serialization.

## Test Signals
Tests should cover counter creation, cron start/stop reuse rejection, timer averages, snapshot JSON serialization before and after metrics exist, sampler rolling average, duplicate sampler behavior, and admin endpoint access control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/instrumentation/InstrumentationService.java -->
