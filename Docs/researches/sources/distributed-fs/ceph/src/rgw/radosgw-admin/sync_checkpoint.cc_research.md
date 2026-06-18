# sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.cc

## Purpose
Implements the `radosgw-admin` bucket sync checkpoint operation. It waits until local bucket sync has caught up with one or more remote source bucket pipes by comparing full-sync state, incremental generation, and per-shard bilog markers.

## Important APIs, Types, and Functions
- `rgw_bucket_sync_checkpoint(...)` is the exported entry point used by admin command handling. It accepts the RADOS store, bucket sync policy, destination bucket info, optional source zone/bucket filters, retry delay, and absolute timeout.
- `bucket_source_sync_checkpoint(...)` handles one source pipe: it polls full sync status, waits for incremental mode, waits for `latest_gen`, then checks per-shard incremental markers.
- `source_bilog_info(...)` resolves the zone connection for the source zone and calls `rgw_read_remote_bilog_info()`.
- Helpers format and compare `BucketIndexShardsManager` values against `std::vector<rgw_bucket_shard_sync_info>`.

## Control Flow
The entry point scans `policy.get_all_sources()`, applies optional source filters, and builds a list of source entries. For each accepted source it spawns two Boost.Asio coroutines on a local `io_context`: one fetches remote bilog marker info and `latest_gen`, the other reads source bucket instance info. After `ioctx.run()`, it checkpoints each source sequentially. The per-source wait loop first tolerates missing full-sync status (`-ENOENT`) while sync is starting, then waits for `BucketSyncState::Incremental`, then for `full_status.incremental_gen >= latest_gen`, then for all local incremental shard markers to reach or pass remote markers.

## State and Persistence
The file does not write durable state directly. It reads durable sync status objects through `rgw_read_bucket_full_sync_status()` and `rgw_read_bucket_inc_sync_status()`, and reads remote bilog state through zone services. The output is process-local progress logging plus admin stdout/stderr. Timeout and retry state are held in local variables.

## Dependencies and Integration Points
It depends on RGW RADOS SAL (`rgw::sal::RadosStore`), bucket sync policy and status helpers, zone connection maps, cls RGW bilog APIs, and Boost.Asio stackful coroutines. It integrates with `radosgw-admin` via `sync_checkpoint.h`.

## Risks and Edge Cases
The marker comparison is lexicographic and shard-order dependent, so malformed or mismatched shard marker sets can give misleading progress. Source fetches throw `std::system_error` from coroutines and are collapsed into negative errno returns. A bucket whose remote markers are all empty is considered caught up without reading incremental status. The function can block until timeout and sleeps on the calling thread during polling.

## Test Signals
Useful tests include mocked full-sync status transitions from missing to incremental, generation lag and catch-up, empty-source marker handling, source zone/bucket filtering, per-shard marker ordering, timeout behavior, and failures from remote bilog or source bucket info reads.
