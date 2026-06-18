<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java

## Purpose
`JvmMetrics` is a private metrics2 source that publishes JVM memory, garbage collection, pause, GC time percentage, and thread-state metrics for Hadoop daemons.

## Important APIs and Types
It implements `MetricsSource`. Public/static entry points include `create`, `reattach`, `initSingleton`, `shutdownSingleton`, `name`, and `description` via enum `JvmMetricsInfo`. Instance setters attach `JvmPauseMonitor` and `GcTimeMonitor`. The singleton enum stores one registered implementation.

## Control Flow
`create` reloads a `Configuration` to decide whether to use `ThreadMXBean`, constructs the source, and registers it with a `MetricsSystem`. `getMetrics` creates a `JvmMetrics` record tagged with process and session, then calls memory, GC, and thread collection helpers. GC collection iterates JVM GC beans, skips ZGC cycle counters, emits per-GC counters through a cached `MetricsInfo[]`, totals count/time, and appends pause monitor and GC time monitor values when present.

## State and Persistence
State is process-local: MXBean references, process/session strings, optional monitors, and a concurrent cache of generated GC metric info names. The singleton registration is mutable for tests and daemon lifecycle.

## Dependencies and Integration Points
It integrates Java management MXBeans, Hadoop `DefaultMetricsSystem`, `MetricsCollector`, `JvmPauseMonitor`, `GcTimeMonitor`, and metrics info enums.

## Risks and Test Signals
Thread enumeration races are handled by null checks, but thread group fallback only sees the current group. New GC names create dynamic metric names. Tests should cover singleton lifecycle, registration reattach, memory max `-1`, ZGC cycle skip, pause/gc monitor values, per-GC info caching, and both thread collection modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java -->
