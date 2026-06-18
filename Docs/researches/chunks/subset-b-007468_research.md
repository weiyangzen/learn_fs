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
