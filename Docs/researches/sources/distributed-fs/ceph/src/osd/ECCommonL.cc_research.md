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
