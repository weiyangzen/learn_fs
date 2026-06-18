# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_mdlog.h

## Purpose
Declares the metadata log service used by RGW multisite metadata replication and admin inspection. It stores metadata mutation entries into sharded cls timelog objects, lists and trims those logs, exposes shard information and locks, and tracks locally modified shards.

## Important APIs And Types
`META_LOG_OBJ_PREFIX` is the base object prefix. `RGWMetadataLogInfo` reports a shard marker and last update time. `RGWMetadataLogInfoCompletion` wraps asynchronous info retrieval with reference-counted lifetime and cancellation-protected callbacks. `RGWMetadataLog` exposes `add_entry()`, `store_entries_in_shard()`, `list_entries()`, `trim()`, synchronous/asynchronous `get_info()`, shard locking/unlocking, `update_shards()`, and modified-shard tracking through `read_clear_modified()`.

`LogListCtx` carries current shard, marker, time range, oid, and completion flag for iterative listing. `RGWMetadataLogData` encodes versioned mdlog status used in synchronization. `RGWMetadataLogHistory` records the oldest realm epoch and period id retained in metadata log history at object id `meta.history`.

## Control Flow And State
The constructor derives an object prefix from the period id, using `meta.log.` for current/default period and `meta.log.<period>.` for period-specific logs. `add_entry()` hashes a key to a shard, marks that shard modified, and adds a timelog entry. Listing initializes a handle for one shard and time interval, then repeated `list_entries()` calls advance the marker.

Persistent state lives in sharded timelog objects in the zone log pool plus the encoded mdlog data/history objects. Runtime state includes service pointers for zone and cls, the prefix, an RW lock, and a set of modified shard ids. The modified set is not durable; it is a local signal for update propagation.

## Dependencies And Integration Points
Depends on `RGWSI_Zone`, `RGWSI_Cls`, cls log types, cls version types, `RGWMDLogStatus`, and metadata manager interfaces. It integrates with metadata handlers that call mdlog completion after put/remove/mutate, and with multisite sync logic that lists, locks, and trims shards.

## Risks And Test Signals
Correctness depends on stable shard hashing and consistent `rgw_md_log_max_shards`. Async completion cancellation protects the callback but still requires caller reference discipline. Locking is per-shard and uses zone id/owner id strings supplied by the caller. Tests should validate shard oid generation by period, add/list/trim behavior, async info cancellation, lock/unlock failure propagation, and encoding compatibility for `RGWMetadataLogData` and `RGWMetadataLogHistory`.
