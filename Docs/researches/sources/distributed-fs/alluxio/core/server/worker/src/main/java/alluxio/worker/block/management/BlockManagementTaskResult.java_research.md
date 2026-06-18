# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockManagementTaskResult.java

Purpose: Aggregates per-operation results for one management task run.

Important APIs: `addOpResults`, `getOperationResult`, `noProgress`, and `toString`.

Control flow: Tasks merge `BlockOperationResult`s by `BlockOperationType`. The coordinator checks `noProgress` to decide whether to sleep after failures or backoffs.

State and persistence: In-memory `HashMap` of operation type to mutable result. Not thread-safe and not persisted.

Dependencies and integration: Used by all management tasks and coordinator logging/backoff logic.

Risks and test signals: `noProgress` returns true when total operations equal failures plus backoffs; an empty result also returns true because counts are zero. Tests should cover empty, partial success, all failure, and merged multi-operation results.
