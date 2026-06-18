# subset-b-006933 research

Grouped source-tree-aligned research for Ceph OSD erasure-coded backend common code, the legacy backend wrapper, and the modern and legacy EC extent caches. Each section is delimited for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackendL.cc -->
# sources/distributed-fs/ceph/src/osd/ECBackendL.cc

## Purpose

Implements the legacy erasure-coded PG backend (`ECLegacy::ECBackendL`) that adapts `ECCommonL` to the classic `PGBackend`/`ECSwitch` objectstore environment. It owns legacy EC recovery orchestration, sub-read/sub-write message dispatch, RMW transaction submission, hash-info validation for non-overwrite EC pools, and backend-specific scrub/read helpers.

## Important APIs, Types, and Functions

Key local types are `ECRecoveryHandle`, `RecoveryMessages`, `SendPushReplies`, `RecoveryReadCompleter`, and `ECClassicalOp`. The central entry points are `ECBackendL::ECBackendL`, `open_recovery_op`, `run_recovery_op`, `recover_object`, `_handle_message`, `handle_sub_write`, `handle_sub_read`, `handle_sub_write_reply`, `handle_sub_read_reply`, `submit_transaction`, `objects_read_async`, and `be_deep_scrub`. `RecoveryBackend` methods implement the legacy recovery state machine using `PushOp` and `PushReplyOp`. `ECClassicalOp::generate_transactions()` delegates per-shard transaction generation to `ECTransactionL::generate_transactions()`.

## Control Flow and Data Flow

Construction wires `read_pipeline`, `rmw_pipeline`, and `recovery_backend` around the same erasure-code implementation and stripe layout. Incoming OSD messages enter `_handle_message()`, which switches on EC sub-write, EC sub-read, their replies, and PG push/push-reply messages. Sub-writes log non-primary operations, queue the shard transaction plus local log transaction, and reply through `SubWriteCommitted`; sub-reads read shard ranges from the local store, optionally perform fragmented subchunk reads, optionally fetch attrs, validate legacy hinfo digests when overwrites are disabled, and return `ECSubReadReply`.

Recovery batches objects in `ECRecoveryHandle`; `run_recovery_op()` moves them into `recovery_ops` and drives `continue_recovery_op()`. The legacy state machine reads a chunk of missing shard data, decodes into `returned_data`, pushes missing shard buffers and attrs, waits for push replies, and either loops or reports peer/global recovery completion. Client reads flow through `objects_read_async()`, which aligns requested logical ranges to stripe/chunk bounds, calls `objects_read_and_reconstruct()`, and slices decoded results back into caller buffers.

## State and Persistence Behavior

Persistent mutations are objectstore transactions: sub-writes queue shard transactions and local PG log transactions, recovery writes temporary or final shard objects, and completed recovery can rename temp objects into place. Runtime state includes `read_pipeline.tid_to_read_map`, `rmw_pipeline.tid_to_op_map` and intrusive queues inherited from `ECCommonL`, `recovery_backend.recovery_ops`, temp object sets managed through the listener/switcher, and unstable hinfo entries in `unstable_hashinfo_registry`. `on_change()` clears RMW, read, and recovery state on interval change; `check_recovery_sources()` cancels or reschedules reads whose source OSDs went down.

## Dependencies and Integration Points

This file depends on `ECCommonL`, `ECTransactionL`, `ECExtentCacheL`, `ECUtilL`, `ECMsgTypes`, `ECInject`, `ECSwitch`, `PrimaryLogPG`, `MOSDECSubOp*`, and `MOSDPGPush*`. It uses `PGBackend::Listener`/`ECListener` for PG metadata, missing sets, message sends, stats, log operations, recovery callbacks, temp object management, and transaction queueing. The objectstore surface is reached through `switcher->store`, `switcher->ch`, and `switcher->coll`.

## Risks and Edge Cases

Read retry logic must preserve `obj_to_source`, `source_to_obj`, and `want_to_read` consistency or recovery cancellation can drop the wrong object. Legacy hinfo handling is high risk: missing, undecodable, or size-mismatched hinfo causes EIO/failed pull, while sanitization must keep the internal hinfo attr from leaking to higher layers. The recovery code assumes the requested extent length and decoded shard buffer sizes match stripe math exactly. `handle_sub_read_reply()` has many iterator and in-place mutation paths, including error injection erases, so malformed replies or partial cancellation can expose assertion-only failures. Deep scrub intentionally degrades digest semantics for EC overwrites, so tests should distinguish unsupported digest behavior from corruption.

## Test Signals

Useful tests cover EC read success, redundant fast read, retry after one shard EIO, cancellation on map change, subchunk fragmented reads, attr fetch failure, legacy hinfo missing/bad digest/size mismatch, RMW commit ordering, backfill/asynchronous recovery temp object cleanup, recovery source loss after first read, snap recovery metadata, dummy roll-forward ops, and deep scrub digest/hash mismatch reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackendL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackendL.h -->
# sources/distributed-fs/ceph/src/osd/ECBackendL.h

## Purpose

Declares the legacy EC PG backend interface and its nested recovery/read/write support classes. It is the header contract for code that still routes erasure-coded PG operations through the legacy `ECLegacy::ECCommonL` path while exposing `PGBackend`-style recovery, read, write, scrub, and predicate APIs.

## Important APIs, Types, and Functions

`ECBackendL` derives from `ECCommonL` and exposes recovery (`open_recovery_op`, `run_recovery_op`, `recover_object`, `dump_recovery_info`), message handling (`_handle_message`, `can_handle_while_inactive`), sub-op handlers, read helpers (`objects_read_local`, `objects_read_async`, `objects_read_and_reconstruct`), write submission (`submit_transaction`, `call_write_ordered`), and scrub/stat helpers. Nested `RecoveryBackend` stores `RecoveryOp` state, read pipeline references, hinfo registry access, and virtual `commit_txn_send_replies()`. `ECRecoveryBackend` binds that abstraction to `PGBackend::Listener`. `ECRecPred` and `ECReadPred` expose recoverability/readability predicates based on the erasure-code plugin.

## Control Flow and Data Flow

The class aggregates `ReadPipeline`, `RMWPipeline`, and `ECRecoveryBackend`. Public PGBackend-facing methods delegate to the nested pipelines/backends, while backend-specific implementations in the `.cc` file supply objectstore access and listener callbacks. `RecoveryOp` carries `hoid`, version, missing shards, `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, decoded `returned_data`, xattrs, hinfo, object context, waiting push shards, and the currently requested extent.

## State and Persistence Behavior

The header defines in-memory state only. Persistent effects are deferred to `submit_transaction`, sub-write handling, recovery push handling, and scrub implementations in the `.cc` file. Notable in-memory state includes `parent`, `cct`, `switcher`, `ec_impl`, `sinfo`, `unstable_hashinfo_registry`, pipeline queues/maps, and `recovery_ops`.

## Dependencies and Integration Points

The contract depends on `ECCommonL.h`, `PGBackend.h`, `OSD.h`, `ErasureCodeInterface`, `ECUtilL`, `ECTransactionL`, `ECExtentCacheL`, and `ECSwitch`. It is instantiated by `ECSwitch` and connected to `PGBackend::Listener`; it interoperates with legacy recovery messages declared in `ECMsgTypes` and object context/log types from the OSD layer.

## Risks and Edge Cases

The header mixes public PGBackend methods, nested recovery internals, and friendship, so ownership boundaries are weak. `RecoveryBackend` stores raw listener/backend pointers and references to shared pipeline/stripe state, making lifetime order important. `object_size_to_shard_size()` preserves `uint64_t::max()` as a sentinel. `ECRecPred` and `ECReadPred` depend on `minimum_to_decode()` semantics and shard id conversion; incorrect acting/missing sets directly change peering decisions.

## Test Signals

Tests should compile both legacy and non-legacy users, assert recoverability/readability predicates for k+m layouts with missing shards, verify `object_size_to_shard_size()` alignment including sentinel max, exercise recovery state dump formatting, and drive interval-change cleanup through `on_change()` and `clear_recovery_state()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackendL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommon.cc -->
# sources/distributed-fs/ceph/src/osd/ECCommon.cc

## Purpose

Implements the modern common erasure-coded backend logic shared by current EC backends: asynchronous shard reads, reconstruction, partial-read/subchunk selection, RMW write pipelining through `ECExtentCache`, recovery push/read state machinery including omap recovery, and write-plan construction.

## Important APIs, Types, and Functions

Read-path functions include `ReadPipeline::get_all_avail_shards`, `get_min_avail_to_read_shards`, `get_remaining_shards`, `start_read_op`, `do_read_op`, `objects_read_and_reconstruct`, `objects_read_and_reconstruct_for_rmw`, and `send_all_remaining_reads`. Write-path functions include `RMWPipeline::start_rmw`, `cache_ready`, `try_finish_rmw`, `finish_rmw`, `on_change`, `on_change2`, and `call_write_ordered`. Recovery functions include `RecoveryBackend::_failed_push`, `handle_recovery_push`, `handle_recovery_push_reply`, `update_object_size_after_read`, `handle_recovery_read_complete`, `dispatch_recovery_messages`, `continue_recovery_op`, and `recover_object`. Utility APIs include equality operators and `ECCommon::get_write_plan()`.

## Control Flow and Data Flow

Reads begin as logical ranges or prebuilt `read_request_t` objects. The pipeline computes wanted shard extents, asks the erasure-code plugin for the minimum decodable shard/subchunk set, applies object-size read/zero masks, sends `MOSDECSubOpRead` messages, records source maps, and completes once enough shard data is available. `ClientReadCompleter` zero-pads as needed, decodes into `shard_extent_map_t`, and returns logical extent maps in client completion order.

RMW writes enter `RMWPipeline::start_rmw()`, which creates one `ECExtentCache::Op` per write plan, executes the cache, and waits for cache reads. `cache_ready()` applies stats, generates shard transactions, sends local/remote `ECSubWrite`s, records pending commit counts, updates the extent cache with written data, and relies on sub-write replies to drain `pending_commits`. `finish_rmw()` preserves ordered completion, advances committed/completed versions, clears cache ops, and can submit an empty dummy op for roll-forward.

Recovery starts from `recover_object()` and `continue_recovery_op()`. It chooses missing shards, decides whether omap must be recovered, reads data/attrs/omap from available shards, loads object info if needed, updates object-size-dependent masks after first attrs, decodes missing data, pushes shard buffers and metadata, waits for replies, and reports peer/global recovery.

## State and Persistence Behavior

This file mostly manages in-memory coordination: `tid_to_read_map`, `shard_to_read_map`, `in_progress_client_reads`, `RMWPipeline::tid_to_op_map`, `waiting_commit`, `oid_to_version`, `pending_roll_forward`, `next_write_all_shards`, `first_write_in_interval`, and `recovery_ops`. Persistent changes are expressed as transactions built by backend-specific `generate_transactions()` implementations or recovery `RecoveryMessages::t`; `dispatch_recovery_messages()` sends push messages and commits reply transactions through the virtual backend hook.

## Dependencies and Integration Points

It depends on `ECCommon.h`, `ECInject`, `ECMsgTypes`, `PGLog`, `osd_tracer`, `MOSDECSubOpRead/Write`, `MOSDPGPush/Reply`, `ECUtil`, `ECTransaction`, `ECExtentCache`, and the configured `ErasureCodeInterface`. Listener callbacks supply acting/backfill shards, missing maps, pool omap support, object context loading, PG stats/logs, message transport, recovery callbacks, and objectstore transaction submission in concrete backends.

## Risks and Edge Cases

Shard selection is sensitive to plugin `minimum_to_decode()` behavior, subchunk support, partial-read masks, object-size unknowns, and redundant fast reads. Omap recovery must avoid dirty omap shards and must fail recovery when no clean primary-capable shard exists. `get_remaining_shards()` must avoid repeating already processed extents while still retrying attrs/omap header on a suitable non-primary shard. `on_change()` must be paired with `on_change2()` for the extent cache. The dummy roll-forward path and `first_write_in_interval` logic protect ordering/rollback invariants and are easy to regress with write pipeline changes.

## Test Signals

Test with k+m layouts that support and do not support partial reads, subchunk EC plugins, fast-read redundant reads, object size zero and unknown-at-first-read recovery, retry after one or more shard EIOs, attrs/omap header retry, dirty omap recovery avoidance, omap key pagination, RMW cache hit/miss/invalidating writes, interval changes during reads/writes, dummy roll-forward generation, and debug parity-read injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommon.h -->
# sources/distributed-fs/ceph/src/osd/ECCommon.h

## Purpose

Defines the modern shared EC backend abstractions for asynchronous shard reads, client reconstruction, RMW write coordination, recovery, and write planning. Concrete EC backends inherit or embed these structures and provide objectstore-specific sub-op handling, object context loading, and transaction commit behavior.

## Important APIs, Types, and Functions

Top-level `ECCommon` owns `ECOmapJournal` and defines `ec_extent_t`, `ec_extents_t`, `shard_read_t`, `read_request_t`, `read_result_t`, `ReadCompleter`, `ClientAsyncReadStatus`, `ReadOp`, `ReadPipeline`, `RMWPipeline`, `RecoveryBackend`, `RecoveryMessages`, `get_object_info_from_obc()`, and `get_write_plan()`. Important virtual methods are `handle_sub_write()`, `objects_read_and_reconstruct()`, and `objects_read_and_reconstruct_for_rmw()`.

## Control Flow and Data Flow

`ReadPipeline` converts logical read wishes into per-shard extent/subchunk reads, sends reads, tracks source/shard maps for cancellation, and hands final results to a `ReadCompleter`. `RMWPipeline` implements the backend-read listener required by `ECExtentCache`, wraps RMW operations with cache pins, routes cache misses to `objects_read_and_reconstruct_for_rmw()`, and sends EC sub-writes through the concrete backend. `RecoveryBackend` stores recovery ops and exposes a state-machine API for recovering missing shards from read results and push replies.

## State and Persistence Behavior

The header declares state containers but no direct persistence. Read state is keyed by tid and source shard. Client read completion is ordered via `in_progress_client_reads`. RMW state is keyed by tid/object, includes pending cache operations/commits, cache op references, roll-forward shard tracking, the EC extent cache, and write-mode flags. Recovery state is keyed by object and contains data, attrs, omap header/entries, object context, missing shards, and progress cursors.

## Dependencies and Integration Points

The type layer depends on `ECUtil`, `ECTypes`, `ECTransaction`, `ECExtentCache`, `ECOmapJournal`, `ECListener`, `ErasureCodeInterface`, `MOSDPGPushReply`, `OSDMap`, object context types, and optional Crimson types under `WITH_CRIMSON`. The `fmt::formatter` specializations allow these pipeline types to participate in fmt/ostream logging.

## Risks and Edge Cases

`read_request_t` carries both logical requests and derived shard state; callers must keep `object_size`, omap flags, and shard extent masks synchronized when retrying. `ReadOp` is move-only because of `unique_ptr<ReadCompleter>`, so code must avoid accidental copies. `RMWPipeline::Op` requires subclass implementations to generate and selectively skip transactions consistently with roll-forward and backfill rules. Template cancellation helpers in the header mutate maps while callbacks may schedule recovery work, so callback side effects must be bounded.

## Test Signals

Compile/test with and without `WITH_CRIMSON`, instantiate read requests with attrs and omap flags, validate `operator==` behavior for request structs, exercise `check_recovery_sources()`/`filter_read_op()` map mutation, verify RMW op lifecycle cleanup deletes `on_all_commit`, and test write-plan construction for creates, overwrites, truncates, clones/renames, cached objects, and different `ec_pdw_write_mode` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommonL.cc -->
# sources/distributed-fs/ceph/src/osd/ECCommonL.cc

## Purpose

Implements the deprecated/legacy common EC pipeline used by `ECBackendL`. It provides older read reconstruction, RMW ordering, intrusive extent-pin cache integration, and unstable hash-info registry behavior for pools that still follow legacy transaction and hinfo semantics.

## Important APIs, Types, and Functions

Important functions are stream/dump helpers, `ReadPipeline::complete_read_op`, `on_change`, `get_all_avail_shards`, `get_min_avail_to_read_shards`, static and member `get_min_want_to_read_shards`, `get_remaining_shards`, `start_read_op`, `do_read_op`, `objects_read_and_reconstruct`, `send_all_remaining_reads`, `kick_reads`, `RMWPipeline::start_rmw`, `try_state_to_reads`, `try_reads_to_commit`, `try_finish_rmw`, `check_ops`, `on_change`, `call_write_ordered`, and `UnstableHashInfoRegistry::{maybe_put_hash_info,get_hash_info}`.

## Control Flow and Data Flow

Read flow computes wanted shard ids, asks the EC plugin for decodable shard/subchunk choices, sends `MOSDECSubOpRead`, and stores replies as a list of aligned read tuples. `ClientReadCompleter` decodes each aligned tuple with `ECUtilL::decode()`, trims back to requested logical offsets, and completes client callbacks in submission order. On errors, `send_all_remaining_reads()` recomputes available shards excluding failed sources and resends remaining shard reads.

RMW flow is a three-queue state machine: `waiting_state`, `waiting_reads`, and `waiting_commit`. `try_state_to_reads()` respects cache invalidation state, opens a write pin, reserves extents in `ECExtentCacheL`, and issues no-cache reads for misses. `try_reads_to_commit()` merges cached and remote read results, calls the subclass transaction generator, updates the cache with written extents, sends local/remote sub-writes, and invokes on-write callbacks. `try_finish_rmw()` waits for apply/commit replies, advances versions, releases write pins, maybe schedules dummy roll-forward, and clears cache-invalid state once the pipe drains.

## State and Persistence Behavior

The file maintains in-memory read op maps, client-read completion queue, RMW queues, `tid_to_op_map`, cache pins, pending apply/commit sets, and the hinfo registry. Persistent effects are delegated to generated `ObjectStore::Transaction`s and remote sub-write handling. `on_change()` drops read operations, clears RMW queues, releases pins for outstanding ops, and resets the pipeline state.

## Dependencies and Integration Points

It depends on `ECCommonL.h`, `ECInject`, `ECMsgTypes`, `PGLog`, `MOSDECSubOp*`, `MOSDPGPush*`, `ECUtilL`, `ECTransactionL`, `ECExtentCacheL`, and `ErasureCodeInterface`. The parent `ECListener` supplies acting/backfill/missing state, OSDMap, PG info, transport, stats, and pool flags such as partial reads and overwrites.

## Risks and Edge Cases

This path is assertion-heavy and deprecated, so regressions may surface as aborts rather than recoverable errors. Partial-read trimming depends on stripe/chunk math and sorted wanted shard ids. The cache-invalid state blocks RMWs that need reads until the pipeline drains; missing a release or queue transition can deadlock writes. Hinfo decoding accepts empty objects but rejects size mismatches and decode failures; callers abort when hinfo cannot be obtained for write planning.

## Test Signals

Test legacy full-stripe and partial reads, fast-read redundant reads, parity-read debug injection, failed shard retry, RMW cache hit/miss, cache invalidation with outstanding reads, write apply/commit ordering for old peers, dummy roll-forward after rollback boundary, hinfo create/load/decode/size mismatch, and interval-change cleanup with outstanding read and write ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommonL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommonL.h -->
# sources/distributed-fs/ceph/src/osd/ECCommonL.h

## Purpose

Declares the legacy common EC abstractions in namespace `ECLegacy`. It is the type contract used by `ECBackendL` for older async reads, RMW write sequencing, extent cache pins, and hinfo lookup.

## Important APIs, Types, and Functions

Important declarations include `ECCommonL`, `ec_extent_t`, `read_request_t`, `read_result_t`, `ReadCompleter`, `ClientAsyncReadStatus`, `ReadOp`, `ReadPipeline`, `RMWPipeline`, `RMWPipeline::Op`, `RMWPipeline::pipeline_state_t`, and `UnstableHashInfoRegistry`. Virtual surface area includes `handle_sub_write()` and `objects_read_and_reconstruct()`. Header template methods implement `ReadPipeline::check_recovery_sources()` and `filter_read_op()`.

## Control Flow and Data Flow

`ReadPipeline` accepts object-to-logical-range maps plus wanted shard ids, computes/records per-source reads, tracks in-flight shards, and completes through a `ReadCompleter`. `RMWPipeline::Op` carries the PG transaction plan, remote read requirements/results, temp object sets, pending sub-op replies, callbacks, and a `ECExtentCacheL::write_pin`. The pipeline queues model ordered transitions from state gate to reads to commit. `UnstableHashInfoRegistry` provides shared refs for hash-info values that must live until corresponding transactions apply.

## State and Persistence Behavior

This header declares in-memory state: `tid_to_read_map`, `shard_to_read_map`, `in_progress_client_reads`, `ECExtentCacheL cache`, `tid_to_op_map`, intrusive wait queues, `completed_to`, `committed_to`, and `pipeline_state`. Persistent behavior is produced only by concrete `generate_transactions()` implementations and the backend's sub-write handlers.

## Dependencies and Integration Points

Dependencies include Boost intrusive containers, `sharedptr_registry`, `ErasureCodeInterface`, `ECUtilL`, `ECTypes`, optional Crimson object context and transaction headers, `ECTransactionL`, `ECExtentCacheL`, `ECListener`, and `fmt` stream formatters. It integrates tightly with `ECBackendL.cc`, which supplies concrete transaction generation and message handlers.

## Risks and Edge Cases

The intrusive queues require `Op` objects to outlive their list membership; `tid_to_op_map` owns them, so erasing the map at the wrong time can invalidate queue entries. `filter_read_op()` erases source/object mappings while iterating and cancels pulls through callbacks. `pipeline_state_t` gates cache validity globally for the pipeline, so one invalidating operation can block later RMW reads. `Op` destructor deletes `on_all_commit`, making callback ownership transfer explicit and potentially fragile.

## Test Signals

Compile legacy users, instantiate move-only `ReadOp`, exercise template cancellation with down OSD maps, check pipeline state transitions and formatting, verify hinfo registry ref sharing, and run sanitizer tests around intrusive queue cleanup on normal finish and `on_change()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECCommonL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCache.cc -->
# sources/distributed-fs/ceph/src/osd/ECExtentCache.cc

## Purpose

Implements the modern EC extent cache used by `ECCommon::RMWPipeline` to avoid rereading shard extents for overlapping or sequential partial writes. It combines per-object active cache lines with a per-OSD-shard LRU of recently used lines and coordinates cache reads, invalidation, and write updates without reordering IO.

## Important APIs, Types, and Functions

Important methods are `Object::request`, `send_reads`, `read_done`, `insert`, `write_done`, `invalidate`, `get_cache`, `ECExtentCache::prepare`, `execute`, `read_done`, `write_done`, `on_change`, `on_change2`, `idle`, `LRU::add`, `LRU::find`, `LRU::remove_object`, `LRU::free_maybe`, `LRU::discard`, and `Op::get_pin_eset`. `check_seset_empty_for_range()` asserts no outstanding request overlaps a line being erased.

## Control Flow and Data Flow

Callers first `prepare()` cache ops, then `execute()` them. `Object::request()` pins line-aligned ranges spanning reads and writes, revives lines from the LRU or creates empty lines, subtracts cached/known-zero regions from read requests, coalesces backend reads, and updates `do_not_read` for in-flight reads, writes, and append holes. `send_reads()` allows at most one backend read per object. When reads finish, `read_done()` marks waiting ops ready, inserts returned shard extent maps into line caches, and `cache_maybe_ready()` completes front-of-queue ops once their reads are cached. `write_done()` inserts generated write buffers into the cache and runs on-write callbacks.

Invalidating operations wait for in-flight reads to finish, clear active lines and LRU entries for the object, reset request state, mark the invalidation honored, and replay outstanding ops for that object so their reads are planned against the empty cache.

## State and Persistence Behavior

The cache is volatile only. State includes `objects`, per-object `requesting`, `do_not_read`, `reading_ops`, `requesting_ops`, weak line map, active IO counters, object sizes, `waiting_ops`, and LRU `map`/`lru`/`size`. Mempool counters track cache item and byte usage. `on_change()` cancels waiting callbacks and clears queued reads; `on_change2()` discards the LRU and asserts all active objects and IO have drained.

## Dependencies and Integration Points

It depends on `ECExtentCache.h`, `ECUtil`, `shard_extent_set_t`, `shard_extent_map_t`, `extent_set`, `extent_map`, mempool accounting, and the backend-supplied `BackendReadListener`. In practice `ECCommon::RMWPipeline` implements backend reads by calling `objects_read_and_reconstruct_for_rmw()`.

## Risks and Edge Cases

Invalidation is the highest-risk path: inserting a late read after clearing cache would corrupt later writes, so invalidating ops block until the object's current read completes. Line ownership relies on `shared_ptr`/`weak_ptr` lifetimes and `Line::~Line()` moving data to the LRU; active IO counters and op destructors must stay balanced. Appends use object-size masks to treat newly grown holes as zero, so projected size drift can cause under-reads. `LRU::free_maybe()` assumes `max_size < size` implies a non-empty list.

## Test Signals

Test cache miss then read completion, cache hit with no backend read, overlapping writes, sequential writes crossing 32 KiB/chunk line boundaries, append holes, invalidating op replay, late read completion around invalidation, LRU revive/evict/remove/discard, mempool accounting, `on_change()` callback cancellation, and `on_change2()` idle assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCache.h -->
# sources/distributed-fs/ceph/src/osd/ECExtentCache.h

## Purpose

Declares the modern EC extent cache API and data model. The cache improves small/overlapping EC partial writes by retaining recently read/written shard extents while preserving IO order and exposing a backend read callback interface.

## Important APIs, Types, and Functions

Public types are `ECExtentCache`, `ECExtentCache::LRU`, `ECExtentCache::Op`, `ECExtentCache::OpRef`, and `BackendReadListener`. Public methods include `prepare()`, `execute()`, `read_done()`, `write_done()`, `on_change()`, `on_change2()`, `contains_object()`, `get_projected_size()`, `idle()`, and `add_on_write()`. Internal types `Object` and `Line` model active per-object cache ownership and line-sized shard extent maps.

## Control Flow and Data Flow

The intended client protocol is documented in the header: prepare all cache ops for one parent operation, execute them, satisfy any backend reads through `BackendReadListener::backend_read()`, call `read_done()` when the backend returns shard extents, accept the cache-ready callback, generate/write EC data, then call `write_done()`. `Op` exposes requested writes, resulting cached read data, object id, and on-write callbacks. `LRU` stores cache lines by `(oid, offset)` and uses a mutex because it is shared at OSD-shard scope.

## State and Persistence Behavior

The header declares volatile cache state only. Active cache lines live under `objects`; recent inactive lines live in `LRU`; line sizes are accounted to the EC extent cache mempool. No on-disk metadata is produced by this class. The destructor calls `on_change()` and `on_change2()` to force cleanup in failed tests or abnormal lifetimes.

## Dependencies and Integration Points

It depends on `ECUtil.h`, `Context`, Ceph mempool, `hobject_t`, `extent_set`, and shard extent set/map helpers. It is embedded in `ECCommon::RMWPipeline` and requires the backend to provide reconstructed shard reads for cache misses.

## Risks and Edge Cases

The API permits reentrant cache-ready callbacks from `execute()`, so callers must build all cache op lists before execution and tolerate immediate completion. `Op::cancel()` deletes a released context; ownership is manual. `add_on_write()` immediately invokes callbacks if there is no waiting op, otherwise attaches to the latest op. `MIN_LINE_SIZE` and chunk-size-derived line sizing determine cache granularity and can affect memory pressure.

## Test Signals

API-level tests should verify immediate versus deferred completion, callback reentrancy, cancel behavior, on-write callback ordering, LRU max-size enforcement under mutex, projected size queries, object containment before/after op destruction, and destructor cleanup with outstanding/canceled ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCacheL.cc -->
# sources/distributed-fs/ceph/src/osd/ECExtentCacheL.cc

## Purpose

Implements the legacy intrusive extent cache used by `ECCommonL::RMWPipeline`. It tracks unstable extents for ordered overlapping partial overwrites, pins extents to write operations, returns cached RMW read data, and releases extents when the owning write completes.

## Important APIs, Types, and Functions

Important methods are `extent::_link_pin_state`, `_unlink_pin_state`, `unlink`, `link`, `move`, `remove_and_destroy_if_empty`, `get_or_create`, `get_if_exists`, `object_extent_set::get_containing_range`, `reserve_extents_for_rmw`, `get_remaining_extents_for_rmw`, `present_rmw_update`, and `print`. The implementation uses `object_extent_set::traverse_update()` from the header for splitting, replacing, and pin-updating interval fragments.

## Control Flow and Data Flow

`reserve_extents_for_rmw()` opens or finds the object extent set, walks each write range, pins all written extents to the current write pin, and returns the subset of requested reads that were missing from cache. `get_remaining_extents_for_rmw()` walks already pinned/present extents and builds an `extent_map` from cached buffer slices. `present_rmw_update()` fills or replaces buffer data for extents after transaction generation. Releasing a pin unlinks and destroys every extent owned by that pin, then deletes an empty per-object cache.

## State and Persistence Behavior

State is entirely in memory: `per_object_caches` owns `object_extent_set` nodes, each set owns intrusive `extent` nodes, and each extent also belongs to exactly one `pin_state` list. A present extent stores a `bufferlist`; a pending extent has no buffer. No data is written to disk by this class.

## Dependencies and Integration Points

It depends on `ECExtentCacheL.h`, Boost intrusive sets/lists, Ceph `bufferlist`, `extent_set`, and `extent_map`. `ECCommonL::RMWPipeline` is the primary caller: it opens write pins, reserves read/write extents, reads cache misses remotely, presents generated writes, and releases pins when commits finish or on interval change.

## Risks and Edge Cases

Intrusive ownership invariants are strict: every extent must be linked into one object set and one pin list, and unlink/move temporarily violates the two-link invariant only in controlled code. `traverse_update()` may split head/tail fragments around update ranges, so off-by-one or buffer length mismatches would corrupt cached data. `get_remaining_extents_for_rmw()` asserts extents are present and pinned by a write, so callers must pass exactly `to_read - remote_read`.

## Test Signals

Test reserving empty ranges, first-write misses, overlapping writes that move pin ownership, partial overlap split into head/middle/tail, cache hit reads after `present_rmw_update()`, release deleting empty object sets, print formatting, and assertion/sanitizer coverage for pin release on normal finish and `on_change()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECExtentCacheL.cc -->
