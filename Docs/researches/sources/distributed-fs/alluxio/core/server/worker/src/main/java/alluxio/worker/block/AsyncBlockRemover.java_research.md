# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AsyncBlockRemover.java

Purpose: `AsyncBlockRemover` performs best-effort block deletion in response to master commands without blocking heartbeat handling on all removals.

Important APIs are constructors, `addBlocksToDelete`, `shutDown`, and inner `BlockRemover.run`. Control flow creates a fixed daemon thread pool, starts remover workers, de-duplicates queued/removing block IDs with a concurrent set, and pushes IDs into a blocking queue. Each remover takes a block ID, increments try/remove metrics, calls `BlockWorker.removeBlock` using `MASTER_COMMAND_SESSION_ID`, logs failures as retry-later best effort, and removes the ID from the in-progress set in `finally`. Shutdown sets a flag and interrupts the pool.

State and persistence are in-memory queue/set plus metrics counters/gauges. Dependencies include `BlockWorker`, `Sessions`, metrics system, Java concurrency, and test-visible constructor injection. Integration point is `BlockMasterSync.handleMasterCommand` for `Free` commands. Risks include blocks being dropped from `mRemovingBlocks` after failed removal without automatic requeue, unbounded queue growth, and duplicate check race between `contains` and `add`. No direct tests in this subset are listed, but metrics and visible constructor support targeted tests.
