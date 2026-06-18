# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.cc

## Purpose
Implements RGW bucket notification reservation, commit/abort, persistent queue management, and background delivery. It supports immediate push endpoints and persistent 2-phase-commit queues, including sharded topic queues, retry/TTL handling, stale reservation cleanup, and migration of entries created before creation-time metadata was present.

## Important APIs, Types, And Functions
Public functions in `rgw::notify` include `init()`, `shutdown()`, `add_persistent_topic()`, `remove_persistent_topic()`, `publish_reserve()`, `publish_commit()`, `publish_abort()`, and `get_persistent_queue_stats()`. `reservation_t` is the caller-facing reservation object; it records applicable topics and aborts uncommitted reservations in its destructor. `rgw_topic_stats` reports reservations, bytes, and entries.

The internal `Manager` owns an Asio `io_context`, worker thread, queue ownership locks, queue retry trackers, and a `SiteConfig`/RadosStore reference. It reads the global queue list object `queues_list_object`, takes exclusive cls locks on queue objects, processes queue entries through `RGWPubSubEndpoint`, removes successful/expired entries, and periodically expires stale 2PC reservations.

## Control Flow
`publish_reserve()` loads bucket notification configuration from v2 notification metadata when all zonegroups support it and v1 topics are absent, otherwise through `RGWPubSub`. For each event type it checks event name, key filter, metadata filter, and tag filter. Persistent topics reserve space on a selected queue shard computed from bucket/object hash; non-persistent topics only record intent in `reservation_t`.

`publish_commit()` builds an S3 event, populates identity, bucket/object fields, tags, metadata, sequence id, and opaque data. Persistent commits encode an `event_entry_t`, enlarge the queue reservation if the encoded size exceeds the initial 4 KiB reservation, then commit asynchronously to the queue shard. Non-persistent commits instantiate the endpoint and send immediately. `publish_abort()` aborts any uncommitted persistent reservation and clears its id.

The background manager refreshes the queue list every 30 seconds, locks queues with a 90-second failover duration, and spawns one processing coroutine per owned queue. Queue processing lists up to 1024 entries under the queue lock, fetches current topic info or falls back to cached entry fields, builds an endpoint, and spawns per-entry processing. Successful, expired, or migration-needed entries are removed up to an adjusted marker. Migration entries are re-reserved/recommitted after stamping current creation time and topic retry settings.

## State And Persistence
Persistent state is stored in the notification pool. `queues_list_object` stores queue names as omap keys. Each topic queue is a cls 2PC queue initialized with `MAX_QUEUE_SIZE` and optionally sharded as `<queue>.<shard_id>`. Queue objects carry cls lock state, committed entries, and reservations. Runtime state includes the global `s_manager`, per-entry retry counters and last retry time in `topics_persistency_tracker`, and per-topic perf counters.

## Dependencies And Integration Points
Depends on cls 2PC queue and cls lock clients, `RGWPubSub` topic/notification metadata, `RGWPubSubEndpoint` implementations from `rgw_pubsub_push.cc`, SAL RadosStore/Bucket/Object, zone feature detection, request state metadata/tags, notification event type matching, perf counters, and librados async completions. Lifecycle and other non-request callers use the alternate `reservation_t` constructor.

## Risks And Edge Cases
Persistent commit is asynchronous; failures after `aio_operate()` are only logged by the completion callback and are not returned to the original caller. The reservation destructor is a leak guard, but callers must keep `reservation_t` alive until commit/abort semantics are complete. Entry processing updates shared flags from spawned coroutines, so ordering depends on the single queue coroutine and token wait discipline. Topic fallback to cached endpoint fields preserves delivery if topic metadata is temporarily unavailable but may use stale policy. Queue migration has a TODO around tenant extraction and aborts if topic lookup by queue name fails. Queue ownership loss returns from processing and relies on failover locks for another RGW to take over.

## Test Signals
Tests should cover notification filter matching for events, key prefixes/suffixes, metadata and tags; v1/v2 config selection; persistent reservation and larger-than-reserved commit; destructor abort; queue sharding determinism; queue add/remove list-object consistency; retry TTL/max retry expiration; endpoint `-EBUSY` backoff behavior; stale reservation cleanup under lock; lock failover between two managers; and persistent queue stats across shards.
