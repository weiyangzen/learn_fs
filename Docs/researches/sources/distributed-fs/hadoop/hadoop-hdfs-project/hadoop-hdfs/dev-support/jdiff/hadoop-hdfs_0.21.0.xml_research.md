# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.21.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007469`: lines 1-5833, `Docs/researches/chunks/subset-b-007469_research.md`
- `subset-b-007470`: lines 5834-11832, `Docs/researches/chunks/subset-b-007470_research.md`
- `subset-b-007471`: lines 11833-16220, `Docs/researches/chunks/subset-b-007471_research.md`

## Chunk Research

### subset-b-007469: lines 1-5833

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

### subset-b-007470: lines 5834-11832

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.21.0.xml lines 5834-11832

## Purpose

This chunk is generated JDiff public API metadata for Hadoop HDFS 0.21.0. It covers a broad middle slice of the exported HDFS surface: protocol status and block-location value types, HDFS block access-token security, delegation-token persistence hooks, balancer entry points, shared server constants, storage-directory state machines, DataNode storage and replica APIs, DataNode metrics, and the beginning of NameNode block/checkpoint/web-serving APIs.

Because the source is JDiff XML rather than Java implementation, the strongest signals are public signatures, inheritance, declared checked exceptions, synchronization flags, fields, and embedded Javadocs. The slice begins after the `FSConstants` interface header and ends shortly after the `FSNamesystem` class header, so both boundaries require neighboring chunk context during merge.

## Important APIs, Types, and Functions

Protocol and client-visible metadata appear first:

- `FSConstants` constants exposed in this slice include defaults for block size, checksum size, write packet size, replication, buffers, socket size, integer size, the `hdfs://` URI scheme, and `LAYOUT_VERSION`.
- `FSConstants.DatanodeReportType` models `ALL`, `LIVE`, and `DEAD` reports. `SafeModeAction` models leave, enter, and get operations. `UpgradeAction` models distributed-upgrade status, detailed status, and forced progress.
- `HdfsFileStatus` is a `Writable` wire representation for file metadata: length, directory/symlink flags, block size, replication, modification/access times, permission, owner/group, local name bytes, full path construction, symlink target, and `EMPTY_NAME`.
- `LocatedBlock` and `LocatedBlocks` are `Writable` block-location responses. They connect `Block`, `DatanodeInfo[]`, start offsets, corrupt flags, last-block-complete state, file length, under-construction state, binary-search insertion helpers, and `BlockAccessToken` propagation.
- `QuotaExceededException` and `NSQuotaExceededException` carry quota, count, and path data with specialized messages. `RecoveryInProgressException`, `UnregisteredNodeException`, and `UnresolvedPathException` are protocol exceptions for replica recovery collisions, invalid DataNode registrations, and symlink resolution.

Security APIs in this slice define HDFS block tokens and delegation-token persistence:

- `AccessTokenHandler` can run in master mode or slave mode. Master mode exports and updates access keys; slave mode imports keys; both modes generate and verify `BlockAccessToken` values. Access modes are `READ`, `WRITE`, `COPY`, and `REPLACE`.
- `BlockAccessKey`, `BlockAccessToken`, and `ExportedAccessKeys` are `Writable` values for key id/material/expiry/MAC state, token id/authenticator pairs, current/all exported keys, key-update intervals, token lifetime, and dummy disabled-token values.
- `InvalidAccessTokenException` reports failed block-token validation.
- `DelegationTokenIdentifier` specializes Hadoop delegation-token identifiers for HDFS using `HDFS_DELEGATION_KIND`.
- `DelegationTokenSecretManager` extends the token secret-manager flow with NameNode persistence hooks: load/save state, add persisted delegation tokens, update master keys, update token renewal/cancellation, expose key counts, and log master-key updates.
- `DelegationTokenSelector` is the HDFS token selector.

Balancer and shared server-common APIs include:

- `Balancer` implements `Tool`, exposes `main`, `run`, `getConf`, and `setConf`, and publishes exit/status constants such as `SUCCESS`, `ALREADY_RUNNING`, `NO_MOVE_BLOCK`, `NO_MOVE_PROGRESS`, `IO_EXCEPTION`, and `ILLEGAL_ARGS`. Its Javadoc describes the iterative disk-utilization balancing algorithm, threshold semantics, bandwidth setting, progress output, and exit criteria.
- `GenerationStamp` is a comparable long counter with synchronized `nextStamp`, `FIRST_VALID_STAMP`, and `GRANDFATHER_GENERATION_STAMP`.
- `HdfsConstants` contains IO timeout constants and nested enums for block-under-construction states, NameNode roles, node types, replica states, and startup options.
- `ReplicaState` maps replica lifecycle values to integer wire values and supports `read(DataInput)`/`write(DataOutput)`. States are `FINALIZED`, `RBW`, `RWR`, `RUR`, and `TEMPORARY`.
- `StartupOption` maps format, regular, backup, checkpoint, upgrade, rollback, finalize, and import options to names and NameNode roles.
- `InconsistentFSStateException` and `IncorrectVersionException` represent unrecoverable storage-directory inconsistency and layout/software version mismatches.
- `JspHelper` supports legacy HDFS web UI and HFTP flows: choosing a best DataNode for a block, streaming block bytes as ASCII, rendering table/path/goto UI fragments, validating path/long/URL inputs, constructing titles, returning version tables, and resolving web `UserGroupInformation` including delegation tokens.

Storage and distributed-upgrade APIs form the persistence core:

- `Storage` extends `StorageInfo` and manages a list of `StorageDirectory` instances. It exposes directory iteration by type, storage-version checking, namespace and cluster id fields through subclasses, storage formatting/recovery helpers, and filesystem transition methods.
- `Storage.StorageDirectory` models one persistent root and exposes `current`, `VERSION`, `previous`, `previous.tmp`, `removed.tmp`, `finalized.tmp`, `lastcheckpoint.tmp`, and `previous.checkpoint` paths. It can analyze startup state, recover failed transitions, and lock/unlock storage directories.
- `Storage.StorageState` enumerates `NON_EXISTENT`, `NOT_FORMATTED`, normal operation, complete/recover upgrade, complete finalize, complete/recover rollback, and complete/recover checkpoint.
- `StorageInfo` is a `Writable` common header: `layoutVersion`, `namespaceID`, and `cTime`, with copying and serialization.
- `Upgradeable`, `UpgradeManager`, `UpgradeObject`, `UpgradeObjectCollection`, and `UpgradeStatusReport` define distributed-upgrade registration, ordering, start/complete commands, synchronized upgrade-state inspection, percentage status, detailed status reports, and `Writable` status serialization.
- `Util` provides time and URI conversion helpers for server-common configuration paths.

DataNode APIs dominate the middle of the slice:

- `DataNode` extends `Configured` and implements `InterDatanodeProtocol`, `ClientDatanodeProtocol`, `FSConstants`, and `Runnable`. Its public/protected surface covers socket creation, static daemon creation, inter-DataNode proxy creation, registration access, NameNode/self addresses, storage-id assignment, `offerService`, retrying `run`, shutdown, disk-error handling, block-received notification, block-report scheduling, dataset access, replica recovery, visible-length queries, protocol version, and `main`.
- `DataStorage` extends storage behavior for DataNode storage ids and version fields. `DatanodeJspHelper` and `DirectoryScanner` appear as exported classes in this slice, though without substantive public methods here.
- `FSDataset` implements the concrete on-disk block store. It exposes metadata-file lookup, stored-block lookup, metadata stream/length checks, capacity/remaining/DFS-used reporting, block file/input-stream access, temporary stream access, unlink-on-snapshot-copy semantics, append/recover-append/recover-close, RBW and temporary replica creation, checksum-channel adjustment, block finalization/unfinalization, block report generation, block validity checks, invalidation, data-dir health checks, shutdown, storage-info text, disk/in-memory reconciliation through `checkAndUpdate`, replica recovery initialization/update, and visible-length reads.
- `FSDatasetInterface` defines the storage contract used by DataNode implementations, including block and metadata streams, replica creation/recovery/finalization, block reports, invalidation, resource checks, visible length, and recovery updates. Nested `BlockInputStreams`, `BlockWriteStreams`, and `MetaDataInputStream` carry paired block/checksum IO handles and metadata length.
- `Replica` exposes block id, generation stamp, state, received bytes, bytes on disk, and reader-visible length. `ReplicaInfo` is the base DataNode metadata implementation extending `Block`; `ReplicaNotFoundException` reports missing replicas.
- `UpgradeObjectDatanode` is a runnable upgrade object for DataNodes with access to the `DataNode`, `doUpgrade`, `run`, and completion-command behavior.
- `DataNodeActivityMBean`, `DataNodeMetrics`, and `FSDatasetMBean` expose DataNode metric registration, periodic updates, min/max reset, shutdown, byte/block counters, client locality counters, operation-latency metrics, heartbeat/block-report metrics, and dataset capacity/usage/storage-info values.

The NameNode portion begins at the end of the chunk:

- `BackupNode` handles backup/checkpoint roles. Its API covers RPC/HTTP addresses, namesystem loading/initialization/stop, block-location queries for the balancer, registration, checkpoint start/end, and journaling from the active node.
- `BackupStorage` specializes `FSImage` conversion checks for backup/checkpoint storage.
- `BlockManager` exposes block-report processing and map/corrupt-file sizing constants. Its Javadoc states it is an `FSNamesystem` helper and several methods require the `FSNamesystem` lock.
- `BlockPlacementPolicy` and `BlockPlacementPolicyDefault` define placement verification, replica deletion choice, initialization from configuration/cluster stats/network topology, and target selection. The default strategy documents first replica local or random, second on a different rack, and third on a different node in the second replica's rack.
- `CheckpointSignature` is a `WritableComparable` `StorageInfo` signature for checkpoint transactions.
- `ContentSummaryServlet`, `DelegationTokenServlet`, `FileChecksumServlets.GetServlet`, `FileChecksumServlets.RedirectServlet`, `FileDataServlet`, and `FsckServlet` are NameNode web/HFTP servlets for content summaries, delegation tokens, file checksums, data redirection to DataNodes, and fsck. `FileDataServlet.createUri` constructs DataNode redirect URIs from `HdfsFileStatus`, UGI, `ClientProtocol`, and the HTTP request.
- `CorruptReplicasMap` tracks block-to-DataNode corrupt replica sets and exposes add/count/size operations.
- `DatanodeDescriptor` extends `DatanodeInfo` for NameNode-internal DataNode state, including constructors from `DatanodeID`, topology/hostname/capacity fields, block counts, scheduled-block counts, equality/hash behavior, `isAlive`, and `needKeyUpdate`. Its Javadoc explicitly says it is not sent to clients/DataNodes and is not persisted in fsimage.
- `DatanodeDescriptor.BlockTargetPair` pairs a block with replication targets.
- `FSClusterStats` provides total cluster load for placement policy decisions.
- `FSEditLog` exposes namespace edit logging and synchronization. `logSync` has detailed Javadoc for transaction IDs, thread-local sync targets, volatile sync-in-progress state, double buffering, and the synchronized/unsynchronized/synchronized sync phases.
- `FSImage` extends `Storage` for namespace checkpointing and edit logs: failed-storage restoration flags, version-field read/write, edit-log access, conversion checks, save-current, checkpoint moves, formatting, edit-file lookup, pre-upgrade storage corruption, static string/byte readers, and fields for `namesystem`, `checkpointTime`, `editLog`, removed storage dirs, and volatile checkpoint state.
- `FSInodeInfo` exposes `getFullPathName` to pluggable block placement.
- `FSNamesystem` begins at the boundary with static `getNamespaceDirs(Configuration)` and `getStorageDirs(Configuration)`.

## Control Flow and Execution Model

The protocol objects in `HdfsFileStatus`, `LocatedBlock`, `LocatedBlocks`, block-token classes, storage status reports, and checkpoint signatures are mostly serialization boundaries. They implement `Writable`/`WritableComparable`, expose default constructors for deserialization, and carry explicit `DataInput`/`DataOutput` methods. Control flow around these values is driven by NameNode/DataNode RPC and HTTP callers outside this XML.

Block access-token flow is split by role. A NameNode-style master `AccessTokenHandler` generates and rotates keys, exports `ExportedAccessKeys`, and generates tokens for users/blocks/modes. DataNode-style slave handlers import exported keys and check token authorization by token, optional user id, block id, and access mode. Delegation-token flow persists longer-lived tokens and master keys through `DelegationTokenSecretManager` hooks that integrate with `FSNamesystem` and edit-log persistence.

Balancer control flow is an administrator-run `Tool`. It repeatedly obtains cluster utilization, classifies nodes by threshold, schedules block moves with a per-DataNode concurrent-move cap, observes bandwidth configuration, writes progress output, and exits when the cluster is balanced, no block can move, progress stalls, IO fails, arguments are invalid, or another balancer is running.

Storage control flow is a startup and upgrade state machine. `StorageDirectory.analyzeStorage` detects normal, missing, unformatted, completed, or recoverable transitional directory layouts. `doRecover` completes or rolls back failed transitions using the named temporary directories. The Javadocs emphasize that `VERSION` is written last so its presence marks a valid storage directory. `Storage.lock`/`unlock` attempt exclusive access, with an explicit warning that not every filesystem, notably NFS, can provide reliable locking.

Distributed upgrade control flow is coordinated by `UpgradeManager`: load applicable `Upgradeable` objects from `UpgradeObjectCollection`, initialize the current set, start and complete upgrade objects, maintain synchronized upgrade state/version/status, and broadcast `UpgradeCommand` messages to peer components. `UpgradeObjectDatanode` runs DataNode-side upgrade work asynchronously via `Runnable`.

DataNode control flow centers on `DataNode.run` and `offerService`. The docs state that `run` retries `offerService` after exceptions until `shouldRun` is disabled by shutdown, while `offerService` loops on remote NameNode functions. Block writes flow through dataset methods that create temporary/RBW replicas, append or recover append, adjust checksum streams, finalize or unfinalize block files, and notify the NameNode of received blocks. Replica recovery flows through `initReplicaRecovery`, `recoverRbw`, `recoverAppend`, `recoverClose`, and `updateReplicaUnderRecovery`.

NameNode-side block management receives DataNode block reports through `BlockManager.processReport`, updates DataNode-to-block and block-to-DataNode maps, filters corrupt replicas through `CorruptReplicasMap`, and uses `BlockPlacementPolicy` to choose new targets or deletion candidates according to rack-awareness and cluster load. `FSEditLog.logSync` describes a three-phase sync model that swaps buffers under synchronization, flushes storage outside the lock, then marks sync complete under synchronization so writers can continue while durable IO proceeds.

Legacy HTTP and JSP control flow resolves request users through `JspHelper.getUGI`, validates request parameters, redirects reads and checksum requests to suitable DataNodes, serves delegation tokens for HFTP, and runs fsck/content-summary servlets against NameNode state.

## State and Persistence Behavior

Persistent state appears in several layers:

- `StorageInfo` persists layout version, namespace id, and creation time. `StorageDirectory` persists these and component-specific fields in `current/VERSION`, with transitional directories for upgrade, rollback, finalize, and checkpoint recovery.
- `FSImage` persists namespace checkpoints and edit-log metadata. Its docs repeat the invariant that version files are written last, and it tracks checkpoint time, edit log, removed/failed storage directories, and checkpoint state.
- `FSEditLog` persists namespace mutations such as open-file leases, close-file records, and mkdirs. `logSync` uses transaction ids and double buffers to coordinate in-memory edits and durable flushes.
- DataNode block state is persisted as block files plus metadata files. `FSDataset` and `FSDatasetInterface` expose metadata lengths/streams, block file lookups, generation stamps, replica states, on-disk lengths, visible lengths, RBW/temporary/finalized lifecycle transitions, invalidation, and disk-to-memory reconciliation.
- DataNode storage state includes DataNode storage ids through `DataStorage` and dataset-level capacity, remaining bytes, DFS-used bytes, valid-volume/resource checks, and storage info strings through `FSDatasetMBean`.
- Block-token keys and tokens are serialized with `Writable` APIs. `ExportedAccessKeys` carries current and historical keys plus token lifetime/update interval; dummy values represent disabled-token operation.
- Delegation-token secret-manager state is durable through load/save and persisted token/key update methods, which are intended to be backed by NameNode namespace/edit-log state.
- `DatanodeDescriptor` is explicitly transient NameNode memory state: it tracks DataNode stats and blocks but is not sent over the wire and not stored in fsimage.
- `CorruptReplicasMap` is in-memory NameNode state mapping blocks to corrupt DataNode replica sets; corrupt copies are hidden from reports until enough good replicas exist.
- Metrics classes hold operational counters/rates and publish through Hadoop metrics/JMX rather than durable storage.

## Dependencies and Integration Points

This chunk touches most core HDFS subsystems:

- Hadoop serialization and IO: `Writable`, `WritableComparable`, `DataInput`, `DataOutput`, `DataInputStream`, `InputStream`, `FilterInputStream`, `Closeable`, `File`, `URI`, and Java collections.
- HDFS protocol model: `Block`, `BlockListAsLongs`, `DatanodeID`, `DatanodeInfo`, `ClientProtocol`, `ClientDatanodeProtocol`, `LocatedBlock`, `LocatedBlocks`, and quota/unresolved-path exceptions.
- Security: Hadoop `UserGroupInformation`, delegation-token identifiers/selectors, `AbstractDelegationTokenSecretManager` lineage, `Text`, `Token`, `javax.crypto.Mac`, servlet request tokens, and block access tokens.
- Server storage: `StorageInfo`, `StorageDirectory`, NameNode/DataNode storage subclasses, `NamespaceInfo`, `UpgradeCommand`, startup options, node roles, and storage directory types.
- DataNode runtime: `InterDatanodeProtocol`, `DatanodeProtocol`, `DatanodeRegistration`, `ReplicaRecoveryInfo`, `BlockRecoveryCommand.RecoveringBlock`, `FSDatasetInterface`, `DataBlockScanner`, Hadoop `Daemon`, IPC `Server`, socket/NetUtils helpers, and disk checker exceptions.
- NameNode runtime: `FSNamesystem`, `BlockManager`, `DatanodeDescriptor`, `FSInodeInfo`, `FSImage`, `FSEditLog`, `JournalStream.JournalType`, checkpoint signatures, backup/checkpoint roles, and block placement policy configured by `dfs.block.replicator.classname`.
- Topology and placement: `NetworkTopology`, `FSClusterStats`, rack locations, writer-local placement, excluded/chosen node lists, and replica deletion sets.
- Web/HFTP integration: `javax.servlet` HTTP request/response, `JspWriter`, NameNode web servlets, HFTP file-data/checksum redirects, content-summary and fsck endpoints.
- Metrics and management: Hadoop metrics registry, `MetricsTimeVaryingLong`, `MetricsTimeVaryingInt`, `MetricsTimeVaryingRate`, DataNode activity MBean, and dataset MBean.

## Risks and Edge Cases

- This XML does not include method bodies. Implementation-specific behavior beyond signatures, synchronization metadata, fields, and Javadocs must be verified against the Java sources for HDFS 0.21.0.
- The line range starts inside `FSConstants`; constants before line 5834 and the interface opening are in the previous chunk. It ends just after `FSNamesystem.getStorageDirs`, so the rest of `FSNamesystem` is in the next chunk.
- Many exposed classes are server internals despite public visibility. `DatanodeDescriptor` explicitly is not a wire or fsimage type, and `BlockManager` docs say some methods require the `FSNamesystem` lock.
- `FSEditLog.logSync` relies on a subtle concurrency protocol: unsynchronized durable flushing allows concurrent writers, while callers needing exclusivity must synchronize and wait for active syncs to finish.
- Storage recovery depends on directory naming invariants and the rule that `VERSION` is written last. Partial writes or manual edits to `previous.tmp`, `removed.tmp`, `finalized.tmp`, or `lastcheckpoint.tmp` can alter startup recovery decisions.
- Storage locking is not guaranteed on all filesystems. Deployments using NFS-like storage need tests and operational safeguards for double-writer prevention.
- Replica lifecycle methods are compatibility-sensitive. Generation stamp, expected length, checksum offset, visible length, and state transitions across temporary, RBW, RWR/RUR, and finalized replicas must align with NameNode recovery.
- `FSDataset.getFile` ignores generation stamp according to its Javadoc, so callers must not treat a filename lookup alone as validation of generation-stamp correctness.
- `FSDataset.checkAndUpdate` reconciles disk and memory after scanner discoveries; mistakes there can delete map entries, add unexpected blocks, update generation stamps, or mark blocks corrupt based on file length mismatches.
- Block-token security depends on key rotation and master/slave key distribution. Stale exported keys, wrong access mode sets, user-id mismatches, or token lifetime skew can break reads, writes, copies, and replacements.
- Web helpers validate paths, longs, and URLs and construct redirects. These are request-boundary APIs; insufficient validation or wrong UGI/token handling can expose HFTP or JSP endpoints.
- The balancer prohibits multiple instances and exits on several conditions. Tests should distinguish no-move, no-progress, already-running, IO failure, and success exit codes.

## Test Signals

Useful validation should come from HDFS tests around the owning subsystems:

- Protocol serialization tests for `HdfsFileStatus`, `LocatedBlock`, `LocatedBlocks`, quota exceptions, unresolved paths, storage info, upgrade status reports, checkpoint signatures, block access keys/tokens, exported keys, and replica-state wire values.
- Block-token and delegation-token tests for master key rotation, exported key import, disabled dummy token behavior, mode-specific checks, expired/invalid tokens, token renewal/cancellation persistence, master-key persistence, and NameNode restart recovery.
- Balancer integration tests for threshold parsing, exit codes, concurrent-instance prevention, per-DataNode concurrent move limits, bandwidth setting effects, no-move/no-progress handling, and block movement under live workload.
- Storage tests for `StorageDirectory.analyzeStorage`, failed upgrade/rollback/finalize/checkpoint recovery, version-file-last invariants, directory locks, unformatted/nonexistent directories, version-upgrade checks, and `StorageInfo` read/write compatibility.
- DataNode lifecycle tests for daemon creation, `offerService` retry behavior, shutdown threading constraints, disk-error handling, block-report scheduling, registration storage id assignment, and inter-DataNode protocol proxies.
- Dataset tests for metadata file lookup, block input streams, temporary/RBW creation, append and recover-append, recover-close, checksum channel positioning, finalization/unfinalization, invalidation, disk health failures, block reports, snapshot unlinking, `checkAndUpdate` reconciliation cases, and visible-length semantics.
- Replica recovery tests for missing replicas, generation stamp bumps, min/max received byte validation, expected length checks, state transitions among `FINALIZED`, `RBW`, `RWR`, `RUR`, and `TEMPORARY`, and DataNode/NameNode agreement after recovery.
- Metrics tests for DataNode counters/rates, min/max reset, MBean registration/shutdown, and dataset capacity/remaining/DFS-used reporting.
- NameNode block-management tests for block report processing under lock, corrupt replica add/count/remove behavior, rack-aware target selection, replica deletion choices, scheduled block counts, and non-persistence of `DatanodeDescriptor`.
- Edit-log and fsimage tests for `logSync` concurrency, open/close/mkdir edit records, output stream iteration by journal type, failed storage restoration, checkpoint moves, format, and static string/byte readers.
- HTTP/JSP/HFTP tests for UGI extraction with and without delegation tokens, path/long/URL validation, content summary, delegation token servlet, checksum redirect/get servlet, file data redirects, and fsck servlet behavior.

## Chunk Boundary Notes

Lines 5834-11832 are chunk 2 of 3 for `hadoop-hdfs_0.21.0.xml`. The range begins in the tail of the `FSConstants` interface, after its class header and earlier constants, and ends inside the beginning of `org.apache.hadoop.hdfs.server.namenode.FSNamesystem`. The merge lane should reconcile this report with `subset-b-007469` and `subset-b-007471` before producing a final per-file research document.

### subset-b-007471: lines 11833-16220

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.21.0.xml lines 11833-16220

## Purpose

This chunk is a JDiff public API description for Hadoop HDFS 0.21.0. It covers the tail of `org.apache.hadoop.hdfs.server.namenode.FSNamesystem`, the main NameNode servlet/daemon/helper classes, NameNode metrics APIs, server-side HDFS RPC protocol types, command/value objects exchanged between NameNode, DataNode, backup/secondary NameNode, and several end-user tools.

The source is generated XML rather than Java implementation. The research signal is therefore the exposed API surface: packages, class/interface inheritance, method signatures, checked exceptions, public/protected fields, synchronization markers, and embedded Javadocs. Implementation-specific behavior below is inferred only where the Javadocs and signatures make the integration path explicit.

## Important APIs, Types, and Functions

The `org.apache.hadoop.hdfs.server.namenode` portion is centered on namespace management and the public RPC facade:

- The chunk begins inside `FSNamesystem`, which implements `FSConstants`, `FSNamesystemMBean`, and `FSClusterStats`. Exposed methods include namespace mutations (`setPermission`, `setOwner`, `concat`, `setTimes`, `createSymlink`, `delete`, `mkdirs`), block allocation and completion (`getAdditionalBlock`, `abandonBlock`, `completeFile`, `setReplication`, `markBlockAsCorrupt`), DataNode lifecycle (`registerDatanode`, `removeDatanode`, `processReport`, `blockReceived`, `refreshNodes`, `stopDecommission`), capacity/replication counters, generation stamp accessors, delegation-token methods, and edit-log master-key logging.
- `FSNamesystem` exposes core stateful collaborators as fields: `dir` (`FSDirectory`), `leaseManager`, `lmthread`, `replthread`, plus `LOG` and `auditLog`. This identifies it as the in-memory namespace/block manager behind the RPC layer.
- `GetImageServlet`, `ListPathsServlet`, and `StreamFile` are HTTP integration points for fsimage retrieval, filesystem metadata listing, and streaming file data through `DFSClient`.
- `INodeSymlink` extends `INode` and exposes symlink identity/value methods (`isLink`, `getLinkValue`, `getSymlink`) while reporting `isDirectory`.
- `LeaseManager` exposes lease lookup by path, lease count, lease-period tuning, and string rendering; `LeaseExpiredException` reports expired write leases.
- `NameNode` implements `NamenodeProtocols` and `FSConstants`. It exposes configuration/bootstrap (`format`, `initialize`, `loadNamesystem`, `createNameNode`, `main`), service lifecycle (`join`, `stop`), RPC/HTTP addresses, metrics, fsimage access, client file APIs, DataNode protocol APIs, backup-node checkpoint/journal APIs, safe mode, namespace save/roll/finalize/upgrade operations, quotas, corrupt-file reporting, symlink APIs, delegation tokens, and refresh operations for hosts, service ACLs, and user/group mappings.
- `NamenodeFsck` provides filesystem checking with status constants (`CORRUPT_STATUS`, `HEALTHY_STATUS`, `NONEXISTENT_STATUS`, `FAILURE_STATUS`) and fixing modes (`FIXING_NONE`, `FIXING_MOVE`, `FIXING_DELETE`).
- `SecondaryNameNode` is a runnable helper daemon for periodic metadata checkpoints. `SafeModeException`, `NotReplicatedYetException`, and `UnsupportedActionException` encode important NameNode state-machine failure modes.
- `UpgradeObjectNamenode` is the abstract NameNode-side distributed-upgrade hook with `processUpgradeCommand`, `startUpgrade`, `forceProceed`, and `getType`.

The `org.apache.hadoop.hdfs.server.namenode.metrics` package exposes operational monitoring:

- `FSNamesystemMBean` publishes stable JMX state: FS state, block/file counts, capacity used/remaining/total, replication queues, total load, and live/dead DataNode counts.
- `FSNamesystemMetrics` implements Hadoop `Updater`; `doUpdates` periodically samples `FSNamesystem` state, converts some values for metrics collectors, and exposes `numExpiredHeartbeats`.
- `NameNodeActivityMBean` wraps the metrics registry as the dynamic JMX bean for NameNode activity.
- `NameNodeMetrics` implements `Updater`, owns public metrics counters/rates for file creation, append, block-location lookup, rename, listing, delete, file-info lookup, add-block, symlink/link-target calls, edit-log transactions, syncs, batched transactions, block reports, safe-mode time, fsimage load time, corrupt blocks, and file counts returned by listings.

The `org.apache.hadoop.hdfs.server.protocol` package defines the low-level wire contracts:

- `DatanodeProtocol` is the DataNode-to-NameNode RPC contract. It includes registration, heartbeats returning `DatanodeCommand[]`, compact long-array block reports, block-received notifications with deletion hints, error reports, namespace-version handshakes, distributed upgrade commands, bad-block reports, and lease-recovery block synchronization commits. Its constants define error codes and DataNode command action codes (`DNA_TRANSFER`, `DNA_INVALIDATE`, `DNA_SHUTDOWN`, `DNA_REGISTER`, `DNA_FINALIZE`, `DNA_RECOVERBLOCK`, `DNA_ACCESSKEYUPDATE`).
- `NamenodeProtocol` is the secondary/backup NameNode contract. It exposes block-location export for a DataNode, access-key export, edit-log size and roll, fsimage roll, version requests, registration, checkpoint start/end, journal sizing, and edit-record journaling. Its constants describe notification/fatal errors, journal actions, and subordinate-node actions (`ACT_SHUTDOWN`, `ACT_CHECKPOINT`).
- `NamenodeProtocols` composes the full NameNode RPC surface by extending `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `RefreshAuthorizationPolicyProtocol`, and `RefreshUserToGroupMappingsProtocol`.
- `BlockCommand`, `BlockRecoveryCommand`, `BlockRecoveryCommand.RecoveringBlock`, `DatanodeCommand`, `KeyUpdateCommand`, `NamenodeCommand`, `ServerCommand`, and `UpgradeCommand` are serializable command objects sent as protocol responses. They carry block transfer/invalidation targets, recovery work and generation stamps, access-key updates, checkpoint actions, generic action codes, and upgrade status/version data.
- `BlocksWithLocations` and nested `BlockWithLocations` provide custom `Writable` serialization for arrays of block/location pairs to avoid the default RPC array overhead.
- `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, and `NodeRegistration` model the identity, layout version, registration ID, storage info, exported keys, role, checkpoint time, and namespace/build/distributed-upgrade version data exchanged during registration and handshakes.
- `InterDatanodeProtocol` supports replica recovery between DataNodes through `initReplicaRecovery` and `updateReplicaUnderRecovery`.
- `ReplicaRecoveryInfo` extends `Block` with original replica state. `DisallowedDatanodeException` reports registration/communication by a DataNode not permitted by include/exclude host policy.

The tools packages expose operational CLIs:

- `DelegationTokenFetcher` obtains a delegation token from the current NameNode and writes it to a supplied output stream/file.
- `DFSAdmin` extends `FsShell` and implements administrative commands: report, safe mode, namespace save, failed-storage restore checks/toggles, host refresh, upgrade finalization/progress, metadata save, topology printing, service ACL refresh, user-to-groups refresh, `run`, and `main`.
- `DFSck` implements `Tool` for filesystem consistency checks and optional repair of missing/corrupt blocks via none, move to `/lost+found`, or delete behavior.
- `HDFSConcat` exposes a CLI entry point for block-level file concatenation.
- `JMXGet` reads NameNode/DataNode MBeans using service, port, server, or local-VM URL settings and can print all values or retrieve one key.
- `OfflineImageViewer` processes an fsimage through an `ImageVisitor`, builds Commons CLI options, and provides a command-line `main`.

## Control Flow and Execution Model

The primary execution path is layered. `NameNode` owns the externally visible RPC server and HTTP server addresses, receives calls through the combined `NamenodeProtocols` interface, verifies requests/version where exposed, and delegates filesystem bookkeeping to `FSNamesystem`. `FSNamesystem` then mutates namespace and block state through `FSDirectory`, `LeaseManager`, generation stamps, replication queues, and DataNode descriptor/block maps. Several mutating `FSNamesystem` methods are marked synchronized in the JDiff (`setPermission`, `setOwner`, `setTimes`, `createSymlink`, `abandonBlock`, `markBlockAsCorrupt`, `registerDatanode`, `removeDatanode`, `processReport`, `blockReceived`, `datanodeReport`, `DFSNodesStatus`), while other public methods are unsynchronized at the API level and likely rely on internal or caller-side locking in the implementation.

Client write flow is visible through both `NameNode` and `FSNamesystem`: clients create or append files, request additional blocks, abandon failed block allocations, complete files, and renew leases. The `getAdditionalBlock` Javadoc notes that the previous blocks must have been reported and replicated before another block is issued, and may ask clients to try again later. Completion returns `FSNamesystem.CompleteFileStatus` internally and a boolean through `NameNode.complete`.

DataNode flow is modeled by `DatanodeProtocol`: a DataNode registers, sends periodic heartbeats with capacity/load values, uploads full block reports as compact `long[]` arrays, sends incremental block-received notifications, reports bad blocks or errors, and receives commands only as return values from those calls. Commands drive block transfer, invalidation, shutdown, re-registration, finalization, block recovery, and access-key updates.

Checkpoint and backup flow is modeled by `NamenodeProtocol`, `NamenodeRegistration`, and `CheckpointCommand`: a subordinate NameNode registers with the active NameNode, requests checkpoint start, receives a command with a `CheckpointSignature` and image-obsolete/return-image flags, finalizes the checkpoint with the same signature, and may receive journal records from the active NameNode via `journal`.

HTTP helper flow is separate from RPC. `GetImageServlet` retrieves image files through the NameNode web server, `ListPathsServlet` turns query parameters into a root/options map and services metadata listing requests, and `StreamFile` obtains a `DFSClient` from the servlet request before streaming data.

Metrics flow is push-oriented through Hadoop metrics `Updater`: `FSNamesystemMetrics.doUpdates` and `NameNodeMetrics.doUpdates` are called periodically by the metrics context, sample current NameNode/FSNamesystem values, and publish them to metrics/JMX registries. `NameNodeActivityMBean` exposes dynamic metrics, while `FSNamesystemMBean` is a stable JMX interface.

Tool execution is command-line oriented: `DFSAdmin.run`, `DFSck.run`, `DelegationTokenFetcher.go`, `OfflineImageViewer.go`, and the various `main` methods translate command-line inputs into RPC, filesystem, JMX, or fsimage-processing calls.

## State and Persistence Behavior

Persistent NameNode state is implied by the namespace and storage APIs. `FSNamesystem` tracks namespace edits directories, upgrade permissions, generation stamps, delegation-token master-key edits (`logUpdateMasterKey`), leases, replication state, corrupt replicas, block counts, DataNode registration IDs, and capacity counters. Its class-level documentation says the NameNode keeps two critical tables: filename to block sequence, which is stored on disk, and block to machine list, which is rebuilt when the NameNode starts.

`NameNode` exposes persistence operations that affect fsimage and edit-log lifecycle: `format`, `saveNamespace`, `getEditLogSize`, `rollEditLog`, `rollFsImage`, `getFsImageName`, `getFsImageNameCheckpoint`, `getFSImage`, checkpoint start/end, and `journal`. The API also carries distributed-upgrade state through `finalizeUpgrade`, `distributedUpgradeProgress`, `UpgradeObjectNamenode`, and `UpgradeCommand`.

Registration state persists across restarts through namespace IDs and registration IDs. `FSNamesystem.registerDatanode` documents that namespace ID is a persistent attribute and that DataNodes with inappropriate registration IDs are rejected. `DatanodeRegistration` combines `DatanodeID`, `StorageInfo`, and exported access keys; `NamenodeRegistration` combines `StorageInfo`, address, role, and checkpoint time; `NamespaceInfo` carries namespace handshake data including build and distributed-upgrade versions.

Block and replica state is transient but operationally critical. `BlocksWithLocations` serializes block-location state for balancing/secondary operations. `BlockCommand` and `BlockRecoveryCommand` carry work queues rather than durable state. `ReplicaRecoveryInfo` preserves the original replica state while recovery updates generation stamp and length. `commitBlockSynchronization` finalizes lease recovery and can close files, delete old blocks, and install new targets.

Metrics and JMX APIs expose sampled runtime state rather than persistent state. `NameNodeMetrics` fields are mutable metrics objects. `FSNamesystemMetrics` notes that capacity values are rounded to GB for collectors, while some long counters are cast to int because collectors may not handle long values.

Tooling persists or inspects external state: `DelegationTokenFetcher` writes tokens to a file/output stream, `DFSAdmin` can trigger namespace saves and metadata dumps, `DFSck` may move or delete corrupt files, `HDFSConcat` changes file block layout, `JMXGet` observes process MBeans, and `OfflineImageViewer` reads an fsimage without requiring a live NameNode.

## Dependencies and Integration Points

This chunk integrates with these HDFS and Hadoop subsystems:

- Core NameNode internals: `FSDirectory`, `LeaseManager`, `DatanodeDescriptor`, `FSImage`, `CheckpointSignature`, safe mode, generation stamps, replication queues, corrupt-replica tracking, and block maps.
- Public HDFS protocols: `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `NamenodeProtocols`, `InterDatanodeProtocol`, `VersionedProtocol`, and Hadoop IPC `Server`.
- HDFS protocol/value classes: `Block`, `LocatedBlock`, `LocatedBlocks`, `DirectoryListing`, `HdfsFileStatus`, `DatanodeID`, `DatanodeInfo`, `BlockListAsLongs`, `ContentSummary`, and `FsServerDefaults`.
- Security: delegation-token secret manager, exported access keys, `Token<DelegationTokenIdentifier>`, `UserGroupInformation`, service ACL refresh, user/group mapping refresh, and access-control exceptions.
- Storage and upgrade: `StorageInfo`, `NamespaceInfo`, `NamenodeRegistration`, `DatanodeRegistration`, `HdfsConstants.NamenodeRole`, `NodeType`, `UpgradeStatusReport`, `UpgradeCommand`, and edit-log journal actions.
- Servlet/HTTP tooling: `HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `DfsServlet`, NameNode Jetty/HTTP server, `DFSClient`, and Commons CLI for offline image viewer options.
- Hadoop metrics/JMX: `MetricsContext`, `MetricsRegistry`, `MetricsDynamicMBeanBase`, `MetricsTimeVaryingInt`, `MetricsTimeVaryingRate`, `MetricsIntValue`, and the stable `FSNamesystemMBean` interface.
- Java and Hadoop serialization: `Writable`, `DataInput`, `DataOutput`, arrays of protocol objects, compact block-report `long[]` encoding, and `IOException`-based RPC failure signaling.

## Risks and Edge Cases

- The chunk starts mid-`FSNamesystem` method metadata, so the class header and earlier methods must be reconciled with the previous chunk. Conclusions about the complete class should not be drawn from this slice alone.
- This XML exposes signatures and docs, not method bodies. Locking, validation order, exact persistence writes, and error handling need implementation-source confirmation before changing behavior.
- API synchronization is mixed. Several namespace/block/DataNode methods are marked synchronized, but many high-impact `NameNode` and `FSNamesystem` APIs are not. Callers and implementations must preserve the expected NameNode/FSNamesystem locking discipline.
- `concat` explicitly validates all arguments before moving blocks to avoid rollback complexity. Any implementation change that partially moves blocks before all preconditions pass risks namespace/block-map inconsistency.
- `setTimes` documents that edits are written but not flushed when needed, so callers relying on immediate durability must understand edit-log sync boundaries.
- `getAdditionalBlock` depends on previous blocks being reported and replicated; tests should cover retry-later behavior and under-replicated last-block cases.
- DataNode registration is sensitive to namespace ID, storage ID, host include/exclude policy, and layout version. Incorrect registration ID or `DisallowedDatanodeException` handling can strand valid DataNodes or admit invalid ones.
- Full block reports use a compact `long[]` representation where each block is represented by multiple longs. Producer/consumer encoding drift would corrupt the NameNode's block map.
- Command action integers are protocol-specific. Reusing `ServerCommand` action values across DataNode and NameNode protocols without checking the target protocol can trigger wrong behavior.
- Checkpointing depends on `CheckpointSignature`, image-obsolete flags, return-image flags, and journal action ordering. Mismatched signatures or stale checkpoint time can corrupt backup/secondary coordination.
- Metrics casts and capacity rounding are documented compatibility compromises; large clusters can lose precision in metrics output even if internal counters remain wider.
- `DFSAdmin.restoreFaileStorage` appears misspelled in the public API. Scripts or compatibility checks may depend on that exact method name.
- `NamenodeFsck` and `DFSck` can perform destructive fixes (`FIXING_DELETE`) or namespace-moving fixes (`FIXING_MOVE`), so CLI option parsing and dry-run/default behavior are safety-critical.
- `OfflineImageViewer` reads fsimage files directly; it must remain compatible with the image format produced by the corresponding NameNode version.

## Test Signals

Validation for this surface should come from subsystem tests rather than XML-only checks:

- NameNode namespace tests: permissions/owner/times/symlink changes, mkdir/delete/rename/concat, quotas, content summaries, corrupt-file reporting, safe-mode rejection, and edit-log/fsimage persistence across restart.
- Client write-path tests: create/append, add-block retry behavior before replication is sufficient, abandon-block cleanup, complete-file status transitions, lease renewal and `LeaseExpiredException`, pipeline update, fsync, and block synchronization during lease recovery.
- DataNode protocol tests: registration with new/existing storage IDs, wrong namespace/layout rejection, heartbeat command generation, block reports using compact `long[]`, incremental block-received notifications with deletion hints, bad-block reports, access-key update commands, and decommission include/exclude refresh.
- Checkpoint/backup tests: `NamenodeProtocol.register`, `startCheckpoint`, `endCheckpoint`, `journal`, edit-log roll, fsimage roll, checkpoint signatures, obsolete-image handling, and secondary NameNode shutdown/run lifecycle.
- Upgrade tests: `UpgradeObjectNamenode.processUpgradeCommand`, `startUpgrade`, `forceProceed`, `UpgradeCommand` serialization, distributed-upgrade progress, and finalization.
- Serialization compatibility tests: `BlockCommand`, `BlockRecoveryCommand`, `RecoveringBlock`, `BlocksWithLocations`, `BlockWithLocations`, `CheckpointCommand`, `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, `ReplicaRecoveryInfo`, `ServerCommand`, `UpgradeCommand`, and `KeyUpdateCommand` `write/readFields` round trips.
- Metrics/JMX tests: `FSNamesystemMBean` values, periodic `doUpdates`, NameNode activity MBean registration/shutdown, min/max reset, large-capacity rounding, and heartbeat-expiry metrics.
- HTTP/tool tests: image servlet downloads, list-path query defaults, stream-file reads, `DFSAdmin` command parsing and return codes, `DFSck` healthy/corrupt/missing statuses plus move/delete repair modes, delegation-token fetch output, `JMXGet` key lookup and print-all behavior, `HDFSConcat` argument handling, and `OfflineImageViewer` CLI option parsing plus fsimage visitor output.

## Chunk Boundary Notes

Lines 11833-16220 begin inside the `FSNamesystem` entry and end after the complete `OfflineImageViewer` class and closing `api` tag. The merge lane should combine this report with the preceding chunk for full `FSNamesystem` coverage and with earlier/later chunks for the complete generated JDiff API file.
