# Research Group: subset-b-008844

This grouped report covers TiKV raftstore split validation, error conversion, public crate wiring, router abstractions, async I/O read/write workers, bootstrap helpers, command response helpers, and compaction guard partitioning. Each file section preserves its original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_observer.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_observer.rs

Purpose: Implements the raftstore admin coprocessor that sanitizes Split and BatchSplit requests before proposal. Its main job is to strip MVCC timestamps from split keys, reject empty/out-of-region keys, deduplicate adjacent versions of the same logical key, and keep split requests sorted so a split does not separate multiple MVCC versions of one user key.

Important APIs and types: `NO_VALID_SPLIT_KEY` is the user-visible failure text when every requested split point is discarded. `strip_timestamp_if_exists` attempts `tikv_util::codec::bytes::decode_bytes` and truncates the undecoded suffix, treating it as a timestamp when the key was encoded. `is_valid_split_key` rejects empty keys and uses `store::util::check_key_in_region_exclusive` to reject region edges or outside keys. `SplitObserver` implements `Coprocessor` and `AdminObserver`; `pre_propose_admin` is the integration point invoked before proposing admin commands.

Control flow: `pre_propose_admin` only handles `AdminCmdType::Split` and `AdminCmdType::BatchSplit`. It validates that the matching request payload exists, moves the split requests out of the protobuf, calls `on_split`, and writes back the cleaned request list. `on_split` consumes the split vector, strips timestamps, filters invalid keys, then uses `itertools::coalesce` to keep strictly increasing split keys and drop duplicates or unsorted keys. If no valid split remains, it returns `NO_VALID_SPLIT_KEY`.

State and persistence: This file has no durable state. It mutates only the in-flight `AdminRequest` before raft proposal. The important persistence implication is indirect: by normalizing split keys before proposal, the persisted region boundary will be a user-key boundary instead of a versioned MVCC key boundary.

Dependencies and integration points: It depends on protobuf request types from `kvproto::raft_cmdpb`, region metadata from `kvproto::metapb`, TiKV byte encoding helpers, and raftstore region range validation. It integrates with the coprocessor framework through `AdminObserver::pre_propose_admin` and surfaces errors through the coprocessor `Result`.

Risks: The timestamp stripping heuristic treats raw keys that happen to decode as encoded keys as encoded keys, which the comment calls out as intentional but subtle. Invalid split requests with all keys filtered fail the proposal; mixed valid/invalid requests silently drop invalid keys after logging. Ordering is strict; out-of-order split keys are dropped rather than sorted into the requested order.

Test signals: `test_forget_encode` verifies timestamp stripping from encoded row keys. `test_split` covers non-split commands, single split compatibility, empty/start keys, duplicate MVCC versions, row/index/table-prefix keys, raw keys, right-derive preservation, and the all-invalid error path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_observer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/errors.rs -->
# sources/storage-engines/tikv/components/raftstore/src/errors.rs

Purpose: Defines raftstore's central `Error` enum, `Result` alias, transport discard reasons, conversion to client-facing `errorpb::Error`, and stable error-code classification. This is the boundary between internal raftstore failure modes and RPC-visible raft command errors.

Important APIs and types: `DiscardReason` distinguishes disconnected, filtered, paused, and full channels. `Error` includes leadership and region routing errors (`NotLeader`, `RegionNotFound`, `StoreNotMatch`, `KeyNotInRegion`), liveness/availability states (`ReadIndexNotReady`, `DataIsNotReady`, `RecoveryInProgress`, flashback states), persistence and dependency errors (`Io`, `Engine`, `Raft`, `Snapshot`, `Encryption`, `SstImporter`), and raftstore-specific conditions (`PendingPrepareMerge`, `IsWitness`, `MismatchPeerId`). `RAFTSTORE_IS_BUSY` is used for full transport queues.

Control flow: `From<Error> for errorpb::Error` always sets the text message, then fills structured protobuf sub-errors for recognized variants. Full transport queues map to `ServerIsBusy`; deadline exceeded uses `set_deadline_exceeded_busy_error`; coprocessor delay requests become `ServerIsBusy` with backoff. `From<TrySendError<T>>` maps channel full/disconnected into transport discard errors, and `From<DeadlineError>` maps directly to `DeadlineExceeded`.

State and persistence: This file has no storage behavior. Its state impact is semantic: the chosen error variant controls client retry behavior, leader redirection, stale epoch refresh, disk-full reporting, and whether callers see a generic message or structured protobuf field.

Dependencies and integration points: It depends on `kvproto::errorpb`, `metapb`, and `raft_serverpb` for wire errors, `error_code` for observability codes, engine/pd/raft/snapshot/import/encryption error types for conversion, and TiKV deadline helpers. It is re-exported from `lib.rs` and used across router, store, coprocessor, and command response helpers.

Risks: New `Error` variants must be added in three places to be fully useful: display text, protobuf conversion, and `ErrorCodeExt`. Missing protobuf mapping falls back to message-only errors. Some internal states such as `RegionNotRegistered` map to unknown, which is appropriate for internal diagnostics but weak for client logic. `Transport(Disconnected)` converts differently depending on path: `TrySendError` can become `Transport`, while router `handle_send_error` maps proposal disconnection to `RegionNotFound`.

Test signals: `test_deadline_exceeded_error` verifies that `DeadlineExceeded` becomes a server-busy style protobuf with the expected message and reason. Broader coverage is indirect through raftstore command response and routing tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/lib.rs -->
# sources/storage-engines/tikv/components/raftstore/src/lib.rs

Purpose: Defines the raftstore crate root, feature gates, public modules, selected re-exports, and a small bytes memory accounting helper.

Important APIs and types: Public modules are `coprocessor`, `errors`, `router`, and `store`; `compacted_event_sender` and `RaftRouterCompactedEventSender` are available only under `engine_rocks`. Re-exports expose `RegionInfo`, `RegionInfoAccessor`, `SeekRegionCallback`, `DiscardReason`, `Error`, and `Result`. `bytes_capacity` reports `bytes::Bytes` memory usage as `len()`.

Control flow: There is no runtime control flow beyond `bytes_capacity`. The crate attributes enable nightly features used by raftstore internals and raise recursion limits for generated or deeply nested types.

State and persistence: No durable state is owned here. The `bytes_capacity` helper is used for metrics and treats deserialized raft-message bytes as having capacity equal to length, avoiding dependence on protobuf-generated `Bytes` internals.

Dependencies and integration points: This is the import surface for other TiKV components. It binds raftstore's error type and coprocessor region-info traits into a stable external API, while module declarations make the store, router, and coprocessor subtrees available.

Risks: Crate-level nightly features (`min_specialization`, `box_patterns`, `type_alias_impl_trait`, `impl_trait_in_assoc_type`) tie compilation to a compatible nightly toolchain. `bytes_capacity` underestimates or abstracts real allocation capacity for non-deserialized `Bytes`, but the comment scopes it to raft message memory metrics.

Test signals: No direct tests are present. Compilation of downstream modules and metric behavior using `bytes_capacity` are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/router.rs -->
# sources/storage-engines/tikv/components/raftstore/src/router.rs

Purpose: Provides raftstore routing traits and adapters for raft messages, proposals, casual/significant peer messages, store messages, local reads, coprocessor callbacks, and CDC leadership/change observer hooks.

Important APIs and types: `RaftStoreRouter<EK>` composes `StoreRouter`, `ProposalRouter`, `CasualRouter`, and `SignificantRouter`, adding methods such as `send_raft_msg`, `broadcast_normal`, `send_command`, `report_unreachable`, `report_snapshot_status`, and store reachability helpers. `ReadContext` carries optional thread read id and timestamp. `LocalReadRouter` abstracts local read execution and snapshot-cache release. `RaftStoreBlackHole` is a no-op router for tests or disabled paths. `ServerRaftStoreRouter` wraps a `RaftRouter` plus `LocalReader`. `CdcHandle` and `CdcRaftRouter` expose CDC/PiTR scheduling through significant messages.

Control flow: `send_command_impl` extracts the region id, wraps the request/callback as `RaftCommand`, attaches extra options, and sends through a proposal router. `handle_send_error` maps full queues to `Transport(Full)` and disconnected proposal channels to `RegionNotFound(region_id)`. `ServerRaftStoreRouter` delegates every routing trait to the underlying raft router or local reader. The `StoreHandle` impl on `RaftRouter` converts coprocessor events into `CasualMessage` variants, logging failures instead of surfacing them.

State and persistence: The router owns no durable state. It controls message delivery and therefore indirectly affects raft persistence and proposal progress. Local reads may use cached snapshots via `LocalReader`, with explicit cache release.

Dependencies and integration points: It depends on engine traits, raft snapshot status, raft command protobufs, raftstore FSM router traits, transport router traits, coprocessor `StoreHandle`, local reader, and CDC change observers. It is a central integration layer used by server frontends, coprocessors, snapshot transport feedback, and CDC/PiTR.

Risks: Several methods intentionally log-and-drop coprocessor feedback on routing failure, which protects background tasks but can delay split-size, hash, bucket, or compaction-decline updates. The black-hole router can hide behavior if accidentally used outside tests or disabled components. Mapping disconnected proposal send to `RegionNotFound` is pragmatic but may obscure shutdown versus actual missing-region causes.

Test signals: No tests are in this file. Its behavior is indirectly covered by raftstore routing, local-read, CDC, and coprocessor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/async_io/mod.rs

Purpose: Declares the async I/O submodules for raftstore store workers.

Important APIs and types: It exposes `read`, `write`, and `write_router` modules. There are no local functions, types, or constants.

Control flow: None in this file. Runtime behavior lives in the three child modules.

State and persistence: None locally. The module boundary groups async raft-log fetching, snapshot generation, write batching, persistence, and write-worker routing.

Dependencies and integration points: Consumers import `store::async_io::read`, `store::async_io::write`, and `store::async_io::write_router` through this declaration.

Risks: The file is simple, but module visibility means removing or renaming any child module breaks raftstore async I/O wiring.

Test signals: No direct tests. Child modules provide their own tests, especially `write_tests.rs` and `write_router` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/read.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/async_io/read.rs

Purpose: Implements the async read-side worker for raftstore: fetching raft log entries from the raft engine and generating tablet snapshots from a tablet engine checkpoint.

Important APIs and types: `ReadTask<EK>` has `FetchLogs` and `GenTabletSnapshot` variants. `FetchedLogs` returns a `GetEntriesContext` plus boxed `RaftlogFetchResult`. `GenSnapRes` is `Option<Box<(Snapshot, u64)>>`, carrying a generated raft snapshot and target peer. `AsyncReadNotifier` reports fetched logs and generated snapshots back to raftstore. `ReadRunner<EK, ER, N>` owns the notifier, raft engine, optional `TabletSnapManager`, and engine phantom.

Control flow: `Runnable::run` matches on `ReadTask`. For `FetchLogs`, it marks replication I/O, fetches `[low, high)` entries from the raft engine into a bounded vector, computes whether the size limit was hit, and notifies with success or converted error. For `GenTabletSnapshot`, it checks cancellation, marks load-balance or replication I/O, asserts the region is not tombstone, builds raft snapshot metadata and `RaftSnapshotData`, computes a `TabletSnapKey`, checkpoints the tablet into the snapshot manager path, registers the snapshot, updates metrics, and notifies success or failure.

State and persistence: Fetching logs is read-only. Snapshot generation creates or replaces a checkpoint directory under the tablet snapshot manager's generation path, potentially deleting an old checkpoint with encryption-aware trash removal. Snapshot metadata persists region, version, removed records, merged records, term, index, conf state, and `for_balance`.

Dependencies and integration points: It depends on `KvEngine` checkpointers, `RaftEngine::fetch_entries_to`, raft protobuf snapshots, `TabletSnapManager`, snapshot metrics, failpoints, file-system I/O type guards, and raftstore worker `Runnable`. Notifications return results to the peer/store FSM that requested log fetch or snapshot generation.

Risks: `snap_mgr()` unwraps, so callers must call `set_snap_mgr` before `GenTabletSnapshot`. Checkpoint creation errors are logged and reported as `None`; callers must interpret missing snapshot results. Cancellation is checked only before expensive work starts, not during checkpoint creation. Snapshot data serialization uses `unwrap`, assuming protobuf serialization cannot fail.

Test signals: No local tests. Coverage is expected from snapshot generation, raft log fetch, and raftstore integration tests using async read workers and failpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/async_io/write.rs

Purpose: Implements raftstore's asynchronous write workers. Peers build `WriteTask`s containing raft log entries, raft states, extra apply/snapshot state, callbacks, and outbound raft messages; workers batch those tasks, persist KV and raft-engine data, execute callbacks, send messages, and notify peers that ready numbers are durable.

Important APIs and types: `PersistedNotifier` reports `(region_id, peer_id, ready_number)` after persistence and is implemented by `RaftRouter` using `PeerMsg::Persisted`. `ExtraWrite<W, L>` carries extra writes either to KV (`V1`) or raft engine (`V2`) and prevents mixing. `WriteTask<EK, ER>` is the per-peer unit with raft log batch, appended entries, raft state, extra write, messages, callbacks, waterfall trackers, snapshot flag, and flushed epoch. `WriteMsg` wraps `WriteTask`, latency inspection, shutdown, and a test pause. `WriteTaskBatch` coalesces tasks into one or more raft log batches. `Worker` is the write-thread event loop. `StoreWriters` manages the worker pool and shared senders.

Control flow: `Worker::run` blocks for one message, handles it, then drains additional messages until the raft-size limit is reached or the receiver is empty. If the batch is below the configured hint, `WriteTaskBatchRecorder` may spin briefly to improve batching. `write_to_db` flushes pending raft states into the latest raft log batch, writes sync KV extra writes first for `ExtraBatchWrite::V1`, writes all raft log batches with `consume_and_shrink`, updates monotonic success timestamps, executes persisted callbacks, sends queued raft messages through `Transport`, optionally notifies peers, records metrics, clears the batch, and applies config updates.

State and persistence: Persistence is split between KV engine extra writes for v1 state and raft engine log batches for raft logs and v2 state. `WriteTaskBatch` keeps only the latest raft state and latest ready per region in a batch, enforcing same peer id and monotonically increasing ready numbers. Large raft batches are split at `RAFT_WB_SPLIT_SIZE` so individual atomic batches remain bounded. KV writes use sync `WriteOptions`; raft writes pass `sync = true`. Success timestamps support fail-fast disk health checks.

Dependencies and integration points: The file depends on engine traits, raft entries and messages, resource-control metering, health latency inspectors, failpoints, file-system I/O type, raftstore metrics, `Transport`, and `RaftRouter`. `StoreWriters::spawn` creates foreground-write threads and publishes `SharedSenders`; `write_to_db_for_test` provides a synchronous persistence helper for tests.

Risks: Many persistence failures panic, which is consistent with raftstore treating durable write failure as fatal but raises blast radius. Mixing `ExtraWrite::V1` and `V2` is an `unreachable!` invariant. The adaptive batching algorithm trades latency and IOPS; bad configuration or workload shifts can affect tail latency despite clamps and tests. Callback execution happens after durable writes but before follower messages and peer notification, so callbacks must be non-blocking. `StoreWriters::decrease_to` only shrinks logical sender visibility and leaves old workers alive for in-flight peers.

Test signals: `write_tests.rs` covers batch recorder and adaptive wait bounds, zero threshold runtime guard, basic worker persistence, v1 KV extra writes, v2 raft state writes, split raft log batches, worker pool basic flow, resource-group metering, notification delivery, outbound message counts, and success timestamp updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_router.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_router.rs

Purpose: Routes each peer's async write messages to a store write worker while preserving per-peer ordering and optionally rescheduling hot peers across workers once previous writes have persisted.

Important APIs and types: `WriteRouterContext` abstracts access to `WriteSenders`, raftstore `Config`, and local raft metrics. `WriteRouter<EK, ER>` tracks the current writer id, retry time, pending reschedule target, last unpersisted ready number, buffered messages, and last resource-control priority. `SharedSenders` wraps the sender vector stored in a `VersionTrack`. `WriteSenders` caches tracked senders and holds a shared `io_reschedule_concurrent_count`.

Control flow: `send_write_msg` resets priority when there are no pending writes, calls `should_send`, and either sends immediately or buffers the message. `should_send` randomly chooses a worker when there is no previous unpersisted ready, avoids rescheduling when disabled or before the hot-spot duration, chooses a different worker as `next_writer_id`, and uses an atomic concurrent-count limit before buffering. `check_new_persisted` completes a reschedule once the persisted ready number reaches `last_unpersisted`, swaps to the new writer, decrements gauges/counters, and drains buffered messages to the new worker. `send` consumes resource quota, tries priority send, and falls back to blocking send while recording write-block wait.

State and persistence: The router itself is in-memory, per peer. Its key state invariant is that buffered messages are not sent to a new worker until earlier writes are durable, preserving sequential handling for a peer. It also carries `last_msg_priority` so resource-control scheduling can maintain per-peer order.

Dependencies and integration points: It depends on `resource_control::channel::Sender`, raftstore `Config`, `PollContext`, write metrics, async `WriteMsg`, and `VersionTrack` configuration updates. `StoreWriters` in `write.rs` owns the shared sender set that `WriteSenders` tracks.

Risks: Random writer choice means tests and behavior must tolerate no-op reschedule attempts when the same worker is selected. If persisted notifications stall, buffered messages remain pending and gauges stay elevated. `SharedSenders` uses a manual `unsafe impl Sync` based on access discipline; violating that discipline could expose sender internals to races. Pool size is min-capped against local cached senders to handle config updates before poller refresh.

Test signals: `test_write_router_no_schedule` verifies disabled rescheduling keeps all messages on the original worker. `test_write_router_schedule` verifies reschedule start, buffering, no completion before the persisted threshold, drain after threshold, and retry behavior when the concurrent reschedule limit is saturated.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_tests.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_tests.rs

Purpose: Provides unit and integration-style tests for `store::async_io::write` and some write-router/resource-control interactions. The file builds test engines, notifiers, transports, workers, and writer pools to validate durable state and asynchronous notifications.

Important APIs and types: Helpers include `must_have_entries_and_state`, `new_raft_state`, `TestNotifier`, `TestTransport`, `TestWorker`, `TestWriters`, `init_write_batch`, KV/raft put-delete helpers, and notification/message assertions. It aliases test KV write batches and raft log batches for readability.

Control flow: Tests construct `WriteTask`s with combinations of KV extra writes, raft log batches, appended entries, raft states, apply/region states, callbacks/messages, then either add them directly to a worker batch or send them through `StoreWriters` senders. Assertions inspect snapshots, raft-engine entries/states, apply/region states, message receivers, notification receivers, and success timestamp atomics.

State and persistence behavior validated: `test_worker` verifies KV extra writes, raft log append/overwrite/delete, latest ready notification per region, outbound messages, and raft/KV success timestamps. `test_worker_split_raft_wb` validates splitting raft log batches while preserving apply states and final raft state. `test_basic_flow` and `test_basic_flow_with_states` validate asynchronous pool behavior for v1 and v2 state paths. Resource-group testing verifies entry headers drive I/O resource accounting through the write router.

Dependencies and integration points: The tests depend on `engine_test` temporary KV/raft engines, `resource_control`, raft command protobufs, raftstore `WriteRouter`, `Config`, local metrics, and peer-storage test entry helpers. They exercise both direct worker methods and spawned writer threads.

Risks: Several async assertions use timeouts, which can be sensitive to overloaded CI. Tests using random write-router selection loop until the desired state appears in `write_router.rs`, while this file mostly routes deterministically by sender id. The tests are strong on persistence invariants but do not simulate disk write failures beyond failpoints present in production code.

Test signals: This file is itself the test signal. It covers adaptive wait clamping, high/low QPS paths, futile-wait reduction, zero adaptive threshold validation/runtime guard, no oscillation at high QPS, worker persistence, split batches, basic spawned writers, v2 state writes, and resource-group scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/bootstrap.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/bootstrap.rs

Purpose: Provides helpers for initializing a raftstore store and preparing or clearing the first cluster bootstrap region.

Important APIs and types: `initial_region` creates the first `metapb::Region` with empty start/end keys, initial epoch constants, and one peer. `bootstrap_store` validates an empty KV default CF, writes `StoreIdent`, and syncs. `prepare_bootstrap_cluster` writes `PREPARE_BOOTSTRAP_KEY`, region local state, initial apply state, and initial raft state. `clear_prepare_bootstrap_cluster` removes prepared raft and KV metadata. `clear_prepare_bootstrap_key` removes only the prepare marker.

Control flow: Store bootstrap first checks range emptiness by scanning the KV engine. Cluster bootstrap writes KV metadata in one write batch, syncs KV, then writes initial raft state to the raft engine and consumes it synchronously. Clearing reverses this by cleaning raft logs/state and deleting prepare, region state, and apply state keys from KV.

State and persistence: This file writes durable store identity at `keys::STORE_IDENT_KEY`, the prepare marker at `keys::PREPARE_BOOTSTRAP_KEY`, region state and apply state in `CF_RAFT`, and initial raft state in the raft engine. Sync calls ensure bootstrap metadata reaches disk before success is returned.

Dependencies and integration points: It uses `engine_traits::Engines`, KV and raft engine traits, raftstore peer-storage initial state helpers, TiKV key layout helpers, and `tikv_util::store::new_peer`. It is used during store and cluster initialization before normal raftstore operation.

Risks: `bootstrap_store` checks only the default CF for emptiness before writing store identity, matching existing expectations but making CF assumptions important. Partial failure between KV prepare writes and raft initial state write can leave prepare metadata that must be cleared or retried. The generic comment notes raft engine lacks the same range-empty query, constraining type simplification.

Test signals: `test_bootstrap` verifies store bootstrap succeeds once and fails when repeated on non-empty KV, prepare writes all expected markers/states, clearing removes prepare metadata and raft data, and the raft log batch dump is empty after cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/cmd_resp.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/cmd_resp.rs

Purpose: Centralizes small helpers for building raft command responses with current term and structured raftstore errors.

Important APIs and types: `bind_term` writes `current_term` into a `RaftCmdResponse` header when term is nonzero. `bind_error` converts crate `Error` into `errorpb::Error` and stores it in the response header. `new_error` constructs an error response. `err_resp` combines error and term binding. `message_error` boxes a generic error into `Error::Other` and returns a response.

Control flow: Helpers mutate or construct protobuf responses directly. `bind_term` is a no-op for zero, preserving responses where no current term is known. Error conversion delegates to `errors.rs`, so structured fields depend on the `Error` variant.

State and persistence: No durable state. These helpers shape client-visible command results after raftstore processing failures or leadership/term changes.

Dependencies and integration points: It depends on `kvproto::raft_cmdpb::RaftCmdResponse` and crate `Error`. Store command handling code can use these helpers to produce consistent error responses without duplicating header manipulation.

Risks: `message_error` wraps errors as `Error::Other`, which produces mostly message-only client errors and unknown error codes. Callers must pass a nonzero term when term redirection semantics matter.

Test signals: No local tests. Behavior is indirectly tested by `errors.rs` conversion tests and raftstore command handling tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/cmd_resp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/compaction_guard.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/compaction_guard.rs

Purpose: Implements a RocksDB SST partitioner factory/generator that tries to align compaction output files with region boundaries and avoid huge future compactions. It also supports temporary force-partition ranges with TTL.

Important APIs and types: `ForcePartitionRangeManager` stores sorted `TtlRange`s and supports add, remove, overlap lookup, expiration cleanup, and iteration. `CompactionGuardGeneratorFactory<P>` validates CF names and creates `CompactionGuardGenerator<P>` from RocksDB partitioner context. `CompactionGuardGenerator` tracks compaction input keys, region boundary keys, next-level SST boundaries/sizes, current cursors, min output size, max compaction size, and force ranges. Helper functions `overlap_with` and `seek_to` handle range overlap and cursor advancement with binary-search fallback.

Control flow: The factory's `create_partitioner` captures context cheaply and defers region provider queries until `should_partition`. `initialize` maps engine keys to data/origin key ranges, asks `RegionInfoProvider` for covered regions, converts region end keys to data keys, merges force range boundaries, sorts/dedups boundaries, and enables or disables guard use. `should_partition` seeks to the next boundary and next-level segments crossed by the current key pair. It requires partitioning when a boundary is crossed and either the current output file is large enough, accumulated next-level overlap reaches `max_compaction_size`, or the key interval overlaps a force-partition range.

State and persistence: The manager's TTL ranges are in-memory control state. The generator's cursors are per-compaction in-memory state. Persistent impact is RocksDB SST layout: compaction output files can be split at region and forced boundaries, reducing future cross-region compaction amplification and honoring temporary split hints.

Dependencies and integration points: It depends on engine trait partitioner interfaces, CF names, TiKV key encoding (`DATA_PREFIX_KEY`, `origin_key`, `data_end_key`), raftstore metrics, and coprocessor `RegionInfoProvider`. It integrates with RocksDB through `SstPartitionerFactory` and `SstPartitioner`.

Risks: Region provider failure disables guard for that compaction after logging and metrics. The guard intentionally skips partitioning small output files unless next-level size or force ranges justify a split, so some regions may share SSTs. `create_partitioner` avoids querying under RocksDB mutex, but the first `should_partition` can still pay provider cost. Force ranges require correct key-space convention; they are merged and expired lazily. The code resets next-level accumulated size after partition, accepting possible undercount of a segment already crossed.

Test signals: Unit tests cover non-data key initialization, partition decisions for output size, boundary crossing, force ranges, next-level size accumulation, binary-search cursor fallback, overlap logic, force range merging/expiration behavior, and RocksDB integration that inspects resulting SST files and level layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/compaction_guard.rs -->
