# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/MetricsMonitorUtils.java

Purpose: centralized metric-name constants used by throttle monitoring code.

Important APIs/types/functions: nested classes `MemoryGaugeName`, `OSGaugeName`, `ServerPrefix`, `ServerGaugeName`, `FileSystemGaugeName`, and `FileSystemCounterName`.

Control flow: no runtime control flow beyond class initialization. Constants are composed from `MetricKey` and `MetricsSystem.getMetricName` where needed.

State and persistence: static constants only, no mutable state and no persistence.

Dependencies/integration: consumed by `ServerIndicator` for JVM/OS/RPC gauges and by `FileSystemIndicator` for filesystem counter snapshots. It ties throttle logic to the exact names registered by the metrics subsystem.

Risks: string constants such as `Master.getConfigHashInProgress` are hand-written and can drift from instrumentation names. Some nested constants include already-prefixed metric names while others are raw `MetricKey` names, so callers must know which registry lookup form to use.

Test signals: compile-time usage is the main guard. Useful tests would validate that each referenced gauge/counter name exists after normal master metric registration and that prefixed names match the registry keys read by `ServerIndicator`.
