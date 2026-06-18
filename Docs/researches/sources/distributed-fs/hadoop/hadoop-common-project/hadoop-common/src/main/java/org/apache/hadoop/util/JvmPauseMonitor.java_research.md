# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JvmPauseMonitor.java

## Purpose

`JvmPauseMonitor` is an `AbstractService` that runs a daemon loop to detect JVM or host pauses by measuring sleep overshoot and logging GC activity around the pause.

## Important APIs, Types, And Functions

Configuration keys are `jvm.pause.warn-threshold.ms` and `jvm.pause.info-threshold.ms`. Service hooks are `serviceInit()`, `serviceStart()`, and `serviceStop()`. Metrics getters expose warning count, info count, and total extra sleep time. Helpers `getGcTimes()` and `formatMessage()` describe GC deltas per collector.

## Control Flow, State, And Persistence

On start, a daemon `Monitor` repeatedly records GC counters, sleeps for 500 ms, computes extra sleep time via `StopWatch`, compares thresholds, logs WARN/INFO with GC differences, and accumulates counters. Stop flips `shouldRun`, interrupts, and joins the thread. State is service lifecycle, monitor thread, counters, and logs only.

## Dependencies And Integration Points

It depends on Hadoop `AbstractService`, `Configuration`, `Daemon`, `StopWatch`, local `Lists`/`Sets`, Guava-thirdparty `Joiner`/`Maps`, and Java MXBeans. Hadoop daemons use it for operational visibility into GC or host scheduling stalls.

## Risks And Test Signals

Counters are not atomic, though normally read from service threads. The sample `main()` intentionally leaks memory for manual testing. Tests should cover thresholds from configuration, start/stop lifecycle, interruption, log-level classification, GC-delta formatting, and metric accumulation.
