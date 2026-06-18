# subset-b-008460 Research

Grouped research for the FoundationDB coordinator and fdbserver core files assigned to `subset-b-008460`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/Coordination.cpp -->
# sources/storage-engines/foundationdb/fdbserver/coordinator/Coordination.cpp

## Purpose
Implements the coordinator server runtime: a durable generation register, the leader-election register service, forwarding after coordinator changes, and cluster-key rewrites for existing coordinator stores. It is the server-side counterpart to the coordination interfaces used by clients, cluster controllers, and quorum-change code.

## Important APIs, Types, and Functions
- `coordinationServer(dataFolder, ccr)` creates well-known `LeaderElectionRegInterface` and `GenerationRegInterface` endpoints, opens an `OnDemandStore`, and races generation-register serving, leader-register serving, and store errors.
- `LocalGenerationReg` serves `GenerationRegReadRequest` and `GenerationRegWriteRequest` against the local store. Stored values are `GenerationRegVal { readGen, writeGen, val }`.
- `LeaderRegister` is an in-memory actor for one cluster key. It tracks candidates, leaders, waiting notifications, connected clients, and monitored leader DB info.
- `LeaderRegisterCollection` multiplexes per-key `LeaderRegister` instances and persists forwarding records under `fwdKeys` and `fwdTimeKeys`.
- `LeaderServer` validates cluster descriptors, checks forwarding state, and routes leader/open-database requests to the appropriate register.
- `coordChangeClusterKey()` and `changeClusterDescription()` rewrite persisted coordinator data when a cluster key changes.

## Control Flow
Generation reads and writes are serialized by `FlowLock`, read the current encoded `GenerationRegVal`, update read or write generation when allowed, commit the store, and reply. The read path advances `readGen` for the caller generation; the write path succeeds only if no later read or write generation blocks it.

Leader requests first go through `LeaderServer`, which checks persisted forwarding and optional cross-cluster descriptor matching. A key-specific `LeaderRegister` then collects candidacy and heartbeat reports over polling intervals, chooses the best candidate or current leader, sends notifications, and retires itself when no state and no connected clients remain. Open-database and election-result requests may lazily start monitor-leader work and keep long-polling clients attached.

Forwarding requests are durably written before being forwarded into the in-memory register. This ensures restarted coordinators can return the new connection string to clients with stale cluster files.

## State and Persistence Behavior
Persistent state lives in the coordinator `OnDemandStore` under unprefixed generation-register keys and reserved forwarding ranges. `GenerationRegVal` serialization is versioned and explicitly tied to `ProtocolVersion::GenerationRegVal`. Forwarding state stores connection strings and the timestamp when forwarding was set. Cluster-key rewrite logic scans all coordinator key/value entries, renames forwarding keys, updates forwarding values, and updates movable coordinated-state connection strings inside generation-register values.

`coordinationServer` has a simulation-only repair path for inconsistent disk queue creation: if one coordinator disk-queue file is missing after a crash, it deletes the remaining peer file so a later boot can recreate a consistent pair.

## Dependencies and Integration Points
This file depends on `OnDemandStore`, `CoordinationInterface`, `MonitorLeader`, `WorkerInterface.actor`, Flow actors, `ProtocolVersion`, and server knobs. It integrates with `CoordinatedState` through generation-register semantics, `LeaderElection.actor.cpp` through leader election and forwarding RPCs, and cluster-file persistence through `IClusterConnectionRecord`.

## Risks and Edge Cases
Generation-register access is intentionally serialized, so store latency directly affects coordination latency. The leader register has several long-polling queues and guards against unbounded notifications with `MAX_NOTIFICATIONS`. Descriptor mismatch behavior depends on `ENABLE_CROSS_CLUSTER_SUPPORT`; changing that knob affects whether requests for other cluster keys are rejected. Forwarding records can become old, and old-cluster-file use is logged after `FORWARD_REQUEST_TOO_OLD`. The cluster-key rewrite path parses stored values as `GenerationRegVal` in the fallback branch, so only expected coordinator-store layouts should be present there.

## Test Signals
The file includes `/fdbserver/Coordination/localGenerationReg/simple`, validating empty reads, successful writes, read/write generation propagation, and actor liveness. Additional coverage should come from simulation tests that exercise leader election, coordinator forwarding, quorum changes, and the disk-queue recovery path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/Coordination.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.cpp -->
# sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.cpp

## Purpose
Implements a lazy wrapper around the coordinator key-value store. The store is opened only when a caller first needs it, which lets coordinator processes avoid creating persistent files until coordination state is actually used.

## Important APIs, Types, and Functions
- `OnDemandStore::open()` creates the backing directory, constructs `keyValueStoreMemory(joinPath(folder, prefix), myID, 500e6)`, and wires its error future into the wrapper promise.
- `get()` and `operator->()` lazily open and return the `IKeyValueStore`.
- `exists()` detects already-created store files, including disk queue files and legacy `.fdb` file names.
- `getError()`, `onClosed()`, `dispose()`, and `close()` implement `IClosable` behavior.

## Control Flow
Construction records folder, UID, and prefix without touching disk. The first `get()` or `operator->()` call opens the store. Destruction calls `close()`, which closes and clears the raw store pointer if it exists. `dispose()` uses the underlying store disposal path and also clears the pointer.

## State and Persistence Behavior
The object owns a raw `IKeyValueStore*` and a `Promise<Future<Void>>` for store errors. The backing files live under `folder` with the supplied prefix. `exists()` is used by coordinator startup to decide whether persistent forwarding state needs to be loaded before any lazy open.

## Dependencies and Integration Points
The implementation uses Flow platform helpers, async file/store APIs, and `keyValueStoreMemory`. It is used by `Coordination.cpp` for generation-register data, forwarding records, and cluster-key rewrites.

## Risks and Edge Cases
`onClosed()` assumes the store is already open and dereferences `store`, so callers must not use it before `get()`. The wrapper is non-copyable but uses a raw pointer, so ownership is manual and must remain single-owner. The fixed memory limit passed to `keyValueStoreMemory` is part of coordinator-store behavior.

## Test Signals
No unit tests are embedded here. Indirect signals are coordinator tests and simulations that start coordinators with empty stores, existing disk-queue files, close/dispose paths, and store error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.h -->
# sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.h

## Purpose
Declares `OnDemandStore`, a small `IClosable` implementation that delays creation of a coordinator-local `IKeyValueStore` until first use.

## Important APIs, Types, and Functions
- Constructor accepts the data folder, local UID, and file prefix.
- `get()` and `operator->()` expose the lazily opened `IKeyValueStore`.
- `exists()` checks for persistent store artifacts without forcing an open.
- `getError()`, `onClosed()`, `dispose()`, and `close()` satisfy the close/error interface.

## Control Flow
The header keeps `open()` private so all callers go through lazy `get()`. The class is `NonCopyable`, preventing accidental multiple owners of the underlying raw store pointer.

## State and Persistence Behavior
Private state is `folder`, `myID`, `store`, `err`, and `prefix`. Persistent behavior is delegated to the concrete key-value store opened by the `.cpp` implementation.

## Dependencies and Integration Points
Includes Flow arena/random/platform headers and `IKeyValueStore`. Coordinator code depends on this type for durable local state while keeping creation cost conditional.

## Risks and Edge Cases
The declaration exposes raw-pointer access to the underlying store, so lifetime remains controlled by the wrapper and callers must not retain the pointer after `close()` or `dispose()`. The error promise is one-shot and tied to the first store open.

## Test Signals
Coverage is indirect through coordinator startup, generation register, and forwarding tests. Useful checks include verifying that `exists()` detects both disk-queue and legacy file layouts without opening a new store.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/OnDemandStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/include/fdbserver/coordinator/CoordinationServer.h -->
# sources/storage-engines/foundationdb/fdbserver/coordinator/include/fdbserver/coordinator/CoordinationServer.h

## Purpose
Public coordinator-server header exporting the actor entry points implemented in `Coordination.cpp`.

## Important APIs, Types, and Functions
- `coordinationServer(std::string dataFolder, Reference<IClusterConnectionRecord> ccf)` starts the coordinator service for a process data folder.
- `coordChangeClusterKey(std::string dataFolder, KeyRef newClusterKey, KeyRef oldClusterKey)` rewrites coordinator persistence after a cluster key update.

## Control Flow
This file contains declarations only. Runtime control flow is in `Coordination.cpp`.

## State and Persistence Behavior
The header itself owns no state. The exported functions imply access to coordinator-local persistence through `dataFolder` and cluster-file state through `IClusterConnectionRecord`.

## Dependencies and Integration Points
Includes `fdbserver/core/CoordinationInterface.h` for the coordination-related types. Included by server code that starts coordinator actors or invokes cluster-key migration.

## Risks and Edge Cases
The include guard and `#pragma once` are redundant but harmless. API signatures expose strings and `KeyRef`s; callers must ensure referenced key memory remains valid for actor execution according to Flow conventions.

## Test Signals
Validated indirectly by link tests and by any simulation that starts coordinator roles or changes cluster keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/coordinator/include/fdbserver/coordinator/CoordinationServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/AccumulativeChecksumUtil.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/AccumulativeChecksumUtil.cpp

## Purpose
Implements helper logic for mutation checksums and accumulative checksum tracking. Commit-side builders assign checksum metadata and maintain per-tag checksum state; storage-side validators buffer mutations and verify emitted accumulative checksum mutations.

## Important APIs, Types, and Functions
- `updateMutationWithAcsAndAddMutationToAcsBuilder()` overloads populate mutation checksums, set the ACS index, and add the mutation for one tag, a vector of tags, or a set of tags.
- `AccumulativeChecksumBuilder::addMutation()`, `updateTable()`, and `newTag()` update per-tag ACS state and reset state when a tag is newly assigned.
- `AccumulativeChecksumValidator::addMutation()` buffers mutations for a version and index.
- `processAccumulativeChecksum()` compares buffered aggregate checksum state with the ACS mutation, updates the validator table, and clears the buffer.
- `restore()` seeds validator state from persisted ACS state, while getter methods return and reset counters.

## Control Flow
Commit-side flow calculates a mutation checksum, stamps its ACS index, and folds the mutation checksum into `acsTable` by tag. Storage-side flow buffers mutations until an ACS mutation arrives, checks all buffered mutations share the expected version/index, aggregates them from the previous stored checksum, compares against the ACS mutation, then advances table state.

## State and Persistence Behavior
Builder state is in-memory per tag, keyed by `Tag`, and records ACS value, version, epoch, and index. Validator state is in-memory per ACS index, can be restored from persisted `AccumulativeChecksumState`, and treats a higher epoch as a reset of older state. Corruption paths throw `please_reboot()` after `SevError` trace events.

## Dependencies and Integration Points
Depends on `AccumulativeChecksumUtil.h`, mutation serialization/checksum support, log epochs, tags, protocol versions, and `CLIENT_KNOBS` feature gates. It integrates with commit proxy mutation generation and storage server mutation validation.

## Risks and Edge Cases
All main paths assert both mutation checksum and ACS knobs are enabled. Version ordering is asserted in the builder. Validator correctness depends on ACS mutations arriving after all mutations for that version/index; stale buffers are logged by `clearCache()`. New epochs deliberately discard old table state.

## Test Signals
Embedded `noSim/AccumulativeChecksum/MutationRef` verifies mutation encoding/decoding, checksum validation, ACS index serialization, and ACS mutation serialization. Broader corruption detection requires simulation or storage-server tests with ACS enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/AccumulativeChecksumUtil.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BackupPartitionMap.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/BackupPartitionMap.cpp

## Purpose
Builds backup partition key ranges from shard metrics and serializes partition metadata to JSON. The goal is to split user keyspace into roughly byte-balanced ranges for partitioned backup work.

## Important APIs, Types, and Functions
- `serializePartitionListJSON()` converts a `PartitionMap` into a JSON object with partition id and printable key bounds.
- `calculateBackupPartitionKeyRanges(KeyRangeMap<ShardTrackedData>* shards)` waits for shard metrics, sums user shard bytes, and emits contiguous partition ranges.

## Control Flow
The calculation loops until every normal-key shard has populated metrics in its `AsyncVar`. It then computes `targetBytesPerPartition` from `BACKUP_NUM_OF_PARTITIONS`, walks shards in key order, accumulates bytes, and cuts a partition whenever the target is reached or the last shard is reached.

## State and Persistence Behavior
No durable state is written. The function reads live shard metric caches and returns an in-memory vector of `KeyRange`s. JSON serialization is pure and depends only on the supplied partition map.

## Dependencies and Integration Points
Uses `KeyRangeMap`, `ShardTrackedData`, `ShardMetrics`, `StorageMetrics`, `normalKeys`, JSON builder utilities, and client knobs. It is intended for backup agents or management paths that need partitioned backup work assignment.

## Risks and Edge Cases
If metrics are delayed, the actor waits on the first missing shard metrics notification and restarts collection. Zero-byte totals can produce a target of zero, causing partition cuts at every shard or the single normal range depending on map shape. The algorithm does not split inside a shard, so highly skewed shard sizes can produce imbalanced partitions.

## Test Signals
Embedded tests cover no user shards, a single shard, varying sizes, zero-size shards, asynchronous metrics population, and many small shards. These validate contiguity and expected partition counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BackupPartitionMap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BackupProgress.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/BackupProgress.cpp

## Purpose
Tracks persisted backup worker progress and computes unfinished backup ranges by epoch and tag. It also reads backup progress metadata from system keys into a `BackupProgress` object.

## Important APIs, Types, and Functions
- `BackupProgress::addBackupStatus()` records the max saved version per epoch/tag and validates total tag count per epoch.
- `updateTagVersions()` converts saved progress into next begin versions for unfinished tag ranges.
- `getUnfinishedPartitionedBackup()` and `getUnfinishedRangePartitionedBackup()` specialize `getUnfinishedBackup()` by locality.
- `getUnfinishedBackup(int8_t locality)` returns a map keyed by `(epoch, epochEnd, tagCount)` to tag begin versions needing work.
- `getBackupProgress()` transactionally reads `backupStartedKey` and `backupProgressKeys`.

## Control Flow
Progress is accumulated per worker status. To find unfinished work, the class enumerates expected tags for each epoch, adjusts overlapping epoch begin versions, consolidates previous-epoch saved progress when needed, and emits begin versions for incomplete or missing tags. `getBackupProgress()` repeatedly performs a system-key transaction and retries through `tr.onError()`.

## State and Persistence Behavior
In-memory state includes `progress`, `epochTags`, `backupStartedValue`, and `epochInfos`. Durable state is read from FoundationDB system keys, with `ACCESS_SYSTEM_KEYS`, `PRIORITY_SYSTEM_IMMEDIATE`, and `LOCK_AWARE` options. No writes are performed here.

## Dependencies and Integration Points
Depends on `BackupProgress.h`, NativeAPI transactions, backup system key encoders/decoders, `WorkerBackupStatus`, tag locality constants, and `EpochTagsVersionsInfo`. Used by backup recruitment logic to restart incomplete backup work after worker progress updates or recovery.

## Risks and Edge Cases
Epoch begin versions can overlap, so the code tracks `lastEnd` and adjusts begin versions to prevent duplicated work. Missing progress in newer epochs can be inferred from older epochs when recovery copied ranges. Tags from older epochs that do not exist in the current epoch are ignored. The system-key range read asserts it did not hit `TOO_MANY`.

## Test Signals
Embedded `/BackupProgress/Unfinished` validates active-backup detection, initial unfinished work, and advancing the next begin version after a saved worker status.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BackupProgress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BulkDumpUtil.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/BulkDumpUtil.cpp

## Purpose
Provides storage-server bulk dump utilities for selecting dump workers, naming and writing dump files, uploading file sets, and marking dump ranges complete in system metadata.

## Important APIs, Types, and Functions
- `getSSBulkDumpTask()` chooses a target storage server from the first data-center group and records checksum servers from the remaining replicas.
- Filename/folder helpers generate versioned manifest, data SST, sample SST, and job/task folders.
- `getLocalRemoteFileSetSetting()` builds matching local and remote `BulkLoadFileSet`s.
- `writeKVSToSSTFile()` writes sorted key/value maps to RocksDB SST files.
- `dumpDataFileToLocalDirectory()` resets a local folder, writes data/sample SSTs, creates a manifest, and writes it atomically.
- `validateSourceDestinationFileSets()`, `uploadBulkDumpFileSet()`, and transport implementations move generated files by local copy or blobstore.
- `persistCompleteBulkDumpRange()` updates the `bulkDumpPrefix` key-range map after validating the task is still current.

## Control Flow
A dump task creates local files from raw range data, derives a manifest whose remote file set omits absent data/sample files, then uploads the local file set using the configured transport. Completion persistence reads the current bulk-dump key-range metadata in chunks, verifies job/task identity and submitted phase, writes the completed state over the task range, commits, and continues from the last returned range boundary.

## State and Persistence Behavior
Local disk state is reset before file generation or CP transport. Remote state is represented by uploaded manifest/data/sample paths. FoundationDB system state is updated through `krmGetRanges()` and `krmSetRange()` under `bulkDumpPrefix` with system and lock-aware transaction options.

## Dependencies and Integration Points
Depends on bulk loading/dumping metadata types, S3/blobstore helpers, RocksDB SST utilities, storage metrics types, and server knobs. It bridges bulk dump output into the same file-set and manifest structures consumed by bulk load.

## Risks and Edge Cases
Existing local output files are treated as retriable errors. Empty data ranges produce manifests without data or byte-sample file names. Source/destination validation enforces basename consistency and data/sample co-presence. Completion can throw `bulkdump_task_outdated()` if the task was cancelled, superseded, or already advanced.

## Test Signals
No embedded tests in this file. Useful signals are simulation tests for empty and non-empty dump ranges, CP and blobstore transports, stale task rejection, manifest correctness, and SST writer failure retries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BulkDumpUtil.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BulkLoadUtil.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/BulkLoadUtil.cpp

## Purpose
Implements bulk load file IO, transport, manifest parsing, metadata polling, and byte-sampling helpers. These utilities support storage-server fetch/load flows and bulk dump interoperability.

## Important APIs, Types, and Functions
- `readBulkFileBytes()`, `writeBulkFileBytes()`, and `copyBulkFile()` provide bounded async file IO with chunking and sync.
- `getBulkLoadTaskStateFromDataMove()` polls system metadata until a data-move record reaches a sufficient read version and contains `BulkLoadTaskState`.
- `doBytesSamplingOnDataFile()` scans a RocksDB SST file and writes a byte-sample SST when sampled keys exist.
- `clearFileFolder()` and `resetFileFolder()` manage local working directories.
- `bulkLoadTransportCP_impl()` and `bulkLoadTransportBlobstore_impl()` download remote file sets.
- `bulkLoadDownloadTaskFileSet()` and `bulkLoadDownloadTaskFileSets()` orchestrate downloads with retries and empty-range handling.
- Manifest helpers download job manifests, parse matching entries, and load task manifest metadata.

## Control Flow
File reads open uncached readonly files, reject oversized files, reserve output capacity, and append chunks after exact-size reads. Writes use atomic-create read/write mode, write chunks, truncate to final size, and sync. Download flows reset local folders, choose CP or blobstore transport, retry non-cancellation errors up to configured limits, and convert excessive failures to `bulkload_task_failed()` for data-distribution retry.

Manifest parsing reads a bounded file in 64 KiB chunks, preserves leftover partial lines, skips the header, and inserts entries whose ranges overlap the job range. Metadata loading downloads each referenced task manifest and adds it to a capped `BulkLoadManifestSet`.

## State and Persistence Behavior
Local filesystem state is aggressively reset for task folders. Remote state is read from CP paths or blobstore paths. FoundationDB state is read from `dataMoveKeyFor(dataMoveId)` using system-key and lock-aware options. No persistent database writes occur in this file.

## Dependencies and Integration Points
Depends on `BulkLoading`, NativeAPI, S3 client helpers, RocksDB checkpoint/SST utilities, server knobs, storage metrics, and Flow generic actors. It is used by storage-server bulk load/fetch paths and by bulk dump code for shared file operations.

## Risks and Edge Cases
The CP transport asserts a data file is present for single-file-set downloads, while multi-file-set downloads explicitly create markers for empty ranges. Blobstore downloads skip missing data files for empty ranges. Manifest and file size guards prevent unbounded memory use. Directory reset is a destructive local operation and must only target task-owned folders. Sampling retries indefinitely except cancellation, deleting partial sample files between attempts.

## Test Signals
No embedded tests here. Coverage should validate large chunked read/write, file-too-large errors, empty range handling, manifest chunk parsing with partial lines, download retry conversion to `bulkload_task_failed()`, and SST byte-sampling behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/BulkLoadUtil.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/core/CMakeLists.txt

## Purpose
Defines the `fdbserver_core` static library target, its coroutine implementation source, tests, include paths, and optional RocksDB dependencies.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_CORE_LOCAL_SRCS)` discovers local sources.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_core ...)` builds the core library.
- `add_fdbserver_link_test()` and `add_fdbserver_unit_test()` add link and unit-test coverage.
- `configure_fdbserver_common_includes()` and `target_include_directories()` configure public/private include paths.
- The `WITH_ROCKSDB` block adds RocksDB, optional liburing, LZ4, and compile definitions.

## Control Flow
CMake collects local sources, appends either `CoroFlowCoro.actor.cpp` or `CoroFlow.actor.cpp` based on `COROUTINE_IMPL`, creates the target, attaches tests, configures includes, links `fdbclient`, and conditionally wires RocksDB support.

## State and Persistence Behavior
No runtime state. Build state is expressed as target dependencies, include directories, link libraries, and compile definitions.

## Dependencies and Integration Points
Integrates with the repository's Flow/CMake helper functions, fdbserver include generation, fdbclient, RocksDB, liburing, and LZ4. It is the build aggregation point for the core files in this subset.

## Risks and Edge Cases
Source discovery makes target composition sensitive to generated or misplaced files in this directory. RocksDB include/link behavior differs depending on `WITH_LIBURING`; missing libraries or incorrect definitions would affect bulk load/dump SST utilities.

## Test Signals
The build file declares `fdbserver_corelinktest` and `fdbserver_core_test`, which are primary signals that core sources link and embedded unit tests compile/run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CoordinatedState.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/CoordinatedState.cpp

## Purpose
Implements quorum-backed coordinated state on top of generation registers, plus movable coordinated state for coordinator changes. It provides read, conflict monitoring, exclusive write, and coordinated-state migration semantics.

## Important APIs, Types, and Functions
- `waitAndSendRead()` and `waitAndSendWrite()` send generation-register RPCs, optionally through hostname retry paths, with simulation buggified delays.
- `CoordinatedStateImpl::read()`, `onConflict()`, and `setExclusive()` implement the public `CoordinatedState` lifecycle.
- `replicatedRead()` and `replicatedWrite()` issue requests to all state servers and wait for quorum responses.
- `MovableValue` encodes `MaybeTo`, `Active`, and `MovingFrom` states.
- `MovableCoordinatedStateImpl::read()`, `setExclusive()`, `move()`, and `moveTo()` manage quorum-change handoff.
- `updateCCSInMovableValue()` rewrites a connection string embedded in a serialized movable value.

## Control Flow
`CoordinatedState::read()` first reads with generation zero to discover current generations, chooses a new unique generation above conflicts, then reads again at that generation to lock in read intent and retrieve the value. `setExclusive()` writes with that generation and throws `coordinated_state_conflict()` if any replica reports a higher generation. `onConflict()` polls for later generations while the state remains usable.

`replicatedRead()` races a majority of non-empty replies against enough empty replies to prove a majority non-empty cannot be achieved, then returns the best reply by write/read generation. `replicatedWrite()` requires all replicas for initial creation and majority for later writes.

Movable state writes an `Active` encoded value normally. During move, it verifies new coordinators are empty, writes `MovingFrom` to new coordinators, confirms old state was not concurrently changed, writes `MaybeTo` to old state, asks leaders to change coordinators, and throws `coordinators_changed()`.

## State and Persistence Behavior
Durable state is stored in coordinator generation registers under the cluster key. `MovableValue` serialization is protocol-version gated. In-memory state tracks stage, selected generation, conflict generation, doomed flag, initial flag, and outstanding actor collection. Migration persists transitional values to old and new coordinator quorums.

## Dependencies and Integration Points
Depends on cluster connection records, coordination interfaces, leader election coordinator-change support, Flow actor utilities, and server knobs. It is a central dependency for cluster controller leadership and quorum-change workflows.

## Risks and Edge Cases
Initial writes require all replicas, making coordinator creation stricter than normal writes. The read algorithm distinguishes empty and non-empty quorums to preserve consistency under partial initialization. Movable-state migration has several conflict and timeout paths and relies on the new coordinator set being uninitialized. `updateCCSInMovableValue()` assumes the input is a versioned `MovableValue`.

## Test Signals
No embedded tests in this file. Coverage should come from coordinator quorum, cluster-file change, coordinator move, conflict, and simulation buggification tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CoordinatedState.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CoordinationInterface.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/CoordinationInterface.cpp

## Purpose
Constructs coordination RPC interface objects for remote and local use. It binds generation-register, leader-election, and server-coordinator endpoint sets to well-known tokens and task priorities.

## Important APIs, Types, and Functions
- `GenerationRegInterface(NetworkAddress)` creates remote read/write endpoints.
- `GenerationRegInterface(INetwork*)` creates local well-known read/write endpoints at coordination priority.
- `LeaderElectionRegInterface(NetworkAddress)` creates remote leader-election endpoints and inherits client leader endpoints.
- `LeaderElectionRegInterface(INetwork*)` creates local candidacy, election-result, heartbeat, and forward endpoints.
- `ServerCoordinators(ccr)` expands a cluster connection string into leader-election and state-server interfaces for hostnames and coordinator addresses.

## Control Flow
Constructors either wrap remote well-known endpoints from addresses or allocate local well-known endpoints on the current network. `ServerCoordinators` reads hostnames and coordinator network addresses from the connection string and appends matching interface instances to leader and state vectors.

## State and Persistence Behavior
No durable state. Interface objects contain endpoint metadata and optional hostname information used by retry paths.

## Dependencies and Integration Points
Depends on `CoordinationInterface.h`, endpoint well-known tokens, `TaskPriority::Coordination`, and cluster connection records. Used by coordinator servers, coordinated state, leader election, and clients that contact coordinators.

## Risks and Edge Cases
Endpoint token compatibility is critical; changing token bindings breaks wire compatibility between clients and coordinators. Hostname-backed and address-backed paths must remain consistent because callers choose retry behavior based on `hostname.present()`.

## Test Signals
Covered by link tests and by any coordinator/leader-election simulation. Direct tests should verify well-known token assignment and that `ServerCoordinators` preserves connection-string hostnames and addresses.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/CoordinationInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/DataMovement.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/DataMovement.cpp

## Purpose
Maps `DataMovementReason` enum values to numeric priorities and back. This centralizes data-distribution reason priority ordering from server knobs.

## Important APIs, Types, and Functions
- `buildPriorityMappings()` initializes static reason-to-priority and priority-to-reason maps.
- `dataMovementPriority(DataMovementReason reason)` returns the configured priority for a reason.
- `priorityToDataMovementReason(int priority)` returns the reason associated with a priority.

## Control Flow
The first call builds static maps from enum constants and `SERVER_KNOBS` priority values. It then constructs the inverse map and asserts that every priority is unique. Public functions look up with `.at()`, so unknown reasons or priorities throw standard map lookup errors/assert in debug depending on context.

## State and Persistence Behavior
No durable state. Static in-process maps persist for the life of the process after first construction.

## Dependencies and Integration Points
Depends on `DataMovement.h` and server knobs. Used wherever data-distribution logic needs to compare, persist, or decode data movement priority/reason metadata.

## Risks and Edge Cases
Duplicate configured priorities are fatal via trace and assert. Because the maps are static, knob values must be finalized before first use; later knob mutation would not rebuild mappings. Sentinel reasons intentionally map to negative values.

## Test Signals
No embedded tests. Useful tests should verify one-to-one priority mappings for all enum values and fail on duplicate priorities.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/DataMovement.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/FDBSimulationPolicy.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/FDBSimulationPolicy.cpp

## Purpose
Installs and maintains FoundationDB-specific simulation fault policy. It controls whether simulated process kills, corruption, storage replica fault injection, and datacenter death are allowed under the current database replication configuration.

## Important APIs, Types, and Functions
- `stringToFDBExtraDatabaseMode()` parses configuration strings into `FDBExtraDatabaseMode`.
- `FDBSimulationPolicy` implements `ISimulationPolicy` methods: `datacenterDead()`, `shouldRunVersionValidation()`, `canSwapToMachine()`, `checkInjectedCorruption()`, `hasCapability()`, and `canKillProcesses()`.
- `installFDBSimulationPolicy()` registers the policy with `g_simulator`.
- `fdbSimulationPolicyState()` returns the singleton mutable policy state.
- `updateFDBSimulationPolicy()` refreshes policy state from `DatabaseConfiguration`.
- `setFDBSimulationPolicyRemoteTLogPolicy()` overrides remote TLog policy.

## Control Flow
Policy decisions derive locality groups for alive/dead processes and validate them against storage, TLog, remote TLog, and satellite replication policies. `canKillProcesses()` may downgrade dangerous kill types to reboot-style actions if too many processes are dead, not enough would remain, or auto-configuration would lack coordinator quorum across unique machines. Capability checks expose TSS/fault-injection modes to simulation components.

## State and Persistence Behavior
All state is process-local singleton `FDBSimulationPolicyState`. It stores replication policies, region IDs, satellite IDs, TSS mode, corrupt worker map, desired coordinator count, extra database mode, and flags such as `allowLogSetKills`. No persistent cluster state is written.

## Dependencies and Integration Points
Depends on simulator interfaces, replication policy utilities, locality data, `DatabaseConfiguration`, and simulator process info. It is installed into the global simulator and is consulted by fault injection, process killing, version validation, and corruption paths.

## Risks and Edge Cases
The safety logic is highly configuration-sensitive, especially with usable regions, remote TLogs, satellite fallback policies, and write anti-quorums. Unique-machine quorum checks can change kill type even when replication policies appear satisfied. Extra databases disable version validation and machine swapping. Unknown extra database mode strings log and assert.

## Test Signals
No embedded unit tests. Simulation workloads that vary replication modes, kill types, satellite settings, TSS modes, and process localities are the relevant coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/FDBSimulationPolicy.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LatencyBandConfig.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/LatencyBandConfig.cpp

## Purpose
Parses and compares latency-band configuration JSON for get-read-version, read, and commit request categories.

## Important APIs, Types, and Functions
- `operator==` and `operator!=` for `RequestConfig` compare dynamic type and fields.
- `RequestConfig::fromJson()` loads the `bands` array.
- `ReadConfig::fromJson()` also loads `max_read_bytes` and `max_key_selector_offset`.
- `CommitConfig::fromJson()` also loads `max_commit_bytes`.
- `LatencyBandConfig::parse()` validates JSON against `JSONSchemas::latencyBandConfigurationSchema` and returns an optional config.
- `LatencyBandConfig` equality compares GRV, read, and commit configs.

## Control Flow
Parsing returns empty optional for empty strings, invalid JSON, or schema mismatch. Valid JSON is wrapped as `JSONDoc`, then each request-category subdocument populates the corresponding config. Equality first checks dynamic type for request configs, then delegates to type-specific `isEqual()` implementations.

## State and Persistence Behavior
No durable state. Parsed configs hold in-memory sets of band thresholds and optional request limits.

## Dependencies and Integration Points
Depends on management API JSON helpers, schema validation, and the latency band schema. Consumers can store configuration as a `ValueRef` and call `parse()` before applying instrumentation or request classification.

## Risks and Edge Cases
`ReadConfig::isEqual()` and `CommitConfig::isEqual()` static-cast after the top-level operator checks type identity; direct calls with the wrong subtype would be unsafe. Invalid configuration is logged and ignored by returning empty optional. Band insertion into a set deduplicates thresholds and loses original order.

## Test Signals
No embedded tests. Useful coverage includes empty config, malformed JSON, schema mismatch, full valid configs, equality across same and different request config types, and limit-field parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LatencyBandConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LeaderElection.actor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/LeaderElection.actor.cpp

## Purpose
Implements client-side leader election against the coordinator leader-election register. It submits candidacy, observes coordinator nominees, handles coordinator forwarding, publishes the elected leader interface, and maintains leadership through heartbeats.

## Important APIs, Types, and Functions
- `submitCandidacy()` repeatedly sends `CandidacyRequest`s to one coordinator and updates a shared nominee slot.
- `buggifyDelayedAsyncVar()` wraps an `AsyncVar` with delayed propagation for simulation eventual-consistency testing.
- `changeLeaderCoordinators()` sends `ForwardRequest`s to old coordinators and waits for quorum.
- `tryBecomeLeaderInternal()` is the main actor for candidacy, election observation, forwarding, leadership acquisition, and heartbeat maintenance.

## Control Flow
The actor optionally delays startup for poor recruitment priority. It then repeatedly creates a new `LeaderInfo` change ID, submits candidacy to every coordinator, watches the aggregate nominees via `getLeader(nominees)`, and updates `outSerializedLeader` when another leader is known. If coordinators report forwarding, it writes forwarding to a quorum, persists the new connection string, and throws `coordinators_changed()`.

When this candidate is elected by a connected quorum, it publishes its serialized interface and enters heartbeat mode. Each heartbeat round sends `LeaderHeartbeatRequest` to coordinators and races majority-true, majority-false, timeout, and priority changes. Majority false or timeout causes the actor to release leadership and restart candidacy.

## State and Persistence Behavior
Most state is actor-local: nominee slots, `myInfo`, candidacy futures, previous change ID, and leadership flag. Persistent behavior occurs through `coordinators.ccr->setAndPersistConnectionString()` when forwarding is detected. Coordinator-side forwarding persistence is handled by `Coordination.cpp`.

## Dependencies and Integration Points
Depends on failure monitor/locality headers, coordination interfaces, monitor-leader types, server knobs, Flow actors, and `getLeader()` logic from the leader-election API. It integrates with cluster controllers and other leader candidates that need a serialized leader interface.

## Risks and Edge Cases
Forwarding can wait up to 20 seconds for old coordinator quorum before proceeding with the received connection string. Bad candidate timeout changes IDs when a candidate appears to block election progress. Heartbeat timeout gives up leadership under poor communication even without majority false. Buggified async variables intentionally delay observed leader publication in simulation.

## Test Signals
No embedded tests in this file. Coverage should come from simulation leader-election workloads, coordinator forwarding/quorum-change tests, priority-change tests, and network partition scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LeaderElection.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LogSystemConfig.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/LogSystemConfig.cpp

## Purpose
Implements comparison, introspection, and formatting helpers for the log system configuration: current TLog sets, old generations, log routers, backup workers, localities, and epochs.

## Important APIs, Types, and Functions
- `TLogSet::toString()`, `operator==()`, and `isEqualIds()` format and compare TLog set topology.
- `OldTLogConf::operator==()` and `isEqualIds()` compare old log generations.
- `LogSystemConfig::toString()`, `isEqual()`, `isEqualIds()`, and `isNextGenerationOf()` compare full configurations and generation transitions.
- `getRemoteDcId()`, `allLocalLogs()`, `numLogs()`, `allPresentLogs()`, `allSharedLogs()` expose log membership.
- `getLocalityForDcId()` maps a datacenter ID to likely tag localities based on current and old logs.
- `hasTLog()`, `hasLogRouter()`, `hasBackupWorker()`, and `getEpochEndVersion()` query membership and epoch metadata.

## Control Flow
Comparison functions first check structural fields and then compare endpoint identity, presence, tokens, or IDs depending on strictness. Collection helpers iterate current and old log sets, filter by locality or presence, and return vectors or booleans. Shared log collection uniquifies `(sharedTLogID, address)` pairs and asserts one address per shared ID.

## State and Persistence Behavior
No state is mutated. Functions inspect serialized/in-memory log system configuration objects that are persisted elsewhere by recovery and master logic.

## Dependencies and Integration Points
Depends on `LogSystemConfig.h`, TLog/backup worker interfaces, tag locality constants, UID/network address utilities, and replication policy `info()` strings. It is used by recovery, log recruitment, backup, and status/diagnostic code that needs to compare or inspect log topology.

## Risks and Edge Cases
Strict equality includes endpoint tokens for present logs and backup workers, while ID equality deliberately ignores endpoint tokens. `isEqualIds()` returns true if any current TLog set matches any set in the other config, not if the entire config matches. `getLocalityForDcId()` uses counts and may return invalid locality values if no matching logs exist.

## Test Signals
No embedded tests. Coverage should validate equality semantics across token changes, old-generation transitions, shared-log uniqueness, remote DC detection, and membership queries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/LogSystemConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MasterInterface.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/MasterInterface.cpp

## Purpose
Provides explicit template instantiations for `MasterInterface` RPC serialization support.

## Important APIs, Types, and Functions
- `template class ReplyPromise<MasterInterface>;`
- `template struct NetSAV<MasterInterface>;`

## Control Flow
No runtime control flow beyond compilation/linkage of template instantiations.

## State and Persistence Behavior
No state or persistence behavior.

## Dependencies and Integration Points
Includes `fdbserver/core/MasterInterface.h`. The explicit instantiations ensure the master interface can be used in reply promises and network serialization/address vector contexts without relying solely on implicit instantiation in downstream translation units.

## Risks and Edge Cases
The file is intentionally tiny; removing it can surface link errors rather than local compile errors. Any change to `MasterInterface` serialization requirements may need corresponding instantiations here or in related files.

## Test Signals
The primary signal is successful linkage of fdbserver core and components that use `MasterInterface` RPCs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MasterInterface.cpp -->
