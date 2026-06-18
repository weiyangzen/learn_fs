# sources/distributed-fs/ceph/src/rgw/rgw_pubsub.h

## Purpose

Defines RGW pubsub and S3 notification data models plus the `RGWPubSub` facade used to manage account topics, bucket notification bindings, and persistent notification event records. The header is the serialization contract for topic destinations, topic metadata, bucket-topic filters, S3-compatible notification XML, and queued event entries.

## Important APIs, Types, and Functions

`rgw_pubsub_s3_notification` models one S3 `TopicConfiguration`, with id, event list, topic ARN, and key/metadata/tag filters. The overloaded `match()` declarations cover key filters, metadata filters, tag filters, and event-type matching. `rgw_pubsub_s3_event` is the JSON/encoded event record with AWS-style fields plus RGW extensions for event id, bucket id, metadata, tags, and opaque data.

`rgw_pubsub_dest` describes delivery endpoint state: endpoint URL and args, ARN, secret-storage flag, persistence flag, queue object name, TTL/retry configuration, and shard count. `rgw_pubsub_topic`, `rgw_pubsub_topic_filter`, `rgw_pubsub_bucket_topics`, and `rgw_pubsub_topics` are the persisted topic and binding structures. `RGWPubSub` exposes topic create/read/list/delete and nested `RGWPubSub::Bucket` exposes bucket notification create/remove/list helpers. Free helpers include `topic_to_unique()`, `find_unique_topic()`, `remove_notification_v2()`, `get_bucket_notifications()`, and topic metadata key formatting/parsing.

## Control Flow and Data Flow

The data path starts with XML notification config decoding into `rgw_pubsub_s3_notification` objects. These become topic filters that are persisted as bucket-topic maps, keyed by topic name or a unique topic/notification composition. Event generation fills `rgw_pubsub_s3_event`, applies filter matching against event type, object key, metadata, and tags, then delivery code can encode queued `rgw::notify::event_entry_t` records for persistent delivery.

`RGWPubSub` chooses v1 or v2 topic management based on site configuration. V1 methods read/write aggregate topic maps, while v2 methods manipulate individual topic metadata and account topic listings. Bucket notification operations read a bucket's topic map with an object version tracker, update or remove entries, and write it back atomically.

## State and Persistence Behavior

All main structs use Ceph `ENCODE_START` versioning. Backward compatibility is explicit: `rgw_pubsub_dest` carries dummy legacy fields, pre-v7 persistent topics derive queue names from `arn_topic`, pre-v8 destinations default to one shard, `rgw_pubsub_topic` decodes legacy owner variants, `rgw_pubsub_topic_filter` stores events as strings, and `rgw_pubsub_topics` converts old `topic_subs` maps. Persistent event entries store delivery timing and retry configuration alongside the event.

Durable state lives in RGW metadata and bucket attributes through SAL driver calls implemented elsewhere. The header's key risk is that these encoded forms are on-disk and cross-version wire contracts, so field ordering and version gates are compatibility-sensitive.

## Dependencies and Integration Points

Depends on SAL forward declarations, zone/site configuration, `rgw_notify_event_type.h`, `rgw_s3_filter.h`, Ceph formatter/encoding utilities, `versioned_variant`, and C++ ranges for shard-name views. Integrates with S3 REST notification APIs, notification delivery queues, bucket metadata, topic metadata, and multisite/account topic listing.

## Risks and Edge Cases

Filter semantics must match S3 expectations for prefix/suffix/regex, metadata, and tags. `DEFAULT_GLOBAL_VALUE` uses `UINT32_MAX` as a sentinel, so dumping and application code must not confuse it with a real high value. Sharded persistent queues depend on stable naming. Notification id/topic uniqueness is split between `topic_to_unique()` and `find_unique_topic()`, which makes migration from older unqualified topic names a compatibility risk.

## Test Signals

Cover XML decode/dump round trips, event matching for key/metadata/tag/event filters, v1-to-v2 topic decode compatibility, persistent destination decode from versions before queue names and shards, topic metadata key parsing with tenants, removal by notification id versus topic name, bucket notification atomic update races, and event-entry encode/decode across all struct versions.
