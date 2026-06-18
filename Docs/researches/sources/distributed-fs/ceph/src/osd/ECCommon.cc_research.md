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
