# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 1-6280

## Scope

This chunk is the opening slice of a generated JDiff API snapshot for `hadoop 0.18.1`. It covers the XML header, JDiff invocation metadata, the package-level Hadoop version annotation, the full public API entries for `org.apache.hadoop.conf`, and the beginning of the HDFS API surface under `org.apache.hadoop.dfs`, `org.apache.hadoop.dfs.datanode.metrics`, and `org.apache.hadoop.dfs.namenode.metrics`. The chunk ends immediately after the declaration of `org.apache.hadoop.dfs.namenode.metrics.NameNodeStatistics`, so that class is only introduced here and its members belong to later lines.

The source is compatibility metadata rather than implementation source. The research surface is therefore the exposed contract: package names, public/protected class and interface names, inheritance, implemented interfaces, constructors, method signatures, declared exceptions, fields, enum-like nested classes, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadocs.

## Purpose

The `org.apache.hadoop` package entry records `HadoopVersionAnnotation`, a compile-time package annotation used to capture the Hadoop version associated with built artifacts.

The `org.apache.hadoop.conf` package defines the core configuration abstraction used across Hadoop. `Configuration` exposes XML-backed resource loading, typed property access, variable expansion, final parameters, class loading helpers, resource lookup, local path selection, iteration, serialization of non-default properties, quiet logging mode, and a debug `main`. `Configurable` and `Configured` define the common pattern for objects that receive and retain a `Configuration`.

The `org.apache.hadoop.dfs` portion documents much of the Hadoop 0.18.1 HDFS public surface. It includes administrative tools (`Balancer`, `DFSAdmin`, `DFSck`), client filesystem implementations (`DistributedFileSystem`, `ChecksumDistributedFileSystem`, `HftpFileSystem`, `HsftpFileSystem`), server daemons (`DataNode`, `NameNode`, `SecondaryNameNode`), servlet endpoints used by NameNode/DataNode web UIs and HTTP file access, data-transfer checksum support, data node identity/status records, block storage interfaces, namespace checking and upgrade status classes, constants for wire protocols and timing, and metrics/JMX-facing classes and interfaces.

The metrics packages expose public counters and management beans for NameNode, FSNamesystem, DataNode, and FSDataset runtime state. These APIs are a major observability integration point for Hadoop 0.18.1 and are explicitly tied to the Hadoop metrics framework and JMX naming conventions.

## Important APIs, Types, and Functions

### Configuration API

- `Configurable` declares `setConf(Configuration)` and `getConf()`.
- `Configured` is the base implementation that stores a `Configuration` and exposes matching constructors.
- `Configuration` implements `Iterable<Map.Entry<String,String>>`. Its constructors create a default configuration or clone another configuration.
- Resource loading is exposed through `addResource(String)`, `addResource(URL)`, and `addResource(Path)`. Later resources override earlier resources unless an earlier property is marked final.
- Property reads include `get`, `getRaw`, typed `getInt`, `getLong`, `getFloat`, `getBoolean`, `getRange`, `getStringCollection`, and `getStrings` overloads. Property writes include `set`, `setInt`, `setLong`, `setBoolean`, and `setStrings`.
- Class lookup/configuration methods include `getClassByName`, `getClass(String, Class<?>)`, interface-constrained `getClass(String, Class<? extends U>, Class<U>)`, and `setClass`.
- Filesystem-local helper methods include `getLocalPath` and `getFile`, both selecting a directory from a configured directory list by path hash and creating the chosen directory if needed.
- Resource accessors include `getResource`, `getConfResourceAsInputStream`, and `getConfResourceAsReader`.
- `write(OutputStream)` writes non-default properties, `iterator()` exposes key/value entries, and `setQuietMode(boolean)` controls diagnostic logging.
- Nested `Configuration.IntegerRanges` parses strings such as `2-3,5,7-`, checks inclusion with `isIncluded(int)`, and formats itself with `toString()`.

### HDFS Tools and Filesystems

- `AlreadyBeingCreatedException`, `LeaseExpiredException`, `NotReplicatedYetException`, `QuotaExceededException`, and `SafeModeException` are typed `IOException` surfaces for common HDFS namespace and write-path failures.
- `Balancer` implements `Tool` and exposes `main`, `run`, `getConf`, and `setConf`. Its public exit code fields distinguish successful completion, another balancer already running, no movable block, no progress, IO failure, and illegal arguments.
- `DFSAdmin` extends `FsShell` and exposes administrative operations for reports, safe mode, refreshing host lists, finalizing upgrades, distributed upgrade progress, metadata save, command dispatch through `run`, and `main`.
- `DFSck` implements `Tool` and runs a filesystem checker that detects missing, under-replicated, and over-replicated blocks, with optional handling of corrupt files.
- `DistributedFileSystem` extends `FileSystem` and is the public HDFS client implementation. It exposes initialization, URI/name access, working/home directory operations, block location lookup, checksum verification toggling, open/create/append, replication, rename, delete, content summary, listing, mkdirs, close, disk/raw capacity reports, datanode stats, safe mode, refresh, finalize upgrade, distributed upgrade progress, metadata save, checksum-failure reporting, status, permissions, and owner changes.
- `ChecksumDistributedFileSystem` extends `ChecksumFileSystem` for backward compatibility and testing over `DistributedFileSystem`; its docs note HDFS already checksums data natively.
- `DistributedFileSystem.DiskStatus` is a capacity/used/remaining value object.
- `HftpFileSystem` and `HsftpFileSystem` expose read-only HTTP/HTTPS filesystem access via NameNode servlet endpoints. `HftpFileSystem` tracks `nnAddr`, user/group information, and a shared date formatter; `HsftpFileSystem` overrides connection opening and URI scheme behavior.

### DataNode, Checksums, and Storage

- `DataChecksum` implements `java.util.zip.Checksum` and provides factory overloads from checksum type/bytes-per-checksum, header bytes, or a `DataInputStream`. It writes and reads checksum headers, writes checksum values to streams or buffers, compares current sums against buffer contents, exposes type/size/header metadata, and implements `getValue`, `reset`, and `update` overloads. Public constants include `HEADER_LEN`, `CHECKSUM_NULL`, and `CHECKSUM_CRC32`.
- `DataNode` extends `Configured`, implements `InterDatanodeProtocol`, `ClientDatanodeProtocol`, `FSConstants`, and `Runnable`, and exposes its daemon lifecycle and protocol entry points. Important methods include `getDataNode`, address getters, `shutdown`, `offerService`, `run`, `scheduleBlockReport`, test-facing `getFSDataset`, `getBlockMetaDataInfo`, `updateBlock`, `recoverBlock`, `getProtocolVersion`, and `main`.
- `DatanodeID` is a `WritableComparable` identity record with name, storage ID, info port, and IPC port. It implements comparison based on the host:port name, plus read/write serialization.
- `DatanodeInfo` extends `DatanodeID` and implements `Node`; it adds capacity, DFS used, remaining space, last update, xceiver count, network location, host name, admin state, tree parent/level, report formatting, and serialization.
- `DatanodeDescriptor` extends `DatanodeInfo` for NameNode-internal tracking. Its docs explicitly state it is not sent over the wire and is not stored persistently in `fsImage`.
- `FSDatasetInterface` defines the storage backend contract for DataNode block storage. It covers metadata length/input streams/existence, block length and lookup, block input streams with optional seek offset, block write streams, generation-stamp/length updates, finalization/unfinalization, block reports, validity checks, invalidation, data-dir health checks, shutdown, and data/checksum stream positioning.
- `FSDatasetInterface.BlockWriteStreams` groups the data and checksum output streams for a block. `FSDatasetInterface.MetaDataInputStream` carries a metadata stream plus length.

### NameNode and Namespace APIs

- `NameNode` is the central public server class in this chunk. It implements client-facing, datanode-facing, and secondary-namenode/rebalancer protocol surfaces. Public methods include formatting storage, joining/stopping the server, retrieving NameNode metrics, returning block locations, creating files, setting replication/permission/owner, adding/abandoning/completing blocks, reporting bad blocks, generation-stamp allocation, block synchronization commit, preferred block size, rename/delete/mkdirs, lease renewal, listing/file info, statistics, datanode reports, safe mode, node refresh, edit-log and image rolling, upgrade finalization/progress, metadata save, content summary, quota set/clear, fsync, datanode registration/heartbeat/block reports/block received/error reports, version and upgrade command handling, request/version verification, fsimage path lookup, service address lookup, and `main`.
- The NameNode Javadocs identify two critical tables: filename to block sequence, and block to machine list. The namespace table is stored on disk and is described as precious; the block map is rebuilt when the NameNode starts.
- `LocatedBlocks` is a `Writable` carrier for located block lists, file length, under-construction state, indexed access, count, and read/write serialization.
- `FSConstants` centralizes public protocol operation codes, ACK/error/status codes, `DATA_TRANSFER_VERSION`, timeout and interval constants, path limits, buffer sizes, default block/socket sizes, layout version, and nested enums for checkpoint state, datanode report type, node type, safe mode actions, startup options, and upgrade actions.
- `Upgradeable` is a `Comparable` contract for distributed upgrade components. It exposes layout version, node type, display description, percent-complete status, start/complete upgrade commands, and upgrade status reports.
- `UpgradeStatusReport` is a `Writable` value object for layout version, upgrade percent, finalization state, status text, string rendering, and serialization.

### Web and Servlet Integration

- `FileDataServlet`, `ListPathsServlet`, `StreamFile`, and `FsckServlet` provide HTTP access for data redirection, path listing, streaming, and fsck execution. The HFTP filesystem and web UI helper APIs depend on these endpoints.
- `GetImageServlet` is used by NameNode Jetty for retrieving fsimage/edit-log files, typically by `SecondaryNameNode` during checkpointing.
- `DataBlockScanner.Servlet` exposes block scanner information over HTTP.
- `JspHelper` supports NameNode/DataNode JSP pages with random/best datanode selection, ASCII block streaming, live/dead node status, table rendering, safe mode/inode/upgrade text, node-list sorting, path links, goto forms, page titles, and percentage graph strings.

### Fsck, Upgrades, and Exceptions

- `NamenodeFsck` performs server-side fsck from an HTTP request context. It exposes `fsck()`, `run(String[])`, logging, and public repair mode constants `FIXING_NONE`, `FIXING_MOVE`, and `FIXING_DELETE`.
- `NamenodeFsck.FsckResult` captures health and aggregate scan statistics: missing block IDs and bytes, over/under replication, actual and intended replication, total directories/files/open files, total sizes and block counts, corrupt file count, and string formatting. Health is defined as having no missing blocks.
- `SecondaryNameNode` implements `Runnable` and `FSConstants`, exposes `shutdown`, `run`, and `main`, and is documented as the daemon that periodically checkpoints NameNode metadata through the primary NameNode protocol.
- `QuotaExceededException` supports both message-based and quota/count constructors, path-name enrichment, and custom message generation.

### Metrics and JMX

- `FSNamesystemMetrics` implements `Updater` and publishes files, blocks, capacity total/used/remaining in GB, total load, pending replication, under-replicated blocks, and scheduled replication blocks. Its docs note periodic updates and casting/rounding choices for collectors that do not handle long values.
- `NameNodeMetrics` implements `Updater`, has `shutdown`, `doUpdates`, `resetAllMinMax`, and exposes counters/rates for files created/renamed, get-block-location/listing/create/delete/add-block operations, transactions, syncs, block reports, safe mode time, fsimage load time, and corrupted blocks.
- `DataNodeMetrics` implements `Updater` and exposes counters/rates for bytes and blocks read/written/replicated/removed/verified, verification failures, local/remote client reads and writes, block operation timings, heartbeats, and block reports.
- `DataNodeStatistics` and `DataNodeStatisticsMBean` expose JMX getters for the DataNode metrics, including interval counts and min/average/max times for read, write, metadata, copy, replace, block-report, and heartbeat operations, plus `resetAllMinMax`.
- `FSDatasetMBean` exposes storage-level capacity, DFS used, remaining, and storage ID.
- `FSNamesystemMBean` exposes NameNode namespace state, block/file/capacity totals, replication queues, load, and live/dead datanode counts. The chunk stops just after `NameNodeStatistics` begins, so its implementation details are outside this research item.

## Control Flow

The XML has no executable control flow, but the API contracts describe several major Hadoop flows.

Configuration flow starts with construction, default resource loading (`hadoop-default.xml` then `hadoop-site.xml`), optional added resources, final-parameter enforcement, variable expansion during `get`, and typed conversion through typed accessors. Class-valued properties flow through the configured class loader and optional interface checks.

HDFS client flow goes through `DistributedFileSystem`: initialize from URI/configuration, validate paths, call NameNode protocol methods for namespace metadata and block locations, stream data through DataNodes, report checksum failures back toward the NameNode, and expose administrative calls such as safe mode and upgrade control. `HftpFileSystem` follows a different read-only flow: open HTTP(S) connections to NameNode servlet paths, list via `ListPathsServlet`, and redirect file-data reads through `FileDataServlet`.

DataNode flow is documented as a long-running loop. `run()` repeatedly calls `offerService()` until shutdown; `offerService()` continuously invokes remote NameNode functions. DataNodes register and heartbeat to the NameNode, send block reports, receive block transfer/delete commands, serve client and peer DataNode sockets, and schedule block reports for the next heartbeat.

NameNode flow exposes both client and datanode RPC paths. Client operations create files, allocate blocks, complete files, mutate namespace entries, query listings, enforce quotas, and control safe mode. Datanode operations register nodes, process heartbeats, receive block reports, record received blocks, verify version/registration IDs, and process upgrade commands. Secondary NameNode/checkpoint flow uses edit-log rolling, fsimage retrieval through `GetImageServlet`, uploaded checkpoint image locations, and image rolling.

Balancer flow iterates over live cluster utilization, computes whether each node is within a threshold of cluster utilization, moves blocks from highly utilized to under-utilized nodes, limits movement per iteration and per-node bandwidth, refreshes datanode information from the NameNode after each iteration, and exits with public status codes for balanced, no block moved, no progress, IO failure, illegal args, or another balancer already running.

Fsck flow scans a requested namespace root, detects missing/under/over-replicated blocks and open files, optionally moves corrupt files to `/lost+found` or deletes them, and accumulates `FsckResult` statistics for reporting.

Metrics flow is periodic. Classes implementing `Updater` are registered with the metrics framework and push current counters/rates during `doUpdates`, while MBean interfaces expose runtime snapshots and reset hooks to JMX clients.

## State and Persistence Behavior

This JDiff XML itself persists the Hadoop 0.18.1 public API for compatibility comparison. Runtime persistence is inferred from documented APIs rather than implementation bodies.

`Configuration` persists mutable configuration state in memory after loading XML resources from classpath URLs, explicit URLs, or local `Path`s. It can write non-default properties to an `OutputStream`. It treats some source properties as final so later resources cannot override them, and it expands variables from both the configuration and Java system properties on normal reads.

HDFS namespace state is owned by the NameNode. The Javadocs distinguish persistent namespace state (`filename -> blocksequence`, stored on disk in the fsimage/edit log) from the block-to-datanode map, which is rebuilt from DataNode block reports at startup. NameNode upgrade/checkpoint APIs (`rollEditLog`, `rollFsImage`, `getFsImageName`, `getFsImageNameCheckpoint`, `finalizeUpgrade`, `distributedUpgradeProgress`) directly affect durable metadata and upgrade state.

DataNode state is local block storage. `DataNode` docs describe a critical `block -> stream of bytes` table stored on local disk and periodically reported to the NameNode. `FSDatasetInterface` formalizes this persistence: data files, metadata/checksum files, temporary unfinalized writes, finalized blocks, invalidated blocks, and generation-stamp/length updates.

`DatanodeID`, `DatanodeInfo`, `LocatedBlocks`, and `UpgradeStatusReport` are `Writable` or contain writable-style read/write APIs, making their field order and encoded values part of the wire/storage compatibility surface. `DatanodeDescriptor`, in contrast, is explicitly NameNode-internal, not wire-transmitted, and not persisted in fsimage.

`DataChecksum` defines checksum headers and checksum value encoding for DFS data transfer and block metadata. Its `DATA_TRANSFER_VERSION` dependency in `FSConstants` is a compatibility risk because the docs note the version should change when `DatanodeInfo` serialization changes, not only when protocol opcodes change.

Metrics classes keep process-local counter/rate objects. They are not durable data stores, but they integrate with periodic metrics sinks and JMX. Some FSNamesystem values are rounded to GB or cast to int for collector compatibility, so observability consumers should not treat these as exact byte counters.

HTTP servlet classes persist no state by themselves in this XML, but they expose durable metadata and file content over HTTP(S), especially fsimage/edit retrieval and HFTP file data/listing routes.

## Dependencies and Integration Points

Major Java dependencies include `java.io` streams and files, `java.net.URI`, `URL`, `InetSocketAddress`, `HttpURLConnection`, servlet APIs, JSP writers, collections, enums, `Comparable`, and `java.util.zip.Checksum`.

Core Hadoop dependencies include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, and `Configured` as the configuration substrate for nearly every tool, daemon, filesystem, and metric class.
- `org.apache.hadoop.fs.FileSystem`, `ChecksumFileSystem`, `FsShell`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `ContentSummary`, and `FsPermission` for HDFS client and administrative operations.
- `org.apache.hadoop.io.WritableComparable` and writable read/write patterns for protocol records and status reports.
- `org.apache.hadoop.net.Node` for rack/topology placement metadata on `DatanodeInfo`.
- `org.apache.hadoop.util.Tool`, `Progressable`, and `DiskChecker.DiskErrorException` for command execution, progress callbacks, and storage health checks.
- `org.apache.hadoop.metrics.Updater`, `MetricsContext`, and metrics util types for counters, rates, and JMX publishing.
- Apache Commons Logging for daemon/tool diagnostics.
- Servlet/JSP infrastructure and Jetty-hosted endpoints for NameNode/DataNode web UI, fsck, HFTP/HSFTP, block streaming, and checkpoint image transfer.
- Security/user classes such as `UserGroupInformation` and `UnixUserGroupInformation` for HTTP filesystem and JSP user context.

Important integration boundaries are the NameNode client/datanode/namenode protocols, DataNode block-transfer protocol constants, FS dataset storage backend, metrics/JMX beans, and HTTP servlet URLs consumed by web UI, fsck, HFTP/HSFTP, and Secondary NameNode checkpointing.

## Risks and Compatibility Notes

- This is generated API metadata, so it lacks implementation bodies. Behavioral conclusions should be treated as API/Javadoc-derived unless verified against the corresponding Java sources.
- The snapshot includes deprecated constructors and methods on `DistributedFileSystem` and `ChecksumDistributedFileSystem`; callers relying on those compatibility surfaces may break when comparing to later Hadoop versions.
- `FSConstants` exposes many protocol opcodes, status codes, timeout constants, and `LAYOUT_VERSION`. Changes here have wire-compatibility and storage-layout implications.
- `DATA_TRANSFER_VERSION` has a documented subtlety: it should change when `DatanodeInfo` serialization changes, not only when the data-transfer protocol itself changes. Missing that coupling can cause cross-version DataNode/client failures.
- `Configuration` final-parameter handling is security/operations sensitive because site administrators rely on final properties to prevent application overrides.
- `Configuration` variable expansion also consults Java system properties, which can introduce surprising values if property names overlap.
- `DatanodeDescriptor` is public in this snapshot despite being documented as NameNode-internal. External use would couple callers to non-persistent, non-wire state.
- HFTP/HSFTP are documented as limited read-only filesystem implementations. Write-style methods are present because of `FileSystem` inheritance, but they should be expected to fail or be unsupported.
- Metrics APIs expose mutable public metrics fields. That is useful for internal updates but widens the compatibility surface and may allow misuse by external code.
- Fsck repair modes can move or delete corrupt files; tooling around `NamenodeFsck`/`DFSck` needs explicit operator intent and careful tests around open-file filtering and lost+found behavior.

## Test Signals

- JDiff/schema validation should confirm the XML remains well formed and conforms to `api.xsd`.
- API compatibility tests should compare this snapshot against neighboring Hadoop versions, especially for `Configuration`, `DistributedFileSystem`, `NameNode`, `DataNode`, `DatanodeInfo`, `FSConstants`, and metrics MBeans.
- Configuration tests should cover resource override order, final parameters, variable expansion from configuration and system properties, typed parse defaults on invalid values, range parsing, class/interface checks, local path hashing, and quiet mode.
- HDFS protocol tests should cover writable serialization round trips for `DatanodeID`, `DatanodeInfo`, `LocatedBlocks`, and `UpgradeStatusReport`, plus data-transfer checksum header/value compatibility through `DataChecksum`.
- Filesystem tests should cover `DistributedFileSystem` path checking, block locations, create/open/delete/rename/mkdirs/list/status, replication, permissions/owner changes, safe mode behavior, and checksum-failure reporting.
- Daemon integration tests should exercise DataNode registration, heartbeat, block reports, scheduled block reports, block recovery/update metadata calls, NameNode version/request verification, and shutdown/join behavior.
- Administrative command tests should cover `Balancer` exit codes, `DFSAdmin` safe mode/refresh/finalize/metasave/upgrade commands, and `DFSck`/`NamenodeFsck` missing-block reporting and repair modes.
- HTTP integration tests should cover `ListPathsServlet`, `FileDataServlet`, `StreamFile`, `FsckServlet`, `GetImageServlet`, and the HFTP/HSFTP connection paths.
- Metrics tests should verify `doUpdates` publishes expected counters/rates, JMX MBean getters match underlying metric values, min/max reset works, and FSNamesystem capacity rounding/casting remains intentional.
