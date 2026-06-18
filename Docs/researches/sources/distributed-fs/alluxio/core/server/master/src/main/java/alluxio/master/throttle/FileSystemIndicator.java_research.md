# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/FileSystemIndicator.java

Purpose: point-in-time snapshot of selected filesystem/master counters for throttle diagnostics, with support for delta computation against a prior snapshot.

Important APIs/types/functions: static `OBSERVED_MASTER_COUNTER`; constructors; `getCounter`, `getPitTimeMS`, `setCounter`, `setPitTimeMS`, `deltaTo`, and `toString`.

Control flow: construction populates a map by reading every observed counter from `MetricsSystem.METRIC_REGISTRY`. `deltaTo` subtracts baseline values for all observed counters, preserving only counters in the observed list. `SystemMonitor` creates these snapshots only when status is stressed or overloaded and logs deltas when consecutive stressed/overloaded samples exist.

State and persistence: state is an in-memory map of counter name to long plus snapshot time. No persistence.

Dependencies/integration: depends on counter-name constants from `MetricsMonitorUtils.FileSystemCounterName` and Dropwizard metrics registry. It gives `SystemMonitor` filesystem activity context during pressure events.

Risks: accessing counters through `METRIC_REGISTRY.counter(name)` creates missing counters with zero values, which may pollute the registry. The observed list is static and manual, so new critical filesystem metrics are missed until added.

Test signals: `IndicatorsTests` should cover snapshot values, copy construction, delta math with missing baseline counters, setter behavior, and string rendering.
