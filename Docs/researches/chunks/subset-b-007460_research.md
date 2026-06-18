# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.6.0.xml lines 10856-16839

## Purpose

This chunk is a JDiff public API description for Hadoop HDFS 2.6.0. It spans the tail of NameNode inode-reference APIs, NameNode HA/storage/snapshot management APIs, WebHDFS NameNode resource methods, DataNode-to-NameNode server protocol value types, short-circuit local-read shared-memory APIs, HDFS command-line and offline viewer tools, low-level HDFS utility classes, and the start of WebHDFS authentication/JSON/range-read helpers.

Because this is generated API metadata rather than Java implementation source, the research signal is public surface area, declared exceptions, synchronization markers, inheritance, Javadocs, and integration contracts. The slice starts inside `INodeReference.DstReference` and ends inside `org.apache.hadoop.hdfs.web.ParamFilter`, so both boundaries require neighboring chunk context during merge.

## Important APIs, Types, and Functions

NameNode namespace and persistence APIs dominate the first half of the range:

- `INodeReference.DstReference`, `INodeReference.WithCount`, and `INodeReference.WithName` model snapshot/rename references. `WithCount` owns reference-count operations and `WITHNAME_COMPARATOR`; `WithName` stores a fixed local name and last-snapshot id; `DstReference` exposes `getDstSnapshotId`, `cleanSubtree`, and `destroyAndCollectBlocks`.
- `INodesInPath` reports path resolution state through `getLatestSnapshotId`, `getPathSnapshotId`, indexed `getINode`, `getLastINode`, and logging.
- `JournalManager.CorruptionException` represents edit-log gaps or corrupt edit files. `JournalSet` implements `JournalManager` over multiple journals with `format`, `startLogSegment`, `finalizeLogSegment`, `selectInputStreams`, `chainAndMakeRedundantStreams`, retention/purge/recovery methods, upgrade/rollback hooks, and manifest creation through `getEditLogManifest`.
- `NameNode.NameNodeHAContext` implements `HAContext` for HA state transitions and operation checks: state setters/getters, active/standby service start/stop, write locks, `checkOperation(OperationCategory)`, and stale-read policy.
- `NameNodeMXBean` and `NameNodeStatusMXBean` expose operational JMX state: version, capacity, safemode, rolling upgrade, cache, blocks/files, live/dead/decommissioning DataNodes, name-dir and journal status JSON, transaction info, compile info, corrupt files, distinct DataNode versions, role, state, address, and security mode.
- `NameNodeLayoutVersion.Feature`, `NNStorage.NameNodeDirType`, `NNStorage.NameNodeFile`, `NNStorageRetentionManager`, `Quota`, and `Quota.Counts` define layout-version feature flags, fsimage/edit storage file naming and directory typing, checkpoint/edit-log retention, and namespace/diskspace quota counters.
- `RenewDelegationTokenServlet` renews HFTP delegation tokens over HTTP. `TransferFsImage.HttpGetFailedException` and `HttpPutFailedException` carry failed image-transfer HTTP response codes.

HA client-side connection APIs appear under `org.apache.hadoop.hdfs.server.namenode.ha`:

- `AbstractNNFailoverProxyProvider` implements Hadoop `FailoverProxyProvider`, tracks `fallbackToSimpleAuth`, and requires subclasses to declare whether logical HA URIs are used.
- `ConfiguredFailoverProxyProvider` lazily creates proxies, performs synchronized failover across configured NameNode addresses, closes all opened proxies, and requires a logical URI.
- `IPFailoverProxyProvider` uses one proxy behind infrastructure-managed IP failover; `performFailover` is intentionally a no-op and `useLogicalURI` is false.
- `WrappedFailoverProxyProvider` adapts old `FailoverProxyProvider` implementations and assumes logical URI semantics.

Metrics and snapshot APIs are extensive:

- `NameNodeMetrics` creates and publishes NameNode activity metrics, including file/block operation counters, snapshot operation counters, transaction/sync latencies, block/cache block report latencies, safe-mode time, and image-transfer latencies.
- `DirectoryWithSnapshotFeature.DirectoryDiff`, `DirectoryDiffList`, `FileDiff`, and `FileDiffList` hold per-snapshot directory/file differences, including created/deleted children lists and file sizes.
- `FSImageFormatPBSnapshot.Loader` and `.Saver` load and serialize protobuf FSImage snapshot sections: inode references, snapshot lists, and snapshot diffs. The saver notes that inode references are serialized only after inode directories and snapshot diffs.
- `Snapshot.Root`, `SnapshotFSImageFormat`, and `SnapshotFSImageFormat.ReferenceMap` support legacy FSImage read/write of snapshots, directory/file diff lists, created-list nodes, and reference-counted inode references.
- `SnapshotManager` is the core public manager for snapshottable directories: `setSnapshottable`, `resetSnapshottable`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `diff`, listing, FSImage `write`/`read`, MXBean registration/shutdown, and bean conversion.

HTTP, protocol, and local-read APIs include:

- `NamenodeWebHdfsMethods` is the NameNode-side WebHDFS JAX-RS resource. It exposes static invocation context helpers and root/path variants for PUT, POST, GET, and DELETE with many typed parameter classes for delegation, proxy user, path, operation, ACLs, XAttrs, snapshots, rename options, create-parent behavior, offsets, lengths, token kinds/services, and excluded DataNodes.
- `BalancerBandwidthCommand`, `DatanodeStorage`, `DatanodeStorage.State`, `DatanodeStorageReport`, `ReceivedDeletedBlockInfo`, `ReceivedDeletedBlockInfo.BlockStatus`, `RemoteEditLog`, `RemoteEditLogManifest`, `StorageBlockReport`, `StorageReceivedDeletedBlocks`, and `StorageReport` are wire/value types used by DataNode reports, block received/deleted notifications, balancer commands, storage utilization, and remote edit-log manifests.
- `DfsClientShm`, `DfsClientShmManager.PerDatanodeVisitorInfo`, `DfsClientShmManager.Visitor`, `DomainSocketFactory`, `DomainSocketFactory.PathInfo`, `PathState`, `ShortCircuitCache.CacheVisitor`, `ShortCircuitCache.ShortCircuitReplicaCreator`, `ShortCircuitReplicaInfo`, and `ShortCircuitShm` with `ShmId`, `Slot`, `SlotId`, and `SlotIterator` define short-circuit local read state, domain-socket path enablement, shared-memory segment allocation, replica validity, anchoring, and cleanup.

Tooling and utility APIs in the tail include:

- `DFSHAAdmin`, `GetConf`, and `GetStoragePolicies` implement HDFS-specific HA administration and configuration/storage-policy CLI commands.
- `OfflineEditsViewer.Flags`, `TeeOutputStream`, `WebImageViewer`, and `XmlImageVisitor` support edits/image offline inspection, recovery/fix flags, tee output, read-only WebHDFS serving of fsimage content, and XML export.
- `AtomicFileOutputStream` provides `.tmp`-then-rename atomic file output with `abort`; `DataTransferThrottler` implements synchronized bandwidth throttling with optional cancellation; `ByteArrayManager.Conf` carries byte-array pool parameters.
- `Diff` and its nested `Container`, `Element`, `ListType`, `Processor`, and `UndoInfo` model ordered create/delete/modify deltas used heavily by snapshots.
- `EnumCounters`, `EnumCounters.Map`, `EnumCounters.Factory`, and `EnumDoubles` provide enum-indexed counters/doubles used by quotas, storage metrics, and accounting code. `Holder` is a mutable wrapper.
- `LightWeightHashSet` and `LightWeightLinkedSet` are low-memory, non-thread-safe set implementations with explicit load-factor growth/shrink behavior and fail-fast modification tracking.
- `LongBitFormat` packs named bit fields into a `long`. `MD5FileUtils` reads, writes, verifies, renames, and locates Unix `md5sum`-style `.md5` files. `ReadOnlyList.Util` creates views and binary-search helpers. `RwLock` declares normal and long read locks plus write locks.
- `XMLUtils.InvalidXmlException`, `XMLUtils.Stanza`, and `XMLUtils.UnmanglingError` are XML parsing/value-bag helpers.
- `AuthFilter`, `ByteRangeInputStream`, `ByteRangeInputStream.URLOpener`, `JsonUtil`, `KerberosUgiAuthenticator`, and the start of `ParamFilter` cover WebHDFS auth, seekable HTTP byte-range streams, JSON conversion for protocol objects, and Jersey request filtering.

## Control Flow and Execution Model

Most APIs are orchestration boundaries around HDFS state machines. `JournalSet` fans edit-log operations across a collection of journal managers, selects redundant input streams from all journals, chains streams for replay, and exposes upgrade, rollback, purge, and recovery phases. Its class doc states methods are not internally synchronized and rely on `FSEditLog` synchronization, while `getEditLogManifest` is explicitly synchronized.

HA control flows are split between server and client. `NameNodeHAContext` lets `HAState` start and stop active/standby services, prepare standby shutdown, lock the namespace, and validate an `OperationCategory`, raising `StandbyException` when an operation is not allowed. Client-side failover providers return `ProxyInfo` objects and expose synchronized proxy creation/close paths; configured failover rotates between configured NameNodes, while IP failover delegates switching to external infrastructure.

Snapshot control flow records namespace mutations as diffs and persists them in FSImage. `SnapshotManager` assumes its caller holds the `FSNamesystem` lock and optionally the `FSDirectory` lock. Creation locates a snapshottable root, checks name/quota constraints, and returns the snapshot path; deletion collects blocks and removed inodes for later block-map cleanup; diff compares two snapshots or a snapshot against current state. `FSImageFormatPBSnapshot` and `SnapshotFSImageFormat` form the load/save paths for snapshot sections, reference maps, and diff lists.

WebHDFS control flow enters `NamenodeWebHdfsMethods` through verb-specific root/path handlers. Each handler receives typed query/path parameters, a `UserGroupInformation`, optional delegation and doAs identity, and returns a JAX-RS `Response` or throws `IOException`/`InterruptedException`. `AuthFilter` supplies Hadoop-Auth configuration to the servlet filter chain, `KerberosUgiAuthenticator` falls back to UGI when SPNEGO is unavailable, and `ParamFilter` begins the Jersey request-filter integration at the chunk tail.

Short-circuit read control flow allocates local shared-memory slots representing replicas. `DomainSocketFactory` resolves path state and can disable either short-circuit usage or all domain-socket usage for a path. `ShortCircuitShm` allocates/registers/unregisters slots under synchronized methods, while `DfsClientShm.handle` marks a segment stale when its domain socket closes and frees empty segments. Slot flags track valid/invalid, anchorable/unanchorable, and anchor counts.

Utility control flows are mostly local algorithms. `Diff` maintains created and deleted lists, supports undo for create/delete/modify, projects a diff onto previous/current lists, and combines with posterior diffs through well-documented state cases. `DataTransferThrottler` synchronizes calls that account bytes and sleep when throughput exceeds the configured period/bandwidth. `AtomicFileOutputStream` writes to a temporary path and commits on close or abandons through `abort`.

## State and Persistence Behavior

Persistent NameNode state appears in edit logs, FSImage sections, MD5 sidecar files, and snapshot diffs:

- `JournalSet` manages edit-log segment lifecycle, manifests, in-progress segment recovery, and retention. Corruption is represented as transaction gaps or corrupt edit files.
- `NNStorage.NameNodeDirType` distinguishes image-only, edits-only, and combined storage directories. `NNStorageRetentionManager` inspects NameNode storage directories and delegates actual deletion/copying to a purger.
- Snapshot state is held as snapshottable directory metadata, snapshot counters/counts, snapshot root directories, inode references, and directory/file diff lists. The protobuf loader/saver and legacy `SnapshotFSImageFormat` APIs serialize this state to FSImage.
- `Quota.Counts`, `EnumCounters`, and `EnumDoubles` hold mutable in-memory accounting state; quota counts are namespace and diskspace counters.
- `RemoteEditLog` and `RemoteEditLogManifest` expose persisted edit-log transaction ranges to remote consumers.
- `MD5FileUtils` persists `.md5` checksum files next to data files and verifies fsimage/checkpoint integrity using `MD5Hash`.
- `AtomicFileOutputStream` persists files via a temporary file and close-time rename, with a documented weaker replacement behavior on Windows.

Several APIs expose transient operational state rather than durable state: JMX beans and metrics, WebHDFS request-local invocation data, HA proxy fallback-to-simple-auth booleans, DataNode storage reports, and shared-memory short-circuit read slots. `LightWeightHashSet` and `LightWeightLinkedSet` maintain in-memory hash-table capacity, size, and modification version; they are not thread-safe. `ShortCircuitShm` maps a shared memory segment and uses slot flags/counters as process-local coordination state backed by OS shared memory.

## Dependencies and Integration Points

The chunk integrates with core Hadoop/HDFS subsystems:

- NameNode namespace: `FSNamesystem`, `FSDirectory`, `INode`, `INodeDirectory`, `INodeFile`, `BlocksMapUpdateInfo`, snapshot classes, quota classes, and FSImage loaders/savers.
- Edit logs and storage: `JournalManager`, `EditLogOutputStream`, `RemoteEditLogManifest`, `NamespaceInfo`, `Storage`, `StorageInfo`, `LogsPurgeable`, and retention purgers.
- HA and RPC: `HAContext`, `HAState`, `HAAdmin`, `HAServiceTarget`, `FailoverProxyProvider`, retry policies, logical URIs, `StandbyException`, and service failure exceptions.
- Metrics and management: Hadoop Metrics2 `JvmMetrics`, NameNode metrics sinks, JMX MXBeans, and JSON strings returned for NameNode status.
- WebHDFS and security: JAX-RS `Response`, Jersey `ResourceFilter`/`ContainerRequestFilter`, servlet filters, Hadoop `UserGroupInformation`, tokens, SPNEGO/Kerberos authentication, delegation-token parameters, ACL/XAttr parameters, and WebHDFS JSON payloads.
- DataNode protocol: `DatanodeInfo`, `DatanodeCommand`, `StorageType`, blocks, storage reports, block report arrays, received/deleted block info, and balancer bandwidth commands.
- Local read stack: UNIX domain sockets, `DomainPeer`, `DomainSocketWatcher`, shared memory through `FileInputStream`, `ExtendedBlockId`, short-circuit replica cache/creator APIs, and invalid-token signaling.
- Java/Hadoop utility stack: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `Configuration`, `Tool`, `Configured`, Guava `Function`, collections, comparators, and XML/JSON helpers.

## Risks and Edge Cases

- This is a public API diff XML. It exposes signatures and docs but not method bodies, constants, annotations, or full enum member sets in this chunk. Implementation-specific conclusions should be verified against Java sources.
- The chunk boundaries are incomplete: `INodeReference.DstReference` begins before line 10856, and `ParamFilter` continues after line 16839.
- `JournalSet` depends on external `FSEditLog` synchronization except for the synchronized manifest method. Direct use without the expected higher-level lock can race edit-log lifecycle operations.
- Snapshot operations assume `FSNamesystem` and sometimes `FSDirectory` locks are already held. Calling `SnapshotManager` methods outside that locking discipline risks inconsistent namespace, diff, quota, or block cleanup state.
- Snapshot diff and inode-reference serialization order is strict. The protobuf saver states that inode references can only be serialized after inode directories and snapshot diffs; violating this can break FSImage load.
- HA failover behavior differs sharply by provider: configured failover rotates proxies and logical URI token handling is required; IP failover does not perform application-level switching and relies on infrastructure plus retry policies.
- `LightWeightHashSet` and `LightWeightLinkedSet` do not support null elements and are not thread-safe. Iterators rely on modification tracking, so concurrent mutation can fail fast.
- `DataTransferThrottler` is shared and synchronized. Long sleeps or cancellation behavior can affect multiple threads using one throttler.
- `ShortCircuitShm` uses shared memory and domain sockets. Slot registration, stale segment handling, anchor counts, and valid bits must be coordinated carefully to avoid stale local reads or leaked mapped segments.
- `ByteRangeInputStream` reopens HTTP connections after seeks and tracks `startPos`, `currentPos`, and `fileLength`. Incorrect resolved URL handling, range support, or EOF handling can surface as wrong-position reads.
- JSON conversion in `JsonUtil` is part of the WebHDFS contract. Field naming, token encoding, XAttr encoding, ACL status, checksum, located-block, and exception mappings are compatibility-sensitive.
- `AtomicFileOutputStream` is not fully atomic on Windows according to its doc; tests and recovery logic should account for delete-then-rename behavior there.

## Test Signals

Useful validation for this API surface should come from HDFS unit/integration suites around the owning subsystems:

- Edit-log and storage tests should cover `JournalSet` segment start/finalize, input stream selection, redundant stream chaining, manifest generation, purging, recovery of unfinalized segments, and upgrade/rollback delegation.
- HA tests should exercise `NameNodeHAContext` operation-category checks, active/standby service transitions, stale-read behavior, `ConfiguredFailoverProxyProvider` failover/proxy close, IP failover no-op behavior, and logical URI token handling.
- Snapshot tests should cover set/reset snapshottable, nested snapshottable checks, snapshot create/delete/rename quotas and duplicate names, snapshot diff results, block/inode collection on deletion, FSImage save/load round trips for snapshot sections and inode references, and `Diff.combinePosterior` edge cases.
- WebHDFS tests should hit root and non-root PUT/POST/GET/DELETE paths with delegation, doAs, ACLs, XAttrs, snapshots, rename options, offsets/lengths, token operations, and excluded DataNodes; JSON round trips should validate `JsonUtil` conversions for tokens, statuses, located blocks, content summaries, checksums, ACLs, XAttrs, and remote exceptions.
- DataNode protocol tests should cover storage ID generation/equality, storage-state and storage-type propagation, received/deleted block status code conversion, storage reports, block reports, balancer bandwidth commands, and remote edit-log ordering/equality.
- Short-circuit read tests should simulate domain-socket path disablement, shared-memory slot allocation/register/unregister, stale segment handling after socket closure, anchor/unanchor transitions, invalid block-token propagation, and cache visitor/creator callbacks.
- Utility tests should cover `AtomicFileOutputStream` commit/abort behavior, throttler bandwidth updates and cancellation, `LightWeightHashSet` growth/shrink/poll/iterator behavior, ordered polling in `LightWeightLinkedSet`, enum counter arithmetic, `LongBitFormat` overflow/packing boundaries, `.md5` read/write/rename/verify, read-only list views and binary search, and XML stanza missing/multiple child behavior.

## Chunk Boundary Notes

Lines 10856-16839 start inside the `INodeReference.DstReference` class and include its constructor/method tail but not the class header. They end after the `ParamFilter` constructor and the beginning of `getRequestFilter`, before the rest of WebHDFS filter APIs. The merge lane should reconcile this report with adjacent chunks before producing final per-file conclusions for the complete `Apache_Hadoop_HDFS_2.6.0.xml` API diff.
