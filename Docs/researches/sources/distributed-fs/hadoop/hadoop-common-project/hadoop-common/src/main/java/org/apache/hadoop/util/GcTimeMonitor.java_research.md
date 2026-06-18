# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GcTimeMonitor.java

## Purpose

`GcTimeMonitor` is a daemon monitoring thread that estimates the percentage of recent wall-clock time spent in JVM garbage collection and invokes a callback when a threshold is exceeded.

## Important APIs, Types, And Functions

`Builder` configures observation window, sleep interval, threshold, and `GcTimeAlertHandler`. The constructor validates bounds and allocates a ring buffer of `TsAndData`. `work()` runs the monitoring loop. `shutdown()` stops future iterations. `getLatestGcData()` returns a clone of mutable metrics stored in `GcData`.

## Control Flow, State, And Persistence

On start, it snapshots GC counters, sleeps, computes per-interval GC pause deltas from all `GarbageCollectorMXBean`s, advances ring-buffer indices, sums pauses inside the observation window, and updates `curData`. Alerts receive a cloned snapshot. State is in-memory thread/ring-buffer data and is lost on shutdown.

## Dependencies And Integration Points

It extends `SubjectInheritingThread`, uses Java management MXBeans, and Hadoop `Preconditions`. It integrates with services that need live back-pressure or warnings when GC time becomes excessive.

## Risks And Test Signals

The alert handler can retain large object graphs if `shutdown()` is not called. Long sleep intervals reduce accuracy; huge windows are rejected by the buffer cap. Tests should cover constructor validation, ring-buffer window math, alert threshold behavior, cloned data immutability, and clean shutdown/interruption.
