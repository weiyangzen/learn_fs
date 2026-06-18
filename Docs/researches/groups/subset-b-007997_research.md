# Research: subset-b-007997

Grouped research for Apache Ozone container-service disk balancer policy, EC reconstruction, and key-value container implementation files. Each section is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/DefaultContainerChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/DefaultContainerChoosingPolicy.java

## Purpose
`DefaultContainerChoosingPolicy` is the default datanode disk-balancer policy for choosing a source volume, destination volume, and movable container. It is deliberately conservative: it snapshots volume usage, compares fixed effective utilization to an ideal usage plus/minus threshold, then returns a single `ContainerCandidate` only when moving that container will not overfill the selected destination.

## Important APIs and Types
The public API is `chooseVolumesAndContainer(OzoneContainer, MutableVolumeSet, Map<HddsVolume, Long>, Set<ContainerID>, double, Set<State>)`. It implements `ContainerChoosingPolicy` and returns either `ContainerCandidate` or `null`. Internally it uses `DiskBalancerVolumeCalculation.VolumeFixedUsage`, `newVolumeFixedUsage`, `getIdealUsage`, and `computeUtilization` to calculate candidate volume states. A `ThreadLocal<Cache<HddsVolume, Iterator<Container<?>>>>` keeps a per-thread Guava cache of source-volume container iterators with one-hour expiry.

## Control Flow
The method takes a global `ReentrantLock`, obtains an immutable volume list, filters non-positive capacity volumes, sorts by utilization and storage ID, calculates ideal/lower/upper thresholds, and exits early when the highest and lowest utilization volumes already fall within the threshold band. It always uses the highest-utilized volume as source, then tries destination volumes from lowest upward when utilization is lower than the source and usable space is positive. `chooseContainer` walks the cached source iterator and filters containers that are absent from the live container set, already in progress, zero-sized, in a non-movable state, too large for destination usable space, or would push destination utilization past the upper threshold. When a container is selected, the destination volume's committed bytes are incremented by the actual container size before returning.

## State and Persistence
The class persists no durable state. Its mutable state is the provided lock, destination committed-byte reservation, and the thread-local iterator cache. The `deltaMap` is read as a caller-provided transient adjustment to usage. The iterator cache can observe stale containers, so `chooseContainer` revalidates each candidate against `ozoneContainer.getContainerSet()` and invalidates the iterator when exhausted.

## Dependencies and Integration Points
It integrates with `DiskBalancerService` through `ContainerChoosingPolicyFactory` and the disk-balancer configuration default. It depends on `OzoneContainer` for controller/container-set access, `MutableVolumeSet` and `HddsVolume` for volume state, and container protobuf `State` for movability. Tests reference it directly in `TestDefaultContainerChoosingPolicy`, `TestDiskBalancerService`, `TestDiskBalancerTask`, and performance-oriented integration coverage in `TestDiskBalancerPolicyPerformance`.

## Risks and Test Signals
The main risks are stale iterator behavior, reservation accuracy when later movement fails, and threshold edge conditions because the code uses strict `<`/`>` and `>=` comparisons. The global lock limits concurrent decision races, but committed bytes are changed outside durable persistence and must be corrected by the larger disk-balancer workflow. Existing tests cover default policy selection, skipping in-progress containers, movable state filtering, and performance/concurrency scenarios; useful additional signals would include cache-expiry/stale-removal behavior and exact threshold-boundary assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/DefaultContainerChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.container.diskbalancer.policy` as the package containing policy classes for the DiskBalancer service. It does not define runtime code, but it anchors Javadoc and package-level ownership for disk-balancer selection policies.

## Important APIs and Types
There are no functions or classes in this file. The relevant exported types in the package include `ContainerChoosingPolicy`, `ContainerCandidate`, and `DefaultContainerChoosingPolicy`.

## Control Flow
No control flow is present. Runtime behavior is implemented by classes in the package, especially the default policy that chooses source/destination volumes and containers.

## State and Persistence
No state is held or persisted. The file only supplies package documentation.

## Dependencies and Integration Points
It integrates with Java package documentation and the disk-balancer implementation by declaring the package. Its practical integration point is indirect: classes in this package are loaded by `ContainerChoosingPolicyFactory` and `DiskBalancerService`.

## Risks and Test Signals
The only material risk is documentation drift: the package currently contains policy classes and the description remains accurate. There is no direct test coverage needed for this descriptor; behavioral tests belong to package classes such as `TestDefaultContainerChoosingPolicy`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECContainerOperationClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECContainerOperationClient.java

## Purpose
`ECContainerOperationClient` wraps the container-level RPC operations needed by erasure-coded offline reconstruction. It centralizes single-datanode pipeline construction and lifecycle management for list, create recovering container, close container, read-state-then-delete, and delete operations.

## Important APIs and Types
Constructors accept either an existing `XceiverClientManager` or a `ConfigurationSource` plus `CertificateClient`. `listBlock` returns `BlockData[]` for a container on a datanode. `closeContainer`, `deleteContainerInState`, and `createRecoveringContainer` delegate to `ContainerProtocolCalls`. `singleNodePipeline` builds a closed `Pipeline` containing one `DatanodeDetails` and a replica-index map.

## Control Flow
Each RPC method acquires a client from `XceiverClientManager` using a single-node pipeline, performs the container protocol call, and releases the client in a `finally` block with `invalidateClient=false`. `createClientManager` installs a `ClientTrustManager` only when security is enabled and configures a small cached client manager. `deleteContainerInState` first calls `readContainer`, checks the current container state against the caller-provided acceptable state set, and only then sends `deleteContainer`.

## State and Persistence
The only long-lived state is the `XceiverClientManager` and its underlying client cache. The class does not write local disk state. Remote operations change container state on target datanodes: creating RECOVERING replicas, closing containers, or deleting acceptable-state replicas.

## Dependencies and Integration Points
`ECReconstructionCoordinator` uses this client for source block listing and target container lifecycle. It depends on SCM pipeline/client classes, datanode protocol protobufs, security certificate/trust-manager classes, Ozone security detection, and `BlockData` protobuf conversion. Integration tests in `TestContainerCommandsEC` use this class directly for EC container command validation.

## Risks and Test Signals
`listBlock` maps protobuf conversion failures to `null` array entries, which can later surprise callers unless they tolerate missing block data. `deleteContainerInState` explicitly documents a race between read and delete: the check is not atomic with deletion, so callers must restrict use to contexts where deleting a newly changed container is acceptable. Test signals include EC reconstruction integration tests, direct `ECContainerOperationClient` use in `TestContainerCommandsEC`, and cleanup-on-failure scenarios that exercise state-gated deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECContainerOperationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCommandInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCommandInfo.java

## Purpose
`ECReconstructionCommandInfo` is an immutable-ish command adapter that extracts the fields needed by datanode EC reconstruction from `ReconstructECContainersCommand`. It converts command source and target lists into sorted maps keyed by replica index.

## Important APIs and Types
The constructor accepts `ReconstructECContainersCommand`. Public getters expose deadline, container ID, EC replication config, and SCM term. Package-private getters expose unmodifiable sorted source and target maps. `toString` formats command type, replication, missing indexes, source nodes, and target nodes for task debug logging.

## Control Flow
Construction copies scalar command fields, then builds `sourceNodeMap` from each `DatanodeDetailsAndReplicaIndex`. It builds `targetNodeMap` by iterating command target datanodes and pairing each target with the corresponding byte from `missingContainerIndexes`. Duplicate replica indexes keep the first entry because the merge function returns `v1`.

## State and Persistence
The object stores command data in memory only. It performs no persistence and does not mutate the source command. It returns unmodifiable map views, which protects callers from modifying its maps through the getters.

## Dependencies and Integration Points
`ECReconstructionCoordinatorTask` owns one instance and uses it to construct an `AbstractReplicationTask` and invoke `ECReconstructionCoordinator.reconstructECContainerGroup`. `ReconstructECContainersCommandHandler` creates tasks from SCM commands. Tests in `TestReplicationSupervisor` build command info instances for task scheduling, duplicate handling, and equality behavior.

## Risks and Test Signals
The main risk is positional coupling between `missingContainerIndexes` and `targetDatanodes`: if their lengths diverge, `byteAt(i)` can fail or targets can be mapped incorrectly. Duplicate indexes are silently collapsed to the first value, which may hide malformed commands. Existing test signals come from reconstruction command handler and replication supervisor tests; stronger unit coverage would validate mismatched target/index lengths and duplicate-index command behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCommandInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinator.java

## Purpose
`ECReconstructionCoordinator` implements the datanode-side workflow for reconstructing missing replicas in an erasure-coded container group. It lists block metadata from healthy source replicas, calculates safe block-group lengths, creates target RECOVERING containers, decodes and streams missing chunks, issues putBlock, closes the targets, and cleans up partial targets on failure.

## Important APIs and Types
The main public method is `reconstructECContainerGroup(long, ECReplicationConfig, SortedMap<Integer,DatanodeDetails>, SortedMap<Integer,DatanodeDetails>)`. `reconstructECBlockGroup` is `@VisibleForTesting` and handles one block group. Helper APIs include `calcBlockLocationInfoMap`, `getECBlockOutputStream`, `rebuildInputPipeline`, `getBlockDataMap`, `calcEffectiveBlockGroupLen`, and `getTermOfLeaderSCM`. It owns `ECContainerOperationClient`, read/write executor pools, `BlockInputStreamFactory`, `TokenHelper`, `ContainerClientMetrics`, and `ECReconstructionMetrics`.

## Control Flow
Container reconstruction rebuilds an input pipeline from source nodes, lists blocks from each source, drops orphaned stripes missing a putBlock entry for any source index, creates block-location info using the minimum observed block-group length, creates RECOVERING containers on all targets, reconstructs each block group, closes successfully created targets, and increments success metrics. Any exception increments failure metrics, attempts to delete only target containers created by the current task when they are UNHEALTHY or RECOVERING, and rethrows. Block reconstruction separates missing indexes into those that require data reconstruction and those that only need empty block metadata. It opens `ECBlockReconstructedStripeInputStream`, creates target output streams, loops over recovered chunks, writes non-empty buffers, waits for futures, and finally executes putBlock on all target streams.

## State and Persistence
Local state includes reusable byte buffers, thread pools, RPC client manager, and metrics counters. Remote persistent state changes happen on target datanodes: RECOVERING containers are created, chunks and block metadata are written, and containers are closed or deleted. Tokens are generated per container/block with `TokenHelper`. The coordinator mutates the retrieved `OzoneClientConfig` to enable checksum verification during reconstruction reads.

## Dependencies and Integration Points
The coordinator is constructed by `DatanodeStateMachine` and used by `ECReconstructionCoordinatorTask`, which is submitted by `ReconstructECContainersCommandHandler` through the replication supervisor. It depends on Ozone client EC read/write streams, SCM block/pipeline types, datanode RPC calls, security token signing, executor configuration from `OzoneClientConfig`, and metrics from `ContainerClientMetrics` and `ECReconstructionMetrics`.

## Risks and Test Signals
Important risks are partial remote side effects, orphan block filtering correctness, minimum-length recovery semantics for inconsistent block lengths, and future/write failure handling. A null block from `ECContainerOperationClient.listBlock` conversion failure would be unsafe if not filtered before dereference. The write executor is memoized and only shut down if initialized; read executor is always shut down in `close`. Tests in `TestContainerCommandsEC` cover full/partial stripe reconstruction, missing indexes, retry-triggered failures, orphan blocks, and cleanup-on-failure. `TestECContainerRecovery`, `TestReconstructECContainersCommandHandler`, and `TestReplicationSupervisor` provide integration and scheduling signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinatorTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinatorTask.java

## Purpose
`ECReconstructionCoordinatorTask` adapts one EC reconstruction command into a runnable replication task understood by the datanode replication supervisor. It supplies metrics naming, deadline/term metadata, status transitions, logging, equality, and delegation to the coordinator.

## Important APIs and Types
It extends `AbstractReplicationTask` and implements `Runnable`. The constructor takes an `ECReconstructionCoordinator` and `ECReconstructionCommandInfo`, passing container ID, deadline, and SCM term to the superclass. It defines metric name `ECReconstructions` and description segment `EC reconstructions`.

## Control Flow
`run()` delegates to `runTask()`. `runTask` logs the command, records a monotonic start time, calls `reconstructECContainerGroup` with container ID, replication config, source map, and target map, then marks status `DONE` on success. It catches any `Exception`, marks status `FAILED`, and logs elapsed time with the failure. `getCommandForDebug` returns a precomputed string from command info.

## State and Persistence
The task itself persists no durable state. In-memory state includes the coordinator reference, command info, debug string, and superclass status/deadline/term fields. Durable effects are performed by the delegated coordinator.

## Dependencies and Integration Points
`ReconstructECContainersCommandHandler` creates this task in response to SCM commands. The replication supervisor schedules it and uses `AbstractReplicationTask` status/metric fields. Tests in `TestReconstructECContainersCommandHandler` verify command handling and metrics name, while `TestReplicationSupervisor` checks scheduling interactions and task de-duplication.

## Risks and Test Signals
Equality and hash code are based only on container ID, so simultaneous reconstruction commands for the same container but different target sets or terms collapse as equal. That is likely intentional for supervisor de-duplication, but it is a risk if SCM ever needs concurrent distinct reconstruction work for the same container. `runTask` catches broad `Exception`, so callers rely on status and logs rather than thrown failures. Tests cover supervisor behavior, but direct task tests for null coordinator misuse and same-container/different-command equality would strengthen coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinatorTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionMetrics.java

## Purpose
`ECReconstructionMetrics` is the metrics source for datanode EC reconstruction coordination. It records container reconstruction attempts/failures and reconstructed block-group attempts/failures.

## Important APIs and Types
The class is annotated with Hadoop metrics annotations and registers under the source name `ECReconstructionMetrics` in the Ozone metrics context. `create()` registers a new instance with `DefaultMetricsSystem`; `unRegister()` unregisters it. Increment APIs are `incBlockGroupReconstructionTotal`, `incBlockGroupReconstructionFailsTotal`, `incReconstructionTotal`, and `incReconstructionFailsTotal`. Getter APIs expose reconstruction total and block-group reconstruction total.

## Control Flow
Metrics registration is explicit through `create`. The coordinator increments success counters after all target containers are closed and increments failure counters in the exception cleanup path. The counters are `MutableCounterLong` fields injected by the metrics system based on `@Metric`.

## State and Persistence
All state is in memory inside Hadoop metrics counters. The class does not persist data to disk. Metrics visibility is through the process metrics system and ends when unregistered or when the process exits.

## Dependencies and Integration Points
`ECReconstructionCoordinator` receives an instance and records reconstruction results. `DatanodeStateMachine` creates the coordinator and metrics, and tests use `ECReconstructionMetrics.create()` in reconstruction integration scenarios. The class depends on Hadoop metrics2, `DefaultMetricsSystem`, and `OzoneConsts.OZONE`.

## Risks and Test Signals
Registration uses a fixed source name, so repeated `create()` without `unRegister()` can conflict or leak metrics in long-running test JVMs. Failure counters do not have public getters, which makes direct assertion harder. Existing integration tests in `TestContainerCommandsEC` assert success totals and block-group counts; additional tests could cover failure counter increments and unregister/re-register behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/package-info.java

## Purpose
This package descriptor labels `org.apache.hadoop.ozone.container.ec.reconstruction` as containing erasure-coding reconstruction-related classes. The comment has a spelling typo ("codding"), but the intent is clear.

## Important APIs and Types
The file exports no methods or classes. Key package types include `ECReconstructionCoordinator`, `ECReconstructionCoordinatorTask`, `ECReconstructionCommandInfo`, `ECContainerOperationClient`, and `ECReconstructionMetrics`.

## Control Flow
No runtime control flow exists in this descriptor. Runtime flow starts when SCM sends a reconstruct EC containers command, the datanode command handler creates a task, and the coordinator executes reconstruction.

## State and Persistence
No state is held or persisted. It only affects package-level documentation.

## Dependencies and Integration Points
The descriptor integrates with Java package documentation. Its package is integrated at runtime with datanode state machine construction, reconstruct-command handling, replication supervision, EC block streams, and container protocol RPCs.

## Risks and Test Signals
The documentation typo is harmless but visible in generated Javadocs. There is no direct test requirement; package behavior is covered by tests for the concrete EC reconstruction classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainer.java

## Purpose
`KeyValueContainer` is the concrete datanode container implementation for Ozone key-value containers. It owns lifecycle transitions, on-disk directory and `.container` file creation/update, DB sync/compaction during close/export, import/export/copy workflows, scanner entry points, and synchronization around container metadata.

## Important APIs and Types
It implements `Container<KeyValueContainerData>`. Major APIs include `create`, `delete`, `hasBlocks`, `markContainerForClose`, `markContainerUnhealthy`, `markContainerForDelete`, `quasiClose`, `close`, `update`, `importContainerData`, `exportContainerData`, `copyContainerDirectory`, `scanMetaData`, `scanData`, and lock methods. It also exposes pending put-block cache methods and path helpers. It uses `KeyValueContainerData`, `VolumeSet`, `VolumeChoosingPolicy`, `ContainerPacker`, `DBHandle`, `BlockUtils`, and `KeyValueContainerUtil`.

## Control Flow
Creation takes the volume-set read lock, chooses a volume, reserves committed space, selects schema/path layout, verifies the container is new, creates metadata/chunks/DB directories, writes the YAML `.container` file through a temp file and atomic rename, and retries other volumes on general IO failures. Close/quasi-close first flush RocksDB WAL outside the write lock, reacquires the write lock, syncs again, updates state and the `.container` file, and clears pending put-block cache. Export takes the write lock, validates state, compacts/removes DB for non-schema-v3, downgrades to read lock while packing, and synchronizes schema-v3 dump generation with `dumpLock`. Import unpacks to a tmp/final destination, loads descriptor data, parses counters, rewrites local metadata, and cleans up partial data on failure.

## State and Persistence
Persistent state includes container directories, chunks directory, DB files, schema-v3 dump files, metadata tables, and the YAML `.container` descriptor. In-memory state includes a non-fair read/write lock, `dumpLock`, `pendingPutBlockCache`, and the config-derived empty-dir check flag. State transitions are persisted by `updateContainerFile`; failures generally restore the prior state unless the container has been marked UNHEALTHY.

## Dependencies and Integration Points
`KeyValueHandler` creates and manipulates these containers for client/container commands. `ContainerReader` reconstructs instances at startup. Replication/import/export paths use `ContainerPacker` and `ContainerImporter`. Data and metadata scanners call `scanMetaData` and `scanData`, which delegate to `KeyValueContainerCheck`. Disk balancer and replication tests construct instances directly. Schema handling integrates with `VersionedDatanodeFeatures` and `OzoneConsts.SCHEMA_V3`.

## Risks and Test Signals
This class has high persistence and concurrency risk. Atomic `.container` update failures call volume failure handling and may leave temp files. `hasReadLock()` appears to call `tryLock()` without unlocking, so it behaves like acquisition rather than ownership inspection. Import failure cleanup can move/delete local directories and remove schema-v3 DB rows. Export lock downgrading must avoid concurrent mutation while still permitting packing. Tests in `TestKeyValueContainer`, `TestKeyValueContainerMarkUnhealthy`, `TestTarContainerPacker`, replication/importer tests, container reader tests, scanner integration tests, and block/delete command tests provide broad signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerCheck.java

## Purpose
`KeyValueContainerCheck` implements integrity scans for key-value containers. `fastCheck` verifies container metadata structure and descriptor consistency. `fullCheck` is a superset for closed/quasi-closed/unhealthy containers that walks block metadata, verifies chunk files and checksums, and builds a Merkle tree of observed data.

## Important APIs and Types
The constructor receives `ConfigurationSource` and a live `KeyValueContainer`. Public APIs are `fastCheck()` returning `MetadataScanResult` and `fullCheck(DataTransferThrottler, Canceler)` returning `DataScanResult`. Key helpers include `scanMetadata`, `checkContainerFile`, `scanData`, `scanBlock`, `verifyChecksum`, `blockInDBWithLock`, and `loadContainerData`.

## Control Flow
`fastCheck` runs `scanMetadata`, converts collected `ContainerScanError`s into a result, and reports deleted if in-memory state became DELETED. Metadata scanning checks the container directory, metadata directory, `.container` file existence/readability, descriptor checksum/type/id/db type/metadata path, and chunks directory presence. `fullCheck` first runs `fastCheck`; if metadata is healthy it opens the DB, iterates block entries with the container's schema-aware unprefixed key filter, and scans each block unless deletion is detected. Chunk scanning locates layout-specific chunk files, handles EC empty padding blocks, verifies per-checksum bytes using `Checksum`, throttles reads, records observed checksums into a `ContainerMerkleTreeWriter`, and suppresses errors if a missing file corresponds to a block concurrently deleted from DB under container read lock.

## State and Persistence
The checker does not modify persistent state. It loads a separate `KeyValueContainerData` instance from disk and uses live in-memory container data to detect deletion during scans. It reads DB files and chunk files, uses a static `DirectBufferPool`, and builds scan result objects containing errors and a Merkle tree.

## Dependencies and Integration Points
`KeyValueContainer.scanMetaData` and `scanData` instantiate this class. Background and on-demand scanner services consume the results. It depends on container YAML utilities, block DB helpers, layout-version chunk lookup, checksum utilities, direct buffer pooling, scanner result/error types, and HDFS throttling/cancelation classes.

## Risks and Test Signals
The scanner intentionally runs much of the data scan without holding the container lock, so it must distinguish real corruption from concurrent block deletion. Buffer return is manual; checksum verification paths should not leak direct buffers on unexpected runtime errors. Missing chunks with zero-length EC padding are not treated as corruption. Tests in `TestKeyValueContainerCheck` cover no-corruption, corrupt metadata, corrupt chunks, checksum output, deleted containers, and scan result behavior across schema/layout variants. Scanner integration tests cover background and on-demand invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerData.java

## Purpose
`KeyValueContainerData` is the in-memory metadata model for a key-value container and the data shape persisted into the `.container` YAML file. It extends `ContainerData` with key-value-specific paths, DB type, schema version, delete transaction tracking, block commit sequence ID, finalized blocks, and schema-aware DB key formatting.

## Important APIs and Types
Important getters/setters include metadata path, DB file, schema version, DB type, block commit sequence ID, and delete transaction ID. `buildContainerReplicaProto` creates datanode container reports. `getContainerReplicaProtoState` maps container protobuf states to SCM replica states. Finalized block APIs manage a concurrent set and `clearFinalizedBlock(DBHandle)` deletes finalized-block table entries. DB key APIs include `getBlockKey`, `getDeletingBlockKey`, `getLatestDeleteTxnKey`, `getBcsIdKey`, `getBlockCountKey`, `getBytesUsedKey`, `getPendingDeleteBlockCountKey`, `getPendingDeleteBlockBytesKey`, filters, `startKeyEmpty`, and `containerPrefix`.

## Control Flow
Construction initializes type, ID, layout, size, origin identifiers, delete transaction ID, and finalized block set. YAML field initialization extends base container YAML fields with metadata path, chunks path, DB type, and schema version. Counter update methods keep in-memory statistics and metadata table values aligned, using batch operations for delete accounting. Schema-aware formatting prefixes keys with the schema-v3 container key prefix and leaves schema-v1/v2 keys unprefixed.

## State and Persistence
The object itself is in memory, but many fields are persisted in `.container` YAML and metadata DB tables. `updateAndCommitDBCounters` and `resetPendingDeleteBlockCount` write RocksDB metadata table values. `deleteTransactionId` is monotonic via `max`. `finalizedBlockSet` is concurrent and cleared from both memory and DB during container close.

## Dependencies and Integration Points
`KeyValueContainer` owns this data object and delegates report/state/path behavior to it. Block managers, delete services, scanners, schema migration tools, and metadata inspector all use its schema-aware keys and filters. It integrates with `DatanodeSchemaThreeDBDefinition` for schema-v3 prefixes and `VersionedDatanodeFeatures` for storage-space-distribution metadata.

## Risks and Test Signals
Schema-aware key formatting is critical: using raw constants instead of helper methods can corrupt schema-v3 shared DB layouts. The copy constructor resets delete transaction ID to zero, which is safe only where callers expect a fresh metadata object. Counter updates subtract released bytes/counts and assume caller-provided values are consistent with in-memory statistics. Tests across `TestKeyValueContainer`, `TestBlockManagerImpl`, block deletion tests, schema compatibility/migration tests, and metadata inspector tests exercise these keys and counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerMetadataInspector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerMetadataInspector.java

## Purpose
`KeyValueContainerMetadataInspector` is an opt-in container inspector for diagnosing and optionally repairing aggregate metadata in key-value container DBs. It emits JSON reports showing stored DB metadata, recomputed aggregate values, chunks-directory status, and detected mismatches.

## Important APIs and Types
The inspector implements `ContainerInspector`. Modes are `REPAIR`, `INSPECT`, and `OFF`, controlled by the system property `ozone.datanode.container.metadata.inspector` or constructor injection. Main APIs are `load`, `unload`, `isReadOnly`, `process`, `inspectContainer`, `getDBMetadataJson`, `getAggregatePendingDelete`, and schema-specific pending-delete counters. Reports are logged to `ContainerMetadataInspectorReport`.

## Control Flow
`load` validates the system property once and enables inspect/repair or disables the inspector. `process` no-ops in OFF mode, verifies the container is `KeyValueContainerData`, builds JSON from DB metadata, recomputed block/byte aggregates, pending delete aggregates, and chunks directory info, then calls `checkAndRepair`. Repairable mismatches include block count, used bytes, pending delete block count, pending delete bytes when the layout feature is finalized, and missing chunks directory. In INSPECT mode repair actions are recorded as not repaired; in REPAIR mode the metadata table or filesystem is updated.

## State and Persistence
The class holds only the current mode. In REPAIR mode it persists changes to the container metadata table and can create the chunks directory. It does not directly update the `.container` YAML descriptor. Reports are JSON strings sent to a logger and returned by the overload used in tests/debug tools.

## Dependencies and Integration Points
`ContainerInspectorUtil` registers this inspector for datanode startup inspection. `InspectSubcommand` in the debug CLI constructs it in inspect mode for explicit inspection. `KeyValueContainerUtil` references its pending-delete aggregation logic. It depends on Jackson JSON nodes, Ozone DB table iterators, schema-specific datanode store implementations, deleted-block transactions, and `VersionedDatanodeFeatures`.

## Risks and Test Signals
Repair mode writes DB metadata based on a full scan, so schema selection and prefix filters must be correct. The pending-delete byte repair action currently returns `false` even after a successful `put`, so JSON can report `"repaired": false` despite the write. Schema-v2 pending delete iteration scans the whole delete transaction table, while schema-v3 uses the container prefix. Tests in `TestKeyValueContainerMetadataInspector` cover load modes, inspect vs repair behavior, aggregate mismatch reports, chunk directory repair, and report logging; schema upgrade tests also rely on inspector-compatible aggregate logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerMetadataInspector.java -->
