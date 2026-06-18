# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/instrumentation/TestInstrumentationService.java

Purpose: Unit/integration suite for instrumentation primitives and the `InstrumentationService`.

Important APIs/types/functions: tests `cron`, `timer`, `sampler`, `variableHolder`, `service`, and `sampling`; classes `InstrumentationService.Cron`, `Timer`, `Sampler`, `VariableHolder`; public `Instrumentation` APIs `incr`, `createCron`, `addCron`, `addVariable`, `addSampler`, and `getSnapshot`.

Control flow: `cron` validates start/stop/end timing and illegal states. `timer` adds several cron samples and validates last/average own/total values plus JSON serialization. `sampler` validates rolling average behavior and JSON. `variableHolder` serializes a variable value. `service` boots a server with instrumentation, records counters/timers/variables/samplers, and confirms snapshot sections for OS env, system properties, JVM, counters, timers, variables, and samplers. `sampling` combines instrumentation with `SchedulerService`, registers a sampled variable, sleeps, and verifies scheduled samples occurred.

State and persistence: all metrics are in-memory. Tests use time sleeps and server lifecycle under `@TestDir`.

Dependencies/integration: Hadoop `Time`, JSON-simple, `Server`, scheduler service for periodic sampling, and `HTestCase` wait ratio.

Risks and test signals: good coverage of metric math and serialization. Timing tolerances and sleeps can be platform-sensitive, but `getWaitForRatio` is overridden to 1 for predictable duration expectations.
