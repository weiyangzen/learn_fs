# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncOperation.java

Purpose: enumerates successful metadata sync operation outcomes and binds each to a metric counter.

Important APIs and types: operations include `NOOP`, `CREATE`, `DELETE`, `RECREATE`, `UPDATE`, `SKIPPED_DUE_TO_CONCURRENT_MODIFICATION`, `SKIPPED_ON_MOUNT_POINT`, and `SKIPPED_NON_PERSISTED`. Each has an integer value and a `Counter`. `fromInteger`, `getValue`, and `getCounter` expose mapping.

Control flow: `DefaultSyncProcess` reports operations through `SyncProcessContext.reportSyncOperationSuccess`, which increments both the operation counter and task stats. `TaskStats` uses integer values to index an array of counts and formats reports using `fromInteger`.

State and persistence behavior: no persistent state. Metrics counters and task reports are in-memory/observability state.

Dependencies and integration points: depends on `SyncOperationMetrics` counters and integrates with `TaskStats`, `SyncProcessContext`, and sync CLI reporting.

Risks: integer values are array indexes; inserting new enum values or changing values can break stats indexing and report interpretation. `fromInteger` must be updated with any new operation.

Test signals: tests should cover every enum's value/counter mapping, invalid integer rejection, and task stats reporting for non-zero operation counts.
