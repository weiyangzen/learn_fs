# subset-b-007485 research

Grouped source research for HDFS block-management helpers, provided storage, slow-node telemetry, server storage metadata, WebHDFS request identity, and common server exceptions/interfaces. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java

## Purpose

`LocatedBlockBuilder` is a small NameNode-side builder for `LocatedBlocks` responses. It accumulates file length, under-construction state, located block entries, the last block, encryption metadata, and erasure-coding policy before producing the protocol object returned to HDFS clients.

## Important APIs and types

The builder exposes fluent package-private setters `fileLength`, `addBlock`, `lastUC`, `lastBlock`, `lastComplete`, `encryption`, and `erasureCoding`. `isBlockMax` enforces a caller-provided maximum block count. `newLocatedBlock` delegates to `BlockManager.newLocatedBlock` so callers can still set block tokens on the returned object. `build(DatanodeDescriptor)` exists as an overridable hook and normally delegates to `build()`.

## Control flow

Callers create the builder with a max block limit, add `LocatedBlock` instances as block metadata is scanned, optionally attach last-block and security metadata, then call `build`. The internal block list starts as `Collections.emptyList()` and switches to an `ArrayList` on the first `addBlock`.

## State and persistence behavior

All state is transient request state. There is no persistence, synchronization, or defensive copying beyond constructing the final `LocatedBlocks` object with the accumulated list reference.

## Dependencies and integration points

It integrates `BlockManager`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `LocatedBlock`, `LocatedBlocks`, `ExtendedBlock`, `FileEncryptionInfo`, and `ErasureCodingPolicy`. `ProvidedStorageMap.ProvidedBlocksBuilder` subclasses it to rewrite provided-storage locations.

## Risks and edge cases

The builder is mutable and package-private; it assumes single-threaded request construction. The `maxBlocks` limit is advisory because `addBlock` itself does not reject overflow. Subclasses must preserve `LocatedBlocks` semantics when overriding location construction or client-aware build hooks.

## Test signals

Useful signals include max-block boundary behavior, empty file construction, last-block and under-construction combinations, encryption/EC metadata propagation, and subclass behavior for provided storage location expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java

## Purpose

`LowRedundancyBlocks` maintains prioritized in-memory queues of blocks or striped block groups that need reconstruction. It is the BlockManager's scheduling input for deciding which endangered data should be reconstructed first.

## Important APIs and types

The class owns five `LightWeightLinkedSet<BlockInfo>` queues: highest priority, very low redundancy, low redundancy, badly distributed, and corrupt. Public package APIs include `add`, `remove`, `update`, `contains`, `chooseLowRedundancyBlocks`, queue iterators, and metric getters for low-redundancy, corrupt, EC, badly distributed, and highest-priority counts. Counters are maintained with `LongAdder`.

## Control flow

`getPriority` chooses a queue from live, read-only, out-of-service, and expected replica counts. Contiguous blocks with one live copy or only read-only/out-of-service copies are highest priority; zero usable copies are corrupt. Striped blocks compare live internal blocks against data and parity unit counts. `update` removes the block using its old computed priority, searches other queues if needed, and re-adds at the current priority. `chooseLowRedundancyBlocks` walks queues in priority order using bookmarks, skips corrupt blocks for reconstruction output, removes deleted blocks, and resets bookmarks at the end or on request.

## State and persistence behavior

All state is in-memory and synchronized on the instance. Queue membership and counters must change together; there is no fsimage persistence because block health is recomputed from block maps and reports.

## Dependencies and integration points

It depends on `BlockInfo`, `BlockInfoStriped`, `LightWeightLinkedSet`, and NameNode/BlockManager logging and metrics. BlockManager uses it during redundancy monitor scans, block report handling, placement checks, and reconstruction scheduling.

## Risks and edge cases

Counter consistency depends on every queue mutation flowing through increment/decrement helpers. Priority calculations differ for contiguous and striped blocks, making read-only, maintenance, decommissioned, and corrupted states easy to misclassify. The corrupt queue is still scanned to purge deleted blocks but not returned for reconstruction. Bookmark iteration can delay recently skipped blocks until reset.

## Test signals

Tests should cover each priority threshold, EC data/parity boundaries, update moves between queues, delete cleanup during `chooseLowRedundancyBlocks`, replication-one corrupt counters, badly distributed counters, and iterator reset fairness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java

## Purpose

`NumberReplicas` is a typed counter container for the replica-state counts BlockManager computes for a block or block group. It centralizes the meaning of live, stale, corrupt, excess, maintenance, decommissioned, and EC-redundant replica counts.

## Important APIs and types

It extends `EnumCounters<StoredReplicaState>`. `StoredReplicaState` includes `LIVE`, `READONLY`, `DECOMMISSIONING`, `DECOMMISSIONED`, `MAINTENANCE_NOT_FOR_READ`, `MAINTENANCE_FOR_READ`, `CORRUPT`, `EXCESS`, `STALESTORAGE`, and striped-only `REDUNDANT`. Accessors expose individual counts and derived totals such as `decommissionedAndDecommissioning`, `maintenanceReplicas`, `outOfServiceReplicas`, and `liveEnteringMaintenanceReplicas`.

## Control flow

There is no complex algorithm in this class. Callers increment enum counters while inspecting storages, then use the named accessors to feed placement, redundancy, maintenance, and reconstruction decisions.

## State and persistence behavior

The state is an in-memory enum-indexed counter array inherited from `EnumCounters`. The class comment calls it immutable, but the inherited counter operations mutate it; callers should treat instances as local computation snapshots rather than persisted state.

## Dependencies and integration points

It integrates with BlockManager replica counting, low-redundancy priority decisions, replication work, decommission/maintenance handling, stale-node logic, excess-replica tracking, and EC internal-block accounting.

## Risks and edge cases

Some counts are intentionally not mutually exclusive: stale replicas may also be live. Maintenance has read-serving and not-for-read subcategories, and out-of-service folds maintenance together with decommissioned/decommissioning. For striped blocks, live excludes redundant internal block replicas, so callers must use `redundantInternalBlocks` separately.

## Test signals

Useful tests exercise accessor derivations after counter increments, stale/live overlap, maintenance read/not-read split, out-of-service totals, and striped redundant counts feeding EC redundancy decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/NumberReplicas.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java

## Purpose

`OutOfLegacyGenerationStampsException` is the specific failure raised when the NameNode exhausts the reserved V1 legacy generation-stamp range.

## Important APIs and types

The class extends `IOException`, has a stable `serialVersionUID`, and exposes a no-argument constructor with the fixed message `Out of V1 (legacy) generation stamps`.

## Control flow

There is no internal control flow. The exception is thrown by generation-stamp allocation code when legacy block compatibility space is unavailable.

## State and persistence behavior

The class has no mutable state beyond inherited exception message/cause fields. It is not persisted directly, but the condition reflects exhaustion of namespace-wide generation-stamp state.

## Dependencies and integration points

It is part of the blockmanagement package and integrates with BlockIdManager/generation-stamp allocation paths that distinguish legacy and current generation-stamp spaces.

## Risks and edge cases

The fixed message gives little context about the current counter value or namespace state. Callers should catch it only where a meaningful upgrade or allocation failure response can be produced.

## Test signals

Allocation tests should force the legacy generation-stamp cursor to the reserved limit and assert this exact exception type is raised without advancing into non-legacy space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java

## Purpose

`PendingDataNodeMessages` queues block reports or incremental block messages that a standby NameNode receives before namespace state is ready to process them. It prevents early or future-state DataNode messages from being lost during HA standby processing.

## Important APIs and types

The main state is `Map<Block, Queue<ReportedBlockInfo>> queueByBlockId` plus a total `count`. `ReportedBlockInfo` stores the copied `Block`, `DatanodeStorageInfo`, and reported `ReplicaState`. APIs include `enqueueReportedBlock`, `removeQueuedBlock`, `removeAllMessagesForDatanode`, `takeBlockQueue`, `takeAll`, `count`, and `toString`.

## Control flow

Enqueue normalizes striped internal block IDs to their block-group ID key while preserving the reported block in the queued record. Removal by queued block similarly normalizes striped IDs, removes all reports from the same storage, and drops empty queues; this is explicitly to avoid an older non-future report being processed after failover. `takeBlockQueue` and `takeAll` transfer ownership to callers and decrement or reset `count`.

## State and persistence behavior

State is in-memory standby-only buffering. There is no synchronization in this class, so callers must provide the surrounding NameNode locking or single-threading discipline.

## Dependencies and integration points

It depends on `Block`, `BlockIdManager`, `DatanodeDescriptor`, `DatanodeStorageInfo`, and `HdfsServerConstants.ReplicaState`. It integrates with standby block report and failover processing.

## Risks and edge cases

The `count` field must stay aligned with queue mutations; bugs can skew metrics and capacity sizing. `removeAllMessagesForDatanode` replaces queue values while iterating map entries but does not remove now-empty block keys. Block key normalization for striped blocks is essential; missing it would split messages for a single block group.

## Test signals

Tests should cover contiguous and striped enqueue/take, same-storage replacement/removal, DataNode-wide removal, count correctness, empty queue cleanup, and failover replay order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java

## Purpose

`PendingReconstructionBlocks` tracks block reconstruction commands that have been issued but not yet satisfied. It lets BlockManager avoid overscheduling the same block and detect reconstruction attempts that timed out.

## Important APIs and types

The class owns `pendingReconstructions`, `timedOutItems`, a monitor `Daemon`, timeout configuration, and `timedOutCount`. APIs include `start`, `stop`, `increment`, `decrement`, `remove`, `clear`, `size`, `getNumReplicas`, `getTimedOutBlocks`, `getNumTimedOuts`, `metaSave`, and `getTargets`. `PendingBlockInfo` stores timestamp and target storages.

## Control flow

`increment` inserts or refreshes a block entry and adds unique target storages. `decrement` removes target entries matching a DataNode descriptor and deletes the block when no targets remain. The monitor sleeps for the smaller of the timeout and five minutes, scans pending entries under lock, moves expired blocks to `timedOutItems`, increments NameNode timeout metrics, and removes them from pending. `getTimedOutBlocks` drains the timeout list and advances the cumulative count.

## State and persistence behavior

All state is in-memory and protected by explicit synchronization on the maps/lists. It is rebuilt from runtime scheduling, not persisted. The monitor lifecycle is controlled by `start` and `stop`.

## Dependencies and integration points

It integrates with `BlockManager`, `DatanodeStorageInfo`, NameNode metrics, metasave diagnostics, and the redundancy monitor.

## Risks and edge cases

Timeouts are coarse-grained, so retry timing can lag. `decrementReplicas` compares DataNode descriptor identity rather than storage identity. `metaSave` formats monotonic timestamps with `java.sql.Time`, which is diagnostic only. Interrupted monitor shutdown ignores interruption after join.

## Test signals

Tests should cover unique target accumulation, decrement-to-zero removal, timeout scanning, `getTimedOutBlocks` drain semantics, `getNumTimedOuts`, monitor start/stop, and metasave output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java

## Purpose

`PendingRecoveryBlocks` rate-limits lease/block recovery attempts. It ensures only one recovery attempt for a block is active until its timeout expires.

## Important APIs and types

The class stores `BlockRecoveryAttempt` entries in a `LightWeightHashSet`. Main APIs are `add`, `remove`, `isUnderRecovery`, `setRecoveryTimeoutInterval`, and test-overridable `getTime`. `BlockRecoveryAttempt` equality and hashing are based only on `BlockInfo`, while `timeoutAt` is mutable.

## Control flow

`add` checks for an existing attempt. If none exists, it inserts one with `now + recoveryTimeoutInterval`. If an existing attempt has timed out, it refreshes the timeout and returns true. If not timed out, it logs the remaining time and rejects the new recovery. `remove` clears an attempt after recovery finishes or is abandoned.

## State and persistence behavior

State is in-memory and all public mutations are synchronized. There is no persistence; recovery-in-progress state is reconstructed from runtime lease/block recovery flows after restart.

## Dependencies and integration points

It depends on `BlockInfo`, `LightWeightHashSet`, monotonic time, and BlockManager logging. It integrates with NameNode block recovery scheduling and lease recovery.

## Risks and edge cases

Timeout comparison uses `currentTime > timeoutAt`, so equality is still considered active. If callers forget `remove`, entries remain until a later retry after timeout. Mutating `timeoutAt` inside a hash-set element is safe only because hash/equality ignore that field.

## Test signals

Useful tests cover first add, duplicate before timeout, retry after timeout, remove-and-readd, `isUnderRecovery`, custom timeout interval, and monotonic time boundary equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java

## Purpose

`ProvidedStorageMap` multiplexes normal DataNode storage with HDFS `PROVIDED` storage, where block bytes live in an external storage system and DataNodes expose access to the same logical provided volume.

## Important APIs and types

The class reads provided-storage configuration, constructs a singleton provided `DatanodeStorageInfo`, loads a `BlockAliasMap`, and exposes `getStorage`, `updateStorage`, `removeDatanode`, `getCapacity`, `chooseProvidedDatanode`, `getAliasMap`, and `newLocatedBlocks`. Nested types include `ProvidedBlocksBuilder`, `ProvidedDescriptor`, `ProvidedDatanodeStorageInfo`, and `ProvidedBlockList`.

## Control flow

When disabled, the map returns normal builders and leaves provided fields null. When enabled, matching storage IDs of type `PROVIDED` are injected into reporting DataNodes and the first provided block report is synthesized from the alias map under the global write lock. `ProvidedBlocksBuilder` rewrites located-block responses: local replicas are preserved, provided replicas are expanded to one or more active provided DataNodes up to the default replication factor, excluding nodes that already host local replicas. `ProvidedDescriptor` tracks active provided DataNodes and randomly chooses live nodes first; replication commands are delegated to a chosen real DataNode.

## State and persistence behavior

The logical provided storage is in-memory NameNode state backed by the configured `BlockAliasMap` for block aliases. Active DataNodes are tracked in a concurrent map plus a selection list. If no active provided DataNodes remain, the provided block report count is reset and storage may transition to failed.

## Dependencies and integration points

It integrates `BlockManager`, `RwLock`, `BlockAliasMap`, `TextFileRegionAliasMap`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `LocatedBlocks`, `BlockListAsLongs`, and `StorageType.PROVIDED`.

## Risks and edge cases

The design assumes a single provider storage ID. `ProvidedDescriptor.getProvidedStorage` appends to the random-choice list on each report, so duplicate DataNode entries must be controlled by caller/report behavior. Choosing provided locations is random and not topology-aware. `ProvidedBlockList` does not support legacy long-array or protobuf buffer access. Correct lock mode is asserted for report processing and removal.

## Test signals

Tests should cover disabled behavior, provided storage injection, first alias-map block report, active DataNode removal/failure state, location expansion with excluded UUIDs, replication delegation, duplicate reporting behavior, and unsupported `ProvidedBlockList` methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java

## Purpose

`ReplicaUnderConstruction` records per-replica state for a block or block-group replica while a file is being written or recovered.

## Important APIs and types

It extends `Block` and adds an expected `DatanodeStorageInfo`, a mutable `HdfsServerConstants.ReplicaState`, and a `chosenAsPrimary` recovery flag. APIs expose expected storage location, state getter/setter, primary-selection getter/setter, `isAlive`, equality/hash inherited from `Block`, and a compact `ReplicaUC[...]` string.

## Control flow

The object is constructed from an existing block, assigned target storage, and reported replica state. Recovery code can mark a replica as chosen primary, update its state as reports arrive, and test whether the expected DataNode is alive.

## State and persistence behavior

State is mutable in memory and tied to block-under-construction metadata. The generation stamp and length inherited from `Block` are the DataNode-reported values. Persistence is indirect through namespace/block-under-construction serialization elsewhere.

## Dependencies and integration points

It integrates with `BlockUnderConstructionFeature`, lease recovery, pipeline construction, DataNode liveness checks, and the `HdfsServerConstants.ReplicaState` state machine.

## Risks and edge cases

The expected storage location is not proof the DataNode actually has the replica. Equality ignores expected location and state because it follows `Block` equality, so collections keyed by this object treat same block IDs as equal. `isAlive` assumes the expected location is non-null.

## Test signals

Tests should cover state mutation, primary selection, liveness pass-through, string rendering, equality semantics for same block/different storage, and recovery flows with stale or missing reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java

## Purpose

`ReplicationWork` is the concrete `BlockReconstructionWork` for normal replicated-block reconstruction. It chooses target storages and enqueues replication work on a single source DataNode.

## Important APIs and types

The constructor takes a `BlockInfo`, owning `BlockCollection`, selected source node array, containing nodes, live replica storages, additional replica count, and priority. It overrides `chooseTargets` and `addTaskToDatanode`.

## Control flow

Construction asserts exactly one source node and increments that node's pending-replication-without-targets counter. `chooseTargets` calls the configured `BlockPlacementPolicy.chooseTarget` unless the block has been deleted, then stores the chosen targets and always decrements the pending counter in a `finally` block. `addTaskToDatanode` calls `addBlockToBeReplicated` on the source node.

## State and persistence behavior

The object is transient scheduling state. It mutates the source DataNode's pending counters and task queues, but it is not itself persisted.

## Dependencies and integration points

It integrates `BlockReconstructionWork`, `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `DatanodeDescriptor`, `DatanodeStorageInfo`, and `NumberReplicas`. It is used by BlockManager reconstruction scheduling for replicated blocks, distinct from erasure-coding work.

## Risks and edge cases

The single-source assertion is central; callers must not pass multiple source nodes. Deleted blocks skip placement to avoid sending invalid `NO_ACK`-sized work. Placement can return null/empty targets, but the task enqueue method still returns true and delegates to source-node handling.

## Test signals

Tests should verify source counter increment/decrement on success and exception, target choice arguments, deleted-block skip behavior, source task enqueue, and assertion/validation of single-source construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java

## Purpose

`SequentialBlockGroupIdGenerator` allocates negative erasure-coded block-group IDs while preserving the low bits reserved for internal block indexes within a group.

## Important APIs and types

It extends `SequentialNumber`, starts at `Long.MIN_VALUE`, and exposes `nextValue`. It uses `BLOCK_GROUP_INDEX_MASK` and `MAX_BLOCKS_IN_GROUP` from `HdfsServerConstants` and checks conflicts through `BlockManager.getStoredBlock`.

## Control flow

`nextValue` advances to the next aligned group boundary by clearing index bits and adding `MAX_BLOCKS_IN_GROUP`. It then probes every possible internal block ID in that group range. If any ID already exists in the block map, it skips the whole group range and retries. If allocation reaches non-negative IDs, it throws to avoid colliding with contiguous blocks.

## State and persistence behavior

The current sequential value is in-memory runtime state inherited from `SequentialNumber` and is initialized/restored by BlockIdManager/namespace loading elsewhere. The method requires an external lock to prevent concurrent ID conflicts.

## Dependencies and integration points

It integrates with BlockManager's block map, EC block ID encoding, and namespace/block ID initialization.

## Risks and edge cases

The collision scan must cover every internal index in the group; otherwise a random legacy block ID could collide with an EC internal block. External locking is required but not enforced in this class. Exhausting negative IDs is fatal.

## Test signals

Tests should cover group-boundary alignment, conflict skipping for each internal index, non-negative exhaustion failure, and concurrent allocation guarded by BlockIdManager locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java

## Purpose

`SequentialBlockIdGenerator` allocates positive contiguous block IDs, starting after the historical reserved range, while skipping conflicts with previously random block IDs.

## Important APIs and types

It extends `SequentialNumber`, defines `LAST_RESERVED_BLOCK_ID` as `2^30`, and exposes `nextValue`. Conflict checking uses `BlockManager.getStoredBlock` and ignores block-map entries whose block collection ID is `INodeId.INVALID_INODE_ID`.

## Control flow

`nextValue` obtains the next sequential number, wraps it in a `Block`, and loops while `isValidBlock` reports a real stored block conflict. It throws if the value wraps negative because negative ID space is reserved for erasure-coded block groups.

## State and persistence behavior

The current counter is runtime namespace state managed externally by BlockIdManager. The generator itself does not persist IDs and relies on external synchronization for uniqueness.

## Dependencies and integration points

It integrates with BlockManager, the block map, INode ID validity, and NameNode block allocation.

## Risks and edge cases

Only valid file-owned block map entries block allocation; invalid collection IDs are skipped. Exhaustion into negative space is fatal. Historical random-ID conflicts should be rare but must be tested because skipping must not allocate an existing block.

## Test signals

Tests should verify initial value, conflict skipping, invalid-inode conflict bypass, negative wrap failure, and lock-protected uniqueness under concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java

## Purpose

`SlowDiskTracker` aggregates slow-disk outlier reports received from DataNode heartbeats and publishes a bounded JSON report of the disks with highest observed latency.

## Important APIs and types

The tracker stores `diskIDLatencyMap` keyed by `datanodeId:disk`, a volatile `slowDisksReport`, report interval/validity settings, and an async-update guard. `DiskLatency` is the Jackson-serializable DTO with `SlowDiskID`, per-operation latency map, timestamp, `getMaxLatency`, and per-op lookup. APIs include `addSlowDiskReport`, `checkAndUpdateReportIfNecessary`, `updateSlowDiskReportAsync`, and `getSlowDiskReportAsJsonString`.

## Control flow

DataNode reports are copied into `DiskLatency` entries with the current monotonic timestamp. On interval expiry, an update thread computes top-N valid disks using a min-priority queue ordered by maximum latency, stores stale entries for cleanup, publishes the volatile report list, removes old reports by identity, and clears the update-in-progress flag.

## State and persistence behavior

State is in-memory and concurrent. Reports expire after three outlier intervals by default. JSON output is derived from the last async report snapshot and returns null when empty or serialization fails.

## Dependencies and integration points

It depends on `SlowDiskReports`, `DiskOp`, `DFSConfigKeys`, `Timer`, Jackson, Guava helpers, `SubjectInheritingThread`, and NameNode/DataNode heartbeat monitoring.

## Risks and edge cases

Async update failures could leave `isUpdateInProgress` true because the runnable has no `finally`. The output ordering is priority-queue iteration order, not sorted descending. Stale cleanup only happens during update. `new ArrayList(ImmutableList.of())` uses a raw type.

## Test signals

Tests should cover report ID construction, top-N selection, stale expiration and cleanup, JSON serialization, update interval gating, concurrent update suppression, and latency-per-operation fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java

## Purpose

`SlowPeerDisabledTracker` is the no-op implementation used when DataNode peer statistics are disabled.

## Important APIs and types

It subclasses `SlowPeerTracker` and overrides `isSlowPeerTrackerEnabled`, `addReport`, `getReportsForNode`, `getReportsForAllDataNodes`, `getJson`, and `getSlowNodes`. It returns immutable empty collections or null JSON and logs trace messages pointing to `dfs.datanode.peer.stats.enabled`.

## Control flow

Construction still calls the superclass constructor, but all public behavior short-circuits. Add and retrieval methods do not mutate or expose superclass report state.

## State and persistence behavior

No slow-peer state is recorded by this disabled variant. Any superclass state initialized by construction remains unused.

## Dependencies and integration points

It integrates with configuration selection of slow peer tracking and preserves the `SlowPeerTracker` API contract for callers that do not want to branch on enablement.

## Risks and edge cases

Because it extends the real tracker, constructor-side configuration or future superclass behavior still runs. `getJson` returns null rather than an empty JSON array, so consumers must already tolerate null from the enabled tracker on serialization failure.

## Test signals

Tests should verify disabled flag, no mutation after `addReport`, empty retrievals, null JSON, empty slow-node list, and caller behavior when switching between enabled and disabled trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java

## Purpose

`SlowPeerJsonReport` is a Jackson DTO that groups all valid reports against one slow DataNode for JSON exposure.

## Important APIs and types

The immutable fields are `SlowNode` and `SlowPeerLatencyWithReportingNodes`, both annotated with `@JsonProperty`. Getters expose the slow node ID and sorted reporting-node latency set. Equality and hashing use Apache Commons builders over both fields.

## Control flow

There is no algorithm beyond construction and object comparison. `SlowPeerTracker` creates instances after filtering stale reports and top-N selecting nodes.

## State and persistence behavior

Instances are immutable and transient. Their only persistence-like behavior is JSON serialization for diagnostics or JMX/HTTP consumers.

## Dependencies and integration points

It depends on Jackson annotations, `SortedSet`, `SlowPeerLatencyWithReportingNode`, and `SlowPeerTracker`.

## Risks and edge cases

Equality depends on the sorted set contents. If the set comparator is inconsistent with equality, set membership and object equality can diverge. The class is package-private and final, so schema changes must be coordinated with tracker JSON consumers.

## Test signals

Tests should cover JSON field names, equality/hash behavior, empty reporting sets, and stable ordering inherited from `SlowPeerLatencyWithReportingNode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java

## Purpose

`SlowPeerLatencyWithReportingNode` records one reporting DataNode's latency evidence against a slow peer.

## Important APIs and types

The immutable Jackson fields are `ReportingNode`, `ReportedLatency`, `MedianLatency`, `MadLatency`, and `UpperLimitLatency`. The class implements `Comparable` by reporting-node string and overrides equality/hash over all fields.

## Control flow

`SlowPeerTracker` creates one instance for each valid non-stale report. Sorted sets use `compareTo` to order reports by reporting node.

## State and persistence behavior

Instances are immutable diagnostic snapshots. They are serialized as part of `SlowPeerJsonReport` and are not otherwise persisted.

## Dependencies and integration points

It depends on Jackson and Apache Commons equality builders. It bridges `OutlierMetrics` values from DataNode reports into the slow-peer JSON schema.

## Risks and edge cases

`compareTo` compares only reporting node while `equals` also compares latency values. In `TreeSet`, two reports from the same reporting node compare equal even if latency fields differ; this matches the one-report-per-reporter model but is important if data is constructed manually.

## Test signals

Tests should cover JSON field names, ordering by reporting node, equality/hash with changed latency fields, and TreeSet replacement/deduplication semantics for same reporting node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java

## Purpose

`SlowPeerTracker` aggregates DataNode peer-latency outlier reports and exposes current slow-peer evidence as sets, JSON, and a top slow-node list.

## Important APIs and types

The main state is `ConcurrentMap<slowNode, ConcurrentMap<reportingNode, LatencyWithLastReportTime>>`. APIs include `isSlowPeerTrackerEnabled`, `addReport`, `getReportsForNode`, `getReportsForAllDataNodes`, `getJson`, `getSlowNodes`, `setMaxSlowPeersToReport`, and test accessor `getReportValidityMs`. `LatencyWithLastReportTime` stores monotonic timestamp and `OutlierMetrics`.

## Control flow

`addReport` creates the nested map if needed and replaces a reporter's previous metrics. Reads filter each nested map by `now - reportTime < reportValidityMs`, converting live entries to `SlowPeerLatencyWithReportingNode`. JSON/top-node generation uses a min-priority queue ordered by number of valid reporters and keeps the top configured count.

## State and persistence behavior

State is in-memory and concurrent. Stale reports are filtered out but not proactively evicted, so old reporter entries can remain indefinitely. JSON serialization returns null only on Jackson failure; empty state returns `[]`.

## Dependencies and integration points

It integrates with `SlowPeerReports`, `OutlierMetrics`, `DFSConfigKeys`, `Timer`, Jackson, Guava primitives/immutable maps, DataNode heartbeat reports, and NameNode/DataNode diagnostics.

## Risks and edge cases

Top-N ordering is by number of reports, not latency magnitude. Ties are priority-queue dependent. Stale reports can accumulate. If `maxNodesToReport` is zero, no nodes are reported. Logging `getSlowNodes` at warn level can be noisy in clusters with persistent slow reports.

## Test signals

Tests should cover report replacement by same reporter, stale filtering, all-node map filtering, JSON schema, top-N by vote count, zero/negative max settings, and disabled subclass parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java

## Purpose

`StorageTypeStats` aggregates capacity and service counts for one HDFS storage type, including special accounting for shared `PROVIDED` storage.

## Important APIs and types

The class tracks total, used, non-DFS used, remaining, block-pool used, nodes in service, and aggregate xceiver count. Public getters expose raw capacities adjusted for `PROVIDED`, percentage helpers via `DFSUtilClient`, and node counts. Package methods add/subtract `DatanodeStorageInfo` and `DatanodeDescriptor` contributions.

## Control flow

`addStorage` and `subtractStorage` assert the storage type, always adjust used/non-DFS/block-pool usage, and include full capacity/remaining only for in-service nodes. Out-of-service nodes contribute DFS-used to total capacity instead. `addNode` and `subtractNode` update in-service node counts and xceiver totals. Getters divide capacity values by nodes in service for `PROVIDED` storage to avoid counting the same logical storage once per reporting DataNode.

## State and persistence behavior

State is in-memory cluster-statistics aggregation. It is rebuilt from DataNode heartbeats/storage reports and not persisted. The copy constructor copies capacity fields and node count but does not copy `storageType` or xceiver count, which is notable for consumers.

## Dependencies and integration points

It integrates with `DatanodeStats`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `StorageType`, provided-storage accounting, and JMX/metrics bean exposure through constructor properties.

## Risks and edge cases

`PROVIDED` division depends on a positive in-service node count. The copy constructor omission of `storageType` can change provided-storage getter behavior if used. Percent remaining uses `getPercentUsed` helper for remaining/total, which is semantically a percentage calculation despite the method name.

## Test signals

Tests should cover in-service and out-of-service accounting, add/subtract symmetry, provided-storage de-duplication, xceiver counts, copy constructor behavior, and percentage zero-total handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java

## Purpose

`UnresolvedTopologyException` signals failure to resolve a node's topology path, such as rack or network location, during block placement or topology-aware operations.

## Important APIs and types

The class extends `IOException`, defines `serialVersionUID`, and exposes a message constructor.

## Control flow

There is no internal algorithm. Callers throw it when topology resolution cannot produce a usable location.

## State and persistence behavior

The class has no mutable state beyond inherited exception fields. It is not persisted.

## Dependencies and integration points

It integrates with block placement policies, network topology mapping, and DataNode registration/placement paths that require resolved rack paths.

## Risks and edge cases

The exception preserves only caller-provided text, so diagnostics depend on including node and mapping context at throw sites.

## Test signals

Tests should cover topology mapper failures, invalid rack strings, and caller behavior that surfaces the exception without falling back to unsafe placement assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java

## Purpose

`AutoCloseDataSetLock` adapts a `Lock` to Hadoop's `AutoCloseableLock` pattern so DataNode dataset locks can be acquired and released with try-with-resources.

## Important APIs and types

The class stores a `Lock`, optional parent `AutoCloseDataSetLock`, and optional `DataNodeLockManager`. `lock` acquires the wrapped lock, `close` releases it, invokes manager `hook`, and closes the parent lock. `setParentLock` assigns a parent only once, and `setDataNodeLockManager` registers the callback manager.

## Control flow

Clients typically receive an already-created lock wrapper from a `DataNodeLockManager`, call `lock`, run protected code, and rely on `close` for release. Parent lock chaining lets lower-level locks release higher-level locks in reverse chain order from a single close call.

## State and persistence behavior

State is in-memory synchronization state only. There is no persistence. The wrapper does not null out the lock after close, so double-close would attempt a second unlock.

## Dependencies and integration points

It integrates with DataNode dataset locking, `DataNodeLockManager`, `DataSetLockManager.LOG`, and Hadoop `StringUtils` stack traces for null-lock misuse diagnostics.

## Risks and edge cases

Null locks are logged rather than throwing, except subclass no-op behavior. Double close and lock/close imbalance depend on underlying `Lock` behavior. Parent chains must be acyclic; no protection exists against cycles.

## Test signals

Tests should cover lock/unlock calls, manager hook invocation, parent close ordering, null-lock logging, no-op subclass behavior, and double-close failure expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java

## Purpose

`BlockAlias` is the minimal interface for objects that expose an HDFS `Block` from an external alias map, primarily for provided-storage loading.

## Important APIs and types

The interface has one method, `getBlock()`, returning `org.apache.hadoop.hdfs.protocol.Block`.

## Control flow

There is no control flow. Alias-map readers iterate implementations and feed blocks to block-report processing or provided-storage metadata consumers.

## State and persistence behavior

The interface owns no state. Implementations such as `FileRegion` hold alias metadata and may be backed by text files, LevelDB, or other alias-map stores.

## Dependencies and integration points

It integrates with `BlockAliasMap`, `ProvidedStorageMap.ProvidedBlockList`, and external storage region descriptors.

## Risks and edge cases

The interface only exposes the block, not the external location. Consumers that need location metadata must downcast or use richer implementation APIs.

## Test signals

Tests should ensure alias-map implementations return stable `Block` values and that block-report wrappers consume only the interface method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java

## Purpose

`DataNodeLockManager` defines the DataNode dataset lock hierarchy abstraction used to coordinate block-pool, volume, and directory level operations.

## Important APIs and types

The generic type parameter extends `AutoCloseDataSetLock`. `LockLevel` enumerates `BLOCK_POOl`, `VOLUME`, and `DIR`. Implementations provide `readLock`, `writeLock`, `addLock`, `removeLock`, and `hook`.

## Control flow

Callers request read or write locks for a lock level and resource path, use the returned auto-close wrapper, and release by closing. The documented order is block pool, then volume, then directory when acquiring nested locks.

## State and persistence behavior

The interface owns no state. Implementations maintain lock registries in memory; `addLock` and `removeLock` allow dynamic resource registration.

## Dependencies and integration points

It integrates with DataNode dataset/replica map locking, `AutoCloseDataSetLock`, concrete `DataSetLockManager`, and `NoLockManager` for tests or temporary maps.

## Risks and edge cases

The enum constant `BLOCK_POOl` uses a lowercase final `l`, so string-based references are fragile. Deadlock avoidance depends on implementations and callers honoring the documented order. The `hook` semantics are implementation-specific.

## Test signals

Tests should cover lock hierarchy ordering, dynamic add/remove, read/write mutual exclusion, hook callbacks, resource key construction, and no-op manager compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java

## Purpose

`ECTopologyVerifier` checks whether the current cluster topology can support enabled erasure-coding policies.

## Important APIs and types

Static entry points accept either a `DatanodeInfo[]` report plus policies or explicit rack/DataNode counts plus policies, returning `ECTopologyVerifierResult`. Helpers compute unique rack count, readable policy names, and minimum required DataNodes/racks.

## Control flow

For all policies, the verifier computes the maximum `dataUnits + parityUnits` as the required DataNode count. It computes rack requirement as `ceil(policyDN / parityUnits)` and takes the maximum across policies. Empty policy sets are treated as success. Verification fails first on insufficient DataNodes, then on insufficient racks, otherwise returns success with a readable policy list.

## State and persistence behavior

The class is stateless and final with a private constructor. It persists nothing.

## Dependencies and integration points

It integrates with `ErasureCodingPolicy`, `DatanodeInfo`, `ECTopologyVerifierResult`, and EC policy enablement/admin flows.

## Risks and edge cases

The rack calculation assumes rack-fault-tolerant placement expectations and may be conservative for custom policies. Rack counting trusts `DatanodeInfo.getNetworkLocation`, including null or default locations as map keys. Empty policies produce success rather than warning failure.

## Test signals

Tests should cover empty policies, multiple policies with different maxima, insufficient DataNodes, insufficient racks, duplicate rack locations, and readable error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java

## Purpose

`FileRegion` represents a provided-storage block alias backed by a byte range in an external file path.

## Important APIs and types

It implements `BlockAlias` and stores a `Pair<Block, ProvidedStorageLocation>`. Constructors accept block ID, `Path`, offset, length, optional generation stamp, optional nonce, or direct `Block` plus `ProvidedStorageLocation`. APIs expose `getBlock`, `getProvidedStorageLocation`, equality, and hash code.

## Control flow

Construction creates a `Block` with the supplied length/generation stamp and a `ProvidedStorageLocation` with path, offset, length, and nonce. Alias-map readers then return `FileRegion` objects to provided-storage block report processing.

## State and persistence behavior

Instances are immutable after construction. Persistence depends on the alias-map implementation that serializes/deserializes file regions, such as text or LevelDB maps.

## Dependencies and integration points

It integrates with `BlockAliasMap`, `ProvidedStorageMap`, `Block`, `Path`, `ProvidedStorageLocation`, and the grandfather generation-stamp constant for older constructors.

## Risks and edge cases

No validation is performed on offset, length, nonce, or path. Equality includes both block and location, so two aliases for the same block but different external range are different `FileRegion` values.

## Test signals

Tests should cover constructor variants, default generation stamp, nonce preservation, equality/hash behavior, and alias-map round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java

## Purpose

`GenerationStamp` is the sequential-number primitive for HDFS block generation stamps.

## Important APIs and types

It extends `SequentialNumber`, defines `LAST_RESERVED_STAMP = 1000L`, and initializes new instances to that reserved value.

## Control flow

The class delegates all increment/skip behavior to `SequentialNumber`. Allocation code uses it as the cursor for new generation stamps.

## State and persistence behavior

The current value is mutable state inherited from `SequentialNumber` and is persisted indirectly as part of namespace/storage metadata managed elsewhere.

## Dependencies and integration points

It integrates with block allocation, block recovery, generation-stamp validation, and `HdfsServerConstants.RESERVED_LEGACY_GENERATION_STAMPS`.

## Risks and edge cases

Correctness depends on external synchronization and persistence of the cursor. Starting at the reserved value prevents allocation of low reserved stamps but callers must use the next-value semantics correctly.

## Test signals

Tests should verify initial value, sequential advancement, skip behavior, persistence restore through BlockIdManager/storage, and recovery generation-stamp ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/GenerationStamp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java

## Purpose

`HdfsServerConstants` centralizes internal HDFS server constants and enums for startup modes, node roles, replica states, block-under-construction states, layout versions, reserved paths, xattrs, and block ID encoding.

## Important APIs and types

Key enums are `NodeType`, `RollingUpgradeStartupOption`, `StartupOption`, `NamenodeRole`, `ReplicaState`, and `BlockUCState`. Constants include path limits, invalid transaction ID, legacy generation-stamp reservation, NameNode layout versions, reserved path components, crypto/security/xattr names, mover ID path, block-group index mask, maximum blocks per group, and maximum DataNode bandwidth.

## Control flow

`RollingUpgradeStartupOption.fromString` rejects the removed `downgrade` option and parses allowed values. `StartupOption` stores mutable option-specific state such as cluster ID, rolling-upgrade option, force/noninteractive format flags, and recovery force level; `getEnum` parses persisted enum strings with rolling-upgrade suboptions. `ReplicaState` serializes by ordinal byte and validates ordinals on read.

## State and persistence behavior

Most constants are static. `StartupOption` enum instances contain mutable fields, so option parsing changes enum singleton state. `ReplicaState` ordinal serialization is persisted/on-wire sensitive and must remain append-compatible with layout-version gating.

## Dependencies and integration points

It integrates with NameNode startup, rolling upgrade, recovery, storage layout versions, FSDirectory reserved names, replica state reports, block construction, xattrs, and EC block group encoding.

## Risks and edge cases

Mutable enum fields can leak between parses/tests if not reset. `ReplicaState` ordinal changes are compatibility-sensitive. The rolling upgrade downgrade rejection embeds documentation text. Block-group constants must match `BlockIdManager` and sequential group ID generation.

## Test signals

Tests should cover startup option parsing/stringification, rolling-upgrade invalid values, recovery context creation, replica state read/write and invalid ordinals, reserved path/xattr constants, and EC block index mask assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HdfsServerConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java

## Purpose

`HostRestrictingAuthorizationFilter` is a WebHDFS servlet filter that restricts selected authenticated read/token operations by user, client IP subnet, and HDFS path.

## Important APIs and types

Configuration uses `dfs.web.authentication.host.allow.rules`. `getFilterParams` extracts prefixed config. `loadRuleMap` parses `user,cidr,path` rules separated by `|` or newline into a concurrent map of copy-on-write rule lists. `handleInteraction` implements the core logic through an `HttpInteraction` abstraction, with servlet integration via `doFilter` and `ServletFilterHttpInteraction`.

## Control flow

Requests outside the WebHDFS path prefix proceed. For WebHDFS, the filter checks query parameters for restricted operations `op=OPEN` or `op=GETDELEGATIONTOKEN`. If no remote user is present, it tries to decode a delegation token and extract the user. It authorizes if either wildcard-user rules or user-specific rules match the remote IP and if `FilenameUtils.directoryContains(rulePath, path)` passes. Otherwise it sends HTTP 403.

## State and persistence behavior

Rules are loaded at filter initialization and kept in memory. There is no dynamic refresh in this class. The map supports concurrent reads after initialization.

## Dependencies and integration points

It integrates servlet APIs, WebHDFS path conventions, delegation-token identifiers, Hadoop tokens, Apache Commons Net `SubnetUtils`, Commons IO path containment, and HDFS web authentication configuration.

## Risks and edge cases

Only exact query parts equal to the restricted operation strings are considered, so parameter ordering and extra parameters matter. `directoryContains` path behavior must match HDFS path expectations. IPv6 is not covered by `SubnetUtils`. Invalid delegation tokens propagate as errors. Empty rules deny restricted operations.

## Test signals

Tests should cover rule parsing errors, wildcard user/network rules, user-specific rules, subnet misses, path containment boundaries, delegation-token user extraction, unrestricted operations, non-WebHDFS paths, and committed response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java

## Purpose

`HttpGetFailedException` reports a failed HTTP GET while preserving the server response code.

## Important APIs and types

It extends `IOException`, stores `responseCode`, reads it from a supplied `HttpURLConnection` in the constructor, and exposes `getResponseCode`.

## Control flow

The constructor can itself throw `IOException` if `connection.getResponseCode()` fails. Callers throw it after a non-success GET response and inspect the code for retry or diagnostics.

## State and persistence behavior

State is limited to the exception message and response code. It is not persisted.

## Dependencies and integration points

It integrates with HDFS HTTP transfer/checkpoint/metadata-fetch paths that use `HttpURLConnection`.

## Risks and edge cases

Because response-code retrieval happens during construction, connection state errors can replace the intended higher-level failure. The exception does not store response body or URL.

## Test signals

Tests should cover response-code preservation, constructor propagation when response-code read fails, and caller handling for expected HTTP status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java

## Purpose

`HttpPutFailedException` reports a failed HTTP PUT while preserving the response code.

## Important APIs and types

It extends `IOException`, stores an integer `responseCode`, and exposes `getResponseCode`.

## Control flow

Callers construct it with the already-known message and status code after a failed PUT operation.

## State and persistence behavior

State is limited to the exception message and response code. It is not persisted.

## Dependencies and integration points

It integrates with HDFS HTTP upload/checkpoint/image transfer paths that use PUT semantics.

## Risks and edge cases

The exception does not include response body, headers, or URL unless the caller includes those in the message.

## Test signals

Tests should verify response-code preservation and caller behavior for retryable and non-retryable HTTP status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java

## Purpose

`InconsistentFSStateException` is thrown when an HDFS storage directory is in an unrecoverable or incompatible filesystem state.

## Important APIs and types

The constructors accept a `File` directory and description, with an overload that appends a stringified cause. Messages include the canonical path when available and fall back to `File.getPath`.

## Control flow

Storage analysis and property-reading code throw this exception for missing `VERSION` fields, incompatible namespace/cluster IDs, invalid directory transition combinations, and non-empty current directories during format checks.

## State and persistence behavior

The exception has no mutable state beyond its message. It describes persistent local storage state but does not modify it.

## Dependencies and integration points

It integrates with `Storage`, `StorageInfo`, NameNode/DataNode startup, upgrade/rollback/checkpoint recovery, and format confirmation paths.

## Risks and edge cases

Cause details are flattened into the message rather than passed as a throwable cause. Canonical path resolution failure is silently ignored.

## Test signals

Tests should assert message content for missing files/properties, incompatible namespace/cluster IDs, bad temp directory combinations, and canonical-path fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/InconsistentFSStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java

## Purpose

`IncorrectVersionException` reports incompatible software, protocol, or storage layout versions.

## Important APIs and types

It extends `IOException` and provides constructors for arbitrary messages, daemon version compatibility, and layout-version mismatch. The daemon constructor formats minimum/reported remote daemon versions; layout constructors format reported and expected numeric versions.

## Control flow

Storage and protocol code throw it when an external version is too old, too new, or otherwise unexpected for the current application.

## State and persistence behavior

The exception is message-only. It is not persisted, but it frequently guards persisted layout metadata parsing.

## Dependencies and integration points

It integrates with `StorageInfo.setLayoutVersion`, startup compatibility checks, inter-daemon compatibility checks, and layout-version upgrade/downgrade validation.

## Risks and edge cases

The numeric layout constructor names are easy to confuse because one overload takes current then reported and delegates to reported/expected ordering. Tests should assert final messages rather than assuming parameter names.

## Test signals

Tests should cover future layout detection, old daemon version messages, null `ofWhat` formatting, and caller mapping to startup failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/IncorrectVersionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java

## Purpose

`JspHelper` centralizes WebHDFS/JSP request identity handling: deriving the effective `UserGroupInformation`, decoding delegation tokens, applying proxy-user authorization, and honoring trusted proxy headers.

## Important APIs and types

Static APIs include `getDefaultWebUserName`, `getUGI` overloads, `getRemoteAddr`, `getRemotePort`, and `checkUsername`. Private helpers resolve NameNode service address, decode token-backed UGI, and parse `user.name` or legacy `ugi` query parameters.

## Control flow

In secure mode, `getUGI` prefers a delegation token parameter; token auth ignores `user.name` and `doAs`. Without a token, it requires servlet-filter authentication via `request.getRemoteUser`. In insecure mode, it uses `user.name`/`ugi` or the configured static web user. If a distinct `doAs` parameter is present, it creates a proxy UGI and calls `ProxyUsers.authorize` using `getRemoteAddr`. Token flow decodes the token, optionally sets service/kind from `nnaddr` or servlet context, verifies with a context `TokenVerifier`, obtains the token user, and attaches the token.

## State and persistence behavior

The helper is stateless. Request-derived tokens are attached to returned UGI instances. No persistent state is modified.

## Dependencies and integration points

It integrates servlet context/request APIs, `NameNodeHttpServer`, WebHDFS parameters, delegation tokens, `SecurityUtil`, `UserGroupInformation`, `ProxyUsers`, `ProxyServers`, and Kerberos short-name mapping.

## Risks and edge cases

Trusted `X-Forwarded-For` is honored only when the immediate remote address is in `ProxyServers`; stale proxy-server config affects audit/proxy checks. Token auth bypasses query user/doAs by design. Missing remote user in secure mode is fatal. `checkUsername` compares expected short names after Kerberos name translation.

## Test signals

Tests should cover secure token, secure filter user, insecure static user, `doAs` authorization, trusted and untrusted proxy headers, `nnaddr` token service setting, token verifier invocation, legacy `ugi`, and username short-name checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java

## Purpose

`MetricsLoggerTask` dumps Hadoop JMX metrics to a named logger, typically for periodic operational diagnostics.

## Important APIs and types

The constructor accepts metrics logger name, node name, and maximum log line length. `run` queries platform MBeans matching `Hadoop:*`, filters unsupported complex attribute types, fetches attributes, and logs `mbeanName:attribute=value` lines. Helpers are `trimLine`, `hasAppenders`, and `getFilteredAttributes`.

## Control flow

The task exits early if the metrics logger is not info-enabled, has no appenders, or the object-name pattern failed to initialize. Otherwise it logs begin/end markers, iterates MBeans, retrieves allowed attributes in batch, truncates long values if configured, and logs per-MBean errors without stopping the whole dump.

## State and persistence behavior

State is limited to logger configuration. Metrics are read live from the platform MBean server and persisted only as log output.

## Dependencies and integration points

It integrates with Java Management APIs, Hadoop `MBeans`, SLF4J, and Log4j appender detection.

## Risks and edge cases

Log4j-specific appender detection is called from SLF4J logger names and may not work with all logging backends. Complex OpenMBean values are skipped entirely. Very high attribute counts can produce large logs despite line truncation.

## Test signals

Tests should cover early exits, attribute filtering, truncation boundaries, per-MBean exception handling, begin/end markers, and logger/appender configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java

## Purpose

`NoLockManager` is a no-op `DataNodeLockManager` for tests or temporary DataNode data structures that do not require real dataset locking.

## Important APIs and types

It returns a singleton `NoDataSetLock`, a private subclass of `AutoCloseDataSetLock` with no-op `lock` and `close`. All manager methods `readLock`, `writeLock`, `addLock`, `removeLock`, and `hook` are no-ops.

## Control flow

Callers can use it through the same try-with-resources lock API as a real manager, but no synchronization occurs.

## State and persistence behavior

The only state is a reusable no-op lock object. There is no persistence and no resource registry.

## Dependencies and integration points

It integrates with code paths parameterized by `DataNodeLockManager`, especially unit tests and temporary replica maps that want to avoid lock setup.

## Risks and edge cases

Using it in production shared mutable dataset paths would remove mutual exclusion. Because the same lock object is returned for all resources, tests that assert distinct lock identity should not use this manager.

## Test signals

Tests should verify API compatibility, no thrown exceptions under try-with-resources, no side effects from add/remove/hook, and clear separation from real lock-manager tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java

## Purpose

`Storage` is the abstract base for HDFS NameNode/DataNode local storage metadata management. It owns storage directories, layout constants, startup-state analysis, upgrade/rollback/checkpoint recovery, locking, formatting confirmation, and VERSION file writing.

## Important APIs and types

Major types are `StorageState`, `StorageDirType`, nested `StorageDirectory`, and `FormatConfirmable`. Directory APIs include iterators, `getFiles`, `addStorageDir`, duplicate checks, `writeAll`, and `unlockAll`. `StorageDirectory` exposes path helpers for `current`, `previous`, temp transition directories, `VERSION`, locking, `analyzeStorage`, `doRecover`, `clearDirectory`, and `hasSomeData`. Static helpers include `confirmFormat`, `checkVersionUpgradable`, `writeProperties`, `rename`, `nativeCopyFileUnbuffered`, `deleteDir`, `getBuildVersion`, and `getRegistrationID`.

## Control flow

Startup calls `analyzeStorage`, which handles provided storage as normal, creates missing directories only for format/hotswap, locks usable directories, checks old layout support, inspects `VERSION` and transition temp directories, and returns a `StorageState`. `doRecover` completes or rolls back interrupted transitions by renaming/deleting `previous.tmp`, `removed.tmp`, `finalized.tmp`, or `lastcheckpoint.tmp`. VERSION writes use `RandomAccessFile`, store properties, then truncate to the written position.

## State and persistence behavior

Persistent state is the storage directory tree and `VERSION` properties: layout version, storage type, namespace ID, cluster ID, and cTime. Runtime state includes a copy-on-write list of `StorageDirectory` objects and file locks. Shared directories skip locking.

## Dependencies and integration points

It integrates with `StorageInfo`, `NamespaceInfo`, NameNode/DataNode storage subclasses, `StorageLocation`, layout-version classes, native IO, filesystem permissions, upgrade/finalize/rollback flows, and format prompts.

## Risks and edge cases

Directory transition recovery is sensitive to exact temp-directory combinations. File locking may be unsupported or unreliable on NFS. Asynchronous deletion renames directories before background deletion, so failures leave `.tmp` cleanup work. `StorageDirectory` supports null roots for provided storage, so callers must handle null path helpers.

## Test signals

Tests should cover every `StorageState`, recovery rename/delete effects, format confirmation force/noninteractive/interactive paths, VERSION write truncation, lock acquisition failures, shared-directory locking bypass, duplicate storage detection, provided storage paths, and native copy validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java

## Purpose

`StorageErrorReporter` is a callback interface for journal/storage components to report errors on underlying files without creating circular dependencies.

## Important APIs and types

It declares one method, `reportErrorOnFile(File f)`.

## Control flow

Implementations receive error reports from components such as `JournalManager` and decide how to mark the storage directory failed, degrade service, or surface diagnostics.

## State and persistence behavior

The interface owns no state. Implementations may mutate storage health state in memory and may indirectly affect persisted storage availability.

## Dependencies and integration points

It depends on `File` and is documented for use by NameNode journal managers and storage owners.

## Risks and edge cases

The interface does not define severity, exception cause, or retryability. Callers must choose the correct file path to let implementations map it to a storage directory.

## Test signals

Tests should cover journal-manager error callbacks, storage-directory failure mapping, repeated reports, and behavior for files outside known storage roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageErrorReporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java

## Purpose

`StorageInfo` holds the common identity and compatibility fields read from HDFS storage `VERSION` files: layout version, namespace ID, cluster ID, creation time, and node type.

## Important APIs and types

It exposes getters, `setStorageInfo`, string conversions, colon-separated parsing helpers, `readProperties`, `readPreviousVersionProperties`, `setFieldsFromProperties`, validation setters for layout, namespace, cluster ID, cTime, and storage type, plus service layout-version/feature-map accessors. `readPropertiesFile` loads Java properties from a `RandomAccessFile`.

## Control flow

Reading a VERSION file loads properties, then sets layout version, namespace ID, cTime, cluster ID if federation is supported, and validates storage type. Future layout versions are rejected with `IncorrectVersionException`; incompatible namespace or cluster IDs raise `InconsistentFSStateException`; missing properties raise `InconsistentFSStateException`.

## State and persistence behavior

Fields are mutable and reflect the currently loaded storage directory set. The data is persisted in `VERSION` files written by `Storage`. Cluster ID is only required for layout versions supporting federation.

## Dependencies and integration points

It integrates with `Storage.StorageDirectory`, `HdfsServerConstants.NodeType`, DataNode and NameNode layout-version feature maps, `LayoutVersion`, and storage startup.

## Risks and edge cases

Colon-separated parsing blindly splits on `:`, so malformed strings throw runtime parsing exceptions. `readPropertiesFile` opens files as `rws`, which can imply write intent for a read operation. Namespace/cluster compatibility allows zero/empty values as unset placeholders.

## Test signals

Tests should cover missing properties, incompatible namespace/cluster IDs, future layout rejection, storage type mismatch, federation and pre-federation cluster ID handling, previous version reads, and string/colon round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/StorageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java

## Purpose

`TokenVerifier` is the WebHDFS delegation-token verification extension point used by NameNode and Router HTTP helpers.

## Important APIs and types

It is generic over `AbstractDelegationTokenIdentifier` and declares `verifyToken(T t, byte[] password) throws IOException`.

## Control flow

`JspHelper` decodes a delegation token from the request, reads the identifier, obtains a verifier from servlet context, and calls `verifyToken` with the identifier and token password before accepting token-backed UGI.

## State and persistence behavior

The interface owns no state. Implementations validate against token secret managers or router-side token services.

## Dependencies and integration points

It integrates with WebHDFS, `JspHelper`, `NameNodeHttpServer`, delegation-token identifiers, and NameNode/Router token verification.

## Risks and edge cases

If no verifier is present in context, `JspHelper` accepts the decoded token UGI without this callback. Implementations must avoid leaking token secrets in exception messages or logs.

## Test signals

Tests should cover successful verification, rejected password/identifier, missing verifier behavior, Router/NameNode implementations, and propagation of `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java -->
