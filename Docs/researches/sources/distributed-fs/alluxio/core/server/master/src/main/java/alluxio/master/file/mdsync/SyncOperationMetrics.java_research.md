# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperationMetrics.java

Purpose: centralizes Dropwizard counters for metadata sync operation outcomes.

Important APIs and types: static counters cover files created, deleted, recreated, updated, skipped due to concurrent update, skipped on mount point, no-op, and skipped non-persisted. Each counter is created through `MetricsSystem.counter` using a `MetricKey`.

Control flow: counters are initialized when the class loads. `SyncOperation` references these counters, and `SyncProcessContext.reportSyncOperationSuccess` increments the appropriate counter.

State and persistence behavior: metrics state is process-local and exported through Alluxio metrics infrastructure. No journaled metadata is owned.

Dependencies and integration points: depends on `MetricKey`, `MetricsSystem`, and `Counter`. It integrates with `SyncOperation` and the metrics backend.

Risks: static initialization can register counters early; metric key names must remain stable for dashboards and alerts. Adding a sync operation requires adding a counter and wiring it through `SyncOperation`.

Test signals: tests can verify counter registration names and operation-to-counter increments through `SyncProcessContext` or metrics registry assertions.
