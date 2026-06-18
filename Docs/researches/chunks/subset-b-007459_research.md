# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.6.0.xml lines 5264-10855

## Purpose

This chunk is part of the HDFS 2.6.0 JDiff API descriptor. It is XML metadata generated from Java public/protected API surfaces, not executable HDFS implementation code. The range starts near the end of `org.apache.hadoop.hdfs.protocolPB.PBHelper`, then walks through public APIs in the Quorum Journal Manager, block and delegation token security, balancer, block management, server common constants, DataNode replica/storage/web APIs, and a large NameNode metadata/persistence section ending at the declaration of `INodeReference.DstReference`.

The practical purpose of this XML is compatibility research: it records method signatures, visibility, synchronization, exceptions, fields, constructors, inheritance, and embedded Javadoc for APIs exposed by Hadoop HDFS 2.6.0. The merge lane should treat it as an API map that points to the real Java source behavior elsewhere in the HDFS tree.

## Important APIs, Types, and Functions

- `org.apache.hadoop.hdfs.protocolPB.PBHelper` tail methods convert between implementation objects and protobuf wire objects for short-circuit shared memory IDs/slots, inotify edit responses, cipher options, cipher suites, crypto protocol versions, and file/encryption-zone metadata. The Javadoc states the conversion convention: internal-to-protobuf converters do not return null, so callers must check internal nulls before invoking them.
- `org.apache.hadoop.hdfs.qjournal.server.Journal` exposes JournalNode edit-log segment control: `heartbeat`, `startLogSegment`, `finalizeLogSegment`, `purgeLogsOlderThan`, `getEditLogManifest`, `prepareRecovery`, `acceptRecovery`, upgrade/finalize/rollback hooks, `getLastWriterEpoch`, `getJournalCTime`, and `close`. Public constants include `LAST_PROMISED_FILENAME` and `LAST_WRITER_EPOCH`.
- `JournalNodeMXBean` exposes JMX status through `getJournalsStatus()`.
- `BlockPoolTokenSecretManager` multiplexes `BlockTokenSecretManager` instances by block pool. It exposes block-pool registration, identifier/password creation, password retrieval, access checks by identifier or token, exported key ingestion, block-token generation, data-encryption-key generation/retrieval, and test-only key clearing.
- `BlockTokenSecretManager.AccessMode` is the enum surface for block token permissions.
- Delegation token nested types include `WebHdfsDelegationTokenIdentifier`, `SWebHdfsDelegationTokenIdentifier`, and `DelegationTokenSecretManager.SecretManagerState`, whose state object carries an FSImage secret-manager section plus persisted keys and tokens.
- Balancer APIs include dispatcher block/datanode/storage-group wrappers, `PendingMove`, `Source`, `StorageGroupMap`, process `ExitStatus`, topology `Matcher` constants (`SAME_NODE_GROUP`, `SAME_RACK`, `ANY_OTHER`), and `MovedBlocks`/`MovedBlocks.Locations` for avoiding recently moved blocks.
- Block management APIs cover `BlockInfoUnderConstruction`, node-group-aware placement policy, placement-status reporting, storage-policy suite and storage-policy XAttrs, corrupt-replica reasons, cached-block lists, decommissioning metrics, datanode aggregate statistics, `DatanodeStorageInfo`, mutable block collections, replica counts, and unresolved topology errors.
- Server common APIs define enums and helpers used across NameNode/DataNode startup and storage: block-under-construction state, NameNode role, node type, replica state serialization, rolling-upgrade startup options, `StartupOption` mutable startup parameters, `JspHelper.Url`, and `Storage.StorageState`.
- DataNode APIs include `CachingStrategy` and builder, layout-version features, `DataNodeMXBean`, finalized/RBW/RWR/RUR replica classes, replica exceptions, secure starter resource wrappers, `ShortCircuitRegistry`, and `ShortCircuitRegistry.NewShmInfo`.
- `org.apache.hadoop.hdfs.server.datanode.fsdataset` exposes volume choice policies, `FsDatasetSpi.Factory`, `FsVolumeSpi`, length-tagged input streams, replica input/output stream containers, rolling logs, and round-robin volume choice.
- `org.apache.hadoop.hdfs.server.datanode.web.resources.DatanodeWebHdfsMethods` exposes REST endpoints for WebHDFS `PUT`, `POST`, and `GET` at root and path variants. `OpenEntity.Writer` is the JAX-RS message body writer for streaming open-file responses.
- NameNode APIs in this range include audit logging, cache-manager persistence state, delegation-token HTTP servlets, content counters, quota features, encryption-zone/fault-injection hooks, edit-log reader/writer helpers, legacy and protobuf FSImage loaders/savers, safe-mode info, audit logger extension, inode block deletion tracking, inode feature markers, inode snapshot attribute copies, `INodeDirectory`, `INodeMap`, and `INodeReference`.

## Control Flow

The control-flow information in this XML is signature and Javadoc level. It does not show method bodies, but the API boundaries imply several major HDFS flows.

The Quorum Journal flow is driven by `Journal`. A writer establishes liveness and fencing with `RequestInfo` through `heartbeat` and epoch-related state, starts an in-progress edit-log segment with `startLogSegment`, commits a closed segment with `finalizeLogSegment`, purges old logs, and exposes manifests for consumers. Recovery uses a two-phase shape: `prepareRecovery(reqInfo, segmentTxId)` returns a protobuf recovery response, then `acceptRecovery(reqInfo, segment, fromUrl)` accepts a selected segment state. Upgrade operations run through `doPreUpgrade`, `doUpgrade`, `doFinalize`, `canRollBack`, and `doRollback`.

Block-token control flow routes through a block-pool lookup before delegating to the appropriate secret manager. Token clients create or validate `BlockTokenIdentifier` values, check an `AccessMode` against an `ExtendedBlock`, add exported block keys, and generate or retrieve data-encryption keys. Failures surface as `SecretManager.InvalidToken`, which is security-critical because DataNode read/write access depends on these checks.

Balancer control flow tracks planned movement from a `Dispatcher.Source` to a target `StorageGroup`, wraps blocks in `DBlock`, and consults `MovedBlocks` before scheduling work. `MovedBlocks.cleanup()` maintains a time-windowed memory of recently moved blocks so the balancer does not churn the same block repeatedly. Topology `Matcher` implementations describe whether two datanodes are acceptable peers by node group, rack, or any-other placement rules.

Block placement and under-construction block flow is centered on `BlockInfoUnderConstruction` and `BlockPlacementPolicyWithNodeGroup`. New or appended files keep the last block in an under-construction state with expected `DatanodeStorageInfo` targets. Recovery assigns a recovery id, chooses a primary DataNode, and later verifies generation stamps and replicas. Node-group placement first tries local storage, falls back to local node group/rack, chooses remote rack replicas, excludes node-group peers to avoid over-concentration, and chooses replica deletion candidates from placement sets.

DataNode replica flow distinguishes finalized replicas, replicas being written, replicas in pipeline, replicas waiting to be recovered, and replicas under recovery. `ReplicaInPipelineInterface` defines bytes-received, bytes-acked, last-checksum, and stream creation behavior. `ReplicaInPipeline.stopWriter()` interrupts and waits for the writer thread. `ReplicaUnderRecovery` wraps an original replica with a recovery id so higher-id recoveries can preempt lower-id recoveries.

Short-circuit read flow uses `ShortCircuitRegistry`. Clients request shared-memory segments over domain sockets, register slots for block IDs, and unregister them later. Cache and invalidation events mark slots anchorable, unanchorable, or invalid so clients stop using stale local replicas. `NewShmInfo` returns the shared-memory id and file stream and must be closed by its caller.

FSImage and edit-log flows are represented by loaders/savers and readers/writers. `FSEditLogLoader.PositionTrackingInputStream` wraps an input stream with byte-position tracking and read limits. `FSEditLogOp.Reader` can read or scan edit-log operations, optionally skipping broken edits. `FSEditLogOp.Writer` writes operations to a `DataOutputBuffer`. `FSImageFormat.Loader` and `FSImageFormatProtobuf.Loader` load FSImage state and expose loaded transaction IDs and MD5 hashes; protobuf saver classes commit named sections and hold string/ref deduplication contexts.

NameNode inode flow is the richest section. `INodeDirectory` controls child lookup, insertion, deletion, snapshot-aware child lists, snapshottable features, snapshot add/remove/rename, quota usage, content-summary computation, block collection during deletion, rename undo, recursive subtree cleanup, and tree dumps. Snapshot-aware operations accept current/prior snapshot ids and return quota deltas or saved inode copies. `INodeReference` forwards most inode metadata and subtree operations to a referred inode while preserving multiple path identities created by snapshots and renames.

## State and Persistence Behavior

State in this XML itself is static API metadata. Persistent behavior is indirect and described through the APIs.

`Journal` persists edit-log segment files and epoch/fencing metadata. Public filename constants for last promised and last writer epochs show that writer fencing state is stored on disk. Segment lifecycle methods mutate JournalNode storage, while manifest and recovery methods expose the persisted segment set to NameNodes and recovery logic.

Token managers maintain in-memory secret state and persistent FSImage state. `BlockPoolTokenSecretManager` owns a map from block pool id to block-token managers. Delegation token persistence is exposed by `SecretManagerState`, which carries protobuf secret-manager section data plus lists of keys and tokens for image save/load.

Balancer state is mostly transient. `MovedBlocks` stores current and old movement windows in memory for a fixed interval, while dispatcher storage groups track scheduled bytes and DataNode delays. These structures prevent inefficient moves but are not filesystem metadata.

Block management state spans persistent namespace metadata and live cluster state. `BlockInfoUnderConstruction` tracks under-construction state, expected storage locations, and recovery ids. `DatanodeDescriptor.DecommissioningStatus` exposes counters for under-replicated, decommission-only, and open-file blocks during decommission. `DatanodeStatistics` aggregates live capacity, cache, block-pool, xceiver, and heartbeat metrics.

Storage policy state is persisted as XAttrs. `BlockStoragePolicySuite` defines storage-policy ids, the unspecified id, the storage-policy XAttr name/namespace, and helpers to build or detect policy XAttrs. `INodeDirectory` and `INodeFileAttributes.SnapshotCopy` expose local/effective storage policy ids, linking namespace metadata to DataNode storage placement.

DataNode replica state is persisted on local volumes as block and checksum files, while Java objects expose the current state. Finalized replicas provide visible/on-disk length. RBW and pipeline replicas track bytes acked, bytes on disk, bytes reserved, writer thread, last checksum, and output streams. Replica states can be serialized through `HdfsServerConstants.ReplicaState.read/write`.

FSDataset state includes volume identity, block-pool directories, available space, storage type, reserved RBW space, transient-storage status, and rolling logs. `ReplicaInputStreams` and `ReplicaOutputStreams` represent paired data/checksum streams, and output streams can sync data and checksum independently.

NameNode persistence is explicit in the FSImage/edit-log APIs. FSImage loaders expose loaded image MD5 and txid; protobuf loader/saver contexts carry string tables, reference lists, and section ordering. Cache-manager persistence stores cache section, pools, and directives. Inode snapshot copies persist immutable metadata snapshots: local name, permission, ACL, modification/access times, XAttrs, directory quotas, file replication, preferred block size, header bits, and storage policy id.

`INodeMap` is an in-memory id-to-inode index. `INode.BlocksMapUpdateInfo` accumulates blocks to remove from the block map during file deletion. `INodeReference` state models multiple namespace paths to one referred inode after snapshot-preserving rename/move operations, including destination snapshot id and reference count behavior.

## Dependencies and Integration Points

This JDiff file depends on the Java API model and names types from many Hadoop and third-party packages. The APIs in the chunk integrate with:

- HDFS protobuf protocol packages: `DataTransferProtos`, `ClientNamenodeProtocolProtos`, `HdfsProtos`, and `QJournalProtocolProtos`.
- Hadoop crypto and encryption types: `CipherOption`, `CipherSuite`, `CryptoProtocolVersion`, and `FileEncryptionInfo`.
- Quorum journal protocols: `RequestInfo`, `QJournalProtocol`, segment-state protobufs, `RemoteEditLogManifest`, and `StorageInfo`.
- Hadoop security token infrastructure: `SecretManager`, `Token`, `BlockTokenIdentifier`, `BlockTokenSecretManager`, delegation token identifiers, and delegation token secret manager state.
- HDFS block/data types: `Block`, `ExtendedBlock`, `ExtendedBlockId`, `DatanodeInfo`, `DatanodeID`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `StorageType`, and replica recovery info.
- Hadoop network topology: `NetworkTopology`, `Node`, node-group placement rules, and unresolved topology errors.
- NameNode namespace types: `FSDirectory`, `FSNamesystem`, `INode`, `INodeDirectory`, inode attributes, ACL/XAttr features, snapshots, quota counts, content-summary context, FSImage protobuf sections, edit-log op codes, and metadata recovery context.
- DataNode storage/runtime types: `DataNode`, `DataStorage`, `FsDatasetSpi`, `FsDatasetImpl`, `FsVolumeSpi`, `FsDatasetCache`, domain sockets, file descriptors, `DataChecksum`, and replica stream wrappers.
- Web and management surfaces: JMX MXBeans, servlet request/response APIs, JAX-RS `Response`, `MessageBodyWriter`, media types, WebHDFS parameter classes, and `UserGroupInformation`.

The empty packages (`qjournal.client`, `qjournal.protocol`, `qjournal.protocolPB`, `server.mover`, and `server.datanode.metrics`) are still significant for JDiff: they preserve package presence even though this chunk lists no public classes for them.

## Risks and Edge Cases

- This is a generated compatibility descriptor. Editing it manually can desynchronize API reports from source code and produce false compatibility conclusions.
- The chunk starts in the middle of `PBHelper`, so the final per-file research must merge with prior chunks for the full conversion-helper surface.
- Many methods marked public in this XML are internal HDFS implementation surfaces rather than stable user-facing APIs. Consumers should avoid assuming all public JDiff entries are safe extension points.
- Several state-mutating methods are synchronized in the API surface, including many `Journal`, token-manager, balancer, DataNode, and short-circuit registry methods. Compatibility changes to synchronization can affect thread-safety assumptions even if signatures remain unchanged.
- `Journal` recovery and epoch files are fencing-critical. Bugs in `getLastWriterEpoch`, promised epoch persistence, `prepareRecovery`, or `acceptRecovery` risk split-brain edit-log writers.
- Block token routing by block pool is security-critical. A missing pool registration, wrong block-pool id, or stale key set can deny valid clients or allow invalid access.
- `PBHelper` encryption converters touch cipher suites, crypto protocol versions, per-file encryption info, and zone key names. Null handling and unknown enum handling are likely compatibility-sensitive.
- Balancer movement windows are transient. Too-short cleanup or incorrect block identity comparison could repeatedly move the same blocks; too-long retention could starve legitimate balancing.
- Node-group placement changes can reduce fault tolerance if rack/node-group exclusion is wrong. `pickupReplicaSet` is also deletion-sensitive because it chooses which excess replica to remove.
- Under-construction and recovery APIs rely on generation stamps and recovery ids. Incorrect ordering can accept stale replicas or preempt the wrong recovery.
- DataNode replica classes expose equality/hash code and mutable state such as lengths, writer thread, and recovery id. Incorrect equality can corrupt in-memory replica maps.
- Short-circuit shared memory slots are invalidation-sensitive. Failing to mark slots unanchorable or invalid on munlock/invalidation can let DFSClient read stale local data.
- `FsVolumeSpi.reserveSpaceForRbw` and `releaseReservedSpace` must stay balanced. Leaks reduce usable DataNode capacity; under-reservation can fail writes late.
- `AvailableSpaceVolumeChoosingPolicy` and `RoundRobinVolumeChoosingPolicy` are synchronized selection points. Changes to policy behavior can alter write distribution and test expectations.
- WebHDFS DataNode methods throw both `IOException` and `InterruptedException`, so request handling must preserve interruption behavior and user identity/delegation parameter semantics.
- `AuditLogger.logAuditEvent` is documented as called in a critical NameNode section and must return quickly. Slow or blocking implementations can hurt namespace throughput.
- `EncryptionZoneManager` documentation warns about lock ordering: it has its own lock but relies on FSDirectory lock for many operations, and FSDirectory lock should not be taken after manager lock.
- FSImage protobuf `SectionName` loading order is determined by enum order. Reordering enum constants can break image load compatibility even if names remain.
- `FSEditLogOp.Reader.readOp` may reuse returned operation objects. Callers must not retain and mutate those objects assuming each read returns a fresh instance.
- Snapshot and rename logic in `INodeDirectory`/`INodeReference` is subtle. Rename undo, reference replacement, deleted/created diff lists, quota deltas, and block collection all interact; small behavior changes can corrupt snapshot namespace views.
- `INodeDirectory` copy constructors explicitly do reference copies for features. Tests and maintainers should not assume deep copies of quota/snapshot/XAttr feature state.

## Test Signals

Useful validation should be API- and behavior-oriented in the real HDFS Java sources, with this XML used as the checklist of exposed surfaces:

- Run JDiff or API-compatibility checks against HDFS 2.6.0 and confirm this chunk's method signatures, fields, visibility, synchronization, and exceptions are preserved when intended.
- Unit-test `PBHelper` round trips for short-circuit shared-memory ids/slots, inotify edit responses, cipher options, cipher suites, crypto protocol versions, file encryption info, per-file encryption info, and zone encryption info.
- Exercise JournalNode segment lifecycle: start a segment, finalize it, retrieve manifests with and without in-progress segments, purge old logs, and verify epoch files survive restart.
- Exercise QJM recovery: create conflicting/incomplete segments, call prepare/accept recovery, and assert only the accepted segment remains authoritative.
- Test JournalNode upgrade/finalize/rollback APIs against storage directories with current and previous layouts.
- Validate block-pool token manager dispatch for multiple block pools, missing block pools, exported key updates, token generation, access checks for each `AccessMode`, and invalid token failures.
- Verify data-encryption-key generation/retrieval for valid and stale key ids.
- Test WebHDFS and SWebHDFS delegation token identifiers return the correct token kind and persist through secret-manager FSImage state.
- Balancer tests should assert `MovedBlocks` window behavior, topology matching for same node group/rack/any-other, source/target scheduled-size updates, and exit-code mapping.
- Block placement tests should cover writer-local placement, node-group fallback, remote-rack placement, exclusion of same node-group peers, stale-node avoidance, and replica deletion candidate ordering.
- Under-construction block tests should cover expected-storage locations, recovery-id initialization, primary DataNode selection, generation-stamp verification, equality/hash behavior, and string formatting.
- Datanode statistics tests should compare aggregate capacity/cache/block-pool/xceiver counters against known `DatanodeStorageInfo` inputs.
- Startup option tests should parse names, cluster ids, rolling-upgrade flags, force/interactive formatting flags, recovery context creation, and node-role mapping.
- Replica tests should cover finalized, RBW, RWR, RUR, missing, duplicate, and unexpected-generation-stamp cases; visible length versus bytes-on-disk; writer interruption; last-checksum tracking; and stream creation.
- Short-circuit registry tests should create memory segments over domain sockets, register/unregister slots, process mlock/munlock/invalidation events, return client names for block ids, and close `NewShmInfo`.
- FSDataset policy tests should compare available-space and round-robin volume selection, including transient storage, insufficient space, and reserved RBW space.
- Rolling-log tests should verify one appender, multiple readers, current-to-previous rolling, failed roll while reading, `skipPrevious`, and iterator previous-state flags.
- WebHDFS DataNode endpoint tests should cover root/path variants for `PUT`, `POST`, and `GET`, delegation and UGI propagation, offsets/lengths, buffer size, overwrite, replication, permissions, and streaming `OpenEntity.Writer`.
- Audit logging tests should verify both base and extended audit paths, including delegation token tracking IDs, without blocking NameNode critical paths.
- Encryption-zone tests should include lock-order assertions where possible, fault injection after key generation, and FSDirectory integration.
- Edit-log tests should cover position tracking, read limits, mark/reset/skip, broken edit skipping, op scanning, max op size, object reuse, and writer serialization.
- FSImage tests should load and save legacy and protobuf images, verify txid and MD5, check string-table/ref-list deduplication, section commit order, and cancellation interval behavior.
- Safe-mode tests should cover safe block threshold, extension timing, manual safe mode, and transition out of startup safe mode.
- Inode directory/snapshot tests should cover child add/remove/search, current versus snapshot child list, snapshot add/remove/rename, snapshot quota, snapshottable feature add/remove, quota usage, content summary, recursive cleanup, rename undo for source/destination parents, and block collection.
- `INodeMap` tests should assert id lookup, replacement on put, remove, iterator behavior, size, and clear.
- `INodeReference` tests should model the documented rename-with-snapshot case: multiple references to the same inode, named versus anonymous references, parent/current-state behavior, reference removal count, destination snapshot id, metadata forwarding, and cleanup/quota propagation.

## Chunk Boundary Notes

Lines 5264-10855 begin inside the closing portion of `PBHelper` and end at the opening of `INodeReference.DstReference`. The final per-file report should merge earlier `PBHelper` chunks and later `INodeReference` subclass chunks to avoid treating this range as a complete package-level API document.
