# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskGroup.java

Purpose: groups one or more `BaseTask`s created for a single user metadata-sync request, especially recursive syncs that include nested mount points.

Important APIs and types: constructor requires at least one task and stores a group id. `getBaseTask`, `getTasks`, `getTaskCount`, `allSucceeded`, `toProtoTasks`, `getGroupId`, and `waitAllComplete` expose group behavior.

Control flow: `DefaultSyncProcess.syncPath` creates a group with the primary task plus nested mount tasks. `waitAllComplete` waits sequentially on each task, computing remaining timeout with a stopwatch and propagating the first task failure or timeout.

State and persistence behavior: in-memory grouping only. The tasks in the group perform persistence and cache updates.

Dependencies and integration points: depends on `BaseTask`, `SyncMetadataTask`, `DeadlineExceededRuntimeException`, Guava `Stopwatch`, and `DefaultSyncProcess` group cache.

Risks: waits are sequential, so a later task may get little or no timeout budget if earlier tasks consume it. `getBaseTask` assumes the first task is semantically primary.

Test signals: tests should cover empty-constructor rejection, allSucceeded aggregation, proto conversion, timeout budget handling, and failure propagation.
