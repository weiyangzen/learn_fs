# Research: subset-b-007505

Grouped research for HDFS NameNode files in subset B. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeRpcServer.java

## Purpose
`NameNodeRpcServer` is the central RPC facade for the NameNode. It implements `NamenodeProtocols` and exposes client, DataNode, lifeline, HA, refresh, reconfiguration, inotify, cache, snapshot, encryption, erasure coding, and storage policy operations. The class is intentionally thin in business logic: it validates startup state and operation category, applies retry-cache idempotency for mutating calls, updates metrics and audit logs, then delegates to `FSNamesystem`, `BlockManager`, `CacheManager`, `NameNode`, or edit-log helpers.

## Important APIs, types, and functions
The constructor builds protobuf translators for client, DataNode, lifeline, NameNode, HA, refresh, user mapping, generic refresh, and reconfiguration protocols. It creates the client RPC server, optional service RPC server, optional lifeline RPC server, service ACLs, tracers, auxiliary listeners, terse exception lists, and address publication back into `NameNode`. Accessors expose RPC servers and listener addresses for tests.

Client protocol methods cover file creation, append, lease recovery, block allocation, block locations, pipeline update, rename, concat, truncate, delete, mkdirs, listings, file info, stats, DataNode reports, safe mode, namespace save, rolling upgrade, snapshots, cache directives, ACLs, xattrs, encryption zones, re-encryption, erasure coding policies, inotify edit reads, reconfiguration, and storage policy satisfier integration. DataNode protocol methods handle registration, heartbeats, block reports, cache reports, incremental block reports, error reports, and lifeline messages. HA methods call `NameNode` state transition logic.

## Control flow
Most RPCs begin with `checkNNStartup()`. Writes call `namesystem.checkOperation(OperationCategory.WRITE)` and many reads call `READ`; unchecked internal calls still validate superuser privilege. Mutating RPCs retrieve a `RetryCache` entry through client id and call id, return cached success when possible, execute the delegated namesystem action, and set retry state in `finally`. Path-creating operations run `checkPathLength`. DataNode calls validate registration IDs through `verifyRequest` and software versions through `verifySoftwareVersion`.

`getEditsFromTxid` is the largest local algorithm. It validates active-read and superuser privilege, determines whether in-progress edit segments can be read from `FSEditLog.getSyncTxId()`, runs the stream selection as the login user for secure remote journal access, iterates edit streams in transaction order, translates `FSEditLogOp` entries to inotify `EventBatch` values, and stops at the max event count or sync txid. Missing or moved edit segments are treated as benign races and return partial or empty results.

## State and persistence behavior
The server owns RPC listener state and published socket addresses. It does not persist namespace changes directly; delegated `FSNamesystem`, edit-log, snapshot, cache, encryption, quota, and erasure-coding paths perform persistence. Retry-cache state is critical for idempotent client retries after RPC failure. `saveNamespace`, checkpoint, rolling upgrade, edit rolling, inotify, and DataNode report operations bridge directly into persistent FSImage/edit-log and block-manager state.

## Dependencies and integration points
Key dependencies include Hadoop IPC `RPC.Server`, protobuf translators, `FSNamesystem`, `NameNode`, `NameNodeMetrics`, `RetryCache`, `BlockManager`, `FSEditLog`, `DFSUtil`, service ACL policy providers, HA service protocol, and security/user mapping services. It is constructed by `NameNode.createRpcServer` and exposed to clients, DataNodes, secondary/backup NameNodes, ZKFC, balancers, administrators, and external SPS.

## Risks and invariants
The class is broad and security-sensitive. Missing a `checkOperation`, superuser check, registration check, or retry-cache update can create authorization bugs, standby write leakage, duplicate mutations, or DataNode spoofing. Output and exception behavior is part of external RPC compatibility. Inotify must not read past committed edit txids. Block report lease handling must avoid accepting stale or duplicate full reports. HA transition methods are synchronized and include a special Observer/ZKFC denial path to avoid an Observer being forced to Standby incorrectly.

## Test signals
Direct signals include `TestNameNodeRpcServer`, `TestHDFSPolicyProvider`, `TestRefreshCallQueue`, HA/Observer tests, inotify tests, block report tests, snapshot/cache/encryption/EC suites, and DataNode registration tests. Useful targeted checks are retry-cache replay for each mutating RPC, service/lifeline address binding with ephemeral ports, standby rejection of writes, DataNode version and registration mismatch rejection, inotify behavior while edit segments roll or disappear, and external SPS mode gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeStatusMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeStatusMXBean.java

## Purpose
`NameNodeStatusMXBean` is the private, stable JMX management interface for NameNode status information. It defines the read-only attributes exposed through JMX rather than a concrete implementation.

## Important APIs, types, and functions
The interface exports `getNNRole()`, `getState()`, `getHostAndPort()`, `isSecurityEnabled()`, `getLastHATransitionTime()`, `getBytesWithFutureGenerationStamps()`, `getSlowPeersReport()`, and `getSlowDisksReport()`. The slow peer and slow disk reports are JSON strings when those features are enabled.

## Control flow
There is no runtime control flow in this file. Implementations, principally NameNode status/metrics classes, are expected to compute these values from NameNode role, HA state, RPC address, security configuration, HA transition bookkeeping, block-manager safe-mode metadata, and slow-node monitoring providers.

## State and persistence behavior
The interface owns no state and performs no persistence. It represents transient operational state visible to JMX clients. The last HA transition time is a durable-looking timestamp value, but storage and updates are handled elsewhere.

## Dependencies and integration points
It depends only on Hadoop classification annotations. It integrates with JMX registration of NameNode MXBeans and with operators or monitoring systems that scrape NameNode role, state, security, and slow DataNode reports.

## Risks and invariants
Because this is marked `InterfaceStability.Stable`, method names and return types are compatibility surface. Changing report formats, especially JSON strings for slow peers/disks, can break monitoring dashboards. Implementations should avoid expensive blocking work on JMX calls.

## Test signals
Relevant coverage is usually in NameNode metrics/JMX tests and slow DataNode reporting tests rather than tests of this interface directly. Regression tests should verify MXBean attribute names, JSON report validity, and HA transition timestamp updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeStatusMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeUtils.java

## Purpose
`NameNodeUtils` contains private utility logic for NameNode startup and addressing. Its only behavior here is resolving the NameNode address clients should use before the configuration is overridden during NameNode initialization.

## Important APIs, types, and functions
`getClientNamenodeAddress(Configuration conf, @Nullable String nsId)` returns `null`, a physical `host:port`, or a logical nameservice ID. It inspects `fs.defaultFS`, configured nameservices, HA namenode lists, and `dfs.namenode.rpc-address.[nsId]`. The constructor is private to prevent instantiation.

## Control flow
The function returns `null` when `fs.defaultFS` is missing, unparsable as a URI host, or lacks a nonzero port after fallback. For HA nameservices, when the current namespace ID is known and has more than one HA namenode, it returns the logical nameservice ID. For federated non-HA namespaces it prefers the current namespace RPC address and falls back to the `fs.defaultFS` authority. It parses a port by splitting on `:`.

## State and persistence behavior
The utility is stateless and does not mutate configuration. Its return value is consumed during startup to preserve the client-facing address before bind addresses and service addresses are finalized.

## Dependencies and integration points
It depends on `Configuration`, `DFSUtilClient.getNameServiceIds`, `fs.defaultFS`, `dfs.ha.namenodes.*`, and `dfs.namenode.rpc-address`. `NameNode` uses this logic while setting `clientNamenodeAddress`.

## Risks and invariants
Address parsing is intentionally conservative. Returning a logical nameservice for HA is required for failover clients. Returning a physical address with port zero or no port would mislead clients, so it returns `null` and lets later startup code resolve a real bind address. The simple colon split is sensitive to IPv6-style authorities unless upstream URI/address conventions shield this path.

## Test signals
Tests should cover unset default FS, default FS without host, single NameNode, HA nameservice, federation where current namespace differs from default, zero/missing port, and namespace-specific RPC-address fallback. Startup tests around `NameNode.clientNamenodeAddress` are the likely integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NamenodeFsck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NamenodeFsck.java

## Purpose
`NamenodeFsck` implements the server-side HDFS fsck operation used by the HTTP fsck servlet and `DFSck` tool. It scans paths, directories, snapshots, files, blocks, replicas, storage policies, and erasure-coded block groups to report health. It can also list corrupt files, inspect individual block IDs, move salvageable corrupt file blocks into `/lost+found`, delete corrupt files, or queue mis-replicated blocks for replication.

## Important APIs, types, and functions
The constructor parses servlet query parameters such as `path`, `move`, `delete`, `files`, `blocks`, `locations`, `racks`, `replicadetails`, `upgradedomains`, `maintenance`, `storagepolicies`, `openforwrite`, `listcorruptfileblocks`, `startblockafter`, `includeSnapshots`, `blockId`, and `replicate`. Public entrypoints are `fsck()`, `blockIdCK(String)`, `getAuditSource()`, and `newDataEncryptionKey()` for encrypted data transfer while copying blocks. Core helpers are `check`, `checkDir`, `getBlockLocations`, `collectFileSummary`, `collectBlocksSummary`, `copyBlocksToLostFound`, `copyBlock`, `bestNode`, and `lostFoundInit`. Nested `Result`, `ReplicationResult`, and `ErasureCodingResult` accumulate report counters and render stable text summaries.

## Control flow
`fsck()` starts by handling block-ID-only queries with superuser privilege and block-manager read access. Normal path fsck logs the request, optionally loads snapshottable roots, resolves the path through `NameNodeRpcServer`, optionally lists corrupt file blocks, initializes storage policy summary, and recursively calls `check`. Directory traversal uses batched `getListing` calls and optionally descends into `.snapshot`. File traversal gets block locations under FSNamesystem read lock, classifies replicated versus erasure-coded results, gathers file totals, and then validates every located block.

`collectBlocksSummary` counts live, decommissioned, maintenance, stale, corrupt, missing, under-replicated, over-replicated, under-minimum, and placement-policy-violating blocks. Open last blocks are skipped when incomplete. If a file is corrupt or missing blocks, non-open files may be moved or deleted depending on options. `copyBlocksToLostFound` creates per-file chain directories and streams each available block from a randomly chosen live DataNode using `BlockReaderFactory`; gaps start a new chain. `doReplicate` queues placement-violating blocks through `BlockManager.processMisReplicatedBlocks`.

## State and persistence behavior
Most state is per-request counters and flags. Persistent side effects occur only for `-move`, `-delete`, and `-replicate`: `/lost+found` directories/files can be created, corrupt files can be deleted through NameNode RPC, and replication work can be enqueued. Block inspection and normal health reports are read-only. Output strings such as `is HEALTHY`, `is CORRUPT`, and `FAILED` are intentionally consumed by `DFSck`.

## Dependencies and integration points
The class depends on `NameNode`, `FSNamesystem`, `NameNodeRpcServer`, `BlockManager`, `NetworkTopology`, `BlockPlacementPolicies`, `DFSClient`, `BlockReaderFactory`, DataNode descriptors, storage policies, erasure coding metadata, block tokens, tracing, and the fsck servlet. `DFSck` parses final status lines and many tests assert exact status text.

## Risks and invariants
Fsck is operationally sensitive. It must not hold locks while doing slow DataNode I/O, must preserve final status strings, and must separate open-under-construction files from corrupt complete files. Salvage can partially copy data and marks `internalError` on failures so the final result becomes failure. Deleting or moving corrupt files is destructive and must continue to route through RPC permission checks. Placement policy checks must distinguish replicated and striped block semantics. Random DataNode selection and retry loops should not spin forever when all replicas are unavailable.

## Test signals
`TestFsck`, `TestHAFsck`, encryption zone fsck tests, EC fsck tests, decommission/maintenance/stale replica tests, and `DFSck` client parsing are primary signals. Important cases include healthy and corrupt paths, nonexistent paths, missing blocks, corrupt replicas, open files hidden or shown, snapshots, block ID lookup, storage policy summaries, maintenance states, lost+found salvage, delete behavior, and replication queueing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NamenodeFsck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Namesystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Namesystem.java

## Purpose
`Namesystem` is a private interface that abstracts the NameNode namespace/block-management core for callers that should not depend on the full `FSNamesystem` concrete type. It combines read/write locking, safe-mode queries, block lookup, namespace services, cache services, and HA context access.

## Important APIs, types, and functions
The interface extends `RwLock` and `SafeMode`. It declares `isRunning()`, `getBlockCollection(long)`, `getFSDirectory()`, `startSecretManagerIfNecessary()`, `isInSnapshot(long)`, `getCacheManager()`, `getHAContext()`, `inTransitionToActive()`, `removeXattr(long, String)`, and `checkAndProvisionSnapshotTrashRoots()`.

## Control flow
There is no implementation here. The contract implies callers must acquire the appropriate inherited lock before operations that require namespace consistency. `inTransitionToActive` lets dependent services avoid racing HA activation startup.

## State and persistence behavior
This interface owns no state. Implementations provide access to persistent namespace structures (`FSDirectory`, block collections, xattrs, snapshots) and runtime services (cache manager, secret manager, HA context). `removeXattr` and snapshot trash provisioning are mutating operations whose persistence is handled by implementors.

## Dependencies and integration points
It integrates with `BlockCollection`, `FSDirectory`, `CacheManager`, `HAContext`, `RwLock`, and `SafeMode`. Many NameNode subsystems can use this narrower type to avoid depending directly on the full concrete namesystem.

## Risks and invariants
Implementations must keep lock semantics consistent with `RwLock` and safe-mode semantics consistent with `SafeMode`. The xattr removal method is inode-ID based, so callers must pass stable IDs and expect failures for deleted or replaced inodes. Snapshot trash provisioning must be idempotent.

## Test signals
Coverage comes through `FSNamesystem` tests, HA transition tests, cache manager tests, snapshot trash provisioning tests, and xattr removal paths. Interface-specific tests are unlikely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Namesystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NetworkTopologyServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NetworkTopologyServlet.java

## Purpose
`NetworkTopologyServlet` exposes the NameNode's current DataNode network topology at `/topology`. It supports text and JSON output and is installed by `NameNodeHttpServer`.

## Important APIs, types, and functions
Constants define servlet name, path, and supported formats. `doGet` resolves the NameNode from servlet context, gets `BlockManager`, asks the DataNode manager network topology for leaves under the root, and delegates to `printTopology`. `printTopology` groups node names by rack and sorts racks and nodes. `printJsonFormat` emits an array of rack objects with node `ip` and optional `hostname`; `printTextFormat` emits readable rack/node lines. `parseAcceptHeader` chooses JSON when the HTTP Accept header contains `json`, otherwise text. `BadFormatException` signals unsupported internal format values.

## Control flow
`doGet` sets content type based on parsed format, writes through a UTF-8 `PrintStream`, catches any throwable during printing, returns HTTP 410 with a stringified exception, and closes the response stream in `finally`. Empty topology prints `No DataNodes`.

## State and persistence behavior
The servlet is read-only and stateless. It reflects transient in-memory DataNode topology and performs reverse hostname lookup through `NetUtils.getHostNameOfIP` for display.

## Dependencies and integration points
It depends on servlet APIs, `NameNodeHttpServer`, `BlockManager`, Hadoop `NetworkTopology`, `Node`, `NodeBase`, Jackson `JsonGenerator`, HTTP Accept headers, and `NetUtils`. Operators and tests consume the endpoint.

## Risks and invariants
The Accept parser is intentionally simple; any Accept header containing `json` gets JSON. Text is the default fallback. Reverse DNS lookup can be slow or return null, so hostname is optional. The response stream is closed even though servlet containers normally own it; this is existing behavior to preserve. JSON shape is a compatibility surface for tooling.

## Test signals
`TestRouterNetworkTopologyServlet` covers the router analogue, while NameNode HTTP tests and network topology tests are relevant. Good targeted checks include empty topology, sorted rack/node output, text defaulting, JSON Accept negotiation, hostname omission when lookup fails, and failure-to-print error response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NetworkTopologyServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Quota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Quota.java

## Purpose
`Quota` defines the two core quota dimensions tracked by the NameNode: namespace object count and storage space bytes including replication.

## Important APIs, types, and functions
The enum values are `NAMESPACE` and `STORAGESPACE`. Nested `Quota.Counts` extends `EnumCounters<Quota>` and provides `newInstance(long namespace, long storagespace)` plus a zero-argument zero counter factory. `isViolated(long quota, long usage)` returns true when a set quota is exceeded. The package-private delta form returns true only when quota is set, delta is positive, and `usage + delta` would exceed quota while avoiding overflow via `usage > quota - delta`.

## Control flow
The logic is simple predicate evaluation. A negative quota means unset or reset and is never considered violated in these helpers.

## State and persistence behavior
The enum and helper counters own no persistent state. Quota values are stored in inode directory features, edit logs, and fsimage structures elsewhere. `Quota.Counts` is a mutable counter object used by quota calculation code.

## Dependencies and integration points
It depends on `EnumCounters`. It is used by `QuotaCounts`, `FSDirectory`, `INode`, directory quota features, quota edit operations, and tests validating namespace and diskspace quota enforcement.

## Risks and invariants
Violation semantics must stay exact: quota is violated only when set and usage is strictly greater than quota. The delta helper must not flag negative or zero deltas, because decreases and no-ops cannot introduce violations. Any change affects all quota enforcement.

## Test signals
`TestQuota`, `TestDiskspaceQuotaUpdate`, snapshot quota tests, EC quota tests, and rename quota correctness tests are relevant. Unit tests should cover unset quota, exact-boundary usage, positive delta crossing the boundary, zero/negative delta, and large values near `Long.MAX_VALUE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Quota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaByStorageTypeEntry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaByStorageTypeEntry.java

## Purpose
`QuotaByStorageTypeEntry` is a small value object representing a quota for one `StorageType`, such as DISK, SSD, ARCHIVE, or RAM_DISK.

## Important APIs, types, and functions
Fields are `StorageType type` and `long quota`. Accessors expose both. `equals`, `hashCode`, and `toString` support comparison, map/set usage, and textual rendering. `Builder` sets storage type and quota and constructs an entry through the private constructor.

## Control flow
There is no complex control flow. `toString` asserts `type != null` and renders the lower-case storage type name, a colon, and quota.

## State and persistence behavior
The object holds an in-memory pair. Persistence of per-storage-type quotas happens in namespace metadata and RPC/protobuf conversions elsewhere. The fields are mutable only internally during construction, but the class is effectively immutable after build because there are no setters on the entry.

## Dependencies and integration points
It depends on `StorageType`, Guava-compatible `Objects`, and `StringUtils.toLowerCase`. It integrates with quota listing/reporting APIs and user-facing quota-by-storage-type displays.

## Risks and invariants
The builder does not validate that `type` is non-null or quota has a legal sentinel/value. Invalid entries can fail later at `toString` or be rejected by downstream quota code. The text format is compact and likely expected by CLI/report consumers.

## Test signals
Quota-by-storage-type tests should cover builder output, equality/hash consistency, text rendering, null type handling through downstream validation, and all storage types. Broader signals come from `TestQuota`, storage policy quota tests, and CLI quota report tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaByStorageTypeEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaCounts.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaCounts.java

## Purpose
`QuotaCounts` aggregates namespace, storage-space, and per-storage-type counters used for quota usage and quota limit calculations throughout the NameNode. It optimizes common all-zero and all-reset cases by sharing immutable `ConstEnumCounters`.

## Important APIs, types, and functions
Static constants represent default zero and `HdfsConstants.QUOTA_RESET` values for both quota dimensions and storage-type dimensions. `modify` copies a const counter to a mutable counter before applying an action. `Builder` sets namespace, storage space, type-space counters, type-space scalar values, or copies another `QuotaCounts`. Instance methods add, subtract, negate, get/set/add namespace and storage space, get/set/add type-space values, check whether any counts meet a threshold, and implement `equals` and `toString`.

## Control flow
The central invariant is copy-on-write for shared `ConstEnumCounters`. Setters call `setQuotaCounter` so when both namespace/storage-space counts are zero or reset, the shared default/reset object is reused. Type-space builder methods similarly reuse shared const counters for all-zero/all-reset values and mutate only when necessary.

## State and persistence behavior
`QuotaCounts` is mutable. It is not itself persistent, but instances are computed from and written into inode quota features, namespace updates, snapshots, rename deltas, and fsimage/edit-log operations elsewhere. `getTypeSpaces` returns a defensive mutable copy, while package-private setters can install shared const counters.

## Dependencies and integration points
It depends on `Quota`, `StorageType`, `EnumCounters`, `ConstEnumCounters`, `HdfsConstants.QUOTA_RESET`, and Java `Consumer`. It is heavily used by `FSDirectory`, `INode`, snapshot reclaim contexts, quota verification, storage policy accounting, and quota tests.

## Risks and invariants
Mutating a shared `ConstEnumCounters` would corrupt global defaults, so every mutation path must use `modify`. Equality compares underlying counters; `hashCode` intentionally asserts false and returns a constant, so instances should not be used as hash keys. Threshold helpers have special behavior for shared default/reset counters that must match full counter semantics. Builder copy behavior must avoid aliasing mutable counters from another instance.

## Test signals
Strong signals include `TestQuota`, `TestDiskspaceQuotaUpdate`, `TestCorrectnessOfQuotaAfterRenameOp`, EC quota tests, and snapshot deletion/rename quota tests. Focused unit tests should verify copy-on-write, default/reset sharing, `getTypeSpaces` defensive copies, add/subtract/negation across namespace/storage/type counters, and threshold behavior for const and non-const counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaCounts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/RedundantEditLogInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/RedundantEditLogInputStream.java

## Purpose
`RedundantEditLogInputStream` merges multiple finalized edit-log input streams that cover the same start transaction and provides failover to alternate streams if the current stream fails. It is used by `JournalSet` when redundant journals can provide overlapping edit segments.

## Important APIs, types, and functions
The class extends `EditLogInputStream`. Constructor arguments are a collection of streams and a start txid. It validates each stream has valid first/last txids and the same first txid, then sorts streams by descending last txid so longer streams are preferred. Public overrides include stream naming, first/last txid, close, next op reading, version, position, length, in-progress flag, max op size, and locality. Internal state includes `curIdx`, `prevTxId`, sorted `streams`, `state`, and `prevException`. The state machine states are `SKIP_UNTIL`, `OK`, `STREAM_FAILED`, `STREAM_FAILED_RESYNC`, and `EOF`.

## Control flow
`nextOp()` loops over the state machine. `SKIP_UNTIL` fast-forwards the current stream to `prevTxId + 1`, throttling log messages. `OK` reads an op, advances `prevTxId`, and returns it. If read returns null before the stream's advertised last txid, it throws a local `PrematureEOFException`. `STREAM_FAILED` fails over to the next stream only if the next stream is not shorter than the failed one; otherwise it throws to avoid metadata loss. `STREAM_FAILED_RESYNC` is used by `nextValidOp()`/recovery mode to either resync the same stream or fail over. `EOF` returns null.

## State and persistence behavior
The class is read-only over edit-log storage but tracks read position and failover state. It never writes edit logs. The metadata safety invariant is that it will not silently switch to a shorter stream after starting a longer one because that could skip committed transactions.

## Dependencies and integration points
It depends on `EditLogInputStream`, `FSEditLogOp`, `HdfsServerConstants.INVALID_TXID`, `IOUtils`, `Preconditions`, `Longs`, and `LogThrottlingHelper`. `JournalSet` constructs it when selecting input streams for edit replay.

## Risks and invariants
All wrapped streams must be finalized and non-pre-transactional with identical start txids. The implementation tries each stream at most once and explicitly does not handle "ping pong" journals where each stream has different subsets of edits. Premature EOF handling differs between normal and recovery reads. Accessors assume at least one stream when not EOF; callers should not ask current stream details for an empty stream set.

## Test signals
`TestRedundantEditLogInputStream` is the direct signal. Tests should cover stream sorting, fast-forwarding from a start txid, failover after IO exceptions, rejection of failover to shorter streams, premature EOF behavior, recovery-mode resync, close propagation, and max op size propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/RedundantEditLogInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionHandler.java

## Purpose
`ReencryptionHandler` is the NameNode background worker that walks encryption zones and submits file EDEK re-encryption batches to a thread pool. It handles traversal, batching, throttling, cancellation, resume from checkpoints, nested-zone skipping, and coordination with `ReencryptionUpdater`.

## Important APIs, types, and functions
The constructor wires `EncryptionZoneManager`, `FSDirectory`, KMS provider validation, sleep interval, batch size, handler throttle ratio, EDEK worker pool, completion service, updater, current batch, and traverser. Public/thread lifecycle methods include `run`, `startUpdaterThread`, and `stopThreads`. Zone state methods include `cancelZone`, `removeZone`, `getTracker`, `addDummyTracker`, `notifyNewSubmission`, `reencryptEncryptionZone`, `completeReencryption`, and `restoreFromLastProcessedFile`. Inner types include `ReencryptionBatch`, `EDEKReencryptCallable`, `ReencryptionPendingInodeIdCollector`, and `ZoneTraverseInfo`.

## Control flow
The handler thread sleeps for the configured interval or until notified, then under FSNamesystem read lock selects the next unprocessed zone and marks it started. `reencryptEncryptionZone` takes the traverser read lock, resolves the zone inode, starts from the beginning or from the last checkpoint, traverses lexicographically, submits remaining batch work, and calls `ReencryptionUpdater.markZoneSubmissionDone`. Traversal adds encrypted files whose EDEK key version differs from the zone target version to `currentBatch`. Submitted `EDEKReencryptCallable` instances run without NameNode locks and call the KMS provider to re-encrypt encrypted keys.

The traverser throttles in three ways: limiting queued callables to roughly CPU count, limiting pending updater tasks to twice CPU count, and enforcing a configured lock-hold ratio. `checkINodeReady` rejects deleted/canceled zones, safe mode, and non-active/write-ineligible NameNodes. Nested encryption zone roots are skipped.

## State and persistence behavior
Persistent re-encryption status is stored in `ReencryptionStatus` and encryption-zone xattrs via `FSDirEncryptionZoneOp`, but the handler maintains volatile runtime submission trackers and current batch state. Cancellation marks zone status and cancels outstanding futures. Completion removes the tracker and returns xattrs for finish persistence by the updater.

## Dependencies and integration points
It depends on `EncryptionZoneManager`, `FSDirectory`, `FSDirEncryptionZoneOp`, `FSTreeTraverser`, `ReencryptionUpdater`, Hadoop KMS `KeyProviderCryptoExtension`, `ZoneReencryptionStatus`, `NameNode.OperationCategory`, `SafeModeException`, and re-encryption DFS config keys. Client RPC `reencryptEncryptionZone` reaches this machinery through `FSNamesystem`.

## Risks and invariants
The handler assumes a single handler thread. It must not hold namespace locks while contacting KMS. Batch sizes above 2000 risk edit-log buffer pressure in the updater. Resume from checkpoint must skip exactly the already-completed lexicographic prefix. Futures and trackers are protected by the handler monitor, while namespace consistency relies on FSDirectory/FSNamesystem locks. If cancellation or standby transition is missed, stale tasks could update xattrs after a command is no longer valid.

## Test signals
Re-encryption tests should cover command submission, empty-zone dummy tracker completion, cancellation, deleted zone handling, resume after checkpoint, nested EZ skipping, KMS failure accounting, throttling, safe-mode retry, active/standby behavior, and test pause hooks. Fault-injection hooks under `EncryptionFaultInjector` provide useful deterministic signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionUpdater.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionUpdater.java

## Purpose
`ReencryptionUpdater` is the single-threaded companion to `ReencryptionHandler` that consumes completed KMS re-encryption tasks, updates file encryption xattrs, advances zone checkpoints, and marks zones complete. It serializes metadata mutation under NameNode write locks.

## Important APIs, types, and functions
Nested `ZoneSubmissionTracker` tracks submitted futures, completion, checkpoint count, and done count. `ReencryptionTask` carries a zone id, batch, failure count, processed flag, updated count, and last processed file. `FileEdekInfo` captures a file inode id and original EDEK under read lock, later storing the new EDEK. Main methods are `run`, `markZoneSubmissionDone`, `takeAndProcessTasks`, `processTask`, `processTaskEntries`, `processCheckpoints`, `checkPauseForTesting`, and `throttle`.

## Control flow
The updater blocks on `CompletionService.take()`, throttles based on configured write-lock ratio, honors test pauses, skips canceled futures, then processes the task under `FSNamesystem` write lock and `FSDirectory` write lock. `processTaskEntries` resolves each inode by id and skips files that were deleted, moved out of matching encryption state, already on the target key version, or whose existing encrypted key material changed. Remaining files get replacement `FileEncryptionInfo` xattrs. `processCheckpoints` walks each zone's futures from the head and advances the zone checkpoint only across contiguous processed tasks, then calls `completeReencryption` when submission is done and no tasks remain.

On retriable or safe-mode failures, `takeAndProcessTasks` sleeps and retries. It calls `dir.getEditLog().logSync()` outside the FSN write lock on every attempt to avoid edit-log buffer overflow while holding the lock. After releasing directory locks, `processTask` saves file xattrs for the batch and logs checkpoint/finish xattrs.

## State and persistence behavior
Runtime state includes pause flags, throttle timers, retry interval, and running flag. Persistent side effects are file encryption xattr replacement, re-encryption progress xattr updates, finish xattr updates, and edit-log `logSetXAttrs` records. Task failure counts are reflected into zone status through progress updates.

## Dependencies and integration points
It depends on `FSDirectory`, `FSDirEncryptionZoneOp`, `ReencryptionHandler`, `CompletionService`, `ZoneReencryptionStatus`, `EncryptedKeyVersion`, `FileEncryptionInfo`, xattr APIs, `RwLockMode`, `RetriableException`, and safe-mode exceptions. It is started and stopped by `ReencryptionHandler`.

## Risks and invariants
Only one updater should run because metadata writes require global write locks. The original EDEK material check prevents stale tasks from overwriting files changed by concurrent namespace or encryption operations. Checkpoints must advance only in task order; out-of-order futures cannot move the checkpoint until earlier tasks are processed. Logging must occur outside the write lock where possible. Retrying indefinitely on safe-mode/retriable errors is intentional but can delay completion.

## Test signals
Tests should cover deleted inode skips, changed key name/version skips, changed existing EDEK skips, checkpoint ordering across out-of-order futures, empty dummy task completion, retriable safe-mode retry, cancellation, edit-log xattr logging, pause hooks, and throttle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionUpdater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeMode.java

## Purpose
`SafeMode` is a private interface that exposes the minimal safe-mode state queries needed by NameNode components.

## Important APIs, types, and functions
It declares `isInSafeMode()` for any safe-mode state and `isInStartupSafeMode()` for automatic safe mode during startup.

## Control flow
There is no implementation here. Implementors, notably `FSNamesystem`, decide how startup, manual, and extension safe-mode states map to these booleans.

## State and persistence behavior
The interface owns no state. Safe-mode state is runtime NameNode state derived from startup thresholds, block reports, administrative commands, and HA state; persistence is handled in the implementing subsystem where relevant.

## Dependencies and integration points
It depends only on Hadoop classification annotations and is extended by `Namesystem`. It is consumed by NameNode services that need safe-mode awareness without requiring the full `FSNamesystem` type.

## Risks and invariants
Callers may treat startup safe mode differently from later manual or resource-triggered safe mode, so implementations must distinguish these accurately. A false negative can allow writes or background work before namespace/block state is ready.

## Test signals
Coverage comes from safe-mode tests such as HA safe mode, striped-file safe mode, contract safe-mode tests, and NameNode startup tests. Focus on transitions into and out of startup safe mode and administrative safe-mode commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceCancelledException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceCancelledException.java

## Purpose
`SaveNamespaceCancelledException` is the package-private checked exception used to abort a running saveNamespace operation when a `Canceler` requests cancellation.

## Important APIs, types, and functions
The class extends `IOException`, has a `serialVersionUID`, and a package-private constructor accepting the cancellation reason as the exception message.

## Control flow
It is thrown by `SaveNamespaceContext.checkCancelled()` and can be caught by saveNamespace workers or callers that need to distinguish cancellation from other I/O failures.

## State and persistence behavior
The exception carries only a message. It does not modify state or persistence. Its effect is control-flow interruption of fsimage save work before or during writes to storage directories.

## Dependencies and integration points
It depends on `IOException` and Hadoop private audience annotation. It integrates with `SaveNamespaceContext`, `FSImage` save workflows, and tests around canceling namespace saves.

## Risks and invariants
Because cancellation is represented as an `IOException`, callers must not accidentally treat it as a storage corruption or permanent I/O failure. The package-private constructor keeps creation localized to NameNode save code.

## Test signals
`TestSaveNamespace` and image-save cancellation tests are the likely signals. Tests should verify cancellation reason propagation and that canceled saves do not mark storage directories failed unless an actual storage error occurred.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceCancelledException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceContext.java

## Purpose
`SaveNamespaceContext` carries shared state for an active saveNamespace operation. It lets cooperating image-save tasks access the source namesystem and txid, report storage-directory errors, mark completion, and observe cancellation.

## Important APIs, types, and functions
Fields are `FSNamesystem sourceNamesystem`, save `txid`, synchronized `List<StorageDirectory> errorSDs`, `Canceler canceller`, and a one-shot `CountDownLatch completionLatch`. Package-private methods expose the namesystem, txid, error reporting, error list, and completion marking. `checkCancelled()` is public and throws `SaveNamespaceCancelledException` when the canceler is set.

## Control flow
Save tasks call `checkCancelled` at safe points. On cancellation it throws with the `Canceler` reason. Storage-directory failures are accumulated through `reportErrorOnStorageDirectory`. `markComplete` asserts the latch has not already completed, then counts it down.

## State and persistence behavior
The context itself is transient per save operation. Its `txid` identifies the namespace transaction being saved. `errorSDs` records persistent storage directories that failed during the save so higher-level image code can handle or remove them from service. The latch records completion but is not exposed here for waiting in the viewed code.

## Dependencies and integration points
It depends on `FSNamesystem`, `StorageDirectory`, `Canceler`, `CountDownLatch`, synchronized lists, and `Preconditions`. It is part of FSImage/saveNamespace coordination and uses `SaveNamespaceCancelledException` for cancellation.

## Risks and invariants
`markComplete` is single-use and will fail if called twice, which catches lifecycle bugs. The returned `errorSDs` list is synchronized but callers still need care when iterating. Cancellation must be checked frequently enough to avoid long uninterruptible fsimage writes. Reported storage-directory errors must be interpreted separately from user-requested cancellation.

## Test signals
`TestSaveNamespace` is the main signal. Useful cases include cancellation reason propagation, multiple storage-directory error accumulation, double completion assertion, save txid propagation, and ensuring canceled operations do not leave inconsistent storage state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceContext.java -->
