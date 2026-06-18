# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_notify.h

## Purpose
Declares RGW notification manager APIs and the reservation contract used by object operations to publish S3-compatible bucket notifications. It covers lifecycle of persistent topic queues, per-operation reservation/commit/abort, and queue statistics.

## Important APIs And Types
`init()` and `shutdown()` manage the process-global notification delivery manager. `add_persistent_topic()` and `remove_persistent_topic()` create/delete cls 2PC queues and maintain the shared queue list. `reservation_t` stores matched topics and request/object context. Its nested `topic_t` records notification configuration id, topic config, 2PC reservation id, event type, and shard id. `publish_reserve()`, `publish_commit()`, and `publish_abort()` form the 2-phase API. `rgw_topic_stats` reports queue reservation count, byte size, and entry count.

## Control Flow And State
Callers construct `reservation_t` either from `req_state` or from explicit non-request context, call `publish_reserve()` before the object operation is finalized, and then call `publish_commit()` after successful object mutation or let the destructor/explicit `publish_abort()` clean up. Persistent topics create queue reservations during reserve and commit encoded events later; non-persistent topics defer sending until commit.

## Dependencies And Integration Points
The interface depends on SAL RadosStore/Object/Bucket, `SiteConfig`, request state, `RGWObjTags`, cls 2PC reservation ids, notification event types, and pubsub topic definitions. It is integrated with object PUT/COPY/DELETE/lifecycle paths that need event publication.

## Risks And Test Signals
`reservation_t` stores raw pointers to request, store, object, bucket, and optional object name; these must outlive reserve/commit/abort. The destructor calls `publish_abort()`, so partially moved or long-lived reservations need clear ownership. Tests should verify API ordering, non-request constructor behavior, metadata/tag caching, persistent and non-persistent publication, and idempotent abort after successful commit.
