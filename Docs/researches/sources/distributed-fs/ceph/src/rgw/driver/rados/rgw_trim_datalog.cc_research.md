# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc` implements data-log trimming for RGW multisite. It queries peer zones for data-sync progress, computes the minimum stable marker per datalog shard, and trims local datalog entries that all peers have consumed.

## Important APIs, Types, and Functions

`DatalogTrimImplCR` sends the actual `datalog_rados->trim_entries()` request for one shard and marker. `get_stable_marker()` chooses `next_step_marker` during full sync and `marker` otherwise. `take_min_markers()` folds peer statuses into per-shard minimum markers. `DataLogTrimCR` queries all peers and spawns shard trims. `DataLogTrimPollCR` periodically takes a RADOS lock and runs trim. `create_data_log_trim_cr()` and `create_admin_data_log_trim_cr()` are the exported factories.

## Control Flow

The periodic coroutine sleeps for the configured interval, locks the first datalog shard object with lock name `data_trim`, and runs `DataLogTrimCR`; it intentionally does not unlock after success so other gateways avoid duplicate work for the lease interval. `DataLogTrimCR` sends `/admin/log/?type=data&status&source-zone=<zone>` requests to all notify targets, requires all responses to succeed, computes minimum stable markers, and spawns `DatalogTrimImplCR` only for shards whose marker advanced beyond `last_trim`.

## State and Persistence Behavior

Trimmed datalog entries are removed from RADOS by `trim_entries()`. The periodic coroutine keeps in-memory `last_trim` markers per shard to avoid repeated trims. There is no separate persisted trim cursor in this file; safety comes from peer sync markers and the RADOS lock.

## Dependencies and Integration Points

The code depends on RGW coroutine infrastructure, REST admin log status endpoints, `RGWHTTPManager`, zone service notify maps, datalog RADOS service, RADOS lock coroutine helpers, and multisite data sync marker types.

## Risks and Edge Cases

All peer status requests must succeed before trimming; one unavailable peer blocks progress. The code assumes peer marker vectors match `num_shards`; malformed or unexpected status can lead to incorrect marker folding if not caught elsewhere. `-ENODATA` from trim is treated as no data and can update `last_trim_marker` except for max marker. The lock is held for the interval by design.

## Test Signals

Tests should cover stable marker selection for full/incremental sync, minimum marker folding across peers, skipping already-trimmed shards, peer REST failure behavior, `-ENODATA` handling, lock contention in poll mode, and factory behavior for periodic versus admin trim.
