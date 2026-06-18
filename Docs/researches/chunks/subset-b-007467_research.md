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
