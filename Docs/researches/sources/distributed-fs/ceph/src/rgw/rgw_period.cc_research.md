# sources/distributed-fs/ceph/src/rgw/rgw_period.cc

## Purpose
`rgw_period.cc` implements selected `RGWPeriod` behavior for multisite realm periods: zonegroup lookup, sync-status capture, pool selection, JSON serialization, and test instances.

## Important APIs, Types, And Functions
Important functions are `RGWPeriod::get_zonegroup()`, `RGWPeriod::update_sync_status()`, `RGWPeriod::find_zone()`, `RGWPeriod::get_pool()`, `dump()`, and `decode_json()`. Internal `read_sync_status()` uses `RGWMetaSyncStatusManager` under `WITH_RADOSGW_RADOS`.

## Control Flow
`update_sync_status()` reads current metadata sync status, compares the current period realm epoch with sync status, and either rejects stale promotion unless forced, records empty shard markers for skipped periods, or copies shard markers for the current epoch. `get_zonegroup()` selects a requested id or `default`. `find_zone()` delegates to period-map lookup.

## State And Persistence
`update_sync_status()` mutates the period's `sync_status` vector. `get_pool()` chooses the period root pool from config or the default. Serialization persists period fields such as id, epoch, predecessor, sync status, period map, master zonegroup/zone, config, realm id, and realm epoch.

## Dependencies And Integration Points
This file integrates with SAL drivers, RADOS sync status manager, `rgw_meta_sync_status`, `rgw_zone`, and config-store consumers that read/write periods. Period pusher/puller/history code uses the period identity, predecessor, epoch, and JSON encoding.

## Risks And Test Signals
Risks include promoting a stale zone and losing metadata updates, marker count mismatches, build behavior without RADOS support returning `-ENOTSUP`, and JSON compatibility. Tests should cover stale and forced promotion, current-epoch marker filtering, missing/default zonegroup lookup, configured/default period root pools, and JSON round trips.
