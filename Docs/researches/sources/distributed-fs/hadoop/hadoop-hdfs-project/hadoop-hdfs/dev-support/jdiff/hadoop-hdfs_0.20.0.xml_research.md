# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.20.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007467`: lines 1-6018, `Docs/researches/chunks/subset-b-007467_research.md`
- `subset-b-007468`: lines 6019-10389, `Docs/researches/chunks/subset-b-007468_research.md`

## Chunk Research

### subset-b-007467: lines 1-6018

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.20.0.xml lines 1-6018

## Purpose

This chunk is the first 6,018 lines of the JDiff API snapshot for `hadoop-hdfs 0.20.0`, generated from the HDFS Java sources in May 2009. It is not executable application code; it records the public and protected Java API surface, method signatures, inheritance, exceptions, fields, and Javadoc for compatibility comparison across Hadoop releases.

The covered range spans the end-user HDFS filesystem wrappers, client-to-NameNode protocol, DataNode and block metadata transfer records, the balancer tool contract, shared server storage/upgrade primitives, and the beginning of the DataNode storage implementation. Later packages in the XML continue beyond this chunk and must be merged with this report for full-file research.

## Important APIs, Types, and Functions

- `org.apache.hadoop.hdfs.ChecksumDistributedFileSystem` extends `ChecksumFileSystem` as a backward-compatible checksum wrapper over `DistributedFileSystem`. It exposes admin/status calls such as raw capacity/used, DataNode stats, safe mode, refresh nodes, finalize upgrade, distributed upgrade progress, `metaSave`, checksum-failure reporting, and file status.
- `DFSClient` is the core client implementation. It creates `ClientProtocol` NameNode proxies, opens files, creates files with replication/block size/permission/progress variants, sets replication/permission/owner/times, lists paths, resolves block locations, reports bad blocks, fetches file checksums, manages lease-sensitive writes, and delegates administrative operations to the NameNode.
- `DFSClient.BlockReader` wraps a DataNode block connection with checksum-aware reads, seeks, skips, chunk reads, `readAll`, close, and static `newBlockReader(...)` factory overloads. It extends `FSInputChecker`, so checksum verification is part of the read path.
- `DFSUtil.isValidName(String)` documents HDFS pathname validation: absolute paths only, with components that do not contain `:` or `/`.
- `DistributedFileSystem` is the `FileSystem` implementation used by end-user code. It wraps `DFSClient` and provides `Path`-oriented APIs for initialize/checkPath/makeQualified, working directory, open/create/append, rename/delete/list/mkdirs, block locations, quotas, content summary, checksum, permissions, ownership, timestamps, cluster stats, safe mode, namespace save, node refresh, upgrade finalization/progress, and `metaSave`.
- `DistributedFileSystem.DiskStatus` is a small capacity/used/remaining value object.
- `HDFSPolicyProvider` exposes HDFS protocol services for Hadoop's service-authorization layer.
- `HftpFileSystem` and `HsftpFileSystem` expose limited read-only HTTP/HTTPS filesystem access through NameNode servlets such as `ListPathsServlet` and `FileDataServlet`. `HftpFileSystem` holds `nnAddr`, `ugi`, random address selection, and date formatting state; `HsftpFileSystem.DummyHostnameVerifier` bypasses HTTPS hostname checks.
- `AlreadyBeingCreatedException`, `QuotaExceededException`, and `UnregisteredDatanodeException` model important namespace/write-state failures: open file conflicts, namespace or diskspace quota violations, and unregistered DataNode access.
- `Block` is the primitive Writable block identity record: block ID, byte length, and generation stamp. It can be constructed from a block file, serialized/deserialized, compared, hashed, and named.
- `BlockListAsLongs` encodes block reports as a compact `long[]` layout instead of `Block[]`, with accessors for block id, length, and generation stamp by index.
- `ClientProtocol` is the main client-to-NameNode RPC interface. It covers block location lookup, create/append/addBlock/abandonBlock/complete, bad-block reports, namespace mutations, directory creation/listing, lease renewal, cluster stats, DataNode reports, preferred block size, safe mode, namespace save, host refresh, upgrade finalization/progress, metadata dump, file info/content summary, quota changes, `fsync`, and timestamp updates.
- `ClientDatanodeProtocol.recoverBlock(...)` is a client/DataNode recovery RPC for generation-stamp recovery with optional length preservation and target DataNode list.
- `DatanodeID` is the WritableComparable identity for a DataNode, built around `host:port`, storage ID, info port, and IPC port. `DatanodeInfo` extends it with capacity/usage/remaining, last update, xceiver count, rack location, host name, tree position, and admin state.
- `DatanodeInfo.AdminStates` covers `NORMAL`, `DECOMMISSION_INPROGRESS`, and `DECOMMISSIONED`; `FSConstants.DatanodeReportType` covers `ALL`, `LIVE`, and `DEAD`; `FSConstants.SafeModeAction` covers enter/leave/get; and `FSConstants.UpgradeAction` covers status, detailed status, and force-proceed.
- `DataTransferProtocol` defines the streaming protocol operation and status constants for client/DataNode data movement: read block, write block, read metadata, replace/copy block, block checksum, and success/error/status codes.
- `LocatedBlock` pairs a `Block` with `DatanodeInfo[]`, start offset, size, and corrupt flag. `LocatedBlocks` adds file length, under-construction state, indexed lookup, binary-search insertion helpers, and Writable serialization.
- `Balancer` is a `Tool` that moves blocks from over-utilized to under-utilized DataNodes until threshold targets or exit conditions are met. It exposes `main`, `run`, configuration getters/setters, max concurrent move limits, and exit codes.
- `GenerationStamp` is a WritableComparable monotonic generation-stamp primitive, with wildcard comparison support for block/version matching.
- `Storage`, `StorageInfo`, and nested `StorageDirectory`/`StorageState`/`StorageDirType` define common NameNode/DataNode local storage metadata. They manage layout version, namespace ID, creation time, VERSION files, storage directory locks, startup state analysis, failed-transition recovery, directory clearing, and upgradeability checks.
- `Upgradeable`, `UpgradeObject`, `UpgradeManager`, `UpgradeObjectCollection`, and `UpgradeStatusReport` define the distributed upgrade framework: versioned upgrade objects, node type, start/complete hooks, status percentages, broadcast commands, sorted upgrade sets, and Writable status reporting.
- `DataNode` is the server process class for block storage. In this range it implements `InterDatanodeProtocol`, `ClientDatanodeProtocol`, `FSConstants`, and `Runnable`, and exposes socket/proxy helpers, NameNode/self addressing, registration/storage ID setup, shutdown, disk checks, the `offerService` loop, NameNode block-received notifications, daemon startup helpers, block metadata lookup, block recovery, block update, protocol-version negotiation, and key public fields such as `namenode`, `data`, `dnRegistration`, scanner state, IPC server, and packet header length.
- `DataStorage` extends `Storage` with DataNode-specific storage ID handling and VERSION-field read/write behavior.
- `FSDataset` and `FSDatasetInterface` define the DataNode block storage contract: block and metadata file lookup, metadata stream/length access, capacity/used/remaining reporting, block-length lookup, read streams, temporary write streams, recovery writes, channel offset management, finalize/unfinalize, block reports, validity checks, invalidation, data directory health checks, metadata validation, shutdown, and storage stringification. Nested `BlockInputStreams`, `BlockWriteStreams`, and `MetaDataInputStream` carry paired data/checksum streams and metadata lengths.
- `UpgradeObjectDatanode` begins at the end of this chunk and only its type, DataNode accessor, and abstract `doUpgrade` hook are visible here.

## Control Flow and Execution Model

The runtime flow implied by this API snapshot is layered. User code enters through `DistributedFileSystem`, which normalizes `Path` values, maintains a working directory, and delegates most operations to `DFSClient`. `DFSClient` talks to the NameNode through `ClientProtocol` for namespace metadata, lease coordination, block allocation, stats, safe mode, and administrative functions. For file reads and writes it then connects directly to DataNodes using the data transfer protocol and block readers/writers.

Read flow is: caller asks `DistributedFileSystem` or `DFSClient` for block locations, the NameNode returns `LocatedBlocks`, the client chooses DataNode locations sorted by proximity, and `DFSClient.BlockReader` reads chunks from a DataNode socket while validating checksums through `FSInputChecker`. On corruption, clients can report `LocatedBlock[]` back through `ClientProtocol.reportBadBlocks`; checksum wrapper code notes that it may report both candidate blocks when exact corruption attribution is uncertain.

Write flow is lease-driven. `ClientProtocol.create(...)` creates an empty namespace entry visible to readers but protected from delete/recreate/rename until completion or lease expiration. Clients allocate additional blocks with `addBlock`, can abandon partial blocks, and call `complete` when done. `complete` may return false until blocks reach minimum replication, requiring caller retries. `renewLease` keeps open creates alive; if the client stops renewing, the NameNode may revoke locks and recover files.

DataNode flow is inverted relative to ordinary RPC servers: DataNodes repeatedly call NameNode-side methods from `offerService`, sending heartbeats and block reports and receiving commands to delete, copy, recover, finalize, or re-register. NameNodes do not directly connect to DataNodes for work dispatch. DataNodes separately keep sockets open for clients and peer DataNodes to transfer blocks.

Storage startup flow is driven by `StorageDirectory.analyzeStorage(startOpt)` and `doRecover(curState)`. The storage layer identifies normal, missing, unformatted, upgrade, rollback, finalize, and checkpoint transition states, recovers incomplete transitions, locks directories, reads/writes VERSION files, and exposes startup options such as regular, format, upgrade, rollback, finalize, and import.

Distributed upgrade flow uses `UpgradeManager` to collect matching `Upgradeable` instances from `UpgradeObjectCollection`, start upgrades, maintain status/version/broadcast-command state, and complete upgrades. `ClientProtocol.distributedUpgradeProgress` and `FSConstants.UpgradeAction` expose status and forced progress to clients/admin tools.

The balancer operates as an external tool loop: it periodically fetches DataNode utilization from the NameNode, chooses movements from high-utilization nodes to low-utilization nodes, enforces per-DataNode move concurrency and bandwidth limits, and exits on balanced cluster, no movable blocks, lack of progress, IO errors, or detection of another running balancer.

## State and Persistence Behavior

HDFS namespace and block state are represented as protocol contracts rather than implementations in this XML, but the documented state model is explicit. The NameNode owns namespace state, file leases, safe mode state, quotas, replication targets, block placement metadata, and cluster statistics. Clients observe and mutate that state through `ClientProtocol`, with exceptions for direct DataNode data transfer.

Safe mode is a persistent operational state of the NameNode during which namespace mutation is blocked and replication/deletion does not proceed. Startup safe mode waits for block reports until a configured percentage of blocks satisfy minimum replication, then remains for an extension period. Manual safe mode persists until explicitly left.

DataNode state centers on the table `block -> stream of bytes`. This table is stored on local disk, reported to the NameNode at startup and periodically, and exposed through `FSDatasetInterface` for reads, writes, validation, and invalidation. Blocks have separate data and metadata/checksum files, and writes can be temporary until `finalizeBlock`.

Storage persistence uses local `VERSION` files in every storage directory. Common fields include node type, layout version, namespace ID, and creation time; DataNode storage adds storage ID. The server holds storage directory locks while running, writes version files after storage-type-specific files are prepared, and uses named directories such as `current`, `previous`, temporary previous/removed/finalized/checkpoint paths to complete or recover upgrades and checkpoints.

Protocol records such as `Block`, `DatanodeID`, `DatanodeInfo`, `LocatedBlock`, `LocatedBlocks`, `GenerationStamp`, and `UpgradeStatusReport` implement Hadoop `Writable` or `WritableComparable`, so their persistence/transport contract is binary Hadoop serialization over RPC or data streams.

Upgrade state is tracked as layout versions, status percentages, finalization flags, sorted upgrade objects, current upgrade state, upgrade version, and broadcast `UpgradeCommand`s. Finalizing an upgrade removes saved previous filesystem state and makes rollback impossible.

## Dependencies and Integration Points

This API snapshot depends on Hadoop core filesystem and utility types: `FileSystem`, `ChecksumFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `ContentSummary`, `Path`, `FileChecksum`, `MD5MD5CRC32FileChecksum`, `FsPermission`, `Configuration`, `Progressable`, `Tool`, `Configured`, `Daemon`, `NetUtils`, `DiskChecker`, `Writable`, `WritableComparable`, `VersionedProtocol`, IPC `Server`, security `UserGroupInformation`, `AccessControlException`, and service-authorization `PolicyProvider`/`Service`.

Network integration spans multiple channels: Hadoop IPC for `ClientProtocol`, `ClientDatanodeProtocol`, and inter-DataNode protocols; raw or NIO sockets for DataNode block transfer; HTTP/HTTPS connections for HFTP/HSFTP read-only access; and servlet integration via NameNode file/listing servlets.

Operational integration points include `DFSAdmin`-style admin calls, `saveNamespace`, safe mode, host include/exclude refresh, `metaSave`, DataNode reports, block reports, quota management, balancer scripts, namespace/image upgrade operations, and DataNode disk health checks. `HDFSPolicyProvider` makes the HDFS protocols visible to Hadoop's service ACL machinery.

The XML itself integrates with JDiff rather than HDFS runtime. Its command-line metadata shows the JDiff doclet, JDK, Ant/Ivy classpath, and `src/hdfs` source path used to generate a compatibility baseline named `hadoop-hdfs 0.20.0`.

## Risks and Edge Cases

- This is generated JDiff XML. The source-of-truth behavior is in Java sources, but this file is authoritative for API compatibility tooling and can expose mismatches between documentation and implementation.
- The chunk line range stops inside `UpgradeObjectDatanode`; conclusions about later DataNode, NameNode, metrics, server protocol, and tools APIs require subsequent chunk reports.
- Several APIs are deprecated but still present for compatibility, including older constructors, `DistributedFileSystem.getName()`, `DFSClient.getHints()`, and `DFSClient.isDirectory()`.
- Append is visible in `ClientProtocol` but documented as enabled only when `dfs.support.append` is true; `DistributedFileSystem.append` and `HftpFileSystem.append` are documented as optional/not yet supported in this snapshot.
- `ClientProtocol.complete()` returning false is normal until minimum replication is reached. Callers that assume a single successful RPC closes a file may mishandle DataNode failure or slow replication.
- Safe mode threshold values have sharp operational edge cases: threshold 0 or empty namespace avoids startup safe mode, threshold 1 requires all blocks to satisfy minimum replication, and threshold greater than 1 prevents automatic exit.
- `getStats()` returns a positional `long[]`; callers must use the `GET_STATS_*_IDX` constants to avoid brittle index assumptions.
- `HftpFileSystem` is documented as read-only but still inherits/create/delete/rename/mkdir method signatures from `FileSystem`; tests should verify these methods reject mutation rather than relying on docs alone.
- `HsftpFileSystem.DummyHostnameVerifier` intentionally bypasses hostname checking, which is a security-sensitive compatibility behavior.
- `DatanodeID.updateRegInfo` explicitly does not update `storageID`, so registration refresh logic must not assume all identity fields are replaced together.
- `DataTransferProtocol.DATA_TRANSFER_VERSION` documentation warns that changes to `DatanodeInfo` serialization should change the data transfer version, not only obvious protocol changes.
- Storage locks are not guaranteed on all filesystems, with NFS called out as inconsistent. Startup tests on shared or network filesystems may expose duplicate-server risks.
- `FSDataset.writeToBlock` recovery mode kills other writers and reopens files; concurrent recovery/write tests need to account for writer interruption and temporary block state.

## Test Signals

Useful validation signals for this chunk are compatibility/API checks rather than direct unit tests of the XML. JDiff consumers should confirm that expected public/protected classes, methods, fields, deprecations, exceptions, and docs remain stable against later HDFS baselines.

Runtime tests suggested by the exposed API surface include:

- `DistributedFileSystem` and `DFSClient` file lifecycle tests for create, add blocks through writes, close/complete retry behavior, open/read, block locations, checksum retrieval, rename/delete/list/mkdirs, permission/owner/time updates, and quota errors.
- Client lease tests covering `renewLease`, abandoned blocks, already-being-created failures, lease expiration, and append behavior with `dfs.support.append` both disabled and enabled.
- Safe mode/admin tests for enter/get/leave, startup threshold behavior, `saveNamespace` requiring safe mode and privilege, refresh hosts/exclude files, `metaSave`, and upgrade finalization/progress reporting.
- Protocol serialization round trips for `Block`, `BlockListAsLongs`, `DatanodeID`, `DatanodeInfo`, `LocatedBlock`, `LocatedBlocks`, `GenerationStamp`, and `UpgradeStatusReport`.
- DataNode registration, heartbeat/block-report, unregistered DataNode rejection, decommission state reporting, bad-block reporting, block recovery, and generation-stamp update tests.
- Data transfer tests for block read/write/checksum operations, corrupt checksum status reporting, block metadata reads, replacement/copy operations, and version compatibility when DataNode info serialization changes.
- `FSDatasetInterface` tests for data/meta file existence, temporary write streams, finalize/unfinalize, channel position restore, metadata validation, block invalidation, block reports, disk health exceptions, and shutdown.
- Storage tests for VERSION file read/write, layout-version upgradeability, directory locks, clear-directory formatting behavior, and recovery from `previous.tmp`, `removed.tmp`, `finalized.tmp`, and checkpoint transition states.
- Balancer integration tests for threshold parsing, single-instance protection, no-move/no-progress exits, DataNode move concurrency limits, bandwidth configuration, and live-cluster utilization convergence.
- HFTP/HSFTP tests for read-only open/list/status/checksum over HTTP(S), random IP selection for multihomed hostnames, user identity query behavior, and expected rejection of mutation methods.

## Chunk Boundary Notes

Lines 1-6018 include all of `org.apache.hadoop.hdfs`, all of `org.apache.hadoop.hdfs.protocol`, all of `org.apache.hadoop.hdfs.server.balancer`, all of `org.apache.hadoop.hdfs.server.common`, and the start of `org.apache.hadoop.hdfs.server.datanode` through the beginning of `UpgradeObjectDatanode`. The XML file continues through more DataNode APIs, NameNode APIs, metrics, server protocols, and HDFS tools, so the merge lane should combine this report with later chunk reports before producing the final per-file document.

### subset-b-007468: lines 6019-10389

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.20.0.xml lines 6019-10389

## Chunk Scope

This chunk is a generated JDiff public API snapshot for HDFS 0.20.0, not Java implementation source. It records public/protected compatibility metadata: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, flags, deprecation state, and embedded Javadoc contracts.

The range starts inside the tail of `org.apache.hadoop.hdfs.server.datanode.UpgradeObjectDatanode`, then covers `org.apache.hadoop.hdfs.server.datanode.metrics`, most of `org.apache.hadoop.hdfs.server.namenode`, `org.apache.hadoop.hdfs.server.namenode.metrics`, `org.apache.hadoop.hdfs.server.protocol`, and the HDFS command-line tools `DFSAdmin` and `DFSck`. Because this is API XML, control-flow, state, and persistence notes are inferred from exposed signatures and documentation rather than method bodies.

## Purpose

The chunk captures the public surface for the core HDFS control plane in the 0.20.0 API: DataNode and NameNode metrics, NameNode namespace and block bookkeeping, edit-log and image persistence, servlet endpoints used by HFTP/web tooling and checkpoints, lease recovery, fsck reporting, distributed upgrade hooks, NameNode-to-DataNode and NameNode-to-SecondaryNameNode RPC protocols, and administrator commands.

This is a high-risk compatibility area. NameNode, FSNamesystem, and server protocol signatures define how HDFS clients mutate namespace metadata, how DataNodes register and report block state, how SecondaryNameNode checkpoints metadata, and how operators observe or force administrative state transitions.

## Important APIs and Types

### DataNode Metrics

`DataNodeActivityMBean` extends `MetricsDynamicMBeanBase` and publishes the DataNode activity MBean under a storage-id-specific JMX name. Its docs emphasize that sampled metrics require a metrics context with periodic update calls; the default null context does not average samples unless configured with an update thread.

`DataNodeMetrics` implements `org.apache.hadoop.metrics.Updater` and exposes public metric objects for DataNode activity: byte counters, block counters, local/remote client read/write counters, operation latency rates for read/write/checksum/copy/replace, heartbeat latency, and block report latency. `doUpdates(MetricsContext)` is the periodic publishing hook; `resetAllMinMax()` resets rate extrema; `shutdown()` tears down metric publication.

`FSDatasetMBean` is a stable JMX interface for DataNode storage status: `getDfsUsed()`, `getCapacity()`, `getRemaining()`, and `getStorageInfo()`. The docs intentionally distinguish this stable dataset MBean from dynamic runtime activity metrics.

### NameNode Persistence and Namespace State

`CheckpointSignature` extends `StorageInfo` and implements `WritableComparable`. It serializes and compares a unique checkpoint token used by `NamenodeProtocol.rollEditLog()` and SecondaryNameNode checkpoint flows.

`FSEditLog` maintains namespace modification logs. Exposed operations include synchronized `open()`, `createEditLogFile(File)`, and `close()`, plus `logSync()`, `logOpenFile(path, INodeFileUnderConstruction)`, `logCloseFile(path, INodeFile)`, and `logMkDir(path, INode)`. The API makes open-file, close-file, and mkdir edits explicit persistence events.

`FSImage` extends common `Storage` and handles checkpointing plus edit logging. It exposes constructors from `StorageInfo` and root `File`, protected version-file property hooks `getFields` and `setFields`, `getEditLog()`, `isConversionNeeded(StorageDirectory)`, `saveFSImage()`, `format()`, `getFsEditName()`, and `corruptPreUpgradeStorage(File)`. `checkpointTime` and `removedStorageDirs` track persistent image state and failed storage directories.

`FSNamesystem` is the central in-memory and persistent NameNode bookkeeping API. It implements `FSConstants` and `FSNamesystemMBean`. Public fields expose `dir` (`FSDirectory`), `corruptReplicas`, `leaseManager`, lease/replication daemon threads, audit logs, and a static `fsNamesystemObject`. Docs define the key tables: filename-to-blocklist persisted on disk and logged, valid block set, block-to-machine and machine-to-block maps rebuilt from reports, and an LRU cache of recent heartbeat nodes.

Important `FSNamesystem` methods include namespace-dir discovery, close/shutdown, permission and owner mutation, block location lookup, access/modification time updates, replication changes, additional block allocation, abandoned block handling, file completion, corrupt and invalidated block handling, rename/delete/mkdir/listing, DataNode registration and reports, replication/invalidation work computation, host include/exclude refresh, DataNode status reports, capacity/load/block/file counters, generation stamp accessors, and metrics access.

### NameNode RPC and Server Facade

`NameNode` implements `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `FSConstants`, and `RefreshAuthorizationPolicyProtocol`. The constructor starts a NameNode from `Configuration` and supports startup options such as regular startup, format, upgrade, and rollback via `dfs.namenode.startup`. It also updates configuration with actual bound ports when zero-valued ports are requested.

The public facade delegates across three main client groups:

- HDFS clients use namespace APIs such as `getBlockLocations`, `create`, `append`, `setReplication`, `setPermission`, `setOwner`, `addBlock`, `abandonBlock`, `complete`, `reportBadBlocks`, `nextGenerationStamp`, `commitBlockSynchronization`, `rename`, `delete`, `mkdirs`, `renewLease`, `getListing`, `getFileInfo`, `getStats`, `setSafeMode`, `saveNamespace`, `finalizeUpgrade`, `distributedUpgradeProgress`, `metaSave`, `getContentSummary`, `setQuota`, `fsync`, and `setTimes`.
- DataNodes use `register`, `sendHeartbeat`, `blockReport`, `blockReceived`, `errorReport`, `versionRequest`, `processUpgradeCommand`, `verifyRequest`, and `verifyVersion`.
- SecondaryNameNode and balancing/checkpoint code use `getBlocks`, `getEditLogSize`, `rollEditLog`, `rollFsImage`, image filename accessors, and checkpoint image upload paths.

Static and lifecycle helpers include `format(Configuration)`, `getAddress(...)`, `getUri(InetSocketAddress)`, `join()`, `stop()`, `createNameNode(argv, conf)`, `main(argv)`, `getNameNodeAddress()`, `getHttpAddress()`, and `refreshServiceAcl()`.

### Web and Diagnostic Surfaces

`FileChecksumServlets.GetServlet` and `RedirectServlet` expose HTTP checksum retrieval and redirect checksum queries to an appropriate DataNode. `FileDataServlet` creates redirect URIs for HFTP file data access. `FsckServlet` runs NameNode fsck over HTTP. `GetImageServlet` serves image/edit files, typically to SecondaryNameNode. `ListPathsServlet` returns XML metadata for filesystem listings and supports query options such as recursion, regex filter, and checksum-file exclusion. `StreamFile` streams file data through a DFS client.

`JspHelper` is the NameNode web UI helper surface. It chooses random or best DataNodes, streams block content in ASCII, reports live/dead node status, renders HTML tables and navigation forms, produces safe mode/warning/inode/upgrade status strings, sorts node lists, and holds static web UI configuration such as `WEB_UGI_PROPERTY_NAME`, `nameNodeAddr`, `conf`, `webUGI`, and `defaultChunkSizeToView`.

### Lease Recovery and Fsck

`LeaseManager` provides lease housekeeping for open files and documents the lease recovery algorithm: retrieve lease state, inspect each file's last block, choose a primary DataNode, obtain a new generation stamp, gather block metadata from replicas, compute minimum length, update replicas with the new generation stamp and length, acknowledge the NameNode, update `BlockInfo`, remove the file/lease, and commit the change to the edit log. Exposed methods include `getLeaseByPath`, synchronized `countLease`, `setLeasePeriod`, and synchronized `toString`.

`LeaseExpiredException`, `NotReplicatedYetException`, and `SafeModeException` model common write-path failure conditions: expired creation leases, not-yet-sufficiently-replicated files, and attempts to mutate namespace while safe mode is active.

`NamenodeFsck` scans DFS paths for missing, under-replicated, and over-replicated blocks. It can leave corrupt files untouched, move them to `/lost+found`, or delete them through constants `FIXING_NONE`, `FIXING_MOVE`, and `FIXING_DELETE`. `NamenodeFsck.FsckResult` aggregates health, missing block IDs and sizes, excessive replicas, missing replicas, total dirs/files/open files, sizes, replication factor, total blocks, open-file blocks, corrupt file count, and formatted output.

`SecondaryNameNode` is a daemon helper for periodic metadata checkpoints. It implements `Runnable`, connects to the primary NameNode, periodically triggers checkpoint work according to configuration, and exposes `shutdown`, `run`, and `main`.

`UpgradeObjectNamenode` is an abstract NameNode-side distributed-upgrade base. It processes generic `UpgradeCommand` messages, exposes node type, starts upgrade work, can access `FSNamesystem`, and can force progress.

### NameNode Metrics

`FSNamesystemMBean` is the stable JMX interface for NameNode filesystem state: safe mode/operational state, allocated block count, capacity total/used/remaining, total file/directory count, pending/under/scheduled replication blocks, total load, and live/dead DataNode counts.

`FSNamesystemMetrics` implements `Updater` and publishes those values through a metrics registry. Its docs note periodic updates, conversion of capacity values from bytes to GB for int-valued collectors, and casts for metrics expected to fit in integers.

`NameNodeActivtyMBean` wraps the NameNode activity metrics registry in a dynamic MBean. `NameNodeMetrics` publishes operation counters and latency rates: files created/appended/renamed/deleted, block location/listing/create/add-block operations, edit-log transactions and syncs, transactions batched in sync, block report latency, safe mode time, fsimage load time, and corrupted block count. It exposes `doUpdates`, `resetAllMinMax`, and `shutdown`.

### Server Protocol Values

`BlockCommand` extends `DatanodeCommand` and serializes block-oriented DataNode work. Constructors accept an action plus either a list or block array; getters return `Block[]` and target `DatanodeInfo[][]` arrays. This is the command container for replication transfer and invalidation work returned from heartbeats or reports.

`BlockMetaDataInfo` extends `Block` with `lastScanTime`, used by inter-DataNode generation-stamp recovery and scanner metadata flows.

`BlocksWithLocations` and nested `BlockWithLocations` implement `Writable` containers for NameNode-to-SecondaryNameNode or balancing state transfer: block identities paired with DataNode storage/location names.

`DatanodeCommand` serializes a command action and exposes singleton `REGISTER` and `FINALIZE` commands. `DatanodeProtocol` defines the DataNode-to-NameNode RPC contract and constants for notification/error codes and DataNode actions: unknown, transfer, invalidate, shutdown, register, finalize, and recover-block. Its version doc notes additions including block synchronization and bad-block reporting.

`DatanodeRegistration` extends `DatanodeID`, carries mutable `StorageInfo`, and serializes all information the NameNode needs to identify and verify a DataNode on each request. `DisallowedDatanodeException` signals include/exclude host-list rejection.

`InterDatanodeProtocol` lets DataNodes query block metadata and update a block to a new generation stamp/length, with a `finalize` parameter. `NamenodeProtocol` lets SecondaryNameNode or rebalancing clients get blocks for a DataNode, query edit-log size, roll the edit log, and roll the fsimage.

`NamespaceInfo` extends `StorageInfo` and is returned during DataNode handshake; it includes build version and distributed-upgrade version. `UpgradeCommand` extends `DatanodeCommand` with upgrade version, current status, and upgrade actions for status reporting or start-upgrade messages.

### Admin Tools

`DFSAdmin` extends `FsShell` and exposes operational commands: cluster report, safe mode enter/leave/get, namespace save, host refresh, upgrade finalization, distributed upgrade progress/status/details/force, metadata dump via `-metasave`, service ACL refresh, `run`, and `main`.

`DFSck` is a configured `Tool` frontend for filesystem checking. Its docs mirror `NamenodeFsck`: scan from a root path, detect missing blocks, optionally move corrupt files to `/lost+found` or delete them, report under/over replication, collect overall DFS statistics, optionally print block locations/replication factors, and filter open files.

## Control Flow and Behavioral Contracts

The central control flow is RPC delegation through `NameNode` into `FSNamesystem`. ClientProtocol calls mutate or inspect namespace state; DataNodeProtocol calls register storage, heartbeat capacity/load, report blocks, report received blocks, submit errors, and participate in block recovery; NamenodeProtocol calls coordinate checkpoint and balancing workflows.

Write-path control flows from file create/append into lease-managed under-construction state. `getAdditionalBlock` allocates a block and target pipeline only after previous blocks are reported and replicated enough; `abandonBlock`, `completeFile`, `NotReplicatedYetException`, and `LeaseExpiredException` encode retry and failure points. Lease recovery shifts coordination to a primary DataNode, updates generation stamps and lengths through inter-DataNode calls, then commits final state to the NameNode edit log.

Block maintenance flows from DataNode reports and corrupt-block notices into FSNamesystem maps. Heartbeats return `DatanodeCommand[]` work; `BlockCommand` carries transfer or invalidation batches and targets. `computeDatanodeWork` schedules replication and removal work that DataNodes receive on later heartbeats. Corrupt replicas are tracked separately so corrupt copies can be hidden and later removed once enough good replicas exist.

Checkpoint control uses `NamenodeProtocol.getEditLogSize`, `rollEditLog`, `GetImageServlet`, `FSImage.saveFSImage`, and `rollFsImage`. `CheckpointSignature` ties the rolled edit log and fsimage operation to a unique transaction token, and `FSImage.setFields` documents that version files are written last so missing/corrupt version files invalidate a checkpoint.

HTTP control flows serve older web and HFTP integrations. Some servlets redirect clients to DataNodes for file data or checksum retrieval, while others expose NameNode-side XML listings, streaming, image download, and fsck results. These are integration points with servlet containers, JSP pages, HFTP clients, and administrative browsers.

Metrics control is periodic. DataNode, NameNode, and FSNamesystem metrics implement or wrap `Updater`/MBean registries; metrics contexts call `doUpdates` on a cadence and MBeans expose live JMX state.

## State and Persistence

Persistent namespace state lives in the NameNode image and edit logs. `FSImage` owns checkpoint metadata, storage directories, checkpoint time, formatting, image saving, and edit-log access. `FSEditLog` records namespace mutations such as open file, close file, and mkdir operations. Namespace ID is persistent and forms part of DataNode registration validation.

FSNamesystem keeps substantial memory-only runtime state: block-to-DataNode and DataNode-to-block maps, corrupt replica maps, heartbeat freshness, lease state, replication queues, invalidation queues, live/dead DataNode status, capacity totals, load, and generation stamp. Its docs explicitly state that `DatanodeDescriptor` state is internal to the NameNode, is not sent over the wire to clients/DataNodes, and is not persisted in fsimage.

DataNode-side state appears through storage IDs, `DatanodeRegistration.storageInfo`, block reports, scanner metadata, and FSDataset capacity/remaining/used MBean values. `NamespaceInfo`, `DatanodeRegistration`, `BlockCommand`, `BlocksWithLocations`, `BlockMetaDataInfo`, and `UpgradeCommand` persist over RPC through `Writable` serialization.

Operational state includes safe mode, decommissioning and include/exclude host files, distributed upgrade progress, service ACL policy, open-file leases, `/lost+found` recovery output, and SecondaryNameNode checkpoint schedules.

Metrics state is mutable process state in public metric fields and registry-backed MBeans. Some capacity metrics are rounded to GB or cast to int for collector compatibility, so monitoring consumers should not treat all published values as byte-accurate.

## Dependencies and Integration Points

The chunk integrates with Java IO (`File`, `DataInput`, `DataOutput`, `IOException`), networking (`InetSocketAddress`, `URI`, `URISyntaxException`), servlets/JSP (`HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `JspWriter`, `ServletException`), XML output (`org.znerd.xmlenc.XMLOutputter`), logging (`commons-logging`), Hadoop IPC (`VersionedProtocol`), Hadoop configuration, metrics, security authorization, and `Writable` serialization.

Internal HDFS dependencies include `Block`, `BlockListAsLongs`, `DatanodeID`, `DatanodeInfo`, `LocatedBlock`, `LocatedBlocks`, `ClientProtocol`, `FSConstants`, common `Storage`/`StorageInfo`, `UpgradeObject`, `UpgradeStatusReport`, `HdfsConstants.NodeType`, `FSDirectory`, `INode`, `INodeFile`, `INodeFileUnderConstruction`, `LeaseManager`, `PermissionStatus`, `FsPermission`, `DFSClient`, and `HftpFileSystem`.

The major external integration surfaces are:

- RPC compatibility between clients, DataNodes, SecondaryNameNode, NameNode, and inter-DataNode recovery calls.
- JMX/metrics compatibility for operational dashboards and alerting.
- HTTP servlet compatibility for web UI, HFTP file reads/listings, fsck, file checksums, and image transfer.
- CLI compatibility for `DFSAdmin` and `DFSck`.
- On-disk compatibility for fsimage, edits, storage version files, checkpoints, namespace IDs, and pre-upgrade storage handling.

## Risks and Compatibility Notes

The chunk starts mid-class in `UpgradeObjectDatanode`, so adjacent chunks are needed for the full DataNode upgrade-object API. The rest of the range appears to end cleanly at the end of the HDFS tools package.

This XML exposes public fields in several operational classes (`FSNamesystem`, metrics classes, `NameNode`, `JspHelper`). Compatibility consumers may depend on field names and types even when they represent internal state.

Changing any RPC method signature, `versionID`, checked exception, or `Writable` field order in server protocol classes can break wire compatibility between old NameNodes, DataNodes, clients, SecondaryNameNodes, and administrative tools.

NameNode persistence is fragile by design. Edit-log sync timing, version-file write order, checkpoint signatures, image/edit rolling, and namespace ID validation must remain coherent across crashes and restarts. The JDiff snapshot does not show implementation safeguards, so final research should reconcile with source code for exact durability guarantees.

FSNamesystem mixes synchronized and unsynchronized public methods. The API indicates explicit synchronization for permission/owner/time mutation, block abandonment, corrupt/invalidate operations, DataNode registration/removal/report handling, and some status methods, but implementation-level lock ordering and daemon interactions are not visible here.

Lease recovery and block synchronization are distributed protocols with several race points: stale leases, missing last-block replicas, inconsistent replica lengths, generation-stamp mismatches, DataNode failure during primary recovery, and edit-log commit after recovery.

Host include/exclude refresh drives decommission transitions. Misreading host files or mishandling removed exclusions can strand nodes in the wrong admin state.

Servlets and JSP helpers expose filesystem metadata and data via HTTP. Authentication, proxy user selection, URI escaping, redirect target selection, XML escaping, and range/offset handling are important but not visible in API XML.

Metrics cast or round some values; capacity and block counts may overflow or lose precision if collector assumptions become invalid.

`NameNode.format(Configuration)` is documented as destructive. CLI and startup paths need strong tests around accidental format, upgrade, rollback, and finalized upgrade actions.

## Test Signals

API compatibility tests should assert that the JDiff XML preserves all classes, interfaces, fields, method signatures, inheritance, implemented interfaces, visibility, static/final/abstract/synchronized flags, checked exceptions, and deprecation strings across this range.

Persistence tests should cover `FSImage.format`, `saveFSImage`, edit-log creation/open/close/sync, open/close/mkdir edit logging, checkpoint signature round trips, edit-log rolling, fsimage rolling, missing/corrupt version-file handling, removed storage directories, and checkpoint recovery after interrupted writes.

NameNode and FSNamesystem tests should cover create/append/addBlock/complete/abandon flows, block location lookup, rename/delete/mkdir/listing, permissions/owner/times, replication increase/decrease scheduling, safe mode mutation rejection, quota/content summary paths, generation stamp update, and audit/operation metrics.

DataNode protocol tests should cover registration with new/reused storage IDs, namespace ID validation, disallowed host rejection, heartbeat command return, block reports, block received notifications, bad block reports, error reports, version mismatches, block synchronization, and command serialization for register/finalize/transfer/invalidate/recover-block actions.

Lease recovery tests should simulate expired leases, last-block replica disagreement, primary DataNode selection, metadata lookup through `InterDatanodeProtocol`, generation stamp updates, finalized versus non-finalized updates, NameNode acknowledgement, edit-log commit, and removal of files from leases.

Corruption and replication tests should cover `CorruptReplicasMap`, hiding corrupt replicas, marking and invalidating replicas, missing block counts, under/over replication counters, scheduled replication counts, and eventual removal after enough good replicas exist.

Checkpoint and SecondaryNameNode tests should cover `getEditLogSize`, `rollEditLog`, image/edit download via `GetImageServlet`, upload/roll of new fsimage, checkpoint schedule, shutdown behavior, and refusal to roll edits in safe mode.

HTTP/web tests should cover `FileDataServlet` redirects, checksum GET/redirect flow, `ListPathsServlet` recursive/filter/exclude options and XML escaping, `StreamFile` offsets/chunking, fsck servlet responses, JSP node sorting/status text, and behavior with missing files or dead DataNodes.

Metrics tests should cover periodic `doUpdates`, JMX registration/shutdown, DataNode metric increments, NameNode operation counters, min/max reset behavior, FSNamesystem capacity conversion to GB, and live/dead DataNode metric updates.

Tool tests should cover `DFSAdmin -report`, `-safemode`, `-saveNamespace`, `-refreshNodes`, `-finalizeUpgrade`, `-upgradeProgress`, `-metasave`, `-refreshServiceAcl`, exit codes, and error handling. `DFSck` tests should cover healthy, missing, under-replicated, over-replicated, open-file filtered, move-to-lost+found, and delete-corrupt scenarios.

## Chunk Boundary Notes

The preceding chunk is required to complete `UpgradeObjectDatanode`. This chunk should not be treated as a final per-file report; it is one source-tree-aligned research shard for `hadoop-hdfs_0.20.0.xml` and should be merged later with adjacent chunk reports for complete file-level synthesis.
