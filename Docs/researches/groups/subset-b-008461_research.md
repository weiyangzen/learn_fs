# subset-b-008461 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MoveKeys.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/MoveKeys.cpp

## Purpose
`MoveKeys.cpp` implements the core system-key transactions and coordination logic used by FoundationDB data distribution to add/remove storage servers and move key ranges between teams. It supports both legacy logical key movement (`keyServers` src/dest lists with boolean `serverKeys`) and shard-encoded location metadata (`DataMoveMetaData`, shard ids in `keyServers` and `serverKeys`, checkpoints, and bulk-load data moves). The file is heavily actor-based and is designed to tolerate retries, concurrent DD generations, removed storage servers, TSS mappings, and simulation fault injection.

## Important APIs, types, and functions
- `DDEnabledState` tracks in-memory DD enablement states: enabled, snapshot, and blob-restore-preparing. Its `trySet*` methods enforce UID ownership of transitions.
- `MoveKeysLock`, `readMoveKeysLock`, `takeMoveKeysLock`, `checkMoveKeysLock`, and `checkPersistentMoveKeysLock` coordinate exclusive DD ownership through `moveKeysLockOwnerKey` and `moveKeysLockWriteKey`.
- `moveKeys`, `rawStartMovement`, `rawCheckFetchingState`, and `rawFinishMovement` select logical versus shard-encoded move paths based on `SERVER_KNOBS->SHARD_ENCODE_LOCATION_METADATA`.
- Logical movement is handled by `startMoveKeys`, `checkFetchingState`, and `finishMoveKeys`.
- Shard-encoded movement is handled by `startMoveShards`, `finishMoveShards`, `checkDataMoveComplete`, `cleanUpDataMove`, `cleanUpDataMoveCore`, `cleanUpDataMoveBackground`, and `cleanUpSingleShardDataMove`.
- Storage server membership is handled by `addStorageServer`, `canRemoveStorageServer`, `removeStorageServer`, and `removeKeysFromFailedServer`.
- Helper paths include `removeOldDestinations`, two overloads of `unassignServerKeys`, `additionalSources`, `pickReadWriteServers`, `addReadWriteDestinations`, `waitForShardReady`, and metadata audit helpers.

## Control flow
The high-level data move sequence is `moveKeys`: sort destination team, start movement, start a fetching-state signal actor, finish movement, then defensively set `dataMovementComplete`. In the logical path, `startMoveKeys` reads overlapping `keyServers` ranges in bounded KRM batches, extends source lists with healthy read-write destinations when needed, sets the destination team in `keyServers`, removes stale destination ownership from `serverKeys`, and marks the new destinations as owning the range. `finishMoveKeys` rereads the same metadata, waits for destination storage servers and optionally TSS pairs to become readable at the transaction read version, then clears `dest` and promotes the destination team to source ownership.

The shard-encoded path persists a `DataMoveMetaData` record. `startMoveShards` creates or resumes metadata, validates conflicting data moves, optionally creates RocksDB checkpoints for physical moves, writes destination shard ids into `keyServers`, writes data-move shard ids into destination `serverKeys`, and can bind a bulk-load task to the data move. `finishMoveShards` waits for destination readiness, promotes destination servers into `keyServers` source ownership, updates every involved `serverKeys` range, deletes checkpoints, clears the data-move record, and completes a bulk-load task when present. Partial KRM pages are handled by shrinking the active range and looping.

Cleanup reverses or finalizes partial shard-encoded moves. `cleanUpDataMoveCore` marks metadata as deleting, restores `keyServers` to sources, preserves unrelated physical shards in `serverKeys`, unassigns old destinations, and deletes checkpoints. If cleanup races before metadata creation, it writes a deleting tombstone and schedules `cleanUpDataMoveBackground` to remove the placeholder later.

## State and persistence behavior
The file mutates FDB system keyspaces: `keyServersPrefix`, per-server `serverKeysPrefixFor`, `serverListKeyFor`, `serverTagKeyFor`, `serverTagHistoryRangeFor`, `tagLocalityListKeyFor`, `serverMetadataKeys`, `serverMetadataChangeKey`, `moveKeysLock*`, `dataMoveKeyFor`, checkpoint keys, TSS mapping and quarantine keys, and bulk-load task ranges. Most transactions use `PRIORITY_SYSTEM_IMMEDIATE` and `ACCESS_SYSTEM_KEYS`; lock-sensitive paths also use `LOCK_AWARE`. KRM updates use `krmSetRangeCoalescing` or `krmSetPreviouslyEmptyRange` to maintain coalesced range maps.

Persistence invariants are symmetric: `keyServers` and `serverKeys` must agree about ownership, and shard-encoded moves must keep `DataMoveMetaData` phase/range/checkpoint state aligned with KRM entries. Physical moves create pending checkpoint metadata and later clear it through `deleteCheckpoints`.

## Dependencies and integration points
The code integrates with `fdbclient/SystemData.h` KRM encoders, `ManagementAPI` for DD mode changes, `StorageServerInterface` RPCs (`getShardState`), `TSSMappingUtil`, `BulkLoadUtil`, `ReadYourWritesTransaction`, `TxnCounters`, and Flow actor primitives. It is called by data distribution when recruiting, moving, or removing shards and is also used by failure handling when removing keys from failed servers.

## Risks and edge cases
Major risks are split-brain DD ownership, partial KRM pages, stale server lists, conflicts with existing data moves, transaction retry storms, and inconsistent location metadata. The lock protocol protects against overlapping DD generations by comparing previous owner/write IDs and self-conflicting writes. `finishMoveKeysBackoff` adds capped jittered exponential backoff for `transaction_too_old`. The audit helpers can detect `keyServers`/`serverKeys` corruption and set DD mode to security mode. Removed destination servers throw `move_to_removed_server`; conflicting physical moves are either cleaned up or cancelled depending on policy. TSS readiness is best effort and eventually skipped to avoid blocking production data movement.

## Test signals
There is a direct `TEST_CASE("/fdbserver/MoveKeys/finishMoveKeysBackoff")` validating the backoff envelope and retry knob. Many `CODE_PROBE` and `buggify` points exercise multi-transaction paths, retries, removed servers, and injected `transaction_too_old`. Trace events such as `RelocateShard_StartMoveKeys*`, `RelocateShard_FinishMoveKeys*`, `StartMoveShards*`, `FinishMoveShards*`, `CleanUpDataMove*`, and `CheckLocationMetadata*` are the main runtime/debug signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MoveKeys.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MutationTracking.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/MutationTracking.cpp

## Purpose
`MutationTracking.cpp` provides optional debug-only tracing for mutations that touch configured keys or ranges. It is guarded by `MUTATION_TRACKING_ENABLED` and explicitly rejected in clean/release builds. When disabled, the public functions return disabled `TraceEvent` objects with near-zero behavioral effect.

## Important APIs, types, and functions
- `debugKeys` and `debugRanges` are global debug filters containing label/key or label/range pairs.
- `debugMutationEnabled` checks a `MutationRef` against those filters and emits a `MutationTracking` trace event with label, context, version, and mutation.
- `debugKeyRangeEnabled` wraps a `KeyRangeRef` as a `MutationRef::DebugKeyRange`.
- `debugTagsAndMessageEnabled` parses a commit blob made of `TagsAndMessage` records and calls `debugMutation` for actual mutation payloads.
- Public functions `debugMutation`, `debugKeyRange`, and `debugTagsAndMessage` dispatch to enabled implementations only when the compile-time flag is set.

## Control flow
Single-mutation tracking first checks explicit debug keys. Clear ranges and debug key ranges use containment/intersection checks against mutation ranges; point mutations compare or test containment against `param1`. It then checks configured debug ranges and returns the first enabled trace event. Commit-blob tracking walks serialized messages, handles version headers, skips log-adapter messages, parses and discards protocol/span context messages, and deserializes ordinary mutations for debug matching.

## State and persistence behavior
There is no database persistence. The only state is process-local debug filter vectors. The code reads serialized commit blob bytes using `BinaryReader` with the current network protocol version and may update the reader protocol version when decoding `LogProtocolMessage`.

## Dependencies and integration points
The implementation depends on `FDBTypes`, `SystemData`, `LogProtocolMessage`, `SpanContextMessage`, and `OTELSpanContextMessage`. Its call sites can annotate specific commit, fetch, or storage flows with `DEBUG_MUTATION` style tracing without changing the data path when mutation tracking is disabled.

## Risks and edge cases
The filter lists are compiled globals and default to broad examples, including an "Everything" range. Enabling this in high-volume contexts can generate large traces and expose key/value data in logs. The code uses a raw peek of four bytes for `VERSION_HEADER`, so callers must pass well-formed commit blobs. Adapter messages are intentionally skipped to avoid duplicate traces.

## Test signals
There are no local tests in this file. Useful validation signals are `MutationTracking` trace events with `Label`, `At`, `Version`, `Mutation`, and optional `MessageTags`; absence of events when disabled is expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/MutationTracking.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/OpenDatabase.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/OpenDatabase.cpp

## Purpose
`OpenDatabase.cpp` builds a client `DatabaseContext` from server-side `ServerDBInfo`. It is the bridge used by server actors that need to issue ordinary client-style transactions while tracking cluster interface changes.

## Important APIs, types, and functions
- `extractClientInfo` watches `AsyncVar<ServerDBInfo>` and publishes a shrunk `ClientDBInfo` into another `AsyncVar`.
- `openDBOnServer` creates a `DatabaseContext` with task priority, lock-awareness, and optional locality load balancing, then initializes global config triggers.

## Control flow
`extractClientInfo` loops forever: copy `db->get().client`, call `shrinkProxyList` with cached commit and GRV proxy lists, publish with `setUnconditional`, and wait on `db->onChange()`. `openDBOnServer` allocates the target `AsyncVar<ClientDBInfo>`, starts `extractClientInfo` as the database context maintenance future, supplies local locality only when locality load balancing is enabled, and registers actor-lineage profiler global-config triggers.

## State and persistence behavior
There is no direct persistence. State is in async variables and the created `DatabaseContext`. `shrinkProxyList` preserves stable proxy interface objects across updates where possible to reduce churn.

## Dependencies and integration points
The code depends on `DatabaseContext`, `MonitorLeader` proxy helpers, `GlobalConfig`, `ActorLineageProfiler`, and `WorkerInterface.actor.h` server DB structures. Server subsystems use `openDBOnServer` to get a `Database` backed by the same cluster metadata they already observe.

## Risks and edge cases
If `ServerDBInfo` changes rapidly, `extractClientInfo` publishes every change without backpressure. Misconfigured locality load balancing can cause the created context to omit locality data. Global config is initialized from the current client info pointer and the source `AsyncVar`, so lifetime and mutation assumptions are tied to `ServerDBInfo`.

## Test signals
There are no local tests. Integration behavior is visible through client transaction success from server processes and profiler config effects for `samplingFrequency`, `samplingProfilerUpdateFrequency`, `samplingWindow`, and `samplingProfilerUpdateWindow`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/OpenDatabase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/QuietDatabase.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/QuietDatabase.cpp

## Purpose
`QuietDatabase.cpp` implements the simulation/test utility that waits for a cluster to become quiet: no meaningful data movement, bounded log/storage queues, stable DD activity, no non-TSS recruitment, acceptable version offset, and bounded multi-region lag. It also includes helper functions for discovering workers and querying runtime metrics through event-log request interfaces.

## Important APIs, types, and functions
- `getWorkers`, `getMasterWorker`, `getDataDistributorWorker`, `getCoordWorkers`, `getStorageServers`, and `getStorageWorkers` discover cluster actors from `ServerDBInfo` and system keys.
- Metric helpers include `getDataInFlight`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getDataDistributionActive`, `getStorageServersRecruiting`, `getVersionOffset`, and `getDatacenterLag`.
- `repairDeadDatacenter` and `reconfigureAfter` are simulation-only helpers for fearless/multi-region tests.
- `enableConsistencyScanInSim` and `disableConsistencyScanInSim` manage consistency scan state around quieting.
- `QuietDatabaseChecker` records failed gates, trace output, and simulation timeout assertions.
- `waitForQuietDatabase` and wrapper `quietDatabase` are the exported quieting flow.

## Control flow
`waitForQuietDatabase` starts with a recovery wait, disables perpetual storage wiggle, disables backup workers, disables consistency scan, and disables DD pipeline control in simulation. It then repeatedly locates the data distributor and concurrently queries data-in-flight, TLog queues, DD queue, team collection validity, storage queue sizes, DD active state, recruitment state, version offset, and datacenter lag. Each loop logs a `QuietDatabase<phase>` event, requires all gates to pass, and needs three consecutive successes before returning. Retryable missing attributes and timeouts are traced and retried; other errors propagate.

## State and persistence behavior
Most reads are non-mutating event-log requests or system-key reads. Mutating side effects are intentional test setup actions: `setPerpetualStorageWiggle(false)`, `disableBackupWorker`, consistency scan config writes through `SystemDBWriteLockedNow`, and simulation reconfiguration with `ManagementAPI::changeConfig` when a datacenter is dead. The file also maintains the process-global `g_ddPipelineControlEnabled` switch.

## Dependencies and integration points
The file integrates with `WorkerInterface` event-log RPCs, `ServerDBInfo`, `ReadYourWritesTransaction`, `RunRYWTransaction`, `ManagementAPI`, simulator state, `FDBSimulationPolicy`, and consistency scan configuration. It is used by simulation workloads and test teardown/checkpoint phases to surface stuck data distribution earlier than generic simulation timeouts.

## Risks and edge cases
Event-log metric names and fields are stringly typed (`TotalDataInFlight`, `TLogMetrics`, `StorageMetrics`, `MovingData`, `TeamCollectionInfo`, etc.); missing or changed fields cause retries or errors. TLog queue inspection is noted as not robust to TLog failure. In simulation, the quiet checker asserts if DD appears stuck past the budget. Multi-region repair is simulation-specific and can change configuration when one datacenter is dead. Team collection validation includes workaround logic for remover oscillation and minimum team counts.

## Test signals
Trace events are the primary signal: `QuietDatabase<phase>Begin/Done/Fail/Retry/Error`, `QuietDatabaseFailure`, `MaxTLogQueueSize`, `MaxStorageServerQueueSize`, `DataDistributionQueueSize`, `GetTeamCollectionValid`, `ConsistencyScan_Sim*`, and `DisablingFearlessConfiguration`. Successful completion requires three consecutive quiet checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/QuietDatabase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/RatekeeperLimitReasons.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/RatekeeperLimitReasons.cpp

## Purpose
`RatekeeperLimitReasons.cpp` defines the stable textual names and descriptions for ratekeeper limiting reasons. These arrays are the presentation/telemetry mapping for the `limitReason_t` enum.

## Important APIs, types, and functions
- `limitReasonName[]` maps enum ordinals to compact machine-readable strings.
- `limitReasonDesc[]` maps the same ordinals to human-readable descriptions.
- `limitReasonEnd` exposes `limitReason_t_end` as an integer.
- `static_assert` checks guarantee both arrays stay in sync with the enum count.

## Control flow
There is no dynamic control flow. Initialization is static at process startup.

## State and persistence behavior
No persistence and no mutable runtime state beyond the exported integer. The table content covers workload/read performance, storage and log queue pressure, MVCC memory, readable/durable lag, disk free-space thresholds by absolute and ratio limits, and failure to fetch the storage server list.

## Dependencies and integration points
The file depends only on `fdbserver/core/RatekeeperLimitReasons.h`. Ratekeeper and status/reporting code can use these arrays to convert limit reason enums into trace, status, or metrics strings.

## Risks and edge cases
The main risk is enum/table drift; static assertions catch missing or extra entries at compile time. Renaming entries may affect dashboards or alerting that depend on stable strings.

## Test signals
Compile-time `static_assert` failures are the local test signal. Runtime validation is through emitted ratekeeper status and trace fields using the expected reason names/descriptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/RatekeeperLimitReasons.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/RocksDBCheckpointUtils.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/RocksDBCheckpointUtils.cpp

## Purpose
`RocksDBCheckpointUtils.cpp` implements RocksDB-backed checkpoint fetching, deletion, reading, and SST file utilities for data movement and bulk-load flows. When `WITH_ROCKSDB` is not enabled, it provides safe no-op or null fallbacks for the same public factory functions.

## Important APIs, types, and functions
- Serialization helpers `getRocksCF`, `getRocksCheckpoint`, and `getRocksKeyValuesCheckpoint` deserialize checkpoint payloads.
- `fetchRocksDBCheckpoint` fetches full RocksDB column-family checkpoints or key-value range checkpoints from storage servers and updates `CheckpointMetaData`.
- `deleteRocksCheckpoint` removes local checkpoint directories/files based on checkpoint format.
- `getTotalFetchedBytes` summarizes fetched file sizes across checkpoint formats.
- `newRocksDBCheckpointReader`, `newRocksDBSstFileWriter`, `newRocksDBSstFileReader`, and `newCheckpointByteSampleReader` are public factories.
- Internal reader classes are `RocksDBColumnFamilyReader`, `RocksDBCFCheckpointReader`, `RocksDBSstFileReader`, `RocksDBSstFileWriter`, and `RocksDBCheckpointByteSampleReader`.

## Control flow
For DataMove Rocks column-family checkpoints, `fetchRocksDBCheckpoint` launches `fetchCheckpointFile` for each SST file and optionally fetches the byte-sample SST. Each file is streamed from a source storage server via `fetchCheckpoint`, written with atomic async file flags, synced, and recorded as fetched in the serialized checkpoint. For RocksDB key-value checkpoints, `fetchCheckpointRanges` compares requested ranges against already fetched files, then `fetchCheckpointRange` streams `FetchCheckpointKeyValues` replies into a local SST writer and records either a real SST path or `emptySstFilePath`.

`RocksDBColumnFamilyReader` imports exported SST metadata into a local RocksDB database under a `/reader` subdirectory, opens the checkpoint column family read-only, and serves bounded range batches through thread-pool actions. `RocksDBCFCheckpointReader` instead exposes raw file chunks for a named SST or byte-sample file. SST reader/writer wrappers provide synchronous point iteration and range reads for bulk-load helpers.

## State and persistence behavior
The code writes local SST files and temporary/readable RocksDB databases under supplied checkpoint directories. It mutates `CheckpointMetaData` by replacing remote file paths with local paths, setting `fetched` flags, and serializing updated checkpoint structures. `readerInitialized` is written to the default RocksDB column family after successful import so future opens can detect whether a `/reader` database is complete. `deleteRocksCheckpoint` recursively removes directories or files referenced by fetched checkpoint metadata.

## Dependencies and integration points
The implementation depends on RocksDB APIs (`DB`, `SstFileReader`, `SstFileWriter`, column-family import metadata), `StorageCheckpoint` data types, storage-server RPCs (`fetchCheckpoint`, `fetchCheckpointKeyValues`), Flow async files, thread pools, `MutationTracking` debug hooks, and `FDBRocksDBVersion` compile-time version checks. It is used by physical shard movement, checkpoint restore/fetch paths, and bulk-load SST range reads.

## Risks and edge cases
RocksDB version mismatch is a compile-time failure. File fetching assumes `metaData->src.front()` identifies an available source storage server; missing server-list entries raise `checkpoint_not_found`. Several functions retry only a bounded number of times. Imported reader DBs are destroyed and rebuilt if the initialization marker is absent. `RocksDBSstFileWriter::finish` intentionally returns false for empty files because RocksDB cannot finish an empty SST. `fetchCheckpointRange` has simulation failure injection and needs careful handling of partial writer output. Recursive deletion trusts metadata-derived paths, so malformed metadata would be dangerous.

## Test signals
There are no local `TEST_CASE`s. Runtime traces include `FetchCheckpointFile*`, `FetchCheckpointRange*`, `RocksDBCheckpointReader*`, `CheckpointReaderImportCheckpoint*`, `RocksDBSstFile*Error`, and `DeleteRocks*Checkpoint`. `DEBUG_MUTATION("FetchCheckpointData", ...)` can expose streamed key-values when mutation tracking is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/RocksDBCheckpointUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/SeedShardServers.cpp -->
# sources/storage-engines/foundationdb/fdbserver/core/SeedShardServers.cpp

## Purpose
`SeedShardServers.cpp` seeds a brand-new database's storage-server metadata and initial shard ownership into a `CommitTransactionRef`. It assigns tags, stores server list and metadata records, initializes `keyServers`, and marks every storage server as owning `allKeys`.

## Important APIs, types, and functions
- `seedShardServers(Arena&, CommitTransactionRef&, std::vector<StorageServerInterface>)` is the only function.
- It uses tag locality helpers (`tagLocalityListKeyFor`, `tagLocalityListValue`, `serverTagKeyFor`, `serverTagValue`), server list helpers, `KeyBackedObjectMap` for storage metadata, `keyServersValue`, `serverKeysValue`, and KRM seeding via `krmSetPreviouslyEmptyRange`.

## Control flow
The function first groups storage servers by `dcId`, assigning each locality a tag locality id and then sequential tag ids within that locality. It sorts servers for deterministic output, forces the transaction to be the first transaction by setting `read_snapshot = 0` and adding an `allKeys` read conflict, then writes per-server tag/list/metadata keys. It builds parallel vectors of tags and server UIDs and initializes `keyServers` and each server's `serverKeys`.

If shard-encoded location metadata is enabled, it creates a new shard/data-move id with `DataMovementReason::SEED_SHARD_SERVER`, writes `keyServers` with source server ids and shard id, and stores `serverKeysValue(shardId)` for each server. Otherwise it writes legacy tag-encoded or UID-encoded `keyServers` values and `serverKeysTrue`.

## State and persistence behavior
The function writes system metadata into the passed commit transaction but does not commit itself. It writes tag locality list entries, server tag entries, server list entries, storage metadata entries, optional TSS identity mappings, `serverMetadataChangeKey`, the all-key `keyServers` range, and all-key `serverKeys` ranges for every server.

## Dependencies and integration points
It depends on system key encoders, `KeyBackedTypes`, `KeyRangeMap`, storage server interfaces, DD/data-move id helpers, and `SERVER_KNOBS`/`CLIENT_KNOBS` feature flags. It is part of initial cluster/database construction and must align with later `MoveKeys.cpp` assumptions about `keyServers` and `serverKeys`.

## Risks and edge cases
Tag locality ids are `int8_t`, so unexpected numbers of distinct DC ids would be risky. The `TSS_HACK_IDENTITY_MAPPING` branch logs severity error and is explicitly test-only behavior. The initial all-keys assignment differs by `TAG_ENCODE_KEY_SERVERS` and `SHARD_ENCODE_LOCATION_METADATA`, so mixed-version or knob-transition scenarios need careful compatibility handling.

## Test signals
There are no local tests. Validation comes from successful cluster bootstrap, correct initial `serverList`/`serverTag`/`keyServers`/`serverKeys` contents, and `TSSIdentityMappingEnabled` traces if the test-only knob is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/core/SeedShardServers.cpp -->
