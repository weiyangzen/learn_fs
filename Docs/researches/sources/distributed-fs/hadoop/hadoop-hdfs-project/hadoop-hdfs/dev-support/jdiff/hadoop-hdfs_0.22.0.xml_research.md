# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007472`: lines 1-5762, `Docs/researches/chunks/subset-b-007472_research.md`
- `subset-b-007473`: lines 5763-11806, `Docs/researches/chunks/subset-b-007473_research.md`
- `subset-b-007474`: lines 11807-17750, `Docs/researches/chunks/subset-b-007474_research.md`
- `subset-b-007475`: lines 17751-18589, `Docs/researches/chunks/subset-b-007475_research.md`

## Chunk Research

### subset-b-007472: lines 1-5762

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

### subset-b-007473: lines 5763-11806

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml lines 5763-11806

## Chunk Scope

This chunk is a JDiff XML API snapshot for Hadoop HDFS 0.22.0. It begins inside `org.apache.hadoop.hdfs.protocol.DataTransferProtocol`, after the deprecated integer operation/status constants, and covers the nested data-transfer protocol records and enums, HDFS protocol metadata records, block and delegation token APIs, balancer entry points, common storage and upgrade infrastructure, and the start of the DataNode public API surface. It ends at the opening of `SecureDataNodeStarter.SecureResources`, so the nested secure-resource details continue in a later chunk.

The file is documentation metadata, not executable source. Its purpose is to preserve the Java API contract: package names, public/protected classes and interfaces, inheritance, implemented interfaces, methods, parameters, exceptions, fields, synchronization flags, deprecation text, and Javadoc CDATA.

## Purpose and Major Areas

The span documents HDFS APIs that sit on the boundary between clients, DataNodes, NameNodes, storage directories, and security tokens:

- Data transfer protocol support for streaming block reads, writes, metadata reads, checksums, copy, replace, packet headers, pipeline acknowledgements, operation dispatch, and status codes.
- Client-visible filesystem metadata records such as `DirectoryListing`, `HdfsFileStatus`, `HdfsLocatedFileStatus`, `LocatedBlock`, `LocatedBlocks`, quota exceptions, unresolved symlink exceptions, and unregistered-node errors.
- HDFS constants and layout-version feature tracking, including safe-mode actions, datanode report filters, upgrade actions, and layout features such as quotas, append RBW directories, atomic rename, concat, symlinks, delegation tokens, and fsimage checksum/compression.
- Block-token and delegation-token classes for secure block access and HDFS delegation authentication.
- Cluster operational APIs for the balancer, generation stamps, block-under-construction states, replica states, startup modes, web/JSP helpers, storage directory state analysis, persistent storage identity, and distributed upgrade status.
- DataNode APIs for daemon lifecycle, NameNode service loops, disk-error handling, registration, inter-DataNode recovery, JMX reporting, data storage, dataset block operations, replica metadata, and secure daemon startup.

## Important APIs and Types

### `org.apache.hadoop.hdfs.protocol`

The chunk starts with deprecated `DataTransferProtocol` integer status constants (`OP_STATUS_ERROR`, `OP_STATUS_ERROR_CHECKSUM`, `OP_STATUS_ERROR_INVALID`, `OP_STATUS_ERROR_EXISTS`, `OP_STATUS_ERROR_ACCESS_TOKEN`, and `OP_STATUS_CHECKSUM_OK`) that point callers to the newer `DataTransferProtocol.Status` enum. The enclosing protocol is documented as the streaming protocol used to transfer data to and from DataNodes.

`DataTransferProtocol.BlockConstructionStage` enumerates write-pipeline phases: append setup, append recovery, data streaming, streaming recovery, close, close recovery, and create setup. Its `getRecoveryStage()` method depends on the enum ordering, with regular stages followed by matching recovery stages.

`DataTransferProtocol.Op` enumerates wire operations `WRITE_BLOCK`, `READ_BLOCK`, `READ_METADATA`, `REPLACE_BLOCK`, `COPY_BLOCK`, and `BLOCK_CHECKSUM`. It exposes a public byte `code`, plus `read(DataInput)` and `write(DataOutput)`, making enum ordinals/codes part of the stream format.

`DataTransferProtocol.PacketHeader` is a `Writable` header for block read/write pipeline packets. It exposes data length, last-packet flag, sequence number, block offset, packet length, `readFields` from `DataInput` or `ByteBuffer`, `write`, `putInBuffer`, equality/hash, and `sanityCheck(lastSeqNo)`, which validates packet sequence progression. `PKT_HEADER_LEN` is the fixed header-size contract.

`DataTransferProtocol.PipelineAck` is a `Writable` acknowledgement record containing a sequence number and an array of `Status` replies. `getNumOfReplies`, `getReply`, and `isSuccess` let callers verify every downstream DataNode in a write pipeline. The public constant is spelled `UNKOWN_SEQNO` in this API snapshot.

`DataTransferProtocol.Receiver` is an abstract dispatch base. `readOp(DataInputStream)` reads an op and checks protocol version; `processOp` dispatches to abstract handlers for `opReadBlock`, `opWriteBlock`, `opReplaceBlock`, `opCopyBlock`, and `opBlockChecksum`. These handlers receive blocks, offsets, lengths, clients, pipeline sizes, stages, generation stamps, DataNode identities, downstream target arrays, and block tokens.

`DataTransferProtocol.Sender` is the symmetric request writer. It has a lower-level `op(DataOutputStream, Op)` initializer and typed methods for read, write, replace, copy, and checksum operations. `DataTransferProtocol.Status` enumerates `SUCCESS`, the error statuses, and `CHECKSUM_OK`; it can be read and written to `DataInput`/`DataOutput` and written to an `OutputStream`.

`DirectoryListing` is a `Writable` partial-directory-listing container. It stores an array of `HdfsFileStatus` plus a remaining-entry count, supports iterative listing through `hasMore()` and `getLastName()`, and serializes with `readFields`/`write`.

`FSConstants` exposes public HDFS constants for minimum write blocks, block invalidation chunk size, quota sentinel values, heartbeat and block-report intervals, lease timings, path length/depth limits, buffer sizes, default block size, checksum size, write packet size, replication, data socket size, URI scheme, and layout version. Nested enums cover datanode reports (`ALL`, `LIVE`, `DEAD`), safe-mode actions (`SAFEMODE_LEAVE`, `SAFEMODE_ENTER`, `SAFEMODE_GET`), and upgrade actions (`GET_STATUS`, `DETAILED_STATUS`, `FORCE_PROCEED`).

`HdfsFileStatus` is the over-the-wire file-status record. It is `Writable` and carries length, directory flag, replication, block size, modification and access times, permission, owner, group, local path bytes, and optional symlink bytes. Its accessors expose local and full names as strings/bytes and full `Path` values. `HdfsLocatedFileStatus` extends it with a `LocatedBlocks` payload.

`LayoutVersion` tracks layout-version compatibility. `getString`, `supports(Feature,int)`, and `getCurrentLayoutVersion` expose feature checks, while `LayoutVersion.Feature` records feature gates including namespace quota, access time, diskspace quota, sticky bit, append RBW directory, atomic rename, concat, symlinks, delegation token, fsimage compression/checksum, release-layout removals, unused slots, and reserved release ranges.

`LocatedBlock` pairs a `Block` with `DatanodeInfo[]`, start offset, corruption flag, and block token. `LocatedBlocks` represents a file's block list plus file length, under-construction flag, last located block, and last-block-complete flag. It supports lookup by index, block count, binary search by offset through `findBlock`, range insertion, insert index calculation, and `Writable` serialization.

Quota and path exceptions include `QuotaExceededException` with protected `pathName`, `quota`, and `count`, plus `DSQuotaExceededException` and `NSQuotaExceededException` subclasses with custom messages. `RecoveryInProgressException` marks concurrent replica recovery. `UnregisteredNodeException` covers unknown DataNode registrations or conflicting DataNode identities. `UnresolvedPathException` extends `UnresolvedLinkException` and can return a resolved `Path` for symlink handling.

### Security Tokens

`org.apache.hadoop.hdfs.security.token.block.BlockKey` extends Hadoop's `DelegationKey` and represents keys used to generate and verify block tokens.

`BlockTokenIdentifier` extends `TokenIdentifier`. It exposes token kind, effective user, expiry date, key id, user id, block id, allowed access modes, byte serialization, equality/hash, and `Writable` read/write. `BlockTokenSecretManager` can run in master or slave mode. Master-mode APIs export, update, and roll keys; slave-mode APIs consume exported keys. It generates block tokens for current or specified users, checks user/block/access-mode authorization, sets token lifetime, creates identifiers, creates passwords, and retrieves passwords.

`BlockTokenSecretManager.AccessMode` enumerates `READ`, `WRITE`, `COPY`, and `REPLACE`, matching the data-transfer operations that can be authorized. `BlockTokenSelector` selects an HDFS block token from a token collection. `ExportedBlockKeys` is a `Writable` key bundle containing token-enable state, key-update interval, token lifetime, current key, and all keys. `InvalidBlockTokenException` represents failed access-token verification.

`DelegationTokenIdentifier` is the HDFS-specific subclass of `AbstractDelegationTokenIdentifier` with `HDFS_DELEGATION_KIND`. `DelegationTokenSecretManager` extends the abstract delegation-token secret manager and persists token/key state through fsimage and edit-log hooks: load/save secret-manager state, add persisted tokens, update persisted master keys, update renewals, update cancellations, query token expiry, count keys, and log master-key updates through the namesystem. `DelegationTokenSelector` is the HDFS-specific selector.

### Balancer and Common HDFS State

`Balancer` is a `Tool` with `main`, `run`, `getConf`, and `setConf`. It exposes return codes for success, already running, no movable block, no progress, I/O exception, and illegal arguments, plus `MAX_NUM_CONCURRENT_MOVES`. The Javadoc documents threshold-driven balancing, iteration limits, bandwidth configuration, output-file monitoring, single-instance protection, and exit conditions.

`GenerationStamp` is a comparable long-backed primitive. It starts at `FIRST_VALID_STAMP`, has a special `GRANDFATHER_GENERATION_STAMP` for older blocks, and synchronizes `nextStamp()` while providing comparison, equality, and hash behavior.

`HdfsConstants` provides internal timeout constants and nested enums. `BlockUCState` models `COMPLETE`, `UNDER_CONSTRUCTION`, `UNDER_RECOVERY`, and `COMMITTED`. `NamenodeRole` includes `ACTIVE`, `BACKUP`, `CHECKPOINT`, and `STANDBY`; `NodeType` distinguishes NameNode and DataNode; `ReplicaState` serializes `FINALIZED`, `RBW`, `RWR`, `RUR`, and `TEMPORARY`; `StartupOption` covers format, regular start, backup, checkpoint, upgrade, rollback, finalize, and import modes.

`JspHelper` contains static and instance helper methods for HDFS web UIs: selecting a best DataNode, streaming block bytes as ASCII, generating table markup, sorting node lists, printing path links and navigation forms, parsing chunk-size inputs, building version tables, validating paths/longs/URLs, deriving the default web user, extracting `UserGroupInformation` and delegation tokens from requests, and building URL parameters.

`StorageInfo` is a `Writable` holder for layout version, namespace ID, and creation time. `Storage` extends it with storage-directory management: iteration by optional directory type, directory listing, adding directories, checking pre-upgradable layouts, validating upgrade support, reading/writing common fields, renaming and deleting directories, writing all `VERSION` files, unlocking all directories, lock-support checks, build version, registration ID, and 0.20.203 layout detection. Its constants define important storage directory/file names and upgrade-version cutoffs.

`Storage.StorageDirectory` models one storage root. It exposes the root, directory type, `VERSION` file read/write, directory clearing, paths for `current`, `previous`, `previous.tmp`, `removed.tmp`, `finalized.tmp`, `lastcheckpoint.tmp`, and `previous.checkpoint`, storage-state analysis, failed-transition recovery, and filesystem locking. `Storage.StorageState` enumerates normal, not-formatted, non-existent, complete/recover upgrade, complete/recover rollback, complete finalize, and complete/recover checkpoint states.

`Upgradeable`, `UpgradeManager`, `UpgradeObject`, `UpgradeObjectCollection`, and `UpgradeStatusReport` define distributed upgrade orchestration. Upgrade objects report target layout version, node type, description, 0-100 percent status, start/complete commands, and status reports. `UpgradeManager` tracks current upgrades, upgrade state/version, and a broadcast `UpgradeCommand`. `UpgradeStatusReport` is `Writable` and records version, percent status, finalization state, text output, and string form.

`Util` is a small common helper with current time and URI conversion methods for strings, files, and string collections.

### DataNode and Dataset APIs

`DataNode` extends `Configured` and implements `InterDatanodeProtocol`, `ClientDatanodeProtocol`, `FSConstants`, `Runnable`, and `DataNodeMXBean`. It exposes address helpers, socket creation, static singleton lookup, inter-DataNode protocol proxy creation, NameNode/self addresses, `DatanodeRegistration`, storage-ID assignment, lifecycle methods (`shutdown`, `run`, `runDatanodeDaemon`, `instantiateDataNode`, `createDataNode`, `main`, `secureMain`), disk-error checks, the NameNode `offerService` loop, block-received notification, block-report scheduling, test-only dataset access, block recovery methods, protocol version, replica visible length, streaming address, and JMX getters.

Important `DataNode` state fields in this API snapshot are public: `namenode`, `data`, `dnRegistration`, `blockScanner`, `blockScannerThread`, and `ipcServer`, along with public static `LOG`, `DN_CLIENTTRACE_FORMAT`, and `EMPTY_DEL_HINT`. `DataNodeMXBean` mirrors operational getters for version, RPC port, HTTP port, NameNode address, and per-volume information; `getVolumeInfo` returns a JSON map keyed by volume name.

`DataStorage` extends `Storage` with DataNode-specific storage ID and storage fields. `DirectoryScanner` is documented as a periodic scanner of data directories for block and metadata files.

`FSDataset` is the concrete block-store manager for DataNodes and implements the storage-facing behavior that `FSDatasetInterface` generalizes. Public APIs cover metadata file discovery (`getMetaFile`, `metaFileExists`, `getMetaDataLength`, `getMetaDataInputStream`), block file discovery (`findBlockFile`, `getBlockFile`, `getFile`), stored block lookup, capacity/remaining/used/failed-volume reporting, block length and input streams, temporary input streams, copy-on-write unlinking, append and recovery variants, RBW/temp replica creation, CRC-channel adjustment, finalize/unfinalize, block reports, validity checks, invalidation, data-dir health checks, shutdown, storage-info text, disk-vs-memory reconciliation through `checkAndUpdate`, replica lookup, replica recovery initialization/update, and visible-length lookup. `METADATA_EXTENSION` and `METADATA_VERSION` define metadata-file format markers.

`FSDatasetInterface` is the storage abstraction used by DataNode. It defines the same essential block-data, metadata, replica, append/recovery, report, invalidation, resource, shutdown, and recovery operations for implementations such as disk-backed `FSDataset` and simulated datasets. Nested `BlockInputStreams`, `BlockWriteStreams`, and `MetaDataInputStream` group data/checksum streams and metadata-stream length.

`Replica` abstracts DataNode replica metadata: block id, generation stamp, replica state, bytes received, bytes on disk, and reader-visible length. `ReplicaInfo` is an abstract `Block` subclass implementing `Replica`, used by DataNodes to maintain replica metadata. `ReplicaNotFoundException` reports a missing local replica. `SecureDataNodeStarter` implements `org.apache.commons.daemon.Daemon` and obtains privileged resources before starting a secure DataNode; the chunk stops just as nested `SecureResources` begins.

## Control Flow and Lifecycle

Data transfer flow is explicitly split between `Sender` and `Receiver`. A sender writes an operation and operation-specific payload, including block identity, client string, offsets/lengths, generation stamps, stage, pipeline topology, and block tokens. A receiver reads and version-checks the operation with `readOp`, then `processOp` dispatches to the corresponding abstract operation handler. Streaming data then moves in `PacketHeader`-framed packets, and write pipelines return `PipelineAck` values whose reply array must be checked for all-success status.

Write-pipeline lifecycle is modeled by `BlockConstructionStage`: create, append, streaming, close, and matching recovery variants. Recovery stages must preserve enum order because `getRecoveryStage()` depends on the regular/recovery pairing. Replica lifecycle is modeled separately by `ReplicaState` (`TEMPORARY`, `RBW`, `RWR`, `RUR`, `FINALIZED`) and block-under-construction lifecycle by `BlockUCState` (`UNDER_CONSTRUCTION`, `UNDER_RECOVERY`, `COMMITTED`, `COMPLETE`).

Client metadata flow uses paging and block-location containers. A NameNode can return `DirectoryListing` pages with remaining-entry counts and last-name cursors. File listings use `HdfsFileStatus` and optionally `HdfsLocatedFileStatus`; block-location reads use `LocatedBlocks`, whose sorted block list supports offset lookup and insertion of new ranges.

Security-token flow has two layers. Block tokens authorize direct DataNode block operations and are generated/validated by `BlockTokenSecretManager` against block id, user id, and access mode. Delegation tokens authorize HDFS clients and persist through NameNode fsimage/edit-log state via `DelegationTokenSecretManager` load, save, renewal, cancellation, and master-key update APIs.

DataNode lifecycle is daemon-oriented. Static factory methods instantiate and optionally start a single DataNode; `run` keeps retrying `offerService()` until shutdown; `offerService` repeatedly calls NameNode functions; `scheduleBlockReport` forces block-report timing; disk checks can react to exceptions or run proactively. Secure startup first acquires privileged resources, then hands them to normal DataNode startup.

Dataset flow moves blocks between storage states. Replication/relocation creates temporary replicas; client writes create RBW replicas; append and close recovery bump generation stamps and verify expected lengths; finalization requires the `Block` length to match bytes written; unfinalization deletes temporary files; invalidation deletes blocks reported obsolete by the NameNode; block reports serialize the full local block map back to the NameNode.

Storage and upgrade lifecycle is filesystem-state based. `StorageDirectory.analyzeStorage` classifies directory state from marker directories; `doRecover` completes or recovers failed transitions; `Storage.writeAll` writes `VERSION` metadata; `unlockAll` releases locks. Upgrade managers collect layout-specific `Upgradeable` implementations, initialize/start/complete upgrades, and broadcast `UpgradeCommand`s until status reports reach completion and finalization.

## State and Persistence Behavior

Several types define stable binary wire or disk formats through Hadoop `Writable`: `PacketHeader`, `PipelineAck`, `DirectoryListing`, `HdfsFileStatus`, `HdfsLocatedFileStatus`, `LocatedBlock`, `LocatedBlocks`, `BlockTokenIdentifier`, `ExportedBlockKeys`, `StorageInfo`, `UpgradeStatusReport`, and replica-state/status enums with explicit read/write helpers. Token identifiers additionally expose raw byte forms used for password generation.

Persistent HDFS namespace and storage state appears in layout version, namespace ID, creation time, storage ID, generation stamps, `VERSION` files, storage directory marker directories, block metadata files, fsimage token state, and edit-log token renewal/cancel/master-key records. `Storage` constants and `LayoutVersion.Feature` values are compatibility-sensitive because older directories and images are interpreted through them.

Runtime DataNode state includes NameNode RPC proxy, DataNode registration, dataset implementation, block scanner and scanner thread, IPC server, socket configuration, disk health, block reports, replica maps, data/checksum streams, recovery IDs, visible lengths, and JMX-visible volume information. The public-field exposure in this API snapshot makes compatibility and tests sensitive to field names and types, not just methods.

Security state is split between master/slave block-key modes, exported key bundles, current and historical keys, token lifetimes, token expiry times, delegation key caches, and persisted token records. Many delegation-token secret-manager APIs are synchronized, indicating that concurrent renewal/cancel/load/save paths are expected.

External state includes live HDFS cluster balance, balancer output logs, NameNode block and datanode reports, HTTP/JSP request parameters, delegation token URL parameters, storage directory locks, local disk block files and checksum files, and privileged sockets/resources for secure DataNode startup.

## Dependencies and Integration Points

The chunk depends on HDFS protocol classes (`Block`, `DatanodeID`, `DatanodeInfo`, `BlockListAsLongs`, `ClientDatanodeProtocol`, `LocatedBlocks`), server protocol classes (`DatanodeProtocol`, `DatanodeRegistration`, `InterDatanodeProtocol`, `BlockRecoveryCommand.RecoveringBlock`, `ReplicaRecoveryInfo`, `UpgradeCommand`, `NodeRegistration`), and DataNode classes (`FSDatasetInterface`, `Replica`, `ReplicaInfo`, `ReplicaInPipelineInterface`, `DataBlockScanner`).

It integrates with Hadoop core APIs: `Configuration`, `Configured`, `Tool`, `Writable`, `Token`, `TokenIdentifier`, `SecretManager`, delegation-token base classes, `DelegationKey`, `UserGroupInformation`, `Text`, `Daemon`, `DiskChecker`, `NetUtils`, `Server`, and filesystem classes such as `Path`, `FsPermission`, and `UnresolvedLinkException`.

Java and platform dependencies include `DataInput`, `DataOutput`, `DataInputStream`, `DataOutputStream`, `OutputStream`, `ByteBuffer`, `InputStream`, `FilterInputStream`, `File`, `URI`, `Socket`, `InetSocketAddress`, collections (`List`, `Collection`, `EnumSet`, `SortedSet`, `Iterator`), servlet request/response-style web helpers implied by JSP utilities, `javax.crypto.SecretKey`, `org.apache.commons.daemon.Daemon`, and `org.apache.commons.logging.Log`.

Operational integration points are direct DataNode streaming sockets, NameNode RPC, inter-DataNode RPC, HDFS web UI/JSPs, JMX through `DataNodeMXBean`, storage directories on local disks, fsimage/edit logs for token persistence, block-token distribution from master to slave managers, balancer scripts and cluster configuration, and secure daemon launch through privileged resources.

## Risks and Edge Cases

- Wire compatibility is fragile: operation codes, status values, packet header length, enum read/write behavior, and `Writable` field order must remain compatible across clients and DataNodes.
- `BlockConstructionStage.getRecoveryStage()` depends on enum ordering. Reordering values can silently break recovery-stage mapping.
- `PipelineAck.isSuccess()` must inspect every reply. Treating the first success as global success would miss downstream pipeline failures.
- Packet sequencing and offsets are correctness-critical. `PacketHeader.sanityCheck` should catch sequence regressions or gaps, but tests need to cover last-packet and offset edge cases.
- Several APIs expose deprecated constants or misspelled names such as `UNKOWN_SEQNO`; compatibility code may need to retain these exact names.
- Token security depends on key rollout, token lifetime, access modes, user/block binding, and synchronized persistence. Incorrect master/slave mode use or stale exported keys can reject valid clients or allow unintended access.
- Delegation-token persistence crosses fsimage and edit logs. Load/save/renew/cancel ordering bugs can resurrect canceled tokens or lose renewals after restart.
- Layout-version and storage-state handling is high risk. Incorrect `StorageDirectory` recovery can delete or promote the wrong marker directory during upgrade, rollback, finalize, or checkpoint recovery.
- Public DataNode fields make refactoring risky because tests or external code may directly inspect `namenode`, `data`, `dnRegistration`, `blockScanner`, or `ipcServer`.
- DataNode shutdown is documented as callable only from the offer-service thread to avoid deadlock; tests should exercise lifecycle calls from the intended thread.
- Dataset recovery methods depend on generation stamp and expected length validation. Accepting mismatched lengths can corrupt replicas; over-strict validation can prevent legitimate lease recovery.
- `adjustCrcChannelPosition` intentionally rewinds checksum output to overwrite the last checksum, which is sensitive to checksum size and partial-chunk appends.
- Balancer behavior is live-cluster sensitive. Very small thresholds may never converge under concurrent writes/deletes, and multiple balancer instances are prohibited.
- JSP helper validation and URL parameter handling are security-sensitive because they process paths, token strings, long values, and URLs from web requests.
- Storage locking may not be supported on all filesystems; `isLockSupported` and lock/unlock failure handling need platform coverage.

## Test Signals

Useful tests for code represented by this API chunk would include:

- JDiff/API compatibility tests asserting the documented classes, methods, fields, exceptions, visibility, synchronization flags, enum names, deprecation text, and misspelled compatibility constants remain present.
- Serialization round trips for `PacketHeader`, `PipelineAck`, `DirectoryListing`, `HdfsFileStatus`, `HdfsLocatedFileStatus`, `LocatedBlock`, `LocatedBlocks`, `BlockTokenIdentifier`, `ExportedBlockKeys`, `StorageInfo`, `UpgradeStatusReport`, and `ReplicaState`.
- Data-transfer protocol tests for op code read/write, protocol-version rejection, sender/receiver dispatch to every operation handler, packet sequence sanity, last-packet handling, checksum status, and multi-hop pipeline acknowledgements.
- Write and recovery tests for every `BlockConstructionStage`, including append recovery, streaming recovery, close recovery, generation-stamp changes, expected-length mismatch, visible length during recovery, and transition to finalized replicas.
- Directory and file-status tests for partial listings, remaining-entry counts, empty listings, local name bytes, full path construction, symlink status, located status serialization, and located-block offset lookup/insertion.
- Quota and path exception tests for namespace and diskspace messages, path-name injection into quota messages, unresolved symlink resolution, unregistered node diagnostics, and recovery-in-progress errors.
- Layout-version tests for each `LayoutVersion.Feature`, reserved/unused layout entries, current-layout reporting, and compatibility decisions for 0.20.203 and pre-generation-stamp layouts.
- Block-token tests for master key export/update, slave key import, token generation for current and explicit users, access checks for each `AccessMode`, expired tokens, wrong block IDs, wrong users, stale key IDs, and selector behavior.
- Delegation-token tests for create, renew, cancel, expiry lookup, fsimage save/load, edit-log replay methods, master-key logging, key counts, and concurrency around synchronized methods.
- Balancer tests for argument validation, threshold boundaries, single-instance detection, no-move/no-progress exit codes, I/O failure exit code, configuration propagation, and maximum concurrent move enforcement.
- Storage tests for `VERSION` read/write, directory state analysis for every `StorageState`, recovery from `previous.tmp`, `removed.tmp`, `finalized.tmp`, and checkpoint markers, lock/unlock behavior, unsupported locks, storage directory filtering by type, and upgrade-version checks.
- DataNode lifecycle tests for address helpers, socket creation mode, daemon factory methods, `offerService` retry behavior, shutdown-thread constraints, disk-error handling, block-report scheduling, JMX getters, and secure startup resource handoff.
- FSDataset tests for metadata file discovery, block input stream offsets, temp stream handling, capacity/remaining/failed-volume accounting, copy-on-write unlinking, create temporary/RBW replicas, append/recover append/recover close, finalize/unfinalize, invalidation, block reports, disk reconciliation, replica lookup, recovery initialization/update, and resource sufficiency.

## Cross-Chunk Notes

This chunk begins after the start of `DataTransferProtocol`, so earlier chunks contain the interface declaration, protocol version fields, and any operation constants before line 5763. It ends immediately after the declaration of `SecureDataNodeStarter.SecureResources`, so downstream chunks should capture the secure resource fields/methods and any remaining DataNode package APIs. The merge lane should treat this as one slice of a larger JDiff XML file and reconcile repeated HDFS protocol, storage, security, and DataNode themes with adjacent chunks before producing a final per-file report.

### subset-b-007474: lines 11807-17750

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml lines 11807-17750

## Purpose

This chunk is a generated JDiff API snapshot for Hadoop HDFS 0.22.0, not implementation source. It records public/protected API metadata for the tail of the DataNode package, DataNode metrics, much of the NameNode server package, NameNode metrics, HDFS server protocols, and the opening of `org.apache.hadoop.hdfs.tools.DelegationTokenFetcher`. The useful research surface is therefore the compatibility contract: class/interface names, inheritance, method signatures, fields, synchronization flags, exceptions, deprecation markers, and Javadoc behavior notes.

The covered APIs describe the classic HDFS control plane. DataNodes register, heartbeat, report blocks, receive block commands, and participate in block recovery. NameNode/FSNamesystem maintain namespace and block maps, expose client and service RPCs, run checkpoints/upgrades, manage leases and safe mode, publish metrics/JMX state, and serve HTTP helper endpoints for HFTP/checkpoint/fsck/token flows. Backup and secondary NameNodes use subordinate NameNode protocols to checkpoint or journal active namespace state.

## Important APIs, Types, and Functions

- `SecureDataNodeStarter.SecureResources` exposes secure DataNode startup resources: a streaming `ServerSocket` and Jetty `SelectChannelConnector`. It is the handoff object for privileged socket/listener setup before the DataNode drops into normal runtime.
- `UpgradeObjectDatanode` extends `UpgradeObject` and implements `Runnable`. It identifies itself as a DataNode upgrade object, exposes the owning `DataNode`, runs `doUpgrade()`, and returns an `UpgradeCommand` from `completeUpgrade()` so DataNodes can keep reporting completion while other nodes are still upgrading.
- DataNode metrics APIs include `DataNodeActivityMBean`, `DataNodeMetrics`, and `FSDatasetMBean`. `DataNodeMetrics` is an `Updater` with public counters/rates for bytes, blocks, replication/removal/verification, local/remote reads/writes, volume failures, block operation latencies, heartbeats, and block reports. `FSDatasetMBean` publishes storage capacity, DFS-used bytes, remaining bytes, storage ID, and failed volume count.
- `BackupNode` extends `NameNode` and overrides address/initialization behavior while implementing subordinate NameNode RPC operations: registration, checkpoint start/end, journal application, block listing, and safe mode handling. Its docs distinguish checkpoint-only nodes from backup nodes that keep a live namespace image synchronized by journal records.
- `BackupStorage` extends `FSImage` for backup/checkpoint storage handling and layout upgrade checks.
- `BlockManager` maintains block-related cluster information for `FSNamesystem`. The visible method `processReport(DatanodeDescriptor, BlockListAsLongs)` updates DataNode-to-block and block-to-DataNode mappings from full block reports; docs note some methods require the `FSNamesystem` lock.
- `BlockPlacementPolicy` is the abstract replica placement contract. It verifies rack placement, chooses a replica deletion candidate, initializes from `Configuration`, `FSClusterStats`, and `NetworkTopology`, and has a `getInstance(...)` factory using `dfs.block.replicator.classname`. `BlockPlacementPolicyDefault` implements the default rack-aware placement strategy.
- HTTP servlets in the NameNode package include `CancelDelegationTokenServlet`, `GetDelegationTokenServlet`, `RenewDelegationTokenServlet`, `ContentSummaryServlet`, `FileChecksumServlets.GetServlet`, `FileChecksumServlets.RedirectServlet`, `FileDataServlet`, `FsckServlet`, `GetImageServlet`, `ListPathsServlet`, and `StreamFile`. They expose HFTP/Web UI/checkpoint helper surfaces for metadata, data redirects, checksums, fsck, image retrieval, token management, path listing, and file streaming.
- `CheckpointSignature` is a `WritableComparable` checkpoint identity object with comparison, equality, hash, and serialization methods. `CheckpointCommand` carries that signature plus image-obsolete and return-image flags for subordinate checkpoint control.
- `DatanodeDescriptor` extends DataNode identity/status behavior and tracks DataNode liveness, key update need, volume failure count, scheduled blocks, and registration updates. `BlockTargetPair` couples a block with replication targets.
- `CorruptReplicasMap` tracks corrupt replicas with add/count/size operations.
- `FSEditLog` represents namespace edit logging. The visible `logSync()` documentation describes a double-buffered concurrency design using per-thread transaction IDs, an `isSyncRunning` flag, synchronized buffer swapping, unsynchronized flush, and notification after sync completion. It also logs open files, close files, mkdirs, buffer capacity changes, and exposes output streams by journal type.
- `FSImage` extends common `Storage` and handles checkpointing and namespace edit logging. It owns `namesystem`, `checkpointTime`, `editLog`, `imageDigest`, `newImageDigest`, `removedStorageDirs`, and volatile `ckptState`; it reads/writes storage fields, saves current image plus empty journal, moves `current` to `lastcheckpoint.tmp`, moves `lastcheckpoint.tmp` to `previous.checkpoint`, formats storage, and returns edit/image files.
- `FSImageSerialization` exposes public static FSImage deserializers for strings, bytes, and path components. The path-component reader avoids String conversion/copying and is public partly for Offline Image Viewer integration.
- `FSInodeInfo` exposes `getFullPathName()` for pluggable block placement policies.
- `FSNamesystem` is the central namespace/block manager and implements `FSConstants`, `FSNamesystemMBean`, `FSClusterStats`, and `NameNodeMXBean`. Its visible API spans namespace directory discovery, permission/owner/time/symlink changes, concat, replication, add/abandon/complete block paths, corrupt block marking, delete/mkdir/listing, DataNode registration and reports, replication work scheduling, decommission state, capacity/load/accounting metrics, generation stamps, delegation tokens, master-key edit logging, JMX state, and shutdown.
- `LeaseManager` manages leases for open file writes and documents the lease recovery algorithm: NameNode chooses a primary DataNode, the primary obtains a new generation stamp, gathers replica info, computes minimum length, updates replicas, acknowledges the NameNode, and the NameNode updates block info, removes the lease, and commits edits.
- `NameNode` implements `NamenodeProtocols` and `FSConstants`. It is the RPC/HTTP server facade over `FSNamesystem`, exposing client RPC, DataNode protocol RPC, subordinate NameNode protocol RPC, service RPC address handling, startup modes, formatting, safemode, checkpoint/edit-log rolling, DataNode registration/heartbeat/block reports, delegation tokens, refresh operations, and admin entry points. Protected state includes `namesystem`, role, service RPC server/address, client RPC address, HTTP server/address, stop flag, and `NamenodeRegistration`.
- `NamenodeFsck` provides DFS consistency checks and status constants. It can report corrupt, healthy, nonexistent, or failure status and supports fix modes: none, move corrupt files to `/lost+found`, or delete corrupt files.
- NameNode metrics APIs include `FSNamesystemMBean`, `FSNamesystemMetrics`, `NameNodeActivityMBean`, `NameNodeMetrics`, and `NameNodeMXBean`. They publish capacity, file/block counts, replication queues, live/dead DataNodes, load, operation counters, edit-log transaction/sync rates, safemode time, FSImage load time, corrupt block count, live/dead/decommissioning node JSON/string summaries, version, and thread count.
- Protocol value/command classes include `ServerCommand`, `DatanodeCommand`, `BlockCommand`, `BlockRecoveryCommand`, `RecoveringBlock`, `BlocksWithLocations`, `BlockWithLocations`, `NamenodeCommand`, `CheckpointCommand`, `KeyUpdateCommand`, `UpgradeCommand`, `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, and `ReplicaRecoveryInfo`. Most implement Hadoop `Writable` serialization or extend serializable block/command bases.
- Protocol interfaces include `DatanodeProtocol`, `InterDatanodeProtocol`, `NamenodeProtocol`, `NamenodeProtocols`, and `NodeRegistration`. They define the RPC boundary among NameNode, DataNode, secondary/backup NameNodes, balancer/checkpointing tools, and inter-DataNode recovery.

## Control Flow

The runtime control flow must be inferred from API contracts and Javadocs because this XML has no method bodies. A normal DataNode lifecycle is visible through `DatanodeProtocol`: the DataNode asks for `NamespaceInfo` with `versionRequest()`, registers through `registerDatanode(DatanodeRegistration)`, sends periodic `sendHeartbeat(...)` calls with capacity/usage/load/failed-volume state, submits full `blockReport(...)` arrays, notifies completed blocks with `blockReceived(...)`, reports errors, asks the NameNode to process upgrade commands, and participates in `commitBlockSynchronization(...)` for recovery. The NameNode replies with `DatanodeCommand[]`, including block transfer/invalidate/finalize/recover/key-update commands.

Block placement and replication flow goes through `FSNamesystem` and `BlockManager`. Client creation calls eventually request `getAdditionalBlock(...)`/`NameNode.addBlock(...)`; target selection is delegated to `BlockPlacementPolicyDefault.chooseTarget(...)`, which documents the classic policy: prefer the writer's local DataNode for the first replica, a different rack for the second, and a different node on that rack for the third. `verifyBlockPlacement(...)` and `chooseReplicaToDelete(...)` support rebalancing and over-replication cleanup.

Write completion and recovery are lease-driven. `FSNamesystem.completeFile(...)` can return false to make clients retry until minimum replication is achieved. If a lease expires, `LeaseManager` describes the recovery sequence where a primary DataNode coordinates replica state, generation stamp, minimum length, and replica updates, then the NameNode updates `BlockInfo` and edit-log state. `InterDatanodeProtocol` is the direct DataNode-to-DataNode recovery API: `initReplicaRecovery(...)` returns actual replica state and `updateReplicaUnderRecovery(...)` applies the new generation stamp and length.

Namespace mutation flow is mediated by `FSNamesystem` and persisted through `FSEditLog`/`FSImage`. Operations such as permission/owner/time updates, symlink creation, replication changes, concat, delete, mkdirs, block allocation, close, corrupt marking, quota, and delegation-token master key updates either mutate namespace/block state or enqueue replication/deletion work. `FSEditLog.logSync()` documents the durability boundary: edits are written into a synchronized memory buffer with transaction IDs, then a sync swaps buffers under lock, flushes storage outside the lock, and wakes waiters afterward.

Checkpoint flow has several variants. `SecondaryNameNode` periodically wakes, talks to the primary over `NamenodeProtocol`, rolls the edit log, downloads image/edits through `GetImageServlet`, merges them locally, and returns or finalizes images. `BackupNode` can either checkpoint periodically or keep a live in-memory namespace synchronized through `journal(...)` records sent by active NameNode journal streams. `CheckpointCommand` tells subordinate nodes whether their current image is obsolete and whether they must return the new image.

Upgrade flow uses generic upgrade objects and commands. NameNode-side `UpgradeObjectNamenode` processes generic `UpgradeCommand`s, starts upgrade, and can force progress. DataNode-side `UpgradeObjectDatanode` runs upgrades in separate threads and reports completion through `completeUpgrade()`. `UpgradeCommand` carries an action, upgrade version, and current status; receivers are expected to verify the version.

HTTP helper flow is routed through NameNode servlets. HFTP-style calls list paths, stream file data, fetch content summaries and checksums, and redirect file or checksum requests to suitable DataNodes. Checkpoint/image operations use `GetImageServlet`, with `isValidRequestor(...)` guarding access. Delegation token servlet endpoints fetch, renew, and cancel tokens for HFTP use.

## State and Persistence Behavior

The key persistent namespace state is documented in the `NameNode` class comment: the filename-to-blocksequence table is stored on disk and is precious, while the block-to-DataNode map is rebuilt at startup from DataNode reports. `FSNamesystem` owns the live namespace/block management state; `FSImage` and `FSEditLog` persist it across restarts.

`FSImage` checkpoint state includes checkpoint time, image MD5 digests, removed storage directories, and a volatile checkpoint state that governs whether the image can be rolled. Its directory transitions are explicit: save the current image and empty journal into `current`, move well-formed `current` to `lastcheckpoint.tmp`, then move `lastcheckpoint.tmp` to `previous.checkpoint`. The `setFields(...)` doc requires writing the version file last so missing/corrupt `VERSION` marks an invalid checkpoint.

`FSEditLog` persists incremental namespace edits. Its double-buffering model is a concurrency and durability contract: transaction IDs are assigned during synchronized writes; per-thread transaction IDs decide what must be synced; a volatile sync-running flag prevents overlapping syncs; and operations requiring exclusive sync ordering must synchronize and wait for any active sync to finish.

DataNode registration state is tied to persistent storage IDs and namespace IDs. `FSNamesystem.registerDatanode(...)` distinguishes new storage from replacement DataNodes using storage IDs, assigns new unique storage IDs when needed, and returns the namespace ID as the registration ID. Later DataNode communication must present an appropriate registration ID or be rejected.

Lease state is runtime state for files under construction, but lease recovery ends with persistent edit-log commits. Generation stamps are explicit NameNode state, exposed through `setGenerationStamp(...)` and `getGenerationStamp()`, and are central to block recovery and stale replica rejection.

Metrics state is runtime/observability state. DataNode and NameNode metrics expose public mutable metric objects that callers can increment or set directly. MBeans publish sampled and averaged metrics through Hadoop metrics contexts; docs note that the null metrics context needs an update thread to produce averaged samples.

Protocol objects carry serialized RPC state. `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, `ReplicaRecoveryInfo`, `BlockCommand`, `BlocksWithLocations`, `CheckpointCommand`, `ServerCommand`, and `UpgradeCommand` all expose `write/readFields` or extend `Writable` bases, making field order and compatibility important for RPC wire behavior.

## Dependencies and Integration Points

This chunk integrates with Hadoop core configuration, metrics, IPC, security, servlet, HTTP, and network topology APIs. Visible dependencies include `Configuration`, `MetricsContext`, `MetricsRegistry`, `MetricsTimeVaryingInt/Long/Rate`, `MetricsIntValue`, `MetricsDynamicMBeanBase`, `VersionedProtocol`, `Server`, `HttpServer`, `UserGroupInformation`, `Token`, `Text`, `FsPermission`, `PermissionStatus`, `ContentSummary`, `Options.Rename`, `AccessControlException`, and `NetworkTopology`.

HDFS protocol dependencies include `Block`, `LocatedBlock`, `LocatedBlocks`, `BlockListAsLongs`, `DatanodeID`, `DatanodeInfo`, `DirectoryListing`, `HdfsFileStatus`, `FSConstants` actions/report types, `QuotaExceededException`, block-token `ExportedBlockKeys`, delegation-token `DelegationTokenIdentifier` and secret manager types, common `StorageInfo`, `StorageDirectory`, `HdfsConstants.NodeType`, `NamenodeRole`, and `ReplicaState`.

External integration points include Jetty connectors, servlet request/response APIs, JMX, HFTP clients, secondary/backup NameNode checkpointing, balancer block selection via `NamenodeProtocol.getBlocks(...)`, include/exclude host refresh through `refreshNodes()`, service authorization refresh, user/group mapping refresh, and superuser proxy group refresh.

The package `org.apache.hadoop.hdfs.server.protocol` is the main RPC compatibility boundary. `NamenodeProtocols` combines `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `RefreshAuthorizationPolicyProtocol`, and `RefreshUserMappingsProtocol`, making `NameNode` the single implementation facade for clients, DataNodes, subordinate NameNodes, and admin refresh operations.

## Risks and Edge Cases

- This is an API baseline, not source. It does not show private fields, method bodies, enum constant values, error branches, lock acquisition order, or exact serialization field order beyond the presence of `Writable` methods. Research consumers should treat algorithmic notes as Javadoc-backed inference.
- The JDiff range starts inside `SecureDataNodeStarter.SecureResources` and ends inside `DelegationTokenFetcher.main`, so adjacent chunks are needed for complete class/package context.
- `FSEditLog.logSync()` is concurrency-sensitive. Any implementation change around transaction IDs, buffer swap timing, unsynchronized flush, or wait/notify behavior can create lost edits, duplicate syncs, deadlocks, or latency regressions.
- `FSImage.setFields(...)` requires writing `VERSION` last. Reordering storage file writes can make partial checkpoints appear valid or valid checkpoints appear corrupt.
- DataNode registration depends on storage IDs and namespace IDs. Reusing, losing, or incorrectly assigning storage IDs can make the NameNode confuse new storage with replacement nodes or reject valid DataNodes.
- `BlockManager` docs require several calls under the `FSNamesystem` lock. Calling report/replication logic without the expected lock risks inconsistent block maps.
- Block placement is rack-aware and policy-pluggable. Misconfigured `dfs.block.replicator.classname`, stale network topology, or incorrect excluded-node handling can reduce fault tolerance or cause allocation failures.
- Lease recovery crosses NameNode and multiple DataNodes. Generation stamp, minimum length, and close/delete flags in `commitBlockSynchronization(...)` are correctness-critical for avoiding divergent replicas.
- Safe mode blocks namespace mutations. APIs expose `SafeModeException` on many write paths; tests must cover the retry/denial behavior when safe mode is active.
- `CheckpointCommand` and `NamenodeProtocol` include deprecated legacy edit-log/image roll methods as well as newer checkpoint/journal flows. Compatibility callers may still rely on deprecated methods.
- Metrics fields are public mutable objects. That is part of the API but allows tests or external code to mutate counters directly.
- HTTP servlet endpoints handle security-sensitive image, token, and file access. `GetImageServlet.isValidRequestor(...)` and delegation token servlet parameter handling are high-risk access control surfaces.
- `NameNode.stopRequested` is documented as testing-only state; relying on it in production logic would be fragile.
- Many protocol classes expose `equals/hashCode` and `Writable` serialization. Equality must remain consistent with serialized identity, especially for registrations and recovery info.
- `FSNamesystemMetrics.doUpdates(...)` casts some long values to int and rounds capacity values to GB because collectors could not handle long values. Large-cluster tests need to account for truncation/rounding in old metrics.

## Test Signals

Useful validation for code represented by this API should include:

- API/JDiff compatibility tests asserting the packages, classes, interfaces, fields, methods, checked exceptions, synchronization flags, visibility, and deprecation markers in this line range.
- DataNode lifecycle tests for `versionRequest`, registration, heartbeat command responses, block reports, block received notifications, bad block reports, error reports, and rejected DataNodes through include/exclude host configuration.
- Block command serialization tests for `BlockCommand`, `BlockRecoveryCommand`, `RecoveringBlock`, `KeyUpdateCommand`, `DatanodeCommand.REGISTER/FINALIZE`, and `UpgradeCommand`.
- Block placement tests with single rack, multiple rack, excluded nodes, writer-local placement, insufficient replicas, placement verification, and replica deletion candidate selection.
- Edit-log tests for concurrent namespace operations calling `logSync()`, batched sync accounting, transaction ordering, open/close file edit records, mkdir edit records, and journal stream iteration by type.
- FSImage storage tests for format, checkpoint save, `current` to `lastcheckpoint.tmp`, `lastcheckpoint.tmp` to `previous.checkpoint`, digest handling, failed storage restore/remove behavior, and invalid/missing `VERSION` detection.
- FSNamesystem tests for permissions, owner, concat validation-before-move behavior, timestamp edit logging without immediate flush, symlinks, replication increase/decrease scheduling, add/abandon/complete block retry behavior, delete/mkdir/listing, corrupt block marking, quota, safe mode, and generation stamp updates.
- Lease recovery tests for soft/hard lease expiry, primary DataNode selection, new generation stamp allocation, minimum replica length calculation, `InterDatanodeProtocol` update behavior, NameNode block-info update, edit-log commit, and lease removal.
- Checkpoint/backup tests for subordinate NameNode registration, `startCheckpoint`, `CheckpointCommand` flags, image transfer through `GetImageServlet`, `endCheckpoint`, backup `journal(...)`, and journal action constants.
- NameNode RPC facade tests for client protocol methods, DataNode protocol methods, subordinate NameNode protocol methods, service RPC address fallback, HTTP address binding, startup options, and clean `stop()/join()` behavior.
- Delegation-token tests through both RPC and HTTP servlets: get, renew, cancel, invalid token handling, renewer identity, master-key edit logging, and secure/insecure configuration behavior.
- Metrics and JMX tests for DataNode/NameNode metric counters, periodic `doUpdates(...)`, reset of min/max metrics, MBean registration/shutdown, null metrics context with update thread, and large-value rounding/casting behavior.
- Fsck and HFTP servlet tests for corrupt/healthy/nonexistent/failure status, move/delete/no-fix modes, content summary, listPaths filters/excludes/recursive output, file-data redirects, checksum redirects, and stream content length.
- Protocol serialization round trips for `BlocksWithLocations`, `BlockWithLocations`, `CheckpointCommand`, `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, `ReplicaRecoveryInfo`, `ServerCommand`, and `UpgradeCommand`.

## Chunk Boundary Notes

Lines 11807-17750 cover the end of DataNode secure startup support, DataNode distributed upgrade support, DataNode metrics, the NameNode server/control-plane APIs, NameNode metrics, and most of `org.apache.hadoop.hdfs.server.protocol`. The line range ends before `DelegationTokenFetcher.main` is closed, so the tools package should be completed by the next chunk. The final per-file report should merge this with adjacent chunks for complete DataNode, NameNode, protocol, and tool coverage.

### subset-b-007475: lines 17751-18589

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.22.0.xml lines 17751-18589

## Chunk Scope

This chunk is the final span of the Hadoop HDFS 0.22.0 JDiff XML API snapshot. It starts in the tail of `org.apache.hadoop.hdfs.tools.DelegationTokenFetcher`, covers HDFS command-line/admin tools, offline fsimage viewer entry points, and HDFS utility collection/throttling types, then closes the XML document.

The file is API metadata, not executable Java source. It records public type signatures, inheritance, implemented interfaces, constructors, methods, fields, exceptions, synchronization flags, deprecation status, and Javadoc CDATA used for compatibility comparison.

## Purpose and Major Areas

The span documents three broad API surfaces:

- HDFS operational tools in `org.apache.hadoop.hdfs.tools`: delegation-token fetching/renewal/cancellation, administrative NameNode commands, filesystem checking, concatenation, and JMX inspection.
- Offline image viewer entry points in `org.apache.hadoop.hdfs.tools.offlineImageViewer`: visitors and CLI plumbing for reading fsimage files without a live NameNode.
- Low-level HDFS utilities in `org.apache.hadoop.hdfs.util`: byte-array key wrapping, transfer throttling, and memory-sensitive set implementations used by HDFS internals.

## Important APIs and Types

### `org.apache.hadoop.hdfs.tools`

`DelegationTokenFetcher` is a command-line helper for obtaining and managing HDFS delegation tokens. This chunk includes `main(String[])`, static `getDTfromRemote(String nnAddr, String renewer)`, static `renewDelegationToken(String nnAddr, Token tok)`, and static `cancelDelegationToken(String nnAddr, Token tok)`. The renew API returns the next token expiration timestamp as a `long`; both renew and cancel document the NameNode address and token parameters and throw `IOException`.

`DFSAdmin` extends `org.apache.hadoop.fs.FsShell` and provides public constructors with and without `Configuration`. Its public administrative methods map command-line subcommands to NameNode operations:

- `report()` prints filesystem status.
- `setSafeMode(String[] argv, int idx)` handles `-safemode enter|leave|get`.
- `saveNamespace()` asks the NameNode to persist the namespace via `ClientProtocol#saveNamespace()`.
- `restoreFaileStorage(String arg)` controls or checks failed-storage restoration. The method name is misspelled in the published API, so compatibility users must preserve that spelling.
- `refreshNodes()` reloads include/exclude host files.
- `finalizeUpgrade()` finalizes a completed upgrade.
- `upgradeProgress(String[] argv, int idx)` reports, details, or forces distributed-upgrade progress.
- `metaSave(String[] argv, int idx)` writes NameNode metadata structures to a named file.
- `printTopology()` prints rack-to-node topology as seen by the NameNode.
- `refreshServiceAcl()`, `refreshUserToGroupsMappings()`, and `refreshSuperUserGroupsConfiguration()` refresh NameNode authorization and identity/group mapping state.
- `run(String[] argv)` implements `Tool`-style dispatch and `main(String[])` is the process entry point.

`DFSck` extends `Configured` and implements `Tool`. Constructors accept `Configuration` and optionally a `PrintStream`, both throwing `IOException`. `run(String[] args)` performs fsck command execution and `main(String[])` is the CLI entry point. The class documentation describes scans from a chosen root path, detection of missing blocks, under-replication, over-replication, detailed DFS statistics, optional block-location and replication-factor output, and optional filtering of open files. For corrupted files, the documented actions are none, move salvageable block chains to `/lost+found`, or delete, corresponding to `NamenodeFsck` fix constants.

`HDFSConcat` is a thin public tool class with a default constructor and `main(String[] args)` throwing `IOException`. The XML does not include detailed command semantics in this span, but the name and placement indicate CLI exposure for HDFS file concatenation.

`JMXGet` is a command-line utility for reading Hadoop MBeans from NameNode or DataNode processes. It exposes mutable target configuration through `setService(String)`, `setPort(String)`, `setServer(String)`, and `setLocalVMUrl(String)`. `init()` initializes the MBean server connection, `printAllValues()` emits all attributes, `getValue(String key)` returns one attribute as a string, and `main(String[])` drives CLI usage. The documented MBean examples include NameNode `FSNamesystemState`, `NameNodeActivity`, NameNode RPC activity, DataNode RPC activity, `FSDatasetState`, and `DataNodeActivity`. Logging is intentionally sent to `System.err` because this is a command-line tool.

### `org.apache.hadoop.hdfs.tools.offlineImageViewer`

`NameDistributionVisitor` extends `TextWriterImageVisitor`. Its constructor accepts an output target string and a boolean flag, and throws `IOException`. The visitor analyzes file names in an fsimage and prints unique filename count, ranges of duplicate-name usage, and estimated heap saved if filename objects are reused.

`OfflineImageViewer` is the main fsimage inspection utility. Its constructor accepts an input image filename, an `ImageVisitor`, and a boolean option. `go()` processes the image file, `buildOptions()` creates Apache Commons CLI `Options`, and `main(String[])` parses CLI arguments, selects an output visitor, processes the fsimage, and exits cleanly or reports errors. The documentation explicitly positions it as both a command-line and programmatic entry point for dumping Hadoop image files to XML or console-oriented formats.

### `org.apache.hadoop.hdfs.util`

`ByteArray` wraps a `byte[]` so arrays can be used as `HashMap` keys. It exposes `getBytes()`, `hashCode()`, and `equals(Object)`. Correctness depends on value-based equality/hash semantics rather than Java array identity.

`DataTransferThrottler` provides thread-safe bandwidth limiting for HDFS data transfers. Constructors accept `bandwidthPerSec` alone or an enforcement `period` plus bandwidth. `getBandwidth()` and `setBandwidth(long)` are synchronized; `setBandwidth` takes effect no later than the end of the current period. `throttle(long numOfBytes)` is synchronized and sleeps the calling thread when aggregate I/O rate exceeds the configured bytes-per-second budget. The docs say the configured bandwidth is shared by all threads using the same throttler instance.

`GSet` is a generic set-like interface extending `Iterable` with map-style lookup. It exposes `size()`, `contains(Object key)`, `get(Object key)`, `put(Object element)`, and `remove(Object key)`. Unlike `Set#add`, `put` replaces an equal existing element and returns the previous stored element. Null keys/elements are unsupported and documented as throwing `NullPointerException`. The generic contract is key type `K` and element type `E`, where `E` is a subclass of `K`.

`GSetByHashMap` implements `GSet` on top of `HashMap`. Its constructor takes initial capacity and load factor. It exposes the full `GSet` surface plus `iterator()`, serving as the straightforward collection-backed implementation.

`LightWeightGSet` implements `GSet` with lower memory overhead. The constructor takes a recommended internal array length. It exposes `size`, `get`, `contains`, `put`, `remove`, `iterator`, `toString`, and `printDetails(PrintStream)`, plus a public static final `LOG` field. The class stores elements in a fixed array and resolves collisions with linked lists. It never rehashes or resizes, rejects null elements, and is explicitly not thread safe. Elements must implement the nested `LightWeightGSet.LinkedElement` interface.

`LightWeightGSet.LinkedElement` is a public static nested interface with `setNext(LightWeightGSet.LinkedElement)` and `getNext()`. It lets the set maintain collision chains without allocating separate wrapper nodes, which is the core memory-saving design point.

## Control Flow and Lifecycle

Tool classes follow the Hadoop CLI pattern: parse arguments in `main` or `run`, build or read configuration, connect to NameNode/DataNode/JMX or local fsimage state, then return an exit code or throw an exception. `DFSAdmin.run` is the central command dispatcher for administrative subcommands. Individual methods perform focused RPC-like operations such as save namespace, refresh nodes, or change safemode. `DFSck.run` drives a scan through the NameNode-side fsck implementation and reports findings/actions through the configured output stream.

Delegation-token flow is remote and token-centered: `getDTfromRemote` obtains credentials from a named NameNode address for a renewer; `renewDelegationToken` sends the token back to the NameNode and returns the updated expiration; `cancelDelegationToken` invalidates it. Callers must handle `IOException` from RPC, address resolution, and token service errors.

Offline image viewing is file-oriented rather than cluster-oriented. `OfflineImageViewer.main` builds CLI options, chooses an `ImageVisitor`, constructs the viewer, and calls `go()`. Visitors such as `NameDistributionVisitor` receive parsed fsimage events and write derived reports.

`DataTransferThrottler` control flow is per-transfer accounting: callers report bytes transferred to `throttle`; the synchronized method compares accumulated bytes over the current period against the configured bandwidth and sleeps if necessary. Shared use across transfer threads intentionally enforces a group bandwidth budget.

`GSet` implementations center on key-equivalent element lookup. `GSetByHashMap` delegates lifecycle to Java collection storage. `LightWeightGSet` uses caller-owned element link pointers, so `put` and `remove` mutate the element chain through `LinkedElement.setNext` and depend on stable `hashCode`/`equals` behavior.

## State and Persistence Behavior

The JDiff XML itself preserves API compatibility state for Hadoop 0.22.0. Within the APIs it describes, persistent or externally visible state includes delegation tokens and `Credentials`, NameNode namespace images, host include/exclude files, upgrade state, metadata dump files from `metaSave`, fsck repair output under `/lost+found`, and offline fsimage input/output reports.

`DFSAdmin.saveNamespace` triggers NameNode persistence of filesystem namespace state. `finalizeUpgrade` and `upgradeProgress` interact with upgrade lifecycle state that must remain consistent across NameNode/DataNode processes. Refresh commands update live in-memory policy, group mapping, superuser proxy configuration, or datanode membership state from external configuration files.

`JMXGet` keeps connection target state in service, port, server, or local VM URL fields until `init` connects. It reads live process metrics but does not define a durable format in this span.

`ByteArray` stores a raw byte-array reference; if callers mutate that array after inserting the wrapper into a hash map, hash/equality behavior can become inconsistent. `DataTransferThrottler` stores synchronized mutable bandwidth and per-period accounting. `LightWeightGSet` stores entries in a fixed-size array and in each element's next pointer, so set membership is embedded partly in the elements themselves.

## Dependencies and Integration Points

These APIs depend on Hadoop core and HDFS types including `Configuration`, `FsShell`, `Configured`, `Tool`, `Credentials`, `Token`, `NameNode`, `ClientProtocol`, `NamenodeFsck`, `ImageVisitor`, and `TextWriterImageVisitor`. They also use Java I/O (`IOException`, `PrintStream`), Java collections/iteration, Apache Commons CLI `Options`, Apache Commons Logging `Log`, and Java MBean/JMX infrastructure through the `JMXGet` tool.

External integration points are operationally significant: NameNode administrative RPCs, DataNode/NameNode JMX MBeans, delegation-token services, fsimage files, Hadoop security authorization policy files, user/group mapping providers, include/exclude hosts files, upgrade-finalization state, and filesystem repair paths such as `/lost+found`.

The utility collection types integrate with HDFS in-memory metadata structures. `LightWeightGSet` is especially tied to high-cardinality metadata use cases where avoiding per-entry wrapper allocation matters, such as block or inode lookup tables in older HDFS internals.

## Risks and Edge Cases

- The published `DFSAdmin.restoreFaileStorage` spelling is part of the public API in this snapshot; correcting it without a compatibility bridge would break callers using the JDiff-defined method.
- Administrative commands mutate live cluster state. Safemode transitions, namespace saves, upgrade finalization, and failed-storage restoration need authorization checks and should be tested against NameNode state transitions, not just CLI parsing.
- Refresh commands are only as correct as their backing configuration sources. Bad hosts files, service ACLs, or group mapping data can immediately affect cluster access and datanode participation.
- Fsck repair modes can delete data or move partial block chains to `/lost+found`; tests need to distinguish reporting-only scans from mutating repair modes.
- Delegation token renew/cancel operations are security-sensitive. Wrong NameNode address, renewer identity, expired tokens, or token service mismatch should fail clearly and avoid leaking credentials.
- JMX MBean names include service, port, and sometimes storage-id-derived names. Hard-coded MBean strings can be brittle across process roles, ports, and versions.
- `ByteArray` is safe as a map key only if the wrapped bytes are treated as immutable while stored in hash-based collections.
- `DataTransferThrottler` is synchronized and may become a contention point when shared by many transfer threads. Bandwidth changes are period-delayed by design.
- `LightWeightGSet` never rehashes, so a poor recommended length or skewed hash distribution can cause long chains and degraded lookup performance. It is not thread safe and corrupts membership if elements' next pointers are reused elsewhere.
- `LightWeightGSet` depends on element implementations of `LinkedElement`, `equals`, and `hashCode`; mutable key fields can make entries unreachable or removable only by traversal accidents.

## Test Signals

Useful validation around code represented by this API snapshot would include:

- JDiff/schema checks asserting that the public classes, methods, exceptions, synchronization flags, and field visibility in this line span remain stable for the 0.22.0 snapshot.
- CLI dispatch tests for `DFSAdmin.run` covering `-safemode`, `-saveNamespace`, `-restoreFailedStorage`, `-refreshNodes`, `-finalizeUpgrade`, `-upgradeProgress`, `-metasave`, topology printing, and refresh commands, including argument-index validation and non-zero exit codes.
- NameNode integration tests for namespace save, hosts refresh, service ACL refresh, group mapping refresh, superuser proxy refresh, safemode transitions, upgrade progress, and upgrade finalization.
- Delegation token tests for fetch, renew, cancel, expired-token handling, wrong renewer, wrong NameNode address, and credential serialization around `getDTfromRemote`.
- Fsck tests for healthy files, missing blocks, under-replicated blocks, over-replicated blocks, open-file filtering, detailed block-location output, delete repair, and move-to-`/lost+found` repair.
- JMX tests with mock or in-process MBean servers verifying server/port/service/local-VM configuration, `init`, `getValue`, missing attributes, and `printAllValues`.
- Offline image viewer tests for option construction, invalid CLI arguments, visitor selection, `go()` error handling, and `NameDistributionVisitor` duplicate-name/heap-savings reporting against small fsimage fixtures.
- `ByteArray` equality/hash tests for same contents, different contents, and mutation-after-insert behavior documentation.
- `DataTransferThrottler` tests using controlled clocks or bounded sleeps for bandwidth enforcement, dynamic `setBandwidth`, shared-thread throttling, and synchronized access.
- `GSet` contract tests shared across `GSetByHashMap` and `LightWeightGSet`: null rejection, `put` replacement semantics, `get` by equal key, `remove`, iteration, and size tracking.
- `LightWeightGSet` stress tests for collision chains, fixed-capacity behavior, iterator consistency after removal, `printDetails`, and non-thread-safe behavior guarded by higher-level synchronization in callers.

## Cross-Chunk Notes

The chunk starts after the beginning of `DelegationTokenFetcher`; adjacent upstream lines contain earlier package context and the start of that class. This chunk ends at `</api>`, so it completes the `hadoop-hdfs_0.22.0.xml` source file. Merge/reconciliation should treat this as a chunk report for the tail of the file, not as a complete source-file report by itself.
