# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml lines 1-5762

## Scope and Artifact Type

This chunk is the opening 5,762 lines of the generated JDiff API description for `hadoop-hdfs 0.22.0`, produced by the JDiff Javadoc doclet on 2011-12-04. It is not implementation source; it records public/protected API signatures, inheritance, deprecation markers, declared exceptions, selected Javadoc text, and public/protected fields for HDFS classes. The source path is under `dev-support/jdiff`, so its direct purpose is API comparison/compatibility reporting rather than runtime behavior.

The chunk covers:

- `org.apache.hadoop.fs.Hdfs`
- major `org.apache.hadoop.hdfs` client and filesystem APIs
- `org.apache.hadoop.hdfs.protocol` through the beginning of `DataTransferProtocol`

Behavioral notes below are therefore contract-level research. Where control flow or persistence is described, it comes from API shape and embedded documentation, not method bodies.

## Purpose

This XML captures the Hadoop HDFS 0.22.0 public API surface used by compatibility tooling. It describes how end users, admin tools, and internal HDFS components are expected to interact with HDFS:

- filesystem facade methods for `AbstractFileSystem` and classic `FileSystem`
- direct DFS client operations against the NameNode and DataNodes
- HDFS configuration keys
- HDFS input/block reader APIs
- HTTP/HTTPS read-only filesystem access
- core protocol objects such as `Block`, block reports, DataNode identity/status, and the NameNode `ClientProtocol`

Because this is a JDiff snapshot, it is also a compatibility contract. Deprecated members remain visible and should be preserved or consciously migrated when comparing releases.

## Important APIs and Types

### `org.apache.hadoop.fs.Hdfs`

`Hdfs` extends `AbstractFileSystem` and exposes the newer filesystem facade for HDFS. Important operations include:

- create/open/delete/list/mkdir/rename through `createInternal`, `open`, `delete`, `listStatus`, `listLocatedStatus`, `listStatusIterator`, `mkdir`, and two `renameInternal` overloads
- metadata methods: `getFileStatus`, `getFileLinkStatus`, `getFileChecksum`, `getFileBlockLocations`, `getFsStatus`, `getServerDefaults`
- mutators: `setOwner`, `setPermission`, `setReplication`, `setTimes`, `setVerifyChecksum`
- symlink support: `supportsSymlinks`, `createSymlink`, `getLinkTarget`

The exception surface repeatedly includes `IOException` and `UnresolvedLinkException`, indicating that symlink-aware path resolution is part of the API contract.

### HDFS client/read classes

`BlockMissingException` is a public `IOException` used when a read encounters a block with no locations. It records a corrupted file name and offset through `getFile()` and `getOffset()`.

`BlockReader` extends `FSInputChecker`. It provides synchronized `read`, `skip`, `seek`, `seekToNewSource`, `readChunk`, `close`, `readAll`, `takeSocket`, and state query methods such as `hasSentStatusCode` and `getFileName`. Three static `newBlockReader` overloads show that a block reader can be built from a socket, file/block metadata, block token, offsets, checksum settings, and client identity. This is the client-to-DataNode data path boundary.

`DeprecatedUTF8` wraps Hadoop's deprecated `UTF8` type and provides constructors plus static `readString`/`writeString`. Its documentation says it should be treated as package-private to HDFS, but the JDiff surface records it as public.

`DFSInputStream` extends `FSInputStream` and negotiates with the NameNode and DataNodes to serve bytes from a named file. Key operations:

- stream state: `getFileLength`, `getCurrentDatanode`, `getCurrentBlock`, `getPos`, `available`
- read paths: single-byte `read`, buffer `read`, positional `read(position, buffer, offset, length)`
- source control: `seek`, `skip`, `seekToNewSource`
- protected `getBlockReader(...)`, which may reuse cached DataNode sockets or create new connections
- no mark/reset support: `markSupported` returns false; `reset` may throw `IOException`

`DFSClient.DFSDataInputStream` adapts `DFSInputStream` into `FSDataInputStream` and exposes `getCurrentDatanode`, `getCurrentBlock`, and `getVisibleLength`.

### `DFSClient`

`DFSClient` is the central programmatic client. It implements `FSConstants` and `Closeable`; docs say regular users should normally use `DistributedFileSystem`, which delegates to `DFSClient`. It uses `ClientProtocol` to communicate with the NameNode and direct DataNode connections for block I/O.

Covered methods include:

- NameNode setup: constructors and static `createNamenode(...)`
- lifecycle: synchronized `close`
- defaults/status: `getDefaultBlockSize`, `getBlockSize`, `getServerDefaults`, `getDefaultReplication`, `getDiskStatus`
- token handling: `getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, `stringifyToken`
- read path: `getBlockLocations`, three `open` overloads
- write/create path: multiple `create` overloads and `primitiveCreate`
- namespace operations: `createSymlink`, `getLinkTarget`, `setReplication`, `rename`, `concat`, `delete`, `exists`, `listPaths`, `getFileInfo`, `getFileLinkInfo`, `mkdirs`, `primitiveMkdir`
- checksum and metadata: `getFileChecksum` instance/static methods, `setPermission`, `setOwner`, `setTimes`
- admin/health operations: `reportBadBlocks`, missing/under-replicated/corrupt block counts, `datanodeReport`, `setSafeMode`, `refreshNodes`, `metaSave`, `finalizeUpgrade`, `distributedUpgradeProgress`

The embedded locking documentation says the lock order is `DFSClient` object, then lease checker, then individual `DFSOutputStream`. That is a high-value concurrency contract even though this chunk does not include those implementation types.

### Configuration and utility APIs

`DFSConfigKeys` extends `CommonConfigurationKeys` and contains a large set of public constants for HDFS configuration keys/defaults. The covered keys span block sizing, replication, stream buffers, NameNode/DataNode addresses, checkpointing, safe mode, permissions, delegation tokens, socket/cache behavior, DataNode storage, block reports, append support, HTTPS, block access tokens, image compression/transfer, plugins, Kerberos keytabs/users, web UGI, and NameNode name-cache threshold.

`HdfsConfiguration` extends `Configuration`. Its `init()` method exists to force class loading so static initialization adds deprecated keys and default resources before other classes use HDFS config. This is a compatibility and bootstrap integration point.

`DFSUtil` provides static path/byte utilities:

- `isValidName` checks HDFS path validity
- UTF-8 conversions: `bytes2String`, `string2Bytes`, `byteArray2String`
- path component splitting: `bytes2byteArray` overloads
- `locatedBlocks2Locations` converts protocol `LocatedBlocks` to filesystem `BlockLocation[]`

`DFSUtil.ErrorSimulator` is explicitly for JUnit error simulation, with methods to initialize, set, clear, and query simulated error events.

### Filesystem facades

`DistributedFileSystem` extends classic `FileSystem` and is the primary end-user HDFS implementation. It wraps `DFSClient` and exposes:

- initialization and path handling: `initialize`, `checkPath`, `makeQualified`, `getUri`, working/home directory methods
- read/write: `open`, `append`, `create`, `primitiveCreate`, `createNonRecursive`
- namespace mutations: `rename`, `concat`, `delete`, `mkdir`, `mkdirs`, `primitiveMkdir`, `setPermission`, `setOwner`, `setTimes`, `setQuota`
- metadata: block locations, content summary, file status, checksum, server defaults
- admin/status: `recoverLease`, status/disk status, raw capacity/used, block health counts, DataNode stats, safe mode, namespace save, restore failed storage, refresh nodes, finalize upgrade, distributed upgrade progress, `metaSave`
- delegation tokens: string and deprecated `Text` renewer overloads, renew, cancel

`DistributedFileSystem.DiskStatus` extends `FsStatus` but is deprecated in favor of `FsStatus`.

`HftpFileSystem` extends `FileSystem` and implements read-only HTTP access to HDFS via NameNode servlets such as `ListPathsServlet` and `FileDataServlet`. It supports URI setup, delegation tokens, `openConnection`, query rewriting, `open`, list/status/checksum/content summary operations, and has unsupported write-style methods such as `append`, `create`, `rename`, `delete`, and `mkdirs` in the API surface.

`HsftpFileSystem` extends `HftpFileSystem` for HTTPS. The nested `DummyHostnameVerifier` and `DummyTrustManager` explicitly bypass hostname and certificate checks.

`HDFSPolicyProvider` supplies HDFS protocol services for Hadoop security authorization.

### Protocol model and RPC APIs

`AlreadyBeingCreatedException` is an `IOException` thrown when a requested file is already open/under creation.

`Block` implements `Writable` and `Comparable`. It represents a primitive HDFS block identified by a long block id plus length and generation stamp. Important APIs:

- filename parsing: `isBlockFilename`, `filename2id`, `isMetaFilename`, static `getGenerationStamp`, static `getBlockId`
- mutable fields via `set`, `setBlockId`, `setNumBytes`, `setGenerationStamp`
- identity/serialization: `getBlockName`, `toString`, `write`, `readFields`, `writeId`, `readId`, `compareTo`, `equals`, `hashCode`
- public constants/patterns: `BLOCK_FILE_PREFIX`, `METADATA_EXTENSION`, `blockFilePattern`, `metaFilePattern`

`BlockListAsLongs` is an optimized block-report representation. It encodes finalized and under-construction replicas in a `long[]`, avoiding a `Block[]` allocation-heavy report. The documented layout is:

- count of finalized replicas
- count of under-construction replicas
- finalized triples: block id, length, generation stamp
- invalid marker triple of `-1`
- under-construction quadruples: block id, length, generation stamp, replica state

`BlockReportIterator` iterates this report while avoiding allocation on each iteration and exposes the current replica state.

`ClientDatanodeProtocol` extends `VersionedProtocol` and exposes `getReplicaVisibleLength(Block)`, used for block recovery/append visibility.

`ClientProtocol` is the main client-to-NameNode RPC contract. The covered methods define:

- block location reads: `getBlockLocations`
- server defaults: `getServerDefaults`
- file creation/appending: `create`, `append`
- replication/permission/owner mutation: `setReplication`, `setPermission`, `setOwner`
- write pipeline lifecycle: `abandonBlock`, `addBlock`, `complete`, `fsync`, `updateBlockForPipeline`, `updatePipeline`
- corruption reporting: `reportBadBlocks`
- namespace ops: deprecated `rename`, option-based `rename`, `concat`, `delete`, `mkdirs`, `getListing`
- lease and recovery: `renewLease`, `recoverLease`
- cluster stats/admin: `getStats`, `getDatanodeReport`, `getPreferredBlockSize`, `setSafeMode`, `saveNamespace`, `restoreFailedStorage`, `refreshNodes`, `finalizeUpgrade`, `distributedUpgradeProgress`, `metaSave`
- metadata: `getFileInfo`, `getFileLinkInfo`, `getContentSummary`, `setQuota`, `setTimes`
- symlinks: `createSymlink`, `getLinkTarget`
- delegation tokens: `getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`

Its public statistic indexes (`GET_STATS_CAPACITY_IDX`, `GET_STATS_USED_IDX`, `GET_STATS_REMAINING_IDX`, `GET_STATS_UNDER_REPLICATED_IDX`, `GET_STATS_CORRUPT_BLOCKS_IDX`, `GET_STATS_MISSING_BLOCKS_IDX`) define the shape of the `long[]` returned by `getStats`.

`DatanodeID` identifies a DataNode by name (`host:portNumber`), storage ID, info port, and IPC port. It implements `Writable` and `Comparable`; comparison is based on the string name only. `updateRegInfo` updates registration info but explicitly does not update storage ID.

`DatanodeInfo` extends `DatanodeID` and implements `org.apache.hadoop.net.Node`. It adds capacity/usage/remaining metrics, last update, active xceiver count, rack/network location, host name, admin state, parent and topology level. It serializes via `write`/`readFields`, has a static `read`, and reports decommission state through `NORMAL`, `DECOMMISSION_INPROGRESS`, and `DECOMMISSIONED`.

`DataTransferProtocol` begins at the end of the chunk. The visible constants include `DATA_TRANSFER_VERSION` and deprecated byte/int opcode/status constants (`OP_WRITE_BLOCK`, `OP_READ_BLOCK`, `OP_READ_METADATA`, `OP_REPLACE_BLOCK`, `OP_COPY_BLOCK`, `OP_BLOCK_CHECKSUM`, `OP_STATUS_SUCCESS`) in favor of newer `Op`/`Status` enums. The version documentation warns it should change when `DatanodeInfo` serialization changes, not only when operation semantics change.

## Control Flow and Lifecycle

The API contracts imply these primary flows:

1. User code calls `FileSystem`/`AbstractFileSystem` facade methods on `DistributedFileSystem` or `Hdfs`.
2. The facade delegates to `DFSClient`.
3. `DFSClient` uses `ClientProtocol` RPCs to the NameNode for namespace metadata, block placement, leases, tokens, quotas, and admin operations.
4. For reads, `DFSClient`/`DFSInputStream` obtains `LocatedBlocks`, selects DataNodes by location, and creates/reuses `BlockReader` connections for actual bytes.
5. For writes, the client creates/open-appends a namespace entry, requests blocks with `addBlock`, streams data to a DataNode pipeline, commits generation stamp/length, retries pipeline recovery through `updateBlockForPipeline`/`updatePipeline`, and calls `complete` until the NameNode reports the file closed and minimally replicated.
6. For block reports, DataNodes can encode many block records compactly via `BlockListAsLongs`; iteration reconstructs block information and replica states for NameNode processing.
7. Admin flows use `ClientProtocol` through `DFSClient`/`DistributedFileSystem` for safe mode, checkpoint/save namespace, failed storage restoration, node refresh, upgrade finalization/progress, and diagnostic metadata dumps.

The `ClientProtocol.create` documentation says a newly created file becomes visible for reads immediately, but cannot be deleted/re-created/renamed by other clients until completed or lease expiration. This is a key namespace and lease-control behavior.

## State and Persistence Behavior

This chunk names several persistent or durable state boundaries:

- HDFS namespace state is managed by the NameNode through `ClientProtocol`; `saveNamespace` writes the current namespace image to storage directories and resets the edit log, requiring superuser privilege and safe mode.
- `fsync` is the explicit API for writing metadata for an open file into persistent storage.
- `complete` persists final block generation stamp and length through NameNode coordination and may need retries until minimum replication is reached.
- `setReplication` updates desired replication immediately, but actual block replication/removal is asynchronous background maintenance.
- `setQuota` persists namespace and diskspace quota limits or resets.
- `setTimes`, `setOwner`, and `setPermission` persist inode metadata.
- `Block` serialization via `Writable`, `DatanodeID`/`DatanodeInfo` serialization, and `BlockListAsLongs` encode wire/persistent-compatible formats that other HDFS components depend on.
- Delegation token APIs expose token issuance, renewal, and cancellation state through NameNode/security services.
- Safe mode state is a NameNode state that blocks namespace writes and block replication/deletion; startup exit depends on configured block-report thresholds.
- `metaSave` appends diagnostic NameNode data structure dumps to a named file.

The JDiff artifact itself persists API state for compatibility comparison. It is generated from build classpaths and source paths, so changing public signatures or doclet configuration changes downstream compatibility outputs.

## Dependencies and Integration Points

Important dependencies visible in signatures:

- Hadoop common filesystem classes: `Path`, `FileSystem`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSInputStream`, `FSInputChecker`, `BlockLocation`, `FileStatus`, `FsStatus`, `FsServerDefaults`, `ContentSummary`, `FileChecksum`, `MD5MD5CRC32FileChecksum`
- Hadoop permissions and options: `FsPermission`, `Options.Rename`, `EnumSetWritable`
- Hadoop IPC and security: `VersionedProtocol`, `AccessControlException`, `UserGroupInformation`, `Token`, `SecretManager.InvalidToken`, `PolicyProvider`, `Service`
- HDFS protocol/server classes: `LocatedBlock`, `LocatedBlocks`, `DirectoryListing`, `HdfsFileStatus`, `FSConstants`, `UpgradeStatusReport`, `SafeModeException`, quota exceptions, `ReplicaState`
- Java networking and SSL: `Socket`, `InetSocketAddress`, `HttpURLConnection`, `HostnameVerifier`, `X509TrustManager`, `SSLSession`
- Utility/logging: `Progressable`, `Configuration`, `CommonConfigurationKeys`, `Log`, regex `Pattern`, `ThreadLocal`, `Random`
- HTTP integration: `HftpFileSystem`/`HsftpFileSystem` depend on NameNode web servlets for listing and file data.

This chunk is especially integrated with NameNode RPC compatibility. `ClientProtocol.versionID`, `ClientDatanodeProtocol.versionID`, DataTransfer version constants, and `Writable` serialization methods all form wire-level compatibility surfaces.

## Risks and Edge Cases

- This XML is generated API metadata. It cannot prove implementation behavior beyond signatures and Javadocs; research consumers should reconcile against Java sources when verifying exact control flow.
- Deprecated APIs are still public (`DFSClient(Configuration)`, old `rename` overloads, `DistributedFileSystem.DiskStatus`, `DataTransferProtocol` opcode constants, `Hftp`/`DFSClient` deprecated token overloads). Removing them can break compatibility reports and downstream callers.
- `HsftpFileSystem` exposes dummy hostname verifier and trust manager classes that bypass TLS verification. Even if intended for legacy behavior/testing, they are security-sensitive API surface.
- `ClientProtocol.getStats` returns a raw `long[]` keyed by public index constants. Ordering mistakes are easy and ABI-compatible but semantically dangerous.
- `BlockListAsLongs` has a compact custom layout with sentinel triples and variable record widths. Parser mistakes can corrupt block-report interpretation, especially around under-construction replicas and replica states.
- `DataTransferProtocol.DATA_TRANSFER_VERSION` documentation says serialization changes in `DatanodeInfo` require a version bump. That coupling is easy to miss when changing DataNode status fields.
- `DFSClient` lock-order documentation indicates deadlock risk if implementation or tests acquire `DFSClient`, lease checker, and output-stream locks in a different order.
- `ClientProtocol.complete` may return false and require retry; callers that treat one false return as fatal could break writes during DataNode failures or delayed replication.
- Safe mode has special threshold cases, including threshold greater than 1 preventing automatic exit. Admin tools must surface exact behavior.
- HDFS has single-writer semantics and byte-stream append semantics, explicitly not record append/mutation semantics. Any compatibility or migration work should preserve that contract.
- Symlink-aware APIs throw `UnresolvedLinkException` in many places; callers must not collapse it into generic missing-file behavior.

## Test Signals

Useful test signals for code using or changing APIs represented by this chunk:

- JDiff/API compatibility generation should still include all public/protected classes, fields, methods, deprecation strings, and declared exceptions expected for HDFS 0.22.0 comparisons.
- Filesystem facade tests should cover `Hdfs` and `DistributedFileSystem` create/open/delete/list/rename/mkdir/status/checksum/symlink methods, including `UnresolvedLinkException` paths.
- DFSClient integration tests should validate NameNode RPC delegation for create/open/append/rename/delete/list/checksum/quota/safe mode/token flows.
- Read-path tests should exercise `DFSInputStream` seeking, positional reads, DataNode failover via `seekToNewSource`, block-reader socket reuse, checksum verification toggles, and visible length.
- Write-path tests should exercise create, append, `addBlock`, `abandonBlock`, `complete` retry behavior, `fsync`, pipeline recovery generation-stamp updates, and lease recovery.
- Block-report tests should validate `BlockListAsLongs` encoding/iteration for finalized replicas, under-construction replicas, invalid sentinel handling, and replica state exposure without per-iteration allocation.
- Serialization tests should cover `Block`, `DatanodeID`, and `DatanodeInfo` round trips, especially after any field or ordering changes.
- Admin tests should cover safe mode transitions, namespace save preconditions, failed storage restore flag behavior, DataNode refresh/decommission reporting, upgrade finalization/progress, and `metaSave`.
- Security tests should cover delegation token get/renew/cancel and policy provider service mapping; HTTPS tests should explicitly decide whether dummy verifier/trust manager behavior is still acceptable.
- Configuration tests should verify `HdfsConfiguration.init()` loads defaults/deprecated keys and that representative `DFSConfigKeys` constants match XML/property expectations.
