# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerSafeMode.java

## Purpose
`BlockManagerSafeMode` is the block-level safe mode state machine used by the NameNode. It counts complete blocks that have reached safe redundancy, checks live datanode minimums, waits through the configured extension period, initializes reconstruction queues at the configured threshold, and prevents normal safe-mode exit when future generation-stamp blocks imply metadata inconsistency.

## Important APIs, Types, and Functions
The package-private class has status enum `BMSafeModeStatus` with `PENDING_THRESHOLD`, `EXTENSION`, and `OFF`. Constructor configuration includes safe-mode block threshold, minimum live datanodes, safe replication minimum, reconstruction queue threshold, safe-mode extension, rollback detection, and monitor interval. Core methods are `activate(long)`, `isInSafeMode()`, `checkSafeMode()`, `adjustBlockTotals(int,int)`, `isSafeModeTrackingBlocks()`, `setBlockTotal(long)`, `getSafeModeTip()`, `leaveSafeMode(boolean)`, `incrementSafeBlockCount(int, BlockInfo)`, `decrementSafeBlockCount(BlockInfo)`, `checkBlocksWithFutureGS(BlockReportReplica)`, byte counters for future blocks, and `close()`.

## Control Flow
`activate(total)` records start time, computes block thresholds, and either exits immediately if thresholds are already met or enters `PENDING_THRESHOLD`. `checkSafeMode()` is the transition driver under the block-manager write lock. In `PENDING_THRESHOLD`, once block and datanode thresholds are met it either enters `EXTENSION` and starts `SafeModeMonitor`, or exits directly if no extension is needed. In `EXTENSION`, the monitor periodically takes the global write lock and calls `leaveSafeMode(false)` only after the extension has elapsed and thresholds still hold.

Safe block accounting happens on replica and block lifecycle events. `incrementSafeBlockCount()` increments only when a contiguous block reaches `safeReplication` or a striped block reaches its real data block count. `decrementSafeBlockCount()` decrements when a complete block falls below that safe count. `adjustBlockTotals()` supports HA standby edit tailing by adjusting both safe and total counts while in safe mode, then rechecking state.

`leaveSafeMode(force)` refuses to exit if bytes from future generation-stamp blocks were detected, unless forced. On exit it initializes reconstruction queues if necessary, logs topology and under-replicated counts, records safe-mode time metrics, starts secret manager work if needed, completes startup progress, and provisions snapshot trash roots.

## State and Persistence Behavior
Safe mode state is in-memory: status, block totals, safe counts, thresholds, reached/start timestamps, last report timestamp, startup progress counter, and future-generation byte counters. The class does not persist metadata itself. Its decisions protect persistent namespace consistency by blocking normal exit if block reports indicate generation stamps ahead of NameNode metadata. `LongAdder` counters distinguish replicated and EC future bytes; forced exit resets them.

## Dependencies and Integration Points
The class depends on `BlockManager` for active block counts, live datanode counts, reconstruction queue initialization, block lookup, replica counting, and generation-stamp checks. It depends on `Namesystem` for global and block-manager lock assertions plus running/transition state. It updates `NameNode` state-change logs, metrics, startup progress, secret manager startup, and snapshot trash provisioning. It uses configuration keys from `DFSConfigKeys` and startup options to treat rollback as a special case where future generation stamps are expected.

## Risks
Threshold math uses `(long)(total * threshold)`, so boundary behavior at fractional thresholds should be tested. Monitor exit takes the global write lock repeatedly; a stuck or slow lock holder can delay safe-mode exit. Future generation-stamp accounting intentionally blocks normal exit because forcing can delete data; tests and admin paths must be explicit about force semantics. In HA, `isSafeModeTrackingBlocks()` only tracks incremental block totals when HA is enabled and status is not off; incorrect lock usage or missed edit-tail adjustments can leave counters inconsistent.

## Test Signals
Tests should exercise zero-block startup, threshold crossing with and without extension, datanode threshold gating, reconstruction queue initialization threshold, safe count increment/decrement for contiguous and striped blocks, HA block total adjustment, rollback vs non-rollback future generation-stamp handling, forced vs normal safe-mode exit, monitor interruption on close, startup progress counter increments, and status-tip content for unmet thresholds and future-byte warnings.
