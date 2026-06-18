# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.cc

## Purpose
This file implements RGW metadata sync for RADOS-backed multisite deployments. It fetches metadata log state from the master zone, initializes local sync status, builds full-sync maps, replays metadata changes locally, advances shard markers, coordinates leases and fairness bids, logs sync errors, and serializes sync status to RADOS.

## Important APIs, Types, and Functions
- Status object names include `mdlog.sync-status`, `mdlog.sync-status.shard.<id>`, `meta.full-sync.index.<id>`, and fairness bid object `meta-sync-bids`.
- `RGWSyncErrorLogger` writes sharded timelog entries under `sync.error-log.<shard>`.
- `RGWSyncBackoff` and `RGWBackoffControlCR` implement exponential retry around failing coroutines.
- `RGWRemoteMetaLog` owns the remote master REST connection, HTTP manager, error logger, sync trace node, and top-level sync coroutine.
- `RGWInitSyncStatusCoroutine` writes initial sync info, reads remote shard positions, writes per-shard markers, then moves to `StateBuildingFullSyncMaps`.
- `RGWFetchAllMetaCR` performs full metadata listing and writes sharded omap full-sync indexes.
- `RGWMetaSyncSingleEntryCR` fetches one remote metadata entry and stores or removes it locally.
- `RGWMetaSyncShardCR` performs full or incremental shard sync under a RADOS lease and fairness bid.
- `RGWMetaSyncCR` coordinates all shard controllers across period-history boundaries.
- `RGWCloneMetaLogCoroutine` copies remote mdlog entries into the local mdlog shard before replay.

## Control Flow
`RGWRemoteMetaLog::run_sync()` is the top-level non-master loop. It fetches remote mdlog info, reads local sync status, initializes status if absent or stale, verifies shard count, starts a RADOS-backed bid manager, then dispatches by sync state. `StateBuildingFullSyncMaps` lists remote metadata sections through `/admin/metadata`, prioritizes user, bucket.instance, bucket, roles, and topic, and writes full-sync indexes. `StateSync` finds the local period cursor, spawns one shard controller per shard, and advances to later periods when shard controllers finish.

Full sync reads keys from the full-sync omap index, spawns `RGWMetaSyncSingleEntryCR` workers, advances markers through `RGWMetaSyncShardMarkerTrack`, switches the marker to incremental state, and removes the full-sync index object. Incremental sync clones fresh remote mdlog entries into the local mdlog, reads local mdlog entries, replays completed operations, skips pending operations while advancing markers, and waits at the live tip based on `rgw_meta_sync_poll_interval`. Period markers stop replay at boundaries so the top-level coroutine can move to the next period.

## State and Persistence Behavior
Sync status is persisted in the zone log pool. The global info object stores state, shard count, period id, and realm epoch. Each shard marker stores state, marker, next-step marker, total entries, current full-sync position, timestamp, and realm epoch. Full-sync indexes are temporary sharded omap objects. Metadata writes use `meta.mgr->put(..., RGWMDLogSyncType::APPLY_ALWAYS, true)` and removals use `meta.mgr->remove()`. Remote mdlog entries are cloned into local mdlog shards. RADOS cls locks protect status and shard marker objects. Fairness bids in the control pool prevent multiple workers from owning the same shard. Error details are persisted as cls timelog records.

## Dependencies and Integration Points
The implementation depends on `RGWRESTConn` and `/admin/log` plus `/admin/metadata` endpoints, `RGWHTTPManager`, coroutine infrastructure, async RADOS processor, metadata manager, mdlog service, cls service, sync trace manager, period history, RADOS lock/omap helpers, and `sync_fairness` bid manager.

## Risks
- The state machine spans REST, local mdlog, metadata writes, RADOS locks, and fairness bids; partial failures rely on marker discipline for retry correctness.
- `RGWMetaSyncCR` asserts that `next` exists after shard completion, so current-period behavior depends on shard controllers not returning terminal success at the live tip.
- Marker advancement is conservative; child failures cause duplicate replay but avoid skipping failed entries.
- Full-sync section ordering is hard-coded for metadata dependencies.
- REST retry behavior mainly special-cases endpoint internal errors; other transient failures depend on outer backoff.

## Test Signals
Strong signals include multisite metadata full sync tests, incremental mdlog replay tests, period transition tests, marker persistence/restart tests, lease-loss and competing-bid tests, remote REST failure retry tests, metadata deletion tests, pending mdlog operation handling, sync error log tests, and upgrade tests where local status lags the master's oldest mdlog period.
