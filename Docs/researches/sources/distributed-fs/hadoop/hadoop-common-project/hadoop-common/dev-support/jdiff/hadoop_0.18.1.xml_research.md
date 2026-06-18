# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007265`: lines 1-6280, `Docs/researches/chunks/subset-b-007265_research.md`
- `subset-b-007266`: lines 6281-12462, `Docs/researches/chunks/subset-b-007266_research.md`
- `subset-b-007267`: lines 12463-18779, `Docs/researches/chunks/subset-b-007267_research.md`
- `subset-b-007268`: lines 18780-25021, `Docs/researches/chunks/subset-b-007268_research.md`
- `subset-b-007269`: lines 25022-31137, `Docs/researches/chunks/subset-b-007269_research.md`
- `subset-b-007270`: lines 31138-37297, `Docs/researches/chunks/subset-b-007270_research.md`
- `subset-b-007271`: lines 37298-43567, `Docs/researches/chunks/subset-b-007271_research.md`
- `subset-b-007272`: lines 43568-44778, `Docs/researches/chunks/subset-b-007272_research.md`

## Chunk Research

### subset-b-007265: lines 1-6280

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

### subset-b-007266: lines 6281-12462

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 6281-12462

## Scope

This chunk is a Hadoop 0.18.1 JDiff API XML segment. It begins inside `org.apache.hadoop.dfs.namenode.metrics.NameNodeStatistics`, includes the complete `NameNodeStatisticsMBean` interface, then covers `org.apache.hadoop.filecache.DistributedCache`, most of the public `org.apache.hadoop.fs` API surface, FTP and Kosmos/KFS filesystem adapters, and the start of `org.apache.hadoop.fs.permission` with `AccessControlException`. It ends at the opening marker for `FsAction`, whose declaration is outside this chunk.

Because the source is generated API XML, this document describes exported contracts, signatures, inheritance, serialization hooks, and behavior documented in Javadocs. Control-flow and state notes are inferred only from those public contracts.

## Purpose

The covered APIs form the core early Hadoop filesystem client layer. They define how code locates filesystem implementations, opens seekable streams, creates files and directories, lists and globs paths, copies between local and remote filesystems, exposes block locations, preserves metadata, tracks I/O statistics, and adapts local, archive, FTP, in-memory, and KFS stores behind the same `FileSystem` abstraction.

The chunk also includes MapReduce-era distributed cache support for shipping read-only files, archives, and classpath resources to task nodes, plus NameNode JMX counters for startup, journal, block report, and operation metrics.

## Important APIs, Types, and Functions

`NameNodeStatistics` is partially visible. The visible methods expose the JMX implementation constructor, `shutdown()`, min/max/average/count getters for block reports, journal transactions, and journal syncs, startup metrics for safemode and FSImage load time, min/max reset, and operation counters for creates, deletes, adds, listings, block-location lookups, and renames. `getNumFilesListed()` is deprecated in favor of `getNumGetListingOps()`.

`NameNodeStatisticsMBean` is the public JMX management interface for NameNode runtime statistics. Its documented metrics are interval-based where applicable, with configuration notes for metrics contexts that perform periodic update calls. It references `FSNamesystemMBean` for status information outside this stats surface.

`DistributedCache` is a static utility for MapReduce application resources. `getLocalCache()` localizes a URI as a file or archive, validates the original modification timestamp, optionally unzips/unjars/untars archives, and can create symlinks in a task working directory. Configuration mutators and accessors cover cache files, cache archives, localized paths, timestamps, classpath additions, symlink enablement, URI conflict checks, `releaseCache()`, and `purgeCache()`.

Core metadata types include `BlockLocation`, `ContentSummary`, and `FileStatus`. `BlockLocation` is `Writable` state for hostnames, host:port names, file offset, and length. `ContentSummary` is `Writable` state for total content length, file count, directory count, and quota output formatting. `FileStatus` is `Writable` and `Comparable`, carrying file length, directory flag, replication, block size, modification time, permission, owner, group, and path; equality and hash code are path-based.

`FileSystem` is the central abstract API. It extends `Configured` and implements `Closeable`. Static factory and configuration methods include `get(Configuration)`, `get(URI, Configuration)`, deprecated `getNamed()`, `getLocal()`, `parseArgs()`, default URI getters/setters, `closeAll()`, and synchronized statistics lookup/printing. Instance methods define URI identity, path qualification/checking, block locations, `open()`, many `create()` overloads, `append()`, replication, rename, recursive/non-recursive delete, `deleteOnExit()`, existence/type/length/content-summary checks, `listStatus()` and `globStatus()`, home and working directories, `mkdirs()`, local copy/move helpers, local output staging, `close()`, usage/default block/default replication, file status, permissions, and ownership.

`FileSystem.Statistics` tracks bytes read and bytes written through increment and getter methods. `FileSystem.statistics` is a protected final field on each filesystem instance, and the static statistics registry is keyed by filesystem class.

Stream interfaces and wrappers define random-access and sync behavior. `Seekable` has `seek()`, `getPos()`, and `seekToNewSource()`. `PositionedReadable` has positional `read()` and `readFully()` overloads. `Syncable` declares `sync()`. `FSInputStream` combines `InputStream`, `Seekable`, and `PositionedReadable`; `BufferedFSInputStream` adds buffering around an `FSInputStream`; `FSDataInputStream` wraps an input stream as `DataInputStream` while delegating seek and positional reads. `FSDataOutputStream` wraps output as `DataOutputStream`, exposes `getPos()`, statistics-aware construction, wrapped stream access, close, and `sync()`.

Checksum support is split across `ChecksumException`, `ChecksumFileSystem`, `FSInputChecker`, and `FSOutputSummer`. `ChecksumFileSystem` wraps a raw filesystem and creates companion checksum files, calculates checksum-file lengths, filters checksum files from listings, keeps checksum and data files in sync across create/rename/delete/copy operations, and reports checksum failures. `FSInputChecker` verifies checksums chunk-by-chunk while reading and seeking. `FSOutputSummer` generates checksums before writing chunks to an underlying stream.

Utility APIs include `DF` and `DU` for shell-backed disk space and disk usage, `FileUtil` for recursive delete, filesystem copy, copy-merge, shell path conversion, local `du`, archive extraction, symlink/chmod, temp-file creation, and replace-file operations, plus `FileUtil.HardLink` for hardlink creation and link-count retrieval. `FsShell` provides command-line access to a `FileSystem` as a `Tool`, and `FsUrlStreamHandlerFactory` installs URL handlers backed by `FileSystem`.

Filesystem implementations and wrappers include `FilterFileSystem`, `HarFileSystem`, `InMemoryFileSystem`, `LocalDirAllocator`, `LocalFileSystem`, `RawLocalFileSystem`, `FTPFileSystem`, `FTPInputStream`, and `KosmosFileSystem`. `FilterFileSystem` delegates to an underlying `FileSystem`. `HarFileSystem` exposes Hadoop Archive contents as a read-oriented filesystem backed by `_masterindex`, `_index`, and `part-*` files. `InMemoryFileSystem` is a checksum filesystem for bounded `ramfs://` data with pre-reserved file and checksum space. `LocalDirAllocator` round-robins writes across configured local directories and searches them for reads. `LocalFileSystem` adds client-side checksums over `RawLocalFileSystem`; `RawLocalFileSystem` maps paths to `java.io.File`. `FTPFileSystem` uses Apache Commons Net FTP and has an explicit warning that input streams must be closed before other APIs are used. `KosmosFileSystem` adapts KFS and exposes block locations, locks, releases, local copy staging, and standard filesystem operations.

`Path` is the URI-backed path type with constructors for parent/child and scheme/authority/path combinations. It exposes `toUri()`, `getFileSystem()`, `isAbsolute()`, name/parent/suffix operations, string/equality/hash/compare/depth, qualification, and constants `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`. `PathFilter` is the predicate interface used by listing, globbing, local allocator, and in-memory filesystem selection.

`Trash` implements Hadoop's user trash behavior. It moves files into `.Trash/current` under the user's home directory while preserving original paths, creates checkpoints, expunges old checkpoints, and provides a superuser-oriented emptier runnable.

`AccessControlException` is an `IOException` subclass for permission failures, with a no-arg constructor needed for unwrapping from `RemoteException` and a message constructor.

## Control Flow

NameNode metrics flow from daemon-internal counters into `NameNodeStatistics`, then out through `NameNodeStatisticsMBean` via JMX. Interval metrics depend on a metrics context that periodically updates averages; `resetAllMinMax()` resets accumulated extrema.

Distributed cache flow starts when client code records file/archive URIs, timestamps, classpath entries, and symlink settings into a job `Configuration`. During task setup, localization calls resolve the URI through `FileSystem`, compare the DFS modification time to the job-time timestamp, copy the resource to a base cache directory if needed, unpack archives based on extension, record local paths, and optionally create symlinks in the task working directory. `releaseCache()` decrements or releases use of a localized cache, while `purgeCache()` deletes backing files during server reinitialization.

`FileSystem.get(URI, Configuration)` chooses an implementation from the URI scheme via the `fs.<scheme>.class` configuration key, constructs it, and calls `initialize()`. Caller operations then usually pass through convenience overloads into abstract primitives implemented by concrete filesystems. For example, simple `create()` overloads fill in default overwrite, buffer size, replication, block size, permission, and progress values before reaching the full abstract `create(Path, FsPermission, boolean, int, short, long, Progressable)`.

Listing and globbing flow through `FileStatus`. `listStatus()` returns status objects for paths and can apply a `PathFilter`. `globStatus()` interprets shell-like pattern operators (`?`, `*`, character classes, negated classes, escapes, and brace alternation), sorts results by path, returns `null` when a non-glob path does not exist, and returns an empty array when a glob has no matches.

Checksum filesystem flow wraps raw file operations. Opening a file creates a stream that reads data and checksum sidecar data; reads verify chunks and can raise `ChecksumException` with a bad position. Creating a file writes data through checksum generation and writes a matching checksum file. Rename, delete, copy, and list operations must keep checksum sidecar files aligned with user-visible files and hide checksum files where appropriate.

HAR flow initializes one `HarFileSystem` per archive URI, maps `har://` URIs to an underlying filesystem archive path, reads the master index to find ranges in the sorted index, then resolves file status, child listing, block locations, and open operations against part-file offsets. The open path returns a stream that fakes EOF at the archived member boundary.

Local allocation flow in `LocalDirAllocator` uses a context configuration key such as `mapred.local.dir`. For writes it round-robins from the last selected configured directory, checks writability and optionally available space, creates parents or temp files, and returns the chosen local path. For reads it scans all configured directories until the requested relative path exists.

FTP flow is more serialized than normal filesystem flow. The class documentation states that an input stream obtained from `open()` must be closed before using other APIs or later calls will block, implying a single active FTP data connection constraint.

## State and Persistence Behavior

The XML file is generated API metadata and has no runtime state, but many exposed APIs are stateful.

`DistributedCache` persists job resource declarations in `Configuration`: cache file/archive URIs, localized paths, timestamps, symlink settings, and classpath entries. Localized cache content persists on worker local disks until released, evicted, or purged. The timestamp contract assumes cached source files are read-only for the duration of the job.

`FileSystem` instances hold configuration, URI identity, working directory state in implementations, optional delete-on-exit registrations, and class-keyed byte statistics. `close()` releases held locks/resources, and `closeAll()` closes cached instances. `FSDataInputStream`, `FSDataOutputStream`, `FTPInputStream`, `FSInputChecker`, and `FSOutputSummer` track stream position, buffers, checksum state, and wrapped native/network resources.

`Writable` metadata types (`BlockLocation`, `ContentSummary`, `FileStatus`) serialize through `DataOutput`/`DataInput`. This makes their field order and default/null handling compatibility-sensitive for RPCs and stored metadata using Hadoop writable serialization.

`ChecksumFileSystem` persists extra checksum files alongside data files, so every data mutation has a sidecar consistency requirement. `LocalFileSystem.reportChecksumFailure()` moves corrupt local files to a bad-file directory on the same device so their storage is not reused.

`HarFileSystem` is read mostly from immutable archive files. Its namespace and file metadata are derived from archive index files rather than full per-file persisted permissions; Javadocs state returned permissions are those of archive index files because permissions are not persisted when creating a Hadoop archive.

`InMemoryFileSystem` stores file data in process memory and requires callers to reserve space, including checksum space, before creating files. It tracks total filesystem size, number of files, selected paths, and percent used.

`LocalDirAllocator` keeps JVM-local allocator state per context, including the last directory selected for round-robin allocation. It does not handle disks becoming read-only or full while a file is already being written.

`Trash` persists moved files under `.Trash/current` plus checkpoint directories. Its design avoids requiring full trash enumeration, filesystem date support, or synchronized clocks.

## Dependencies and Integration Points

The chunk integrates `org.apache.hadoop.conf.Configuration`, `Configured`, `org.apache.hadoop.util.Tool`, `Progressable`, `Shell`, Hadoop `Writable` serialization, `org.apache.hadoop.fs.permission.FsPermission`, `java.net.URI`, `java.net.URLStreamHandlerFactory`, `java.io` streams/files, `java.util.zip.Checksum`, and Apache Commons Logging.

MapReduce integration appears through `DistributedCache` documentation and APIs referencing `JobConf`, `JobClient`, `Mapper`, `Reducer`, `OutputCollector`, and `Reporter`. The cache is a bridge between job configuration, HDFS or HTTP resources, local task working directories, archive utilities, symlink creation, and task classpaths.

Filesystem implementation selection is configuration-driven through `fs.<scheme>.class`. Concrete schemes represented here include local/raw local, HAR, in-memory `ramfs://`, FTP via Apache Commons Net, and KFS/Kosmos. DFS and DistributedFileSystem are referenced as integration targets but their declarations are outside this chunk.

Shell integration is substantial in this early API: `DF`, `DU`, `ShellCommand`, `FileUtil.symLink()`, `FileUtil.chmod()`, `RawLocalFileSystem.setOwner()`, and `RawLocalFileSystem.setPermission()` all expose behavior backed by platform commands.

JMX and metrics integration is represented by `NameNodeStatisticsMBean`; URL integration by `FsUrlStreamHandlerFactory`; CLI integration by `FsShell` and its `Tool` implementation; IPC/remote exception integration by `AccessControlException`'s no-arg constructor.

## Risks and Edge Cases

This is an old Hadoop public API snapshot with several deprecated methods. Deprecated surfaces include `NameNodeStatisticsMBean.getNumFilesListed()`, `FileSystem.getName()`, `FileSystem.getNamed()`, path-based `getFileBlockLocations(Path, long, long)`, `FileSystem.getBlockSize()`, `RawLocalFileSystem.getName()`, `RawLocalFileSystem.lock()/release()`, `ShellCommand`, and single-argument delete methods in some implementations. Compatibility code may still depend on them.

Distributed cache correctness depends on stable source modification times and unique URI fragments when symlinks are enabled. Missing fragments, duplicate fragments, mutation of source files while a job is running, archive extraction failures, path traversal in archives, and aggressive `purgeCache()` can all affect task correctness or local disk safety.

`FileSystem` factories and caches can leak resources if callers hold instances past `closeAll()` or use closed cached filesystems. `deleteOnExit()` can accumulate state in long-lived JVMs. `setOwner()` explicitly rejects both username and group being null.

Glob and listing behavior has subtle null-versus-empty semantics, sorted result expectations, checksum-file filtering, and filter ordering. Tests and callers must distinguish nonexistent literal paths from unmatched glob patterns.

Checksum sidecar files create consistency risk: a data file copied, renamed, deleted, or listed without matching checksum handling can produce false checksum failures or expose internal `.crc`-style files. Checksum verification can raise during `read()`, `skip()`, or `seek()` because those operations may touch the target chunk.

`FSInputStream.seek()` says it cannot seek past EOF, while `FSInputChecker.seek()` allows seeking past EOF and returns `-1` on later read. Implementations and callers need to preserve the more specific contract for the concrete stream type they use.

`HarFileSystem` is not a general writable filesystem. Many mutating operations are documented as not implemented, and permissions returned from archive members do not reflect original per-file permissions. Creating one filesystem instance per `Path.getFileSystem()` call is explicitly warned against for HAR archives.

`LocalDirAllocator` does not protect against a disk becoming full or read-only after allocation. It also relies on JVM-local context singletons, so stale configuration or context reuse can affect later allocations.

FTP support has blocking hazards if streams are left open before later filesystem calls. It also lacks append support and depends on FTP server semantics for rename, delete, directory listing, and status details.

KFS and FTP adapters expose the common `FileSystem` contract over external systems whose replication, block locations, locks, permissions, and local copy semantics may diverge from HDFS behavior.

Shell-backed utilities are OS-sensitive. Javadocs mention Linux, FreeBSD, Cygwin, and Windows XP support in specific places, so command output parsing, symlink support, chmod/chown behavior, and hardlink counts need platform-specific validation.

## Test Signals

NameNode metrics tests should verify JMX registration/shutdown, interval counters, min/max reset, deprecated and replacement listing counters, safemode and FSImage load times, and behavior when no updating metrics context is configured.

Distributed cache tests should cover configuration round trips for files, archives, timestamps, classpath entries, localized paths, symlink flags, fragment conflict detection, timestamp mismatch rejection, cache reuse versus copy, archive extraction for `.zip`, `.jar`, `.tar`, `.tgz`, and `.tar.gz`, `releaseCache()`, and guarded `purgeCache()`.

Core `FileSystem` tests should exercise scheme-based implementation loading, default URI handling, cached instance close/closeAll behavior, path qualification/checking, all create/open/append overload paths, overwrite behavior, recursive and non-recursive delete, delete-on-exit processing, rename semantics, permissions and owner changes, content summaries, block locations, home and working directory resolution, and statistics increments for bytes read/written.

Listing and glob tests should verify path filters, multi-path listings, checksum-file exclusion, sort order, literal-missing `null`, glob-no-match empty array, escaping, character classes, negation, ranges, and nested brace expansion.

Writable metadata tests should round-trip `BlockLocation`, `ContentSummary`, and `FileStatus`, including empty hosts/names, quota output formatting, default permission/owner/group fallback, path-based equality, and compare ordering.

Checksum tests should cover checksum filename detection, checksum length calculations, create/open round trips, sidecar rename/delete/copy behavior, listing filters, `reportChecksumFailure()`, corrupted data and corrupted checksum streams, seek/skip across chunk boundaries, EOF behavior, and `FSOutputSummer` direct-write versus buffered chunk paths.

Stream tests should verify seek, position, positioned read, `readFully()` short-read handling, `seekToNewSource()`, sync delegation, statistics-aware output streams, closed-stream behavior, and mark/reset unsupported behavior where declared.

Utility tests should cover `DF` and `DU` parsing on supported platforms, refresh thread start/shutdown, manual inc/dec usage accounting, recursive delete partial failure, filesystem-to-filesystem copy and copy-merge, local-to-remote and remote-to-local copy, archive extraction, symlink/chmod exit codes, hardlink creation/link counts, temp-file delete-on-exit, and replace-file failure handling.

Implementation-specific filesystem tests should cover `FilterFileSystem` delegation, `HarFileSystem` index lookup and read-only operation failures, `InMemoryFileSystem.reserveSpaceWithCheckSum()` success/failure and percent-used accounting, `LocalDirAllocator` round-robin and space-aware selection, `LocalFileSystem` checksum failure quarantine, `RawLocalFileSystem` path-to-file conversion and shell-backed owner/permission changes, FTP open-stream blocking constraints and unsupported append, and KFS block locations/locks/replication behavior.

`Path`, `PathFilter`, `FsShell`, `FsUrlStreamHandlerFactory`, `Trash`, and `AccessControlException` tests should cover URI constructors and normalization, parent/name/suffix/depth/qualification, filter acceptance wiring, shell initialization/run/close and byte formatting helpers, URL handler creation only for known schemes, trash disabled/already-in-trash returns, checkpoint/expunge/emptier behavior, and remote-exception unwrapping of access-control failures.

## Cross-Chunk Notes

The chunk starts mid-`NameNodeStatistics`; its class declaration and any earlier fields or methods are in the preceding chunk. The final report should merge this with the previous NameNode metrics chunk for a complete description of the implementation class.

The chunk ends before `FsAction`; the permission enum/action API and likely `FsPermission` details are in a following chunk, even though many APIs here depend on `FsPermission`.

Several referenced types are declared outside this chunk, including `DistributedFileSystem`, `FSNamesystemMBean`, `FsPermission`, `Progressable`, `Shell`, `Tool`, MapReduce `JobConf` and mapper/reducer types, and KFS/FTP implementation internals. The merge lane should connect those declarations to this filesystem API surface.

### subset-b-007267: lines 12463-18779

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 12463-18779

## Scope

This chunk is a JDiff API description for Hadoop Common 0.18.1. It is generated API metadata, not executable Java source. It records public API names, inheritance, visibility, method parameters, checked exceptions, deprecation state, fields, and Javadoc-derived contracts.

The slice begins inside `org.apache.hadoop.fs.permission`, covering the tail of `FsAction` plus `FsPermission` and `PermissionStatus`. It then covers the old block-based S3 filesystem API in `org.apache.hadoop.fs.s3`, the native-object S3 filesystem entry point in `org.apache.hadoop.fs.s3native`, the early filesystem shell command helpers in `org.apache.hadoop.fs.shell`, and a large portion of `org.apache.hadoop.io`. The `org.apache.hadoop.io` part starts at `AbstractMapWritable`, includes many core `Writable` primitives, buffers, stringification, `MapFile`, `SequenceFile`, `SetFile`, `SortedMapWritable`, and `Text`, and ends inside the deprecated `UTF8` class.

Because this is API XML, the control-flow notes below describe documented public contracts, object lifecycle, serialization shape, and extension points inferred from signatures and Javadocs. Adjacent chunks are required for complete package coverage, especially for the beginning of `FsAction`, any nested enum constants omitted by JDiff presentation, and the tail of `UTF8`.

## Purpose

The chunk captures several foundational Hadoop Common APIs from the 0.18.1 era:

- Permission model value types for filesystem metadata: `FsAction`, `FsPermission`, and `PermissionStatus`.
- Two S3 filesystem models: a Hadoop-specific block/inode store (`org.apache.hadoop.fs.s3.S3FileSystem`) and a native S3 object store filesystem (`org.apache.hadoop.fs.s3native.NativeS3FileSystem`).
- Early `fs` shell command support for command dispatch, option parsing, and the `-count` command.
- Hadoop's core binary serialization and file container APIs: `Writable`, `WritableComparable`, raw comparators, reusable input/output buffers, arrays/maps of writables, primitive writable wrappers, `ObjectWritable`, `GenericWritable`, `DefaultStringifier`, `MapFile`, `SequenceFile`, and `Text`.

These APIs are central compatibility surfaces. The permission classes affect filesystem metadata persistence. The S3 classes define filesystem behavior over eventually remote object storage. The IO classes define on-disk file formats, MapReduce key/value serialization, sort order, raw comparator behavior, and configuration persistence of serialized objects.

## Important APIs, Types, and Functions

### Filesystem Permissions

`FsAction` is a public final enum for filesystem actions such as read and write. The visible API includes enum helpers `values()` and `valueOf(String)`, lattice-style operators `implies(FsAction)`, `and(FsAction)`, `or(FsAction)`, and `not()`, and public final fields `INDEX` and `SYMBOL` for octal and symbolic representations. It is the low-level action algebra used by permission bits.

`FsPermission` is a public mutable `Writable` value object for file and directory permission bits. It can be constructed from user/group/other `FsAction` values, from a `short` mode, or by copy. Important methods include `createImmutable(short)`, `fromShort(short)`, `toShort()`, `read(DataInput)`, `write(DataOutput)`, `readFields(DataInput)`, `getUserAction()`, `getGroupAction()`, `getOtherAction()`, `applyUMask(FsPermission)`, `getUMask(Configuration)`, `setUMask(Configuration, FsPermission)`, `getDefault()`, and `valueOf(String)` for Unix symbolic permissions such as `-rw-rw-rw-`. Public static fields `UMASK_LABEL` and `DEFAULT_UMASK` expose the configuration key and default mask.

`PermissionStatus` stores ownership and permission metadata. It implements `Writable`, is constructible from user name, group name, and `FsPermission`, and exposes immutable construction through `createImmutable(String, String, FsPermission)`. Accessors return user, group, and permission. `applyUMask(FsPermission)` delegates permission masking to `FsPermission`. It supports instance and static serialization helpers: `readFields(DataInput)`, `write(DataOutput)`, static `read(DataInput)`, and static `write(DataOutput, String, String, FsPermission)`.

### Block-Based S3 Filesystem

`org.apache.hadoop.fs.s3.Block` is a simple metadata value for data blocks stored by a `FileSystemStore`. It has an id and length, exposed through `getId()`, `getLength()`, and `toString()`.

`FileSystemStore` is the persistence abstraction behind the old Hadoop block-based S3 filesystem. It initializes from a `URI` and `Configuration`, exposes `getVersion()`, stores/retrieves/deletes `INode` and `Block` objects, checks inode/block existence, retrieves a block into a local `File` from a byte-range start, lists direct and deep subpaths, and includes test/diagnostic operations `purge()` and `dump()`.

`INode` holds file metadata for the block-based S3 layer: a file type and a list of `Block` pointers. It exposes `getBlocks()`, `getFileType()`, `isDirectory()`, `isFile()`, `getSerializedLength()`, `serialize()`, and static `deserialize(InputStream)`. Public static fields include `FILE_TYPES` and `DIRECTORY_INODE`. The API clearly separates metadata objects from data blocks.

`MigrationTool` is a `Configured` `Tool` for migrating old S3 filesystem data versions. Its Javadoc says migration rewrites block metadata and does not touch data files. Public entry points are `main(String[])`, `run(String[])`, and `initialize(URI)`.

`S3Credentials` extracts AWS credentials from a filesystem URI or `Configuration`. It has `initialize(URI, Configuration)`, `getAccessKey()`, and `getSecretAccessKey()`, with `IllegalArgumentException` documented when credentials cannot be determined.

`S3Exception` is an unchecked wrapper for Amazon S3 communication problems. `S3FileSystemException` is a checked fatal exception for `S3FileSystem`, and `VersionMismatchException` is raised when stored S3 filesystem data has an unreadable or incompatible version.

`S3FileSystem` extends `FileSystem` and implements Hadoop's block-based S3 filesystem. It can be constructed with the default store or an injected `FileSystemStore`, which is an important test seam. Public filesystem operations include `initialize(URI, Configuration)`, `getUri()`, deprecated-style `getName()`, working directory getters/setters, `mkdirs(Path, FsPermission)`, `isFile(Path)`, `listStatus(Path)`, `create(Path, FsPermission, boolean, int, short, long, Progressable)`, `open(Path, int)`, `rename(Path, Path)`, both old and recursive `delete` forms, and `getFileStatus(Path)`. `append()` is documented as unsupported, and permission parameters are documented as currently ignored.

### Native S3 Filesystem

`NativeS3FileSystem` extends `FileSystem` but stores files in their native S3 object form so other S3 tools can read them. It can be constructed with an injected `NativeFileSystemStore`, and its public operations mirror core filesystem behavior: `initialize`, `create`, `open`, `delete`, recursive `delete`, `getFileStatus`, `getUri`, `listStatus`, `mkdirs`, `rename`, `setWorkingDirectory`, and `getWorkingDirectory`. `append()` is unsupported. The public static `LOG` field uses Commons Logging.

The `listStatus(Path)` Javadoc is performance-significant: listing a file makes one S3 call, while listing a directory may make up to roughly `(n / 1000) + 2` S3 calls for `n` direct child files/directories. That exposes S3 pagination and cost/latency directly through the API contract.

### Filesystem Shell Helpers

`Command` is an abstract base for filesystem shell commands. It keeps protected `fs` and `args` state, requires `getCommandName()` and protected `run(Path)`, and provides `runAll()` to execute the command over every source path, returning `0` on success and `-1` on failure.

`CommandFormat` parses command arguments. Its constructor takes a command name, minimum/maximum parameter counts, and option names. `parse(String[], int)` returns non-option parameters from a starting position, and `getOpt(String)` reports whether an option was set.

`Count` extends `Command` for the `-count` shell command. It exposes static constants `NAME`, `USAGE`, and `DESCRIPTION`, static `matches(String)`, command name lookup, and protected path execution. The Javadoc says it counts directories, files, bytes, quota, and remaining quota.

### Core Writable Containers and Primitive Writables

`AbstractMapWritable` is an abstract `Writable` and `Configurable` base for `MapWritable` and `SortedMapWritable`. It keeps a per-instance class-id map rather than a static map, supporting nested map writables. Class ids range from 1 to 127, so a map instance can encode at most 127 distinct classes. Protected methods `addToMap(Class)`, `getClass(byte)`, `getId(Class)`, and synchronized `copy(Writable)` manage the registry. It also serializes/deserializes the class map and carries a `Configuration`.

`ArrayWritable` is a homogeneous writable array wrapper. It stores a value class, supports construction from a writable class, writable array, or `String[]`, and exposes `getValueClass()`, `toStrings()`, `toArray()`, `set(Writable[])`, `get()`, `readFields()`, and `write()`.

`TwoDArrayWritable` is the 2D version for `Writable[][]`, with class-based construction, `set`, `get`, `toArray`, and standard writable serialization.

The primitive writable wrappers in this chunk include `BooleanWritable`, `ByteWritable`, `IntWritable`, `LongWritable`, `FloatWritable`, and `DoubleWritable`. Each implements `WritableComparable`, provides default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. Their nested `Comparator` classes extend `WritableComparator` and compare serialized byte forms directly. `LongWritable` also exposes a `DecreasingComparator`.

`BytesWritable` is a resizable byte sequence usable as a key or value. It distinguishes logical size from backing capacity with `getSize()`, `setSize(int)`, `getCapacity()`, and `setCapacity(int)`. `get()` returns the backing bytes but only the range `0..getSize()-1` is valid. It supports copying from another `BytesWritable` or byte range, writable serialization, bytewise comparison, MD5-based hash behavior, equality, and hex-pair `toString()`. Its comparator is optimized for serialized bytes.

`NullWritable` is a singleton writable with no data. `get()` returns the single instance, serialization reads/writes no content, comparison is trivial, and its comparator is optimized for the empty serialized form.

`MD5Hash` is a `WritableComparable` wrapper around 16-byte MD5 digests. It can be constructed empty, from hex, or from raw bytes. It supports static and instance serialization, copying from another hash, raw digest access, digest construction from byte arrays, byte ranges, strings, and deprecated `UTF8`, plus `halfDigest()`, `quarterDigest()`, equality, ordering, hex conversion, and `setDigest(String)`. Public `MD5_LEN` defines the digest length, and the nested comparator compares serialized digests.

`MultipleIOException` aggregates multiple `IOException` instances. `getExceptions()` returns underlying exceptions and static `createIOException(List<IOException>)` creates a convenient wrapper or single exception.

### Buffers, Compression, Stringification, and Generic Object Wrappers

`CompressedWritable` is an abstract base for writables that store their serialized data compressed and inflate lazily. `readFields(DataInput)` and `write(DataOutput)` are final; subclasses implement `readFieldsCompressed(DataInput)` and `writeCompressed(DataOutput)`. Methods that access fields must call `ensureInflated()`.

`DataInputBuffer` is a reusable in-memory `DataInputStream`. It can be reset to a byte array and length or byte array, start, and length; accessors expose backing data, current position, and input length. Its purpose is avoiding repeated `DataInputStream` and `ByteArrayInputStream` allocation.

`DataOutputBuffer` is the writable counterpart over an in-memory buffer. Constructors support default and initial size. `getData()` returns the backing bytes valid only through `getLength()`. `reset()` clears the buffer and returns itself. `write(DataInput, int)` copies bytes directly from a `DataInput`.

`InputBuffer` and `OutputBuffer` are stream-level reusable buffers. `InputBuffer` extends `FilterInputStream` and resets over a byte array segment; `OutputBuffer` extends `FilterOutputStream`, exposes backing data/length, reset, and write support.

`DefaultStringifier<T>` implements `Stringifier<T>` using Hadoop serialization and base64. It obtains `Serializer` and `Deserializer` objects from `SerializationFactory`. Instance methods convert objects to/from strings and close resources. Static helpers `store`, `load`, `storeArray`, and `loadArray` persist serialized objects or arrays in `Configuration` keys. `storeArray` explicitly throws `IndexOutOfBoundsException` for an empty array.

`Stringifier<T>` is the interface for `toString(T)`, `fromString(String)`, and `close()`.

`GenericWritable` is an efficient wrapper for one of a fixed set of writable classes. Subclasses implement `getTypes()` to return the allowed classes. The serialized form stores a compact type id rather than writing a class name for every record. It implements `Configurable` and passes configuration to wrapped objects that are configurable before deserialization.

`ObjectWritable` is the general-purpose object wrapper. It stores a declared class and instance, supports `get()`, `getDeclaredClass()`, `set(Object)`, writable serialization, static `writeObject()` and `readObject()` helpers, and configuration propagation. Compared with `GenericWritable`, it is more flexible but more expensive because class declarations are serialized.

`RawComparator` extends the object comparator contract with `compare(byte[], int, int, byte[], int, int)` so Hadoop can compare serialized keys without deserializing them.

The deprecated `Closeable` interface simply extends `java.io.Closeable` and is marked "use java.io.Closeable".

### MapFile, ArrayFile, and SetFile

`MapFile` is a file-based sorted map from writable-comparable keys to writable values. Its storage is a directory containing a `data` file with all records and an `index` file containing a fraction of keys. Public constants `INDEX_FILE_NAME` and `DATA_FILE_NAME` expose those names. Static methods support renaming, deleting, command-line entry, and `fix(FileSystem, Path, Class, Class, boolean, Configuration)` to recreate a corrupt index and return the number of valid entries or `-1` if no repair is needed.

`MapFile.Reader` provides synchronized access to an existing map. It can be constructed with a filesystem/path string and configuration, or with a custom `WritableComparator`. Protected construction and `createDataFileReader()` let subclasses defer opening streams and specialize the `SequenceFile.Reader`. Important operations include `reset()`, `midKey()`, `finalKey(WritableComparable)`, `seek(WritableComparable)`, `next(WritableComparable, Writable)`, `get(WritableComparable, Writable)`, two `getClosest()` forms, and `close()`.

`MapFile.Writer` writes sorted map files. It has constructor overloads for key/value classes or a comparator, compression type, optional compression codec, and optional `Progressable`. It exposes instance and static `setIndexInterval`, `getIndexInterval()`, synchronized `append(WritableComparable, Writable)`, and synchronized `close()`. `append` requires each key to be greater than or equal to the previous key.

`ArrayFile` is a dense file-backed mapping from integer positions to values. Its `Reader` extends `MapFile.Reader` and adds `seek(long)`, `next(Writable)`, `key()`, and `get(long, Writable)`. Its `Writer` extends `MapFile.Writer` and appends values with implicit long keys.

`SetFile` is a file-backed sorted set built on `MapFile`. Its `Reader` exposes `seek(WritableComparable)`, `next(WritableComparable)`, and `get(WritableComparable)`. Its `Writer` appends keys and stores `NullWritable`-style values internally.

### MapWritable and SortedMapWritable

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`. It provides default and copy constructors, standard map operations (`clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`), plus `write` and `readFields` that include both the class registry and map entries.

`SortedMapWritable` is the sorted-key counterpart, extending `AbstractMapWritable` and implementing sorted map semantics over `WritableComparable` keys. It exposes `comparator()`, `firstKey()`, `lastKey()`, `headMap()`, `subMap()`, `tailMap()`, standard mutable map operations, and writable serialization.

### SequenceFile

`SequenceFile` is the key/value container format used heavily by Hadoop jobs and internal tooling. The top-level class exposes compression configuration helpers `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)`, multiple overloaded `createWriter()` factories, and public `SYNC_INTERVAL`.

The Javadoc describes a common header: magic bytes `SEQ` plus version, key class name, value class name, compression flags, optional compression codec, metadata, and a sync marker. It documents three record formats:

- Uncompressed: header, then records with record length, key length, key, value, and periodic sync markers.
- Record-compressed: same structure except values are compressed.
- Block-compressed: record blocks contain compressed key lengths, keys, value lengths, and values, with lengths encoded as zero-compressed integers.

`SequenceFile.CompressionType` is a public enum for compression modes used by `SequenceFile.Writer`.

`SequenceFile.Metadata` is a `Writable` map of `Text` keys to `Text` values. It supports default and `TreeMap<Text, Text>` construction, `get(Text)`, `set(Text, Text)`, metadata map access, writable serialization, equality, hash, and string conversion.

`SequenceFile.Reader` opens sequence files from `FileSystem`, `Path`, and `Configuration`. It exposes class-name and class-object getters for keys and values, compression flags and codec, metadata, close, synchronized typed iteration (`next(Writable)`, `next(Writable, Writable)`, `getCurrentValue(...)`), object-style `next(Object)`, raw iteration (`createValueBytes()`, `nextRaw`, `nextRawKey`, `nextRawValue`), `seek(long)`, `sync(long)`, `syncSeen()`, `getPosition()`, and `toString()`. `seek(long)` requires a position previously returned by `Writer.getLength()`; arbitrary positioning should use `sync(long)`.

`SequenceFile.ValueBytes` represents raw sequence-file values. It can write uncompressed bytes, write compressed bytes without recompressing uncompressed data, and report data size.

`SequenceFile.Writer` is a closeable writer with constructors for filesystem, configuration, path, key/value classes, optional progress, metadata, and replication/block-size parameters. It exposes key/value class and codec getters, `sync()`, `close()`, typed `append(Object, Object)`, `append(Writable, Writable)`, `appendRaw(byte[], int, int, ValueBytes)`, and `getLength()`. The public serializer fields `keySerializer`, `uncompressedValSerializer`, and `compressedValSerializer` reveal the serialization pipeline used for keys and values.

`SequenceFile.Sorter` sorts and merges sequence files. Constructors accept filesystem, key/value classes or a `RawComparator`, and configuration. Tunables include merge factor, memory bytes, and `Progressable`. Public workflows include sorting one or many input files, sorting and returning a raw iterator, merging by path arrays or `SegmentDescriptor` lists, cloning file attributes such as compression into an output writer, writing iterator records to a writer, and merging into an output file. Its Javadoc warns that key `readFields` implementations must avoid allocation for best performance.

`SequenceFile.Sorter.RawKeyValueIterator` iterates raw sorted key/value pairs and exposes current key as `DataOutputBuffer`, current value as `ValueBytes`, `next()`, `close()`, and `Progress`.

`SequenceFile.Sorter.SegmentDescriptor` describes a file segment by offset, length, and path. It is comparable and supports sync checks, preserving or deleting input, raw key/value iteration, stored key access, and cleanup. Default cleanup closes the file handle and deletes the file, but subclasses can override cleanup.

### Text and Deprecated UTF8

`Text` is Hadoop's standard UTF-8 string type. It implements writable-comparable behavior and stores raw UTF-8 bytes with an integer length encoded through zero-compressed format. Constructors accept empty, `String`, another `Text`, or byte array. It exposes raw bytes and length, byte-position `charAt(int)` returning Unicode scalar values or `-1`, `find(String)` and `find(String, int)` without converting the backing buffer to `String`, several `set` overloads, byte-range `append`, `clear`, `toString`, `readFields`, static `skip(DataInput)`, `write`, bytewise UTF-8 ordering, equality, hash, decoding/encoding helpers with optional malformed-input replacement, static `readString`/`writeString`, UTF-8 validation, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.

`Text.Comparator` is a serialized-byte comparator optimized for `Text` keys.

`UTF8` is deprecated and explicitly replaced by `Text`. The visible portion includes empty, `String`, and copy constructors; `getBytes()`, `getLength()`, `set(String)`, `set(UTF8)`, `readFields(DataInput)`, static `skip(DataInput)`, and the beginning of `write(DataOutput)`. The chunk ends before the class is complete.

## Control Flow and Lifecycle

Permission construction flows from symbolic/octal/user-group-other input into `FsPermission` instances. `toShort()` and `fromShort()` define the compact numeric representation, while `write()`/`readFields()` carry that representation through Hadoop serialization. `PermissionStatus` composes user, group, and permission and provides static write/read helpers for metadata records.

The old block-based S3 filesystem flow is metadata-first. `S3FileSystem.initialize()` configures a `FileSystemStore`, validates or reads store version, and uses `INode` entries to represent directories and files. File content is split into `Block` records, while path operations manipulate `INode` mappings and block references. Creating a file writes blocks and then inode metadata; opening a file retrieves inode metadata and streams blocks; deleting removes inode and block records. `MigrationTool` walks this metadata layer and rewrites block metadata without rewriting data files.

The native S3 filesystem flow maps Hadoop paths to native S3 keys. It does not use the block/inode store documented in `org.apache.hadoop.fs.s3`; instead, it exposes `FileSystem` operations around native objects and directory markers or prefix listings. Listing cost scales with S3 pagination, and append remains unsupported.

Filesystem shell commands follow a simple lifecycle. A concrete `Command` is constructed with a `FileSystem` and command arguments. `CommandFormat` parses options and operands. `runAll()` iterates source paths, calling the subclass's `run(Path)` for each path and collapsing success/failure into a process-style exit code.

Writable values use the standard Hadoop pattern: a no-argument constructor creates an empty instance, `readFields(DataInput)` mutates it in place from serialized data, and `write(DataOutput)` writes the current state. Primitive writables write fixed-width values. Variable-length structures such as `BytesWritable`, arrays, maps, `Text`, and `SequenceFile` records write lengths followed by bytes or nested writable payloads.

`AbstractMapWritable`-based maps first maintain and serialize a per-instance class-id registry, then serialize entries by compact class ids plus each key/value's writable payload. During deserialization, the class registry must be read before entries so ids can be resolved to classes.

`GenericWritable` writes a compact type discriminator for one of the subclass-declared types, then delegates serialization to the wrapped writable. `ObjectWritable` writes enough class information to reconstruct arbitrary supported object types and can pass configuration to configurable deserialized objects.

`MapFile` write flow requires sorted appends. The writer writes all records to the data sequence file and periodically writes index entries according to `indexInterval`. Reader flow loads the index into memory, uses the comparator to seek near a target key, and then scans the data file for exact or closest matches. `fix()` reconstructs the index from the data file when the index is corrupt or missing.

`SequenceFile` write flow starts with the header and sync marker, then appends records in one of the three documented compression formats. `Writer.getLength()` exposes positions suitable for later `Reader.seek()`. Reader flow validates the header, instantiates key/value classes and compression codec, then supports typed iteration, raw iteration, seeking to known writer positions, and syncing forward from arbitrary byte offsets.

`SequenceFile.Sorter` performs external sort/merge. It reads raw records through `SequenceFile.Reader`, buffers records up to configured memory, sorts using a `RawComparator`, spills intermediate segment files, and merges segments with a configurable fan-in. `RawKeyValueIterator` and `SegmentDescriptor` keep sort/merge paths mostly in serialized form to avoid excessive object allocation.

`Text` operations are mostly byte-level. Searches, comparisons, validation, and some traversal avoid constructing Java `String` objects. Serialization writes a zero-compressed byte length and then raw UTF-8 bytes.

## State and Persistence Behavior

The XML file itself has no runtime state, but it documents persistent formats and stateful APIs.

`FsPermission` and `PermissionStatus` are persisted into filesystem metadata via Hadoop `Writable` serialization. Compatibility depends on stable short-mode encoding, stable `FsAction` indices/symbols, and stable serialization order for user, group, and permission.

`S3FileSystem` persists a Hadoop-specific layout in S3: version information, path-to-`INode` metadata, and block objects identified by `Block` ids. That layout is not the same as ordinary S3 object storage and requires version checks and migration tooling. A failed create, rename, delete, or migration can leave orphaned blocks, stale inodes, or mismatched metadata if store operations are not atomic.

`NativeS3FileSystem` persists native S3 objects. Its directory behavior is inferred from path listings and possible directory markers rather than a traditional hierarchical filesystem namespace. Working directory is client-side state. Remote object storage persistence and list behavior dominate correctness.

`Command` instances hold mutable `args` state and a fixed `FileSystem` reference. `CommandFormat` holds parsed option state after `parse()`.

Reusable buffers (`DataInputBuffer`, `DataOutputBuffer`, `InputBuffer`, `OutputBuffer`) expose backing arrays directly. Callers must honor valid lengths and positions; subsequent resets or writes mutate the same backing storage.

`BytesWritable` distinguishes capacity from logical size. The backing array may contain undefined bytes beyond `getSize()`, and callers using `get()` must not persist or compare beyond the valid range.

`CompressedWritable` stores compressed bytes until `ensureInflated()` is called. This makes copy-through cheap but means field access has hidden inflation side effects.

`DefaultStringifier` persists serialized, base64-encoded object state inside `Configuration` values. Deserialization depends on the configured `SerializationFactory`, the stored class, and class availability at load time.

`MapWritable` and `SortedMapWritable` persist both data and their per-instance class registry. The 127-class limit is an explicit compatibility and capacity boundary for complex nested maps.

`MapFile` persists as a directory with separate `data` and `index` files. The data file is authoritative for `fix()`, while index size and lookup memory use are controlled by index interval.

`SequenceFile` persists a binary container with magic/version, class names, compression metadata, file metadata, sync marker, and records. Compatibility depends on stable serializers, writable implementations, compression codecs, sync marker handling, and class names embedded in the header.

`SequenceFile.Sorter` creates temporary segment files and may delete input files depending on `deleteInput` and `SegmentDescriptor.preserveInput`. Cleanup is stateful and can mutate the filesystem.

`Text` persists UTF-8 bytes with zero-compressed integer length. It can contain malformed input only when decode/encode calls choose replacement behavior; validation methods explicitly reject invalid UTF-8 with `MalformedInputException`.

`NullWritable` is singleton state in memory and zero bytes on disk.

## Dependencies and Integration Points

The permission APIs integrate with `org.apache.hadoop.conf.Configuration`, filesystem metadata, `FileStatus`, and `DataInput`/`DataOutput` writable serialization.

The S3 APIs integrate with `FileSystem`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `Progressable`, `FsPermission`, Java `URI`, local temporary `File` objects, and AWS S3 stores. `S3FileSystem` depends on the `FileSystemStore` abstraction; `NativeS3FileSystem` depends on `NativeFileSystemStore` outside this chunk. Credential loading bridges URI authority/user-info and Hadoop configuration.

Filesystem shell helpers integrate with the broader `FsShell` command layer outside this chunk, the configured `FileSystem`, and path/status quota APIs.

The IO APIs are the core integration point for MapReduce, HDFS metadata, RPC payloads, sequence/map/set file storage, sorting, configuration serialization, and user-defined key/value types. They depend on Java IO, collections, `Configuration`, Hadoop serializers/deserializers, compression codecs, `Progressable`, filesystem paths and streams, and `WritableComparator`.

`RawComparator` and the nested primitive comparators are performance integration points for Hadoop sorting and grouping: they let sort code compare serialized bytes without object allocation. `SequenceFile.Sorter` and `MapFile.Reader` depend on those comparators for ordering.

`DefaultStringifier` integrates with `SerializationFactory`, `Serializer`, and `Deserializer`, allowing arbitrary serializable Hadoop objects to be embedded in configuration. This is useful for job setup but creates compatibility coupling to configured serialization implementations.

`ObjectWritable` and `GenericWritable` are integration points for heterogenous value types. `GenericWritable` is more efficient for known finite type sets, while `ObjectWritable` is broader and used by RPC-like or generic serialization paths.

`MapFile`, `ArrayFile`, and `SetFile` integrate `SequenceFile` storage with `FileSystem` paths. `MapFile` also integrates with command-line repair via `main(String[])`.

`Text` integrates with `SequenceFile.Metadata`, string serialization utilities, key sorting, and all writable APIs that need stable UTF-8 behavior. `UTF8` remains for backward compatibility but is deprecated in favor of `Text`.

## Risks and Edge Cases

This source is generated API XML. It gives the public contract but not implementation internals, private fields, enum constants, or all nested helper classes. Implementation-specific research should be reconciled with the Java sources if code changes are planned.

The slice starts mid-`FsAction` and ends mid-`UTF8`, so adjacent chunk reconciliation is required for complete class documentation.

`FsPermission.valueOf(String)` expects Unix symbolic strings. Incorrect string length, file-type prefix handling, or invalid symbols are likely input-validation risks. Umask parsing through `Configuration` can also cause broad filesystem behavior changes.

Permission parameters in the S3 filesystems are documented as ignored in some operations. Callers expecting POSIX-like permission enforcement on S3 will get misleading metadata or no enforcement.

The old `S3FileSystem` stores data in Hadoop-specific blocks and inodes, so it is not directly interoperable with native S3 tools. Version mismatch handling and migration are critical. Metadata/data updates are likely non-atomic over S3, so rename, delete, and create can leave partial state after failures.

`NativeS3FileSystem` is interoperable with S3 tools but inherits object-store limitations. Append is unsupported, rename may require copy/delete semantics, and list status cost grows with remote pagination. Directory behavior may not match hierarchical filesystems.

`S3Credentials` can source secrets from URI or configuration; URI-embedded credentials risk leaking through logs, diagnostics, or stringified URIs.

`Command.runAll()` returns a coarse success/failure code. If a multi-path command partially succeeds, callers need diagnostics outside the return code.

`AbstractMapWritable` has a hard 127 distinct-class limit per map instance. Complex nested maps can exceed this unexpectedly.

Reusable buffers and byte writables expose backing arrays directly. Misusing `getData()` or `get()` beyond valid length can leak stale bytes, corrupt comparisons, or write unintended data.

`BytesWritable` capacity changes preserve current data but new bytes are undefined. Tests should avoid assuming zero-fill after growth.

`CompressedWritable` requires subclasses and field accessors to call `ensureInflated()`. Missing that call can read stale compressed state rather than real fields.

`DefaultStringifier` stores base64 serialized blobs in configuration. Empty arrays are explicitly invalid for `storeArray`, and deserialization can fail if serializers, classes, or configuration differ between store and load.

`GenericWritable` only works for classes declared by `getTypes()`. Unknown type ids, changed type order, or removed classes break compatibility. `ObjectWritable` is more flexible but serializes class names frequently and is more expensive.

`MapFile.Writer.append()` requires nondecreasing sorted keys. Out-of-order writes corrupt the map's searchable contract. Large index intervals reduce memory use but increase seek scan cost; small intervals increase index memory use.

`MapFile.Reader` reads the index into memory, so large or heavy key objects can cause high memory pressure. Its synchronized methods provide per-reader serialization but not necessarily safe external mutation of key/value instances supplied by callers.

`SequenceFile` embeds class names and compression codec names in headers. Renaming classes, changing serializers, or removing codecs can make old files unreadable. Raw APIs require exact handling of key/value lengths and compression state. `seek()` is only safe for positions emitted by `Writer.getLength()`, while arbitrary offsets must use `sync()`.

`SequenceFile.Sorter` performance depends heavily on efficient key deserialization and raw comparison. It may delete input or temporary files, so failure handling must protect caller data when `deleteInput` is true.

Block-compressed sequence files encode key/value lengths with zero-compressed integers. Bugs in length decoding can desynchronize the rest of a block.

`Text.charAt(int)` and `find(String, int)` use byte positions, not Java UTF-16 character indexes. Callers can get `-1` for invalid positions or trailing bytes. `bytesToCodePoint(ByteBuffer)` advances the buffer position and changes marks, which can surprise callers reusing the buffer.

`Text.decode(..., replace)` changes error behavior based on the `replace` flag. Tests must cover both replacement and exception behavior for malformed UTF-8.

`UTF8` is deprecated, so new code should avoid adding dependencies on it except for compatibility with old serialized data.

## Test Signals

API compatibility tests should compare this JDiff XML against generated API for signature, visibility, checked exceptions, inheritance, public fields, deprecation state, and Javadoc-sensitive contracts.

Permission tests should cover `FsAction` boolean algebra, octal and symbolic representations, `FsPermission` short round trips, symbolic `valueOf`, umask get/set through `Configuration`, `applyUMask`, default permissions, immutable creation, equality/hash behavior, and `PermissionStatus` serialization including user/group strings.

Block-based S3 tests should use an injected `FileSystemStore` to exercise initialize/version checks, inode and block storage, create/open round trips, byte-range block retrieval, directory listing, recursive and non-recursive delete, rename, migration rewriting metadata without touching block files, version mismatch exceptions, unsupported append, ignored permission parameters, `purge`, and `dump`.

Native S3 tests should cover native object create/open/delete/list, recursive delete, directory marker or prefix behavior, working directory resolution, rename semantics, unsupported append, injected `NativeFileSystemStore`, URI handling, file status for files versus directories, and listing pagination/call-count behavior around 1000-key boundaries.

Credential tests should cover URI-provided credentials, configuration-provided credentials, missing credentials raising `IllegalArgumentException`, and secret redaction in any diagnostics outside the API.

Shell command tests should cover `CommandFormat` minimum/maximum operands, option parsing from arbitrary start positions, unknown/duplicate options, `getOpt`, `Command.runAll()` success/failure aggregation across multiple paths, and `Count.matches()` plus count output for files, directories, quotas, and remaining quotas.

Primitive writable tests should round-trip every primitive wrapper through `write`/`readFields`, compare object and raw comparator ordering, verify equality/hash/toString, and include negative, zero, boundary, NaN, and signed byte cases where relevant.

`BytesWritable` tests should cover size versus capacity, growth and shrink behavior, copying from byte ranges, serialized comparator ordering, equality over logical size only, hex string output, and stale bytes beyond logical size not participating in comparison.

Buffer tests should cover `DataInputBuffer` and `InputBuffer` reset with offsets, position/length reporting, `DataOutputBuffer.write(DataInput, int)`, reset reuse, backing array validity only through length, and large writes that force capacity growth.

`CompressedWritable` tests should implement a small subclass and verify lazy inflation, final `readFields`/`write` behavior, subclass compressed read/write hooks, and field access after read.

`DefaultStringifier` tests should store/load single objects and arrays in `Configuration`, verify base64 content is present under the expected key, reject empty arrays, close serializers/deserializers, and fail clearly when classes or serializers are unavailable.

`GenericWritable` tests should verify allowed type serialization, type id stability, configuration propagation before deserialization, rejection of unsupported wrapped classes, and compatibility when `getTypes()` order is unchanged. `ObjectWritable` tests should cover declared class preservation, null instance handling, primitive/writable/object payloads supported by the implementation, static read/write helpers, and configuration propagation.

`MapWritable` and `SortedMapWritable` tests should cover class registry serialization, nested maps, copy constructors, the 127-class limit, sorted-key operations, standard map views, mutation after serialization, and interoperability with `WritableComparable` keys.

`MapFile` tests should write sorted records, reject or diagnose out-of-order appends, tune index interval, read exact keys, seek missing keys, get closest before/after, compute mid/final keys, close/reset behavior, rename/delete directories, repair missing or corrupt indexes with `fix()`, and verify index memory behavior with large key objects.

`ArrayFile` tests should verify implicit long keys, seek by index, next value iteration, and random get. `SetFile` tests should verify key-only append, membership lookup, seek, and next-key iteration.

`SequenceFile` tests should cover writer factory overloads, metadata round trips, uncompressed, record-compressed, and block-compressed formats, sync marker insertion, `Writer.getLength()` followed by `Reader.seek()`, arbitrary offset `sync()`, `syncSeen()`, typed and raw iteration, value byte compressed/uncompressed writes, codec absence or mismatch, class-name compatibility, and close behavior.

`SequenceFile.Sorter` tests should sort one and many input files, merge with different fan-in values, enforce memory limits enough to spill segments, preserve or delete inputs according to flags, report progress, clone compression attributes, write raw iterator records, clean up temporary segments, and use custom `RawComparator` without unnecessary key object allocation.

`Text` tests should cover UTF-8 encode/decode with and without replacement, malformed input validation, zero-compressed length serialization, byte-position `charAt`, byte-position `find`, append and clear, bytewise comparison, raw comparator ordering, `readString`/`writeString`, `skip`, `bytesToCodePoint` buffer-position side effects, and `utf8Length` for ASCII, multibyte, and surrogate-pair input.

`UTF8` compatibility tests should remain for reading old serialized values, skipping encoded data, and comparing behavior against `Text` where the visible API overlaps.

## Cross-Chunk Notes

The final per-file reconciliation should merge this chunk with adjacent chunks for the complete `org.apache.hadoop.fs.permission` package and the remainder of deprecated `org.apache.hadoop.io.UTF8`.

Several referenced types are outside this chunk: `Writable`, `WritableComparable`, `WritableComparator`, `SequenceFile` helper internals, `NativeFileSystemStore`, `CompressionCodec`, `SerializationFactory`, and the full `FileSystem` base class. This chunk documents how the visible APIs depend on them, but complete behavior requires their declarations and implementation sources.

The Hadoop 0.18.1 S3 APIs are historically important but differ from modern object-store filesystem contracts. Reconciliation should call out the difference between block-based `s3:` and native `s3n:` style storage when comparing across Hadoop versions.

### subset-b-007268: lines 18780-25021

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml - subset-b-007268

Chunk lines: 18780-25021.

## Purpose

This chunk is part of the Hadoop 0.18.1 JDiff XML API snapshot. It is not implementation code; it records public/protected API signatures, inheritance, implemented interfaces, deprecation metadata, checked exceptions, public fields, and embedded Javadoc for Hadoop common, IPC, logging, and old `mapred` APIs. The file is used by JDiff/dev-support tooling to compare Hadoop API surfaces across releases, so the source of truth here is the shape and documentation of API contracts rather than executable control flow.

The chunk starts in the tail of `org.apache.hadoop.io.UTF8`, continues through complete package sections for `org.apache.hadoop.io.compress`, `org.apache.hadoop.io.compress.lzo`, `org.apache.hadoop.io.compress.zlib`, `org.apache.hadoop.io.retry`, `org.apache.hadoop.io.serializer`, `org.apache.hadoop.ipc`, `org.apache.hadoop.ipc.metrics`, and `org.apache.hadoop.log`, then enters `org.apache.hadoop.mapred`. It ends inside the `JobConf` class immediately after the opening of `setOutputFormat`, so `JobConf` is only partially visible in this chunk.

## Important APIs, Types, and Contracts

### Hadoop IO serialization

- `UTF8.Comparator` is a `WritableComparator` optimized for serialized UTF8 keys. The surrounding `UTF8` tail shows string conversion, equality, hash, byte conversion, `readString(DataInput)`, and `writeString(DataOutput, String)`. `UTF8` is documented as deprecated in favor of `Text`, which is an API migration signal for any consumers still relying on old string writables.
- `VersionedWritable` implements `Writable` and requires `getVersion()`. Its `write(DataOutput)` and `readFields(DataInput)` contract stores/checks a version byte and may throw `VersionMismatchException`, giving older writable payloads an explicit compatibility hook.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length integers and longs. Their public API is the standard Hadoop writable shape: constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `Writable` defines the core serialization protocol: `write(DataOutput)` and `readFields(DataInput)`. Its Javadoc emphasizes reuse of existing storage during deserialization.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` and is documented as the expected key type for the old MapReduce framework.
- `WritableComparator` is the core comparator registry and byte-level comparison utility. It has synchronized static `get(Class)` and `define(Class, WritableComparator)` registry methods, object and raw byte comparison overloads, and byte parsing helpers such as `compareBytes`, `hashBytes`, `readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, and `readVInt`.
- `WritableFactories`, `WritableFactory`, and `WritableName` provide construction and name-alias indirection for writable types, including support for non-public writable classes and class renaming without invalidating serialized files containing class names.
- `WritableUtils` collects serialization utilities: compressed byte/string arrays, string arrays, cloning via serialization, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, variable-length integer size/sign helpers, enum serialization via strings, and `skipFully`.

### Compression APIs

- `CodecPool` is a global compressor/decompressor pool for reusing potentially native codec objects. Its API is `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`.
- `CompressionCodec` defines the codec abstraction: creating compression/decompression streams with or without caller-supplied `Compressor`/`Decompressor`, discovering compressor/decompressor classes, creating codec-specific codec engines, and reporting a default filename extension.
- `CompressionCodecFactory` maps filename suffixes to codec instances. It is configured from `io.compression.codecs`, defaults to gzip and zip per the doc, exposes static `getCodecClasses`/`setCodecClasses`, `getCodec(Path)`, `removeSuffix`, and a small `main` test hook. It publishes a public static final `LOG`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases over protected final `in`/`out`. They force subclasses to implement byte-array `read`/`write`, `resetState`, and output `finish`, preventing accidental leakage to the underlying stream.
- `Compressor` and `Decompressor` are stateful, stream-oriented interfaces modeled after `java.util.zip.Deflater` and `Inflater`. They expose input buffers, dictionaries, finish/finished state, byte counters, `compress`/`decompress`, `reset`, and `end`.
- `DefaultCodec`, `GzipCodec`, and `LzoCodec` implement `CompressionCodec` and in some cases `Configurable`. `GzipCodec` includes protected static bridge stream classes wrapping deflater/inflater streams. `LzoCodec` exposes `isNativeLzoLoaded(Configuration)` and depends on native LZO availability.
- `LzoCompressor` and `LzoDecompressor` implement `Compressor`/`Decompressor` with synchronized mutable methods and strategy enums. They include native-loaded checks, direct-buffer-size constructors, byte counters, reset/end, and `finalize` on the decompressor.
- Zlib support includes Java built-in wrappers (`BuiltInZlibDeflater`, `BuiltInZlibInflater`) and native-capable `ZlibCompressor`/`ZlibDecompressor` with enum types for compression header, level, and strategy. `ZlibFactory` chooses native or built-in compressor/decompressor implementations from `Configuration`.

### Retry, serializer, and IPC APIs

- `RetryPolicies` is a factory and constants holder for immutable `RetryPolicy` implementations. It exposes fixed sleep, maximum time, proportional sleep, randomized exponential backoff, exception-class dispatch, remote-exception dispatch, `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`.
- `RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, return silently for void methods, or rethrow an exception. `RetryProxy.create` uses dynamic proxies to wrap an implementation with either one policy for all methods or a method-name-to-policy map.
- Serializer contracts are split into `Serializer<T>`, `Deserializer<T>`, `Serialization<T>`, and `SerializationFactory`. Serializers/deserializers are explicitly stateful but must not buffer across calls because other producers/consumers may interleave reads or writes on the same stream.
- `JavaSerialization`, `JavaSerializationComparator`, `DeserializerComparator`, and `WritableSerialization` bridge Hadoop's pluggable serialization system to Java `Serializable`, `Comparable`, `RawComparator`, and `Writable` contracts.
- `Client`, `Server`, `RPC`, `RPC.Server`, `RPC.VersionMismatch`, `RemoteException`, and `VersionedProtocol` describe the old Hadoop IPC/RPC layer. IPC calls pass and return `Writable` values; RPC protocols are Java interfaces with primitive, `String`, `Writable`, or array parameters/returns and should throw only `IOException`.
- `Client.call` supports single calls, user-ticket calls, and parallel batch calls to multiple addresses. `Server` exposes lifecycle (`start`, `stop`, `join`), listener/socket configuration, current server context, remote address helpers, queue/connection metrics, public `HEADER`/`CURRENT_VERSION`, and abstract `call(Writable, long)`.
- `RPC.getProxy`, `waitForProxy`, `stopProxy`, parallel `call`, and `getServer` create client proxies and server wrappers for `VersionedProtocol` implementations. `VersionedProtocol.getProtocolVersion` is the wire compatibility gate, with `RPC.VersionMismatch` carrying interface, client version, and server version.
- `RemoteException` wraps remote exception class names and can unwrap to specific lookup types or instantiate an `IOException`/`Throwable` with a string constructor when possible.

### Metrics, logging, and MapReduce APIs

- `RpcMetrics` implements `Updater`, publishes queue and processing time metrics, and registers JMX management. `RpcMgtMBean` exposes sampled RPC operation counts, average/min/max processing and queue times, reset, open-connection count, and call-queue length.
- `LogLevel` provides runtime log-level changes through a command-line `main` and a `LogLevel.Servlet` HTTP endpoint.
- `ClusterStatus` is a writable snapshot of old MapReduce cluster state, including task tracker counts, running map/reduce tasks, maximum capacities, state serialization, and textual representation.
- `Counters`, `Counters.Counter`, and `Counters.Group` are synchronized writable counter containers. Counters support enum and string group addressing, increment, lookup, summing, logging, compact string output, display names/localization, and a documented binary external format.
- `DefaultJobHistoryParser.parseJobTasks` populates a `JobHistory.JobInfo` object from a history log file on a `FileSystem`.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` model MapReduce configuration/input/output validation failures. `InvalidInputException` carries a list of `IOException` problems and synthesizes a message from them.
- `FileInputFormat<K,V>` is the base for file-based input formats. It validates/list statuses, computes splits from file blocks, supports path filters, manages input paths, and leaves `getRecordReader` abstract.
- `FileOutputFormat<K,V>` is the base for file-based output formats. It manages output compression configuration, output paths, per-task temporary work output paths, output-spec validation, and abstract record writer creation. Its documentation highlights speculative-execution side-file risks and the `_temporary/_${taskid}` promotion model.
- `FileSplit` is a writable `InputSplit` containing file path, byte start, byte length, and host locations. The constructor that takes `JobConf` is deprecated in favor of the host-list constructor.
- `ID` is the comparable/writable integer identifier base for `JobID`, `TaskID`, and `TaskAttemptID`.
- `InputFormat<K,V>` defines `validateInput`, `getSplits`, and `getRecordReader`; `InputSplit` defines `getLength`, `getLocations`, and extends `Writable`.
- `IsolationRunner.main` is a command-line hook to rerun failed tasks in isolation.
- `JobClient` is the primary old MapReduce client API. Visible methods cover construction, initialization/close, filesystem access, job submission by `JobConf` or job-file string, job lookup, map/reduce task reports, cluster status, job listing, blocking `runJob`, task output filtering, default map/reduce capacity lookup, system directory lookup, `Tool.run`, and `main`. Its documentation lays out the submission workflow: validate input/output, compute splits, set distributed-cache accounting, copy jar/config to the system directory, submit to `JobTracker`, then optionally monitor.
- `JobClient.TaskStatusFilter` is an enum represented by generated `values` and `valueOf`.
- `JobConf` begins here and is partial. Visible API covers constructors from default config, example class, `Configuration`, XML path/string, jar path resolution, local directories/files, deprecated old input/output path methods, user name, failed-task temporary file retention, task-file retention regexes, working directory, input/output format class accessors up to the start of `setOutputFormat`.

## Control Flow and Behavioral Semantics

Because this is a JDiff XML document, control flow is represented by API contracts and Javadoc rather than Java statements.

- Writable flow is `write(DataOutput)` followed by object reuse and `readFields(DataInput)`. `VersionedWritable` adds a leading version check, and variable-length integer utilities define byte-level encodings that consumers must read symmetrically.
- Raw comparator flow favors comparing serialized bytes first. `WritableComparator.compare(byte[],...)` falls back to deserializing two writable keys, then calling object comparison, unless subclasses override the raw comparator.
- Compression flow is push/pull state machine based: callers provide input when `needsInput()` is true, call `compress`/`decompress` into output buffers, signal `finish()`, check `finished()`, then `reset()` for reuse or `end()` to release resources. `CodecPool` makes this lifecycle reusable but requires explicit return of codec engines.
- Stream compression flow wraps caller streams in `CompressionInputStream`/`CompressionOutputStream`. Output streams must call `finish()` to flush codec trailers without necessarily closing the underlying stream; input streams can `resetState()` after repositioning underlying input.
- Retry flow is proxy-mediated. A failed method call is passed to `RetryPolicy.shouldRetry`; the result decides whether the proxy retries, returns for void-only silent policies, or rethrows.
- IPC/RPC flow is client proxy or writable call -> socket connection to `Server`/`RPC.Server` -> version/protocol checks for `VersionedProtocol` -> server `call` dispatch -> `Writable` response or `RemoteException`.
- MapReduce job flow in `JobClient` is explicitly documented: validate IO specs, compute splits, prepare distributed-cache metadata, copy the job jar/configuration into the distributed filesystem system directory, submit to `JobTracker`, and monitor through `RunningJob` or notification.
- File input flow lists `FileStatus` entries, optionally filters them, computes split sizes using target/min/block sizes, maps offsets to block indexes/locations, and creates `InputSplit` values consumed by `RecordReader`.
- File output flow validates destination paths, configures optional codec output, writes attempt output into a task-specific temporary path, then relies on framework promotion to final output for successful attempts.

## State and Persistence Behavior

- The XML itself persists public API state: class names, inheritance, method signatures, documentation, and deprecation strings. It is deterministic metadata for API comparison.
- `Writable` implementations persist object state to `DataOutput` and restore it from `DataInput`; versioned writables persist an implementation version byte.
- `WritableName` and `WritableFactories` hold static registries that affect deserialization/instantiation of named writable classes and non-public writable classes.
- Variable-length integer/string/compressed-array helpers define long-lived binary file and shuffle formats, so small encoding changes would break compatibility.
- Codec objects are mutable resources with internal buffers and optional native state. Pools, `reset`, and `end` are essential state-management boundaries.
- Serializer/deserializer instances are stateful around opened streams, but their contracts prohibit buffering that would hide bytes from other stream users.
- IPC client/server objects manage sockets, handler threads, call queues, connection counts, ping intervals, user tickets, and metrics.
- `RpcMetrics` persists runtime samples in metrics objects and publishes them through Hadoop metrics/JMX.
- MapReduce state appears in `JobConf` configuration properties, `ClusterStatus` snapshots, `Counters` binary payloads, `FileSplit` serialized split metadata, `JobClient` job submission artifacts, and filesystem output paths. `FileOutputFormat` documents persistence of side-effect files through attempt-specific temporary directories and promotion on success.

## Dependencies and Integration Points

- Java core APIs: `java.io` streams and `DataInput`/`DataOutput`, `java.net` sockets/addresses, `java.util` collections/comparators/enums, `java.util.concurrent.TimeUnit`, `java.util.zip` deflater/inflater, reflection `Method`, servlet APIs for log-level changes, and JMX/metrics interfaces.
- Hadoop common APIs: `Configuration`, `Configured`, `Configurable`, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `PathFilter`, `Progressable`, `UserGroupInformation`, metrics contexts/util classes, and Hadoop `Writable`/`RawComparator`.
- Native integration points: LZO and zlib codecs can use native libraries, with explicit `isNativeLzoLoaded` and `isNativeZlibLoaded` checks and built-in Java zlib fallback wrappers.
- MapReduce integration: `JobClient`, `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `Reporter`, `OutputFormat`, `RecordWriter`, `TaskReport`, `JobStatus`, `RunningJob`, `DistributedCache`, and `JobTracker` are linked by Javadoc and signatures.
- Tooling integration: as a `dev-support/jdiff` artifact, this XML integrates with API-diff generation rather than runtime Hadoop services.

## Risks and Edge Cases

- Boundary risk: this chunk starts in the middle/tail of `UTF8` and ends inside `JobConf`, so a final merged file report must combine adjacent chunks before claiming full API coverage.
- Compatibility risk: many APIs define binary formats (`Writable`, `Counters`, `FileSplit`, VInt/VLong, compressed arrays). Signature or encoding changes can break persisted Hadoop data, shuffle data, or RPC payloads.
- Native resource risk: LZO/zlib compressors and decompressors carry native/direct-buffer state; missed `reset`, `end`, or pool return can leak resources or corrupt reuse.
- Threading risk: many counter and codec methods are synchronized, but pool and registry APIs also expose shared mutable global state. Callers must respect object lifecycle and not share mutable compressors across concurrent streams unless designed for it.
- API deprecation risk: visible deprecated APIs include `UTF8`, `FileInputFormat.listPaths`, old `FileSplit(Path,long,long,JobConf)`, `InputFormat.validateInput`, `JobClient` string job-id overloads, several `JobConf` input/output path helpers, `JobConf.getSystemDir`, and numeric counter lookup. Later code should prefer the documented replacements.
- Documentation quality risk: several Javadocs contain typos or malformed escaped text, including `DataOuput`, `deseriablize`, `mutliplied`, `invalidiating`, and escaped fragments in a `JobConf.setOutputPath` deprecation string. JDiff consumers should treat signature attributes as authoritative over prose.
- Remote error risk: `RemoteException.unwrapRemoteException` depends on class-name lookup and constructors, which can fail or return the wrapper when a local class is unavailable or incompatible.
- MapReduce output risk: `FileOutputFormat.getWorkOutputPath` documents speculative task attempts writing side files; applications must use attempt-unique temporary paths or rely on work output paths to avoid duplicate writers.
- Retry risk: `RETRY_FOREVER` and exponential retry policies can mask persistent failures or increase load if paired with non-idempotent methods.

## Test Signals and Validation Targets

- API-diff tests should verify that this XML remains well-formed, that class/interface boundaries match expected JDiff output, and that deprecated strings are preserved exactly because downstream comparisons may be textual.
- Serialization compatibility tests should round-trip `Writable`, `VersionedWritable`, `VIntWritable`, `VLongWritable`, `Counters`, `Counter`, `Group`, `FileSplit`, and `ID` through `DataOutput`/`DataInput`.
- Byte comparator tests should compare raw `WritableComparator` output with object-level `compareTo` behavior and validate `compareBytes`, hash, primitive readers, and VInt/VLong byte decoding.
- Codec tests should exercise codec factory lookup by suffix, configured codec class lists, compressor/decompressor pooling, `finish`/`finished`, `reset`, and native-zlib/native-lzo fallback behavior.
- Retry/proxy tests should cover fixed, proportional, exponential, exception-specific, remote-exception-specific, and no-fail/forever policies, especially exception propagation semantics.
- IPC tests should cover client/server round trips, parallel calls, proxy stop, protocol version mismatch, remote exception unwrapping, listener address reporting, connection counts, and call queue metrics.
- Metrics/logging tests should validate `RpcMetrics.doUpdates`, JMX bean values, min/max reset, and log-level servlet/CLI behavior.
- MapReduce tests should cover input path parsing/filtering, split computation from block locations, output path validation and compression class configuration, work output path isolation for speculative attempts, job submission path preparation, task report lookup overloads, and `JobConf` deprecated-method compatibility.

## Chunk Merge Notes

- Preceding chunk is needed for the beginning of `org.apache.hadoop.io.UTF8` and any package preamble before line 18780.
- Following chunk is needed for the rest of `org.apache.hadoop.mapred.JobConf` and later `mapred` API classes.
- This chunk should be merged as an API-surface section, not as implementation source analysis. The final per-file report should explain that `hadoop_0.18.1.xml` is a generated JDiff snapshot for API compatibility research.

### subset-b-007269: lines 25022-31137

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 25022-31137

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not executable implementation source. It covers public API metadata in the old `org.apache.hadoop.mapred` package: the tail of `JobConf`, `JobConfigurable`, job end notification, job history records and listeners, job identifiers/profiles/statuses, most of `JobTracker`, text/sequence-file input and output helpers, the core map/reduce interfaces, task identifiers, task completion events, task logs, task reports, and the opening of `TaskTracker`.

The XML records API compatibility data: class and interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, visibility, deprecation text, and Javadoc contracts. Because the range starts inside `JobConf` and ends inside `TaskTracker`, adjacent chunks are required before making whole-class claims about those two types.

## Purpose and Major API Surface

`JobConf` is represented from map-output and output-format configuration through debug scripts, job-end notification, and job-local directory access. The visible methods configure map-output compression and compressor classes, map/final output key/value classes, raw comparators and grouping comparators, mapper/map-runner/partitioner/reducer/combiner classes, combine-once behavior, speculative execution for maps and reduces, map/reduce task counts, max task attempts, failure percentages, job name/session/priority, task profiling, map and reduce debug scripts, job-end notification URI, and task-local job directories. Several methods expose compatibility quirks, including deprecated sequence-file compression-type settings for intermediate map outputs and deprecated string job IDs in nearby job-status/profile APIs.

`JobConfigurable` is a small extension hook with `configure(JobConf)`. It is the old mapred-era dependency-injection mechanism used by input/output formats, partitioners, mappers, reducers, and utility classes to receive job configuration before execution.

`JobEndNotifier` exposes lifecycle entry points for asynchronous end-of-job notifications: starting/stopping the notifier, registering a completed `JobStatus`, and local-runner notification. It integrates with `JobConf` job-end notification URIs.

`JobHistory` and nested history types define the old job-history logging API. `JobHistory.init(JobConf, String, String, long)` initializes history logging, `parseHistoryFromFS` replays a history file into a `JobHistory.Listener`, and disable/enable flags control history emission. `JobHistory.JobInfo`, `Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide static `logSubmitted`, `logStarted`, `logFinished`, `logFailed`, and `logKilled` methods, with overloads accepting either string IDs or typed `JobID`, `TaskID`, and `TaskAttemptID`. Enums `Keys`, `Values`, and `RecordTypes` describe the serialized record vocabulary. `HistoryCleaner` is a `Runnable` for purging old history.

`JobID`, `TaskID`, and `TaskAttemptID` are typed, immutable identifiers extending `ID`. They implement equality, ordering, string conversion, `Writable`-style `readFields`/`write`, static `read(DataInput)`, `forName(String)` parsing, and regex-pattern helpers. Their docs define canonical string forms such as `job_...`, `task_..._m_...`, and task-attempt IDs, and warn applications to avoid manual string parsing.

`JobPriority`, `JobTracker.State`, and `TaskCompletionEvent.Status` are enums used to classify scheduling priority, tracker lifecycle state, and task completion state. The JDiff metadata only shows standard `values()` and `valueOf()` entry points, but these enums are wire/API values and therefore compatibility-sensitive.

`JobProfile`, `JobStatus`, `TaskCompletionEvent`, and `TaskReport` are serializable job/task metadata carriers implementing `Writable` where applicable. `JobProfile` contains user, typed and deprecated string job IDs, job file, tracking URL, and job name. `JobStatus` stores map/reduce progress, run state, start time, and username. `TaskCompletionEvent` carries event ID, task attempt ID, tracker HTTP address, runtime, status, map/reduce classification, and per-job task index. `TaskReport` contains task ID, progress, reporter state string, diagnostics, counters, start time, and finish time.

`JobShell` is a `Configured` command-line `Tool` with `init`, `run`, and `main`, providing a mapred-era CLI entry around job submission and control.

`JobTracker` is the central old mapred master API. It implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. The visible surface starts and stops the tracker, serves RPC protocol versions, offers service, exposes tracker identity/ports/start time/build version, returns running/failed/completed jobs and task trackers, manages network topology resolution, accepts task-tracker heartbeats, reports tracker errors, allocates job IDs, submits jobs, returns cluster/job/task status, kills jobs/tasks, returns task completion events and diagnostics, resolves assigned trackers and task-in-progress objects, exposes system/local job directories, and has a `main` entry point.

Record input APIs include `LineRecordReader`, `LineRecordReader.LineReader`, `KeyValueLineRecordReader`, and `KeyValueTextInputFormat`. They implement or produce `RecordReader` instances over `LongWritable`/`Text` or `Text`/`Text`, handle split-aware reading, expose position/progress, and close underlying streams. `KeyValueLineRecordReader.findSeparator` and configurable key-value separator behavior are the main parsing concern.

Map/reduce execution contracts are represented by `Mapper`, `MapRunnable`, `MapRunner`, `MapReduceBase`, `Reducer`, `Partitioner`, `OutputCollector`, `Reporter`, `RecordReader`, `RecordWriter`, `OutputFormat`, and `OutputFormatBase`. `Mapper.map` and `Reducer.reduce` consume keys/values and emit via `OutputCollector.collect`. `MapRunner.run` drives records from a `RecordReader` into a mapper. `Reporter` exposes status updates, counters, and the current `InputSplit`. `Partitioner.getPartition` maps keys to reduce partitions. `RecordReader` and `RecordWriter` define streaming IO lifecycle methods. `MapReduceBase` provides no-op `configure` and `close` defaults for user code.

Output and split helpers include `MapFileOutputFormat`, `MultiFileInputFormat`, `MultiFileSplit`, `OutputLogFilter`, and `OutputFormatBase`. `MapFileOutputFormat` writes `MapFile` output and provides static readers/get-entry helpers. `MultiFileInputFormat` groups multiple files into `MultiFileSplit`; `MultiFileSplit` persists path and length arrays and exposes locations. `OutputLogFilter` filters output log paths. `OutputFormatBase` provides static compression configuration helpers plus abstract record-writer and output-spec checks.

Sequence-file APIs include binary/text input formats and readers, `SequenceFileInputFormat`, `SequenceFileRecordReader`, `SequenceFileOutputFormat`, `SequenceFileAsBinaryOutputFormat`, `WritableValueBytes`, and `SequenceFileInputFilter` with `Filter`, `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`. These APIs bridge Hadoop `SequenceFile` storage to mapred `RecordReader`/`RecordWriter`, expose key/value class discovery, raw byte records, text conversion, compression type configuration, and filter sampling by hash, percentage, or regex.

`RunningJob` is the client-facing job handle contract. It exposes typed and deprecated string job IDs, job name/file/tracking URL, progress, completion/success checks, blocking `waitForCompletion`, `killJob`, task completion event paging, task killing by string or typed attempt ID, and counters.

`StatusHttpServer`, `StackServlet`, and `TaskGraphServlet` describe a Jetty-style status HTTP server used by mapred daemons. The API sets attributes, adds servlets, reads attributes/port, configures threads, adds SSL listeners, starts/stops, and serves stack traces or task graphs via servlet `doGet`.

`TaskLog`, `TaskLog.LogName`, `TaskLogAppender`, and `TaskLogServlet` define task-local logging APIs. `TaskLog` locates per-task log files, purges old logs, calculates configured log-length caps, wraps commands to capture stdout/stderr or debug output, and quotes shell command components. `TaskLogAppender` is a log4j `FileAppender` for child task logs with task ID and total-log-size properties. `TaskLogServlet` exposes task logs over HTTP from task trackers.

`TaskTracker` begins at the end of the chunk. The visible metadata shows it implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`, has a `JobConf` constructor, exposes task-tracker metrics, and begins the RPC `getProtocolVersion` method. Its full behavior belongs to the next chunk.

## Control Flow and Behavioral Contracts

The XML has no executable control flow, but the Javadocs describe API-level flows. A job is configured through `JobConf`, submitted to `JobTracker.submitJob`, monitored via `RunningJob`, `JobStatus`, `JobProfile`, `TaskReport`, counters, diagnostics, and `TaskCompletionEvent`, and eventually killed or completed. `JobEndNotifier` and `JobHistory` are side channels triggered by job completion and task lifecycle transitions.

Map task flow is expressed by `RecordReader.next` producing input records, `MapRunner.run` invoking a configured `Mapper.map`, and `OutputCollector.collect` emitting intermediate records. The job configuration selects mapper, map runner, partitioner, combiner, reducer, map-output key/value types, comparators, grouping comparator, and compression. Reducer flow groups equal keys according to the grouping comparator and invokes `Reducer.reduce` with an iterator of values, emitting final output through the same collector abstraction.

Input flow is split-aware. `LineRecordReader` and `KeyValueLineRecordReader` track current byte position and progress; `LineReader` has overloads for max line length and max bytes to consume; `KeyValueTextInputFormat` decides splitability and constructs readers for file splits. `MultiFileInputFormat` creates grouped splits and corresponding readers.

Output flow is controlled by `OutputFormat.getRecordWriter` and `checkOutputSpecs`. `OutputFormatBase` centralizes output compression settings. `SequenceFileOutputFormat` and `MapFileOutputFormat` construct storage-specific writers, while `RecordWriter.close(Reporter)` is the completion hook. `OutputLogFilter` excludes task/log artifacts from output path listings.

Sequence-file reader flow wraps `SequenceFile.Reader` and exposes typed or raw key/value records. Binary readers expose `BytesWritable` and class-name metadata; text readers convert keys and values to `Text`; filter readers apply configured `SequenceFileInputFilter.Filter` instances before records reach the mapper. Filter configuration is job-conf driven, with `MD5Filter`, `PercentFilter`, and `RegexFilter` reading frequency or pattern settings from configuration.

Job history flow writes lifecycle records using static logging helpers and can parse persisted history from a filesystem path into a listener callback. History events are represented as key/value pairs keyed by `JobHistory.Keys`, with values constrained by `JobHistory.Values` and record categories by `RecordTypes`.

JobTracker flow is RPC-heavy. Task trackers send `heartbeat` requests containing tracker status, accept/response ID, initial-contact flags, and response IDs; clients call job-submission protocol methods for IDs, submission, status, diagnostics, reports, counters, task completion events, and kill operations. Topology helpers resolve task trackers into network nodes for locality-aware scheduling.

Task log flow wraps child task commands in shell invocations that redirect stdout/stderr to per-task files, optionally retaining only a tail segment. The servlet and appender surface the same task-specific logs through HTTP and log4j.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API metadata used by compatibility tooling. Runtime state described in the chunk belongs to the Hadoop APIs.

Configuration state lives primarily in `JobConf`: selected classes, compression flags/codecs, comparator classes, speculative execution flags, task counts, retry/failure thresholds, priority, profiling parameters, debug scripts, notification URIs, and local job directories. These settings influence task JVM launch, shuffle output, scheduling, monitoring, and cleanup behavior.

Persistent job metadata includes job history files, local job file paths, system job directories, job profiles/statuses, task reports, counters, task completion events, and task logs. `JobHistory.JobInfo.encode*` and `decodeJobHistoryFileName` indicate filesystem-stored history paths and filenames must be URL/path safe and reversible.

Identifier classes persist over RPC and storage via `readFields`/`write`. `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`, and `MultiFileSplit` are wire-format classes, so field ordering and parsing behavior are compatibility-sensitive.

Filesystem side effects occur through job submission, local job file path management, mapred output writers, sequence/map file writers, history logging, log cleanup, command-output capture, HTTP log serving, and task/job kill operations. Many methods throw `IOException`, and servlet entry points throw `ServletException`/`IOException`.

Mapred execution state includes record-reader positions, reader progress, reporter status strings, counters, input split identity, map/reduce progress, task start/finish times, task diagnostics, task attempt runtime, and tracker assignment. `RunningJob.waitForCompletion` is explicitly blocking, while `JobTracker.offerService` runs master service loops.

## Dependencies and Integration Points

The chunk is centered on the legacy `org.apache.hadoop.mapred` API and depends on Hadoop IO types such as `Writable`, `WritableComparable`, `RawComparator`, `LongWritable`, `Text`, `BytesWritable`, `SequenceFile`, `MapFile`, and compression codecs. It also depends on Hadoop filesystem types including `Path`, `FileSystem`, `FileStatus`, `PathFilter`, `FileSplit`, and `InputSplit`.

Mapred integration points include `JobConf`, `JobConfigurable`, `Mapper`, `Reducer`, `MapRunnable`, `Partitioner`, `OutputCollector`, `Reporter`, `InputFormat`, `OutputFormat`, `RecordReader`, `RecordWriter`, `RunningJob`, `JobSubmissionProtocol`, `InterTrackerProtocol`, `TaskUmbilicalProtocol`, `HeartbeatResponse`, `TaskTrackerStatus`, `ClusterStatus`, `Counters`, and `MRConstants`.

Daemon and monitoring dependencies include servlet APIs (`HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `ServletException`), log4j (`FileAppender`, `LoggingEvent`), network types (`InetSocketAddress`, topology `Node`), URL/HTTP strings, and Java process command wrapping.

Compatibility tooling depends on XML structure and attributes, not implementation bytecode. Public/protected signature changes, deprecation changes, thrown-exception changes, enum value changes, or Javadoc contract changes in these APIs can affect JDiff comparisons against other Hadoop releases.

## Risks and Compatibility Notes

This line window is partial at both ends. `JobConf` begins before line 25022 and `TaskTracker` continues after line 31137, so this chunk must not be treated as complete coverage of either type.

The old `mapred` APIs mix typed IDs with deprecated string IDs. Callers and compatibility tests must preserve deprecated accessors such as `getJobId`, `getTaskId`, and string-based kill/submission overloads while preferring typed `JobID`, `TaskID`, and `TaskAttemptID`.

Map-output type and comparator configuration is easy to misconfigure. The docs explicitly allow map-output key/value classes to differ from final output classes. Grouping comparator and sort comparator can differ to support secondary sort-like behavior, but the reduce sort is not guaranteed stable.

Combiner behavior is not equivalent to reducer behavior unless the operation is associative and safe for repeated or skipped execution. `setCombineOnceOnly` exists, but the general combiner contract still requires care because combiners may otherwise run zero or more times.

Speculative execution, task-attempt limits, and failure-percentage thresholds affect correctness for jobs with side effects. Output commit protocols and idempotent mappers/reducers are important because this API allows duplicate attempts and task killing.

Sequence-file binary/text adapters expose raw bytes or stringified values. Tests and downstream tools must verify that key/value class metadata, raw byte boundaries, compression settings, and text conversion are consistent with `SequenceFile` semantics.

Command wrapping in `TaskLog.captureOutAndError`, debug-script capture, and `addCommand` is shell-sensitive. Quoting, executable path handling, log truncation, and setup commands are portability and injection-risk areas.

`JobTracker` public methods expose many internal types (`JobInProgress`, `TaskInProgress`, task tracker status, topology nodes). That broad surface makes API compatibility fragile and ties clients/tests to master internals.

## Test Signals

JDiff validation should confirm the XML remains well-formed across this line range and preserves all class/interface boundaries, including partial `JobConf` and partial `TaskTracker`.

API compatibility tests should check method signatures, generic bounds, visibility, declared exceptions, deprecation strings, enum presence, and constructor overloads for the covered `mapred` classes and interfaces.

Job configuration tests should cover map-output compression/codecs, map/final output key/value classes, comparator and grouping comparator classes, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution flags, task counts, attempt limits, failure percentages, job priority, profiling ranges, debug scripts, and job-end notification URI.

Map/reduce contract tests should exercise `MapRunner` driving a `Mapper`, reducer grouping behavior with custom comparators, `OutputCollector.collect`, reporter status/counters/input split, no-op `MapReduceBase.configure/close`, and `RecordReader`/`RecordWriter` lifecycle behavior.

Input/output tests should cover line and key-value readers across split boundaries, separator handling, max line length behavior, `MultiFileSplit` writable round trips, output spec validation, compression setting propagation, map-file lookups, and output-log filtering.

Sequence-file tests should cover typed record reads, raw binary reads/writes, text conversion readers, key/value class-name exposure, compression type configuration, `WritableValueBytes`, and MD5/percent/regex filtering from `JobConf`.

JobTracker/client tests should exercise job ID allocation, submission, profile/status/counter/report retrieval, task completion event paging, diagnostics, job/task kill paths, cluster status, tracker heartbeat response compatibility, tracker error reporting, and topology helper behavior.

Serialization tests should round-trip `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`, and `MultiFileSplit`, including deprecated string accessors and `forName` malformed-input failures.

History and log tests should verify job/task/attempt history logging overloads, history parsing through a listener, history disable behavior, encoded history paths/names, history cleanup, task-log file selection by `LogName`, old-log cleanup, stdout/stderr capture with tail length, debug-output capture, appender close/size behavior, and servlet `doGet` error handling.

### subset-b-007270: lines 31138-37297

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 31138-37297

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not implementation source. The range starts inside the public API entry for `org.apache.hadoop.mapred.TaskTracker`, then completes several `mapred` utility APIs, covers the full `org.apache.hadoop.mapred.jobcontrol` package, most of `org.apache.hadoop.mapred.join`, `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, the Pipes job submitter, and the original Hadoop metrics API and SPI through the beginning of `org.apache.hadoop.metrics.util.MetricsLongValue`.

The XML records compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, visibility/static/final/synchronized flags, deprecation notes, fields, and embedded Javadocs. Research below is based on those signatures and contracts. This is a line-bounded chunk: `TaskTracker` began before this range, and `MetricsLongValue` continues after it.

## Purpose and major API surface

The initial `org.apache.hadoop.mapred` section finishes `TaskTracker` APIs for cleanup, shutdown, task-child RPC, task status, diagnostics, heartbeat pings, task completion, shuffle and local filesystem error reporting, map-output-loss notifications, map completion event lookup, idle checks, and process startup. Nested `TaskTracker.Child` is the child-process `main`, `TaskTracker.MapOutputServlet` serves map outputs from the TaskTracker's Jetty HTTP server, and `TaskTracker.TaskTrackerMetrics` is a periodic metrics updater. The same package also exposes `TextInputFormat`, `TextOutputFormat`, and `TextOutputFormat.LineRecordWriter` for line-oriented text input/output, with text input keys as file offsets and values as lines.

`org.apache.hadoop.mapred.jobcontrol.Job` models a MapReduce job plus its dependency list. It tracks Hadoop job configuration, a JobControl-local ID, assigned MapReduce `JobID`, user message, dependency jobs, and states `WAITING`, `READY`, `RUNNING`, `SUCCESS`, `FAILED`, and `DEPENDENT_FAILED`. Deprecated string mapred job ID accessors coexist with typed `JobID` accessors. `JobControl` is a `Runnable` manager for a group of these jobs, assigning IDs, exposing lists of waiting/running/ready/successful/failed jobs, adding jobs or collections of jobs, and controlling its worker thread through run, stop, suspend, resume, state lookup, and all-finished checks.

`org.apache.hadoop.mapred.join` provides old MapReduce-side sorted join support. `ComposableInputFormat` refines `InputFormat` to return `ComposableRecordReader`; `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding reader IDs, access to the current head key, key cloning, availability checks, skipping through keys, and accepting matching records into a join collector. `CompositeInputFormat` parses `mapred.join.expr`, default and user-defined join operators, table expressions, input paths, and join key comparator configuration; it validates child inputs, builds `CompositeInputSplit` arrays by aligning child splits, and constructs composable record readers. Static `compose` helpers build expression strings.

`CompositeInputSplit` serializes/deserializes a fixed collection of child splits, reports aggregate and per-child lengths, and unions child split locations. `CompositeRecordReader` is the abstract base for joins, managing child record-reader queues, key comparison, configuration, progress, position, close, child initialization, and a `combine` hook for subclasses. `JoinRecordReader`, `InnerJoinRecordReader`, and `OuterJoinRecordReader` build tuple-valued joins; `MultiFilterRecordReader` and `OverrideRecordReader` reduce multiple sources to one value stream. Parser classes (`Parser`, `Node`, `Token`, `NodeToken`, `NumToken`, `StrToken`, `TType`) describe the expression parser for composite joins.

Join buffering is represented by `ResetableIterator`, `ArrayListBackedIterator`, `StreamBackedIterator`, and `ResetableIterator.EMPTY`. The contract is FIFO replay after `reset`, `replay` of the last returned value, explicit `add`, `clear`, and `close`, with stream-backed storage preferred over the array-list implementation. `TupleWritable` is a `Writable`/`Iterable` container for heterogeneous writable children, preserving which tuple positions are populated and serializing count, element types, and objects. `WrappedRecordReader` adapts a normal `RecordReader` into the composable join protocol while caching the current head key/value and collecting values that match a join key.

`org.apache.hadoop.mapred.lib` supplies stock mapred helpers. `FieldSelectionMapReduce` performs configurable field selection over key/value text using `mapred.data.field.separator`, map output field specs, and reduce output field specs. `HashPartitioner` partitions by `Object.hashCode`; `KeyFieldBasedPartitioner` is a configurable partitioner with the same visible partitioning contract in this snapshot. `IdentityMapper`, `IdentityReducer`, `InverseMapper`, and `LongSumReducer` implement common pass-through, key/value swap, and long-summing behavior. `MultipleOutputFormat` routes output records to multiple files by overriding generated leaf names, file names for key/value pairs, actual keys/values, and input-file-based output names; `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide sequence-file and text implementations. `MultithreadedMapRunner`, `NLineInputFormat`, `NullOutputFormat`, `RegexMapper`, and `TokenCountMapper` round out utility mapred components for parallel map execution, fixed-line splits, no-output jobs, regex extraction, and token counting.

`org.apache.hadoop.mapred.lib.aggregate` is the old Aggregate framework for common counting/statistics jobs. Value aggregators include numeric sum/max/min classes, string max/min, unique value counting, and histograms. The `ValueAggregator` interface exposes `addNextValue`, reporting, combiner output, and reset. `ValueAggregatorDescriptor` generates aggregation ID/value pairs from input records, with a type separator and common `ONE` value. `UserDefinedValueAggregatorDescriptor` and `ValueAggregatorBaseDescriptor` provide descriptor implementations and plugin loading. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` implement generic map/combine/reduce stages over `Text` aggregation keys and values; `ValueAggregatorJob` creates and submits configured aggregate jobs; `ValueAggregatorJobBase` stores configured descriptor lists and shared lifecycle behavior.

`org.apache.hadoop.mapred.pipes.Submitter` is the command-line/API entry point for Hadoop Pipes jobs. It gets and sets the executable URI, chooses whether record reader, mapper, reducer, and record writer are Java or non-Java components, controls retention of the downlink command file for debugging, mutates a `JobConf` for Pipes execution, submits it as a `RunningJob`, and exposes `main`.

The metrics packages define Hadoop's original metrics system. `ContextFactory` is a singleton configured from `hadoop-metrics.properties`, stores attributes, and constructs named `MetricsContext` instances by reflective `<contextName>.class` configuration or defaults to `NullContext`. `MetricsContext` manages lifecycle, records, periodic updater registration, and `DEFAULT_PERIOD`. `MetricsRecord` is the typed tag/metric update API with setters for string/integer/long/short/byte tags, setters and incrementers for numeric metrics, `update`, and `remove`. `MetricsUtil` simplifies context lookup and host-tagged record creation, and `Updater` is the periodic callback interface.

Provider packages include `FileContext`, which appends metrics to a configured file or stdout and flushes/closes the writer; `GangliaContext`, which emits metrics records to Ganglia; and JVM metrics classes. `EventCounter` is a Log4J appender that counts fatal, error, warn, and info events. `JvmMetrics` is a singleton `Updater` that periodically emits JVM metrics for a process/session.

`org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the provider base class. It initializes from `ContextFactory`, exposes context attributes and attribute tables, starts/stops monitoring with a timer period, creates final public `MetricsRecord` instances, registers/unregisters updaters, keeps the internal buffered metric table, delegates provider output to abstract `emitRecord`, and allows subclasses to override `flush` and record creation. `MetricsRecordImpl` backs the public record API and delegates `update`/`remove` to its context. `MetricValue` distinguishes absolute and incremental numbers. `NullContext` discards metrics entirely; `NullContextWithUpdateThread` keeps periodic updater calls while suppressing output, useful when another system such as JMX samples state. `OutputRecord` is the emitted tag/metric view, and `Util.parse` parses comma/space-separated host[:port] lists.

`org.apache.hadoop.metrics.util` starts with `MBeanUtil`, which registers/unregisters MBeans under the standard Hadoop `hadoop.dfs:service=...,name=...` naming convention, and `MetricsIntValue`, a synchronized helper for a non-time-varied int metric that pushes only once after updates while JMX reads through `get()`. The chunk ends during the analogous `MetricsLongValue` API after constructor, `set`, `get`, `inc`, and the start of `dec`.

## Control flow and behavioral contracts

TaskTracker control flow is task-child and JobTracker coordinated. Startup can clean temporary storage from previous runs; `run()` is a retry loop that reconnects to the JobTracker when TaskTracker state becomes stale; child processes call back to fetch `Task` data, report progress, send diagnostics, ping the parent, mark completion, and report shuffle/filesystem/map-output failures. Shutdown and close are synchronized lifecycle boundaries that stop tasks/threads and clean local disk state so a TaskTracker can restart in the same JVM.

JobControl flow is dependency-driven. A `Job` starts in `WAITING`; if it has no dependencies or all dependencies reach `SUCCESS`, it becomes `READY`; dependency failure moves it to `DEPENDENT_FAILED`; successful submission moves it to `RUNNING`; runtime completion moves it to `SUCCESS` or `FAILED`. The `JobControl.run()` loop checks running jobs, updates waiting jobs, and submits ready jobs. Dependency additions are only accepted while a job is still waiting.

Composite join flow starts from a join expression in `mapred.join.expr` or one built with `CompositeInputFormat.compose`. The input format parses the expression, validates child inputs, obtains child splits, aligns the ith split from each child into a `CompositeInputSplit`, and constructs a tree of composable record readers. Readers compare head keys, skip through sorted streams, collect all values matching a key into resettable iterators, and subclasses combine child values into either tuple outputs or filtered single-value outputs. The contracts assume participating data sources are sorted and partitioned the same way.

Resettable iterator flow is stateful: callers `add` values, call `reset` before replaying, use `next` to copy successive writable values into caller-provided objects, and can `replay` the last returned value. `close` releases resources and makes later calls undefined; `clear` releases current data sources while preserving reusable internal resources.

Mapred library flows are conventional MapReduce pipelines. Field selection parses configured field specs and emits selected key/value text fields in map and reduce phases. Multiple output routing creates a composite writer; each output record can derive a destination file name and transformed key/value before delegation to a base writer. Aggregate jobs map each input record through configured descriptors into aggregation-type-prefixed IDs, combine values of the same aggregation key, and reduce them into final reports.

Pipes submission flow mutates the supplied `JobConf` to include executable and Java/non-Java component choices, optionally keeps a command file for debugging, then submits to the MapReduce cluster. The command-file debugging path depends on task-directory retention settings and the `hadoop.pipes.command.file` environment variable when replaying externally.

Metrics flow is provider driven. A client obtains the singleton `ContextFactory`, gets or creates a named context, creates records, sets tags/metrics, calls `update`, and starts monitoring. Contexts periodically call registered `Updater` instances, buffer rows keyed by record name and tag values, emit rows each period through provider-specific `emitRecord`, then flush. `remove` deletes rows matching a record's tags, and `stopMonitoring` pauses emission without necessarily freeing buffered rows; `close` stops and resets buffered state.

## State, persistence, and side effects

The JDiff XML itself is persistent API compatibility data. Runtime persistence described by this chunk includes TaskTracker local temporary storage, task process state, map output files served by Jetty, child-to-parent task status, JobTracker RPC state, text output files, serialized input splits and tuples, aggregate framework output, Pipes command files, metrics configuration attributes, metrics buffers, metrics files, Ganglia network packets, log event counters, JVM metrics records, and JMX MBean registrations.

TaskTracker APIs are state-heavy and partially synchronized. They expose task tables, report address binding, task status updates, diagnostics, failure notifications, map completion event state, idle detection, cleanup, and restart-oriented shutdown semantics. Correctness depends on coordinated cleanup of local disk and child processes.

JobControl maintains multiple tables/lists of jobs by state, a group-local ID space, per-job dependency lists, Hadoop-assigned job IDs, messages, and thread state. The public getters return `ArrayList` views in this old API surface, so caller mutation and synchronization are compatibility concerns unless implementations defensively copy.

Join APIs store parser trees, child split collections, current head key/value for each wrapped reader, priority queues of readers sorted by key, tuple populated-position bits, and resettable value buffers. `CompositeInputSplit` and `TupleWritable` both have explicit binary serialization formats that are part of job submission/task execution compatibility.

Mapred utility classes persist configuration-driven behavior in `JobConf`: field separators/specs, multiple-output filename derivation, input-file trailing-leg count, multithreaded runner settings, regex/token settings, aggregate plugin descriptors, and Pipes executable/component flags. Aggregate objects keep running sums, extrema, unique sets, and histograms; histogram reports can include full value/frequency detail.

Metrics APIs maintain global singleton factory state, context attributes from `hadoop-metrics.properties`, monitoring timers, registered updater lists, per-context buffered metric tables, record tag/metric maps, absolute vs incremental metric values, provider output handles, and MBean registrations. `MetricsIntValue` and the visible portion of `MetricsLongValue` use synchronized access around mutable counters and an updated-since-last-push flag implied by the push contract.

## Dependencies and integration points

TaskTracker integrates with `JobTracker` through `InterTrackerProtocol`, child task processes, `TaskAttemptID`, `TaskStatus`, `TaskCompletionEvent`, local filesystem storage, Jetty/servlet APIs, and the metrics framework.

Text input/output integrate with `FileInputFormat`, `FileOutputFormat`, `RecordReader`, `RecordWriter`, `LongWritable`, `Text`, `FileSystem`, `Path`, `JobConf`, `Reporter`, `Progressable`, and `DataOutputStream`.

JobControl depends on `JobConf`, `JobID`, `RunningJob`-style MapReduce execution, Java `Runnable`, collections, and `IOException`. It is an orchestration layer above classic `org.apache.hadoop.mapred`.

The join package integrates with `InputFormat`, `InputSplit`, `RecordReader`, `Reporter`, `Writable`, `WritableComparable`, `WritableComparator`, `WritableUtils`-style serialization, `Configuration`, `Path`, Java `PriorityQueue`, arrays/collections, and expression parsing. It depends on sorted, identically partitioned inputs and reflectively loaded input formats/join operators.

The utility MapReduce package integrates with `Mapper`, `Reducer`, `Partitioner`, `OutputCollector`, `Reporter`, `MapReduceBase`, `SequenceFileOutputFormat`, `TextOutputFormat`, text and sequence inputs, regex APIs, and job configuration properties.

The aggregate framework integrates with the same old `mapred` Mapper/Reducer APIs, `Text`, `Writable`, `WritableComparable`, `JobControl`, generic Hadoop option parsing, plugin descriptor classes, and collection types such as `ArrayList`, `Map.Entry`, and `TreeMap`.

Pipes integrates Java MapReduce submission with non-Java executable URIs, HDFS-distributed binaries, Java/non-Java component toggles, task local directories, command files, and `RunningJob`.

Metrics integrates with `hadoop-metrics.properties`, reflective provider construction, file IO, Ganglia, Log4J appenders/events, JVM runtime metrics, JMX MBeans, `InetSocketAddress` parsing, and Hadoop components such as DataNode/TaskTracker that register periodic `Updater`s.

## Risks and compatibility notes

This chunk has partial boundaries. Earlier `TaskTracker` fields and methods are outside the range, and `MetricsLongValue` is incomplete here, so final per-file reconciliation needs adjacent chunks before making whole-class conclusions for those two classes.

The JDiff file is a compatibility artifact. Changes to signatures, visibility, generic type parameters, exception declarations, field constants, deprecation metadata, or embedded contracts can represent source or binary compatibility changes for old Hadoop clients.

TaskTracker APIs are concurrency and lifecycle sensitive. Misordered shutdown, stale JobTracker reconnect state, unsynchronized status transitions, or failure-report handling can leak child processes, lose diagnostics, leave map outputs behind, or make restarts in the same JVM unsafe.

JobControl depends on correct state transitions and dependency semantics. Allowing dependency mutation after submission, misclassifying dependent failures, or failing to stop/suspend/resume the worker loop correctly can submit jobs too early, never submit ready jobs, or leave orchestration threads running.

Composite joins are fragile around input assumptions. Inputs must be sorted and partitioned identically, child split counts must align, configured key comparators must match the serialized key type, and parser expressions must resolve reflectively. Incorrect resettable-iterator ordering or head-key comparison can duplicate or drop joined records.

Serialization formats for `CompositeInputSplit` and `TupleWritable` are externally visible during job submission and task execution. Changing class-name encoding, count ordering, child split ordering, tuple type ordering, or populated-slot semantics would break old jobs.

`MultipleOutputFormat` can create many output files and derives names from keys, values, and input paths. Bugs in path derivation or user overrides can collide files, create invalid paths, or expose unexpected input path fragments in output layout.

Aggregate framework keys encode aggregation type and ID in text. Bad descriptor output, separator collisions, malformed histogram value/frequency strings, or inconsistent combiner/reducer report formats can produce incorrect statistics.

Pipes job submission mutates the supplied `JobConf` and coordinates Java with external executables. Risks include missing executable URIs, wrong Java/non-Java toggles, unavailable distributed binaries, command-file leakage when debugging, and failure to preserve task directories needed for replay.

Metrics APIs are highly stateful. Provider construction falls back to `NullContext`, so configuration mistakes can silently discard metrics if callers use `MetricsUtil`. Periodic updater thread safety, record-row matching by tags, incremental vs absolute metric handling, `stopMonitoring` vs `close`, file append behavior, Ganglia network failures, and MBean naming collisions all matter for observability correctness.

## Test signals

JDiff validation should ensure this XML range remains well formed around partial boundaries and preserves package/class/interface boundaries, constructor and method signatures, generic parameter text, declared exceptions, synchronized/static/final flags, field constants, deprecation text, and Javadocs.

TaskTracker tests should cover cleanup-on-startup, shutdown/close idempotence, child `getTask`, periodic `statusUpdate`, diagnostic reporting, ping liveness, task `done`, shuffle/fs/map-output error handling, map completion event lookup, idle detection, report address binding, map-output servlet responses, and metrics updater registration.

Text format tests should cover splitability decisions, line reader behavior for linefeed/carriage return, offset keys, record writer separators, synchronized line writes, close behavior, and interaction with configured output paths.

JobControl tests should cover dependency graph state transitions, dependency failure propagation, rejection of dependency additions after waiting state, job ID assignment, typed assigned `JobID` accessors, deprecated string ID accessors, run-loop submission of ready jobs, suspend/resume/stop, all-finished detection, and list getters by state.

Join tests should cover expression parsing and `compose`, user-defined join operators, invalid expressions, child input validation, split-count alignment, `CompositeInputSplit` serialization and location aggregation, inner/outer/override join semantics, comparator configuration, skip/accept behavior, resettable iterator FIFO replay, `clear` vs `close`, stream-backed buffering, `TupleWritable` has/get/iterator/string/write/readFields, and wrapped reader head-key comparison/progress/position forwarding.

Mapred utility tests should cover identity mapper/reducer passthrough, inverse mapper swapping, hash and key-field partitioning, long summing, field selection specs including ranges and open ranges, multiple-output filename/key/value overrides, input-file-based output naming, sequence/text multiple-output writers, multithreaded map runner behavior, N-line split generation, null output writer behavior, regex extraction, and token count emission.

Aggregate tests should cover each numeric/string/unique/histogram aggregator, malformed inputs, combiner output round trips into reducers, descriptor plugin configuration, generated aggregation ID/value pairs, mapper iteration across descriptor lists, reducer report output, job creation with and without explicit descriptor classes, and integration with `JobControl`.

Pipes tests should cover executable get/set, Java component toggles for record reader/mapper/reducer/record writer, command-file retention configuration, `submitJob` mutation of `JobConf`, missing executable failures, command-line parsing in `main`, and debugging replay expectations around `downlink.data`.

Metrics tests should cover `ContextFactory` singleton loading from `hadoop-metrics.properties`, attribute set/remove/table behavior, reflective context creation and null fallback, context lifecycle start/stop/restart/close, updater registration/unregistration and periodic calls, record creation and host tagging, tag/metric setter overloads, incremental vs absolute metrics, atomic update behavior across separate records with matching tags, remove semantics, provider emit/flush behavior for file and Ganglia contexts, Log4J event counts, JVM metrics singleton initialization, `OutputRecord` lookup views, server-spec parsing defaults, MBean register/unregister naming, and synchronized `MetricsIntValue` plus visible `MetricsLongValue` counter operations.

### subset-b-007271: lines 37298-43567

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 37298-43567

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not executable Java source. It begins inside the tail of `org.apache.hadoop.metrics.util.MetricsLongValue`, covers time-varying metrics, the full `org.apache.hadoop.net` package visible in this API file, the Hadoop Record I/O runtime, Record I/O compiler and generated JavaCC parser support, Record I/O metadata classes, early security user/group identity APIs, distributed tools, and utility classes through the beginning of `org.apache.hadoop.util.PriorityQueue.clear`. The final `PriorityQueue` method and class documentation continue past the requested line range, so the boundary class is partial.

The XML records public/protected compatibility surface: packages, classes/interfaces, inheritance, implemented interfaces, fields, constructors, methods, parameter and exception types, visibility, `static`/`final`/`abstract`/`synchronized` flags, deprecation markers, and Javadoc. The research below describes contracts implied by those signatures and docs; it does not infer hidden method-body details except where the Javadoc names behavior.

## Purpose and major API surface

The metrics tail covers mutable metrics primitives. `MetricsLongValue` exposes a synchronized `pushMetric(MetricsRecord)` that publishes only if changed since the last push. `MetricsTimeVaryingInt` tracks interval deltas with synchronized `inc()`, `inc(int)`, `pushMetric(MetricsRecord)`, and `getPreviousIntervalValue()`. `MetricsTimeVaryingRate` tracks operation counts and elapsed time with `inc(long)`, `inc(int,long)`, interval push, previous interval operation count, previous interval average time, min/max single-operation time, and `resetMinMax()`.

`org.apache.hadoop.net` provides host, rack, socket, and topology support. `DNS` offers static forward/reverse helpers for a named interface and optional nameserver: `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, and `getDefaultHost`. `DNSToSwitchMapping` defines pluggable rack resolution from a list of host/IP names to network paths. `ScriptBasedMapping` implements that interface and `Configurable`, using a configured external script to resolve names.

`NetUtils` centralizes network setup. It chooses socket factories from `Configuration`, builds `InetSocketAddress` objects from `host[:port]` or URI-like strings, merges legacy split bind-address/port settings into a new address setting, maintains static hostname resolutions, normalizes wildcard server addresses into client-connect addresses, and wraps sockets with timeout-aware input/output streams. `SocketInputStream` and `SocketOutputStream` adapt Java NIO channels and sockets into `InputStream`/`OutputStream` plus `ReadableByteChannel`/`WritableByteChannel`, adding `waitForReadable`, `waitForWritable`, and `transferToFully` support. `SocksSocketFactory` and `StandardSocketFactory` implement `SocketFactory` overloads; the SOCKS variant is configurable and proxy-aware.

`NetworkTopology`, `Node`, and `NodeBase` define rack-aware cluster topology. `Node` exposes network location, name, parent, and tree level. `NodeBase` implements those attributes and provides path constants and `normalize`. `NetworkTopology` stores a hierarchical tree of leaves and racks, with constants such as `DEFAULT_RACK`, `UNRESOLVED`, and `DEFAULT_HOST_LEVEL`; it can add/remove leaves, test containment, look up nodes by path, report rack and leaf counts, compute node distance, test same-rack locality, choose random nodes under a scope excluding a scope, count available leaves, stringify the tree, and pseudo-sort replicas by distance from a reader.

`org.apache.hadoop.record` is the legacy Hadoop Record I/O runtime. `RecordInput` and `RecordOutput` define the serialization contract for primitive values, strings, buffers, records, vectors, and maps with string tags. Binary, CSV, and XML concrete input/output classes implement these interfaces. `BinaryRecordInput` and `BinaryRecordOutput` also expose thread-local `get(DataInput/DataOutput)` helpers. `Index` is the iterator-style cursor for reading maps and vectors. `Record` is the abstract generated-record base and implements `WritableComparable` plus `Cloneable`, with tagged and tagless `serialize`/`deserialize`, `write`, `readFields`, `compareTo`, and `toString`. `RecordComparator` extends `WritableComparator` and registers optimized raw comparators for generated records.

`Buffer` is the Record I/O native Java representation of a byte sequence. It tracks a backing byte array, count, and capacity; exposes constructors from empty, array, and array slice; distinguishes `set(byte[])` aliasing from `copy(byte[], offset, length)` copying; supports capacity changes, reset, truncate, append, comparison, equality, hash code, clone, and string conversion with default or explicit charset.

`org.apache.hadoop.record.Utils` provides low-level binary compatibility helpers: parse floats/doubles from byte arrays, read/write zero-compressed variable-length ints and longs from byte arrays or streams, compute encoded integer size, compare byte arrays lexicographically, and expose hex characters. The XML/XML and CSV/Binary serializer classes rely on these stable primitive encodings.

`org.apache.hadoop.record.compiler` contains the public Record I/O compiler model. `JType` is the base for supported IDL types, with scalar specializations `JBoolean`, `JByte`, `JDouble`, `JFloat`, `JInt`, and `JLong`, plus composite/special types such as `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`. `JField<T extends JType>` wraps a field name and type. `JFile` models a parsed Record DDL file and generates code in a requested language. `CodeBuffer` handles indentation, and `Consts` exposes compiler string constants such as record input/output and runtime type information names.

`org.apache.hadoop.record.compiler.ant.RccTask` integrates the Record I/O compiler with Ant. It accepts language, input file, destination directory, `failonerror`, and file sets, then invokes the compiler on each record definition file.

`org.apache.hadoop.record.compiler.generated` is JavaCC-generated parser/lexer support for the Record I/O compiler. `Rcc` parses includes, modules, record lists, records, fields, primitive/composite types, maps, and vectors from `InputStream`, `Reader`, or token-manager sources; it also exposes `main`, `usage`, `driver`, `ReInit`, token access, parse-exception generation, and tracing toggles. `RccConstants` defines token IDs and lexical states. `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError` expose lexer/parser state, token images, line/column tracking, token chains, parse diagnostics, and lexical error formatting.

`org.apache.hadoop.record.meta` represents runtime type metadata for Record I/O. `TypeID` exposes singleton base type IDs and a `typeVal` byte using `TypeID.RIOType` constants. `MapTypeID`, `VectorTypeID`, and `StructTypeID` describe composite types. `FieldTypeInfo` binds field names to type IDs. `RecordTypeInfo extends Record` so type information can itself be serialized/deserialized, named, augmented with fields, queried for nested struct type info, and compared in a compatibility-oriented way. `meta.Utils.skip` can consume serialized values from a `RecordInput` according to a `TypeID`.

`org.apache.hadoop.security` exposes the early user/group identity API. `UserGroupInformation` is a `Writable` abstract class for user and group data with per-thread current UGI access (`getCurrentUGI`, `setCurrentUGI`), username/groups access, `login(Configuration)`, and `readFrom(Configuration)`. `UnixUserGroupInformation` implements it for Unix systems, adds constructors for username/group arrays, immutable creation, serialization/deserialization, config persistence through `saveToConf` and `readFromConf`, Unix/config login variants, equality, hash code, and string conversion. `UGI_PROPERTY_NAME` is a public config key.

`org.apache.hadoop.tools` contains command-line/distributed utilities. `DistCp implements Tool` and recursively copies directories between filesystems, exposing `copy(Configuration, srcPath, destPath, logPath, srcAsList, ignoreReadFailures)`, `run`, `main`, and random job ID generation; its nested `DuplicationException` carries an `ERROR_CODE`. `HadoopArchives implements Tool` creates Hadoop archives from source paths into a destination. `Logalyzer` archives and analyzes Hadoop logs, while `LogComparator` is a configurable raw UTF8 comparator and `LogRegexMapper` is a MapReduce mapper that extracts text matching a configured regular expression.

`org.apache.hadoop.util` begins with process and filesystem helpers. `Daemon extends Thread` and always constructs daemon threads around optional `Runnable` and `ThreadGroup` inputs. `DiskChecker` creates directories with stricter exists semantics and validates directories, throwing `DiskErrorException` or `DiskOutOfSpaceException`. `GenericOptionsParser` uses Commons CLI to parse Hadoop generic command-line options (`-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, `-archives`) into a `Configuration`, remaining application args, and a `CommandLine`. `GenericsUtil` converts generic lists to arrays and extracts runtime classes.

The utility sorting and platform classes expose reusable building blocks. `IndexedSortable` supplies index-based `compare` and `swap`; `IndexedSorter` sorts an index range, optionally reporting progress; `HeapSort` implements that interface. `MergeSort` sorts integer index arrays using an `IntWritable` comparator. `HostsFileReader` reads include/exclude host files and can refresh. `NativeCodeLoader` reports whether native Hadoop code is loaded and stores per-job native-library loading preference in `JobConf`. `PlatformName` reports the JVM platform string. `PrintJarMainClass` prints a jar manifest main class. `PriorityQueue` is an abstract heap whose subclasses define `lessThan`, then call `initialize(maxSize)` and use `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and the partially visible `clear`.

## Control flow and behavioral contracts

Metrics flow is interval-based. Callers mutate counters/rates with synchronized `inc` or set-like operations, then the metrics system calls `pushMetric(MetricsRecord)`. Time-varying values publish deltas since the last push and retain previous-interval values for JMX-style reads. Rate metrics derive average time from operation count and total time, while min/max are independent state that can be reset.

Network identity flow starts with local interface discovery through `DNS`, optional reverse lookup through a nameserver, and batch host-to-rack resolution through `DNSToSwitchMapping`. `ScriptBasedMapping` adds configuration before resolution, so caller behavior depends on both the host list and the configured script. `NetworkTopology` expects leaves to be represented as `Node`s with normalized paths; add/remove update tree membership, distance calculations walk tree relationships, and `pseudoSortByDistance` reorders an array so local and near-rack nodes are favored for data locality.

Socket setup flow goes through `NetUtils`. Hadoop components resolve a configured socket factory for a protocol class or fall back to default JVM sockets, parse textual endpoints into `InetSocketAddress`, then request timeout-capable streams over sockets. The stream wrappers expose blocking stream APIs while using channel readiness waits for read/write timeouts; callers must close streams/channels to release socket resources.

Record I/O flow is generated-code driven. A `.jr`-style record definition is parsed by `Rcc`, represented as `JFile`, `JRecord`, `JField`, and `JType` objects, then emitted in a target language. At runtime, generated `Record` subclasses serialize each field sequentially through a chosen `RecordOutput` and deserialize sequentially through `RecordInput`. Collection deserialization uses an `Index`: call `startVector` or `startMap`, loop until `done()`, consume each element, call `incr()`, then close the vector/map with `endVector` or `endMap`.

Record metadata flow mirrors data flow. `RecordTypeInfo` can serialize a record schema, deserialize it back, and find direct nested struct metadata. `meta.Utils.skip` uses a supplied `TypeID` to advance over serialized data without materializing it, which is important for schema-evolution or filtered-read paths.

Security flow is config and thread scoped. `UnixUserGroupInformation.login()` can discover the current Unix user/groups, while `login(conf, save)` can read configured identity and optionally persist it. `UserGroupInformation.getCurrentUGI()` returns the per-thread identity, and `setCurrentUGI()` changes that thread-local context for downstream filesystem/RPC actions.

Tool flow follows the Hadoop `Tool` pattern. Tools are constructed or configured with `Configuration`, parse command-line arguments in `run(String[])`, then submit or run MapReduce/filesystem workflows. `DistCp.copy` is the programmatic entry point for recursive copy, `HadoopArchives.archive` is the archive creation entry point, and `Logalyzer` splits work into archive and analyze phases.

Utility control flow is mostly lifecycle-oriented. `GenericOptionsParser` mutates or augments the supplied `Configuration` before application-specific parsing. `HostsFileReader.refresh()` rereads include/exclude files. `DiskChecker.checkDir()` validates directory existence/writability and usable space. `PriorityQueue` requires subclass ordering plus initialization before use; `put` and `pop` maintain heap order, while `insert` keeps only acceptable elements when the queue is full.

## State, persistence, and side effects

The JDiff XML itself is persistent API compatibility metadata. Runtime state described by this chunk includes metrics current and previous interval values, min/max timing history, DNS results, static hostname resolutions, configured socket factories, socket/channel readiness state, network topology tree nodes, Record I/O byte buffers, serialized records, parser token streams, type metadata records, user/group identities, tool job configuration, host include/exclude sets, native-library flags, and heap contents.

Metrics classes are mutable and synchronized, but their values are intentionally interval scoped. `pushMetric` changes publication state by resetting or rolling current values into previous-interval state. Rate min/max state persists until `resetMinMax()` rather than automatically resetting every interval.

Network topology state is in-memory but influences persistent distributed behavior such as HDFS replica placement and block read ordering. `NodeBase` has public/protected-style state fields (`name`, `location`, `level`, `parent`) and path constants, so serialized logs, tests, and subclass behavior can depend on path normalization and root/rack naming. `NetUtils` static resolutions are process-global overrides for host lookup.

Record I/O persists data in binary, CSV, or XML encodings. Binary compatibility depends on field ordering, tag handling, collection size markers, buffer byte contents, and zero-compressed variable-length integer encoding. `Buffer.set(byte[])` adopts caller storage while `copy(...)` duplicates it, so aliasing can leak later caller mutations into serialized values if used carelessly.

The compiler-generated parser has explicit mutable state: token source, current token, next token, character buffers, line/column arrays, lexical states, debug streams, and parse exception fields. Reuse through `ReInit` changes this state in place. Public parser/token fields make compatibility sensitive to JavaCC output shape.

Security APIs persist user/group identity through Hadoop `Configuration` strings and Hadoop `Writable` streams. Per-thread current UGI is mutable process state. Unix login depends on host OS user/group lookup and may throw `LoginException`.

Tools have filesystem and MapReduce side effects. `DistCp` copies data between filesystems and writes logs; duplicate source paths can raise `DuplicationException`. `HadoopArchives` creates archive files under a destination path. `Logalyzer` reads and writes log archives and analysis output through filesystem and MapReduce APIs.

Utility side effects include directory creation/checking, native library loading or disabled-use flags in `JobConf`, host-file rereads, daemon thread creation, command-line configuration mutation, and jar manifest inspection.

## Dependencies and integration points

Metrics APIs integrate with `org.apache.hadoop.metrics.MetricsRecord` and the older Hadoop metrics/JMX update flow.

Network APIs depend on Java networking and naming (`InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, DNS/JNDI naming exceptions), Java NIO channels, Hadoop `Configuration`, commons logging, and cluster components that consume rack topology. `NetUtils` also bridges old and new config keys during server-address migration.

Record I/O runtime depends on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, collections (`ArrayList`, `TreeMap`), `WritableComparable`, `WritableComparator`, `Text.Comparator`, and `IOException`. Its generated-code model and compiler depend on the Record IDL grammar, JavaCC parser artifacts, Ant tasks, and code generation target language selection.

Record metadata integrates with the Record runtime by extending `Record` and using `RecordInput`/`RecordOutput`. `TypeID` constants bridge runtime values, metadata skipping, and compiler-generated type declarations.

Security APIs depend on Hadoop `Configuration`, Hadoop `Writable`, Java security login exceptions, Unix user/group lookup, and per-thread caller context used by filesystem and RPC code.

Tools integrate with `Tool`, `Configuration`, Hadoop filesystems (`Path`), old MapReduce APIs (`JobConf`, `Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`), Hadoop writables (`Text`, `LongWritable`, `WritableComparable`), and command-line `main` entry points.

Utility classes integrate with Commons CLI, Java files, Java threads, Java comparators, Hadoop `Progressable`, `JobConf`, and native Hadoop library loading.

## Risks and compatibility notes

This is a line-bounded chunk with partial boundary classes. `MetricsLongValue` starts before the range and `PriorityQueue.clear` completes after the range, so final per-file reconciliation should merge adjacent chunks before making whole-file conclusions.

The XML is a public API contract for an old Hadoop release. Even misspelled Javadocs and unusual signatures are compatibility-relevant because downstream consumers may compare JDiff output exactly or depend on generated API shapes.

Metrics classes are synchronized and interval-sensitive. Changing reset timing, previous-interval visibility, min/max reset semantics, or whether unchanged values are published would alter metrics dashboards and JMX consumers.

Rack topology APIs affect placement and scheduling. Bad path normalization, wrong distance calculations, incorrect same-rack checks, or inconsistent random selection under include/exclude scopes can cause poor data locality or placement imbalance. Static DNS resolutions and script-based mappings are process/configuration sensitive and can hide real DNS changes.

Socket wrappers are resource and timeout sensitive. NIO channel readiness, socket close semantics, transfer loops, and factory equality/hash behavior can affect RPC connection reuse and failure modes. `NetUtils.createSocketAddr` must preserve support for legacy endpoint string formats.

Record I/O is a legacy serialization surface, so wire compatibility is the main risk. Variable-length integer encoding, binary float/double parsing, CSV/XML escaping, buffer aliasing, record field order, collection traversal, and raw comparator behavior must remain stable for existing data and generated classes.

The Record compiler exposes generated JavaCC internals as public API. Token IDs, lexical state names, parser method names, public fields, exception message formatting, and stream line/column accounting can be consumed by tests or downstream tools even though they look implementation-specific.

Security identity APIs predate later Hadoop UGI designs and rely on mutable thread-local state plus configuration persistence. Incorrect save/read formatting, immutable UGI handling, group order, equality/hash code, or thread scoping can create authorization bugs.

Tools are high-blast-radius utilities. DistCp and HadoopArchives operate on distributed data and can overwrite, duplicate, omit, or incorrectly archive large path sets if argument parsing, path listing, duplicate detection, logging, or failure handling changes.

Utility algorithms have hidden assumptions. `PriorityQueue` has fixed maximum size and throws if `put` exceeds capacity; `insert` drops elements based on `lessThan(element, top())`. Sorters assume `IndexedSortable.compare` is consistent and `swap` is correct. `GenericsUtil.toArray(List)` documents failure on empty lists, so callers may depend on that exception.

## Test signals

JDiff validation should check this XML range remains well-formed when combined with neighbors and preserves package/class/interface boundaries, inheritance, implemented interfaces, field names and types, method overloads, declared exceptions, synchronized/static/final flags, visibility, deprecation markers, and embedded Javadocs.

Metrics tests should cover unchanged-value push suppression for `MetricsLongValue`, interval delta rollover for `MetricsTimeVaryingInt`, operation count and average-time reporting for `MetricsTimeVaryingRate`, min/max timing updates, `resetMinMax`, and synchronized concurrent increments.

Network tests should cover DNS interface lookup fallback, reverse DNS failure propagation, rack mapping one-to-one list behavior, script mapping configuration and missing-script behavior, socket factory lookup from class-specific and default config keys, static hostname resolution add/get/list, wildcard server-address conversion, socket stream timeout waits, channel close behavior, SOCKS proxy configuration, socket factory equality/hash code, topology add/remove/contains, rack and leaf counts, distance, same-rack checks, random choice with exclusions, available-node counting, and pseudo-sort ordering.

Record I/O runtime tests should cover binary/CSV/XML round trips for every primitive plus string, buffer, record, vector, and map; tagged and tagless generated-record serialization; `Index.done/incr` collection traversal; `Buffer` set/copy alias behavior, append, reset, truncate, capacity growth, comparison, equality, clone, and charset conversion; zero-compressed int/long edge cases; byte-array lexicographic compare; raw `RecordComparator` registration; and legacy encoded-data compatibility.

Record compiler tests should cover parsing modules, includes, records, fields, primitive types, maps, vectors, comments, and syntax errors; `Rcc.driver` return codes; `ReInit` reuse; parse exception message content; token line/column positions; token-manager lexical states; Ant `RccTask` file and fileset handling; destination directory output; and `failonerror` behavior.

Record metadata tests should cover base `TypeID` singleton equality/hash code, map/vector/struct equality, `FieldTypeInfo` equality, `RecordTypeInfo` add/get/nested lookup behavior, metadata serialize/deserialize round trips, `compareTo` behavior, and `meta.Utils.skip` for each primitive and composite type.

Security tests should cover Unix login success/failure paths, config save/read of UGI strings, immutable UGI creation, `Writable` serialization round trips, username/group accessors, equality/hash code, string conversion, `getCurrentUGI` and `setCurrentUGI` thread isolation, and `UserGroupInformation.readFrom(Configuration)`.

Tool tests should cover `DistCp.copy` with single sources, source lists, duplicate sources, missing/unreadable files, log path use, ignore-read-failure behavior, `run` exit codes, random ID format, archive creation with multiple paths, Logalyzer archive/analyze flows, regex mapper matches and nonmatches, and log comparator raw-byte ordering.

Utility tests should cover daemon constructors setting daemon status and preserving runnable, directory creation and disk-error exceptions, generic option parsing effects on `Configuration` and remaining args, generic usage printing, generic array conversion including empty-list failure for the one-argument overload, heap sort with and without `Progressable`, host include/exclude refresh, merge sort index behavior, native library loaded/unloaded reporting and JobConf flag persistence, platform name output, jar main-class detection, and `PriorityQueue` heap operations including full-queue insert/drop behavior and `adjustTop`.

### subset-b-007272: lines 43568-44778

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 43568-44778

## Scope

This chunk is the closing section of the Hadoop 0.18.1 JDiff API XML for package `org.apache.hadoop.util`. It starts in the tail of `PriorityQueue`, then covers public API metadata for `ProgramDriver`, `Progress`, `Progressable`, `QuickSort`, `ReflectionUtils`, `RunJar`, `ServletUtil`, `Shell` and nested shell helper classes, `StringUtils`, `Tool`, `ToolRunner`, `VersionInfo`, and `XMLUtils`. The file is an API snapshot, so it documents signatures, visibility, exceptions, fields, inheritance, and Javadoc text rather than Java implementation bodies.

## Purpose

The covered APIs form Hadoop's common utility layer around command dispatch, progress reporting, indexed sorting, reflective object construction, jar launching, web UI helpers, operating-system command execution, string and time formatting, generic command-line option integration, build metadata, and XML transformation.

Within the source tree this JDiff XML is used for API comparison and compatibility tracking. The practical behavioral contract described by this chunk is the public Hadoop 0.18.1 utility surface that downstream tools, examples, MapReduce applications, JSPs, and server startup code could compile against.

## Important APIs, Types, and Functions

### `PriorityQueue` tail

The chunk begins with the final `clear()` method and class documentation for `org.apache.hadoop.util.PriorityQueue`. The class maintains a partial ordering so the least element can be found in constant time, while `put()` and `pop()` are logarithmic. Because the start of the class is outside this range, this chunk only establishes the clearing behavior and high-level performance contract.

### Program and progress utilities

- `ProgramDriver` is a registry and dispatcher for executable programs. `addClass(String name, Class mainClass, String description)` registers a named class, and `driver(String[] args)` uses `args[0]` to find a registered program and invoke its `main` method with the remaining arguments. Both methods can throw broad reflection or program exceptions through `Throwable`.
- `Progress` models hierarchical execution phases. A root is created with the public constructor, children are added with `addPhase()` or `addPhase(String status)`, `startNextPhase()` advances among siblings, `phase()` returns the current child, `complete()` advances the parent, `set(float)` records leaf progress, `get()` reports root progress, and `setStatus(String)` attaches status text. Several mutating/read methods are synchronized, indicating intended use from concurrently observed execution paths.
- `Progressable` is a single-method callback interface with `progress()`. Long-running clients call it to tell the Hadoop framework that work is still active and avoid timeout assumptions.

### Sorting and reflection

- `QuickSort` is a final `IndexedSorter` implementation. It sorts an `IndexedSortable` range with `sort(s, p, r)` and has an overload accepting a `Progressable` reporter. The protected static `getMaxDepth(int)` returns `2 * ceil(log(n))`; when recursion depth falls below that limit the algorithm switches to `HeapSort`, making the API an introsort-style quicksort wrapper.
- `ReflectionUtils` centralizes reflective construction and diagnostics. `setConf(Object, Configuration)` injects configuration into configurable objects, `newInstance(Class<?>, Configuration)` creates and configures objects, `setContentionTracing(boolean)` toggles contention diagnostics, `printThreadInfo(PrintWriter, String)` and `logThreadInfo(Log, String, long)` dump thread stacks, and generic `getClass(T)` returns a correctly typed `Class<T>`.

### Launching, servlets, shell, and strings

- `RunJar` provides `unJar(File, File)` and `main(String[])`. It unpacks job jars and runs the main class from the manifest or command line.
- `ServletUtil` exposes `initHTML(ServletResponse, String)`, `getParameter(ServletRequest, String)`, `htmlFooter()`, and public constant `HTML_TAIL`. It standardizes simple servlet/JSP page setup and treats all-whitespace request parameters as absent.
- `Shell` is an abstract base for running Unix commands with optional re-execution throttling. Static helpers expose command arrays for groups and permissions and derive a `ulimit` memory command from a `JobConf`. Subclasses set environment and working directory, implement `getExecString()` and `parseExecResult(BufferedReader)`, and call protected `run()`. Public inspection methods expose the current `Process` and exit code. `execCommand(String[])` is a simple static command execution helper.
- `Shell.ExitCodeException` extends `IOException` with `getExitCode()`, preserving failed process status.
- `Shell.ShellCommandExecutor` is a concrete nested shell runner for fixed commands, optional working directory, and optional environment. `execute()` runs it, `getOutput()` returns captured output, and the Javadoc warns that output is stored as-is and should be small.
- `StringUtils` is a broad static helper class. APIs cover exception stack traces, simple hostnames, human-readable powers-of-1024 integers, percentages, comma-joined arrays, byte/hex conversion, URI and `Path` conversion, elapsed-time formatting, date-plus-duration formatting, comma-separated string collections, escaped splitting, escaping/unescaping separators, hostname lookup without throwing, and startup/shutdown logging. Public constants define comma and escape characters.

### Tooling, version, and XML APIs

- `Tool` extends `Configurable` and defines `run(String[] args): int`. Its Javadoc establishes the Hadoop command-line convention: `ToolRunner` handles generic Hadoop options and the tool handles application-specific options.
- `ToolRunner` provides `run(Configuration, Tool, String[])`, `run(Tool, String[])`, and `printGenericCommandUsage(PrintStream)`. It integrates with `GenericOptionsParser`, mutates or creates the `Configuration`, sets it on the `Tool`, then delegates to `Tool.run`.
- `VersionInfo` exposes static build metadata: Hadoop version, source-control revision, build date, build user, repository URL, combined build version, and a `main(String[])` printer.
- `XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` applies a stylesheet to XML and declares `TransformerConfigurationException` and `TransformerException`.

## Control Flow

`ProgramDriver` flow is registry first, dispatch later: callers register named classes, then `driver()` reads the first command-line token, locates the matching class, and reflectively invokes its `main` entry point. Errors are intentionally not narrowed, because program code and reflection can both fail.

`Progress` flow is tree-shaped. Application code builds phases, descends to the current `phase()`, sets leaf progress, and calls `complete()` or `startNextPhase()` to advance. The root `get()` aggregates subphase state into a single float for reporting.

`QuickSort` flow is range-based sorting over an `IndexedSortable`. It uses quicksort until the maximum recursion depth is exhausted, then falls back to `HeapSort`; the reporter overload allows long sorts to call back through `Progressable`.

`Shell` flow is template-method based. Subclasses provide a command vector and parser, optional environment and working directory are configured on the base, `run()` decides whether the interval allows execution, starts the process, exposes it through `getProcess()`, parses stdout through `parseExecResult()`, and records the exit code. `ShellCommandExecutor` supplies the common parser that captures all output into a string.

`ToolRunner` flow is the standard Hadoop CLI path: parse generic options with a `Configuration`, set the resulting configuration on the `Tool`, call `Tool.run(args)`, and return its integer exit status.

## State and Persistence Behavior

The XML itself is static API metadata and has no runtime state. The described Java APIs, however, imply several stateful components:

- `ProgramDriver` holds an in-memory registry of command names, classes, and descriptions.
- `Progress` holds an in-memory tree of phases, current phase indexes, status strings, and progress floats. Some methods are synchronized, but `complete()` and `toString()` are not marked synchronized in this API snapshot.
- `ReflectionUtils` likely maintains static diagnostic state for contention tracing and last-log throttling, based on the exposed toggles and `logThreadInfo(..., minInterval)`.
- `Shell` instances hold command execution state: environment, working directory, last execution timing, current process, exit code, and parsed output in subclasses. `ShellCommandExecutor` additionally persists captured command output in memory.
- `StringUtils`, `RunJar`, `ServletUtil`, `ToolRunner`, `VersionInfo`, and `XMLUtils` are primarily stateless static helpers, except for interactions with files, servlet responses, logs, configuration objects, and build metadata resources.

Persistent external effects are limited to helper behavior: `RunJar.unJar` writes extracted jar contents to a directory, shell commands may mutate the host depending on the command, servlet utilities write HTTP response content, `startupShutdownMessage` writes logs, and XML transforms write to the supplied `Writer`.

## Dependencies and Integration Points

These APIs sit at the intersection of Hadoop Common, MapReduce, servlet UI code, logging, and Java platform services:

- Hadoop types: `Configuration`, `Configurable`, `JobConf`, `Path`, `IndexedSortable`, `IndexedSorter`, `HeapSort`, `GenericOptionsParser`, `Tool`, and `Progressable`.
- Java platform types: reflection `Class`, `Throwable`, `Process`, `File`, `BufferedReader`, `IOException`, `PrintWriter`, `PrintStream`, `DateFormat`, `URI`, collections, servlet request/response interfaces, and JAXP transformer exceptions.
- External/common libraries: `org.apache.commons.logging.Log`.
- Operational integration: `Shell` assumes Unix-like command semantics for many constants but exposes `WINDOWS` and returns `null` for memory-limit commands on non-Unix/Cygwin/Windows platforms.
- Application integration: MapReduce applications implement `Tool`, delegate generic option handling to `ToolRunner`, report activity through `Progressable`, and may rely on `StringUtils` and `VersionInfo` for diagnostics and UI output.

## Risks and Edge Cases

- `ProgramDriver` exposes `Throwable` from both registration and dispatch. Callers need top-level error handling so one example program does not terminate a larger launcher without diagnostics.
- `Progressable` is a liveness signal. Missing or infrequent `progress()` calls around long operations can still trigger framework timeouts.
- `Progress` synchronization is mixed. The API marks several phase/progress methods synchronized, but not every public method is synchronized, so concurrent status rendering and updates need tests for consistent output.
- `QuickSort` depends on correct `IndexedSortable.compare` and `swap` implementations. Bad comparator ordering can cause incorrect results, while the heap fallback is only useful if the recursion-depth guard is correct.
- `ReflectionUtils.newInstance` relies on accessible no-argument construction and optional configuration injection. Misconfigured classes, security managers, or missing constructors can fail at runtime.
- `RunJar.unJar` is security-sensitive because jar entries can contain unexpected paths. The API snapshot does not show path traversal defenses, so implementation review and tests are important.
- `ServletUtil.initHTML` and `htmlFooter` generate HTML, while `getParameter` only trims whitespace semantics. Callers still need escaping for user-provided values.
- `Shell` is platform-sensitive and command-injection-sensitive. APIs accept raw command arrays, environment maps, and working directories; callers must avoid constructing commands from untrusted strings.
- `ShellCommandExecutor` stores command output in memory and is documented for small output only. Large stdout streams can cause memory pressure.
- `StringUtils.hexStringToByte` depends on even-length, valid hex input; malformed strings should be tested. Escaped split/unescape helpers must handle trailing escape characters, escaped escape characters, and empty tokens.
- `ToolRunner` mutates the `Tool` configuration after parsing generic options. Tools that read configuration in constructors can observe stale values.
- `VersionInfo` depends on build/package metadata being present in the runtime artifact; development or shaded jars may report missing or placeholder values.
- `XMLUtils.transform` surfaces transformer exceptions directly and writes to caller-owned streams, so partial output on transformation failure is possible.

## Test Signals

Useful validation for this API area should include:

- JDiff/API checks confirming these classes, methods, fields, visibility, checked exceptions, and inheritance relationships remain stable for Hadoop 0.18.1 compatibility.
- `ProgramDriver` registration and dispatch tests for successful command routing, unknown command usage behavior, empty arguments, and propagation of exceptions thrown by target `main`.
- `Progress` tree tests for nested phase aggregation, named statuses, `complete()`, `startNextPhase()`, concurrent `set()`/`get()`, and `toString()` output.
- `Progressable` timeout-oriented integration tests around long-running map/reduce, filesystem, or sort operations.
- `QuickSort` tests over empty, singleton, sorted, reverse-sorted, duplicate-heavy, and adversarial comparator ranges, with a reporter that verifies progress callbacks.
- `ReflectionUtils` tests for `Configurable` and non-`Configurable` classes, constructor failure, typed `getClass`, thread-info printing, and min-interval throttling in `logThreadInfo`.
- `RunJar` tests for manifest main class, command-line main class, missing main class, jar extraction, duplicate entries, nested directories, and unsafe jar entry names.
- `ServletUtil` tests for response content type/header generation, whitespace-only request parameters, normal parameters, and footer output.
- `Shell` tests for environment and working directory propagation, nonzero exit status and `ExitCodeException`, output capture, interval gating, Windows/null ulimit behavior, and large-output boundaries.
- `StringUtils` tests for stack trace stringification, hostname simplification, percentage and byte formatting, byte/hex round trips, URI/path conversion, escaped split/escape/unescape edge cases, and elapsed-time formatting including negative intervals.
- `Tool`/`ToolRunner` integration tests for generic option parsing, configuration mutation, application arguments preserved after generic parsing, return-code propagation, and printed generic usage.
- `VersionInfo` tests against known build metadata resources and fallback behavior when metadata is absent.
- `XMLUtils.transform` golden-output tests plus invalid stylesheet/XML failure tests.
