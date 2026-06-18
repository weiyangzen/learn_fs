# sources/distributed-fs/ceph/src/rgw/rgw_pubsub.cc

## Purpose
`rgw_pubsub.cc` implements RGW bucket notification and pubsub topic metadata behavior, including S3 notification XML parsing/dumping, topic/destination JSON/XML formatting, v1/v2 topic storage, bucket notification attr updates, account topic listing, persistent-topic shard cleanup, and notification removal.

## Important APIs, Types, And Functions
Utility functions format and parse topic metadata keys (`tenant:topic[.shard]`), generate event ids, match event lists, and decode XML event lists. `rgw_pubsub_s3_notification(s)` handles S3 `NotificationConfiguration`. `rgw_pubsub_s3_event`, `rgw::notify::event_entry_t`, `rgw_pubsub_topic`, `rgw_pubsub_topic_filter`, `rgw_pubsub_bucket_topics`, `rgw_pubsub_topics`, and `rgw_pubsub_dest` dump or decode notification structures. `RGWPubSub` implements topic listing, topic get/create/remove, and nested `Bucket` notification operations. Helper functions manage bucket notification attrs and topic-bucket mappings.

## Control Flow
The constructor determines whether notification v2 is supported by all zonegroups. Topic reads use v2 metadata when enabled and v1 migration state is absent; otherwise they read tenant topic aggregates. Bucket writes in v2 refuse service while v1 topic migration is present or indeterminate. Creating a bucket notification reads the topic, reads existing bucket topics with an object-version tracker, inserts/updates a filter, and writes back. V2 notification deletion edits `RGW_ATTR_BUCKET_NOTIFICATION` and updates mapping metadata. Topic deletion removes persistent queue shards before deleting topic metadata.

## State And Persistence
Persistent state includes topic metadata objects, v1 tenant topic aggregates, bucket topic objects, `RGW_ATTR_BUCKET_NOTIFICATION` attrs, bucket-topic mapping omaps, and persistent topic queues/shards. Version trackers protect some writes. The code tolerates absent metadata as no-op in several delete/read paths.

## Dependencies And Integration Points
It depends on SAL driver topic APIs, bucket attr APIs, `rgw_notify`, zone feature detection, account id validation, ARN/topic structs, XML/JSON formatters, notification event type conversion, and common errno handling. Operation classes declared elsewhere call these APIs for S3-compatible topic and bucket notification endpoints.

## Risks And Test Signals
Risks include v1/v2 migration gating, partial failure between bucket attr writes and mapping updates, shard-name parsing/removal, tenant/account key filtering, missing topic treatment, object-version race handling, event/filter XML compatibility, and cleanup of persistent queues. Tests should cover v1 and v2 topic create/list/get/delete, migration-in-progress service-unavailable behavior, account topic listing, bucket notification create/remove by topic and id, delete-all behavior, attr decode failures, persistent topic shard cleanup, event XML defaults, and topic metadata key parsing with tenants and shard suffixes.
