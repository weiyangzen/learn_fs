# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007258`: lines 1-6312, `Docs/researches/chunks/subset-b-007258_research.md`
- `subset-b-007259`: lines 6313-12474, `Docs/researches/chunks/subset-b-007259_research.md`
- `subset-b-007260`: lines 12475-18820, `Docs/researches/chunks/subset-b-007260_research.md`
- `subset-b-007261`: lines 18821-25080, `Docs/researches/chunks/subset-b-007261_research.md`
- `subset-b-007262`: lines 25081-31138, `Docs/researches/chunks/subset-b-007262_research.md`
- `subset-b-007263`: lines 31139-37383, `Docs/researches/chunks/subset-b-007263_research.md`
- `subset-b-007264`: lines 37384-43272, `Docs/researches/chunks/subset-b-007264_research.md`

## Chunk Research

### subset-b-007258: lines 1-6312

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 1-6312

## Scope and Purpose

This chunk is the opening portion of a generated JDiff XML API description for `hadoop 0.17.0`, generated from Hadoop's Javadoc on 2008-06-10. It is not executable Hadoop code; it is a machine-readable public API snapshot used by JDiff to compare exposed packages, classes, interfaces, constructors, methods, fields, inheritance, deprecation status, and Javadoc text across releases. The file begins with `<api name="hadoop 0.17.0" jdversion="1.1.0">` and records the doclet command line, classpath, source path, API directory, and API name used to generate the snapshot.

The chunk covers the top-level Hadoop version annotation, the configuration API in `org.apache.hadoop.conf`, a large part of the HDFS API in `org.apache.hadoop.dfs`, the datanode metrics package, and the beginning of the namenode metrics package. Line 6312 stops in the middle of the `NameNodeStatisticsMBean` documentation, so this report intentionally describes only the visible chunk and leaves later package closure and any following APIs to later chunks.

## Document Structure

The XML is organized as package elements containing class or interface entries. Each type entry records modifiers such as `abstract`, `static`, `final`, `visibility`, and `deprecated`, plus relationships through `extends` and `implements`. Constructors, methods, fields, parameters, exceptions, return types, and documentation are represented as nested XML tags. Documentation is stored in CDATA blocks and often preserves Javadoc markup such as `{@link ...}`, `<pre>`, `<ol>`, and HTML tables/lists.

Important structural signals in this chunk:

- `org.apache.hadoop`: contains `HadoopVersionAnnotation`.
- `org.apache.hadoop.conf`: contains `Configurable`, `Configuration`, `Configuration.IntegerRanges`, and `Configured`.
- `org.apache.hadoop.dfs`: contains core HDFS public API, admin tools, datanode/namenode endpoints, servlets, constants, fsck, upgrade, and metrics-adjacent classes.
- `org.apache.hadoop.dfs.datanode.metrics`: contains datanode metrics publishers and JMX interfaces.
- `org.apache.hadoop.dfs.namenode.metrics`: begins namenode/FSNamesystem metrics and JMX interfaces.

## Important APIs and Types

`HadoopVersionAnnotation` is recorded as a public abstract annotation type implementing `java.lang.annotation.Annotation`. Its purpose is to capture the Hadoop version used at compile time.

`Configurable` defines the standard configuration injection contract with `setConf(Configuration)` and `getConf()`. `Configured` implements that contract as a base class, providing constructors with or without an initial `Configuration`.

`Configuration` is a central public class implementing `Iterable<Map.Entry<String,String>>`. The exposed API covers resource loading from classpath names, URLs, and Hadoop `Path`s; value retrieval with variable expansion; raw retrieval without expansion; typed accessors and setters for integers, longs, floats, booleans, string arrays, and classes; classloader control; resource lookup; iteration; serialization of non-default properties to an output stream; quiet mode; and a debugging `main`. Its Javadoc defines the resource layering model (`hadoop-default.xml`, then `hadoop-site.xml`, then application-added resources), final parameters that cannot be overridden by later resources, and property/system-property variable expansion. `Configuration.IntegerRanges` parses range expressions like `2-3,5,7-` and exposes `isIncluded(int)`.

The HDFS portion starts with exception and tool classes. `AlreadyBeingCreatedException`, `LeaseExpiredException`, `NotReplicatedYetException`, and `SafeModeException` represent namespace/write-state failures visible to clients or internal callers. `Balancer`, `DFSAdmin`, and `DFSck` are public command-style tools implementing `Tool` or extending `FsShell`; their methods expose `run`, `main`, administrative commands, safe mode operations, upgrade progress, metadata save, refresh nodes, and reporting. The `Balancer` Javadoc is especially substantive: it documents threshold-based balancing, per-iteration movement limits, bandwidth configuration, monitoring output, single-instance protection, and exit codes.

`DistributedFileSystem` is the primary public `FileSystem` implementation for HDFS clients. The visible API includes URI initialization, working directory and home directory access, default block size and replication, block location lookup, checksum verification toggling, `open`, `create`, `rename`, `delete`, recursive delete, content length and summary, `listStatus`, `mkdirs`, close, disk status, raw capacity and used-space queries, datanode stats, safe mode control, node refresh, upgrade finalization/progress, `metaSave`, checksum failure reporting, file status, permissions, and owner changes. `ChecksumDistributedFileSystem` wraps a `DistributedFileSystem` behind `ChecksumFileSystem` primarily for backward compatibility and tests even though DFS already performs native checksums.

`DataNode` is recorded as both a daemon/program and a `Runnable` implementing `FSConstants`. Its public surface includes address lookup, static singleton access, NameNode/self address access, shutdown, `offerService`, retrying `run`, block-report scheduling, access to the `FSDatasetInterface` for tests, and `main`. Its documentation describes the DataNode as storing local disk blocks, serving client and peer datanode reads/writes, reporting block tables to the NameNode, and polling the NameNode because the NameNode does not initiate direct connections.

`DatanodeID`, `DatanodeInfo`, and `DatanodeDescriptor` model datanode identity and status. `DatanodeID` is `WritableComparable` with name, storage ID, info port, host/port helpers, equality/hash/compare, and binary serialization. `DatanodeInfo` extends it and implements `org.apache.hadoop.net.Node`, adding capacity, DFS used, remaining space, last update, xceiver count, rack/network location, hostname, formatted reports, topology parent/level, admin state, and serialization. `DatanodeDescriptor` adds NameNode-internal liveness and block/location tracking; the doc notes that it is not sent to clients or datanodes and is not persisted in `fsImage`.

`DataChecksum` provides checksum utilities for DFS data transfers and implements `java.util.zip.Checksum`. It exposes factories from type/bytes-per-checksum, serialized headers, or `DataInputStream`, plus header/value writing, value comparison, checksum metadata access, reset, and update methods. Constants include `HEADER_LEN`, `CHECKSUM_NULL`, and `CHECKSUM_CRC32`.

`FSConstants` is a broad public constants interface. It exposes data transfer and legacy client operation opcodes, status codes, data transfer version, completion status codes, block invalidation chunk size, heartbeat/block-report intervals, lease periods, read/write timeouts, path limits, buffer sizes, default block size, socket size, integer size, and layout version. Associated enum-like nested types include `CheckpointStates`, `DatanodeReportType`, `NodeType`, `SafeModeAction`, `StartupOption`, and `UpgradeAction`.

`FSDatasetInterface` defines the storage abstraction behind DataNode block persistence and implements `FSDatasetMBean`. It exposes metadata length and input streams, metadata existence, block length, block input streams with optional seek offset, `writeToBlock`, `finalizeBlock`, `unfinalizeBlock`, block reports, validity checks, invalidation, data-directory health checks, shutdown, and stream position get/set for recovery. Nested helper classes `BlockWriteStreams` and `MetaDataInputStream` represent paired data/checksum output streams and metadata streams with length.

HTTP/servlet integration appears through `FileDataServlet`, `FsckServlet`, `GetImageServlet`, `ListPathsServlet`, `StreamFile`, and `SecondaryNameNode.GetImageServlet`. These classes integrate HDFS with Jetty/servlet endpoints for reading file data, running fsck from the NameNode, transferring image/edit files for checkpointing, listing paths as XML, and streaming files. `HftpFileSystem` and `HsftpFileSystem` implement read-only HTTP/HTTPS access, backed by `ListPathsServlet` and `FileDataServlet`, with URL connection opening, `open`, `listStatus`, and `getFileStatus`; mutating filesystem methods are present because they satisfy `FileSystem`, but the class documentation says the interface is limited and read-only.

`JspHelper` supports the NameNode web UI and JSP pages: random/best datanode selection, block streaming in ASCII, live/dead datanode status, HTML table helpers, safe mode/inode/upgrade status text, datanode list sorting, path link rendering, goto forms, page titles, and percentage graphs. It exposes static configuration and web user/group fields.

`LocatedBlocks` is a `Writable` collection of `LocatedBlock` entries with file length, indexed access, count, list access, and serialization.

`NameNode` is the largest visible type in this chunk. It implements `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, and `FSConstants`, exposing both client-facing namespace APIs and datanode/secondary namenode protocol methods. Client-protocol methods include block location lookup, create, replication and permission/owner changes, add/abandon/complete block/file writes, bad-block reporting, preferred block size, rename/delete, deprecated `exists`, mkdirs, lease renewal, listings, file info, stats, datanode report, safe mode, content summary, and `fsync`. Datanode-protocol methods include registration, heartbeat, block report, block received, error report, version request, upgrade command processing, block CRC upgrade location lookup, request/version verification, and command-oriented responses. Namenode/checkpoint methods include edit-log size, roll edit log, roll fs image, fsImage/fsEdit file locations, checkpoint upload validation and completion, and NameNode address lookup. Static/service methods include format, metrics access, stop, join, and `main`. The class documentation states that the NameNode owns the namespace table persisted on disk and the block-to-machine table rebuilt at startup, while `FSNamesystem` performs most filesystem management.

`NamenodeFsck` and nested `FsckResult` represent NameNode-side filesystem checks. The tool can inspect files/directories for missing blocks, under-replication, and over-replication, and can optionally move corrupt files to `/lost+found` or delete them. `FsckResult` tracks health, missing block IDs and size, excessive replicas, actual and intended replication, missing replicas, directory/file/block totals, total size, corrupt files, and string rendering.

Upgrade APIs include `Upgradeable` and `UpgradeStatusReport`. `Upgradeable` ties upgrade objects to layout versions and node types and exposes description, percent status, start/complete hooks returning `UpgradeCommand`, and detailed status reports. `UpgradeStatusReport` is a `Writable` with version, percent status, finalized flag, text rendering, and serialization.

Metrics APIs include `NameNodeMetrics`, `DataNodeMetrics`, `DataNodeStatistics`, `DataNodeStatisticsMBean`, `FSDatasetMBean`, `FSNamesystemMBean`, `NameNodeStatistics`, and the beginning of `NameNodeStatisticsMBean`. They expose Hadoop metrics `Updater` hooks, JMX MBean registration/shutdown/reset, counters and rates for block reads/writes/replication/removal/verification, client locality, read/write/metadata/copy/replace block operations, heartbeats, block reports, NameNode file operations, journal transactions and syncs, safe mode time, image load time, capacity, file totals, and live/dead datanode counts.

## Control Flow and Runtime Behavior

Because this is a generated API snapshot, the XML itself has no runtime control flow. The meaningful control-flow information is in the documented APIs it records.

Configuration flow is resource-layered: default resources load first, site resources next, and application resources later; later resources override earlier ones unless a prior value is marked final. Accessors perform variable expansion unless callers use `getRaw`.

HDFS client control flow centers on `DistributedFileSystem` calling NameNode APIs for namespace metadata and block locations, then reading or writing blocks through datanodes. Creation proceeds through `create`, `addBlock`, datanode writes, lease renewal, `complete`, and potentially `fsync`; failures can surface as lease expiration, incomplete replication, or already-being-created exceptions.

DataNode flow is polling-oriented. `run` retries `offerService` until shutdown, and `offerService` repeatedly invokes NameNode remote methods. The DataNode sends heartbeats and block reports, receives commands to transfer, invalidate, copy, replace, or otherwise manage blocks, and uses `FSDatasetInterface` for local block and checksum persistence.

NameNode flow spans multiple protocols: clients mutate/query namespace and block mappings, datanodes report storage state and block inventory, and secondary namenodes/checkpointing tools roll edit logs/images and transfer checkpoint files over HTTP. The NameNode doc explicitly distinguishes persisted namespace data from reconstructed block location data.

Administrative flow appears through `DFSAdmin` and `Balancer`. Admin commands call into distributed filesystem/NameNode controls for safe mode, refresh nodes, upgrade status/finalization, reports, and metadata dumps. The balancer performs iterative cluster-utilization analysis and block movement until balanced, unable to move, no progress, IO failure, or duplicate balancer detection.

HTTP/HFTP flow maps servlet requests into HDFS metadata/data access. `ListPathsServlet` returns XML listings, `FileDataServlet` redirects file-data requests to datanodes, `GetImageServlet`/`SecondaryNameNode.GetImageServlet` transfer image/edit files for checkpointing, `FsckServlet` invokes NameNode-side fsck, and `StreamFile` streams data to web clients.

Metrics flow is periodic: metrics classes implement `Updater.doUpdates(MetricsContext)`, JMX-facing statistics objects read sampled metric values, and `resetAllMinMax` clears min/max timing windows. Documentation notes that sampled averaging depends on a metrics context with update calls.

## State and Persistence Behavior

The XML persists an API state, not live runtime state. It preserves generation metadata, public API signatures, inheritance, deprecation markers, and Javadocs for Hadoop 0.17.0. Any consumer should treat it as an artifact derived from source and classpath state at generation time.

Runtime persistence behavior described by the APIs includes:

- `Configuration` stores and writes non-default properties, resolves resources from classpath/local filesystem, and respects final parameters.
- DataNodes persist block bytes and checksum metadata on local disks through `FSDatasetInterface`; block reports reconstruct NameNode block mappings.
- NameNode persists the namespace table on disk as image/edit state, while the block-to-datanode table is rebuilt at startup from datanode reports.
- `SecondaryNameNode` performs periodic checkpoints by coordinating with the primary NameNode, rolling edit logs/images, and transferring image/edit files.
- Upgrade APIs track layout versions, upgrade percentage, finalized state, and broadcast upgrade commands.
- Metrics classes hold counters/rates and expose them through Hadoop metrics and JMX, with explicit shutdown/unregister hooks.

## Dependencies and Integration Points

The generation comment lists a broad Hadoop 0.17-era classpath: commons-cli, commons-codec, commons-httpclient, commons-logging, jets3t, Jetty 5.1.4, Jetty JSP extensions, JUnit, KFS, log4j, servlet API, xmlenc, Hadoop `conf`, Ant libraries, Xerces, XML APIs, and JDK tools. Those dependencies are generation-time inputs and also reveal the runtime ecosystem used by the exposed APIs.

Visible API dependencies include:

- Java core IO/network/reflection/concurrency-adjacent APIs: `IOException`, `DataInput`, `DataOutput`, streams, `File`, `URI`, `URL`, `HttpURLConnection`, `InetSocketAddress`, `ClassLoader`, `Class`, `Iterator`, collections, and `Checksum`.
- Servlet/JSP APIs: `HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `ServletException`, and `JspWriter`.
- Hadoop core APIs: `Configuration`, `Path`, `FileSystem`, `ChecksumFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FsShell`, `Progressable`, `Tool`, `Writable`, `WritableComparable`, metrics types, security/user group types, net `Node`, and permission `FsPermission`.
- HDFS protocol/storage types referenced but not always defined in this chunk, such as `Block`, `LocatedBlock`, `BlocksWithLocations`, `DatanodeRegistration`, `DatanodeCommand`, `NamespaceInfo`, `UpgradeCommand`, `BlockCrcInfo`, `DFSFileInfo`, `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, and `FSNamesystem.SafeModeInfo`.
- XML output support through `org.znerd.xmlenc.XMLOutputter`.

## Risks and Maintenance Notes

This is a generated file, so hand edits are high risk: they can make API comparisons lie about the actual source or break JDiff tooling expectations. Regeneration should be preferred when Hadoop source or public APIs change.

The chunk is a partial view of a 43,272-line XML file. It begins at the XML root but ends mid-documentation inside the namenode metrics section, so consumers must not infer that the API is complete from this chunk alone.

Many deprecated elements are still present for compatibility, including older constructors taking `InetSocketAddress`/`Configuration`, `DistributedFileSystem.getName`, and `NameNode.exists`. API-diff consumers should preserve deprecation messages exactly because they are compatibility signals.

The public API exposes many internal-looking HDFS classes, constants, and mutable metrics fields. Compatibility changes to these signatures, field names, enum types, or serialization methods can affect downstream tests, tools, administrative scripts, web UI integrations, and older clients.

Several APIs encode wire/storage compatibility concerns: `FSConstants.DATA_TRANSFER_VERSION`, `LAYOUT_VERSION`, `Writable` read/write methods, datanode registration/version verification, upgrade reports, and checksum headers. Any generated diff against these areas is likely significant.

The documentation contains typos and historical package references, but those are part of the API snapshot and may be relevant for documentation diffs. The XML encoding is declared as `iso-8859-1`; tooling should preserve or correctly decode it.

## Test Signals

Useful validation for this chunk research is structural rather than unit-test based:

- The source file has 43,272 lines, and this work item covers lines 1-6312.
- The chunk starts with a valid XML declaration and `<api>` root metadata for `hadoop 0.17.0`.
- Package/type boundaries in this chunk include `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.dfs`, `org.apache.hadoop.dfs.datanode.metrics`, and `org.apache.hadoop.dfs.namenode.metrics`.
- Public APIs with serialization or compatibility implications are visible: `Configuration.write`, `DatanodeID.write/readFields`, `DatanodeInfo.write/readFields`, `LocatedBlocks.write/readFields`, `UpgradeStatusReport.write/readFields`, and many `Writable`/`WritableComparable` implementors.
- Administrative and protocol behavior is documented through `Balancer`, `DFSAdmin`, `DFSck`, `DistributedFileSystem`, `DataNode`, `NameNode`, `SecondaryNameNode`, and servlet endpoints.
- Metrics/JMX exposure can be checked through `Updater.doUpdates`, `resetAllMinMax`, MBean interfaces, and public metric fields.

### subset-b-007259: lines 6313-12474

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 6313-12474

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.17.0, not executable implementation source. It starts at the tail of `org.apache.hadoop.dfs.namenode.metrics.NameNodeStatisticsMBean` documentation, then covers complete public API entries for `org.apache.hadoop.filecache.DistributedCache`, most of the old `org.apache.hadoop.fs` package, the KFS and S3 filesystem adapters, filesystem permission value types, `org.apache.hadoop.fs.shell.Count`, and the beginning of `org.apache.hadoop.io`.

The source records API compatibility metadata: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadocs. Runtime control flow and private state are not present in the XML, so behavioral notes below are based on the public contracts visible in this chunk.

The chunk is partial at both boundaries. The first lines finish a NameNode metrics MBean entry owned by the previous package, and the last line stops inside the class documentation for `org.apache.hadoop.io.ArrayWritable`; adjacent chunks are needed for complete reports on those partial classes/packages.

## Purpose

The `org.apache.hadoop.filecache` section documents the MapReduce `DistributedCache` API used to localize read-only files, archives, and classpath additions for jobs. It stores cache URIs, timestamps, localized paths, symlink flags, and classpath entries in `Configuration`, then exposes helper methods used by task localization to copy, unpack, link, validate, release, and purge cached resources.

The `org.apache.hadoop.fs` section is the main filesystem API for this Hadoop release. It defines the abstract `FileSystem` contract, core path and stream abstractions, metadata records, local filesystem implementations, checksum wrappers, command-line shell support, trash behavior, disk-usage helpers, and utilities for copying, deleting, linking, chmod, archive extraction, and temporary-file replacement.

The `org.apache.hadoop.fs.kfs` section exposes `KosmosFileSystem`, an adapter that lets Hadoop jobs use the Kosmos filesystem through the standard `FileSystem` API when the configured default filesystem points at a `kfs://` URI.

The `org.apache.hadoop.fs.permission` section defines access-control and Unix-style permission value objects used by filesystem status records and create/mkdir APIs: `AccessControlException`, `FsAction`, `FsPermission`, and `PermissionStatus`.

The `org.apache.hadoop.fs.s3` section documents the original block/inode based S3 filesystem implementation. It models files as metadata inodes plus separately stored blocks, exposes a pluggable `FileSystemStore` interface, and provides an `S3FileSystem` adapter plus migration and exception types.

The `org.apache.hadoop.fs.shell` section adds the `Count` command for reporting directory count, file count, and byte totals.

The visible `org.apache.hadoop.io` portion begins Hadoop Writable collection support: class-ID mapping for heterogeneous map writables, dense array files built on `MapFile`, and the start of `ArrayWritable`.

## Important APIs, Types, and Functions

### DistributedCache

- `DistributedCache.getLocalCache(URI, Configuration, Path, FileStatus, boolean, long, Path)` and the overload without explicit `FileStatus` are the localization entry points. They return the local `Path` for a cached file or the directory created by unpacking an archive. Archives with `.zip` or `.jar` extensions are documented as automatically extracted.
- `releaseCache(URI, Configuration)` decrements or releases use of a localized cache entry after the task is done.
- `makeRelative(URI, Configuration)` derives the local relative path used for cache materialization.
- `getTimestamp(Configuration, URI)` reads the remote modification time so jobs can detect cache changes after submission.
- `createAllSymlink(Configuration, File, File)` and `createSymlink(Configuration)` manage symlink creation in task work directories.
- Cache configuration methods include `setCacheArchives`, `setCacheFiles`, `getCacheArchives`, `getCacheFiles`, `addCacheArchive`, `addCacheFile`, `setArchiveTimestamps`, `setFileTimestamps`, `getArchiveTimestamps`, `getFileTimestamps`, `setLocalArchives`, `setLocalFiles`, `getLocalCacheArchives`, and `getLocalCacheFiles`.
- Classpath integration methods include `addFileToClassPath`, `getFileClassPaths`, `addArchiveToClassPath`, and `getArchiveClassPaths`.
- `getSymlink(Configuration)` checks whether symlink creation is enabled, `checkURIs(URI[], URI[])` validates URI fragments for symlink conflicts, and `purgeCache(Configuration)` deletes the entire backing cache.

### Core Filesystem Records and Streams

- `BlockLocation` is a `Writable`-style block metadata record with hosts, names, offset, length, setters, getters, `write`, `readFields`, and `toString`.
- `ContentSummary` stores length, directory count, and file count, with `Writable` serialization and string rendering.
- `FileStatus` stores length, directory flag, replication, block size, modification time, permissions, owner, group, and path. It supports setters for permission/owner/group, `Writable` serialization, ordering, equality, and hash code based on path identity.
- `FSInputStream` is the abstract seekable input base. It extends normal stream behavior with `seek(long)`, `getPos()`, `seekToNewSource(long)`, and `readFully` overloads.
- `BufferedFSInputStream` wraps an `FSInputStream` with buffering while preserving position, skip, seek, new-source seeking, byte reads, and full reads.
- `FSDataInputStream` wraps an `InputStream` as a `DataInputStream` while exposing `Seekable` and `PositionedReadable` methods when the wrapped stream supports them.
- `FSDataOutputStream` wraps an `OutputStream` as a data output stream, tracks position through `getPos()`, forwards close, and exposes the wrapped stream.
- `FSInputChecker` verifies checksums while reading. It exposes subclass hooks such as `readChunk` and `getChunkPosition`, a `needChecksum` switch, seek/skip/read paths that can throw `ChecksumException`, and `set` for checksum parameters.
- `FSOutputSummer` generates checksums before data is written. Subclasses implement `writeChunk`; callers write one byte, byte arrays, and flush pending checksum/data buffers.
- `ChecksumException` carries a bad-checksum byte position. `FSError` is an `Error` for unexpected native filesystem failures assumed to be disk related.

### FileSystem API and Wrappers

- `FileSystem` is the abstract base for Hadoop filesystems. Static helpers include command-line `parseArgs`, default filesystem lookup and mutation through `getDefaultUri`/`setDefaultUri`, filesystem factory methods `get`, deprecated `getNamed`, local filesystem lookup, `closeAll`, and statistics printing.
- Initialization and identity APIs include `initialize(URI, Configuration)`, `getUri()`, deprecated `getName()`, `makeQualified(Path)`, and `checkPath(Path)`.
- Core operations include `open`, many `create` overloads, `createNewFile`, `rename`, recursive and deprecated non-recursive `delete`, existence/type/length checks, content summaries, list and glob status methods, `mkdirs`, working-directory and home-directory accessors, replication and default block size/replication access, `getFileStatus`, permission and owner setters, and close.
- Local transfer APIs include copy/move from local, copy/move to local, `startLocalOutput`, and `completeLocalOutput`.
- Block locality APIs include deprecated `getFileCacheHints` and replacement `getFileBlockLocations`.
- `FileSystem.Statistics` tracks bytes read and written, with increment methods, getters, and string rendering.
- `FilterFileSystem` wraps another `FileSystem` in field `fs` and delegates identity, path qualification, block locations, open/create, replication, rename/delete, listing, working directory, mkdirs, copy staging, defaults, status, owner/permission, close, and configuration access.
- `ChecksumFileSystem` wraps a raw filesystem and generates/verifies client-side checksum files. Its API exposes the raw filesystem, checksum path and length calculations, bytes-per-checksum, open/create, replication, rename/delete/list/mkdir, local copy behavior with optional CRC copies, output staging, completion, and checksum-failure reporting.
- `LocalFileSystem` is the checksumed local implementation. It converts Hadoop `Path` values to `File`, copies to/from local without unnecessary transfer, and reports checksum failures by moving bad files aside.
- `RawLocalFileSystem` is the direct local `file:` implementation. It exposes `pathToFile`, URI/name initialization, open/create overloads, rename, delete, list, mkdirs, working directory, lock/release, local-output staging, close, status, owner, and permission operations.
- `InMemoryFileSystem` is a `ramfs://` implementation with reservation and checksum registration through `reserveSpaceWithCheckSum`, plus file listing/count and capacity/percent-used accessors.

### Path, Filters, Shell, Trash, and Utilities

- `Path` is the central URI-like path abstraction. Constructors accept string parent/child pairs, `Path` parent/child pairs, raw strings, and scheme/authority/path components. Methods expose `toUri`, filesystem lookup, absolute/name/parent/suffix/depth checks, string rendering, equality, hashing, ordering, and qualification. Public constants are `SEPARATOR`, `SEPARATOR_CHAR`, and `CUR_DIR`.
- `PathFilter.accept(Path)` is the file-status filter contract.
- `PositionedReadable` declares positioned `read` and `readFully` overloads that do not change the current stream offset and are documented as thread-safe.
- `Seekable` declares `seek`, `getPos`, and `seekToNewSource`.
- `FsShell` provides command-line access to a `FileSystem`, including initialization, `run`, `close`, byte-length formatting helpers, current trash lookup, and `main`.
- `Trash` moves files into user trash, creates checkpoints, expunges old checkpoints, returns an emptier `Runnable`, and has a `main` entry point.
- `DF` and `DU` wrap Unix `df` and `du` style disk usage probes. They expose directories, capacity, used/available space, percent used, mount/filesystem strings, command construction, parsing, string rendering, and `main`.
- `ShellCommand` is a deprecated base class for Unix-like shell commands, superseded by `Shell`.
- `LocalDirAllocator` implements round-robin local disk allocation across configured directories. It provides write path selection with known or unknown size, read path lookup, temporary-file creation, context validity checks, and existence checks.
- `FileUtil` provides static conversion of `FileStatus` arrays to `Path` arrays, recursive delete, filesystem-to-filesystem and local copy overloads, `copyMerge`, shell path conversion, local disk usage, unzip, symlink, chmod, temporary-file creation, and atomic-ish replacement.
- `FileUtil.HardLink` provides hardlink creation and link-count retrieval on Unix, Cygwin, and Windows XP.
- `org.apache.hadoop.fs.shell.Count` exposes `matches(String)`, `count(String, Configuration, PrintStream)`, and command metadata fields `NAME`, `USAGE`, and `DESCRIPTION`.

### KFS Adapter

- `KosmosFileSystem` implements the standard `FileSystem` surface for Kosmos/KFS: URI/name initialization, working directory handling, mkdirs, file/directory tests, content length, listing, status, create/open, rename/delete, length/replication/defaults, lock/release, block locations, copy to/from local, and local-output staging.
- The package documentation describes configuration through `fs.default.name` using a `kfs://host:port/` URI and notes that MapReduce job trackers will route file I/O to KFS when configured this way.

### Permission Types

- `AccessControlException` is an `IOException` for access-control failures, with a no-arg constructor needed for unwrapping from `RemoteException` and a message constructor.
- `FsAction` is an enum-like permission action type. Public methods include `values`, `valueOf`, `implies`, `and`, `or`, and `not`; fields include octal `INDEX` and symbolic `SYMBOL`.
- `FsPermission` is a `Writable` for user/group/other `FsAction` triples. It supports construction from actions, a short mode, or another permission; immutable creation; user/group/other getters; `write`, `readFields`, static `read`; conversion to short; equality/hash/string conversion; umask application and configuration getters/setters; defaults; and `valueOf` for Unix symbolic strings such as `-rw-rw-rw-`.
- `PermissionStatus` combines user name, group name, and `FsPermission`. It supports immutable creation, getters, umask application, `Writable` serialization, static read, and string rendering.

### S3 Filesystem

- `Block` stores an S3 block ID and length, with getters and string rendering.
- `INode` stores file metadata: a file type and an array of `Block` pointers. It exposes `getBlocks`, `getFileType`, file/directory tests, serialized-length calculation, `serialize`, static `deserialize`, and fields `FILE_TYPES` and `DIRECTORY_INODE`.
- `FileSystemStore` abstracts S3 persistence for inodes and blocks. It initializes from URI/configuration, reports stored version, stores/retrieves/deletes inodes and blocks, checks existence, lists shallow or deep subpaths, purges everything for tests, and dumps diagnostics.
- `S3FileSystem` is a `FileSystem` backed by a `FileSystemStore`. It exposes URI/name initialization, working directory handling, mkdirs, file tests, listing, create/open, rename, delete, and S3-specific `FileStatus` creation. Permission parameters on create/mkdirs are documented as ignored.
- `MigrationTool` is a `Tool`-style migration command with `main`, `run`, and `initialize`.
- `S3Exception`, `S3FileSystemException`, and `VersionMismatchException` describe S3 communication failures, fatal S3 filesystem failures, and stored-data version mismatches.
- The package documentation explains the persistence design: paths are URL-encoded inode keys, data is stored as `block-*` objects, files point at a list of blocks, seeks use inode block metadata plus HTTP range requests, and renames move only inode metadata through delete-then-put because S3 has no rename.

### Visible IO Types

- `AbstractMapWritable` is a configurable base for `MapWritable` and `SortedMapWritable`. It maps classes to byte IDs and back, supports synchronized class registration and copy from another `Writable`, carries `Configuration`, and serializes/deserializes the class table. The docs state class IDs range from 1 to 127, limiting a map instance to 127 distinct classes.
- `ArrayFile` extends `MapFile` as a dense file-based mapping from long integer positions to values.
- `ArrayFile.Reader` can seek to an index, read the next value, return the current key, and fetch the value at a specific index.
- `ArrayFile.Writer` creates array files for a value class, optionally with `SequenceFile.CompressionType` and `Progressable`, and appends values with synchronized `append`.
- `ArrayWritable` begins in this chunk. Visible constructors accept a value class, a value class plus `Writable[]`, or `String[]`. Visible methods include value-class lookup, string conversion, object-array conversion, set/get, `readFields`, and `write`; its class documentation is truncated by the chunk boundary.

## Control Flow and Behavioral Contracts

The XML itself has no executable control flow. The APIs imply the main flows used by Hadoop 0.17.0 callers.

Distributed cache flow starts when job setup stores cache files, archives, timestamps, localized outputs, symlink preferences, and classpath additions in `Configuration`. Task-side code calls `getLocalCache` with the remote URI, base cache directory, archive flag, expected timestamp, and work directory. The implementation either reuses a valid local copy or copies the file from the configured `FileSystem`, unpacks archives when applicable, and optionally creates symlinks using URI fragments. After task use, callers call `releaseCache`; server or task-tracker reinitialization may call `purgeCache`.

Filesystem resolution flow starts with a `Path` and `Configuration`. `Path.getFileSystem(conf)` or `FileSystem.get(uri, conf)` resolves a concrete filesystem by scheme and authority, calls `initialize`, then operations run through the abstract `FileSystem` contract. `FilterFileSystem`, `ChecksumFileSystem`, `LocalFileSystem`, `RawLocalFileSystem`, `KosmosFileSystem`, and `S3FileSystem` are all implementations or wrappers that preserve this call shape.

Read flow uses `FSDataInputStream` over an `FSInputStream` or other seekable/positioned input stream. Stateful callers use `seek` and normal reads; positional callers use `PositionedReadable.read` or `readFully`, which should not mutate the stream offset. Checksum-aware reads pass through `FSInputChecker`, which reads chunks, verifies checksums, retries or seeks to new sources when supported, and throws `ChecksumException` with a byte position on corruption.

Write flow uses `FileSystem.create` overloads to return `FSDataOutputStream`. Checksum-aware filesystems wrap writes through `FSOutputSummer` and create companion checksum files. Local-output flows call `startLocalOutput` to write to a temporary or local path, then `completeLocalOutput` to move or finalize the result.

Copy and delete flows are helper-driven. `FileUtil.copy` variants move data between filesystems or local disk, optionally deleting sources. `fullyDelete` recursively deletes local directories and may leave partial deletion if it returns false. `copyMerge` concatenates directory children into one output. `replaceFile` moves a source to a target name and throws on failure.

Trash flow wraps delete-like behavior. `Trash.moveToTrash` moves a file or directory under the current user's trash area unless trash is disabled or the item is already in trash. `checkpoint` creates a time-based checkpoint, `expunge` deletes old checkpoints, and `getEmptier` returns a background cleanup runnable.

Permission flow is value-object based. `FsPermission` is constructed from actions, mode shorts, symbolic strings, or existing permissions; `applyUMask` returns a permission with the configured mask applied. `PermissionStatus` carries user/group/permission triples through Writable serialization, and `FileStatus` exposes owner/group/permission for listed files.

S3 flow is metadata-first. `S3FileSystem` reads an inode for a path to determine whether it is a file or directory and, for files, which `Block` objects contain the data. Opens compute block offsets and use range reads against the store. Creates write new block objects and then store inode metadata. Renames are implemented as inode delete/put because S3 lacks native rename.

Writable flow follows Hadoop's `write(DataOutput)` and `readFields(DataInput)` convention. `AbstractMapWritable` serializes class-ID mappings before subclasses serialize entries; `ArrayFile` stores dense numeric keys through `MapFile`; `ArrayWritable` serializes a homogeneous array of `Writable` values.

## State, Persistence, and Side Effects

The JDiff XML is persistent API metadata used for compatibility comparison. Runtime state described by this chunk belongs to Hadoop APIs and their implementations.

`DistributedCache` stores most job-facing state in `Configuration`: cache archives, cache files, timestamps, localized file/archive paths, classpath additions, and symlink enablement. It also creates persistent local cache entries under task-tracker cache directories, unpacks archives into local directories, creates symlinks in task work directories, maintains reference/release state, and can delete all backing cache files through `purgeCache`.

`FileSystem` implementations persist data to their backing stores: HDFS-like stores, local disk, KFS, S3, in-memory storage, or wrapper-managed checksum files. Operations in this chunk can create, overwrite, rename, delete, recursively delete, list, chmod, chown, change replication, set owner/group, make directories, copy to/from local, create symlinks/hardlinks, extract archives, and move files to trash.

`ChecksumFileSystem` and `LocalFileSystem` persist companion checksum files and may move corrupt local files into a bad-file area when checksum failure is reported. `FSInputChecker` and `FSOutputSummer` hold process-local checksum state for the current stream buffer/chunk.

`FileSystem.Statistics` is process-local mutable telemetry with bytes-read and bytes-written counters. It is exposed both per filesystem and through static printing; changes affect diagnostics rather than file contents.

`Path`, `BlockLocation`, `ContentSummary`, `FileStatus`, `FsPermission`, `PermissionStatus`, `Block`, `INode`, `AbstractMapWritable`, `ArrayFile`, and `ArrayWritable` are durable or transport-facing value types. Their `Writable` formats, equality, ordering, and string forms are compatibility-sensitive because they may appear in RPC, file metadata, sequence/map files, and configuration-driven behavior.

`Trash` persists deleted user data by moving it under a trash directory and creating/deleting checkpoint directories. Misconfiguration can turn delete operations into permanent removal or unbounded trash accumulation.

`RawLocalFileSystem`, `DF`, `DU`, `FileUtil`, `FileUtil.HardLink`, and `ShellCommand` depend on host filesystem and shell behavior. Their side effects include local file creation/deletion, permission/owner changes, temp files, hardlinks, symlinks, archive extraction, and platform command execution.

`S3FileSystem` persists inodes and blocks as S3 objects. The package documentation makes clear that directory and file names use leading-slash inode keys while data blocks use `block-` keys. Rename is not atomic in the same way as local/HDFS rename because it is represented by delete plus put.

## Dependencies and Integration Points

This chunk depends heavily on Java platform types: `URI`, `File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `PrintStream`, arrays, collections, `Checksum`, `IOException`, and shell/platform commands for disk usage, symlink, chmod, chown, and hardlink behavior.

Key Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for filesystem resolution, distributed-cache metadata, local-directory allocation, permissions/umask, KFS/S3 initialization, and Writable configuration propagation.
- `org.apache.hadoop.fs.FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FSDataInputStream`, `FSDataOutputStream`, `PathFilter`, `Seekable`, and `PositionedReadable` as the central filesystem contract.
- `org.apache.hadoop.fs.permission.FsPermission`, `FsAction`, `PermissionStatus`, and `AccessControlException` for authorization metadata.
- `org.apache.hadoop.io.Writable`, `WritableComparable`-style serialization conventions, `MapFile`, `SequenceFile.CompressionType`, and `ArrayWritable` for persistent binary formats.
- `org.apache.hadoop.util.Progressable` and `Tool`-style command execution for streaming progress and migration/shell commands.
- MapReduce job configuration and `JobClient` integration for `DistributedCache`.
- KFS configuration through `fs.default.name=kfs://host:port/`.
- S3 store backends through the `FileSystemStore` abstraction and S3 object layout/version metadata.
- Apache Commons Logging appears via public `LOG` fields on filesystem/checksum classes.

## Risks and Compatibility Notes

- This is generated API metadata, not implementation source. It cannot prove private state handling, lock ordering, exact path normalization, retry loops, or byte-level serialization details beyond the visible signatures and Javadocs.
- The chunk starts and ends inside larger API contexts. Whole-file reports should merge adjacent chunks before making complete claims about `NameNodeStatisticsMBean` or `ArrayWritable`.
- `DistributedCache` uses URI fragments for symlink names. Missing fragments, duplicate fragments, or conflicts between file and archive fragments can create broken links or task-local name collisions.
- `DistributedCache` relies on remote modification timestamps captured at job submission. Clock skew, stores with weak mtime semantics, or changed files with unchanged timestamps can lead to stale or inconsistent localized resources.
- `purgeCache` is explicitly destructive and can delete backing cache files used by jobs if called outside reinitialization.
- `FileSystem.create` has many overloads with overwrite, permission, buffer size, replication, block size, and progress variants. Compatibility depends on all overloads preserving consistent defaults.
- Deprecated APIs such as `getName`, `getNamed`, `delete(Path)`, `isDirectory`, `getLength`, `getContentLength`, `getBlockSize`, `getFileCacheHints`, and `ShellCommand` remain visible and can still be used by old callers.
- Positioned reads must not disturb stream offset and are documented as thread-safe. Implementations that share mutable seek state can corrupt concurrent readers.
- `readFully` and checksum reads must handle short reads, EOF, retries, and checksum exceptions precisely; silent partial reads can corrupt higher-level record readers.
- `ChecksumFileSystem` must keep data files and checksum files synchronized across create, rename, delete, copy, and local-output completion. Orphaned or stale checksum files are a common risk.
- Local filesystem behavior is platform-sensitive. Shell commands, symlink/hardlink support, permission bits, owner/group lookup, Windows path syntax, and disk-usage parsing can all vary by OS.
- `FileUtil.copy` and `fullyDelete` are not atomic. Failures can leave partial destination trees, partially deleted sources, or mixed merged output.
- `LocalDirAllocator` depends on configured local directories and free-space estimates. Stale context state, failed disks, or unknown write sizes can select unsuitable paths.
- `Trash` is configuration-sensitive. Disabled trash, files already in trash, checkpoint naming, and expunge interval mistakes can cause immediate data loss or excessive retained data.
- `FsPermission` has multiple representations: action triples, short modes, symbolic strings, umask-adjusted permissions, and Writable bytes. Conversion bugs can become security bugs.
- `FileStatus` equality and ordering are path-centered. Callers comparing metadata changes must not assume equality includes length, owner, permission, or modification time.
- KFS integration can only be correct when the default filesystem URI and KFS client/native dependencies are available. Missing KFS libraries or invalid authority values will break normal Hadoop file I/O.
- S3 in this release uses an inode/block layout, not a simple object-per-file layout. Store version mismatches, orphaned blocks, eventual consistency, delete-then-put rename, and range-read failures can affect correctness.
- `S3FileSystem` documents ignored permission parameters, so code expecting HDFS-like permission enforcement on create/mkdirs will not get it.
- `FileSystemStore.purge` is test-oriented and destructive; accidental use against production buckets would remove all inodes and blocks known to the store.
- `AbstractMapWritable` has only 127 class IDs per map instance. Complex nested maps with many distinct Writable classes can exceed the documented range.
- `ArrayFile` depends on monotonically dense integer keys generated by the writer. Manual corruption or out-of-order writes would break reader seek/key assumptions.

## Test Signals

Useful validation for this API surface should include:

- JDiff compatibility checks that the XML remains well formed and preserves package/class/interface boundaries, public/protected signatures, declared exceptions, visibility, static/final/abstract/synchronized flags, field names, deprecation markers, and documentation-bearing entries in lines 6313-12474.
- Distributed cache tests for cache file/archive configuration round trips, timestamp capture, localization reuse, archive extraction for `.jar` and `.zip`, symlink creation from URI fragments, duplicate fragment rejection through `checkURIs`, classpath additions, release semantics, and destructive purge behavior in an isolated cache directory.
- `FileSystem` contract tests for default URI resolution, `get(URI, conf)` initialization, path qualification, create overload defaults, overwrite handling, mkdir permissions, open/read/write/close, rename/delete semantics, list and glob status, content summaries, local copy/move methods, replication/default block size, owner/permission setters, and statistics counters.
- Stream tests for `FSInputStream`, `BufferedFSInputStream`, `FSDataInputStream`, `FSInputChecker`, `FSOutputSummer`, and `FSDataOutputStream`: seek/getPos consistency, positioned reads not changing offset, `readFully` short-read loops, EOF behavior, checksum failure position reporting, retry/new-source paths, output position tracking, close propagation, and checksum chunk boundaries.
- `ChecksumFileSystem` and `LocalFileSystem` tests for checksum-file naming and length calculation, create/open verification, rename/delete/list filtering of checksum files, local copy with and without CRC files, checksum failure quarantine, raw filesystem access, and local-output staging.
- `RawLocalFileSystem` tests for path-to-file conversion, URI/name behavior, create/open/delete/rename/list/mkdirs/status, recursive delete flags, working directory, home directory, lock/release, owner/permission shell command paths, and platform-specific symlink/hardlink behavior.
- `Path` tests for every constructor form, URI conversion, relative and absolute paths, final component, parent at root, suffix, depth, qualification, equality, hashing, ordering, separator constants, and filesystem lookup from configuration.
- `FileUtil` tests for `stat2Paths`, recursive delete partial failures, filesystem-to-filesystem copy, local copy, `copyMerge`, shell path conversion on Unix and Windows, disk usage, unzip, symlink return codes, chmod return codes, temp-file creation, replace-file failure cleanup, and hardlink/link-count behavior.
- `DF` and `DU` tests with mocked command output for Linux, FreeBSD, and Cygwin formats, plus refresh interval behavior and parsing failure paths.
- `LocalDirAllocator` tests for round-robin directory selection, known-size and unknown-size writes, read path lookup across all directories, missing file handling, temporary-file creation, invalid context detection, and failed/full disk fallback.
- `Trash` tests for disabled trash, already-in-trash return false, move-to-trash success, checkpoint creation, expunge of old checkpoints, emptier runnable behavior, and CLI `main` paths.
- Permission tests for `FsAction` implication/algebra, `FsPermission` action and short constructors, immutable creation, symbolic `valueOf`, umask application, configuration-backed umask getters/setters, Writable round trips, equality/hash/string output, and `PermissionStatus` serialization.
- KFS adapter tests, when KFS dependencies are available, for initialization from `kfs://` URI, working directory, mkdirs, create/open, rename/delete, status/listing, content length, block locations, replication defaults, local copy staging, and lock/release behavior.
- S3 filesystem tests with a controlled `FileSystemStore` fake for inode/block storage, version mismatch, file and directory status, create/open with multi-block files, range-like seek behavior, rename as inode move, recursive and non-recursive delete, ignored permission arguments, list shallow/deep paths, purge/dump diagnostics, and orphan-block cleanup expectations.
- `fs.shell.Count` tests for command matching, output formatting, and accurate directory/file/byte counts through a test filesystem.
- `AbstractMapWritable` tests for class registration, ID lookup, ID limit behavior, copy constructor support, configuration propagation, serialization of class tables, and nested map compatibility.
- `ArrayFile.Reader` and `ArrayFile.Writer` tests for dense append, seek by index, current key tracking, next value reads, random get, compression/progress constructor behavior, and interoperability with `MapFile`.
- `ArrayWritable` tests for value-class preservation, string-array construction, set/get, `toStrings`, `toArray`, empty arrays, mixed-class rejection or behavior, and Writable round trips. Adjacent chunk coverage is needed to finish its full documentation review.

### subset-b-007260: lines 12475-18820

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 12475-18820

## Scope And Purpose

This chunk is a JDiff API-description slice for Hadoop 0.17.0. It starts at the tail of `org.apache.hadoop.io.ArrayWritable` documentation, covers most of the public `org.apache.hadoop.io` serialization, comparison, text, and file-container APIs, and ends in the opening public contract for `org.apache.hadoop.io.compress.GzipCodec`. The file is not executable implementation code; it is generated XML describing classes, interfaces, constructors, methods, fields, inheritance, deprecation state, and embedded Javadoc. The research below therefore treats behavior as the public API contract exposed by this release.

The dominant purpose of the chunk is to define Hadoop's low-level binary data model: `Writable` serialization, `WritableComparable` keys, raw byte comparators, reusable in-memory input/output buffers, primitive writable wrappers, text encodings, map/set/sequence file containers, object/string serialization helpers, versioned wire formats, and compression codec interfaces. These APIs are central integration points for MapReduce records, HDFS-backed persistent files, RPC object transport, sorting/merging pipelines, and compression-aware readers and writers.

The chunk boundary matters. `ArrayWritable` is only represented by trailing documentation, so its constructors and methods are not complete in this slice. `GzipCodec` is present only through its class declaration and first methods, with nested gzip stream classes and later LZO/zlib APIs outside this chunk.

## API Families Covered

### Writable Core

`Writable` is the base binary serialization contract. It exposes `write(DataOutput)` and `readFields(DataInput)` and documents the important reuse expectation: implementations should deserialize into existing storage where possible. `WritableComparable` extends `Writable` and `Comparable`, making it the expected key shape for Hadoop sorting and MapReduce keys.

`WritableComparator` implements `RawComparator` and is the registry/factory for optimized key comparisons. It can return a comparator for a key class with `get(Class)`, register an optimized comparator with `define(Class, WritableComparator)`, instantiate keys with `newKey()`, compare fully materialized `WritableComparable` objects, or compare serialized byte ranges directly. Static helpers parse fixed-width primitives and variable-length integers from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), compare byte ranges lexicographically, and hash bytes.

`RawComparator<T>` extends `Comparator<T>` with `compare(byte[], int, int, byte[], int, int)`. This is the bridge between Hadoop's serialized spill/sort paths and Java object comparison. Optimized primitive comparators in this chunk (`BooleanWritable.Comparator`, `BytesWritable.Comparator`, `FloatWritable.Comparator`, `IntWritable.Comparator`, `LongWritable.Comparator`, `LongWritable.DecreasingComparator`, `MD5Hash.Comparator`, `Text.Comparator`, `UTF8.Comparator`) all plug into this raw-comparison model.

`WritableFactory` and `WritableFactories` provide class-to-factory registration and instantiation. `WritableName` maps writable classes to short names and back. These registries are stateful static integration points: they allow custom classes to avoid reflection-only construction or to preserve legacy wire names, but they also introduce global process state that can affect deserialization in tests and long-lived daemons.

`WritableUtils` is the utility surface for common wire encodings: compressed byte arrays and strings, string arrays, compressed string arrays, byte-array display, cloning and clone-into through `Configuration`, variable-length integer/long read-write helpers, enum read/write, and `skipFully`. Its variable-length integer helpers back `VIntWritable`, `VLongWritable`, `Text` length encoding, and raw comparator parsing.

### Primitive And Simple Writable Types

The chunk defines primitive wrappers that all follow the same basic shape: no-arg and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, `toString`, and usually a raw comparator:

- `BooleanWritable` stores a boolean key/value and has a specialized raw comparator.
- `FloatWritable`, `IntWritable`, and `LongWritable` store fixed-width primitives and expose optimized comparators that parse serialized bytes directly.
- `LongWritable.DecreasingComparator` reverses both object and raw-byte ordering for descending sorts.
- `VIntWritable` and `VLongWritable` store integer values with Hadoop's variable-length encoding, reducing serialized size for smaller values.
- `NullWritable` is a singleton-like zero-length placeholder value/key. It serializes no state and is used where a key or value slot is structurally required but semantically empty.
- `BytesWritable` is a resizable byte sequence with explicit logical size versus backing capacity. It exposes raw storage with `get()`, size/capacity mutation, copy/set operations, serialization, memcmp-like sorting, MD5-front hashing per Javadoc, equality over the active byte range, and a hex `toString`.
- `MD5Hash` is a fixed-length hash writable with constructors from string/bytes, digest helpers over byte arrays/strings/input streams, half/quarter digest extraction, byte-level comparison, `setDigest`, and the public `MD5_LEN` field.

These classes are deliberately small and allocation-conscious. Their `readFields` methods mutate existing instances, and their raw comparators let sort paths avoid full object creation.

### Arrays, Maps, Generic Values, And Object Serialization

`ArrayWritable` is only partially visible at the beginning of the chunk, but the visible documentation shows its intended subclassing model: callers often subclass it to fix the element value class, especially when using it as a reducer input value.

`TwoDArrayWritable` stores a matrix of `Writable` instances of a declared class. It exposes constructors with the value class and optional initial values, `toArray()`, `set`, `get`, `readFields`, and `write`.

`MapWritable` extends `AbstractMapWritable` and implements `Map<Writable, Writable>`. It exposes normal `Map` operations plus `readFields` and `write`. `SortedMapWritable` similarly extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`, adding sorted-map range and endpoint methods (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`) alongside the normal map API and serialization.

`GenericWritable` wraps one of a bounded set of writable implementation classes supplied by subclass `getTypes()`. It is also `Configurable`, so deserialized wrapped values can be constructed/configured under a `Configuration`.

`ObjectWritable` serializes arbitrary declared Java objects under a declared class. It is also `Configurable` and has static `writeObject` and `readObject` helpers. It is the broadest and riskiest serialization surface in the chunk because it crosses from Hadoop's narrow `Writable` model into Java primitive, string, array, enum, and configured object handling. The declared class is part of the serialized contract and is returned by `getDeclaredClass()`.

`DefaultStringifier<T>` implements `Stringifier<T>` using `Configuration` and a target class. It converts objects to/from strings, and includes static helpers for storing/loading a single value or arrays in `Configuration` properties. This makes serialized objects part of configuration state rather than file state.

`Stringifier<T>` is the generic closeable string conversion interface with `toString(T)`, `fromString(String)`, and `close()`.

### Text And Encoding

`Text` is the primary UTF-8 string writable in this release. It stores standard UTF-8 bytes with an integer length encoded in zero-compressed format. It supports construction from Java `String`, another `Text`, or byte arrays; raw byte and length access; code-point traversal with `charAt`; substring search with `find`; setting from strings, bytes, and other `Text`; appending raw UTF-8 bytes; clearing; serialization/deserialization; bytewise UTF-8 ordering; and equality/hash behavior over content.

`Text` also exposes static helpers for UTF-8 conversion and validation: `decode`, `encode`, `readString`, `writeString`, `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. The APIs distinguish replacement behavior for malformed input from strict `CharacterCodingException` / `MalformedInputException` paths.

`UTF8` is still present but deprecated in favor of `Text`. It is a `WritableComparable` string type with raw byte/length access, setters, read/write, skip, comparison, static string read/write helpers, and an optimized comparator. Its presence is a compatibility signal for old sequence files or APIs that still name `UTF8`.

### Reusable Buffers And IO Utilities

`DataInputBuffer` and `DataOutputBuffer` are reusable in-memory `DataInput`/`DataOutput` implementations. `DataInputBuffer` resets over a byte array plus start/length and reports current position and length. `DataOutputBuffer` exposes backing data and valid length, can reset to empty, and can copy bytes directly from a `DataInput`.

`InputBuffer` and `OutputBuffer` provide similar reusable byte-buffer behavior for `InputStream`/`OutputStream` rather than `DataInput`/`DataOutput`. `OutputBuffer.write(InputStream, int)` copies directly from an input stream.

`IOUtils` is the stream/socket helper surface. It contains multiple `copyBytes` overloads, `readFully`, `skipFully`, `closeStream`, and `closeSocket`. `IOUtils.NullOutputStream` discards all bytes, acting like `/dev/null`.

The control-flow pattern across these utilities is direct streaming/copying with explicit byte counts, EOF-sensitive read/skip loops, and defensive close helpers that callers can use in cleanup paths.

### Versioned Serialization And Error Aggregation

`VersionedWritable` is an abstract `Writable` base that writes/reads a version byte and compares it to subclass `getVersion()`. On mismatch, it throws `VersionMismatchException`. The documentation explicitly instructs evolving subclasses to catch version mismatches in `readFields` if they can translate old formats.

`VersionMismatchException` reports expected versus found versions. `MultipleIOException` wraps or creates an `IOException` from a list of `IOException` instances. These APIs support robust cleanup and migration behavior in storage and stream code.

## File Container APIs

### SequenceFile

`SequenceFile` is the main flat binary key/value file format described in this chunk. Its static `createWriter` overloads construct writers over `FileSystem`/`Path` or raw `FSDataOutputStream`, with configurable key/value classes, buffer size, replication, block size, compression type, codec, progress callback, and metadata. Deprecated `getCompressionType(Configuration)` and `setCompressionType(Configuration, CompressionType)` redirect users toward job-specific MapReduce configuration or explicit writer creation.

The Javadoc describes three formats:

- Uncompressed records: header, record length, key length, key bytes, value bytes, and periodic sync markers.
- Record-compressed records: same record envelope, but values are compressed.
- Block-compressed records: batches of key lengths, keys, value lengths, and values are compressed as separate blocks, with lengths encoded in zero-compressed integer format.

All formats share a header containing magic/version, key class, value class, compression booleans, codec class when enabled, file metadata, and a sync marker. `SYNC_INTERVAL` controls approximate spacing between sync points.

`SequenceFile.CompressionType` is the enum selecting none, record, or block compression. `SequenceFile.Metadata` is a `Writable` wrapper around `TreeMap<Text, Text>` with get/set, direct metadata access, serialization, equality, hash, and string conversion.

`SequenceFile.Reader` reads all SequenceFile variants. It can open an `FSDataInputStream` through a protected `openFile` hook, report key/value class names and classes, report compression mode and codec, expose metadata, close the file, read key-only records, read key/value records, read current values, create `ValueBytes`, read raw key/value records, seek to exact writer-returned positions, sync to the next marker after an arbitrary position, report whether a sync was seen, and report current byte position.

`SequenceFile.ValueBytes` is the raw-value abstraction used by raw readers/writers. It exposes `writeUncompressedBytes`, `writeCompressedBytes`, and `getSize`.

`SequenceFile.Writer` exposes constructors for all writer modes and lower-level stream parameters, then provides `getKeyClass`, `getValueClass`, `getCompressionCodec`, `sync`, `close`, typed `append(Writable, Writable)`, raw append variants, and `getLength`. Its fields include serializers for keys, uncompressed values, and compressed values, indicating integration with Hadoop's serializer framework even though this chunk only shows the API metadata.

`SequenceFile.Sorter` sorts and merges SequenceFiles using either key/value classes or an arbitrary `RawComparator`. It exposes merge factor, memory budget, progress callback, `sort`, `sortAndIterate`, `merge`, `cloneFileAttributes`, and `writeFile`. `Sorter.RawKeyValueIterator` provides the streaming sorted-run interface (`getKey`, `getValue`, `next`, `close`, `getProgress`). `Sorter.SegmentDescriptor` represents an input segment with constructors by path or explicit offset/length, metadata accessors for length and path, `ignore`, `preserveInput`, and a `doSync` flag. This is the public contract for external sorting and multi-pass merging.

### MapFile And SetFile

`MapFile` is a directory-based persistent sorted map over Hadoop files. The public fields `INDEX_FILE_NAME` and `DATA_FILE_NAME` identify the two child files. The data file stores all key/value pairs; the index file stores a fraction of keys determined by `MapFile.Writer`'s index interval and is read entirely into memory by readers. The class offers static `rename`, `delete`, `fix`, and `main`. `fix` can rebuild a corrupt index from the data file, optionally as a dry run, and returns the number of valid entries or `-1` if no fix was needed.

`MapFile.Reader` opens an existing map with a `FileSystem`, directory name, optional `WritableComparator`, `Configuration`, and a protected delayed-open constructor for subclasses. It exposes synchronized navigation and lookup: `reset`, `midKey`, `finalKey`, `seek`, `next`, `get`, `getClosest` with optional before/after behavior, and `close`. It also has protected `open` and `createDataFileReader` hooks, so subclasses can specialize the underlying `SequenceFile.Reader`.

`MapFile.Writer` creates sorted maps with key/value classes or explicit comparators, optional compression type, codec, progress callback, and configuration. It exposes static and instance index interval configuration, `append`, and `close`. The API contract requires in-order key appends; large database updates are expected to be built by copying/merging sorted versions rather than in-place modification.

`SetFile` extends `MapFile` and models a sorted persistent set by storing keys with empty values. `SetFile.Reader` extends `MapFile.Reader` and narrows operations to `seek`, key-only `next`, and key-returning `get`. `SetFile.Writer` extends `MapFile.Writer` and exposes constructors for key class/comparator and compression, plus key-only `append`.

## Compression APIs

`CompressionCodec` is the top-level codec interface. It creates compression output streams with or without a provided `Compressor`, reports the compressor type, creates compressors, creates compression input streams with or without a provided `Decompressor`, reports the decompressor type, creates decompressors, and returns a default filename extension. This interface is consumed directly by SequenceFile writers/readers and by `CompressionCodecFactory`.

`CompressionCodecFactory` is a configuration-driven codec registry and filename matcher. It constructs from `Configuration`, can list/set codec classes, find the codec for a file name, remove a codec suffix, stringify its registered set, and has a `main` entry point. It exposes a `LOG` field using Apache Commons Logging. Its public documentation describes it as a factory that finds the correct codec for a filename.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases wrapping protected final `InputStream in` and `OutputStream out`. Input streams require subclasses to implement `read(byte[], int, int)` and `resetState()`, with reset intended for cases where the underlying stream was repositioned. Output streams require `write(byte[], int, int)`, `finish()` without closing the underlying stream, and `resetState()` without resetting the underlying stream. `close` and `flush` are part of the base contract.

`Compressor` and `Decompressor` model streaming codecs after `java.util.zip.Deflater` and `Inflater`. `Compressor` accepts input, reports `needsInput`, accepts dictionaries, reports byte counts, handles `finish`/`finished`, fills output buffers via `compress`, and supports `reset` and `end`. `Decompressor` mirrors this with `setInput`, `needsInput`, dictionary support and `needsDictionary`, `finished`, `decompress`, `reset`, and `end`.

`DefaultCodec` implements `CompressionCodec` and `Configurable`, exposing all codec factory methods plus `setConf`/`getConf`. `GzipCodec` extends `DefaultCodec`; this chunk includes its constructor and overrides for stream creation, compressor/decompressor creation/type reporting, and default extension. The class doc states that it creates gzip compressors/decompressors, but nested gzip stream classes continue after the chunk boundary.

## Control Flow And Data Flow

The central data flow is object-to-bytes-to-object. Writers call `Writable.write(DataOutput)` into files, buffers, RPC streams, or compression streams. Readers reuse instances and call `readFields(DataInput)` to mutate them from serialized bytes. Comparators sit on both sides: normal object comparators compare deserialized keys, while raw comparators compare serialized byte slices during sort/merge operations.

For SequenceFiles, control flow is file-format driven. A writer emits a header, metadata, sync marker, and then records according to the selected compression mode. It returns byte positions through `getLength()` that readers can later use for exact `seek`. For non-exact positions, readers use `sync(long)` to advance to the next marker and `syncSeen()` to detect split boundaries. Raw read/write APIs move serialized key/value bytes through `DataOutputBuffer` and `ValueBytes` without materializing Java objects, which is important for sort/merge performance.

For MapFiles, control flow layers on SequenceFile. A writer appends sorted keys to the data file and periodically writes index entries. A reader loads the index into memory, binary-searches or scans to the nearest indexed key, seeks the underlying data reader, and then scans forward to the target or closest key. `fix` reconstructs index state from the data file when the index is missing or corrupt.

For Sorter APIs, the implied flow is external sort: consume one or more input SequenceFiles, use a `RawComparator` to sort records under a memory budget, spill or merge sorted segments with a configurable merge factor, and expose merged output either as a file or `RawKeyValueIterator`.

For compression, clients create streams through `CompressionCodec`, optionally reuse `Compressor`/`Decompressor` instances, push input while checking `needsInput`, drain output through `compress`/`decompress`, signal `finish`, and then reset or end codec state. `CompressionInputStream.resetState()` explicitly supports repositioning the underlying input stream, which is required by splittable readers or sync-seeking file readers that reuse buffered compression wrappers.

## State And Persistence Behavior

Most primitive and collection writables hold only in-memory object state and serialize it exactly through `DataOutput`/`DataInput`. The important persistence contract is binary compatibility: field order, length encoding, variable-length integer handling, class names, and metadata encodings become on-disk or over-the-wire state.

`BytesWritable`, `Text`, `UTF8`, `DataOutputBuffer`, and `OutputBuffer` distinguish backing capacity from valid length. Callers that consume `get()` or `getData()` must respect `getSize()` or `getLength()`; otherwise stale bytes beyond the logical end can leak into comparisons, hashes, or writes.

`MapWritable` and `SortedMapWritable` persist dynamic class mappings through `AbstractMapWritable` behavior outside this chunk. The API shape shows they must serialize both entries and enough type information for arbitrary writable keys and values. Copy constructors indicate state can be duplicated while preserving those mappings.

`DefaultStringifier.store/load` and `storeArray/loadArray` persist object state into `Configuration` properties. This is not durable file persistence by itself, but in Hadoop deployments configuration can be serialized into job submissions, so values stored through these helpers can cross process and cluster boundaries.

`SequenceFile` persists the richest state: magic/version, key/value class names, compression flags, codec class, `Metadata`, sync marker, and records. Compression choices and codec class names become part of the file's readability contract. `Metadata` persists `Text` key/value attribute pairs. `Writer.sync()` injects recovery/split points into the file; `Reader.sync()` and `syncSeen()` are the corresponding read-side persistence hooks.

`MapFile` persists a directory containing `data` and `index`. The index is derived state, but it is persisted for lookup speed and can be repaired with `fix`. Because the index is loaded fully into memory, key size and index interval are persistent design choices that affect reader memory footprint.

`SetFile` persists only set keys on top of `MapFile`, using the map container machinery with semantically empty values.

Compression codecs keep transient native or Java codec state. `reset()` allows instance reuse for a new stream; `end()` releases resources and discards unprocessed input. Mismanaging this lifecycle can leak native resources or corrupt subsequent streams if a codec instance is reused without reset.

Global static registries (`WritableComparator.define`, `WritableFactories.setFactory`, `WritableName.setName/addName`, `CompressionCodecFactory.setCodecClasses`) are mutable process state. They are integration conveniences but can make tests order-dependent if not isolated.

## Dependencies And Integration Points

This chunk sits at the intersection of Hadoop common, filesystem APIs, Java IO, and MapReduce:

- Java IO primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FilterInputStream`, `FilterOutputStream`, `IOException`, `Closeable`, and sockets via `IOUtils`.
- Hadoop filesystem APIs: `FileSystem`, `Path`, and `FSDataOutputStream` for persistent SequenceFile, MapFile, and SetFile storage.
- Hadoop configuration: `Configuration` and `Configurable` are used by generic/object/string serializers, codec factories, and file readers/writers.
- Hadoop progress reporting: `Progressable` is accepted by SequenceFile and MapFile writer/sorter APIs.
- Hadoop serializer framework: `SequenceFile.Writer` exposes serializer fields, showing integration with `org.apache.hadoop.io.serializer.Serializer`.
- Compression: `CompressionCodec`, codec factories, compressor/decompressor pools or implementations, and filename suffix detection integrate with file formats and job output settings.
- MapReduce: Javadocs explicitly refer to MapReduce keys/values, reduce outputs, map output compression type, and SequenceFile output format configuration.
- Logging: `CompressionCodecFactory.LOG` uses Apache Commons Logging.
- Java NIO charset APIs: `Text` uses `ByteBuffer`, `CharacterCodingException`, and `MalformedInputException` behavior for UTF-8 encoding/decoding.
- Security-sensitive class loading/reflection: object, writable-name, writable-factory, comparator, and codec-class APIs all depend on resolving classes from serialized names or configuration.

## Risks And Edge Cases

The highest compatibility risk is binary format drift. Changing primitive encodings, `Text` length encoding, variable-length integer rules, SequenceFile headers, sync marker handling, metadata serialization, or MapFile index layout would break persisted files and cross-version jobs.

Raw comparator correctness is critical. If a comparator interprets serialized bytes differently from the corresponding object's `compareTo`, SequenceFile sorting, MapFile lookup, partitioning, grouping, and merge behavior can diverge. Descending comparators and variable-length integer comparators are especially easy to get wrong because raw byte order does not always match numeric order.

Reusable buffers expose backing arrays directly. Callers must respect logical lengths, and implementations must avoid retaining mutable caller arrays in surprising ways unless documented. `BytesWritable(byte[])` explicitly uses the input as backing storage, so external mutation can affect object state.

Text handling has malformed UTF-8 branches. Replacement versus strict decoding must remain explicit; otherwise data-cleanup behavior can hide corrupt input or unexpectedly fail old workloads. `UTF8` deprecation also creates migration risk because old files may still contain or expect the legacy class.

`ObjectWritable`, `WritableName`, `WritableFactories`, and codec class lookup can instantiate classes by name or from configuration. That is a powerful extension mechanism but raises classpath, compatibility, and security risks in environments that deserialize untrusted data or run jobs with broad classpaths.

`MapFile` requires sorted appends. Writer APIs do not model in-place updates; callers must merge sorted change lists into new map directories. Violating sorted order can make indexes incorrect and lookups unreliable. Large index keys can also create reader memory pressure because the index is loaded entirely.

SequenceFile split/seek semantics depend on sync markers and exact positions returned by writers. Arbitrary seeks must use `sync`; direct `seek` to arbitrary offsets is documented as invalid. Compression mode complicates raw reads, block boundaries, and sync behavior.

Compression stream lifecycle is another risk area. `finish()` must not close the underlying stream, `resetState()` must not reset underlying output streams, and `end()` must be called when native resources exist. Buffered decompression plus underlying stream repositioning requires correct `resetState()` implementation to avoid stale buffered bytes.

Several APIs are deprecated but still present: `UTF8`, `SequenceFile.getCompressionType`, `SequenceFile.setCompressionType`, and a deprecated `SequenceFile.Reader.next(DataOutputBuffer)` raw API. Tests and migration code should verify both compatibility and warnings/alternate paths.

The JDiff XML itself can be incomplete at chunk boundaries. Research consumers should not treat this chunk as the full definition of `ArrayWritable` or `GzipCodec`; adjacent chunks are required for those complete APIs.

## Test Signals

Strong test coverage for this API family should include binary round trips for every `Writable` in the chunk: default construction, value mutation, `write`, `readFields` into reused instances, equality, hash behavior, and `compareTo`.

Comparator tests should compare object-level and raw-byte comparator results for the same values, including boundary values: booleans, negative/zero/positive ints and longs, floats including special values if supported by implementation, variable-length integer size boundaries, empty and non-empty byte arrays, UTF-8 strings with multibyte code points, and MD5 hash ordering.

Buffer tests should verify that `getData()`/`get()` expose extra capacity but only `getLength()`/`getSize()` bytes are valid; reset should reuse storage without leaking previous logical data. `readFully`, `skipFully`, and direct copy helpers should be tested against short reads and EOF.

Text tests should cover UTF-8 encode/decode, strict malformed-input exceptions, replacement behavior, `charAt`, `find`, append, clear, static `readString`/`writeString`, `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. Compatibility tests should still read/write deprecated `UTF8`.

SequenceFile tests should create and read uncompressed, record-compressed, and block-compressed files with metadata. They should validate header-derived key/value classes, codec reporting, raw and object reads, `getCurrentValue`, exact `seek` to writer positions, `sync` from arbitrary offsets, `syncSeen`, `ValueBytes`, appendRaw, `getLength`, close behavior, and deprecated raw-read compatibility.

Sorter tests should sort multiple SequenceFiles with default and custom `RawComparator`s, vary memory and merge factor settings, test `sortAndIterate`, preserve or delete input segments according to flags, and compare output ordering against object-level comparators.

MapFile and SetFile tests should append sorted keys, reject or expose failures for out-of-order keys, verify index interval effects, run lookup paths (`seek`, `get`, `getClosest` before/after, `midKey`, `finalKey`, `next`, `reset`), validate `rename`/`delete`, and rebuild a missing/corrupt index with `fix` in dry-run and real modes.

Compression tests should exercise `CompressionCodecFactory` suffix lookup and suffix removal, codec class configuration, `DefaultCodec` and visible `GzipCodec` stream creation, compressor/decompressor reuse with `reset`, dictionary branches where supported, `finish` without closing underlying streams, and `CompressionInputStream.resetState()` after repositioning input.

Global-registry tests should isolate static state for `WritableComparator`, `WritableFactories`, `WritableName`, and codec class lists. Without isolation, one test's custom registration can mask failures or change behavior in later tests.

### subset-b-007261: lines 18821-25080

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 18821-25080

## Scope and Artifact Type

This chunk is part of the Hadoop 0.17.0 JDiff XML API snapshot. It records public and protected API metadata, inheritance, implemented interfaces, method signatures, exceptions, fields, deprecation markers, and embedded Javadoc for several Hadoop packages. It is not implementation source, so control flow and state behavior are inferred from the exposed contracts, docs, exceptions, and `Writable`/stream lifecycle APIs visible in the XML.

The chunk begins inside `org.apache.hadoop.io.compress.GzipCodec`, covers compression codecs and native zlib/lzo adapters, retry and serialization frameworks, IPC and RPC metrics/logging utilities, and then enters a large `org.apache.hadoop.mapred` section through the start of `JobStatus`.

## Purpose

The primary purpose of this XML section is API compatibility documentation for Hadoop common and old MapReduce (`mapred`) classes. It captures the Hadoop 0.17.0 public surface that downstream code could compile against:

- Compression APIs expose gzip, lzo, and zlib codec implementations and direct compressor/decompressor contracts.
- Retry APIs provide dynamic proxy wrapping around arbitrary interfaces with reusable retry policies.
- Serialization APIs define pluggable serializers/deserializers selected from configuration.
- IPC APIs expose Hadoop's `Writable`-based client/server RPC layer, versioned protocols, remote exception wrapping, and RPC metrics.
- Logging APIs expose runtime log-level adjustment via CLI and servlet.
- MapReduce APIs expose job submission, cluster/job status, input/output format contracts, split serialization, job configuration, counters, job history, persistence of retired jobs, notification, and CLI wrappers.

## Important APIs, Types, and Functions

### Compression

- `org.apache.hadoop.io.compress.GzipCodec` is only partially visible at the start of the chunk. The visible methods include `getCompressorType`, `createInputStream(InputStream)`, `createInputStream(InputStream, Decompressor)`, `createDecompressor`, `getDecompressorType`, and `getDefaultExtension`. The doc identifies it as a gzip compressor/decompressor factory.
- `GzipCodec.GzipInputStream` extends `DecompressorStream`. It has constructors from `InputStream` and protected `DecompressorStream`, plus `available`, `close`, `read()`, `read(byte[], int, int)`, `skip(long)`, and `resetState`.
- `GzipCodec.GzipOutputStream` extends `CompressorStream`. It has constructors from `OutputStream` and protected `CompressorStream`, plus `close`, `flush`, `write(int)`, `write(byte[], int, int)`, `finish`, and `resetState`. The class bridges `DeflaterOutputStream` into Hadoop's `CompressionOutputStream`.
- `LzoCodec` implements `Configurable` and `CompressionCodec`. It exposes `setConf`, `getConf`, static `isNativeLzoLoaded(Configuration)`, stream factories with optional `Compressor`/`Decompressor`, factory methods for compressor/decompressor instances and types, and `getDefaultExtension`.
- `LzoCompressor` implements `Compressor`. It supports a `CompressionStrategy` enum, direct buffer sizing, native-load checks, synchronized `setInput`, `setDictionary`, `finish`, `finished`, `compress`, `reset`, `getBytesRead`, `getBytesWritten`, and `end`.
- `LzoDecompressor` implements `Decompressor` with a matching `CompressionStrategy`, native-load checks, synchronized input/dictionary/state methods, `decompress`, `reset`, `end`, and protected `finalize`.
- `BuiltInZlibDeflater` extends `java.util.zip.Deflater` and implements Hadoop `Compressor`; `BuiltInZlibInflater` extends `java.util.zip.Inflater` and implements `Decompressor`. Both provide synchronized byte-array methods that throw `IOException`.
- `ZlibCompressor` and `ZlibDecompressor` implement direct-buffer native-style zlib compression/decompression with configurable headers, levels, strategies, byte counters, reset/end lifecycle, and dictionary support.
- `ZlibFactory` chooses zlib compressor/decompressor types and instances based on `Configuration`, falling back or selecting native code depending on `isNativeZlibLoaded`.

### Retry Framework

- `RetryPolicy` defines `shouldRetry(Exception e, int retries)`, returning whether to retry, returning false for "do not retry but do not fail" semantics for void methods, or throwing to fail.
- `RetryPolicies` is a static factory and constants holder. It exposes `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, `RETRY_FOREVER`, fixed-sleep count/time policies, proportional sleep, exponential backoff with randomness, exception-class dispatch, and `RemoteException`-aware dispatch.
- `RetryProxy` creates dynamic proxies for an interface and implementation, either with one policy for all methods or a `Map<String, RetryPolicy>` keyed by method name. Missing method-specific policies default to `TRY_ONCE_THEN_FAIL`.

### Serialization

- `Serializer<T>` and `Deserializer<T>` define stateful stream lifecycle APIs: `open(OutputStream/InputStream)`, `serialize(T)` or `deserialize(T reuse)`, and `close`.
- Their docs explicitly warn they are stateful but must not buffer across calls because other producers/consumers may interleave on the same stream.
- `Serialization<T>` encapsulates an accepted class family and provides matching serializer/deserializer instances.
- `SerializationFactory` extends `Configured`; its constructor reads `io.serializations` from `Configuration` as a comma-delimited class list.
- `WritableSerialization` adapts Hadoop `Writable` to the generic serialization framework through `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- `JavaSerialization` is marked experimental for `java.io.Serializable`; `JavaSerializationComparator` and `DeserializerComparator` compare byte ranges by deserializing objects and using regular comparators, while warning that direct `RawComparator` implementations are better for compare-heavy paths.

### IPC and RPC

- `Client` is Hadoop's low-level IPC client for single-`Writable` request/response calls. It has constructors with value class, `Configuration`, and optional `SocketFactory`; `stop`; `setTimeout`; single-address `call`; user-ticket-aware `call`; and parallel multi-address `call` returning nulls for timed-out or errored calls.
- `RemoteException` wraps remote exception class names and messages. `unwrapRemoteException(Class[])` can match desired exception types, and no-arg `unwrapRemoteException` tries to instantiate the wrapped throwable by class name/string constructor, otherwise returning itself.
- `RPC` builds dynamic client proxies for `VersionedProtocol`, waits for proxies, stops proxies, performs expert parallel reflective calls, and constructs `RPC.Server` instances.
- `RPC.Server` extends `Server` and dispatches `Writable` invocation requests to methods on a protocol implementation instance.
- `RPC.VersionMismatch` exposes protocol interface name, client version, and server version.
- `Server` is the abstract IPC service. It handles bind/listen lifecycle, thread start/stop/join, network timeout and send buffer configuration, listener address queries, static current server/remote IP/remote address accessors for code running under an RPC call, and an abstract `call(Writable, long)`.
- `VersionedProtocol` requires `getProtocolVersion(String protocol, long clientVersion)` and expects subclasses to define static `versionID`.
- `Server` exposes `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`.

### RPC Metrics and Runtime Log Control

- `RpcMetrics` implements `Updater`, registers JMX-facing RPC metrics, and publishes queue time, processing time, discarded operations, and a public metrics map. `doUpdates(MetricsContext)` pushes values to the metrics subsystem; `shutdown` tears down the metrics registration.
- `RpcMgtMBean` exposes sampled operation counts, average/min/max processing and queue times, discarded operation counts/queue time, open connection count, call queue length, and `resetAllMinMax`.
- `LogLevel` provides runtime log-level changes with a CLI `main(String[])`, a `USAGES` string, and `LogLevel.Servlet.doGet(HttpServletRequest, HttpServletResponse)` for HTTP-based changes.

### MapReduce Status, Persistence, Counters, and File Formats

- `ClusterStatus` implements `Writable` and reports task tracker count, running map/reduce counts, max map/reduce capacity, and `JobTracker.State`; `JobClient#getClusterStatus()` is the integration point.
- `CompletedJobStatusStore` implements `Runnable`; it persists retired job information in DFS when `persist.jobstatus.hours` is nonzero and exposes read methods for `JobStatus`, `JobProfile`, `Counters`, and ranges of `TaskCompletionEvent`.
- `Counters` implements `Writable` and `Iterable<Counters.Group>`. It groups counters by enum class/group, supports synchronized lookup, increment, merge, `sum`, size, binary read/write, logging, `toString`, and compact comma-separated `name=value` formatting.
- `Counters.Counter` and `Counters.Group` are `Writable` nested types. Counters hold display name/value and synchronized increments; groups localize display names, lookup counters by id/name, serialize themselves, and iterate over counters.
- `DefaultJobHistoryParser.parseJobTasks(String, JobHistory.JobInfo, FileSystem)` populates an object model from a job history log file.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are MapReduce validation exceptions. `InvalidInputException` wraps multiple input problems and exposes the list plus a concatenated message.
- `FileInputFormat<K,V>` is the base class for file-backed `InputFormat`. It defines splitability checks, static input path and path-filter configuration helpers, `listPaths`, default `validateInput`, default `getSplits`, split-size/block-index helpers, and abstract `getRecordReader`.
- `FileOutputFormat<K,V>` is the base class for file-backed `OutputFormat`. It defines output compression settings, compressor class selection, abstract `getRecordWriter`, output spec validation, output path configuration, and `getWorkOutputPath` for task-attempt temporary output.
- `FileSplit` implements `InputSplit` and `Writable`, representing a path/start/length plus host locations. The constructor taking `JobConf` is deprecated in favor of the host-list constructor.
- `InputFormat<K,V>` validates input, creates logical `InputSplit[]`, and returns a `RecordReader` that respects record boundaries.
- `InputSplit` is `Writable` and reports byte length plus locality hostnames.

### Job Client, Configuration, History, and CLI

- `JobClient` extends `Configured`, implements `MRConstants` and `Tool`, and is the primary client-side interface to `JobTracker`. It constructs/connects to default or specified job trackers, initializes with `JobConf`, closes resources, gets the submission `FileSystem`, submits jobs by job-file path or `JobConf`, retrieves `RunningJob`, map/reduce task reports, cluster status, pending/incomplete jobs, all jobs, and runs a job synchronously by polling progress. It also manages `TaskStatusFilter` in instance or `JobConf` form and has `run`/`main`.
- `JobConf` extends `Configuration` and is the central job description object. It has constructors from defaults, class/jar inference, inherited configuration, XML path/string, and extensive getters/setters for jar, system/local directories, user, input/output paths, input/output formats, compression, key/value classes, comparators, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce counts, retry/failure tolerances, job priority, profiling, debug scripts, job-end notifications, and localized job scratch directory.
- `JobConfigurable` defines `configure(JobConf)` for components initialized from job configuration.
- `JobEndNotifier` manages asynchronous job-completion notification: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification`.
- `JobHistory` handles append-mode job history files, master index files, listener-based parsing, initialization, disable toggles, and cleanup. It exposes `LOG` and `JOBTRACKER_START_TIME`.
- `JobHistory.HistoryCleaner` deletes history older than one month and updates the master index.
- `JobHistory.JobInfo` logs job submitted/started/finished/failed events, exposes all tasks, local job file path, and URL encoding/decoding helpers for history paths and filenames.
- `JobHistory.Keys`, `RecordTypes`, and `Values` are enums for history key namespace, record type tokens, and common string values.
- `JobHistory.Listener` handles parsed history records as `RecordTypes` plus key/value maps.
- `JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` log task/TIP and attempt lifecycle events with timestamps, hostnames, shuffle/sort times for reduces, counters, and errors.
- `JobPriority` is an enum describing priority.
- `JobProfile` implements `Writable`, tracking user, job id, job configuration file path, web UI URL, and job name for living or retired jobs.
- `JobShell` extends `Configured` and implements `Tool`; it parses `hadoop jar`-style submission flags for `-libjars`, `-archives`, and `-files`.
- `JobStatus` starts at the chunk end. Visible API includes constructors and the beginning of `getJobId`; it implements `Writable` and represents job id, map progress, reduce progress, and run state.

## Control Flow and Lifecycle

Because this is JDiff XML, implementation branches are not visible, but public lifecycle contracts are clear:

- Compression stream flow is `createOutputStream`/`createInputStream` from a codec, optionally using externally supplied compressor/decompressor instances, followed by repeated `write`/`read`, then `finish`/`flush`/`close`, with `resetState` for stream reuse. Raw compressor/decompressor flow is `setInput`, optional `setDictionary`, `compress`/`decompress` while consulting `needsInput`, `finish`/`finished`, `reset`, then `end`.
- Native codec selection flows through `LzoCodec.isNativeLzoLoaded` and `ZlibFactory.isNativeZlibLoaded`, then type/instance factory methods choose the concrete compressor/decompressor exposed to codecs and jobs.
- Retry flow wraps an implementation in a dynamic proxy. On failure, the proxy calls `RetryPolicy.shouldRetry(e, retries)`, sleeps according to the policy where applicable, retries, returns silently for allowed void failures, or rethrows.
- Serialization flow is factory selection from `io.serializations`, `accept(Class)` matching, `open`, repeated serialize/deserialize operations with potential object reuse, and `close`.
- IPC flow is client construction, proxy or direct `Client.call` invocation, server-side `Server.start`, queued request dispatch to `call(Writable, receiveTime)`, metrics update, and `stop`/`join` teardown. `RPC.getProxy` adds protocol-version checking through `VersionedProtocol`.
- MapReduce submission flow documented on `JobClient`: validate input and output specs, compute input splits, set up `DistributedCache` accounting, copy job jar/configuration into the distributed system directory, submit to `JobTracker`, and optionally monitor with `runJob`.
- File input flow is `FileInputFormat.validateInput`, `listPaths`, split computation bounded by filesystem block size/min split size, `InputFormat.getSplits`, then `getRecordReader` per split.
- File output flow is `FileOutputFormat.checkOutputSpecs`, `getRecordWriter`, task writes to `mapred.work.output.dir`, and successful task-attempt output promotion from `${mapred.output.dir}/_temporary/_${taskid}` to final output.
- Job history flow is `JobHistory.init`, append log records for job/task/attempt lifecycle, parse history with a listener or `DefaultJobHistoryParser`, then cleanup of old history files.
- Completed job persistence flow is `CompletedJobStatusStore.store(JobInProgress)` at retirement, later `readJobStatus`, `readJobProfile`, `readCounters`, and `readJobTaskCompletionEvents` from DFS.

## State and Persistence Behavior

- The compressors/decompressors are explicitly stateful: input buffers, dictionaries, counters, finish/finished flags, direct buffer size, native library state, and byte counters are observable. Many methods are synchronized, indicating mutable shared state protection on the object.
- Serializer/deserializer instances are stateful stream adapters but are contractually not allowed to buffer data beyond calls because streams can be shared with other producers/consumers.
- `Configuration`/`JobConf` is the persistent job control surface: most `JobConf` methods set named configuration properties that affect cluster behavior, submission, task JVMs, compression, scheduling, speculative execution, profiling, debug scripts, and notifications.
- `Writable` persistence is central. `ClusterStatus`, `Counters`, `Counters.Counter`, `Counters.Group`, `FileSplit`, `JobProfile`, and `JobStatus` are serialized through `DataOutput`/`DataInput` for RPC, DFS persistence, and job tracker/client communication.
- `Counters.write` documents a binary external format: group count followed by groups, display names, counter counts, and counter name/value pairs.
- `CompletedJobStatusStore` stores retired job data in DFS subject to a configured retain time; a daemon thread removes old persisted job files.
- `JobHistory` persists plain-text append-only records with `[type (key=value)*]` lines. A master index records job tracker/job start/stop information, and each job gets a separate history file named from job tracker id and job id.
- `FileOutputFormat.getWorkOutputPath` documents task-attempt temporary directories and promotion semantics, which are a persistence boundary for exactly-once output under failures/speculation.
- `JobConf.getJobLocalDir` exposes a localized per-job scratch directory under `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/`, also available as a system property.
- RPC metrics maintain interval state and min/max state through `MetricsTimeVaryingRate` fields exposed publicly and via JMX.

## Dependencies and Integration Points

- Compression depends on Java `InputStream`, `OutputStream`, `Deflater`, `Inflater`, Hadoop `CompressionCodec`, `CompressionInputStream`, `CompressionOutputStream`, `Compressor`, `Decompressor`, and `Configuration`.
- Native compression selection integrates with external zlib/lzo libraries and configuration-driven native-code availability.
- Retry integrates with Java dynamic proxy-style interface wrapping, `TimeUnit`, exception-class maps, and `RemoteException`.
- Serialization integrates with Hadoop `Configuration` through `io.serializations`, `Writable`, Java `Serializable`, `RawComparator`, and stream APIs.
- IPC integrates with sockets, `SocketFactory`, `InetSocketAddress`, `UserGroupInformation`, reflection `Method`, Hadoop `Writable`, metrics, JMX, and versioned protocol interfaces.
- Runtime log-level control integrates with servlet APIs and command-line execution.
- MapReduce APIs integrate with `FileSystem`, `Path`, `PathFilter`, `BlockLocation`, `FileStatus`, `DistributedCache`, `Mapper`, `Reducer`, `Partitioner`, `MapRunnable`, `RecordReader`, `RecordWriter`, `OutputCollector`, `Reporter`, `Progressable`, `Tool`, `JobTracker`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, and `SequenceFile.CompressionType`.
- Job history and completed-job store integrate with DFS/HDFS through `FileSystem` and with user-facing web UI through `JobProfile.getURL`.

## Risks and Edge Cases

- This chunk is API metadata only; method bodies, private fields, exact configuration keys for many setters, and runtime error handling details require source cross-checking outside this XML.
- Many compression objects expose mutable synchronized state. Incorrect pooling, missing `reset`, missing `end`, or mixing dictionaries can corrupt compression streams or leak native/direct-buffer resources.
- Native lzo/zlib availability is configuration- and environment-dependent. Code must tolerate factory fallback and `isNative*Loaded` false paths.
- `finalize` on decompressor classes implies cleanup may rely on GC as a backstop; callers should still use `end` deterministically.
- Retry policies can hide failures, especially `TRY_ONCE_DONT_FAIL` on void methods and `RETRY_FOREVER`; policy selection affects idempotency and backpressure.
- Serialization docs prohibit buffering because streams may be shared. A custom serializer/deserializer that buffers aggressively can break downstream readers/writers.
- `DeserializerComparator` deserializes for comparisons and is likely expensive in sort-heavy MapReduce paths; custom `RawComparator` is the intended optimization.
- `RemoteException.unwrapRemoteException` depends on class lookup and string constructors; missing classes or incompatible constructors fall back to the wrapper.
- RPC protocol versions are explicit through `VersionedProtocol`; missing or wrong `versionID`/`getProtocolVersion` behavior causes `RPC.VersionMismatch`.
- `Server.get`, `getRemoteIp`, and `getRemoteAddress` are context-sensitive and may return null outside valid RPC call contexts.
- `FileOutputFormat.getWorkOutputPath` warns about side-effect file races under speculative execution. Writers must use task-attempt-specific paths or the work output directory to avoid duplicate attempts writing the same HDFS path.
- The `JobConf.getNumMapTasks` doc visible here appears to say "reduce tasks" despite being a map method; this looks like a documentation typo in the API snapshot.
- `JobConf` contains deprecated input/output path methods; callers should use `FileInputFormat` and `FileOutputFormat` static helpers to avoid compatibility drift.
- `InvalidInputException` does not copy its problem list according to docs, so callers must not mutate the list after passing it or after retrieving it.
- `JobHistory` plain-text history parsing and URL encoding helpers make file naming, escaping, and backward-compatible parse behavior important.
- Completed job persistence is disabled when retain time is zero; callers of read methods must handle nulls or empty arrays.
- Runtime log-level servlet/CLI changes are operationally powerful and need access control in deployments, although this XML does not describe security checks.

## Test Signals

Useful tests for code corresponding to this API surface would include:

- Codec round trips for gzip, zlib, and lzo where available; factory fallback tests when native libraries are unavailable; `getDefaultExtension` and compressor/decompressor type consistency.
- Compressor/decompressor lifecycle tests covering `setInput`, partial reads/writes, `needsInput`, `finish`, `finished`, byte counters, `reset`, and `end`, including synchronized reuse paths.
- Retry proxy tests for fixed-count, max-time, proportional, exponential, exception-specific, remote-exception-specific, void-method no-fail, and forever policies with idempotent fake implementations.
- Serialization factory tests using `io.serializations`, `WritableSerialization`, Java serialization, object reuse in `deserialize(T)`, and stream interleaving behavior.
- IPC tests for direct `Client.call`, parallel calls with timeout/null results, UGI-ticket calls, proxy creation/stop, `VersionedProtocol` version mismatch, remote exception wrapping/unwrapping, server start/stop/join, listener address, call queue length, and remote address context methods.
- Metrics tests verifying `RpcMetrics.doUpdates`, JMX bean values, discarded-operation tracking, min/max reset, open connection count, and call queue length.
- `FileInputFormat` tests for path parsing, path filters, nonexistent/mixed input validation, split sizing around block size and `mapred.min.split.size`, unsplittable inputs, and host locality in `FileSplit`.
- `FileOutputFormat` tests for output path validation, existing-output failure, compression codec configuration, work output path formation, and promotion/cleanup behavior under failed and speculative task attempts.
- `Counters` tests for enum and string lookup, localization fallback, synchronized increments, merge/sum behavior, binary write/read compatibility, compact string generation, and logging output.
- `JobClient` tests for submission preflight order, job-file and `JobConf` submission, polling in `runJob`, task report retrieval, task output filter persistence in `JobConf`, and resource close behavior.
- `JobConf` tests for class/jar inference, XML/path constructors, deprecated path compatibility, mapper/reducer/combiner/partitioner/input/output format class storage, compression settings, speculative toggles, failure thresholds, profiling ranges/params, debug script DistributedCache expectations, notification URI substitution, and local/system directory resolution.
- Job history tests for init success/failure, disabled history, submitted/started/finished/failed/killed records, map/reduce attempt records including shuffle/sort times, listener-based streaming parse, object-model parse, URL encode/decode helpers, master index updates, and history cleanup retention.
- Completed job store tests for disabled retain time, DFS write/read of status/profile/counters/events, range slicing of task completion events, null/empty responses on missing jobs, and cleanup daemon behavior.

## Chunk Boundary Notes

The first visible lines are the tail of `GzipCodec`; earlier gzip class declarations and output-stream factory methods are outside this chunk. The final visible line starts `JobStatus.getJobId`; the rest of `JobStatus` is outside this chunk and must be covered by the following chunk before producing the merged per-file report.

### subset-b-007262: lines 25081-31138

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 25081-31138

## Scope

This chunk is a JDiff API XML slice for Hadoop 0.17.0. It begins inside `org.apache.hadoop.mapred.JobStatus`, covers most of the public old `mapred` package surface from `JobSubmissionProtocol` through `TextOutputFormat`, includes the `org.apache.hadoop.mapred` package overview, then covers `org.apache.hadoop.mapred.jobcontrol` and most of `org.apache.hadoop.mapred.join` through the start of `WrappedRecordReader`.

Because this source is generated API metadata, the research describes exported classes, interfaces, fields, method signatures, and Javadoc contracts rather than implementation bodies. Control-flow and state notes are inferred from method names, synchronization flags, inheritance, writable serialization methods, and embedded documentation.

## Purpose

The chunk documents Hadoop's pre-YARN MapReduce public API and daemon-facing protocols. It spans:

- Client to JobTracker RPC through `JobSubmissionProtocol` and its `JobTracker` implementation.
- JobTracker and TaskTracker process APIs, heartbeats, task assignment, task completion events, task logs, diagnostic reporting, and status web UI hooks.
- User-facing MapReduce programming interfaces: `Mapper`, `Reducer`, `MapRunnable`, `MapRunner`, `Partitioner`, `OutputCollector`, `Reporter`, `RecordReader`, `RecordWriter`, `InputFormat` and `OutputFormat` variants.
- File and sequence-file input/output adapters, text line readers, key-value line readers, multi-file splits, map-file outputs, and output compression settings.
- Higher-level job dependency orchestration in `mapred.jobcontrol`.
- Composable/join input APIs in `mapred.join`, including join expression parsing, composite splits/readers, resettable value iterators, and tuple serialization.

The package-level documentation in this range also states the classic MapReduce data-flow contract: input `<k1,v1>` pairs are mapped to intermediate `<k2,v2>` pairs, optionally combined, shuffled and partitioned by key, reduced to `<k3,v3>` output, and stored through an `OutputFormat`/`RecordWriter` on a Hadoop `FileSystem`.

## Important APIs, Types, and Functions

### Job and Tracker Control

`JobStatus` is partially visible at the start of the slice. The visible contract includes synchronized getters for map/reduce progress, run state, start time, and username; synchronized `setRunState(int)`; writable `write(DataOutput)`/`readFields(DataInput)`; and public state constants `RUNNING`, `SUCCEEDED`, `FAILED`, and `PREP`. It is documented as a compact status summary rather than a full `JobProfile`.

`JobSubmissionProtocol` extends `VersionedProtocol` and is the public RPC contract between `JobClient` and `JobTracker`. It allocates job ids (`getNewJobId()`), accepts staged jobs (`submitJob(String)`), exposes cluster status, kills jobs and task attempts, returns `JobProfile`, `JobStatus`, `Counters`, map/reduce `TaskReport[]`, task completion events, task diagnostics, filesystem name, incomplete jobs, and all jobs. Its `versionID` field makes wire compatibility explicit.

`JobTracker` implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. The public surface includes daemon lifecycle (`startTracker(JobConf)`, `stopTracker()`, `offerService()`, `main(String[])`), protocol version lookup, configured bind address lookup, tracker identity/ports/start time, job queues (`runningJobs()`, synchronized `getRunningJobs()`, `failedJobs()`, `completedJobs()`), TaskTracker state (`taskTrackers()`, `getTaskTracker(String)`), network topology placement (`resolveAndAddToTopology()`, `getNode()`, `getParentNode()`, cache-level counters), and RPC operations mirroring `JobSubmissionProtocol`. It also exposes heartbeat handling from TaskTrackers, tracker error reporting, task assignment lookup, and local job-file path lookup. Nested `JobTracker.IllegalStateException` and enum-like `JobTracker.State` are part of the public API.

`RunningJob` is the client handle for a submitted job. It exposes identifiers, job file, tracking URL, map/reduce progress, completion/success status, blocking `waitForCompletion()`, job kill, task completion event pagination, task kill, and counters.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. Its API covers construction from `JobConf`, task-tracker metrics, protocol version, storage cleanup, shutdown/close, connection to the JobTracker, report address, main run loop, task fetch, task status updates, diagnostic reporting, liveness ping, task completion, shuffle and local filesystem error reporting, map completion event fetch, lost map-output reporting, idle state, and process entry point. Nested public APIs include `TaskTracker.Child.main()` for child task JVMs, `MapOutputServlet` for serving map outputs over HTTP, and `TaskTrackerMetrics` as a metrics `Updater`.

`TaskCompletionEvent` is a writable event record for JobTracker task-completion history. It has a default writable constructor and a constructor carrying event id, task id, runtime, map/reduce flag, status, and task-tracker HTTP address. It provides getters/setters, `toString()`, helpers `isMapTask()` and `idWithinJob()`, writable serialization, `EMPTY_ARRAY`, and nested status enum values. The Javadoc requires event ids to be assigned incrementally per job starting at zero.

`TaskReport` is a writable task summary with task id, progress, state string, diagnostics, counters, finish time, start time, and `write()`/`readFields()`.

### MapReduce User Interfaces

`Mapper<K1,V1,K2,V2>` extends `JobConfigurable` and Hadoop `Closeable`. Its single `map(K1,V1,OutputCollector<K2,V2>,Reporter)` method is the user transform hook for one input key/value pair.

`Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and `Closeable`. Its `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)` method receives grouped values for a key and emits final output.

`MapReduceBase` is the convenience base implementation for `JobConfigurable` and `Closeable`, with default `configure(JobConf)` and `close()` methods.

`MapRunnable<K1,V1,K2,V2>` extends `JobConfigurable` and defines `run(RecordReader<K1,V1>, OutputCollector<K2,V2>, Reporter)`. `MapRunner` is the default implementation, configuring itself from `JobConf` and iterating the reader to call the configured mapper.

`OutputCollector<K,V>` emits intermediate or final key/value pairs through `collect(K,V)`.

`Partitioner<K2,V2>` extends `JobConfigurable` and maps an intermediate key/value to a reducer partition through `getPartition(K2,V2,int)`.

`Reporter` extends `Progressable` and lets tasks update status, increment named counters, and access their `InputSplit`. `Reporter.NULL` is a public no-op reporter.

`RecordReader<K,V>` defines old-API split reads with caller-reused key and value objects: `next(K,V)`, `createKey()`, `createValue()`, `getPos()`, `getProgress()`, and `close()`.

`RecordWriter<K,V>` writes output key/value pairs and closes with a `Reporter`.

`OutputFormat<K,V>` creates a `RecordWriter` from `FileSystem`, `JobConf`, output name, and `Progressable`, and validates output specs through `checkOutputSpecs(FileSystem, JobConf)`.

`OutputFormatBase<K,V>` implements `OutputFormat` and adds static output compression configuration helpers: `setCompressOutput()`, `getCompressOutput()`, `setOutputCompressorClass()`, and `getOutputCompressorClass()`. Its writer/spec methods remain public hooks.

### Input and Output Formats

`LineRecordReader` reads text lines as `<LongWritable byteOffset, Text line>`. Constructors accept `Configuration`/`FileSplit` or raw `InputStream` with start/end offsets, optionally plus configuration. It provides key/value factories, `next()`, progress, position, and close. Nested `LineReader` wraps an `InputStream`, closes it, and reads a line into `Text` with a maximum length.

`TextInputFormat` extends `FileInputFormat<LongWritable,Text>`, is configurable, decides splitability, and creates `LineRecordReader` instances. Its Javadoc states lines are delimited by linefeed or carriage return, keys are byte positions, and values are line text.

`KeyValueLineRecordReader` reads each line into `Text` key and `Text` value by locating a separator with `findSeparator(byte[], int, int)`. `KeyValueTextInputFormat` configures the separator behavior, decides splitability, and creates this reader.

`TextOutputFormat<K,V>` extends `FileOutputFormat` and returns a line-oriented `RecordWriter`. Its protected nested `LineRecordWriter` synchronizes `write(K,V)` and `close(Reporter)` around a `DataOutputStream`.

`SequenceFileInputFormat<K,V>` lists input paths and creates `SequenceFileRecordReader<K,V>`. `SequenceFileRecordReader` exposes key/value classes, factories, both standard and raw-ish `next()` forms, current value access, progress, position, `seek(long)`, close, and a protected `conf` field.

`SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` adapt sequence file records to `Text` keys and values.

`SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` adapt sequence file keys/values to `BytesWritable` and expose original key and value class names.

`SequenceFileInputFilter` extends sequence-file input with a configurable filter class. The nested `Filter` interface is `Configurable` and tests keys with `accept(Object)`. `FilterBase` stores configuration. `MD5Filter`, `PercentFilter`, and `RegexFilter` provide static configuration setters and implement key acceptance by MD5 frequency, percent frequency, and regular expression matching respectively.

`SequenceFileOutputFormat` writes sequence files, creates `SequenceFile.Reader[]` for existing output directories, and controls output compression type through `getOutputCompressionType(JobConf)` and `setOutputCompressionType(JobConf, SequenceFile.CompressionType)`.

`MapFileOutputFormat` writes map files, opens multiple `MapFile.Reader` instances, and retrieves an entry by partitioning a key across readers with `getEntry(...)`.

`MultiFileInputFormat<K,V>` groups multiple files into splits and delegates reader creation to subclasses. `MultiFileSplit` is a writable `InputSplit` over parallel `Path[]` and `long[]` lengths, with total length, per-path length, path accessors, locations, serialization, and `toString()`.

`OutputLogFilter` implements `PathFilter` to reject output-log paths from output listings.

### Status HTTP, Logs, and Diagnostics

`StatusHttpServer` is an embedded Jetty wrapper for daemon status pages. It constructs from server name, bind address/name, port, and `findPort`; exposes webapp attributes; installs servlets; reports the selected port; configures thread counts and SSL listener; starts and stops. The documented contexts are `/logs/`, `/static/`, and `/` JSP content from `src/webapps/<name>`.

`StatusHttpServer.StackServlet` serves current stack traces and logs them. `TaskGraphServlet` emits SVG task-status graphs and exposes public graph dimension/margin constants.

`TaskLog` manages task user logs. Static APIs resolve task log files by task id and log name, purge old logs, read the configured maximum log length, wrap commands so stdout/stderr are captured to files with optional tail truncation and setup commands, quote commands through `addCommand()`, and capture debug output. Nested `LogName` is an enum-like type with `toString()`. Nested `TaskLog.Reader` is an `InputStream`-style reader over one task log name and byte range.

`TaskLogAppender` is a log4j appender with task id and total log file size properties. It activates options, appends logging events, and closes.

`TaskLogServlet` exposes task logs over HTTP through `doGet()`.

### JobControl

`org.apache.hadoop.mapred.jobcontrol.Job` wraps a `JobConf` with dependency and state management. It has constructors with or without depending jobs, getters/setters for job name, internal job id, MapReduce job id, job conf, state, and message; dependency access; `addDependingJob(Job)`; readiness and completion checks; `submit()`; and `main()`. Public state constants are `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`.

`JobControl` is a `Runnable` manager for dependent jobs. It is constructed with a group name and exposes lists for waiting, running, ready, successful, and failed jobs. It can add one or more jobs, report controller state, stop, suspend, resume, determine whether all jobs are finished, and run its scheduler loop.

### Join and Composite Input APIs

`ArrayListBackedIterator<X extends Writable>` implements `ResetableIterator<X>` using an in-memory `ArrayList`. It supports construction with an empty or supplied list, `hasNext()`, copying next/replayed values into a supplied writable, reset, add, close, and clear.

`ResetableIterator<T extends Writable>` is the core stateful replay iterator abstraction. It can test availability, copy the next element into a caller-provided writable, replay the last value, reset to the start, add elements, close data sources, and clear state for reuse. The Javadoc requires FIFO replay order after reset and warns that `next()` may fail for nested joins even when more elements exist if join constraints are not satisfied. `ResetableIterator.EMPTY` is a no-op implementation.

`StreamBackedIterator<X extends Writable>` implements `ResetableIterator` with a byte-array-backed stream, trading memory representation and serialization for replayability.

`TupleWritable` is a writable, iterable tuple of child `Writable` values. It has empty and array constructors, `has(int)`, `get(int)`, `size()`, equality/hash/string methods, iterator support that does not flatten nested tuples, and writable serialization. The documented wire format is count, child types, then child objects.

`ComposableInputFormat<K,V>` extends `InputFormat` and returns `ComposableRecordReader<K,V>`. `ComposableRecordReader<K,V>` extends `RecordReader` and `Comparable`, adding stream id, current key access/copy, `hasNext()`, key skipping, and `accept(CompositeRecordReader.JoinCollector,K)` to register matching values with a join collector.

`CompositeInputFormat<K>` implements `ComposableInputFormat<K,TupleWritable>`. It has static expression helpers `compose()` and `addDefaults()`, validates input, creates composite splits, and constructs composite record readers from a join expression. Its Javadoc-visible role is expression-based composition of multiple input formats.

`CompositeInputSplit` is a writable `InputSplit` that groups child splits. It supports empty and capacity constructors, `add(InputSplit)`, child access, total and indexed lengths, aggregate and indexed locations, and serialization.

`CompositeRecordReader<K,V,X>` is a configurable base for join readers. It is constructed with stream id, child count, and comparator class; exposes abstract-ish `combine(Object[], TupleWritable)` behavior, id, configuration, a priority queue of child readers, the comparator, child add, key access/copy, `hasNext()`, `skip(K)`, delegate iterator creation, collector accept/fill, comparison, key/value creation, position, close, progress, and fields for the join collector and children.

`JoinRecordReader<K>` implements `ComposableRecordReader<K,TupleWritable>` for joins that emit `TupleWritable` values. It has `next(K,TupleWritable)`, tuple factory, and delegate iterator. Its nested `JoinDelegationIterator` implements resettable tuple replay.

`InnerJoinRecordReader`, `OuterJoinRecordReader`, and `OverrideRecordReader` specialize join semantics. Inner and outer readers expose `combine(...)`; override readers expose `emit(TupleWritable)` and override `fillJoinCollector(...)`, indicating value selection from competing streams.

`MultiFilterRecordReader<K,V>` is another composite-reader specialization that emits one value type instead of a full tuple. It defines `emit(TupleWritable)`, `combine(...)`, `next(K,V)`, `createValue()`, and a resettable delegate. Its nested `MultiFilterDelegationIterator` replays emitted values.

`Parser` and nested token/node types parse join expressions. `Parser.Node` implements `ComposableInputFormat`, stores an identifier, stream id, comparator class, and a static map from identifiers to composable record-reader constructors. It can register identifiers, assign id, and set key comparator. `NodeToken`, `NumToken`, `StrToken`, generic `Token`, and `TType` model parser tokens.

`WrappedRecordReader<K,U>` is partially visible at the end of the chunk. It implements `ComposableRecordReader<K,U>` by wrapping a normal `RecordReader`; the visible API includes id, current key access/copy, `hasNext()`, `skip(K)`, protected advancement, collector accept, public `next(K,U)`, key/value factories, progress, position, and close.

## Control Flow

Job submission flow begins with `JobClient` calling `JobSubmissionProtocol.getNewJobId()`, staging job files under the JobTracker system directory for that id, then calling `submitJob(jobName)`. The JobTracker returns a `JobStatus`; clients can poll status/profile/counters/task reports, page through task completion events, ask for diagnostics, or kill jobs/tasks.

Tracker daemon flow is split across two protocols. TaskTrackers call JobTracker-side heartbeat/reporting APIs and receive `HeartbeatResponse` assignments. Child task JVMs call TaskTracker-side `TaskUmbilicalProtocol` methods visible through `TaskTracker`: `statusUpdate()`, diagnostic reporting, liveness ping, `done()`, shuffle/local filesystem error reporting, and map-output-lost reporting. Reduce tasks obtain map completion locations through completion event pagination and fetch outputs through `TaskTracker.MapOutputServlet`.

The old MapReduce application flow is explicitly described in package documentation. An `InputFormat` creates `InputSplit`s. Each map task uses a `RecordReader` to repeatedly fill reusable key/value objects and passes those to `Mapper.map()`. The mapper uses `OutputCollector.collect()` and `Reporter` updates. Intermediate keys are partitioned by `Partitioner`, optionally combined, fetched by reducers over HTTP, grouped by key, and supplied to `Reducer.reduce()`. Reducers emit final records through a `RecordWriter` created by the configured `OutputFormat`.

Reader/writer control flow is pull-based and object-reuse-oriented. Callers allocate keys and values via `createKey()` and `createValue()`, then loop while `next(key,value)` returns true. Implementations expose byte position and fractional progress so tasks can report progress. Writers accept key/value pairs until `close(Reporter)`.

Text and key-value input formats follow line-oriented flow: split a file, choose whether the file is splitable, read lines within split boundaries, derive key/value pairs from byte offset or separator position, and close the stream. Sequence-file readers instead use Hadoop `SequenceFile.Reader` metadata and support typed object creation plus seeking.

Status HTTP flow is daemon-local. A `StatusHttpServer` creates a Jetty server, publishes daemon objects through context attributes, installs servlets, optionally binds SSL, starts asynchronously, and is later stopped. Stack, task graph, task log, and map-output servlets expose diagnostic or shuffle data through servlet `doGet()` methods.

JobControl flow is a small scheduler loop. Jobs start in waiting states, dependencies are checked through `isReady()` and `isCompleted()`, ready jobs are submitted, running jobs transition to success or failure, and dependent jobs can become `DEPENDENT_FAILED`. `JobControl` can be suspended, resumed, stopped, or run until all jobs finish.

Join flow starts with a composition expression built by `CompositeInputFormat.compose()` or supplied directly in configuration. `Parser` builds a tree of `Parser.Node` instances that resolve identifiers to composable record-reader constructors. `CompositeInputFormat` validates inputs, builds one `CompositeInputSplit` from child splits, creates child `ComposableRecordReader`s, and delegates to a `CompositeRecordReader` subclass. Composite readers keep child readers in a priority queue ordered by key comparator, collect matching values for the current key into resettable iterators, and combine them according to inner, outer, override, or multi-filter semantics.

## State and Persistence Behavior

The XML file itself is generated public API inventory and has no runtime persistence. The APIs it describes are heavily stateful.

Writable state appears in `JobStatus`, `MultiFileSplit`, `ReduceTaskStatus`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable`. These types use Hadoop `DataInput`/`DataOutput` serialization and therefore are compatibility-sensitive in RPC, split planning, task status propagation, and join value materialization.

Tracker state is distributed and process-local. `JobTracker` owns job queues, task-tracker registrations, job ids, topology resolution, job counters, task completion events, task diagnostics, and filesystem/system-directory locations. `TaskTracker` owns local task execution state, local storage cleanup, map output availability, user logs, task child processes, and the HTTP endpoint used by reducers.

MapReduce task state is communicated by status objects, reporters, counters, and completion events. Several JobTracker and TaskTracker methods are marked synchronized in the API XML, especially progress/state reads or task-update callbacks, signaling concurrent access from RPC, timer, and worker threads.

Input split and reader state is transient but serializable where needed. Splits persist enough path/offset/length/location metadata to move from JobTracker planning to TaskTracker execution. RecordReaders track current stream position and progress. `LineRecordReader` and `SequenceFileRecordReader` own open streams/readers until `close()`.

Output state is controlled by `OutputFormatBase` compression settings in `JobConf` and by `RecordWriter` implementations that write to `FileSystem` streams. `TextOutputFormat.LineRecordWriter` synchronizes writes and close, indicating possible shared access or defensive serialization around its stream.

Task logging state lives in local log files and log4j appenders. `TaskLog` APIs cap log size, capture stdout/stderr, purge old user logs, quote command lines, and expose bounded readers. Incorrect cleanup or capture behavior directly affects post-failure diagnostics.

JobControl state is explicit through integer constants and job lists: waiting, ready, running, successful, failed, and dependent-failed. A `Job` stores both the wrapper id and the underlying MapReduce job id, plus a human message and its dependency list.

Join state is centered on resettable iterators and tuple bitsets. `ArrayListBackedIterator` stores values in memory; `StreamBackedIterator` stores replay data in a byte array; `ResetableIterator.EMPTY` represents no values. `TupleWritable` stores child writables plus per-position presence state. Composite readers maintain a priority queue, child array, join collector, comparator, and delegate iterators for repeated combination.

## Dependencies and Integration Points

The APIs integrate with Hadoop core interfaces from `org.apache.hadoop.io`, `org.apache.hadoop.fs`, `org.apache.hadoop.conf`, `org.apache.hadoop.ipc`, `org.apache.hadoop.net`, `org.apache.hadoop.util`, and old MapReduce classes such as `JobConf`, `JobClient`, `JobProfile`, `ClusterStatus`, `Counters`, `TaskStatus`, `InputSplit`, `FileInputFormat`, and `FileOutputFormat`.

RPC integration is through `VersionedProtocol`, `JobSubmissionProtocol`, `InterTrackerProtocol`, and `TaskUmbilicalProtocol`. The version id fields and protocol-version methods are important for old Hadoop daemon/client compatibility.

Filesystem integration is broad: input/output formats use `FileSystem`, `Path`, `PathFilter`, split locations, map/sequence files, compression codecs, and task output naming. The package documentation assumes most job input and output is stored in a Hadoop `FileSystem`.

Serialization integration uses Hadoop `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, `SequenceFile`, `MapFile`, and `DataInput`/`DataOutput`. Join and sequence-file APIs depend on stable writable class names and constructors.

HTTP integration uses embedded Jetty and servlet APIs (`HttpServlet`, requests, responses, `ServletException`) for daemon status, task logs, task graphs, stack traces, and map-output shuffle serving.

Logging and metrics integration uses Apache Commons Logging, log4j appenders/events, and Hadoop metrics `Updater`/`MetricsContext`.

JobControl integrates with `JobConf` and old `JobClient` submission semantics while adding its own wrapper-level dependency graph. Join APIs integrate with `InputFormat` implementations through reflection-like constructor registration in `Parser.Node.rrCstrMap`.

## Risks and Edge Cases

This is old `mapred` API surface, so compatibility risk is high. Public signatures, writable field ordering, RPC method names, protocol versions, and enum/state constants can affect clients, daemons, serialized splits, task status messages, and on-disk/intermediate data.

The line range starts inside `JobStatus` and ends inside `WrappedRecordReader`. A final reconciled report must merge adjacent chunks to avoid treating either class as complete based only on this slice.

Job and task kill APIs distinguish killing a task attempt from failing it through `killTask(taskId, shouldFail)`. Tests and callers need to preserve this distinction because it affects whether a failed attempt counts toward job failure.

Task completion event pagination depends on monotonically increasing per-job event ids and correct `fromEventId`/`maxEvents` handling. Off-by-one errors can make reducers miss map outputs or clients miss diagnostics.

Tracker methods are concurrent RPC entry points. The synchronized flags visible on heartbeat, status update, diagnostics, ping, done, shuffle error, filesystem error, map-output-lost, and idle checks indicate thread-safety pressure around mutable tracker state.

Text input edge cases include split boundaries, CR/LF handling, very long lines, and key-value separator detection. Incorrect boundary logic can duplicate or drop lines at split edges.

Sequence-file adapters depend on stored key/value class metadata. Binary and text adapters must preserve bytes or text conversion without corrupting arbitrary writable data.

Output compression settings are stored in `JobConf`, so defaults, codec class lookup, and compression type need compatibility with existing jobs. `OutputFormat.checkOutputSpecs()` must reject invalid output paths early enough to avoid partial writes.

HTTP servlets expose operational data and shuffle data. Risks include leaking logs, mishandling byte ranges, serving stale or lost map outputs, incorrect SSL listener configuration, and blocking daemon threads in servlet handlers.

`TaskLog.captureOutAndError()` and `addCommand()` manipulate shell commands. Quoting, executable path handling, setup command ordering, and tail truncation are security and diagnostics sensitive.

JobControl uses integer state constants and mutable dependency lists. Cyclic dependencies, dependency failure propagation, suspension/resume races, duplicate job submission, and inconsistent wrapper id versus MapReduce job id are natural edge cases.

Join APIs are complex and stateful. Resettable iterators require callers to call `reset()` after `add()` to avoid concurrent modification; nested joins can have available elements that do not satisfy join constraints; stream-backed replay depends on writable serialization; tuple serialization depends on writable class availability; and comparator mismatches across sources can break grouping.

`CompositeInputSplit` must keep child splits aligned with child input formats. Incorrect length/location aggregation can hurt scheduling locality or create invalid task assignments.

## Test Signals

For `JobSubmissionProtocol` and `JobTracker`, tests should cover job id uniqueness, system-directory staging assumptions, successful submission, invalid/missing job files, cluster status reporting, job/profile/status/counter lookups, map/reduce task reports, task diagnostics, job kill, task kill with both `shouldFail` values, task completion event pagination, and protocol version compatibility.

Tracker integration tests should cover TaskTracker heartbeat initial contact, response id sequencing, task assignment, task status updates, diagnostic reporting, child liveness ping, `done()` promotion behavior, shuffle error handling, filesystem error handling, map output lost notification, idle detection, TaskTracker shutdown/cleanup, and map-output servlet fetches.

Writable round-trip tests should exist for every visible writable type: `JobStatus`, `TaskCompletionEvent`, `TaskReport`, `MultiFileSplit`, `ReduceTaskStatus`, `CompositeInputSplit`, and `TupleWritable`. Tests should include empty/default constructors because those are required by Hadoop deserialization.

MapReduce programming contract tests should cover mapper and reducer invocation with reusable objects, `MapRunner` iteration over a `RecordReader`, reporter status and counters, partitioner bounds, `Reporter.NULL`, and correct close/configure ordering through `MapReduceBase`.

Input format tests should exercise line splitting at file boundaries, CR/LF variants, long lines, compressed versus splitable files where applicable, key-value separator configuration, empty values, sequence-file class metadata, binary sequence-file reads, text sequence-file conversion, filter configuration, MD5/percent/regex filter acceptance, multi-file split serialization, and locality arrays.

Output format tests should cover text output formatting for null/empty keys or values, synchronized close behavior, compression flags and codec class settings in `JobConf`, sequence-file compression type, map-file output lookup across partitioned readers, and `OutputLogFilter` rejection of log paths.

Status server and logging tests should cover port selection with `findPort`, context attributes, servlet registration, SSL listener setup failures, start/stop lifecycle, stack servlet response, task graph servlet response, task log file resolution, log cleanup by retain hours, command quoting, stdout/stderr capture with whole-output and tail modes, debug-output capture, `TaskLog.Reader` byte ranges, and appender task id/log-size properties.

JobControl tests should cover dependency readiness, successful submission order, failed dependency propagation to `DEPENDENT_FAILED`, state-list membership, `allFinished()`, suspend/resume/stop behavior, duplicate dependencies, and cyclic dependency handling or rejection.

Join tests should cover `CompositeInputFormat.compose()` expression strings, parser identifier registration, comparator selection, composite split child alignment, inner join emission only on all matching sources, outer join emission with missing tuple positions, override join value selection, multi-filter emission, priority queue ordering, key skip behavior, resettable iterator FIFO replay, `reset()` after `add()`, `EMPTY` iterator no-op behavior, stream-backed iterator writable serialization, tuple `has()`/`get()`/iteration/string/equality/hash semantics, and serialization round trips for nested tuples.

## Cross-Chunk Notes

The preceding chunk contains the beginning of `JobStatus`; this chunk only captures its trailing methods and constants.

The following chunk should contain the rest of `WrappedRecordReader` and any remaining `org.apache.hadoop.mapred.join` API declarations. Merge/reconciliation should combine those fragments before making final per-file conclusions about the join package.

The API references many classes declared outside this range, including `JobClient`, `JobConf`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `TaskStatus`, `ClusterStatus`, `Counters`, `HeartbeatResponse`, `Task`, `InterTrackerProtocol`, and `TaskUmbilicalProtocol`. Final file-level research should connect this chunk to the chunks where those declarations appear.

### subset-b-007263: lines 31139-37383

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 31139-37383

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop 0.17.0. It starts at the tail of `org.apache.hadoop.mapred.join.WrappedRecordReader`, includes package documentation for the join framework, then covers `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, `org.apache.hadoop.mapred.pipes`, the old Hadoop metrics API and SPI packages, network utilities in `org.apache.hadoop.net`, and the beginning of the record I/O package `org.apache.hadoop.record`. It ends inside `CsvRecordOutput`, after the `writeDouble(double, String)` signature.

The source is generated compatibility metadata, not implementation source. The research surface is therefore the externally visible contract: packages, classes, interfaces, inheritance, implemented interfaces, fields, constructors, method signatures, exceptions, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadocs.

## Purpose

The join tail documents `WrappedRecordReader` as the proxy that keeps the current head key/value and buffered matching values for a sorted-data join. The package documentation explains the pre-map join framework, its `mapred.join.expr` grammar, default identifiers (`inner`, `outer`, `override`), optional key comparator, and custom join-operation extension points.

The `org.apache.hadoop.mapred.lib` portion exposes common old-MapReduce building blocks: identity and inverse mappers, identity and summing reducers, hash and key-field partitioners, regex and token-count mappers, multithreaded map execution, null output, field selection, and multiple-output formats for splitting job output by key/value or source input file.

The `org.apache.hadoop.mapred.lib.aggregate` portion documents Hadoop's Aggregate framework. It turns mapper output into typed aggregation-id/value pairs, combines and reduces them with built-in aggregators, and allows user-defined descriptors to generate aggregation keys. Built-ins include numeric sums, long min/max, string min/max, unique value counting, and histograms.

The `org.apache.hadoop.mapred.pipes` portion exposes the Java submitter for Hadoop Pipes, allowing C++ components to participate in map/reduce jobs. It controls the executable URI, Java-versus-native reader/mapper/reducer/writer flags, debug command-file retention, and job submission.

The metrics packages document Hadoop's original metrics API. `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, and `MetricsUtil` define the public metrics reporting model; `file`, `ganglia`, `jvm`, `spi`, and `util` packages provide file/Ganglia emitters, JVM/log4j counters, provider-side buffering, MBean registration, and convenience metric value objects.

The `org.apache.hadoop.net` portion documents network identity, socket, rack-topology, and socket-factory APIs. It includes DNS helpers, pluggable DNS-to-rack mapping, socket factory lookup from configuration, static hostname resolution for tests, timeout-capable NIO socket streams, network topology selection, and node path modeling.

The `org.apache.hadoop.record` portion starts Hadoop record I/O. It exposes binary and CSV record input/output adapters and the mutable `Buffer` byte sequence used as a record-native type.

## Important APIs, Types, and Functions

### Join Tail

- `WrappedRecordReader.compareTo(ComposableRecordReader<K, ?>)` compares current head keys, and `equals(Object)` follows the comparison contract. `close()` forwards to the proxied reader. This class is the visible per-source reader proxy used by composable join readers.
- Join package documentation defines the expression grammar `func ::= ident(func,...)` and `tbl(class,"path")`, required `mapred.join.expr`, optional `mapred.join.keycomparator`, and custom `mapred.join.define.<ident>` mapping.

### Mapred Library

- `FieldSelectionMapReduce` implements both `Mapper<K,V,Text,Text>` and `Reducer<Text,Text,Text,Text>`. It parses field lists from `map.output.key.value.fields.spec` and `reduce.output.key.value.fields.spec`, uses `mapred.data.field.separator`, ignores the map key for `TextInputFormat`, and emits selected fields as output keys and values.
- `HashPartitioner<K2,V2>` partitions by `Object.hashCode()`. `KeyFieldBasedPartitioner<K2,V2>` has the same public partitioner shape in this snapshot, with configuration plus `getPartition`.
- `IdentityMapper`, `IdentityReducer`, and `InverseMapper` provide direct pass-through map, pass-through reduce, and key/value swap map behavior over old `mapred` APIs.
- `LongSumReducer<K>` sums `LongWritable` values for each key.
- `MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` that returns a composite `RecordWriter`. Protected hooks include `generateLeafFileName`, `generateFileNameForKeyValue`, `generateActualKey`, `generateActualValue`, `getInputFileBasedOutputFileName`, and abstract `getBaseRecordWriter`.
- `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` implement base writer construction for sequence-file and text output.
- `MultithreadedMapRunner` implements `MapRunnable<K1,V1,K2,V2>` with `configure` and `run`, intended for maps whose bottleneck is not CPU.
- `NullOutputFormat` consumes output while still satisfying `OutputFormat` with `getRecordWriter` and `checkOutputSpecs`.
- `RegexMapper` extracts text matching a configured regular expression; `TokenCountMapper` emits token/frequency pairs using tokenization.

### Aggregate Framework

- `ValueAggregator` defines the aggregator lifecycle: `addNextValue(Object)`, `reset()`, `getReport()`, and `getCombinerOutput()`.
- `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram` implement `ValueAggregator`. Numeric aggregators accept object/string forms plus primitive overloads where present. Combiner output is a compact representation that downstream reducers can aggregate again.
- `UniqValueCount` supports `setMaxItems(long)`, exposes `getUniqueItems()`, and returns unique items for combiner use. Its max-item limit is an important memory-control contract.
- `ValueHistogram` accepts values in a value/count form, reports unique count, min, median, max, average, and standard deviation, and can expose details or a `TreeMap`.
- `ValueAggregatorDescriptor` creates aggregation-id/value pairs from input key/value pairs and can be configured with `JobConf`. Its fields include `TYPE_SEPARATOR` and `ONE`.
- `ValueAggregatorBaseDescriptor` supplies built-in aggregation type constants, default record counting, `generateEntry(type,id,val)`, `generateValueAggregator(type)`, and input-file-aware configuration.
- `UserDefinedValueAggregatorDescriptor` dynamically instantiates a user descriptor by class name and delegates `generateKeyValPairs`.
- `ValueAggregatorJobBase` holds the protected `aggregatorDescriptorList` used by mapper, combiner, and reducer classes.
- `ValueAggregatorMapper` iterates descriptors and emits aggregation pairs. `ValueAggregatorCombiner` combines values for a typed aggregation key. `ValueAggregatorReducer` creates the correct aggregator from the key prefix and emits final reports.
- `ValueAggregatorJob` creates `JobConf` or `JobControl` instances and has a `main` entry point for aggregate jobs, including descriptor class setup.

### Pipes

- `Submitter` exposes static `getExecutable`/`setExecutable` for the application executable URI, boolean toggles for Java record reader, mapper, reducer, and writer use, `getKeepCommandFile`/`setKeepCommandFile`, `submitJob(JobConf)`, and `main(String[])`.
- Pipes package documentation defines the CLI options and integration model: a separate C++ process communicates with Java map/reduce components over sockets using Writable serialization, with optional C++ combiners and partition functions.

### Metrics

- `ContextFactory` is a singleton-style factory with attributes loaded from `hadoop-metrics.properties`. It supports attribute get/list/set/remove, synchronized context construction by name, and null-context creation.
- `MetricsContext` defines monitoring lifecycle, record creation, updater registration, and `DEFAULT_PERIOD`.
- `MetricsRecord` defines tags and metrics with `String`, `int`, `short`, `byte`, and `float` overloads, plus `update()` and `remove()` for buffered metric table rows.
- `MetricsUtil` wraps context and record creation and tags records with host identity. `Updater.doUpdates(MetricsContext)` is the periodic callback contract.
- `FileContext` emits metrics to a configured file or standard output, with `fileName` and `period` attributes. `GangliaContext` emits records to Ganglia using server and per-metric metadata attributes.
- `EventCounter` is a log4j appender counting fatal, error, warn, and info events. `JvmMetrics` is a singleton `Updater` for JVM metrics.
- `AbstractMetricsContext` implements context lifecycle, timer period, updater registration, record buffering, update/remove row semantics, `flush`, and abstract `emitRecord`.
- `MetricsRecordImpl` stores record state and delegates update/remove back to its `AbstractMetricsContext`. `MetricValue` distinguishes absolute and incremental numbers.
- `NullContext` discards all metrics. `NullContextWithUpdateThread` keeps callbacks active without emitting records, useful when another system such as JMX reads sampled values.
- `OutputRecord` provides read-only access to emitted tags and metrics. `metrics.spi.Util.parse` parses comma/space separated host and optional port specifications.
- `MBeanUtil` registers and unregisters MBeans using Hadoop's standard `hadoop.dfs:service=...,name=...` naming pattern.
- `MetricsIntValue`, `MetricsTimeVaryingInt`, and `MetricsTimeVaryingRate` are synchronized helper objects that push changed, interval-delta, and rate/min/max metrics to a `MetricsRecord`.

### Network

- `DNS` provides reverse lookup against a specified nameserver, IP enumeration for an interface, default IP selection, host lookup with default or explicit nameserver, and default host lookup.
- `DNSToSwitchMapping.resolve(List<String>)` maps host names or IP addresses to rack-like network paths while preserving input/output order. `ScriptBasedMapping` implements it through a configured `topology.script.file.name`.
- `NetUtils` selects socket factories from configuration keys, creates socket addresses from `host:port` or URI-like forms, migrates old host/port config pairs to combined addresses, tracks static hostname resolutions, converts wildcard server bind addresses to connectable addresses, and returns timeout-aware socket streams.
- `NetworkTopology` models a hierarchical cluster tree. It can add/remove/lookup nodes, count racks and leaves, compute distance, test same-rack membership, choose random nodes within or outside a scope, count available nodes excluding a list, and pseudo-sort replica arrays by distance to a reader.
- `Node` and `NodeBase` define and implement network location, node name, parent, level, path normalization, path construction, and constants for path separators and root.
- `SocketInputStream` and `SocketOutputStream` wrap selectable channels with read/write timeouts, expose the underlying channel for zero-copy transfer, implement `ReadableByteChannel`/`WritableByteChannel`, and synchronize close.
- `SocksSocketFactory` is configurable and creates sockets through a SOCKS proxy. `StandardSocketFactory` creates normal sockets while matching the socket-factory API.

### Record I/O

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` for `DataInput`/`DataOutput` or streams. Static `get(...)` methods return thread-local adapters for supplied data streams.
- `CsvRecordInput` and the visible part of `CsvRecordOutput` implement the same record input/output primitive methods for CSV streams.
- `Buffer` is a mutable, resizable byte sequence implementing `Comparable` and `Cloneable`. It exposes backing-array assignment, copying, append, count/capacity management, truncation, reset, lexicographic comparison, equality, hash code, string conversion with optional charset, and cloning.

## Control Flow

The XML does not contain executable method bodies, but the documented APIs imply several core paths.

In old MapReduce library jobs, `configure(JobConf)` initializes helpers, map methods consume key/value pairs through `OutputCollector` and `Reporter`, reduce methods iterate all values for a key, and output formats return record writers that translate collected key/value pairs into target files. `MultipleOutputFormat` inserts an extra dispatch layer: the composite writer derives a leaf name, output path, actual key, and actual value before delegating to a base writer.

Field-selection flow treats input as separator-delimited fields. The mapper builds fields from value only for text input, or from key plus value for other formats, then applies configured key/value field specs. The reducer repeats the same extraction style with the reduce key always included.

Aggregate flow is data driven. A mapper calls each configured `ValueAggregatorDescriptor.generateKeyValPairs`, emits keys with an aggregation-type prefix, then the combiner or reducer parses the prefix, constructs the matching `ValueAggregator`, calls `addNextValue` over all values, and emits either `getCombinerOutput` or `getReport`. Associativity and commutativity are required when combiners are used.

Pipes submission flow mutates a `JobConf` with the executable and Java/native component flags before submitting a job. At task runtime, Java map/reduce components communicate with an external C++ process over sockets using Writable serialization.

Metrics flow starts with `ContextFactory.getFactory()`, optional attribute inspection or mutation, `getContext(name)`, and `createRecord(recordName)`. Callers set tags and metrics on a `MetricsRecord`, call `update()` or `remove()`, and the context buffers rows until its monitoring timer invokes updaters and emits output records. Concrete contexts provide `emitRecord`; file and Ganglia contexts write to their respective sinks, while null contexts intentionally discard output.

Network flow includes configuration-driven socket factory selection, socket address creation, optional static hostname overrides, and stream wrapping through `NetUtils.getInputStream`/`getOutputStream`. If a socket has a channel, the returned stream uses non-blocking mode plus timeout handling; after that, direct use of `Socket.getInputStream()` or `getOutputStream()` can fail because the channel has been switched to non-blocking mode.

Topology flow maps hosts to rack paths, normalizes paths through `NodeBase`, adds leaf nodes into `NetworkTopology`, and uses distance/scope calculations for rack-aware placement. `pseudoSortByDistance` only moves local and same-rack candidates to the front and leaves the rest of the array largely untouched.

Record I/O flow follows `RecordInput`/`RecordOutput` callbacks: start/end record, vector, and map, with primitive reads and writes in between. Binary adapters work over `DataInput`/`DataOutput`; CSV adapters use streams. `Buffer` supports efficient in-memory mutation before serialization.

## State and Persistence Behavior

This JDiff file persists the Hadoop 0.17.0 public API for compatibility comparison. It does not store runtime data, but it documents classes whose runtime state is significant.

MapReduce helpers are mostly stateless per call, except for configuration-derived state such as field specs, regex patterns, aggregate descriptor lists, multithreaded runner settings, and multiple-output writer caches. Output formats and writers persist data to Hadoop filesystems; `NullOutputFormat` intentionally discards it.

Aggregate state lives inside `ValueAggregator` instances during each key group: sums, extrema, unique sets, histograms, and combiner output buffers. `UniqValueCount` and `ValueHistogram` can retain large in-memory sets/maps, making their state proportional to input cardinality. Descriptor configuration can persist an input file name and user class names in `JobConf`.

Pipes state is encoded in `JobConf`, including executable URI and Java/native component flags. The keep-command-file flag persists debug command data as `downlink.data` in task directories when enabled.

Metrics state is buffered in `AbstractMetricsContext` until periodic emission. `ContextFactory` has process-global attributes and context instances; `hadoop-metrics.properties` provides classpath-loaded configuration. `MetricsIntValue` tracks whether a set value has already been pushed, while time-varying helpers retain current and previous interval values. `FileContext` persists metrics by appending to a file when configured; `GangliaContext` sends UDP/network metrics; `NullContext` discards all metric records.

Network state includes process-local static hostname resolutions in `NetUtils`, configuration-backed socket factory selections, rack topology trees in `NetworkTopology`, parent/level/location fields in `NodeBase`, and proxy configuration in `SocksSocketFactory`. Socket streams mutate channel blocking mode and hold timeout settings until closed.

Record I/O state includes thread-local binary input/output adapters, current stream positions in underlying `DataInput`/`DataOutput`, and mutable byte arrays in `Buffer`. `Buffer.set(byte[])` uses the supplied array as backing storage, while `copy(byte[], int, int)` creates its own backing storage. Count and capacity are distinct, so callers must respect `getCount()`.

## Dependencies and Integration Points

This chunk depends on the old `org.apache.hadoop.mapred` API: `Mapper`, `Reducer`, `MapRunnable`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`, `FileOutputFormat`, `RecordWriter`, `OutputFormat`, `RunningJob`, and `jobcontrol.JobControl`.

Filesystem and serialization dependencies include `FileSystem`, `Progressable`, `Writable`, `WritableComparable`, `LongWritable`, `Text`, `SequenceFileOutputFormat`, `TextOutputFormat`, Java `InputStream`/`OutputStream`, `DataInput`/`DataOutput`, byte arrays, `ArrayList`, `TreeMap`, and iterators.

Configuration integration is central. Aggregate descriptors, Pipes submitter settings, socket factory classes, topology script mapping, metrics context classes, metrics periods, file output paths, Ganglia servers, and proxy sockets are all selected or shaped by `JobConf`, `Configuration`, or metrics factory attributes.

Metrics integrations include log4j (`AppenderSkeleton`, `LoggingEvent`) for `EventCounter`, JMX (`ObjectName`) for `MBeanUtil`, Ganglia wire emission, file/stdout emission, and periodic callbacks through `Updater`.

Network integrations include Java DNS/JNDI (`NamingException`), `InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, NIO selectable channels, byte buffers, Hadoop IPC `Server`, and Hadoop `VersionedProtocol`-oriented socket factory lookup.

Record integrations include `RecordInput`, `RecordOutput`, `Record`, `Index`, and the generated-record runtime conventions used by Hadoop's old record compiler.

## Risks and Edge Cases

- This chunk starts and ends mid-class. Full research for `WrappedRecordReader` and `CsvRecordOutput` requires adjacent chunks.
- JDiff metadata omits method bodies, so exact parsing, validation, synchronization internals, and serialization byte formats require implementation-source review.
- `HashPartitioner` and `KeyFieldBasedPartitioner` depend on hash stability and positive modulo behavior. Negative hash values and zero reducers are important failure edges.
- Field-selection specs include specific fields, ranges, and open ranges, but open ranges only apply to value fields. Off-by-one field indexing and separator escaping can break output compatibility.
- `MultipleOutputFormat` can create many writers if filenames are key-dependent. Writer lifecycle, path sanitization, and close-on-failure behavior are high-risk.
- Multithreaded map execution can expose mapper implementations that are not thread safe. Shared collector/reporter use and exception propagation need explicit tests.
- Aggregate keys encode type and id in a single `Text` key. Missing separators, unknown type names, descriptor bugs, or ids containing the separator can misroute values.
- Combiner correctness depends on associative and commutative aggregators. Unique counts and histograms can consume unbounded memory without configured limits.
- Dynamic descriptor loading in `UserDefinedValueAggregatorDescriptor` can fail due to classpath, constructor, type, or access problems.
- Pipes jobs mix Java and native code over sockets. Writable serialization mismatches, executable URI errors, command-file leakage, and C++ combiner ordering by `memcmp` instead of Java comparators are compatibility risks.
- Metrics API defaults differ between docs in this span: `ContextFactory.getContext` says missing context classes create `NullContext`, while package docs describe `FileContext` as default. This mismatch should be reconciled against implementation and tests.
- Metrics records are buffered, so callers expecting immediate emission after `update()` can observe delayed output. Tags define row identity, and `remove()` semantics can remove broad sets when few tags are set.
- `ContextFactory` and `AbstractMetricsContext` have synchronized lifecycle methods but can interact with updater callbacks and emitters; deadlocks or missed updates are possible if emitters call back into context state.
- File metrics append to local paths and flush periodically. File permission, disk full, restart, and stop/close behavior need coverage.
- Ganglia emission depends on server parsing and UDP/network availability; malformed per-metric attributes can silently weaken reporting.
- `EventCounter` is static-counter-like API surface; tests must verify level mapping and reset behavior if any exists outside this chunk.
- DNS APIs depend on host network interfaces and external nameservers. Tests should isolate default interface, missing interface, reverse lookup failure, and default nameserver behavior.
- `NetUtils.createSocketAddr` accepts both `host:port` and URI-like forms; malformed ports, IPv6 literals, missing ports, and wildcard bind addresses are sensitive cases.
- Static host resolution is process-global and test-oriented. Tests must clean up or isolate it to avoid cross-test contamination.
- `SocketInputStream` and `SocketOutputStream` require selectable channels and non-negative timeouts. They mutate channel blocking mode, so mixed direct socket stream use can throw `IllegalBlockingModeException`.
- `NetworkTopology.add` requires leaf nodes and rejects adding under leaves. Distance and same-rack calculations must handle null nodes and nodes outside the topology.
- Scope strings beginning with `~` invert selection in topology APIs. Empty scopes, unresolved/default racks, and excluded-node overlap are high-risk placement paths.
- `NodeBase.normalize` and path construction must preserve root and separator behavior. Bad normalization breaks rack identity and topology lookup.
- `ScriptBasedMapping` relies on an external script. Missing script, timeout, partial output, and output order mismatch can cause wrong rack assignments.
- `SocksSocketFactory.equals`/`hashCode` must reflect proxy configuration; otherwise RPC connection caching can reuse the wrong socket factory.
- `StandardSocketFactory` documentation says SOCKS proxy even though the class is standard. This apparent Javadoc copy/paste error is a documentation compatibility signal.
- Binary record input/output thread-local adapters must be safe when reused with different `DataInput`/`DataOutput` instances on the same thread.
- `Buffer.get()` exposes backing storage; callers must not read past `getCount()` or mutate unexpectedly. `set(byte[])` aliases caller storage while `copy` does not.
- `Buffer.setCapacity` shrinking below count, append growth, lexicographic comparison of signed bytes, charset conversion, and clone independence need focused coverage.
- CSV record output is incomplete in this chunk, so final API review must merge continuation lines before claiming complete CSV output behavior.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that confirm every public/protected package, class, interface, field, constructor, method, exception, visibility flag, synchronized/static/final/abstract marker, and deprecation marker in lines 31139-37383.
- Join framework tests for sorted input joins, `WrappedRecordReader` head-key comparison, equality/hash behavior, close forwarding, configured key comparator, nested join expressions, and custom `mapred.join.define.<ident>` operations.
- `FieldSelectionMapReduce` tests for text versus non-text input field construction, custom separators, simple/range/open-range specs, map and reduce specs, empty fields, invalid specs, and field ordering.
- Mapper/reducer/partitioner tests for identity, inverse, long sum, regex extraction, token counting, hash partitioning with negative hashes, and key-field partitioning configuration.
- `MultipleOutputFormat` tests for generated leaf names, key/value-derived filenames, input-file-derived filenames, actual key/value rewrites, multiple writer creation, close propagation, and sequence/text concrete formats.
- `MultithreadedMapRunner` tests with thread-safe and non-thread-safe mappers, exception propagation, reporter progress, and configurable thread count.
- `NullOutputFormat` tests that output is accepted and no files are written.
- Aggregate framework tests for every built-in aggregator, object and primitive add paths, reset, report formatting, combiner output round trips, unique-count limits, histogram detail output, unknown aggregation type, and key ids containing separators.
- Aggregate job tests for descriptor configuration, user descriptor dynamic loading failures, mapper descriptor iteration, combiner/reducer type parsing, default record counting, input-file counting, and `ValueAggregatorJob` argument parsing.
- Pipes submitter tests for all Java/native component flags, executable URI configuration, keep-command-file behavior, `submitJob` JobConf mutations, CLI parsing, and mixed Java/C++ component combinations.
- Metrics factory tests for `hadoop-metrics.properties` loading, attribute mutation/removal, context class selection, null-context fallback, and singleton behavior.
- Metrics record tests for all tag and metric overloads, absolute versus incremental values, `update()` row merge, `remove()` row matching, callback registration/removal, timer period changes, close/stop/start lifecycle, and exception handling.
- File and Ganglia context tests for configured periods, file append/stdout output, flush, stop/close, server-list parsing, malformed server specs, and per-metric metadata attributes.
- JVM metrics and log event counter tests for singleton initialization, periodic update output, and log level counters.
- Metrics utility tests for MBean name construction/unregistration and synchronized helper metrics pushing exactly once or per interval as documented.
- DNS and network utility tests for interface lookup, explicit/default nameserver behavior, static resolution add/get/list, socket address parsing, legacy host/port config migration, wildcard listener connect address, socket factory lookup and fallback, malformed factory properties, and SOCKS proxy configuration.
- Socket stream tests for read/write timeout, zero timeout, negative timeout rejection, close synchronization, channel exposure, NIO `ByteBuffer` read/write, and illegal blocking mode behavior after wrapping.
- Network topology tests for add/remove/contains/getNode, rack and leaf counts, distance, same-rack checks, random selection in normal and inverted scopes, excluded-node counts, unresolved/default rack paths, and pseudo distance sorting.
- `NodeBase` tests for constructors, `normalize`, `getPath`, parent/level setters, root path handling, path separator constants, and string rendering.
- `ScriptBasedMapping` tests with successful script output, missing script, wrong output count, null/empty name lists, and configuration replacement.
- Record I/O tests for binary primitive read/write round trips, record/vector/map boundaries, thread-local adapter reuse, CSV primitive parsing/writing, invalid input, and `IOException` propagation.
- `Buffer` tests for aliasing versus copying, count/capacity behavior, append growth, truncate/reset, lexicographic compare, equality/hash, string conversion with unsupported charset, clone independence, and reading only valid bytes between zero and `getCount() - 1`.

### subset-b-007264: lines 37384-43272

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 37384-43272

## Scope

This chunk is the tail of the Hadoop 0.17.0 JDiff API XML. It begins inside the already-open `org.apache.hadoop.record.CsvRecordOutput` class, covers the rest of `org.apache.hadoop.record`, the record compiler and generated parser packages, record type metadata, early security user/group APIs, the `Logalyzer` tool, most of the common utility package, and ends with `VersionInfo`, `XMLUtils`, the package summary for `org.apache.hadoop.util`, and the closing `</api>`.

Because the source is JDiff XML, this document describes the exported API contract rather than method bodies. Control-flow and state notes are inferred from signatures, inheritance, exceptions, fields, and Javadocs embedded in this chunk.

## Purpose

The chunk documents several foundational Hadoop Common surfaces from the 0.17.0 release:

- Hadoop Record I/O runtime APIs for generated records, record input/output encodings, raw comparators, XML serialization, and binary/variable-length utilities.
- Hadoop Record I/O compiler APIs, including the DDL model classes, Ant integration, JavaCC-generated parser, lexer, token stream, and parse/lexical error types.
- Record type metadata APIs that describe primitive, vector, map, and struct field types and can serialize `RecordTypeInfo`.
- User/group identity APIs for Unix-style users, groups, login, thread-local current UGI, and configuration persistence.
- Operational tools and utilities: log archiving/analyzing, recursive distributed copy, daemon threads, disk checks, generic command-line parsing, native library loading, shell execution, sorting helpers, progress reporting, reflection helpers, jar running, servlet helpers, string utilities, tool execution, build/version metadata, and XML transformation.

The APIs are cross-cutting infrastructure rather than one runtime subsystem. They support Hadoop serialization, command-line tools, MapReduce utilities, daemon diagnostics, filesystem/process interaction, and legacy security identity propagation.

## Important APIs, Types, and Functions

`org.apache.hadoop.record.Index` is a two-method iterator interface for deserializing vectors and maps. `done()` reports whether all elements have been consumed, and `incr()` advances to the next element. The Javadoc shows the expected loop shape: call `startVector()` or `startMap()`, process until `done()`, and call `incr()` after each element.

`org.apache.hadoop.record.Record` is the abstract base class for generated records. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput, String)`, tagged `deserialize(RecordInput, String)`, and `compareTo(Object)`, and provides untagged overloads plus Hadoop `Writable` adapters `write(DataOutput)` and `readFields(DataInput)`. `toString()` is exported, implying generated records can render through the record output layer.

`RecordComparator` extends `WritableComparator` for optimized raw byte comparisons of generated `Record` implementations. Subclasses implement raw `compare(byte[], int, int, byte[], int, int)`. The static synchronized `define(Class, RecordComparator)` registers a raw comparator for a record class.

`RecordInput` and `RecordOutput` define the core record serialization contract. Inputs read primitive and composite values by tag: `readByte`, `readBool`, `readInt`, `readLong`, `readFloat`, `readDouble`, `readString`, `readBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Outputs provide the symmetric methods `writeByte`, `writeBool`, `writeInt`, `writeLong`, `writeFloat`, `writeDouble`, `writeString`, `writeBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Tags are primarily for tagged encodings such as XML.

`org.apache.hadoop.record.Utils` provides record runtime helpers: float/double parsing from byte arrays, variable-length integer and long reads from byte arrays or streams, `getVIntSize(long)`, variable-length integer and long writes to `DataOutput`, and byte-array lexicographic comparison. The public `hexchars` field supports hex-oriented encoding.

`XmlRecordInput` and `XmlRecordOutput` implement `RecordInput` and `RecordOutput` over `InputStream`/`OutputStream`, exposing the same primitive/composite read/write methods. These are the XML serializer and deserializer for the record runtime.

The `org.apache.hadoop.record` package-level documentation is unusually substantive. It defines Record I/O as a language-neutral DDL and translator for generating serialization/deserialization code. It documents primitive types (`byte`, `boolean`, `int`, `long`, `float`, `double`, `ustring`, `buffer`), composite types (`record`, `vector`, `map`), DDL syntax with `include`, `module`, and `class`, `rcc` invocation with `-l/--language`, Java and C++ type mappings, and binary/CSV/XML encodings.

`org.apache.hadoop.record.compiler.CodeBuffer` wraps a `StringBuffer` with automatic indentation and exposes `toString()`. `Consts` exports string constants used by generated compiler output: `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.

The DDL model classes are `JType` plus concrete primitive/composite subclasses: `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField<T>` wraps a field name and type. `JFile` represents a DDL compilation unit with a filename, included `JFile`s, and records, and exposes `genCode(String language, String destDir, ArrayList<String> options)`.

`org.apache.hadoop.record.compiler.ant.RccTask` is the Ant integration for the record compiler. It has setters for output language, single input file, fail-on-error behavior, destination directory, and nested `FileSet`s, and `execute()` invokes the compiler. Its Javadoc says default language is Java, default destination is `.`, and `failonerror` defaults to true.

The `org.apache.hadoop.record.compiler.generated` package is JavaCC-generated parser infrastructure. `ParseException` carries `currentToken`, `expectedTokenSequences`, `tokenImage`, and `specialConstructor`, and can produce a parse error message through `getMessage()`. `Rcc` implements `RccConstants` and exposes `main`, `usage`, `driver`, grammar productions (`Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, `Vector`), parser reinitialization overloads, token access, parse exception generation, and tracing toggles. `RccConstants` defines token ids for EOF, module/record/include keywords, primitive types, vector/map, braces, angle brackets, semicolon, comma, dot, string literal, identifier, lexical states, and `tokenImage`.

`RccTokenManager` is the generated lexer with debug stream support, `ReInit`, lexical-state switching, token creation, and `getNextToken()`. `SimpleCharStream` is the generated character stream for ASCII input, with constructors over `Reader` and `InputStream` plus optional encoding, line/column tracking, buffer expansion/fill, token start, character reading, backup, reinitialization, image/suffix extraction, cleanup, and begin-line/column adjustment. `Token` exposes token kind, begin/end position, image, next token, special-token chain, and `newToken(int)`. `TokenMgrError` represents lexer errors and provides escaping, lexical-error message creation, and `getMessage()`.

The record metadata package describes runtime type information. `FieldTypeInfo` pairs a field id/name with a `TypeID` and implements equality/hash behavior. `TypeID` represents primitive types with shared constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`; `TypeID.RIOType` contains byte constants for supported IDL types. `VectorTypeID`, `MapTypeID`, and `StructTypeID` describe composite element/key/value/struct metadata. `RecordTypeInfo` extends `Record`, stores a record name and a collection of `FieldTypeInfo`, supports adding fields, looking up one-level nested struct type info, and serializing/deserializing the metadata. `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` skips data in a record stream based on type metadata.

`UnixUserGroupInformation` extends abstract `UserGroupInformation`. It has constructors from user/group names, `createImmutable(String[])`, user and group getters, `Writable` serialization/deserialization, `saveToConf(Configuration, String, UnixUserGroupInformation)`, `readFromConf(Configuration, String)`, and login overloads from Unix or configuration. Public `UGI_PROPERTY_NAME` identifies the default property name. Equality and hash code are user/group identity oriented, with hash code based on username.

`UserGroupInformation` is the abstract base for identity state. It implements `Writable`, exposes static `getCurrentUGI()` and `setCurrentUGI(UserGroupInformation)` for current-thread identity, abstract user/group getters, static `login(Configuration)`, static `readFrom(Configuration)`, and public logging field `LOG`.

`org.apache.hadoop.tools.Logalyzer` is a utility for archiving and analyzing Hadoop logs. `doArchive(String logListURI, String archiveDirectory)` archives logs listed by a URI. `doAnalyze(String inputFilesDirectory, String outputDirectory, String grepPattern, String sortColumns, String columnSeparator)` runs grep/sort analysis. `LogComparator` extends `Text.Comparator` and implements `Configurable` for optimized raw log-key sorting. `LogRegexMapper` extends `MapReduceBase` and implements `Mapper<K, Text, Text, LongWritable>` to emit matches for a configured regular expression.

`CopyFiles` implements `Tool` and provides recursive MapReduce-based copying between filesystems. It exposes configuration setters/getters, a static `copy(Configuration, String srcPath, String destPath, Path logPath, boolean srcAsList, boolean ignoreReadFailures)`, `run(String[])`, and `main(String[])`. `CopyFiles.DuplicationException` is an `IOException` subtype with public `ERROR_CODE`.

`Daemon` is a `Thread` subclass whose constructors mark the thread as daemon; it can wrap a `Runnable` and exposes `getRunnable()`.

`DiskChecker` provides `mkdirsWithExistsCheck(File)` and `checkDir(File)`, with `DiskErrorException` and `DiskOutOfSpaceException` as `IOException` subtypes. The mkdir helper explicitly tolerates races where another process creates a parent directory between existence check and mkdir.

`GenericOptionsParser` parses Hadoop-generic command-line options into a `Configuration`, optionally alongside caller-supplied Commons CLI `Options`. It exposes remaining application args, the parsed `CommandLine`, and static generic usage output. The documented generic options are `-conf`, `-D`, `-fs`, and `-jt`.

`GenericsUtil` exposes `getClass(T)`, `toArray(Class<T>, List<T>)`, and `toArray(List<T>)`. The no-class overload requires a non-empty list and can throw `ArrayIndexOutOfBoundsException` on an empty list.

`HostsFileReader` reads include and exclude host files through a constructor taking two path strings, `refresh()`, `getHosts()`, and `getExcludedHosts()`.

`IndexedSortable` and `IndexedSorter` define index-addressed sorting. Sortable collections expose `compare(int, int)` and `swap(int, int)`. Sorters expose `sort(IndexedSortable, int l, int r)` over `[l, r)`. `QuickSort` implements `IndexedSorter` with `sort` overloads, including one that accepts a `Progressable`. `MergeSort` exposes `mergeSort(int[] src, int[] dest, int low, int high)` over integer index arrays and is constructed with a comparator over `IntWritable`.

`NativeCodeLoader` exposes `isNativeCodeLoaded()` and job-level native-library controls `getLoadNativeLibraries(JobConf)` and `setLoadNativeLibraries(JobConf, boolean)`. `PlatformName` reports the JVM platform string. `PrintJarMainClass` prints a jar's main class. `RunJar` can `unJar(File, File)` and run a Hadoop job jar from `main(String[])`.

`PriorityQueue` is an abstract heap-like queue. Subclasses define `lessThan(Object, Object)` and call `initialize(int maxSize)`. The API includes `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

`ProgramDriver` registers and dispatches named programs with `addClass(String name, Class mainClass, String description)` and `driver(String[] args)`.

`Progress` models hierarchical progress. It supports adding named/unnamed phases, advancing to the next phase, returning the current phase, completing a node, setting leaf progress, computing overall root progress, setting status text, and `toString()`. `Progressable` is the single-method callback interface `progress()`.

`ReflectionUtils` provides configuration injection and reflective construction through `setConf(Object, Configuration)` and `newInstance(Class, Configuration)`, plus thread diagnostics and contention tracing via `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, and `logThreadInfo(Log, String, long)`.

`ServletUtil` provides simple servlet/JSP helpers: `initHTML(ServletResponse, String)`, `getParameter(ServletRequest, String)` returning null for all-whitespace values, `htmlFooter()`, and public `HTML_TAIL`.

`Shell` is an abstract base for executing platform commands with an optional minimum re-execution interval. It exposes helpers for Unix groups, permission, and ulimit commands; protected environment and working-directory setters; protected `run()`; abstract `getExecString()` and `parseExecResult(BufferedReader)`; process and exit-code getters; static `execCommand(String[])`; command constants; and `WINDOWS`. `Shell.ExitCodeException` is an `IOException` with an exit code. `Shell.ShellCommandExecutor` stores small command output as-is and supports command/working-directory/environment constructors plus `execute()`, `getOutput()`, and inherited execution hooks.

`StringUtils` provides exception stringification, hostname shortening, human-readable integer formatting using `k/m/g`, percentage formatting, comma-separated array formatting, hex conversion, URI/path string conversion, elapsed-time formatting, comma-separated string parsing, escaped splitting, escaping/unescaping of separators, hostname retrieval without propagating exceptions, and startup/shutdown log messages. Public constants are `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`.

`Tool` is the standard Hadoop command interface. It extends `Configurable` and defines `run(String[] args)`. `ToolRunner` runs a `Tool` with generic option parsing, sets the tool configuration, delegates remaining args, and can print generic usage.

`VersionInfo` exposes static build metadata getters for Hadoop version, Subversion revision, build date, build user, and source URL, plus `main(String[])`. `XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` runs an XML transform and surfaces `TransformerConfigurationException` and `TransformerException`.

## Control Flow

Record I/O control flow starts with generated record classes extending `Record`. A caller writes a record through `Record.write(DataOutput)` or `serialize(RecordOutput, tag)`. The generated implementation calls `RecordOutput.startRecord`, writes each field with the correct primitive/composite method, iterates vectors/maps, and closes the record. Reads reverse the sequence through `RecordInput.startRecord`, primitive reads, `startVector`/`startMap` returning an `Index`, repeated `done()`/`incr()` iteration, and `end*` calls. Untagged `serialize`/`deserialize` are convenience adapters over tagged methods; `Writable` methods adapt records to Hadoop's `DataInput`/`DataOutput` ecosystem.

The record compiler flow is DDL text to generated code. `Rcc.main()` or `Rcc.driver()` parses arguments, the JavaCC parser walks grammar productions from `Input()` through includes, module names, records, fields, and nested type productions. It creates `JFile`, `JRecord`, `JField`, and `JType` model objects. `JFile.genCode()` then dispatches to a lower-level language generator for Java or C++ output. `RccTask.execute()` wraps this flow for Ant by gathering a single file and/or filesets, applying language/destination/fail-on-error options, and invoking the compiler for each record definition.

The parser/lexer flow is JavaCC-standard. `SimpleCharStream` buffers characters and tracks token positions. `RccTokenManager` reads the stream, applies lexical states including comment states, and returns `Token` objects. `Rcc` consumes tokens through grammar methods, throws `ParseException` on grammar mismatch, and exposes `generateParseException()` for detailed expected-token errors. Lexical failures are represented by `TokenMgrError`.

Record metadata flow uses `TypeID` instances to describe fields independent of generated Java classes. Callers build a `RecordTypeInfo`, set its name, add fields with `addField(fieldName, TypeID)`, and serialize it through the normal `Record` path. During deserialization, a `RecordTypeInfo` can reconstruct metadata from a `RecordInput`. `meta.Utils.skip()` uses the type id to consume and discard a matching value from an input stream.

UGI control flow has both configuration-backed and OS-backed paths. `UnixUserGroupInformation.login()` reads the current Unix username and groups, while `login(Configuration, boolean)` first tries configured identity and falls back to Unix lookup. `readFromConf()` loads comma-separated user/group identity from a configuration property and can reuse an existing per-user UGI cache according to the Javadoc. `saveToConf()` writes the comma-separated identity back to configuration. `UserGroupInformation.setCurrentUGI()` and `getCurrentUGI()` provide current-thread identity propagation.

`Logalyzer` has two high-level flows. Archiving reads a URI that serves log-file URIs and copies those logs into an archive directory. Analysis configures a MapReduce job around regex extraction and sorted output: `LogRegexMapper` reads text lines, emits matching text with counts, and `LogComparator` sorts raw UTF8 keys according to configured columns/separators.

`CopyFiles.run()` is the command driver for recursive distributed copy. Its Javadoc describes listing the source recursively, distributing copy work across map input files in round-robin fashion, copying in mappers, and using no reducer. The static `copy()` entry point exposes this workflow directly for callers that already have a configuration and copy flags.

`GenericOptionsParser` and `ToolRunner` define the legacy Hadoop CLI flow. Generic options mutate the configuration and are removed from the application argument list. `ToolRunner.run(conf, tool, args)` parses those options, sets the resulting configuration on the tool, and invokes `tool.run()` with only the remaining command-specific arguments. `ToolRunner.run(tool, args)` delegates using the tool's existing configuration.

Sorting flow is decoupled from storage. `QuickSort` and any `IndexedSorter` implementation call only `IndexedSortable.compare(i, j)` and `swap(i, j)` for indices in `[l, r)`. This lets sort algorithms operate over arrays, buffers, or other structures without owning the data.

`Progress` flow is tree-shaped. Applications build phases with `addPhase()`, enter work through `phase()`/`startNextPhase()`, report leaf progress with `set(float)`, complete nodes with `complete()`, and query aggregate root progress with `get()`. `QuickSort` can receive a `Progressable` callback to report activity during long sorts.

`Shell` flow checks the configured minimum interval, prepares environment and working directory, runs `getExecString()` through a subprocess, lets `parseExecResult()` consume stdout, records the process and exit code, and throws `ExitCodeException` on non-zero exit. `ShellCommandExecutor` implements the abstract hooks by returning a fixed command and collecting output into an internal string.

`RunJar` flow unpacks a job jar into a directory, discovers or accepts the main class, constructs an execution environment, and invokes the jar's main entry point. `PrintJarMainClass` is the smaller manifest-inspection utility.

## State and Persistence Behavior

The XML file itself is generated API metadata and does not persist runtime state. The APIs described here, however, expose several stateful contracts.

Generated `Record` classes are stateful data containers. Their persistent form is controlled by `RecordOutput`/`RecordInput` implementations and Hadoop `Writable` adapters. Binary encoding persists vector/map lengths, zero-compressed integers/longs, UTF-8 strings with lengths, raw buffers with lengths, and network-order floating-point values. CSV and XML encodings persist additional delimiters/tags and escaping.

`RecordComparator.define()` mutates global comparator registration state for a record class. This state affects subsequent raw comparisons by Hadoop sorting/shuffle code that consults `WritableComparator` registrations.

The record compiler model (`JFile`, `JRecord`, `JField`, `JType`) is in-memory compilation state. `genCode()` persists generated Java/C++ source files under the destination directory. `RccTask` persists nothing itself but writes generated source files as an Ant build side effect.

JavaCC parser state is mutable: `Rcc` stores `token_source`, current `token`, and `jj_nt`; `SimpleCharStream` stores buffer positions, line/column arrays, previous newline flags, input reader, and tab size; tokens carry linked-list references for regular and special tokens. Reuse is supported through `ReInit()` methods rather than constructing new parser objects.

`RecordTypeInfo` persists metadata as a record. It stores record name and fields, serializes/deserializes through normal record streams, and provides nested-struct lookup limited to one nesting level. `TypeID` primitive constants are shared singleton-like public objects; composite `TypeID` objects carry references to element/key/value/record metadata.

`UnixUserGroupInformation` persists identity in two forms: Hadoop `Writable` binary/string-format serialization and comma-separated configuration properties. The configuration format starts with username followed by default group and other groups. The API also implies a per-user UGI cache, so repeated login/read operations can return an existing object.

`UserGroupInformation` keeps current identity per thread. That state is process-local and can affect downstream filesystem, RPC, or job behavior that queries the current UGI.

`HostsFileReader` maintains in-memory include and exclude host sets loaded from files. `refresh()` reloads them, and getters expose the current sets.

`NativeCodeLoader` exposes process-level native-code load state through `isNativeCodeLoaded()` and job-level configuration state through `getLoadNativeLibraries()`/`setLoadNativeLibraries()`.

`PriorityQueue`, `Progress`, and `Shell` are stateful utility objects. `PriorityQueue` stores heap contents and max size. `Progress` stores a phase tree, current phase, per-node progress, and status text. `Shell` stores command interval, process, exit code, environment, and working directory; `ShellCommandExecutor` additionally stores captured output.

`StringUtils` and most simple utility classes are stateless, but methods such as `startupShutdownMessage()` write to logs, `getHostname()` observes host environment, and URI/path conversion allocates domain objects. `VersionInfo` observes build metadata embedded in the artifact. `XMLUtils.transform()` streams transformed output to a caller-provided `Writer`.

## Dependencies and Integration Points

Record I/O integrates with `org.apache.hadoop.io.WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, `RecordInput`, `RecordOutput`, `Buffer`, Java collections (`ArrayList`, `TreeMap`), and Java I/O streams. The design docs explicitly connect generated Java and C++ code to binary, CSV, and XML encodings.

The record compiler integrates with JavaCC-generated parser classes, Ant (`Task`, `FileSet`, `BuildException`), filesystem paths for source/destination files, and lower-level language generators referenced in package documentation (`CppGenerator` and `JavaGenerator`). Generated Java code maps DDL modules to packages and DDL records to `.java` classes; generated C++ maps modules to namespaces and DDL files to `.cc/.hh` pairs.

Record metadata integrates back into the record runtime: `RecordTypeInfo` is itself a `Record`, `meta.Utils.skip()` consumes a `RecordInput`, and `TypeID` constants mirror the Record I/O DDL type system.

Security APIs integrate with `Configuration`, `Writable`, `Shell`-style Unix group/user discovery, `javax.security.auth.login.LoginException`, and logging. The configuration-persistence methods make UGI data available to clients/jobs without requiring every component to re-run OS login.

`Logalyzer` integrates with the old `org.apache.hadoop.mapred` API (`Mapper`, `MapReduceBase`, `JobConf`, `OutputCollector`, `Reporter`), Hadoop IO types (`Text`, `LongWritable`, `WritableComparable`), raw comparators, and DFS/local files used for archived logs and analysis output.

`CopyFiles` integrates with `Tool`, `Configuration`, `Path`, MapReduce execution, recursive filesystem listing, map input splitting, and job log paths. It is an early precursor to distributed copy behavior.

Common utilities integrate broadly: `GenericOptionsParser` uses Apache Commons CLI; `ToolRunner` depends on `Tool` and `Configuration`; `NativeCodeLoader` and `Shell` integrate with OS/platform capabilities; `ReflectionUtils` integrates with `Configurable` objects and logging; `ServletUtil` integrates with `javax.servlet`; `XMLUtils` integrates with `javax.xml.transform`; `RunJar` and `PrintJarMainClass` integrate with jar manifests and dynamic application launch.

## Risks and Edge Cases

This chunk starts in the middle of `CsvRecordOutput`, so the final per-file reconciliation should combine it with the prior chunk for the full CSV output API. Likewise, many compiler superclass details such as `JCompType` and generator internals are referenced but not declared here.

Record I/O compatibility is sensitive to field order, type signatures, container lengths, tag handling, and encoding choice. The package documentation says optional fields/backward-forward compatibility were planned but not described in this version, so generated records in 0.17.0 should be treated as schema-order-sensitive.

`RecordInput` vector/map iteration relies on callers correctly pairing `start*`, `Index.done()/incr()`, element reads, and `end*`. Off-by-one loops or missing `incr()` can desynchronize the stream. Tagged formats can also fail if generated field tags do not match expected XML names.

Variable-length integer encoding must preserve sign and boundary cases. The documented compact range for integers/longs and multi-byte length marker creates risk around values near `-120`, `127`, max/min int, and max/min long.

CSV and XML encodings include escaping rules for nulls, line feeds, percent signs, commas, control characters, and binary buffers. Incorrect escaping can produce data loss, invalid XML, or records that are readable in one implementation but not another.

`RecordComparator` raw comparators must match object-level `compareTo()` semantics. Divergence can break MapReduce sorting/grouping because raw bytes may be used without object deserialization.

The record compiler parser is generated and exposes mutable public fields. Reusing parser/token-manager instances without `ReInit()` or across threads is risky. `TokenMgrError` extends `Error`, so lexical failures may bypass normal checked-exception handling.

`RecordTypeInfo.compareTo()` is documented as not meaningful for normal ordering. Code should not use it for sorted collections despite the class extending `Record` and therefore inheriting `WritableComparable` expectations.

UGI identity is weak by modern security standards: it stores user/group names, reads from Unix/configuration, and serializes comma-separated strings. Malformed configuration raises `LoginException`, and trusting configuration-sourced users can be unsafe unless the caller controls that configuration. Thread-local current UGI can also leak identity across reused threads if not reset.

`Shell` and `NativeCodeLoader` are platform-dependent. `getUlimitMemoryCommand()` may return null on Windows/Cygwin or when unspecified. Shell command output is expected to be small in `ShellCommandExecutor`; using it for large outputs risks memory pressure. Environment/working-directory mutation affects subprocess behavior and must be tested separately on supported platforms.

`DiskChecker.mkdirsWithExistsCheck()` is designed for races but still depends on filesystem permissions and eventual directory writability. `checkDir()` can surface disk errors through custom exceptions.

`GenericOptionsParser` mutates the provided `Configuration`. Applications that parse generic options too late or reuse a configuration across tests can observe surprising defaults for `fs.default.name`, `mapred.job.tracker`, or custom `-D` values.

`GenericsUtil.toArray(List<T>)` is unsafe for empty lists per its own Javadoc. Prefer the overload taking `Class<T>` when the list may be empty.

`PriorityQueue.insert()` is bounded by initialized max size, and subclasses define ordering through `lessThan()`. Incorrect `lessThan()` consistency can corrupt queue semantics. `adjustTop()` must be called after mutating the top element.

`ReflectionUtils.newInstance()` may run arbitrary constructors and then inject configuration. Constructors with side effects or missing no-arg constructors can fail before configuration is set.

`StringUtils.split`/`escapeString`/`unEscapeString` must keep escaping semantics aligned, especially around trailing escape characters, escaped commas, and double escaping. Hex conversion requires even-length valid hex strings.

`RunJar` executes user-supplied jar code and unpacks archives, so callers must consider classpath isolation, manifest correctness, extraction paths, and error propagation from invoked main methods.

## Test Signals

Record runtime tests should round-trip generated records through binary, CSV, and XML `RecordInput`/`RecordOutput` implementations; cover every primitive type; cover nested records, vectors, and maps; verify null/empty strings and buffers; exercise non-ASCII `ustring` data; and compare tagged versus untagged `serialize`/`deserialize` paths.

Variable-length utility tests should cover compact and expanded encodings for `int` and `long`, boundary values around `-120` and `128`, min/max integer values, stream and byte-array reads, encoded-size calculation, and lexicographic byte comparison behavior.

Comparator tests should assert that registered `RecordComparator` raw comparisons produce the same ordering as deserialized `Record.compareTo()` for representative records and edge values.

Record compiler tests should parse valid DDL with includes, modules, primitive fields, vectors, maps, and record references; reject malformed DDL with useful `ParseException` messages; verify token line/column reporting; generate Java and C++ into expected destination directories; and verify Ant `RccTask` behavior for file, fileset, language, destination, and fail-on-error combinations.

Record metadata tests should build `RecordTypeInfo` with primitive and composite fields, serialize/deserialize it, compare `FieldTypeInfo` and `TypeID` equality/hash behavior, retrieve nested struct metadata, and verify `meta.Utils.skip()` consumes exactly the bytes for each type without corrupting subsequent reads.

UGI tests should cover constructor validation, immutable creation, group ordering with default group first, writable serialization round trips, comma-separated configuration save/read, malformed configuration failures, login fallback behavior, per-thread current UGI isolation, equality/hash code, and behavior when the Unix group command fails.

`Logalyzer` tests should cover archive input URI handling, archive destination creation, regex mapper configuration and match output, sort column/separator interpretation in `LogComparator`, and end-to-end analysis output on a small fixture.

`CopyFiles` tests should cover recursive source listing, multiple filesystem URI schemes, list-file source mode, duplicate source detection and `DuplicationException.ERROR_CODE`, ignored versus fatal read failures, log-path output, command-line argument validation, and `ToolRunner` integration.

Utility tests should cover `Daemon` daemon flag and wrapped runnable retention; `DiskChecker` directory creation races, non-directory paths, unwritable paths, and disk-space exceptions; `GenericOptionsParser` handling of `-conf`, `-D`, `-fs`, `-jt`, unknown options, remaining args, and custom Commons CLI options; and `GenericsUtil` empty-list behavior.

Sorting tests should verify `QuickSort` and `MergeSort` on empty, single-item, duplicate, already-sorted, reverse-sorted, and random data; assert that `IndexedSortable` swaps stay within `[l, r)`; and verify `Progressable.progress()` is invoked for long quicksort runs.

`PriorityQueue` tests should validate max-size initialization, `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, `clear`, and ordering when `lessThan()` defines reverse or equal-priority cases.

`Progress` tests should build multi-level phase trees, verify current phase transitions, complete propagation to parents, aggregate progress values, status text, and `toString()` output.

`Shell` tests should run simple commands, non-zero exit commands, custom environment, custom working directory, interval gating, stdout parsing, large-output guard behavior for `ShellCommandExecutor`, Windows/null command branches where applicable, and `ExitCodeException.getExitCode()`.

`ReflectionUtils` tests should instantiate configurable and non-configurable classes, verify configuration injection order, handle constructor failures, and exercise thread-info logging without assuming stable thread ordering.

`StringUtils` tests should cover exception stack rendering, hostnames with/without dots, human-readable integer thresholds, percentage precision, empty and non-empty arrays, byte/hex round trips, invalid hex strings, URI/path conversion, negative and zero time differences, escaped split/escape/unescape edge cases, hostname fallback, and startup/shutdown logging.

`Tool`/`ToolRunner` tests should verify configuration propagation, null configuration handling, remaining application arguments after generic parsing, returned exit codes, thrown exceptions, and generic usage output.

`VersionInfo` tests should verify all metadata getters return non-null stable strings for a packaged build and that `main()` prints the expected fields. `XMLUtils` tests should run a small XSLT transform, malformed stylesheet, malformed XML, and writer error propagation.

## Cross-Chunk Notes

The chunk begins after the start of `CsvRecordOutput`; earlier `org.apache.hadoop.record` declarations such as `Buffer`, `BinaryRecordInput`, `BinaryRecordOutput`, `CsvRecordInput`, and the beginning of `CsvRecordOutput` are expected in the preceding chunk.

The compiler package references `JCompType`, `CppGenerator`, and `JavaGenerator`, but this chunk only exposes the public DDL model and generated parser surfaces. The final reconciliation should connect those references to chunks containing their declarations or implementation details.

The `org.apache.hadoop.util` section in this chunk starts at `CopyFiles` and ends the package. Earlier utility classes, if any, are outside this chunk and should be merged into the final per-file research for complete Hadoop 0.17.0 utility coverage.
