# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc` implements bucket-index-log trimming for RGW multisite. It chooses hot and cold bucket instances to trim, queries peer zones for their bucket sync progress, trims safe bilog markers, removes obsolete bucket index generations, persists the cold-list cursor, and coordinates multiple gateways through RADOS locks and watch/notify.

## Important APIs, Types, and Functions

The watch/notify protocol is built from `TrimNotifyType`, `TrimCounters`, `TrimComplete`, `TrimNotifyHandler`, and `BucketTrimWatcher`. `BucketTrimShardCollectCR` trims bilog shards concurrently. `BucketCleanIndexCollectCR` removes old bucket index generation objects. `RGWReadRemoteStatusShardsCR` reads peer bucket-index sync status. `BucketTrimInstanceCR` is the main per-bucket trim state machine. `take_min_status()` correlates peer markers. `AsyncMetadataList` and `MetadataListCR` list bucket instance metadata with wraparound from a saved marker. `BucketTrimCR` selects buckets and runs trims for one interval. `BucketTrimPollCR` runs periodic locked trims. `RecentEventList` tracks recently trimmed buckets. `BucketTrimManager::Impl` implements counter sharing and observer behavior. `configure_bucket_trim()` reads config, and `bilog_trim()` exposes direct shard trimming.

## Control Flow

Gateways call `BucketTrimManager::on_bucket_changed()` as data sync sees bucket changes, incrementing a bounded counter unless the bucket was recently trimmed. The manager starts a `BucketTrimWatcher` on the `bilog.trim` object in the log pool. Periodic trim sleeps for the configured interval, takes a RADOS lock on that object, then runs `BucketTrimCR`.

`BucketTrimCR` notifies peer gateways for their hot-bucket counters, merges responses, selects top hot buckets, then fills remaining capacity by listing bucket.instance metadata from the saved `BucketTrimStatus` marker while skipping recently trimmed or already selected buckets. It trims selected buckets concurrently. Afterward it writes the new cold marker and sends a trim-complete notify so peers reset counters.

`BucketTrimInstanceCR` fetches the bucket sync policy and current bucket info, queries relevant destination zones for merged bucket-index status, finds the minimum generation peers still need, optionally removes an obsolete generation and updates/removes bucket instance metadata with retries, or computes per-shard minimum markers and trims the current generation's bilogs.

## State and Persistence Behavior

Persistent state includes `BucketTrimStatus` stored at `bilog.trim` in the zone log pool, bucket index log objects, bucket instance metadata layout generations, and destination peer sync progress queried over REST. In-memory state includes bounded hot-bucket counters, a recent-trim circular buffer, notify replies, selected bucket lists, retry counters, and per-trim last markers. Watch/notify replies are transient but coordinate all gateways in the same zone.

## Dependencies and Integration Points

This file integrates with RGW coroutine collectors, RADOS lock/notify/watch helpers, bucket sync policy handlers, bucket instance metadata, bilog RADOS service, zone service connection maps, REST admin log endpoints, metadata manager listing, and `BoundedKeyCounter`. It uses `no_change_attrs()` from `rgw_tools` when updating bucket info without changing attributes.

## Risks and Edge Cases

All peer statuses must be fetched before trimming, so missing zone connections or REST failures stop a bucket trim. Generation cleanup modifies bucket info and can race, handled with retries but still high risk. The code refuses to remove the only live non-deleted log generation. Old peers without v2 status fall back to generation 0, which can limit trimming. Notify decode errors or timeouts reduce hot-bucket selection. The periodic lock is intentionally held for the interval unless errors unlock, so lock duration and lease behavior matter.

## Test Signals

Key tests include notify encode/decode and counter aggregation, watcher restart on disconnect, bucket selection from hot counters plus cold metadata listing, persistent marker wraparound, peer status parsing v1/v2, min generation and min marker selection, old generation cleanup and bucket-info retry races, deleted bucket cleanup, shard-count mismatch errors, recent-trim filtering, and direct `bilog_trim()` generation lookup.
