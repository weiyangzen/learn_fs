# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Dispatcher.java

## Purpose

`Dispatcher` is the HDFS Balancer/Mover engine that turns planned source-to-target storage movements into concrete DataNode `replaceBlock` operations. It discovers live DataNodes, tracks storage groups by DataNode UUID and `StorageType`, chooses eligible blocks from overloaded sources, selects a proxy replica close to the target, dispatches authenticated data-transfer requests, and records moved-block, success, failure, timeout, and block-pinning state for each balancing iteration.

## Important APIs, Types, and Functions

The public construction surface accepts a `NameNodeConnector`, include/exclude host sets, moved-block window width, mover and dispatcher thread counts, per-node concurrency, getBlocks sizing, movement timeout, iteration timeout, and configuration. `init()` retrieves live storage reports from the NameNode, filters nodes, and rebuilds `NetworkTopology`. `dispatchAndCheckContinue()` and `dispatchBlockMoves()` run the iteration and delegate continuation policy to `NameNodeConnector.shouldContinue`.

Important nested types are `Allocator` for global mover-thread budgeting, `GlobalBlockMap` for canonical `DBlock` instances across sources, `StorageGroupMap` keyed by `datanodeUuid:storageType`, `PendingMove` for one scheduled move, `DBlock` and `DBlockStriped` for contiguous and erasure-coded block-group candidates, `Task` for bytes scheduled toward one target, `DDatanode` for per-DataNode queues and executors, and `Source` for source storage groups with fetch/choose/dispatch loops.

Key functions include `Source.getBlockList()`, `Source.chooseNextMove()`, `PendingMove.markMovedIfGoodBlock()`, `PendingMove.chooseProxySource()`, `executePendingMove()`, `PendingMove.dispatch()`, `receiveResponse()`, `isGoodBlockCandidate()`, `isGoodBlockCandidateForPlacementPolicy()`, `waitForMoveCompletion()`, `checkForBlockPinningFailures()`, and `reset()`.

## Control Flow

An iteration starts with `init()` building the topology from `getLiveDatanodeStorageReport()`. Higher-level balancer code creates `DDatanode` objects, source and target `StorageGroup`s, and `Task`s. `dispatchBlockMoves()` computes per-target thread lots from `maxMoverThreads` and target count, starts one dispatcher job per source, and waits for all source loops and target pending queues to drain.

Each `Source.dispatchBlocks()` seeds `blocksToReceive` to twice its scheduled bytes, then repeatedly tries `chooseNextMove()`. A move first reserves the target queue, then scans candidate `DBlock`s, checks moved-window, duplicate-target, storage-type, and placement-policy constraints, converts striped block groups to the internal block present on the source, chooses a proxy replica preferring same node, same node group, same rack, then any non-delayed location, and records the block in `MovedBlocks`. The move is then submitted to the target DataNode's executor.

`PendingMove.dispatch()` connects to the target transfer address, obtains a block token from `KeyManager`, negotiates SASL streams, sends a `replaceBlock` request with target storage type, source UUID, and proxy DataNode, then consumes `IN_PROGRESS` responses until final status or timeout. Success increments `bytesMoved` and `blocksMoved`; failure increments `blocksFailed`, records block-pinning failures separately, and otherwise delays both proxy and target nodes to avoid error storms. Finally it closes streams/socket, removes pending-queue entries, resets the `PendingMove`, and notifies waiters.

## State and Persistence Behavior

The dispatcher itself is in-memory, iteration-scoped state. Persistent HDFS metadata is not directly mutated here; successful `replaceBlock` operations are performed by DataNodes and later reflected through NameNode block reports. `MovedBlocks` retains current and old time windows across `reset()` so the same block is not moved repeatedly. `GlobalBlockMap` retains only moved blocks after reset. `NameNodeConnector` owns persisted balancer id-file locking and NameNode counters; `Dispatcher` reads those counters for progress.

Threading state is split between `dispatchExecutor` for source scheduling and per-target `moveExecutor`s allocated lazily by `Allocator`. `DDatanode` keeps pending moves, delay timestamps, success/failure flags, and block-pinning failure maps. `Source` keeps planned tasks, fetched source blocks, and a start timestamp used by `maxIterationTime`.

## Dependencies and Integration Points

The class depends on HDFS NameNode protocols via `NameNodeConnector`, DataNode data-transfer protocol classes (`Sender`, `BlockOpResponseProto`, `Status`, `SaslDataTransferClient`), block token and encryption support via `KeyManager`, topology decisions through `NetworkTopology`, and placement validation via `BlockPlacementPolicies`. It consumes `BlocksWithLocations`, including `StripedBlockWithLocations`, and integrates with erasure coding through internal block length/index calculations.

Higher-level integration is with `Balancer` and `Mover`, which compute source/target utilization and tasks. Operational knobs come from `DFSConfigKeys`, `HdfsClientConfigKeys`, getBlocks limits, movement timeout, no-move timeout, hot-block interval, include/exclude host lists, and client DataNode hostname behavior.

## Risks and Edge Cases

`dispatchBlockMoves()` casts `dispatchExecutor` to `ThreadPoolExecutor`; the constructor path with `dispatcherThreads == 0` leaves it null and must not call this method. Thread allocation can starve targets when `maxMoverThreads < targets.size()`. `ANY_OTHER`-style proxy selection does not reserve per-node concurrency by count alone; queue admission is delayed-node based, while executor pool sizing provides the real cap. `PendingMove` is reset after dispatch, so callers must not inspect it after completion.

Striped block handling is index-sensitive: missing storage groups from excluded, decommissioned, or maintenance nodes require `adjustIndices()` to keep locations aligned with indices. Placement checks use the contiguous policy regardless of block type, which is a notable simplification for striped groups. Timeouts stop waiting but may not stop the DataNode-side transfer. Block pinning failures are preserved for later exclusion, but other failures only create temporary delay. `MovedBlocks` uses `Block` keys, so equality and group/internal block identity matter for duplicate suppression.

## Test Signals

Useful tests should exercise candidate rejection for same source/target, wrong storage type, already moved blocks, target already hosting a replica, and placement-policy violation. Additional signals include striped internal block selection and index adjustment, proxy preference ordering, invalid encryption key retry once, timeout handling during `IN_PROGRESS`, block-pinning failure collection, include/exclude matching by host/IP/port, per-target thread allocation under small mover-thread budgets, no-move interval reset, max-iteration cancellation, and reset retaining only moved blocks.
