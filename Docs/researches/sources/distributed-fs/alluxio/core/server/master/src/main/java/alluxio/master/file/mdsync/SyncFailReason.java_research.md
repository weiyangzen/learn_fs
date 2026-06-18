# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncFailReason.java

Purpose: enumerates categories of metadata sync failure for reporting and diagnostics.

Important APIs and types: values include generic `UNKNOWN` and `UNSUPPORTED`, load-stage failures for UFS IO and missing mount point, and processing-stage failures for unknown errors, concurrent updates, missing files, and missing mount point.

Control flow: `LoadRequestExecutor` records load failures, `LoadResultExecutor` records processing failures, and `SyncProcessContext` records failures discovered inside sync logic. Reasons are stored in `TaskStats.SyncFailure`.

State and persistence behavior: no persistence itself. Values appear in task reports and metrics/debug output and can be surfaced to CLI/API users.

Dependencies and integration points: integrates with `TaskStats`, `LoadRequestExecutor`, `LoadResultExecutor`, and `DefaultSyncProcess`.

Risks: enum lacks numeric stable ids, so serialized text consumers should not assume ordinal stability. Some values are broad, so overuse of `PROCESSING_UNKNOWN` can reduce debuggability.

Test signals: tests should verify correct classification for load IO failures, mount-point missing in load versus process stage, and concurrent modification failures.
