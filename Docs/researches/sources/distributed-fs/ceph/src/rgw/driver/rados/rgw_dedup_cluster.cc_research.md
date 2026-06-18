# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_cluster.cc

## Purpose
`rgw_dedup_cluster.cc` implements the dedup cluster control plane. It owns epoch creation and compare-and-swap updates, work and MD5 shard token objects, shard progress xattrs, statistics aggregation, RADOS watch/notify control messages, and restart-scan orchestration.

## Important APIs, Types, And Functions
The file defines `DEDUP_EPOCH_TOKEN` and `DEDUP_WATCH_OBJ` control-pool objects. `get_control_ioctx()` opens the zone control pool. `get_epoch()`, `set_epoch()`, and `swap_epoch()` read and update the `RGW_DEDUP_ATTR_EPOCH` xattr on `DEDUP_EPOCH_TOKEN`.

`shard_progress_t` is the persisted progress xattr payload for each shard token. It records progress counters, completion state, creation, update and completion times, an owner cluster id, and encoded stats. It is encoded in `SHARD_PROGRESS_ATTR`.

`cluster::reset()` reads or initializes the epoch, waits for shard counts, cleans old token objects, creates current run tokens, and verifies that all expected token objects exist. `get_next_shard_token()` locks a shard token with `cls_lock`, writes initial progress, and returns the shard id. Completion and heartbeat updates are persisted through `mark_shard_token_completed()` and `update_shard_token_heartbeat()`.

`cluster::collect_all_shard_stats()` is the admin-facing stats path. It reads worker and MD5 shard progress xattrs, decodes `worker_stats_t` and `md5_stats_t`, aggregates timing per owner, prints incomplete shards, and reports estimate and actual dedup ratios.

`watch_reload()`, `unwatch_reload()`, `ack_notify()`, `dedup_control_bl()`, `dedup_control()`, and `dedup_restart_scan()` implement the watch/notify command channel used by `radosgw-admin` and the background service.

## Control Flow
Startup calls `reset()`. It reads the current epoch; if shard counts are already set, the member accepts them. If counts are missing and the caller has counts, it attempts `swap_epoch()` until counts are visible. Old token objects whose mtimes predate the epoch are deleted. New work and MD5 token objects are created with prefixes `WRK.SHRD.TK.` and `MD5.SHRD.TK.`.

Workers call `get_next_work_shard_token()` and MD5 processors call `get_next_md5_shard_token()`. Each function scans forward from the current local cursor and attempts an exclusive lock on the token object. On success it writes a fresh `shard_progress_t`; on busy or missing tokens it skips to the next candidate.

Barrier checks call `all_shard_tokens_completed()`. They read every token's `SHARD_PROGRESS_ATTR`, decode progress, mark completed local cache slots, return `-EAGAIN` for active or not-started shards, and return `-ETIME` for shards whose heartbeat exceeds `EPOCH_MAX_LOCK_DURATION_SEC`.

Restart-scan flow first gets or creates an epoch, sends `URGENT_MSG_ABORT` to running watchers, compare-and-swaps a new epoch with zero shard counts, then notifies `URGENT_MSG_RESTART` with an optional encoded `dedup_filter_t`.

## State And Persistence Behavior
The control pool stores one epoch object, one watch object, and one object per work or MD5 shard token. The epoch is persisted as the `rgw.dedup.attr.epoch` xattr. Token progress is persisted as `shard_progress` xattr. Lock ownership uses RADOS cls lock with a generated cookie and the hard-coded lock name `dedup_shard_token`.

Shard token object names are compact hex suffixed strings, for example `WRK.SHRD.TK.000`. Cleanup only removes legal token names and skips objects newer than the epoch time, reducing risk of deleting tokens from a newer run.

## Dependencies And Integration Points
This file depends on zone control-pool configuration, SAL RADOS store access, `rgw_rados_operate()`, `rgw_rados_notify()`, cls lock, cls xattr compare operations, Ceph formatters, and stats types from `rgw_dedup_utils.h`. It is the bridge between `radosgw-admin` dedup commands and the background worker in `rgw_dedup.h`.

## Risks And Edge Cases
Epoch `set_epoch()` accepts existing epoch xattrs when the compare against an empty xattr fails, so stale epoch handling depends on later restart logic. `all_shard_tokens_completed()` treats missing, undecodable, or xattr-less tokens as corruption and returns `-ENODATA`; callers must distinguish transient incompleteness from real failure. Heartbeat timeout only records timeout state in memory and does not break locks in this implementation path.

`dedup_control_bl()` returns the first nonzero ack status; in multi-RGW deployments one bad ack can fail the command even if other members succeeded. Notify timeout returns `-EAGAIN`.

## Test Signals
Tests should cover epoch compare-and-swap races, cleanup skipping new token objects, token lock contention, xattr decode failures, heartbeat timeout reporting, stats aggregation with missing shards, restart with and without filters, throttle notify decoding, and no-watcher notify timeout behavior.
