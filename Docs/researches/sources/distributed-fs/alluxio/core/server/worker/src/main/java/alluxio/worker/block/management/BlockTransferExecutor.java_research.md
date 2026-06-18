# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferExecutor.java

Purpose: Executes lists of block move and swap orders concurrently while backing off from active user IO.

Important APIs: Constructor wires executor, block store, load tracker, concurrency limit, and partitioner; `executeTransferList` optionally accepts an exception handler; private `executeTransferPartition` performs each transfer.

Control flow: Empty lists return an empty result. Non-empty lists are partitioned, submitted via `ExecutorService.invokeAll`, and partition counters are aggregated. Each transfer is skipped if `loadDetected` sees activity at source or destination; moves call `LocalBlockStore.moveBlock`; swaps perform two moves with reserved space enabled.

State and persistence: Holds service dependencies only. Operations mutate block-store metadata and underlying block files through `LocalBlockStore`.

Dependencies and integration: Consumes `BlockTransferInfo`, `AllocateOptions`, `Sessions`, `StoreLoadTracker`, and `BlockTransferPartitioner`. Used by all concrete tier tasks.

Risks and test signals: TODO notes missing location locks, so concurrent partitions can collide. Swap is not guaranteed atomically. Tests should cover partition aggregation, backoff counting, interrupt handling, exception callback invocation, and swap reserved-space behavior.
