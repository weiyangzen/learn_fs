# subset-b-007482 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManager.java

## Purpose
`BlockManager` is the NameNode-side owner of HDFS block state. It maintains the global block-to-storage map, replica health maps, reconstruction and invalidation queues, block report processing, safe-mode accounting hooks, block tokens, storage policy integration, and block placement decisions for both replicated and striped erasure-coded blocks. Its class comment defines the durability invariant it tries to maintain: live replicas normally match expected redundancy, while maintenance mode relaxes the invariant to preserve a minimum live count and count maintenance replicas toward eventual redundancy.

## Important APIs, Types, and Functions
The constructor builds the `DatanodeManager`, `HeartbeatManager`, `BlockIdManager`, `BlocksMap`, `BlockPlacementPolicies`, `BlockStoragePolicySuite`, `PendingReconstructionBlocks`, `PendingRecoveryBlocks`, `BlockReportLeaseManager`, `BlockManagerSafeMode`, asynchronous block report processor, provided-storage map, SPS manager, and configuration-derived limits. `activate()` starts pending reconstruction, datanode services, the redundancy monitor, marked-delete scrubber, block report thread, JMX registration, and safe mode. `close()`, `shutdown()`, and `clear()` stop or reset these resources.

Public and package APIs span several surfaces: storage policy lookup, block token/key generation, placement target selection (`chooseTarget4NewBlock`, `chooseTarget4AdditionalDatanode`, `chooseTarget4WebHDFS`), block commit and completion (`commitOrCompleteLastBlock`, `forceCompleteBlock`, `convertLastBlockToUnderConstruction`), block locations (`createLocatedBlocks`, `getBlocksWithLocations`), datanode block reports (`processReport`, `processIncrementalBlockReport`, `requestBlockReportLeaseId`, `removeBRLeaseIfNeeded`), corrupt block handling (`findAndMarkBlockAsCorrupt`, `markBlockReplicasAsCorrupt`), safe mode delegation, queue introspection metrics, and test hooks.

Major internal types include `StatefulBlockInfo` for under-construction report handling, `BlockInfoToAdd` for deferred report diffs, `MisReplicationResult`, `RedundancyMonitor`, `MarkedDeleteBlockScrubber`, and `BlockReportProcessingThread`. Key collaborators are `BlocksMap`, `LowRedundancyBlocks`, `PendingReconstructionBlocks`, `PendingRecoveryBlocks`, `CorruptReplicasMap`, `InvalidateBlocks`, `ExcessRedundancyMap`, `PendingDataNodeMessages`, `ProvidedStorageMap`, and `BlockPlacementPolicy`.

## Control Flow
Startup initializes configuration and then `activate()` starts background services and enters `BlockManagerSafeMode`. During safe mode, first block reports are optimized through `processFirstBlockReport()` and `addStoredBlockImmediate()`: known valid finalized replicas are added, complete/committed blocks may be completed, and safe block counts are incremented without doing full low/extra redundancy queue work until reconstruction queues are populated.

Full block reports flow through `processReport(DatanodeID, DatanodeStorage, BlockListAsLongs, BlockReportContext)`. The method takes the global write lock, validates datanode registration and storage, resolves provided storage, discards duplicate non-initial startup reports, then either uses `processFirstBlockReport()` or computes a normal diff with `reportDiff()`. `reportDiff()` inserts a delimiter into the storage's block list, scans reported replicas through `processReportedBlock()`, moves reported blocks before the delimiter, and treats remaining blocks after the delimiter as missing from the datanode. It later applies queued additions, removals, invalidations, corrupt markings, and under-construction updates.

Incremental reports flow through `processIncrementalBlockReport()`. Deleted blocks remove the storage mapping; received blocks call `addBlock()`, decrement scheduled counts, reduce pending reconstruction if the generation stamp matches, and process the finalized report; receiving blocks are handled as RBW. The common `processAndHandleReportedBlock()` path builds at most one action from add, invalidate, corrupt, or under-construction handling and then applies it.

Replica validation is centralized in `checkReplicaCorrupt()`. It compares reported replica state with stored block UC state, generation stamp, and length. For striped blocks it converts internal block IDs and verifies internal block length via `StripedBlockUtil.getInternalBlockLength`. Standby/failover cases can queue future-generation or temporarily inconsistent reports in `PendingDataNodeMessages` instead of marking them corrupt.

Reconstruction is driven by `RedundancyMonitor.run()`, which calls `computeDatanodeWork()` when queues should be populated. That schedules reconstruction via `computeBlockReconstructionWork()`, requeues timed-out pending items, rescans postponed misreplicated blocks, and processes timed-out excess blocks. Reconstruction scheduling has three phases: choose low-redundancy candidates under lock, release the global lock to choose placement targets, then reacquire the block-manager lock to validate and enqueue datanode work. `scheduleReconstruction()` chooses source datanodes, handles replicated vs EC work, rejects unavailable EC source sets, and returns `ReplicationWork` or `ErasureCodingWork`. `validateReconstructionWork()` rechecks state, placement improvement, effective live plus pending redundancy, adds work to source datanodes, increments scheduled target counts, and moves the block into `pendingReconstruction`.

Extra redundancy handling checks live replica counts and duplicated EC internal blocks. `processExtraRedundancyBlockWithoutPostpone()` builds non-excess normal storages while postponing stale storages. Contiguous block excess deletion delegates to the placement policy and storage policy excess type selection. Striped block excess deletion identifies duplicated internal indices and asks the EC placement policy which duplicate storages to remove. Chosen excess replicas are recorded in `ExcessRedundancyMap` and `InvalidateBlocks`.

Block completion and reopening update both namespace and block queues. `commitOrCompleteLastBlock()` commits the client-reported last block, counts usable replicas including decommissioning and entering-maintenance nodes, completes if minimum storage is met, and force-completes after recovery if needed. `convertLastBlockToUnderConstruction()` removes the block from reconstruction/pending deletion queues and decrements safe-mode totals because under-construction blocks do not count as safe complete blocks.

## State and Persistence Behavior
This class is mostly in-memory coordination around persisted NameNode namespace edits and datanode reports. `BlocksMap` holds the authoritative in-memory relation from block IDs to block collections and storage locations. `BlockCollection` and `FSDirectory` update persistent namespace-facing state when blocks complete or are removed; block ID and generation stamp state is advanced through `BlockIdManager`.

Queue state is transient and rebuilt or reconciled from persisted namespace plus datanode reports: `neededReconstruction`, `pendingReconstruction`, `invalidateBlocks`, `excessRedundancyMap`, `postponedMisreplicatedBlocks`, `pendingDNMessages`, and `markedDeleteQueue`. Safe-mode counters are delegated to `BlockManagerSafeMode` and adjusted on block completion, deletion, and replica arrival/removal. Block report leases track report protocol progress rather than durable metadata. Background scrubber and redundancy monitor mutate transient queues under NameSystem locks.

Block token state is maintained through `BlockTokenSecretManager`; it may be null when block access tokens are disabled. Provided storage state is integrated through `ProvidedStorageMap`, which can map provided storage reports onto a selected datanode. SPS state is delegated to `StoragePolicySatisfyManager` when enabled. JMX state is registered as the `BlockStatsMXBean`.

## Dependencies and Integration Points
`BlockManager` is tightly coupled to `Namesystem` locking, `FSDirectory`, `INodeFile`/`BlockCollection`, `NameNodeMetrics`, `StartupProgress`, `CacheManager`, HA context, datanode registration and heartbeat state, and the datanode protocol objects used for full/incremental block reports. Placement and storage policy decisions route through `BlockPlacementPolicies`, `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `NetworkTopology`, and storage type metadata. EC behavior depends on `BlockInfoStriped`, `ErasureCodingPolicy`, internal block indices, and `ErasureCodingWork`.

External protocol surfaces include `LocatedBlocks`/`LocatedBlock` construction for clients, `BlockCommand` invalidations and reconstruction tasks returned on heartbeats via datanode queues, exported block keys and data encryption keys, and block report leases. HA standby integration is explicit: future or inconsistent datanode reports can be postponed until edits arrive, then replayed by `processQueuedMessagesForBlock()` or drained by `processAllPendingDNMessages()` after becoming active.

## Risks
Correctness depends heavily on lock discipline. Several comments note TODOs where write locks are used because data structures are not clearly safe under read locks. Target selection deliberately releases the global lock and then revalidates; bugs in the revalidation path can schedule stale or duplicate work. Full block report diffing relies on temporary delimiter insertion and block-list ordering, so storage list mutation bugs can remove valid replicas or miss deletions.

The maintenance, decommission, stale-storage, corrupt, excess, and EC duplicate-index cases interact in subtle ways. Counting an EC block group's live redundancy must deduplicate internal block indices; a mistake can report a block group as safe while one internal block is missing. Standby postponement of future generation stamps prevents false corruption but can accumulate pending datanode messages or replay them out of the intended sequence if the queue protocol changes.

There is a likely configuration setter bug in `setExcessRedundancyTimeoutCheckLimit(long limit)`: it tests the field `excessRedundancyTimeoutCheckLimit <= 0` instead of the `limit` parameter, so the first call will normally take the default branch regardless of the passed positive limit. Operationally, block report queue saturation, long global write-lock holds, and large marked-delete batches are scalability-sensitive. Immediate corrupt replica deletion is guarded by stale-storage checks unless configured otherwise, because deleting when another replica only appears available on stale storage risks data loss.

## Test Signals
Tests should cover first and subsequent full block reports, incremental received/deleted/receiving reports, corrupt state matrix cases, standby postponed reports and replay ordering, block report lease request/removal behavior, safe-mode block count adjustments, completion/reopen transitions, and reconstruction queue initialization. Reconstruction tests need replicated and striped blocks, busy source nodes, pending reconstruction timeouts, decommission/maintenance nodes, placement-policy-only insufficiency, and stale storage postponement. Excess redundancy tests should include rack-aware contiguous deletion, EC duplicate internal indices, storage type excess selection, timeout re-invalidation, and provided storage. Concurrency and scale tests should exercise block report batching, max write-lock hold behavior, marked-delete scrubber lock release, and JMX/metric counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerFaultInjector.java

## Purpose
`BlockManagerFaultInjector` is a test-only seam for injecting faults around block manager operations. Production behavior is intentionally inert: the singleton instance methods are no-ops unless tests replace `instance` with a subclass or mock.

## Important APIs, Types, and Functions
The class exposes a visible-for-testing static `instance`, `getInstance()`, and four visible-for-testing hook methods: `incomingBlockReportRpc(DatanodeID, BlockReportContext)`, `requestBlockReportLease(DatanodeDescriptor, long)`, `removeBlockReportLease(DatanodeDescriptor, long)`, and `mockAnException()`. `incomingBlockReportRpc` can throw `IOException`; the others are void no-ops by default.

## Control Flow
Callers obtain the singleton with `BlockManagerFaultInjector.getInstance()` and invoke hooks at specific protocol points. In `BlockManager`, lease hooks are called after requesting and removing block report leases, and `mockAnException()` is invoked in heartbeat update paths. The hook object can be swapped by tests to force exceptions, delays, or observations without changing production code paths.

## State and Persistence Behavior
The only state is the mutable static singleton. There is no persistence and no synchronization around replacement. Default methods do not mutate state.

## Dependencies and Integration Points
The injector depends on HDFS block-management datanode descriptors plus protocol identifiers `DatanodeID` and `BlockReportContext`. Its integration points are narrow but important because they sit near block report lease management, incoming block report RPC processing, and heartbeat update code.

## Risks
Because `instance` is public static and mutable for tests, tests must restore it to avoid cross-test contamination. The class has no concurrency protection, so simultaneous tests in the same JVM can interfere. Production callers should not rely on side effects from the default implementation.

## Test Signals
Useful tests replace `instance` with a custom injector that throws from `incomingBlockReportRpc` or `mockAnException()`, records lease IDs from request/remove hooks, and verifies block manager behavior under injected report or heartbeat failures. Test cleanup should reset `instance` to a new default injector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerSafeMode.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicies.java

## Purpose
`BlockPlacementPolicies` is a small holder that creates and routes between the configured placement policy for replicated contiguous blocks and the configured placement policy for striped erasure-coded block groups.

## Important APIs, Types, and Functions
The constructor reads `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` and `DFS_BLOCK_PLACEMENT_EC_CLASSNAME_KEY`, instantiates both classes with `ReflectionUtils.newInstance`, and initializes each policy with `Configuration`, `FSClusterStats`, `NetworkTopology`, and `Host2NodesMap`. `getPolicy(BlockType)` returns the replicated policy for `CONTIGUOUS`, the EC policy for `STRIPED`, and throws `IllegalArgumentException` for unsupported block types.

## Control Flow
Construction eagerly creates and initializes both policy instances. Runtime selection is a switch on `BlockType`. `BlockManager` calls this holder for new block placement, reconstruction target selection, placement verification, replica deletion choices, slow-node exclusion toggles, and min-blocks-for-write settings.

## State and Persistence Behavior
The class stores two final policy instances. It has no persistence. Refresh behavior is handled by `BlockManager.refreshBlockPlacementPolicy()`, which replaces the entire holder with a newly constructed one.

## Dependencies and Integration Points
Dependencies are Hadoop configuration, `DFSConfigKeys`, `BlockType`, `NetworkTopology`, `FSClusterStats`, `Host2NodesMap`, `ReflectionUtils`, and the `BlockPlacementPolicy` base type. It is the bridge between block management logic and configurable rack/storage/EC placement implementations.

## Risks
Misconfigured policy class names fail at construction or initialization time. Both policies must implement all methods expected by `BlockManager`, including target choice, placement verification, replica deletion, slow-node exclusion, and minimum write targets. Adding a new `BlockType` requires updating this switch or callers will receive an `IllegalArgumentException`.

## Test Signals
Tests should verify default policy instantiation, custom replicated and EC policy class loading, initialization arguments, routing by `CONTIGUOUS` and `STRIPED`, replacement through `BlockManager.refreshBlockPlacementPolicy()`, and unsupported block type failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicies.java -->
