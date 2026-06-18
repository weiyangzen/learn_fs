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
