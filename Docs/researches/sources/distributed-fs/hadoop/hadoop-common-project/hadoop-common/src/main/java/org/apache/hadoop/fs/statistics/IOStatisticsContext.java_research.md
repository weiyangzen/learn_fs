# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsContext.java

Purpose: public interface for per-thread IOStatistics capture. It gives filesystem and stream code a current-thread context whose aggregator can collect statistics from operations and later return an incremental `IOStatisticsSnapshot`.

Important APIs, types, and functions: extends `IOStatisticsSource`; exposes `getAggregator()`, `snapshot()`, `getID()`, and `reset()`. Static helpers delegate to `IOStatisticsContextIntegration`: `getCurrentIOStatisticsContext()`, `setThreadIOStatisticsContext()`, and `enabled()`.

Control flow: callers fetch the current context through the static accessor, pass `getAggregator()` into statistics-producing code, and call `snapshot()` or `reset()` when work units complete. The accessor wraps the integration result in `requireNonNull()` to catch regression to a null context.

State and persistence: no direct state in the interface. Runtime state lives in implementation instances and in the thread map managed by `IOStatisticsContextIntegration`. Snapshots can be serialized through `IOStatisticsSnapshot`; the live context itself is process/thread scoped.

Dependencies and integration points: depends on `IOStatisticsAggregator`, `IOStatisticsSnapshot`, `IOStatisticsSource`, and the implementation bridge in `statistics.impl`. It is the public entry point used by filesystem clients that want thread-level accounting.

Risks and test signals: behavior depends on the global thread-level statistics configuration. Tests should cover enabled and disabled modes, null reset behavior, unique IDs, snapshot/reset semantics, and the safety check that the current context is never null.
