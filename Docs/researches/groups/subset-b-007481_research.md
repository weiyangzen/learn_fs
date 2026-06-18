# subset-b-007481 Research

Grouped source research for HDFS balancer dispatch/support classes and block-management placement/block metadata classes. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Dispatcher.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Dispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/ExitStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/ExitStatus.java

## Purpose

`ExitStatus` is the balancer command-line status enum. Each enum value maps directly to the process exit code returned by HDFS balancer and related tooling.

## Important APIs, Types, and Functions

The enum constants are `SUCCESS`, `IN_PROGRESS`, `ALREADY_RUNNING`, `NO_MOVE_BLOCK`, `NO_MOVE_PROGRESS`, `IO_EXCEPTION`, `ILLEGAL_ARGUMENTS`, `INTERRUPTED`, and `UNFINALIZED_UPGRADE`. The only method, `getExitCode()`, returns the integer code stored by the private constructor.

## Control Flow

There is no internal algorithm. Callers choose an enum based on balancer outcome and pass `getExitCode()` to CLI process-exit paths.

## State and Persistence Behavior

State is immutable enum metadata. There is no persistence, serialization logic, or external resource ownership.

## Dependencies and Integration Points

It depends only on Java enum mechanics and is consumed by balancer command code to standardize shell-visible result codes.

## Risks and Edge Cases

The numeric values are part of CLI behavior; changing them can break scripts or monitoring. Positive `IN_PROGRESS` is distinct from `SUCCESS`, while most error states are negative.

## Test Signals

Tests should assert the exact code for each enum and cover CLI mappings from already-running, no-progress, invalid-argument, interrupted, I/O, and unfinalized-upgrade paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/ExitStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/KeyManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/KeyManager.java

## Purpose

`KeyManager` provides the balancer with block access tokens and optional data-transfer encryption keys. It mirrors NameNode-exported block keys into a local `BlockTokenSecretManager`, refreshes them periodically, and supplies tokens for `REPLACE` and `COPY` DataNode operations.

## Important APIs, Types, and Functions

The constructor fetches `ExportedBlockKeys` from `NamenodeProtocol`, detects whether block tokens are enabled, initializes `BlockTokenSecretManager`, and creates a `BlockKeyUpdater` daemon at one quarter of the NameNode key update interval. `startBlockKeyUpdater()` starts refresh. `getAccessToken()` returns a dummy token when block tokens are disabled or generates a token with `REPLACE` and `COPY` access modes for a specific `ExtendedBlock`, storage types, and storage IDs. `newDataEncryptionKey()` implements `DataEncryptionKeyFactory`, caching an encryption key until expiry. `clearDataEncryptionKey()`, `updateBlockKeys()`, and `close()` manage key refresh and shutdown.

## Control Flow

At connector startup, `NameNodeConnector` creates a `KeyManager` after reading server defaults for encrypt-data-transfer. Factory methods then call `startBlockKeyUpdater()`. During a move, `Dispatcher.PendingMove.dispatch()` asks for an access token and passes the key manager into SASL negotiation. If DataNode negotiation throws `InvalidEncryptionKeyException`, the dispatcher calls `updateBlockKeys()` and `clearDataEncryptionKey()` once before retrying.

The updater daemon loops while `shouldRun`, fetching keys from the NameNode and adding them to the local secret manager. `newDataEncryptionKey()` synchronizes around the cached key so concurrent move threads share a still-valid key and only regenerate when absent or expired.

## State and Persistence Behavior

All state is process-local: NameNode proxy, booleans for token/encryption mode, `shouldRun`, secret manager, updater daemon, cached `DataEncryptionKey`, and testable `Timer`. It does not persist keys; they are fetched from the NameNode and kept in memory. `close()` flips `shouldRun` and interrupts the daemon.

## Dependencies and Integration Points

It depends on `NamenodeProtocol.getBlockKeys()`, `ExportedBlockKeys`, `BlockTokenSecretManager`, `BlockTokenIdentifier`, `DataEncryptionKeyFactory`, HDFS encryption configuration keys, and Hadoop `Daemon`/`Timer`. It integrates with `NameNodeConnector` lifecycle and `SaslDataTransferClient` during balancer moves.

## Risks and Edge Cases

If block tokens are enabled but the updater has been closed, `getAccessToken()` throws. The updater logs and continues after `IOException`, but unexpected `Throwable` disables future token generation by setting `shouldRun` false. `updateInterval / 4` assumes a positive NameNode interval. The cached encryption key relies on token lifetime/key lifetime invariants in `BlockTokenSecretManager`; stale keys surface as transfer negotiation failures and only one retry is attempted by `Dispatcher`.

## Test Signals

Tests should cover token-disabled dummy-token behavior, token-enabled access modes, updater startup/shutdown, failure after close, encryption key caching and expiry using a controllable timer, clearing cached keys, explicit block-key update, and dispatcher retry behavior after invalid encryption keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/KeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Matcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Matcher.java

## Purpose

`Matcher` is a small topology predicate interface used by balancer planning code to classify whether two nodes satisfy a desired locality relationship.

## Important APIs, Types, and Functions

The interface defines `match(NetworkTopology cluster, Node left, Node right)`. Built-in instances are `SAME_NODE_GROUP`, `SAME_RACK`, and `ANY_OTHER`, each with a descriptive `toString()`.

## Control Flow

`SAME_NODE_GROUP` delegates to `NetworkTopology.isOnSameNodeGroup`, `SAME_RACK` delegates to `isOnSameRack`, and `ANY_OTHER` returns true when the two `Node` references are not the same object.

## State and Persistence Behavior

The matchers are stateless singleton anonymous classes. There is no persistence or mutation.

## Dependencies and Integration Points

It depends on Hadoop `NetworkTopology` and `Node`. It integrates with balancer matching and source/target selection phases that need to try same-node-group, same-rack, then broader candidates.

## Risks and Edge Cases

`ANY_OTHER` uses reference inequality instead of `equals`, so two distinct objects representing the same logical node would match. Node-group matching only makes sense when the topology implementation supports node groups. Null inputs are not defended here and rely on callers/topology behavior.

## Test Signals

Tests should assert same-rack and same-node-group delegation on representative topologies, `ANY_OTHER` reference behavior, `toString()` values, and behavior when node-group awareness is absent or topology stubs return false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Matcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/MovedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/MovedBlocks.java

## Purpose

`MovedBlocks` tracks blocks recently selected for movement so the balancer does not repeatedly schedule the same block within a configured time window.

## Important APIs, Types, and Functions

The generic `Locations<L>` wrapper stores a `Block` and synchronized location list, with `clearLocations()`, `addLocation()`, `isLocatedOn()`, `getLocations()`, `getBlock()`, and `getNumBytes()`. `MovedBlocks` itself exposes `put()`, `contains()`, and `cleanup()` over two maps: current window and old window.

## Control Flow

Newly selected blocks are inserted into the current window. `contains()` checks both windows. `cleanup()` compares monotonic time with `lastCleanupTime + winTimeInterval`; once the interval expires, it discards the old window, moves the current window to old, creates a new current map, and updates `lastCleanupTime`.

## State and Persistence Behavior

State is in-memory only: two `Map<Block, Locations<L>>` windows and the last cleanup timestamp. Methods are synchronized, making window mutation thread-safe for concurrent dispatcher source threads. The structure intentionally survives dispatcher reset long enough to prevent near-term rebalancing churn.

## Dependencies and Integration Points

It depends on HDFS `Block` and Hadoop `Time.monotonicNow()`. `Dispatcher` extends `Locations` as `DBlock`, records successful candidate selections with `put()`, checks moved status during candidate filtering, and calls `cleanup()` between iterations.

## Risks and Edge Cases

Window rotation is lazy; stale entries remain until `cleanup()` is called. If the cleanup interval is too long, balancing may skip useful candidates; if too short, blocks can churn. `Locations.getLocations()` returns the mutable backing list even though access is synchronized only during the method call. Correctness depends on `Block.equals`/`hashCode` matching the desired block identity.

## Test Signals

Tests should cover insertion, lookup across current and old windows, cleanup rotation after interval, no rotation before interval, duplicate location suppression, synchronized access under concurrent put/contains, and dispatcher reset retaining moved-block suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/MovedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/NameNodeConnector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/NameNodeConnector.java

## Purpose

`NameNodeConnector` is the balancer's NameNode-facing utility. It creates protocol proxies, discovers block pool identity, fetches live DataNode and block-location data, manages the single-balancer lock file in HDFS, owns the `KeyManager`, tracks movement counters, and decides when repeated idle iterations should stop.

## Important APIs, Types, and Functions

Static `newNameNodeConnectors()` overloads create one connector per NameNode URI or URI-to-target-path mapping and start each connector's key updater. Test hooks `setWrite2IdFile()` and `checkOtherInstanceRunning()` control lock-file behavior. Constructors initialize `BalancerProtocols`, `DistributedFileSystem`, block pool ID, server defaults, key manager, getBlocks rate limiter, target paths, and optional namespace ID.

Important methods include `getBlocks()`, `getLiveDatanodeStorageReport()`, `isUpgrading()`, `getProxy()`, `shouldContinue()`, `checkAndMarkRunning()`, `close()`, movement counter accessors, `addBytesMoved()`, `getFallbackToSimpleAuth()`, and `getNNProtocolConnection()`.

## Control Flow

Connector construction creates an RPC proxy to the configured NameNode, opens the DFS, requests namespace information, creates a `KeyManager`, and optionally calls `checkAndMarkRunning()`. The lock path is handled by deleting stale files that can be appended, creating a replicated recursive file, writing the local hostname, hflushing, and keeping the stream open until close. If the create fails with `AlreadyBeingCreatedException`, another balancer is considered running.

`getBlocks()` optionally rate-limits, selects a proxy with `getProxy()`, and when configured for HA standby reads, discovers the standby `ClientProtocol` for the namespace and creates a `NamenodeProtocol` proxy to its address; otherwise it uses the main `BalancerProtocols` proxy. `getLiveDatanodeStorageReport()` follows the same standby selection for client protocol calls. `shouldContinue()` resets idle count on moved bytes and exits after `maxNotChangedIterations` zero-progress iterations.

## State and Persistence Behavior

Persistent external state is the HDFS id lock file at `idPath`, deleted on close or filesystem exit. In-memory state includes NameNode URI, block pool ID, protocol proxies, HA standby-read flags, namespace ID, configuration, key manager, DFS handle, target paths, atomic counters for bytes/blocks moved and failed, idle iteration count, and optional getBlocks rate limiter. Movement counters are process-local and reset by process restart.

## Dependencies and Integration Points

It depends on `NameNodeProxies`, `BalancerProtocols`, `NamenodeProtocol`, `ClientProtocol`, `DistributedFileSystem`, HA utilities, rolling-upgrade APIs, `DatanodeStorageReport`, `BlocksWithLocations`, Guava `RateLimiter`, and `KeyManager`. `Dispatcher` uses it for block listings, storage reports, block pool ID, tokens, counters, and continuation decisions. `Balancer` uses connector factory methods across federated or HA NameNodes.

## Risks and Edge Cases

The lock-file mechanism assumes append/create semantics accurately detect an active writer and that `hflush`/`hsync` capability exists. Static test flags are global mutable state. Standby getBlocks routing silently falls back to active behavior if no standby proxy is found. The `finally` log in `getBlocks()` says success for standby requests even if the call threw after proxy selection. Rate limiting applies only to getBlocks, not storage reports. `close()` best-effort deletes the id file and logs deletion failures.

## Test Signals

Tests should cover lock-file acquisition, already-running detection, stale id-file deletion, test flags, target path defaults, getBlocks QPS limiting, HA standby proxy selection and fallback, rolling-upgrade detection, live storage report retrieval, idle-iteration exit behavior, counter increments, key-manager lifecycle, and close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/NameNodeConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/package-info.java

## Purpose

`package-info.java` documents the `org.apache.hadoop.hdfs.server.balancer` package: HDFS Balancer tooling that moves blocks between DataNodes and storage devices to reduce skewed data distribution.

## Important APIs, Types, and Functions

The file contains package documentation only and declares the package. It does not define runtime APIs, annotations, or helper functions.

## Control Flow

There is no control flow. The text serves generated documentation and package-level context.

## State and Persistence Behavior

There is no state or persistence behavior.

## Dependencies and Integration Points

It integrates with Java package documentation for the balancer package. The described runtime classes include `Balancer`, `Dispatcher`, `NameNodeConnector`, and related helpers.

## Risks and Edge Cases

The only risk is documentation drift if balancer behavior or scope changes without updating the package summary.

## Test Signals

No executable tests are needed. Documentation checks can verify package docs build and that package names remain aligned after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceBlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceBlockPlacementPolicy.java

## Purpose

`AvailableSpaceBlockPlacementPolicy` extends the default HDFS block placement policy by biasing random DataNode choices toward nodes with lower DFS-used percentage. It preserves default placement structure while improving space balance during writes and optional local-vs-local-rack selection.

## Important APIs, Types, and Functions

`initialize()` reads balanced-space preference fraction, tolerance, tolerance limit, and local-node balancing configuration. `chooseDataNode(scope, excludedNode, StorageType)` uses `DFSNetworkTopology.chooseRandomWithStorageTypeTwoTrial()` twice, while `chooseDataNode(scope, excludedNode)` uses `clusterMap.chooseRandom()` twice. `select()` compares the two candidates and applies a random preference percentage. `compareDataNode()` implements the utilization comparison. `chooseLocalStorage()` optionally compares the local node and local rack choice when `optimizeLocal` is enabled. `swapStorageTypes()` restores storage-type request counts after trying alternate paths.

## Control Flow

After default policy initialization, configuration values are validated with warnings and defaults for invalid tolerance ranges. On each DataNode choice, the policy samples two candidates, compares their used percentage, treats them equal when they are the same node, within tolerance, under the tolerance limit condition, or a sufficiently empty local node is being considered, and then either returns the first candidate or chooses the less-used candidate with configured probability.

For optimized local placement, the policy first tries local storage with cloned storage-type demands. It then optionally tries local rack with another clone, removes tentative results while comparing, and restores the storage-type map matching the selected path.

## State and Persistence Behavior

The policy stores only in-memory configuration-derived fields: `balancedPreference`, `balancedSpaceTolerance`, `balancedSpaceToleranceLimit`, and `optimizeLocal`. It does not persist state. Placement results affect NameNode block placement decisions that later become file/block metadata.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicyDefault`, `DFSNetworkTopology`, `DatanodeDescriptor.getDfsUsedPercent()`, storage-type-aware random selection, and HDFS DFSConfigKeys. It is selected through NameNode block placement policy configuration and participates in normal write pipeline target selection.

## Risks and Edge Cases

Preference fractions outside `[0.0, 1.0]` are warned but still converted to an integer percentage, so values above 1.0 can make the preferred less-used candidate effectively always selected and negative values can invert behavior. The storage-type overload requires `clusterMap` to be a `DFSNetworkTopology`. The local optimization temporarily mutates `results`, `excludedNodes`, and storage-type maps and must keep those side effects balanced. Random tie behavior always returns `a` on exact equality.

## Test Signals

Tests should cover initialization validation, preference values at 0.5/1.0/out-of-range, tolerance and tolerance-limit comparisons, storage-type two-trial selection requiring `DFSNetworkTopology`, local optimization selecting local versus rack, restoration of `results`, `excludedNodes`, and storage-type counts, and fallback when one candidate is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceRackFaultTolerantBlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceRackFaultTolerantBlockPlacementPolicy.java

## Purpose

`AvailableSpaceRackFaultTolerantBlockPlacementPolicy` combines rack-fault-tolerant placement with an available-space bias. It keeps the rack-diversity behavior of `BlockPlacementPolicyRackFaultTolerant` while choosing between random candidates based on DataNode utilization.

## Important APIs, Types, and Functions

`initialize()` reads rack-fault-tolerant balanced-space preference and tolerance keys. `chooseDataNode(scope, excludedNode, StorageType)` samples two storage-type-compatible candidates from `DFSNetworkTopology`. `chooseDataNode(scope, excludedNode)` samples two regular candidates from `clusterMap`. `select()` applies `compareDataNode()` and the configured random preference. `compareDataNode()` treats candidates within tolerance as equal and otherwise orders by lower `getDfsUsedPercent()`.

## Control Flow

The policy initializes its superclass first, then validates preference/tolerance settings with warnings and default fallback for invalid tolerance. Each choice samples two candidates from the requested scope, compares them, and returns the less-used node with configured probability. If one sample is null, it returns the non-null sample.

## State and Persistence Behavior

State is limited to in-memory `balancedPreference` and `balancedSpaceTolerance` values. The class itself persists nothing; selected targets are persisted indirectly as NameNode block placement metadata after writes proceed.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicyRackFaultTolerant`, `DFSNetworkTopology`, `NetworkTopology`, `DatanodeDescriptor`, `StorageType`, and rack-fault-tolerant DFS configuration keys. It is used when the NameNode is configured for rack-fault-tolerant available-space placement.

## Risks and Edge Cases

Like the non-rack policy, preference fractions outside the documented range are warned but still applied numerically. The storage-type path requires `DFSNetworkTopology`. There is no tolerance-limit or local-node optimization variant here, so behavior differs from `AvailableSpaceBlockPlacementPolicy`. Equal candidates return the first sample, which can preserve random-sampling bias.

## Test Signals

Tests should cover config initialization, invalid tolerance fallback, warnings for preference outside expected bounds, less-used candidate preference probability, equal-within-tolerance behavior, null candidate handling, storage-type selection through `DFSNetworkTopology`, and preservation of rack-fault-tolerant superclass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/AvailableSpaceRackFaultTolerantBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockCollection.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockCollection.java

## Purpose

`BlockCollection` is the NameNode-side interface that lets `BlockManager` reason about an owning collection of blocks, typically an inode file, without depending directly on the inode implementation.

## Important APIs, Types, and Functions

The interface exposes block access (`getLastBlock()`, `getBlocks()`, `setBlock()`, `numBlocks()`), file/storage metadata (`getPreferredBlockSize()`, `getPreferredBlockReplication()`, `getStoragePolicyID()`, `getName()`, `getId()`), state checks (`isUnderConstruction()`, `isStriped()`), content accounting (`computeContentSummary()`), and under-construction conversion (`convertLastBlockToUC()`).

## Control Flow

There is no implementation in this file. `BlockManager` and related NameNode code call these methods while allocating, committing, recovering, deleting, or summarizing file blocks. Implementations supply the inode-specific mutation and validation.

## State and Persistence Behavior

The interface owns no state. Implementations back these calls with persistent namespace metadata in fsimage/edit logs. The distinction between contiguous and striped collections affects how block arrays represent replicas or block groups.

## Dependencies and Integration Points

It depends on `BlockInfo`, `DatanodeStorageInfo`, `BlockStoragePolicySuite`, `ContentSummary`, and Hadoop access-control exceptions. Implementations integrate with `INodeFile`, `BlockManager`, quota/content summary calculation, storage policy selection, and lease/recovery paths.

## Risks and Edge Cases

Callers must handle erasure-coded files where preferred replication returns 0. `convertLastBlockToUC()` can throw and may mutate both block state and expected locations. `setBlock()` must preserve array/index consistency in implementations. Content summary can throw access-control exceptions depending on subtree permissions.

## Test Signals

Tests should use concrete implementations to verify block array mutation, last-block conversion to under construction, striped versus contiguous reporting, storage policy IDs, preferred replication for EC files, content summary behavior, and stable block collection IDs used by `BlockInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockCollection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockIdManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockIdManager.java

## Purpose

`BlockIdManager` allocates and tracks HDFS generation stamps and block IDs for contiguous and striped blocks. It also separates legacy randomly allocated block IDs from sequential IDs and handles standby-to-active generation stamp safety during HA failover.

## Important APIs, Types, and Functions

The manager owns `legacyGenerationStamp`, current `generationStamp`, standby-only `impendingGenerationStamp`, `legacyGenerationStampLimit`, `SequentialBlockIdGenerator`, and `SequentialBlockGroupIdGenerator`. Public and package APIs set/get last allocated contiguous and striped IDs, set/get legacy and current generation stamps, upgrade legacy generation stamps, set/apply impending generation stamps, allocate next generation stamps and block IDs, detect future generation stamps, clear test state, and classify striped block IDs.

Important helpers are `isLegacyBlock()`, `isStripedBlock(Block)`, static `isStripedBlockID(long)`, `convertToStripedID(long)`, and `getBlockIndex(Block)`.

## Control Flow

During first upgrade to sequential block IDs, `upgradeLegacyGenerationStamp()` advances the new generation stamp past the legacy stamp plus a reserved range and records that value as the switch limit. New generation stamps route to the legacy or current generator based on whether the block is legacy. Legacy allocation throws `OutOfLegacyGenerationStampsException` if it reaches the limit. New block IDs route by `BlockType`: contiguous IDs from `SequentialBlockIdGenerator`, striped block-group IDs from `SequentialBlockGroupIdGenerator`.

For HA, standby tracks the highest generation stamp seen from active as `impendingGenerationStamp`; on failover `applyImpendingGenerationStamp()` bumps the active generator if needed so generation stamps are not reused. Striped detection masks block IDs and excludes legacy blocks, since old random IDs could be negative and look striped.

## State and Persistence Behavior

The class is in-memory state owned by NameNode `BlockManager`, but its allocations and current values are persisted by `FSNamesystem` through `FSEditLog` and fsimage. `BlockIdManager` itself does not write edits; it enforces allocation invariants used by the persisting layer.

## Dependencies and Integration Points

It depends on `GenerationStamp`, `SequentialBlockIdGenerator`, `SequentialBlockGroupIdGenerator`, `BlockManager`, `FSNamesystem`, `FSEditLog`, `HdfsConstants`, `HdfsServerConstants`, and `BlockType`. It integrates with block allocation, append/recovery generation stamp updates, fsimage loading, edit tailing, and erasure-coded block-group indexing.

## Risks and Edge Cases

Incorrect legacy limit handling can either reject valid legacy appends or risk generation stamp collision. `isStripedBlockID()` alone is insufficient for legacy blocks; callers must use `isStripedBlock(Block)` when generation stamp context matters. `convertToStripedID()` assumes the low block-group index bits encode internal block index. Standby failover safety depends on faithfully applying impending stamps before new allocations.

## Test Signals

Tests should cover upgrade stamp reservation, legacy limit exhaustion, sequential contiguous and striped ID allocation, fsimage setter/getter restoration, future generation stamp checks for legacy and new blocks, standby impending stamp apply behavior, `clear()` test reset, striped block ID masking, internal block index extraction, and rejection of unsupported `BlockType` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockIdManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfo.java

## Purpose

`BlockInfo` is the abstract NameNode metadata record for a block or erasure-coded block group. It extends protocol `Block` with owning block collection ID, replica/storage locations, per-storage linked-list pointers, replication information, and under-construction state.

## Important APIs, Types, and Functions

Core state accessors include `getReplication()`, `setReplication()`, `getBlockCollectionId()`, `setBlockCollectionId()`, `delete()`, `isDeleted()`, `getStorageInfos()`, `getDatanode()`, `getCapacity()`, and abstract storage APIs `numNodes()`, `addStorage()`, `removeStorage()`, `hasNoStorage()`, `isProvided()`, `isStriped()`, and `getBlockType()`.

Location internals are stored in `triplets`: for each storage slot, `[DatanodeStorageInfo, previous BlockInfo, next BlockInfo]`. Helper methods read and mutate storage, previous, and next slots; `findStorageInfo()` resolves by DataNode or storage; `listInsert()`, `listRemove()`, and `moveBlockToHead()` maintain DataNode storage block lists. Under-construction APIs include `getUnderConstructionFeature()`, `getBlockUCState()`, `isComplete()`, `isUnderRecovery()`, `isCompleteOrCommitted()`, `convertToBlockUnderConstruction()`, `convertToCompleteBlock()`, `setGenerationStampAndVerifyReplicas()`, and `commitBlock()`.

## Control Flow

Concrete subclasses allocate triplet capacity and implement how reported blocks map to storage slots. Block-map and block-report paths call `addStorage()` and insert the block into each `DatanodeStorageInfo` list. Removal requires the block to be detached from the list first, enforced by assertions. List operations update previous/next pointers in-place to avoid per-replica linked-list entry objects.

For writes and recovery, complete blocks can be converted to under-construction with expected storage targets. Repeated conversion updates the existing `BlockUnderConstructionFeature`. Commit validates block ID consistency, moves the UC state to committed, updates length, sets the final generation stamp, and returns stale replicas that should be invalidated or handled by recovery logic.

## State and Persistence Behavior

`BlockInfo` carries persistent NameNode metadata: block ID, length, generation stamp inherited from `Block`, owning block collection ID, replication for contiguous blocks, and under-construction metadata. The in-memory `triplets` and linked-list pointers are reconstructed from block reports/fsimage and are optimized for memory. `bcId` is volatile because block collection ownership can be read concurrently.

## Dependencies and Integration Points

It depends on `Block`, `BlockCollection`, `BlocksMap`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `StorageType.PROVIDED`, `BlockUnderConstructionFeature`, `ReplicaUnderConstruction`, `BlockUCState`, and `LightWeightGSet.LinkedElement`. It is central to `BlockManager`, storage reports, file inode block arrays, replication, reconstruction, deletion, and lease recovery.

## Risks and Edge Cases

The triplet array is compact but assertion-heavy; corruption of slot alignment breaks block-list traversal. `getStorageInfos()` exposes an iterator tied to `BlocksMap.StorageIterator`. Provided storage matching uses storage ID rather than DataNode object and may return a provided storage after scanning local matches. `moveBlockToHead()` assumes non-null previous when moving a non-head block. Many consistency checks are Java assertions, so production builds may not catch misuse. `commitBlock()` throws on block ID mismatch but assumes UC state exists.

## Test Signals

Tests should cover triplet capacity, storage add/remove in contiguous and striped subclasses, DataNode and provided-storage lookup, linked-list insert/remove/head movement, deletion via invalid block collection ID, equality/hash behavior inherited from `Block`, UC conversion/update, commit length and generation stamp changes, stale replica detection, and malformed list assertions in assertion-enabled tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoContiguous.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoContiguous.java

## Purpose

`BlockInfoContiguous` is the `BlockInfo` implementation for traditionally replicated HDFS blocks. It maps each replica storage to one triplet slot and grows capacity when replication increases.

## Important APIs, Types, and Functions

Constructors accept a replication size alone or a `Block` plus replication size. `addStorage()` validates the reported block ID matches this block, ensures one free triplet slot, and stores the `DatanodeStorageInfo`. `removeStorage()` removes a storage by swapping the last populated triplet into the removed slot. `numNodes()` counts populated slots by scanning from the end. `isProvided()` detects any `StorageType.PROVIDED` replica. `isStriped()`, `getBlockType()`, and `hasNoStorage()` identify the contiguous block shape.

## Control Flow

When a DataNode reports a replica, `addStorage()` calls `ensureCapacity(1)`, appends the storage at the first free slot, and clears list pointers. When a replica disappears, `removeStorage()` requires the block to have been removed from the storage's linked list first, then compacts the array by moving the last populated triplet to the removed index and clearing the old tail.

## State and Persistence Behavior

State is inherited from `BlockInfo`: block identity, generation stamp, block collection ID, replication, UC state, and triplet location array. The subclass persists no separate fields. Triplet capacity can exceed current replica count after replication changes.

## Dependencies and Integration Points

It depends on `BlockInfo`, `DatanodeStorageInfo`, `StorageType`, `BlockType.CONTIGUOUS`, and `BlockManager` callers that manage replica reports and storage lists. It is used for non-erasure-coded HDFS files and provided-storage blocks.

## Risks and Edge Cases

Duplicate storage is not explicitly rejected in `addStorage()`; callers are expected to avoid duplicate additions. `removeStorage()` compaction can change storage slot indexes, so external code must not cache contiguous indexes across mutations. Assertions enforce that linked-list pointers are clear before removal. `hasNoStorage()` only checks slot 0, which is valid because compaction keeps populated slots packed from the front.

## Test Signals

Tests should cover block ID validation on add, capacity expansion after replication increase, packed slot behavior after removal, `numNodes()` after add/remove, provided-storage detection, no-storage detection, contiguous block type reporting, and duplicate-add caller behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoContiguous.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoStriped.java

## Purpose

`BlockInfoStriped` is the `BlockInfo` implementation for erasure-coded HDFS block groups. It tracks one group block plus per-internal-block storage locations and block indexes, including over-replicated internal blocks.

## Important APIs, Types, and Functions

The constructor accepts a group `Block` and `ErasureCodingPolicy`, sizes initial triplets to data plus parity units, initializes `indices` to -1, and stores the policy. Accessors expose total/data/parity counts, cell size, real data/total block counts for short final stripes, and the policy. Storage APIs include `addStorage()`, private `addStorage(storage,index,blockIndex)`, `removeStorage()`, `getStorageBlockIndex()`, `getBlockOnStorage()`, `numNodes()`, `hasNoStorage()`, and `isProvided()`. Capacity helpers `findSlot()`, `findStorageInfoFromEnd()`, and `ensureCapacity()` handle over-replication. `spaceConsumed()` computes EC storage consumption. `StorageAndBlockIndex` and `getStorageAndIndexInfos()` expose storage/index iteration.

## Control Flow

When a DataNode reports an internal block, `addStorage()` validates that the reported ID is striped and masks to this block-group ID. The low index bits choose the canonical slot for that internal block. If that slot is occupied by another storage, the code treats the report as over-replication: it returns true if the same storage is already recorded, otherwise it finds or creates an overflow slot. The selected slot stores the storage and its internal block index.

Removal searches from the end so overflow entries are removed before canonical entries when the same storage appears multiple times. It clears storage, list pointers, and the index byte without compacting, because canonical slot positions matter. Iteration skips null storage slots and returns storage plus block index pairs.

## State and Persistence Behavior

In addition to inherited `BlockInfo` state, this class stores immutable `ErasureCodingPolicy` and mutable `indices` aligned one-to-one with triplet slots. The group block length represents data length, while `spaceConsumed()` accounts for data plus parity. Persistent block-group identity and EC policy are NameNode metadata; the triplet/index location mapping is maintained in memory from block reports and namespace state.

## Dependencies and Integration Points

It depends on `BlockIdManager` striped ID helpers, `ErasureCodingPolicy`, `StripedBlockUtil`, `BlockType.STRIPED`, `BlockUCState`, and `DatanodeStorageInfo`. It integrates with erasure-coded file writes, block reports, reconstruction, block group accounting, and balancer/mover code that maps group blocks to internal blocks.

## Risks and Edge Cases

Index alignment is critical: canonical slots map directly to internal block indexes, while overflow slots carry explicit index bytes. Removing storage leaves holes, so `numNodes()` counts non-null slots rather than relying on packed layout. `getRealDataBlockNum()` uses `(getNumBytes() - 1) / cellSize + 1`; zero-length groups would need careful handling by callers. Provided storage is explicitly unsupported for striped blocks. Capacity growth copies both triplets and indices; any mismatch corrupts reported internal block mapping.

## Test Signals

Tests should cover canonical add, over-replicated add to overflow slots, duplicate storage add idempotence, removal from overflow and canonical slots, storage block index lookup, `getBlockOnStorage()` ID construction, short final stripe real data counts, space consumed calculation, iterator skipping holes, capacity expansion preserving indices, and rejection of non-striped or wrong-group reported blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockInfoStriped.java -->
