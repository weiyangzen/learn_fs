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
