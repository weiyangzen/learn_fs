# Research Group subset-b-008854

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/peer_storage.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/peer_storage.rs

## Purpose
`peer_storage.rs` is the Raft storage adapter for a TiKV region peer. It implements the `raft::Storage` contract on top of TiKV's separated KV and Raft engines, owns the in-memory storage-facing view of region metadata, coordinates snapshot generation/application, and prepares `WriteTask`s for async persistence. The file is also responsible for local peer metadata initialization and cleanup, including crash-recovery paths where snapshot metadata may have been written to one engine but not the other.

## Important APIs, Types, and Functions
The key type is `PeerStorage<EK, ER>`, parameterized by `KvEngine` and `RaftEngine`. It wraps `Engines<EK, ER>`, the current `metapb::Region`, local peer identity, a `SnapState`, optional `GenSnapTask`, a region worker scheduler, retry counters, and an `EntryStorage<EK, ER>`. `Deref`/`DerefMut` expose `EntryStorage`, so methods such as `append`, `term`, `first_index`, `last_index`, `applied_index`, `raft_state`, and cache maintenance are integrated as if they belonged to `PeerStorage`.

`SnapState` models snapshot lifecycle: `Relax`, `Generating { canceled, index, receiver }`, `Applying(status)`, and `ApplyAborted`. `CheckApplyingSnapStatus` maps worker status atomics into peer-FSM decisions. Constants such as `RAFT_INIT_LOG_INDEX`, `RAFT_INIT_LOG_TERM`, `INIT_EPOCH_VER`, and job status integers encode bootstrap and snapshot-worker invariants.

Initialization flows through `PeerStorage::new`, `init_raft_state`, and `init_apply_state`. If a region is already initialized but lacks persisted state, the initial log index/term and applied/truncated state are seeded at `5`, which forces new followers to obtain a snapshot before normal log catch-up. `recover_from_applying_state` repairs a crash window by comparing a KV-side snapshot raft state with the raft-engine raft state and, if the snapshot state has a higher commit, cleaning raft logs and copying that state into the raft engine.

Snapshot APIs include `snapshot`, `validate_snap`, `need_gen_snap_precheck`, `cancel_generating_snap`, `apply_snapshot`, `handle_raft_ready`, and `persist_snapshot`. Metadata helpers include `clear_meta`, `clear_meta_in_kv_and_raft`, `write_initial_raft_state`, `write_initial_apply_state`, and `write_peer_state`. `do_snapshot` builds an actual raft snapshot via `SnapManager`.

## Control Flow
For normal raft reads, the raft crate calls the `Storage` implementation, which delegates entries and terms to `EntryStorage`. `initial_state` returns an empty `ConfState` for uninitialized peers with default hard state, otherwise derives the conf state from the current region. Snapshot requests enter `PeerStorage::snapshot`: witness leaders refuse snapshot generation, witness recipients can receive an empty snapshot if local apply has caught up, and normal recipients use an asynchronous generation task. Existing generation is polled with `try_recv`; stale, canceled, disconnected, or decode/epoch-invalid results cause retry or error. Retry count is capped by `MAX_SNAP_TRY_CNT`.

Incoming raft `Ready` values are handled by `handle_raft_ready`. It creates a `WriteTask`, applies a non-empty ready snapshot into that task, appends ready entries, updates hard state when appropriate, and records a raft-state write only when state changed or a snapshot is present. For snapshots, it also writes a KV copy of the snapshot raft state and the apply state so restart recovery can bridge the KV/raft engine write ordering.

Applying a snapshot decodes `RaftSnapshotData`, verifies region id, prepares raft/KV write batches, clears existing metadata if initialized, tombstones overlapped destroy regions, writes the new `RegionLocalState` as `Applying` unless it is a witness snapshot, and updates last/applied/truncated indexes and terms in memory. `persist_snapshot` then schedules actual data cleanup/application work, handles source-region extra-data cleanup for merges, bypasses the async apply worker for witness snapshots, and finally updates the stored region.

Destroy flow is split between in-peer scheduling and worker-side synchronous cleanup. `schedule_destroy_peer` clears entry caches and force-schedules `RegionTask::ClearPeerMeta`. `clear_meta_in_kv_and_raft` coordinates with `StoreMeta` and `pending_create_peers`, writes KV tombstone state with sync write options, then consumes the raft log batch synchronously.

## State and Persistence Behavior
This file spans three state surfaces: in-memory `PeerStorage`/`EntryStorage`, KV CF_RAFT metadata, and raft-engine logs/state. KV metadata includes region state, apply state, and temporary snapshot raft state. Raft engine state includes `RaftLocalState` and raft logs. Persistence order is deliberate: snapshot apply writes KV state that can survive a crash before raft-engine state is consumed; peer destroy writes tombstone metadata to KV first with sync enabled, then consumes raft cleanup. The code comments call out crash windows and explain why `recover_from_applying_state` exists.

Snapshot generation registers `SnapEntry::Generating` with `SnapManager`, validates the KV snapshot's apply state against the caller-supplied last applied state, verifies the region is still `PeerState::Normal`, builds snapshot files, and serializes `RaftSnapshotData` into raft snapshot data. Snapshot cancellation uses atomics shared with generation workers and optional compaction indexes to avoid canceling still-valid snapshots.

## Dependencies and Integration Points
The module integrates `engine_traits`, `kvproto` raft/metapb messages, `raft::Storage`, `EntryStorage`, async IO `ReadTask`/`WriteTask`, region workers, `SnapManager`, `StoreMeta`, peer utilities, metrics, failpoints, and TiKV key encoders. `read_queue.rs` and `simple_write.rs` sit elsewhere in peer request flow, while `region_snapshot.rs` uses `PeerStorage::raw_snapshot` and `PeerStorage::region` to build bounded read snapshots.

## Risks and Edge Cases
The highest-risk areas are cross-engine persistence ordering, snapshot staleness validation, witness snapshot special cases, destroy/create races under local first replicate, and cleanup of extra data around merge/split ranges. `clear_meta_in_kv_and_raft` contains panics for inconsistent pending-create state. `handle_raft_ready` intentionally skips hard-state persistence when `last_index == 0`, so incorrect initialization could suppress necessary persistence. Snapshot retry accounting is subtle: canceled attempts do not always increment `snap_tried_cnt`, unknown peers do not count, and disconnected generation channels trigger retries.

## Test Signals
Tests cover term lookup, metadata cleanup, async entry fetch fallback, compaction boundaries, snapshot generation retry/staleness/cancellation behavior, multi-file snapshot layout for TiKV/TiFlash/witness roles, snapshot application state transitions, cancel/check apply snapshot status transitions, and validation failures for inconsistent raft/apply state. These tests exercise both in-memory invariants and persisted engine state.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/peer_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/read_queue.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/read_queue.rs

## Purpose
`read_queue.rs` manages pending ReadIndex requests for region peers. It batches client callbacks behind raft read-index contexts, advances requests when raft returns read states, tracks readiness separately from queue position, and serializes/deserializes the opaque context bytes carried through raft. It supports both leader-local ordering and follower/replica out-of-order responses.

## Important APIs, Types, and Functions
`ReadIndexRequest<C>` stores one logical read-index context UUID, the pending raft commands and callbacks, the proposal timestamp, optional resolved read index, optional extra `ReadIndexRequest` protobuf for lock checking, optional `LockInfo`, and an `in_contexts` flag indicating whether the UUID is still tracked in the queue's context map. `push_command`, `with_command`, `cmds`, and `take_cmds` are the main request APIs. `Drop` records pending duration metrics.

`ReadIndexQueue<C>` stores a `VecDeque<ReadIndexRequest<C>>`, `ready_cnt`, `handled_cnt`, a `HashMap<Uuid, usize>` from UUID to absolute queue offset, retry countdown, and log tag. Its main APIs are `check_needs_retry`, `has_unresolved`, `clear_all`, `clear_uncommitted_on_role_change`, `push_back`, `advance_leader_reads`, `advance_replica_reads`, `pop_front`, `push_front`, and `gc`.

`ReadIndexContext` encodes the raft context payload. The first 16 bytes are always the UUID. Optional tagged fields carry a protobuf `raft_cmdpb::ReadIndexRequest`, protobuf `LockInfo`, and a `read_index_safe_ts` u64. `parse`, `to_bytes`, and `fields_to_bytes` provide backward-compatible serialization; a bare UUID remains valid old-format context.

## Control Flow
Requests enter via `ReadIndexRequest::with_command` and `ReadIndexQueue::push_back`. Leader requests are queued without UUID map entries because leader read states are expected to advance strictly in queue order. Follower/replica requests are inserted into `contexts` with an absolute offset equal to `handled_cnt + reads.len()` so later pops do not invalidate stored offsets.

Retry handling is tick-based. `check_needs_retry` returns false if all queued reads are already ready, uses `usize::MAX` as a just-pushed sentinel, decrements countdown while waiting, and returns true when unresolved requests should be retried through raft.

Leader advancement uses `advance_leader_reads`, comparing each returned UUID with `reads[ready_cnt]`. A mismatch logs surrounding expected/actual UUID context and panics, preserving the invariant that leader read states must arrive in request order. Replica advancement uses `advance_replica_reads`, removes UUIDs from `contexts`, converts absolute offsets back to current deque offsets by subtracting `handled_cnt`, records lock information, clears `addition_request` to signal lock checking completion, and updates `read_index` to the lowest observed index when multiple states touch the same request. It then marks all requests through the highest changed offset ready, allowing out-of-order replica responses to release a prefix.

Ready requests are consumed with `pop_front`, which decrements `ready_cnt`, increments `handled_cnt`, removes still-tracked contexts, and returns the request. `push_front` requeues a popped ready request when raft cannot yet process it, restoring `ready_cnt` and `handled_cnt`.

## State and Persistence Behavior
The queue is memory-only; persistence happens through raft's read-index mechanism rather than local storage. Metrics are stateful side effects: pending count increments when commands are added, decrements on queue clearing, and pending duration is observed on `ReadIndexRequest` drop. Memory accounting is implemented in the `memtrace` module through `HeapSize`, including command heap usage, optional extra request memory, deque capacity, and context-map estimates.

## Dependencies and Integration Points
The module depends on `kvproto` raft command and lock messages, `uuid`, TiKV metrics, `MustConsumeVec` callback safety, store config, and apply notification helpers. It integrates with peer FSM role changes through `clear_uncommitted_on_role_change`, with region removal through `clear_all(Some(region_id))`, and with raft Ready read states through the leader/replica advance methods.

## Risks and Edge Cases
The absolute-offset scheme depends on accurate `handled_cnt` updates in every pop/push-front path. Incorrect role-change sequencing could leave stale contexts, which is why tests cover leader-to-follower and retake-leadership flows. `ReadIndexContext::parse` trusts encoded lengths enough to slice buffers; malformed internal raft contexts can panic or error depending on the field. The `READ_INDEX_SAFE_TS_FLAG` length is encoded as an eight-byte number containing the fixed u64 length, which is unusual and must remain compatible with the parser.

## Test Signals
Tests validate backward-compatible UUID-only context parsing, context serde for request/lock/safe-ts fields, role changes from follower to leader to follower, leadership retake after an unhandled ready read, and out-of-order replica advancement. These tests target the key invariants around context-map cleanup and queue offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/read_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/region_meta.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/region_meta.rs

## Purpose
`region_meta.rs` defines serde-friendly debug/status structures that expose raft and region metadata without requiring protobuf-generated types to derive serde directly. The output is a compact, serializable snapshot of peer state for diagnostics, inspection APIs, and tests.

## Important APIs, Types, and Functions
The file defines mirror enums and structs for raft progress and region metadata. `RaftProgressState` mirrors raft `ProgressState`. `RaftProgress` captures matched index, next index, state, pause flag, pending snapshot/request-snapshot indexes, and recent activity. `RaftHardState`, `RaftStateRole`, and `RaftSoftState` expose hard and soft raft state. `RaftStatus` aggregates raft node id, hard/soft state, applied index, voter and learner progress maps, last index, persisted index, and test-only unstable entry statistics.

Peer and region wrappers include `RaftPeerRole`, `Epoch`, `RegionPeer`, `RegionMergeState`, `RaftTruncatedState`, `RaftApplyState`, `RegionLocalState`, and top-level `RegionMeta`. Conversion implementations map raft/protobuf types into these serde structs, including bidirectional conversion between `RaftPeerRole` and `metapb::PeerRole`, plus equality helpers against protobuf peers.

The main constructor is `RegionMeta::new(local_state, apply_state, group_state, raft_status, last_index, persisted_index)`. It copies region id/range/epoch/peers, optional merge target state, tablet index, raft apply/truncate indexes, raft status, and group state into one serializable value.

## Control Flow
Construction starts from a protobuf `RegionLocalState`, protobuf `RaftApplyState`, a `GroupState`, raft `Status<'_>`, and caller-supplied log indexes. `RegionMeta::new` reads the embedded region, converts every peer into `RegionPeer`, converts merge state only if present, converts raft status through `From<raft::Status>`, then patches `last_index` and `persisted_index` because raft status itself does not supply those storage-level values. Bucket keys are initialized as an empty vector for later population by callers.

`From<raft::Status>` builds progress maps only when raft exposes progress, splitting entries into voters and learners according to the raft configuration. `From<ProgressState>` and `From<StateRole>` are exhaustive over current raft variants. Peer-role conversions are exhaustive over protobuf peer roles and preserve witness state separately at `RegionPeer`.

## State and Persistence Behavior
This module does not persist or mutate raftstore state. It snapshots in-memory/protobuf state into owned Rust structs containing primitive values, vectors, and maps. The serialized shape is intentionally independent from protobuf internals, which makes it useful for JSON/debug output but also means it must be maintained when raft or kvproto state grows.

## Dependencies and Integration Points
Dependencies are limited to `kvproto::{metapb, raft_serverpb}`, the raft crate's `Progress`, `Status`, and role enums, serde derives, and `super::GroupState`. The likely integration point is region/peer inspection code that wants a stable serializable `RegionMeta` rather than raw protobuf or raft structs. `replication_mode.rs` influences commit grouping but is separate from the `GroupState` carried here.

## Risks and Edge Cases
Because this is a mirror layer, drift is the main risk. New raft progress states, peer roles, local-state fields, bucket metadata fields, or unstable-entry fields can be silently omitted unless this file is updated. The voter/learner split depends on `progress.conf().voters().contains(*id)`; all non-voter progress is categorized as learner, which may hide more detailed joint-consensus roles in this debug projection. `RegionPeer::PartialEq<metapb::Peer>` converts into a protobuf peer and compares all populated fields, but comments acknowledge the comparison is conservative rather than a custom semantic match.

## Test Signals
There are no local tests in this file. Compile-time exhaustiveness checks cover enum conversions. Behavioral confidence depends on callers/tests that serialize or inspect `RegionMeta`, plus any testexport feature coverage for unstable entry metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/region_meta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/region_snapshot.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/region_snapshot.rs

## Purpose
`region_snapshot.rs` wraps an engine snapshot so reads and iterators are constrained to a single TiKV region. It translates logical user keys to TiKV data keys, enforces region boundaries, exposes apply-index/data-version metadata, and supplies a region-aware iterator for scans and reverse scans.

## Important APIs, Types, and Functions
`RegionSnapshot<S: Snapshot>` owns an `Arc<S>` engine snapshot, `Arc<Region>`, lazily cached apply index, a `from_v2` data-version mode flag, optional raft term, transaction extra operation, optional transaction extensions, optional bucket metadata, and an optional observed snapshot hook. Constructors include `new(&PeerStorage)`, `from_raw(db, region)`, and `from_snapshot(snap, region)`.

Important methods include `set_observed_snapshot`, `replace_snapshot`, `get_region`, `get_snapshot`, `set_from_v2`, `get_data_version`, `set_apply_index`, `get_apply_index`, `iter`, `scan`, `get_start_key`, and `get_end_key`. The `Peekable` implementation provides bounded `get_value_opt` and `get_value_cf_opt`.

`RegionIterator<S>` wraps the engine iterator and region metadata. It exposes RocksDB-style iterator methods: `seek_to_first`, `seek_to_last`, `seek`, `seek_for_prev`, `prev`, `next`, `key`, `value`, `valid`, and `should_seekable`. Helper functions `update_lower_bound` and `update_upper_bound` clamp iterator bounds to encoded region boundaries.

## Control Flow
Point reads validate that the logical key belongs to `[region.start_key, region.end_key)` via engine utility checks, encode it with `keys::data_key`, and delegate to the underlying snapshot. On engine errors, `handle_get_value_error` increments critical-error metrics and either panics with a panic marker or logs and returns the engine error depending on TiKV's unexpected-key/data panic configuration.

Apply index is loaded lazily. `get_apply_index` returns the cached atomic value if nonzero; otherwise `get_apply_index_from_storage` reads `RaftApplyState` from CF_RAFT using the region id, stores the applied index back into the atomic, and returns it. `get_data_version` returns the underlying snapshot sequence number in v2 mode, rejecting zero, otherwise the apply index.

For scans, `scan` builds data-key lower/upper bounds from logical keys, creates a `RegionIterator`, seeks to the start key, and loops until the callback returns false or the iterator is exhausted. `RegionIterator::new` clamps any caller-provided bounds against `enc_start_key(region)` and `enc_end_key(region)` before creating the engine iterator. `seek` and `seek_for_prev` enforce inclusive region seekability, encode the seek key, and delegate to the engine iterator. Returned keys are decoded back to origin keys with `keys::origin_key`.

`replace_snapshot` consumes the wrapper, extracts the inner snapshot with `Arc::into_inner`, optionally transfers the observed snapshot hook, and builds a new `RegionSnapshot<Sp>`. It intentionally panics if the snapshot has already been cloned, preserving ownership assumptions for replacement.

## State and Persistence Behavior
This module is read-only with respect to user data. Its only mutation is local metadata caching (`apply_index`) and wrapper replacement. It reads persisted apply state from CF_RAFT when needed. Iterator bounds are encoded data-key bounds, so region isolation depends on correct key encoding and correct region metadata supplied by `PeerStorage` or callers.

## Dependencies and Integration Points
The file depends on `engine_traits` snapshot, iterator, read options, metrics, and range checks; `keys` data-key encoding; `kvproto` region/apply-state messages; PD bucket metadata; TiKV critical-error/panic hooks; and `PeerStorage`. It integrates directly with coprocessor observed snapshots, transaction extension metadata, and read paths that need a `Peekable`/iterable view limited to a region.

## Risks and Edge Cases
Region boundary handling is the core risk. Point gets use exclusive end-key checks, while iterator `should_seekable` allows inclusive checks so `seek(end_key)` can legally produce no result at the boundary. Incorrect lower/upper-bound prefix handling could leak keys outside a region or hide in-range keys. `replace_snapshot` will panic if clones exist; callers must use it before sharing the snapshot. Malformed or missing apply state causes data-version errors. Error handling can intentionally panic under strict corruption-detection settings.

## Test Signals
Tests cover point reads inside and outside a region, seek/seek-for-prev behavior across lower and upper bounds, multi-level flushed/compacted datasets, forward scans with early termination, whole-range behavior for the last region with empty end key, iterator upper bounds, and reverse iteration with lower bounds. These tests directly exercise region isolation around boundary keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/region_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/replication_mode.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/replication_mode.rs

## Purpose
`replication_mode.rs` tracks global replication-mode metadata and maps stores into commit groups for disaster-recovery auto-sync mode. It lets raftstore calculate per-peer group ids from store labels while preserving labels across majority-mode periods.

## Important APIs, Types, and Functions
`StoreGroup` is the main registry. It stores backed-up labels by store id, label-value to group-id mapping, store-id to group-id mapping, active label key, current version/state id, and a dirty flag. Key methods are `backup_store_labels`, `register_store`, `group_id`, and private `recalculate`.

`GlobalReplicationState` wraps the current `ReplicationStatus`, a public `StoreGroup`, and a reusable `group_buffer`. It exposes `status`, `set_status`, `calculate_commit_group`, and `store_dr_autosync_status`.

## Control Flow
When the system is in majority mode, `backup_store_labels` can save a store's labels after taking them from the store object. If the saved labels are unchanged it does nothing; otherwise it marks the registry dirty. `register_store` associates a live store with labels. If the store is already registered, the same label key must map to the same group id or the function panics. If the store is new and the active label key exists in its labels, the label value is assigned an existing or new group id and the store is mapped to it. Stores missing the active label key can be known in `labels` but have no group id.

`set_status` stores a new PD replication status and calls `StoreGroup::recalculate`. Recalculation is skipped in majority mode and skipped when label key and dirty flag are unchanged. Otherwise, the new DR state id must increase, caches are cleared, the active label key and version are updated, and every saved store label is scanned to rebuild store/group mappings.

`group_id(version, store_id)` returns no group when the caller's version is older than the registry version, preventing regions computed under older label keys from mixing with newer group assignments. `calculate_commit_group` clears and reuses `group_buffer`, walking region peers and adding `(peer_id, group_id)` for peers whose store currently has a group id. `store_dr_autosync_status` exposes only the DR auto-sync state/state-id subset when the mode is `DrAutoSync`.

## State and Persistence Behavior
This module is in-memory state. Durability comes from external PD/store metadata feeds, not from local persistence here. The `version` field is the DR auto-sync state id and gates stale calculations. The dirty flag makes label backups visible to the next recalculation even if the label key did not change.

## Dependencies and Integration Points
The module depends on `kvproto::metapb` stores/peers and `replication_modepb` mode/status messages. It integrates with store heartbeat or PD status update paths that call `set_status`, store registration paths that call `register_store` or `backup_store_labels`, and raft proposal/commit logic that needs commit groups for a region's peer set.

## Risks and Edge Cases
Several invalid state transitions intentionally panic: recalculating with a non-increasing state id, registering an already grouped store with labels that imply a different group, or registering an already grouped store without the active label key. Group ids are assigned by `HashMap`/insertion progression over stored labels, so tests should guard expected behavior but external code should not depend on stable ids beyond a given process/state calculation. Switching back to majority mode does not clear cached group ids, by design, so callers must respect mode/version semantics.

## Test Signals
`test_group_register` verifies delayed group assignment before DR status, grouping by zone labels, adding stores after calculation, majority-mode preservation, recalculation with newer state ids, and label-key switch to host. `test_backup_store_labels` verifies backup while labels are taken from stores, dirty-triggered recalculation, stores without group ids later updating labels, and panic on attempts to change a calculated group id.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/replication_mode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/simple_write.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/simple_write.rs

## Purpose
`simple_write.rs` implements a compact binary encoding for simple raft write commands. It avoids full `RaftCmdRequest` protobuf overhead for common put/delete/delete-range/ingest operations, supports batching compatible operations with the same header, and can decode back into normal raft command requests when needed.

## Important APIs, Types, and Functions
`SimpleWriteEncoder` builds a `SimpleWriteBinary` by appending `put`, `delete`, `delete_range`, or `ingest` operations. `SimpleWriteBinary` owns the encoded operation bytes and records a private `WriteType`; `freeze` marks it unbatchable and `data_size` reports encoded size. `SimpleWriteReqEncoder<C>` wraps a raft request header, a magic-prefixed buffer containing length-delimited header plus simple-write operations, response channels, a size limit, and a write type. Its main APIs are `new`, `amend`, `encode`, `add_response_channel`, `data_size`, and `header`.

Operation structs are `Put`, `Delete`, `DeleteRange`, and enum `SimpleWrite<'a>`, with `Ingest(Vec<SstMeta>)` for SST ingestion. `SimpleWriteReqDecoder<'a>` parses request buffers. `new` detects `MAGIC_PREFIX`; if absent it returns a fallback-decoded `RaftCmdRequest`. It implements `Iterator<Item = SimpleWrite<'a>>` and can materialize a full protobuf request via `to_raft_cmd_request`.

Private codec helpers include `encode_len`/`decode_len`, `encode_bytes`/`decode_bytes`, `encode_cf`/`decode_cf`, `encode`, and `decode`. CF names use one-byte tags for default/write/lock and an arbitrary string tag for other CFs. Operation tags distinguish put, delete, delete range, and ingest.

## Control Flow
Encoding starts with operation-level `SimpleWriteEncoder`. Each mutating method debug-asserts that operations are compatible with the existing write type: put/delete can mix, delete-range batches only with delete-range, and ingest batches only with ingest. `encode` freezes the current buffer into `SimpleWriteBinary`.

`SimpleWriteReqEncoder::new` creates the raft-log payload by writing `MAGIC_PREFIX`, serializing the header as a length-delimited protobuf, and appending the operation bytes. `amend` batches another binary only if headers are identical, write types match, the incoming type is not `Unspecified`, and the size limit would not be exceeded. Response callbacks are tracked separately in `channels` and returned with encoded bytes.

Decoding first checks the magic byte. Non-magic data is delegated to a caller-supplied fallback parser for normal protobuf raft commands. Magic data reads the length-delimited header and leaves the remaining operation bytes for iteration. The iterator repeatedly calls `decode`, which slices borrowed keys/values from the input for put/delete/delete-range and reads length-delimited `SstMeta` protobuf messages for ingest. `to_raft_cmd_request` converts each decoded simple operation into its equivalent protobuf `Request`.

The variable-length length codec uses a SQLite4-inspired scheme optimized for short keys/values: one byte up to 240, two bytes through 2287, three through 67823, then tagged big-endian three- or four-byte forms for larger values.

## State and Persistence Behavior
The module does not persist directly; its encoded buffers become raft log entry data elsewhere. Compatibility hinges on `MAGIC_PREFIX == 0x00`, chosen because protobuf field tags cannot start with zero. Old/non-simple log entries remain decodable through fallback. Corrupted magic-prefixed data panics or `slog_panic!`s while reading the header, and lower-level decode helpers also panic on malformed internal buffers.

## Dependencies and Integration Points
Dependencies include engine CF constants, kvproto raft command and SST metadata messages, protobuf coded streams, slog logging, and store callback traits. The codec integrates with raft proposal batching and apply-side command decoding. `peer_storage.rs` persists raft entries that may contain these compact buffers, while apply logic can use `SimpleWriteReqDecoder` to process them or convert back to protobuf requests.

## Risks and Edge Cases
The decoder assumes trusted raft log data after magic detection; truncated lengths, invalid CF tags, invalid UTF-8 arbitrary CFs, and invalid operation tags panic. Batching relies on `WriteType`; an empty encoder has `Unspecified`, and `freeze` prevents later coalescing. `amend` uses a strict `< size_limit` check, so exactly equal size is rejected. Ingest uses protobuf per SST for simplicity, so it does not share the zero-copy behavior of key/value operations.

## Test Signals
Tests validate put/delete/delete-range/ingest round trips, arbitrary CF names, header preservation, variable-length number boundaries, fallback decoding of normal protobuf `RaftCmdRequest`, rejection of mismatched headers/frozen binaries/oversized batches, and conversion back to full `RaftCmdRequest` for each operation type.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/simple_write.rs -->
