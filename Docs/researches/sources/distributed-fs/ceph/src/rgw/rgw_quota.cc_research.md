# sources/distributed-fs/ceph/src/rgw/rgw_quota.cc

## Purpose

Implements RGW bucket, user, and account quota enforcement using cached storage stats, asynchronous refresh, background owner-stat synchronization, and configurable quota limit application. It is the runtime enforcement layer behind `RGWQuotaHandler`.

## Important APIs, Types, and Functions

`RGWQuotaCache<T>` is the template base for TTL-cached stats with async refresh hooks. `RGWBucketStatsCache` fetches bucket stats by loading the bucket and reading current index shard stats. `RGWOwnerStatsCache` fetches owner stats via SAL, starts optional sync threads, tracks modified buckets, and synchronizes owner stats from bucket stats and metadata listings. `RGWQuotaInfoApplier`, `RGWQuotaInfoDefApplier`, and `RGWQuotaInfoRawApplier` decide whether limits compare against rounded or raw size. `RGWQuotaHandlerImpl` implements `check_quota()` and `update_stats()`. The file also implements default quota application and JSON/dump helpers for `RGWQuotaInfo`.

## Control Flow and Data Flow

Quota checks first return early when both user and bucket quota are disabled. Bucket quota checks fetch bucket stats through `bucket_stats_cache.get_stats()`, which serves fresh cached entries, starts async refresh after half TTL, or synchronously fetches from storage on miss/expiry. User/account quota checks use `owner_stats_cache.get_stats()` similarly. The applier then compares `stats.num_objects + requested_objects` and either raw or rounded size against configured max values and returns `-ERR_QUOTA_EXCEEDED` on violations.

Write paths call `update_stats()` after object changes. Both bucket and owner caches adjust cached stats in place and `RGWOwnerStatsCache::data_modified()` records the bucket for the bucket-sync thread. Background sync threads periodically process modified buckets and all owners/accounts, loading metadata keys and calling `sync_owner()` when owners are not idle or need a full sync.

## State and Persistence Behavior

The caches are in-memory LRU maps with expiration and async refresh timestamps. They do not make quota decisions from strong, freshly persisted state on every request unless cache entries are absent or expired. Persistent state is read and updated through SAL bucket stats, owner stats, metadata listing, `bucket->sync_owner_stats()`, `bucket->check_bucket_shards()`, and `rgw_sync_all_stats()`. The destructor waits for async refresh references and stops sync threads.

## Dependencies and Integration Points

Depends on SAL driver/bucket APIs, `lru_map`, Ceph clocks, threads, mutexes, `RefCountedWaitObject`, bucket layout helpers, RADOS-specific user helpers when available, and config values including quota cache size, TTL, sync intervals, default limits, and raw-size mode. Integrates with object mutation paths via `RGWQuotaHandler::update_stats()` and with account/user metadata via `meta_list_keys_*`.

## Risks and Edge Cases

Quota enforcement is eventually consistent because cached stats can be stale and async refresh failures are logged but not fatal. `fetch_stats_from_storage()` treats `-ENOENT` as zero stats after `get_stats()`, which may be correct for missing buckets/owners but should be tested. Owner sync thread stop takes locks while joining bucket sync. Default applier uses rounded object size while raw applier uses raw bytes; mismatched configuration can surprise operators. Full owner sync relies on metadata key parsing into `rgw_owner` and tenant lookup for account ids.

## Test Signals

Cover bucket and user quota enabled/disabled combinations, raw versus rounded size checks, max object boundaries, cache fresh/expired/async-refresh paths, async success/failure callbacks, indexless buckets, negative deltas clamped to zero, owner sync idle-user skipping, account tenant lookup, metadata listing errors, default quota config application, JSON backward compatibility for `max_size_kb`, and thread start/stop with pending async operations.
