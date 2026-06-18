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
