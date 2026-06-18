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
