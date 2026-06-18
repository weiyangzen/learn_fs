# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ServerIndicator.java

Purpose: numeric load indicator for throttle decisions, representing heap, direct memory, CPU load, JVM pause time, Netty direct memory, RPC queue size, and snapshot time.

Important APIs/types/functions: constructors for point, copy, and scaled threshold indicators; static `getSystemTotalJVMPauseTime`, `createFromMetrics`, `createThresholdIndicator`; getters; `addition`; `reduction`; and `toString`.

Control flow: `createFromMetrics` reads JVM pause metrics conditionally, RPC queue length, memory gauges, and OS CPU load from the metrics registry with default fallback values. `createThresholdIndicator` converts configured heap ratio to absolute heap bytes based on current heap max. `addition` and `reduction` support sliding-window aggregate indicators; reduction clamps at zero.

State and persistence: all fields are in-memory scalar values. No persistence. Scaled copies multiply additive metrics by the window size while preserving heap max and point-in-time pause total.

Dependencies/integration: used by `SystemMonitor` for current samples, aggregate windows, and active/stressed/overloaded thresholds. Reads names from `MetricsMonitorUtils` and config flag `MASTER_JVM_MONITOR_ENABLED`.

Risks: `getMetrics` uses unchecked generic casts and catches all exceptions, so type/name mismatches silently become defaults. CPU and heap threshold logic in `SystemMonitor` currently emphasizes heap usage, so other fields may be diagnostic more than decisive.

Test signals: indicator tests should cover metric defaults, threshold scaling, addition/reduction clamping, JVM monitor enabled/disabled pause handling, and string content.
