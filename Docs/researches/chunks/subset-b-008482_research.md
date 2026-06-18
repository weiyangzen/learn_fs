# sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp lines 1-6163

## Scope

This chunk covers the beginning of FoundationDB's storage server actor implementation through the first part of the update section. It includes includes and persistent key-prefix definitions, move-in and adding shard state types, the central `StorageServer` state object, validation helpers, the major read RPC handlers, checkpoint serving, shard-state serving, mapped-range helpers, audit/restore validation paths, bulk-dump serving, range streaming, `getKey`, queue metrics, eager-read setup, and the start of durable-version advancement. The chunk ends inside `changeDurableVersion()`, so mutation application, shard changes, update log consumption, disk restore, server startup, and interface registration are outside this report.

## Purpose

The code defines the in-memory and durable state model used by an FDB storage server and implements much of the read-side RPC surface. Its main responsibilities in this range are:

- Maintain MVCC state by combining durable `IKeyValueStore` contents with an in-memory `VersionedMap<KeyRef, ValueOrClearToRef>` and a per-version mutation log.
- Track shard ownership and lifecycle through `ShardInfo`, including not-assigned, adding/fetching, moving-in physical shards, read-write pending, and readable states.
- Expose read APIs (`getValue`, `getKeyValues`, mapped range, streaming range, `getKey`) that wait for a readable version, verify shard ownership, merge storage-engine data with MVCC mutations, and return load-balancing penalties.
- Serve checkpoint discovery and checkpoint transfer for physical backup/data movement workflows.
- Support watches, range caching metadata, byte-sampling metadata, hot-range metrics, storage metrics, latency sampling, and read throttling based on durability lag.
- Run storage consistency/audit workflows comparing local shard metadata to system keyspaces, comparing restored backup data to source data, and comparing replicas for HA/replica validation.
- Serve bulk dump requests by reading local data, generating SST/manifest/sample files, uploading them, and persisting range-completion metadata.
- Prepare eager reads for mutation application by prefetching keys/values needed by atomic operations and selected clears.

## Important APIs, Types, and Functions

- Persistent key constants:
  - `persistFormat`, `persistShardAwareFormat`, `persistID`, `persistVersion`, `persistLogProtocol`, and `persistPrimaryLocality` encode storage-server identity/version/protocol metadata.
  - `persistShardAssignedKeys`, `persistShardAvailableKeys`, `persistStorageServerShardKeys`, `persistBulkLoadTaskKeys`, checkpoint prefixes, byte-sample prefixes, and accumulative-checksum prefixes describe durable metadata namespaces stored under `\xff\xff`.
  - `encodePersistAccumulativeChecksumKey()` and `decodePersistAccumulativeChecksumKey()` serialize checksum indexes with `bigEndian16`.

- Request/error helpers:
  - `canReplyWith()` lists errors that read/audit RPCs should return to callers instead of surfacing as actor failures, including `transaction_too_old`, `future_version`, `wrong_shard_server`, overload, mapper errors, and mapped-range quick-read misses.
  - `trackedReadType()` extracts `ReadOptions::type` when per-read-type latency tracking is enabled.
  - `dataMoveConflictError()` maps TSS data-movement conflicts to `please_reboot()` in simulation to avoid severity-40 test failures.

- Shard movement state:
  - `MoveInUpdates` buffers updates for physical shard move-in while the shard is not yet read-write. It can spill updates to the key-value store, load them back with `loadUpdates()`, and expose readiness through `hasNext()`.
  - `MoveInShard` wraps `MoveInShardMetaData`, fetch/apply promises, transfer version, phase, bulk-load mode, and mutation routing for physical shard move-in.
  - `AddingShard` models logical shard fetch during data movement, with phases `WaitPrevious`, `Fetching`, `FetchingCF`, and `Waiting`, plus deferred update buffering until fetch completes.
  - `ShardInfo` is the range-map value for ownership state. It converts to/from `StorageServerShard`, merges adjacent compatible shard entries, reports read/fetch readiness, routes mutations to adding/move-in/read-write paths, and stores physical shard IDs/version/team ID.

- Persistence adapter:
  - `StorageServerDisk` wraps `IKeyValueStore` with storage-server-specific counters and persistence helpers. In this chunk its interface includes durable-state creation/restoration, version/mutation durability, TSS quarantine persistence, log-protocol updates, range add/remove/replace for shard-aware stores, checkpoint/restore/delete, and counted read APIs.

- Main state object:
  - `StorageServer` owns `VersionedData versionedData`, `mutationLog`, watch metadata, `checkpoints`, `pendingCheckpoints`, physical-shard pending add/remove maps, histograms, `shards`, `newestAvailableVersion`, `newestDirtyVersion`, version notifiers, log-system cursor state, TSS pairing/quarantine state, locks, rate limiters, audit/dump locks, counters, metrics, and database handles.
  - `StorageServer::Counters` extends `CommonStorageCounters` with query counts, get-mapped-range stats, logical input/durable bytes, storage-engine read/commit counters, fetch metrics, PTree metrics, shard-change counters, read latency samples, latency bands, and special live counters for versions, locks, watches, rates, and kvstore sizes.
  - `currentRate()`, `getPenalty()`, `shouldRead()`, `readGuard()`, and `getQueryDelay()` implement local read admission and load-balancing penalty behavior based on durability lag and queue size.
  - `addVersionToMutationLog()`, `addMutationToMutationLog()`, and `addMutationToMutationLogOrStorage()` bridge MVCC/mutation-log accounting and byte sampling.

- Read/version helpers:
  - `waitForVersionActor()`, `waitForVersion()`, and `waitForVersionNoTooOld()` wait for the storage server to reach a requested version, handle `latestVersion`, version-vector commit-version optimization, `transaction_too_old`, `future_version`, and `process_behind`.
  - `getRealReadVersion()` and `getLatestCommitVersion()` use `VersionVector` and the storage server's tag to choose a safe read version when version vectors indicate no mutations happened between commit and requested read versions.
  - `getShardKeyRange()` finds the contiguous readable shard span around a key selector and throws `wrong_shard_server()` when the selector is outside readable ownership.

- Point/range reads:
  - `getValueQ()` serves `GetValueRequest` using MVCC first and durable storage second, validates shard changes after storage IO, updates read metrics, and returns `GetValueReply` with cache flag and penalty.
  - `merge()` combines durable `RangeResult` data with newer `VersionedMap` sets, respecting forward/reverse limits and byte limits.
  - `readRange()` reads a key range at a version by alternating MVCC traversal and storage reads, skipping clears, merging results, and computing `more`, byte, row, and logical-size metrics.
  - `findKey()` implements key-selector resolution within one readable shard, returning either an exact key or an offset/key pair that tells the caller the selector escaped the shard or byte limit.
  - `getKeyValuesQ()`, `getKeyValuesStreamQ()`, and `getKeyQ()` layer shard validation, key-selector handling, range reads, streaming continuations, transaction-tag accounting, and latency metrics over these helpers.

- Watches:
  - `ServerWatchMetadata` tracks the key, expected value, original version, tags, debug ID, and shared watch actor state for storage-server watches.
  - `watchWaitForValueChange()` repeatedly reads the watched key at safe versions, subscribes to `AsyncMap` changes, handles races with newer watch versions, and limits watch memory.
  - `watchValueSendReply()` wraps the watch future with timeout handling, fast timeout when no recent updates exist, watch-byte accounting, cancellation cleanup, and reply/error delivery.

- Checkpoint serving:
  - `getCheckpointQ()` waits for the requested version to be durable, verifies the requested range is readable, and returns a completed checkpoint matching version/format/action/range.
  - `deleteCheckpointQ()` waits for durability, removes checkpoint files, erases in-memory state, and writes mutation-log clears for both pending and completed checkpoint metadata keys.
  - `fetchCheckpointQ()` streams raw checkpoint chunks from `ICheckpointReader`.
  - `fetchCheckpointKeyValuesQ()` streams checkpoint contents as key-value batches, with per-server parallelism limiting and reuse/cleanup of `liveCheckpointReaders`.

- Mapped range helpers:
  - `quickGetValue()` and `quickGetKeyValues()` attempt local storage-server reads for secondary mapped lookups and optionally fall back to normal database transactions.
  - `preprocessMappedKey()`, `constructMappedKey()`, tuple unpack helpers, and literal escaping parse mapper tuple templates containing literals, `{K[n]}`, `{V[n]}`, and `{...}` range-query markers.
  - `mapSubquery()`, `mapKeyValues()`, and `getMappedKeyValuesQ()` scan index rows, construct mapped keys, dispatch point/range subqueries in bounded parallel batches, enforce byte limits, and preserve first/last index entries for continuation.

- Audit and validation:
  - `getThisServerShardInfo()` extracts local shard ownership over an audit range from `StorageServer::shards`.
  - `auditStorageServerShardQ()` compares local shard info with `serverKeys` and `keyServers` system keyspace views, records shard-assignment history during version catch-up, persists per-server audit state, and rate-limits remote reads.
  - `fetchSourceAndRestoredData()`, `compareSourceAndRestoredData()`, and `auditRestoreQ()` validate backup restore output by comparing normal-key source data with restore-prefixed data under `validateRestoreLogKeys`.
  - `issueGetKeyValuesRequest()` and `auditStorageShardReplicaQ()` compare local and remote storage-server range reads for HA/replica validation, persisting range progress and error state.

- Bulk dump:
  - `getRangeDataToDump()` reads local range data in batches using `getKeyValuesQ()`, builds raw KV and byte-sample maps, and returns `retry()` when the first read fails.
  - `bulkDumpQ()` serializes a requested range to local SST/manifest/sample files, uploads the resulting file set, persists completed bulk-dump range metadata, batches by size/count knobs, handles retryable failures, and best-effort cleans local task folders.

- Metrics and update prelude:
  - `getQueuingMetrics()` returns queue/durability/storage/rate/cpu/disk/busiest-tag status to the caller.
  - `doEagerReads()` deduplicates eager-read keys, reads key ends for clear-range conversion and value prefixes for atomics, stores results in `UpdateEagerReadInfo`, and records storage-engine read metrics.
  - `changeDurableVersion()` begins the process of pruning already-durable MVCC entries and mutation-log/freeable state; the function continues beyond this chunk.

## Control Flow

Storage-server read RPCs follow a repeated pattern. They increment counters and queue-size tracking, optionally yield at a priority that prevents load-balancing probes from dominating endpoint work, acquire a read priority lock, wait for a version using either the request version or version-vector commit version, capture the current `shardChangeCounter`, verify shard readability, perform MVCC/storage reads, then re-check `shardChangeCounter` before replying. Errors in the `canReplyWith()` list are converted into replies with current penalty where applicable; other errors abort the actor.

`getValueQ()` performs a point lookup by first checking `versionedData.at(version).lastLessOrEqual(key)`. If it finds a set for the exact key, it returns that value. If no relevant clear covers the key, it reads the durable store. After any storage read it rejects the result if the requested version fell behind `storageVersion()` or if shard metadata changed concurrently. The result updates empty/nonempty row counters, byte counters, read sampling, cache metadata, transaction tag counters, latency samples, and latency-band measurements.

Range reads are split across `getKeyValuesQ()`, `findKey()`, and `readRange()`. `getKeyValuesQ()` resolves selectors inside the contiguous readable shard span, treats offsets other than 0/1 as `wrong_shard_server`, and handles empty ranges directly. `readRange()` then walks the versioned PTree and the durable storage engine in ascending or descending direction. It detects clear ranges in MVCC, bounds storage reads to the next MVCC key or clear end, merges durable and MVCC rows, decrements row and byte limits, and reports whether there may be more rows. This is the core control path used by normal range reads, key-selector resolution, audit local reads, bulk dump reads, and stream batches.

`getKeyValuesStreamQ()` uses the same selector validation but sends multiple `GetKeyValuesStreamReply` messages. Each iteration waits for the reply stream to be ready, acquires a read lock, verifies the fixed version is still not too old, reads a batch, sends it, advances `begin` or `end` by the last key depending on direction, and finally sends `end_of_stream()`. Unlike non-stream range reads, this actor holds version constant across chunks and must reject with `transaction_too_old` if the storage server advances oldest version too far.

Mapped-range control flow starts like a normal range read to fetch index rows. It then releases the read lock before issuing mapped subqueries, because those subqueries re-enter `getValueQ()` or `getKeyValuesQ()` and would otherwise contend with the same read lock held by the parent. Mapper parsing turns a tuple template into either a point-mapped key or a prefix range query. Subqueries run in batches capped by `MAX_PARALLEL_QUICK_GET_VALUE`; local misses optionally fall back to database transactions. The response keeps boundary index entries so callers can continue from the right position.

Watch control flow shares one `ServerWatchMetadata` per watched key. The watch actor waits until the desired version is known, repeatedly reads the key at current server version, fires when the value differs at or after the requested version, otherwise subscribes to `watches.onChange(key)` or waits for a newer version needed to resolve races. `watchValueSendReply()` runs the caller-facing timeout loop, adjusting timeout mode when `noRecentUpdates` changes and cleaning the shared watch actor when the last promise reference disappears.

Checkpoint serving first ensures the checkpoint version is durable. Discovery (`getCheckpointQ`) scans the in-memory checkpoint map for completed metadata matching version/action/range. Raw transfer (`fetchCheckpointQ`) sends chunks until `end_of_stream` or `checkpoint_not_found`. Key-value transfer (`fetchCheckpointKeyValuesQ`) guards parallelism, lazily creates/reuses a key-value checkpoint reader, streams iterator batches, and closes/removes readers when no longer in use.

Audit actors are long-running, lock-limited flows. `auditStorageServerShardQ()` reads local shard info at the storage server's current version, enables shard-assignment history tracking, reads `serverKeys` and `keyServers` transactionally until their read version is at least the local view version, waits for the storage server to catch up, rejects if any shard assignment happened in the interval, then compares the three ownership views over an overlapping claim range. It persists complete or error state and advances through partial KRM reads under a rate limiter.

`auditRestoreQ()` validates source normal-key data against restore-prefixed data. It uses database transactions for both sides to avoid local shard-boundary artifacts, compares keys after stripping the restore prefix, fails fast if either side is completely empty at the start while the other is non-empty, periodically persists running progress by byte interval, and persists final complete/error state. `auditStorageShardReplicaQ()` gathers remote `StorageServerInterface`s from `serverList`, chooses a transaction read version, requests range data from each remote plus local, compares key/value sequences pairwise, persists progress every 100 checks or at completion, and reports the first mismatch as audit error.

`bulkDumpQ()` is an SS-side data-export loop. For each batch it clears local task files, gets a read version, calls `getRangeDataToDump()`, computes local and remote file-set paths, constructs byte-sampling settings, writes local SST/manifest/sample files, uploads only files that exist, persists completed range metadata, then advances to `keyAfter(lastKey)`. It retries most errors up to a high count, but gives up on task-outdated, shard-server, platform, and IO errors, and always attempts local cleanup at the end.

## State and Persistence Behavior

The chunk's central state split is durable storage versus MVCC overlay. Durable user data and storage-server metadata live in `IKeyValueStore`. Recent mutations live in `versionedData` and `mutationLog` until made durable. `oldestVersion`/`durableVersion`/`desiredOldestVersion` define the readable MVCC window and the point to which recovery can rely on disk. The comments on `StorageServer::versionedData` define invariants: clears are non-overlapping and maximal, reads combine storage plus `VersionedMap`, versioned data spans `[storageVersion(), version]`, old shard entries are eventually erased, and latest entries must have insert versions newer than `durableVersion`.

Shard state is persisted and exposed through both logical assignment ranges and physical shard-aware metadata. `StorageServer::shards` stores live `ShardInfo` entries. `newestAvailableVersion` and `newestDirtyVersion` track readability and partial availability. `persistShardAssignedKeys`, `persistShardAvailableKeys`, `persistStorageServerShardKeys`, pending checkpoint keys, pending physical-shard add/remove maps, and bulk-load task metadata are the durable side of this state. In shard-aware stores, `StorageServerDisk` also delegates physical range mapping to `IKeyValueStore::addRange`, `removeRange`, `replaceRange`, and `persistRangeMapping`.

Move-in state can be memory-only or spilled. `MoveInUpdates::loadUpdates()` reads serialized `VerUpdateRef` values from keys derived from move-in ID and version, restores older updates ahead of in-memory updates, uses a spill buffer when a range read returns `more`, and clears the spilled flag only when the last batch is loaded. `AddingShard` and `MoveInShard` both gate read/write availability through promises and phase changes; their deferred updates must be replayed only after fetched data is ready.

Checkpoint state is both in-memory and durable/file-backed. `StorageServer::pendingCheckpoints` and `checkpoints` track pending and completed metadata. Completed checkpoint files are read by `ICheckpointReader`, and deletion clears both checkpoint files and persisted metadata keys by adding clear mutations to the current mutation log. `liveCheckpointReaders` retains active readers for key-value checkpoint streaming until no iterator is using them.

Audit and restore validation persist state back through the normal database API rather than local storage-engine metadata. `persistAuditStateByServer()` and `persistAuditStateByRange()` record progress/error/complete state tied to audit IDs, DD IDs, ranges, and server IDs. The actors use transactional reads of system keyspaces (`serverKeys`, `keyServers`, `serverList`) and lock-aware/system-key options, so their correctness depends on consistent cluster metadata versions as well as local shard metadata.

Bulk dump persistence spans local disk, remote blob/storage transport, and system metadata. The actor first writes local SST and manifest artifacts under the storage server's bulk dump folder, uploads to the job/task/batch remote path, and then persists the completed range's manifest metadata. Cleanup deletes local task files best-effort; remote inconsistency is expected to be detected by the DD and retried with a new task.

TSS state affects read behavior. A server with `tssPairID` is a TSS; `tssInQuarantine` can be persisted via `makeTssQuarantineDurable()`. Quarantined TSSs reject reads via `shouldRead()` but remain alive enough for operator investigation and eventual removal.

## Dependencies and Integration Points

- Flow actor runtime: functions return `Future<T>`, use `co_await`, `ACTOR`, `choose`, `Promise`, `FutureStream`, `AsyncVar`, `AsyncMap`, `FlowLock`, `PriorityMultiLock`, `ThroughputLimiter`, `SpeedLimit`, and actor collection management.
- FDB client/server interfaces: request/reply types such as `GetValueRequest`, `GetKeyValuesRequest`, `GetMappedKeyValuesRequest`, `GetKeyValuesStreamRequest`, `GetKeyRequest`, `WatchValueRequest`, `GetCheckpointRequest`, `FetchCheckpointRequest`, `AuditStorageRequest`, `BulkDumpRequest`, and `StorageQueuingMetricsRequest` define the external RPC surface.
- Storage engine abstraction: `IKeyValueStore` supplies durable reads/writes, range management, checkpoints, restore, physical shard operations, and storage-byte accounting. This code assumes its range reads obey row/byte limits and `more` semantics.
- Log system and data movement: included dependencies and state refer to `LogSystemConsumer`, `IReplayPeekCursor`, `TLogInterface`, `MoveKeys`, `DataMovement`, `StorageServerShard`, and physical shard move metadata. Later chunks implement update consumption and shard changes, but this chunk defines much of the state they mutate.
- System keyspace/database transactions: audit, restore validation, mapped-range fallback, and bulk-dump metadata persistence use `Database`, `Transaction`, system-key options, lock-aware options, `serverListKeyFor()`, `getThisServerKeysFromServerKeys()`, `getShardMapFromKeyServers()`, and audit/bulk-load persistence helpers.
- Tuple and mapper contracts: mapped-range APIs depend on `Tuple::unpack`, tuple element raw strings, and user-facing mapper template syntax. Errors are mapped to specific mapper error codes.
- Metrics/tracing: `TraceEvent`, `g_traceBatch`, `ReadLatencySamples`, `LatencyBands`, histograms, `CommonStorageCounters`, `StorageMetrics`, hot-range metrics, transaction tag counters, and event cache holders are deeply integrated with every read/audit/data-transfer path.
- Simulation and test hooks: `buggify()`, `CODE_PROBE`, `g_network->isSimulated()`, `FDBSimulationPolicy`, consistency-scan corruption injection, targeted restart/delay injection, and TSS fault injection shape edge-case behavior in tests.
- Bulk load/dump/checkpoint utility layers: `BulkDumpUtil`, `BulkLoadUtil`, `ServerCheckpoint`, checkpoint readers/iterators, byte-sample helpers, file upload helpers, and local folder cleanup are used by checkpoint and dump handlers.

## Risks and Edge Cases

- MVCC/storage merge correctness is delicate. `readRange()` must correctly account for clears spanning the requested bounds, forward versus reverse ordering, storage `more` semantics, byte limits, and duplicate keys where MVCC sets override durable values.
- Shard-change races are explicitly guarded by `shardChangeCounter`. Missing a post-IO check would let a read answer for a range that moved away while the storage read was in progress.
- Version-window errors are split across `transaction_too_old`, `future_version`, and `process_behind`. Version-vector optimization can legally read at a commit version older than the requested read version only when the tag has no newer mutations; mistakes here would violate snapshot semantics.
- Read throttling depends on durability lag and random rejection. `shouldRead()` must reject quarantined TSS reads and overload only replyable request types; otherwise clients may see actor failures instead of load-balanced retries.
- Mapped-range subqueries are reentrant. The parent releases the read lock before launching subqueries; holding it would create self-contention or deadlock under the same priority lock. Conversely, releasing it means shard state must be revalidated after mapping.
- Mapper parsing trusts tuple structure but must reject bad indexes, malformed tuple keys/values, non-final `{...}`, and non-tuple mapper inputs with the correct public errors.
- Watches can consume unbounded memory if not capped. The code tracks both queued watch overhead and implementation overhead; exceeding `MAX_STORAGE_SERVER_WATCH_BYTES` cancels watches and falls back to polling behavior.
- Audit shard validation currently gives up if shard assignment history is non-empty between the local view and system-key read version rather than replaying history. This is conservative but can produce failed/cancelled audit work under active data movement.
- Audit flows rely on per-server parallelism lock being one for shard-info audits because `trackShardAssignmentMinVersion` is a single shared state. Increasing the lock without redesign would make concurrent audits interfere.
- Restore validation has asymmetric empty-side fast failures and compares prefixed restored keys after stripping `validateRestoreLogKeys.begin`. Wrong prefix/range construction would turn valid restore output into false missing/extra-key errors.
- Replica validation considers any completed read among replicas enough to mark the round complete; if other replies have `more`, size/key mismatches surface as errors in that round. This intentionally catches inconsistency but makes limit alignment important.
- Bulk dump writes/upload/persist is not atomic across local files, remote files, and database metadata. The comments rely on DD retry/verification to detect remote inconsistencies; local cleanup is best effort.
- Checkpoint streaming owns raw reader pointers in `liveCheckpointReaders`. Correct `inUse()` checks and close/erase ordering are required to avoid leaks or closing a reader still backing an iterator.
- `getKeyValuesStreamQ()` does not use the same initial read-admission path as normal range reads; it yields at endpoint priority and then repeatedly locks per batch. It must still guard too-old versions inside the loop.
- The chunk ends as durable-version pruning begins. Full risk analysis of mutation-log deletion, `freeable` arenas, and VersionedMap forgetting requires the continuation after line 6163.

## Test Signals

- Point reads: values present in MVCC, values present only on disk, keys covered by MVCC clears, absent keys, cached-range flags, system-key counters, debug IDs, overloaded/quarantined TSS rejection, and post-read shard-change `wrong_shard_server`.
- Version handling: `latestVersion`, too-old reads, future-version timeout, process-behind behavior, version-vector commit-version reads, and reads around `oldestVersion` advancement during storage IO.
- Range reads: forward/reverse scans, clear ranges crossing begin/end, MVCC overriding durable rows, byte-limit and row-limit `more`, large selector offsets returning `wrong_shard_server`, empty ranges, contiguous readable shard boundaries, consistency-scan corruption injection in simulation, and range-stream continuations to `end_of_stream`.
- Key selectors: exact keys, `firstGreaterOrEqual`, backward selectors at shard boundaries, selectors escaping shard boundaries with offset 1, large offsets that hit byte limits, and reverse selector one-row edge cases.
- Watches: immediate value change, timeout with and without `noRecentUpdates`, racing watches for the same key/version, transaction-too-old retry in the watch loop, watch memory cap cancellation, and cleanup when the last promise reference disappears.
- Checkpoints: checkpoint lookup by version/format/action/range, unreadable range rejection, checkpoint-not-found, raw chunk streaming, key-value checkpoint streaming, active reader reuse, iterator end-of-stream, and checkpoint deletion clearing both file and metadata keys.
- Mapped ranges: mapper literal escaping, `{K[n]}` and `{V[n]}` extraction, `{...}` prefix range queries, non-tuple key/value/mapper errors, bad indexes, local quick-get hit/miss counters, fallback enabled/disabled, byte-limit truncation, and preserved boundary index rows for continuation.
- Audit shard validation: mismatch between `serverKeys`, `keyServers`, and local `shards`; partial KRM reads; system-key read version behind local version requiring retry; shard-assignment history non-empty during audit; DD ID validation; progress/error persistence; and rate limiter accounting.
- Restore validation: matching source/restored ranges, missing key, extra key, value mismatch, empty baseline/source fast paths, retryable future/too-old/overload errors, periodic running-progress persistence, and final error/complete state.
- Replica audit: missing remote server list entries, remote RPC errors, local/remote key mismatch, value mismatch, missing local or remote keys, nothing-to-compare case, partial progress persistence every 100 checks, and wrong-shard handling for out-of-range returned keys.
- Bulk dump: empty range manifest, batches split by byte and count limits, byte sample file generation/omission, local folder cleanup, upload failure retry, task-outdated handling, wrong-shard/platform/IO failure mapping, and persisted completed range metadata matching manifest range.
- Metrics and throttling: queue metric replies, busiest tag reporting, latency-band filtering for large reads or selector offsets, read-priority mapping by `ReadType`, local rate changes as durability lag crosses soft/hard thresholds, and storage-engine read counters from eager reads.
