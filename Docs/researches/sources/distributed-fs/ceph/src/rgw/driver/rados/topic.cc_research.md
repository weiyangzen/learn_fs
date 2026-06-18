# sources/distributed-fs/ceph/src/rgw/driver/rados/topic.cc

## Purpose
Implements v2 pubsub topic metadata storage in RADOS, including read/write/remove, bucket links per topic, account topic indexes, persistent notification queue setup/removal, cache integration, and metadata sync handling.

## Important APIs, types, and functions
- `read()` loads a topic by metadata key from `topic.{key}` in `zone.topics_pool`, using `RGWChainedCacheImpl<cache_entry>` when possible.
- `write()` stores encoded `rgw_pubsub_topic`, links account-owned topics through `rgwrados::topics::add()`, and records mdlog completion.
- `remove()` deletes topic info, deletes the related `buckets.{key}` omap object, unlinks account topics, and records mdlog.
- `link_bucket()`, `unlink_bucket()`, and `list_buckets()` maintain an omap set of bucket keys associated with a topic.
- `MetadataHandler` implements metadata sync type `topic`, including persistent queue creation/deletion for persistent push topics.

## Control flow
Read first checks chained cache; on miss it reads the system object, decodes, stores cache entry with cache invalidation metadata, and returns optional mtime/version data. Write encodes the topic, writes the main object, optionally adds account index, then completes mdlog. Metadata `put()` calls write and then ensures persistent queues exist when required. Metadata `remove()` reads the topic to discover destination properties, removes topic metadata, and then best-effort removes persistent queues.

## State and persistence behavior
Topic info is stored in `zone.topics_pool` under `topic.{metadata_key}`. Bucket associations are stored as omap keys in `buckets.{metadata_key}`. Account topic indexes use `account::get_topics_obj()` with `rgwrados::topics`. Persistent queues are stored in `zone.notif_pool` through `rgw::notify`. Read caching uses `RGWChainedCacheImpl<cache_entry>` and `RGWSI_SysObj_Cache`.

## Dependencies and integration points
Depends on RGW pubsub structures, account helpers, notification queue helpers, metadata services, system object cache, RADOS refs, mdlog, zone params, and `topics.cc` account-topic helpers. It integrates with bucket notification APIs and multisite metadata replication.

## Risks and edge cases
Account link/unlink failures are logged and non-fatal, risking stale or missing account topic lists. Deleting the buckets object is also non-fatal. Persistent queue cleanup failures other than `-ENOENT` are logged but not fatal during metadata remove. Cache returns move object/version data out of the cache entry copy; cache semantics must ensure this is safe. `mutate()` is unsupported.

## Test signals
Tests should cover cached and uncached reads, exclusive write conflicts, account-owned topic link/unlink, bucket link/unlink/list pagination, missing buckets object listing, persistent queue create/remove during metadata sync, mdlog completion, and corrupt topic decode.
