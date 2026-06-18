# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.21.0.xml lines 1-5833

## Purpose

This chunk is the opening range of a generated JDiff XML API description for Hadoop HDFS 0.21.0. It records public and protected Java API metadata rather than executable implementation: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, fields, deprecation markers, declared exceptions, synchronization flags, and Javadoc text.

The range begins with the XML/JDiff header and generation command line, then covers `org.apache.hadoop.fs.Hdfs`, the full `org.apache.hadoop.hdfs` package present in this early API section, and the beginning of `org.apache.hadoop.hdfs.protocol`. It ends inside the `FSConstants` interface after the `SMALL_BUFFER_SIZE` field begins, so later constants and subsequent protocol classes require adjacent chunks during merge.

## Important APIs, Types, and Functions

The `org.apache.hadoop.fs` package contributes the `Hdfs` class, an `AbstractFileSystem` implementation for HDFS. Its surface mirrors Hadoop's newer abstract filesystem contract: `createInternal`, `delete`, `open`, `mkdir`, `renameInternal`, `listStatus`, `listStatusIterator`, status/checksum/block-location lookups, replication/owner/permission/time mutation, checksum verification toggling, symlink support, `createSymlink`, `getLinkTarget`, `getServerDefaults`, and default URI port discovery. The declared exceptions repeatedly include `IOException` and `UnresolvedLinkException`, marking symbolic-link handling as part of the HDFS filesystem contract in 0.21.0.

The `org.apache.hadoop.hdfs` package exposes client-side HDFS access and filesystem wrappers:

- `BlockMissingException` extends `IOException` and carries the corrupted file name plus offset for reads that encounter a block with no locations.
- `BlockReader` extends `FSInputChecker` and is the low-level client wrapper around a DataNode socket. It provides synchronized byte-array reads, single-byte reads, skipping, seeking, chunk-position calculation, protected `readChunk`, `readAll`, close, and three `newBlockReader` factory overloads that progressively add checksum verification and client-name parameters. The factories require block id, generation stamp, `BlockAccessToken`, offset/length, socket, and buffer size.
- `DeprecatedUTF8` wraps the deprecated Hadoop `UTF8` type while making deprecation explicit in the type name. It has string/copy constructors plus static `readString` and `writeString` helpers over `DataInput`/`DataOutput`.
- `DFSClient` is the core client implementation used by `DistributedFileSystem`. It implements `FSConstants` and `Closeable`, connects to the NameNode through `ClientProtocol`, and directly talks to DataNodes for block IO. It exposes NameNode proxy creation, lifecycle close, default block size/replication/server defaults, delegation-token get/renew/cancel, bad-block reporting, block locations, opens, many create overloads, primitive create with already-masked permissions and bytes-per-checksum, symlink creation and first-link resolution, replication, rename, concat, delete, existence checks, partial listings, file/link status, checksums, permission/owner/time setters, disk and block health statistics, DataNode reports, safemode, refresh, metasave, finalize/upgrade progress, mkdir variants, and `toString`.
- `DFSClient.DFSDataInputStream` extends `FSDataInputStream` around `DFSInputStream` and exposes the current DataNode, current block, and visible file length.
- `DFSConfigKeys` extends `CommonConfigurationKeys` and is a large public constant holder for HDFS configuration keys and defaults. Families visible in this chunk cover block size, replication, client buffers/checksums/packet size, NameNode and backup/checkpoint HTTP addresses, DataNode balance bandwidth, safemode and replication tuning, permissions, HTTPS keystore/auth flags, access-time precision, failed volume tolerance, delegation-token timing, data/name/edits/checkpoint directories, client retry and socket tuning, balancer windows, DataNode addresses, directory-scan settings, DNS, reserved disk space, handler counts, xceiver limits, block scanners, simulated storage, transferTo, heartbeat, decommissioning, append support, HTTPS enablement, block access tokens, block report intervals, plugin keys, startup keys, web UGI, and Kerberos keytab/principal keys.
- `DFSUtil` provides utility methods for path-name validation, keytab login, and UTF-8 byte/string conversion. The nested `DFSUtil.ErrorSimulator` has static methods to initialize, set, clear, and query simulated error events for tests.
- `DistributedFileSystem` extends `FileSystem` and is the end-user HDFS filesystem facade backed by `DFSClient`. It exposes URI initialization, path normalization that tolerates explicit default ports, working/home directories, block locations, checksum verification, open, append, create/primitive create/non-recursive create, replication, concat, rename, delete, content summary, quota setting, listing, mkdir/primitive mkdir, close, raw client access, capacity/status calls, block-health counters, DataNode stats, safemode, namespace save, failed-storage restore, refresh, upgrade finalization/progress, metasave, server defaults, checksum-failure reporting, file status/checksum, permission/owner/time mutation, and delegation-token operations.
- `DistributedFileSystem.DiskStatus` extends `FsStatus` and is deprecated in favor of `FsStatus`, but still exposes `getDfsUsed`.
- `HdfsConfiguration` extends `Configuration` and documents that it registers deprecated keys.
- `HDFSPolicyProvider` extends Hadoop security `PolicyProvider` and returns HDFS protocol service definitions.
- `HftpFileSystem` and `HsftpFileSystem` provide read-only HTTP/HTTPS filesystem access via NameNode servlets. `HftpFileSystem` handles date formatting, URI initialization, HTTP connection opening, open/list/status/checksum, working directory, unsupported append/create/rename/delete/mkdir operations, and content summary. `HsftpFileSystem` extends it for HTTPS and adds protected dummy hostname verifier/trust manager nested classes that bypass certificate/hostname validation.

The package-level HDFS Javadoc included at the end of `org.apache.hadoop.hdfs` states the design model: a distributed `FileSystem` loosely based on GFS, but with strictly one writer per file and append-only byte-stream semantics for the active writer.

The `org.apache.hadoop.hdfs.protocol` package starts with protocol value types and RPC contracts:

- `AlreadyBeingCreatedException` reports an attempt to create a file already open for creation.
- `Block` is a primitive `Writable` and `Comparable` block identifier with block id, length, generation stamp, block/meta filename parsing helpers, setters/getters, serialization, comparison, equality, hashing, and filename regex fields.
- `BlockListAsLongs` represents block reports compactly as a `long[]`, avoiding arrays of `Block` objects. It encodes finalized replicas as triples, then a sentinel invalid replica, then under-construction replicas as quadruples including replica state. Accessors expose the raw array, block count, id, length, generation stamp, an iterator, and a specialized `BlockReportIterator`.
- `BlockListAsLongs.BlockReportIterator` iterates over block-report entries and exposes the current replica state.
- `ClientDatanodeProtocol` begins with `getReplicaVisibleLength`, a DataNode-facing client protocol method for visible replica length.
- `ClientProtocol` is the main client-to-NameNode RPC interface used through `DistributedFileSystem`. Visible methods include block locations, server defaults, create, append, replication, permissions, owners, abandon/add/complete block, bad-block report, rename/concat/delete, mkdirs, partial listing, lease renewal, filesystem stats, DataNode reports, preferred block size, safemode, namespace save, failed-storage restore, refresh, finalize upgrade, distributed-upgrade progress, metasave, corrupt-file listing, file/link info, content summary, quota setting, fsync, time setting, symlink creation/resolution, pipeline generation-stamp/token update, pipeline update, and delegation-token get/renew/cancel. Fields include protocol `versionID` and indexes into the `getStats` array.
- `DatanodeID` is a `WritableComparable` identity for a DataNode, composed of `name` (`host:port`), `storageID`, info port, and IPC port. It supports constructors/copying, field access, host/port parsing, registration update without storageID replacement, comparison by name, serialization, equality, hashing, and an empty-array constant.
- `DatanodeInfo` extends `DatanodeID` and implements network `Node`. It adds capacity, DFS used, non-DFS used, remaining space, usage percentages, last update, xceiver count, network location/rack, host name, formatted reports, decommission state transitions, admin state, topology parent/level, serialization, equality, and static read helper.
- `DatanodeInfo.AdminStates` is an enum for DataNode administrative state.
- `DataTransferProtocol` defines the DataNode data-transfer wire protocol. Visible nested enums/classes include block construction stages, operations, pipeline acknowledgements, receiver dispatch, sender serialization helpers, and status codes.
- `DataTransferProtocol.BlockConstructionStage` includes recovery-stage mapping for pipeline/block construction state.
- `DataTransferProtocol.Op` serializes/deserializes operation codes.
- `DataTransferProtocol.PipelineAck` serializes acknowledgements for a pipeline sequence number and per-DataNode status list, with success checking and string formatting.
- `DataTransferProtocol.Receiver` reads an operation from a stream, dispatches it, and requires subclasses to implement read-block, write-block, replace-block, copy-block, and block-checksum handlers.
- `DataTransferProtocol.Sender` writes operation requests for read, write, replace, copy, and checksum actions, including block id, generation stamp, client name, construction stage, pipeline targets, source DataNode, and block access token.
- `DataTransferProtocol.Status` is the response enum with `SUCCESS`, generic and specialized error statuses, access-token error, and `CHECKSUM_OK`; it supports `DataInput`, `DataOutput`, and `OutputStream` writing.
- `DirectoryListing` is a `Writable` partial directory listing containing `HdfsFileStatus[]` plus remaining-entry count, `hasMore`, last-name retrieval for iterative listing, and serialization.
- `DSQuotaExceededException` specializes `QuotaExceededException` for disk-space quota violations and formats a message from quota/count values.
- `FSConstants` begins at the chunk tail with constants for minimum write blocks, invalidation chunking, quota sentinel values, heartbeat/block-report intervals, lease periods, max path length/depth, and buffer sizes. The interface continues beyond this chunk.

## Control Flow and Execution Model

This XML does not contain method bodies, but the public control-flow contracts are visible through API shape and docs.

Client filesystem control flow is layered. End-user code can enter through `DistributedFileSystem` for the classic `FileSystem` API or through `org.apache.hadoop.fs.Hdfs` for the newer `AbstractFileSystem` API. Both adapt path-level operations to HDFS-specific client logic and surface symbolic-link exceptions. `DistributedFileSystem` delegates most work to `DFSClient`, which in turn uses `ClientProtocol` for namespace and block-location RPCs and uses `BlockReader`/DataNode transfer protocol objects for block data. `DFSClient.close` is synchronized and documented as abandoning leases/open creates and closing NameNode connections.

Read control flow is split between NameNode metadata lookup and DataNode streaming. `DFSClient.getBlockLocations` asks the NameNode for block hosts for a file region. `DFSClient.open` creates `DFSInputStream`; `DFSClient.DFSDataInputStream` lets callers inspect the current DataNode and block. `BlockReader` handles socket reads from a DataNode with checksum-aware chunk reads, synchronized `read`, `skip`, `readChunk`, and `close`, and factory overloads that establish a reader with block token, generation stamp, offset/length, buffer size, checksum policy, and optional client name. `BlockMissingException` is the read-side failure signal when no block locations remain.

Write control flow starts with `create` variants or `append`. `DFSClient` and `DistributedFileSystem` expose high-level overloads that fill defaults for permissions, parent creation, replication, block size, progress callbacks, buffer size, and checksum bytes, then lower-level `primitiveCreate` variants use absolute/masked permissions. `ClientProtocol.create`, `addBlock`, `complete`, `abandonBlock`, `updateBlockForPipeline`, and `updatePipeline` define the NameNode coordination loop for file creation and pipeline recovery. `DataTransferProtocol.Sender.opWriteBlock` serializes the DataNode pipeline write request, and `PipelineAck` models the downstream acknowledgement path.

Namespace mutation and metadata control flow are centralized in `ClientProtocol`: rename, concat, delete, mkdirs, set owner, set permission, set replication, set quota, set times, symlink creation, link-target resolution, and content-summary lookups. Many of these methods declare `UnresolvedLinkException`, so callers must either resolve symlinks or use APIs that intentionally return link status instead of target status. Partial listings use `DirectoryListing` and `startAfter` byte names to page through large directories.

Cluster administration control flow is exposed both through `DFSClient` and `DistributedFileSystem`, then maps to `ClientProtocol`: safemode enter/leave/get, save namespace, restore failed storage, refresh hosts/excludes, finalize upgrade, distributed-upgrade progress, metasave, DataNode reports, block-health counts, and filesystem stats. `ClientProtocol.setSafeMode` documentation describes startup safemode, block-report collection, minimal replication threshold, extension delay, manual safemode, and special threshold values.

HTTP filesystem control flow enters `HftpFileSystem`/`HsftpFileSystem`, which open HTTP(S) connections to NameNode servlets for reads, listings, file status, checksums, and content summaries. Mutating filesystem methods exist because of the `FileSystem` contract but are documented as unsupported or effectively not part of the read-only HFTP model. `HsftpFileSystem` overrides initialization, URI, and connection behavior and supplies permissive SSL verification helpers.

Data-transfer wire flow is expressed as a small operation protocol. `Receiver.readOp` reads an `Op`, `processOp` dispatches by op, and abstract protected methods force concrete DataNode receivers to implement read/write/replace/copy/checksum behavior. `Sender` provides matching static writers for each op. Status and pipeline acknowledgement classes serialize response state back over streams.

## State and Persistence Behavior

The XML itself is generated state for API compatibility comparison. The header records generation by the JDiff Javadoc doclet, the API name `hadoop-hdfs 0.21.0`, JDiff version `1.0.9`, source path, classpath, and dependency jars. It is intended as an input to API diff tooling rather than runtime HDFS behavior.

Within the represented APIs, persistent HDFS state includes namespace metadata, edit-log/fsimage state implied by `saveNamespace`, upgrade state, quotas, symlinks, file status, content summaries, permissions, ownership, modification/access times, replication, block generation stamps, leases, delegation tokens, and DataNode block reports. The chunk exposes these as protocol and client contracts but not their implementation storage.

Block and DataNode protocol types are explicit serialization boundaries. `Block`, `BlockListAsLongs`, `DatanodeID`, `DatanodeInfo`, `DirectoryListing`, `DataTransferProtocol.Op`, `Status`, and `PipelineAck` all read and/or write to `DataInput`/`DataOutput` streams. `BlockListAsLongs` is particularly persistence/wire sensitive because the long-array layout encodes finalized and under-construction replicas with different tuple widths and a sentinel invalid replica.

Lease and pipeline state are visible through `ClientProtocol.renewLease`, `abandonBlock`, `complete`, `fsync`, `updateBlockForPipeline`, and `updatePipeline`. The lease documentation states that clients periodically renew leases so the NameNode can recover locks and live file creates from dead clients. Pipeline recovery asks the NameNode for a new generation stamp plus access token, then updates the pipeline with old/new block identifiers and DataNode targets.

Security state appears through delegation-token operations, keytab/principal configuration keys, HTTPS keystore keys, block access token keys/defaults, and `BlockAccessToken` parameters on block-read/write/copy/checksum operations. `HDFSPolicyProvider` supplies protocol authorization services for HDFS RPC interfaces.

Transient client state includes working directories, checksum verification settings, `DFSClient` server-default caches implied by `SERVER_DEFAULTS_VALIDITY_PERIOD`, the `BlockReader` socket/checksum position, `DFSClient.DFSDataInputStream` current DataNode/block, HFTP `UserGroupInformation`, random selection state, and thread-local date formatter. `DFSUtil.ErrorSimulator` is test-only static state for injecting errors.

## Dependencies and Integration Points

The generated descriptor itself depends on JDiff/Javadoc structure and the `api.xsd` schema. Its command-line comment shows build-time dependencies on Hadoop common, commons-cli, xmlenc, commons-httpclient/codec/net, Jetty/JSP/servlet APIs, JUnit, HSQLDB, Avro, Jackson, SLF4J, log4j, AspectJ, Mockito, JDiff, Xerces, Ant, Ivy, and other Hadoop 0.21-era libraries.

Runtime API dependencies shown in signatures include:

- Hadoop core filesystem APIs: `AbstractFileSystem`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, `FileChecksum`, `MD5MD5CRC32FileChecksum`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `Path`, `Options.Rename`, and `CreateFlag` enum sets.
- Hadoop configuration and utility APIs: `Configuration`, `CommonConfigurationKeys`, `Progressable`, `Tool`-adjacent filesystem contracts, `Writable`, `WritableComparable`, `UTF8`, and `Text`.
- HDFS protocol APIs: `ClientProtocol`, `LocatedBlock`, `LocatedBlocks`, `HdfsFileStatus`, `DirectoryListing`, `DatanodeID`, `DatanodeInfo`, `FSConstants` enums, `BlockAccessToken`, quota exceptions, and upgrade status reports.
- Security APIs: `UserGroupInformation`, `PolicyProvider`, `Service`, `Token`, `SecretManager.InvalidToken`, Kerberos keytab/principal configuration, and block/delegation tokens.
- Networking and IO: `Socket`, `SocketFactory`, `InetSocketAddress`, `URI`, `HttpURLConnection`, `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `OutputStream`, `InputStream`, `File`, and Java SSL verifier/trust-manager interfaces.
- Topology APIs: `org.apache.hadoop.net.Node` for `DatanodeInfo` rack/tree integration.

Integration points between packages are strong. `DistributedFileSystem` is the public facade, `DFSClient` is the operational bridge, `ClientProtocol` is the NameNode RPC contract, `DataTransferProtocol` is the DataNode data-plane wire contract, and the protocol value objects provide the serialization types crossing those boundaries. `Hdfs` gives the same HDFS backend to the newer `AbstractFileSystem` API.

## Risks and Edge Cases

- This is API metadata, not implementation. It does not expose method bodies, constant values, private fields, annotations, generic type parameters in full fidelity, or runtime lock usage beyond JDiff synchronization flags and Javadocs. Implementation claims must be verified against the Java source.
- The chunk boundary cuts off `FSConstants`; only the opening fields are visible. Later constants, nested enums, and protocol classes must be reconciled from following chunks.
- The XML is generated from a 2010 build command and contains old dependency paths and `0.21.0-SNAPSHOT` classpath entries. Build-path details are provenance, not necessarily portable build instructions.
- HDFS 0.21.0 exposes deprecated APIs: `DFSClient(Configuration)`, a `DFSClient.open` overload with `FileSystem.Statistics`, old boolean `rename`, `DistributedFileSystem.DiskStatus`, raw capacity/used calls, and possibly old HFTP/HSFTP behaviors. Compatibility consumers may depend on them even when replacement APIs exist.
- The HFTP/HSFTP surfaces are read-only but still implement mutating `FileSystem` methods. Callers that assume all `FileSystem` implementations can create/rename/delete may hit unsupported-operation behavior at runtime.
- `HsftpFileSystem` dummy hostname verifier and trust manager intentionally bypass host/certificate checks. That is a security-sensitive API surface and should be restricted to the intended compatibility/testing context if implemented as documented.
- Data-transfer protocol serialization is compatibility-sensitive. Changing enum ordering, status encodings, block construction stage mapping, or `PipelineAck` layout can break cross-version DataNode/client communication.
- `BlockListAsLongs` relies on exact long-array layout and a sentinel invalid replica. Off-by-one decoding, finalized/under-construction count mismatches, or replica-state mapping errors can corrupt block reports.
- Symlink support is visible across `Hdfs`, `DFSClient`, `DistributedFileSystem`, and `ClientProtocol`, but many APIs throw `UnresolvedLinkException`. Callers must choose link-aware variants such as file-link status or link-target resolution when they do not want transparent target traversal.
- Lease renewal is central to open-file recovery. Missing or delayed `renewLease` calls can cause the NameNode to revoke client-held creates/locks and trigger recovery.
- Quota operations use sentinel values (`QUOTA_DONT_SET`, `QUOTA_RESET`) and throw namespace/diskspace quota exceptions. Invalid sentinel handling or confusing diskspace vs namespace quotas can produce runtime failures.
- `DatanodeID` equality/comparison is based primarily on name, while storage ID is mutable and deliberately not always updated during registration refresh. Tests should cover re-registration and replacement cases.
- Several methods are synchronized (`DFSClient.close`, `BlockReader` read/skip/chunk/close, `DatanodeInfo` network-location accessors), but most client/protocol methods are not. Thread-safety assumptions should be checked in implementation sources.

## Test Signals

Useful validation for this API surface should come from compatibility tests, unit tests around serializers, and HDFS integration tests:

- JDiff/API compatibility checks should parse this XML, compare it against adjacent HDFS versions, and flag additions/removals/deprecations for `Hdfs`, `DFSClient`, `DistributedFileSystem`, `ClientProtocol`, and `DataTransferProtocol`.
- Filesystem facade tests should exercise both `DistributedFileSystem` and `Hdfs` over MiniDFSCluster for create/open/delete/rename/list/status/checksum/block-location, permission/owner/time/replication, working-directory behavior, default-port URI normalization, and symlink/link-status behavior.
- Read-path tests should cover `DFSClient.open`, `DFSDataInputStream` current DataNode/block/visible length, `BlockReader` checksum verification on/off, read/skip/seek/readAll, missing/corrupt blocks, bad-block reporting, and block-token failures.
- Write-path and lease tests should cover create overloads, primitive create with masked permissions, create-parent false, append, add/complete/abandon block, fsync, lease renewal expiry/recovery, pipeline recovery via `updateBlockForPipeline` and `updatePipeline`, and `PipelineAck` success/error combinations.
- NameNode RPC tests should cover `ClientProtocol` namespace operations, partial directory listings with `startAfter`, content summary, quota set/reset/dont-set semantics, safemode transitions, save namespace restrictions, refresh hosts/excludes, metasave, corrupt-file listing, upgrade finalization/progress, and delegation-token lifecycle.
- Serialization tests should round-trip `Block`, `BlockListAsLongs` with finalized and under-construction replicas, `DatanodeID`, `DatanodeInfo`, `DirectoryListing`, `DataTransferProtocol.Op`, `Status`, and `PipelineAck`.
- DataNode/admin tests should validate `DatanodeInfo` capacity/remaining/used percentages, xceiver count, last update, topology parent/level, network location synchronization, admin-state transitions, and formatted report strings.
- HFTP/HSFTP tests should validate read-only open/list/status/checksum/content summary over HTTP and HTTPS, date parsing, URI construction, UGI handling, unsupported mutation calls, and SSL trust/hostname behavior.
- Configuration tests should verify every `DFSConfigKeys` key/default visible here maps to the intended `hdfs-default.xml` names and that `HdfsConfiguration` registers deprecated key aliases.
- Security tests should exercise `HDFSPolicyProvider`, Kerberos keytab login through `DFSUtil.login`, delegation-token get/renew/cancel, block access token enforcement on DataTransferProtocol read/write/copy/checksum, and HTTPS keystore configuration.

## Chunk Boundary Notes

Lines 1-5833 start at the XML document header and cover complete sections for `org.apache.hadoop.fs.Hdfs`, `org.apache.hadoop.hdfs`, and many early `org.apache.hadoop.hdfs.protocol` types. The range ends inside `FSConstants`, immediately after the opening of the `SMALL_BUFFER_SIZE` field. The merge lane should combine this report with later chunks before producing the final source-tree-aligned research document for the full `hadoop-hdfs_0.21.0.xml` file.
