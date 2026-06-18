# sources/distributed-fs/ceph/src/rgw/rgw_rest_pubsub.cc

## Purpose

`rgw_rest_pubsub.cc` implements RGW REST operations for two related APIs: SNS-compatible topic management and S3-compatible bucket notification configuration. It bridges HTTP request parsing, IAM authorization, topic policy checks, persistent notification queue lifecycle, and bucket metadata updates into the `RGWPubSub` and SAL driver layers. The file also contains helper validation for topic names, topic ARNs, endpoint secrets, topic policies, and owner/account handling.

## Important APIs, types, and functions

- `verify_transport_security()` and `validate_and_update_endpoint_secret()` protect topic endpoint credentials. They detect credentials embedded in endpoint URLs or topic attributes such as `user-name`, `password`, and `ssl-key-password`, set `rgw_pubsub_dest::stored_secret`, and reject insecure transport unless `rgw_allow_notification_secrets_in_cleartext` permits it.
- `validate_topic_name()` enforces the default SNS-like topic name character and length contract unless relaxed topic names are configured. `validate_topic_arn()` parses and validates `TopicArn`.
- `get_account_or_tenant()` normalizes an `rgw_owner` variant to the account id or tenant string used as the topic namespace.
- `verify_topic_permission()` is the central resource/identity policy evaluator. It handles account-root behavior, same-owner access, cross-account access requiring both identity and resource policy allows, legacy non-account owner fallback, and the compatibility setting for publish without a policy.
- `should_forward_request_to_master()` gates metadata-master forwarding when the local zone is not metadata master and all zonegroups support `notification_v2`.
- SNS-style `RGWOp` classes: `RGWPSCreateTopicOp`, `RGWPSListTopicsOp`, `RGWPSGetTopicOp`, `RGWPSGetTopicAttributesOp`, `RGWPSSetTopicAttributesOp`, and `RGWPSDeleteTopicOp`.
- S3 notification classes: `RGWPSCreateNotifOp`, `RGWPSDeleteNotifOp`, and `RGWPSListNotifsOp`.
- `op_generators` maps AWS `Action` values to operation constructors for `RGWHandler_REST_PSTopic_AWS::op_post()`.
- `remove_notification_by_topic()` and `delete_all_notifications()` coordinate legacy notification and auto-generated topic cleanup.

## Control flow

The SNS path enters through `RGWHandler_REST_PSTopic_AWS::op_post()`, which sets the request dialect/protocol flags, reads `Action`, and dispatches through `op_generators`. The handler authorizes with S3 authentication and explicitly rejects anonymous identities. Each operation parses request arguments in `init_processing()`, often loads existing topic metadata through `RGWPubSub`, evaluates IAM/topic policy in `verify_permission()`, performs metadata-master forwarding in `execute()` when needed, and writes XML SNS responses in `send_response()`.

`CreateTopic` validates name, endpoint, persistence options, retry fields, arbitrary endpoint args, and optional topic policy. It can create persistent queue shards through `driver->add_persistent_topic()` before storing the topic with `RGWPubSub::create_topic()`. Repeated creation of an already persistent topic preserves the existing queue and shard count rather than resharding.

`ListTopics` selects v2 listing when all zonegroups support `notification_v2` and no v1 topic marker exists, otherwise falls back to v1. Account users are authorized up front against account root ARN; non-account users list then filter topics by `snsGetTopicAttributes`. Topic responses containing stored secrets require secure transport.

`GetTopic` and `GetTopicAttributes` parse `TopicArn`, load topic metadata from the ARN account namespace, reject missing topics as `NotFound`, block secret-bearing topic output over insecure transport, and require `snsGetTopicAttributes`.

`SetTopicAttributes` loads a topic, maps a single `AttributeName`/`AttributeValue` into updated destination, opaque data, policy text, or endpoint args, then forwards if needed. It creates persistent queue shards when a topic becomes persistent and removes shards when it becomes non-persistent before rewriting topic metadata.

`DeleteTopic` is idempotent for missing topics. If the topic exists, it authorizes against `snsDeleteTopic`, forwards when needed, and removes topic metadata.

The S3 notification path enters through `RGWHandler_REST_PSNotifs_S3` for `GET`, `PUT`, and `DELETE` on `?notification`. `PUT` parses XML `NotificationConfiguration`, validates notification ids, topic ARNs, event types, and topic existence, then requires bucket `s3PutBucketNotification` and `snsPublish` on every target topic. For v1, it creates per-notification internal topics named by `topic_to_unique()`, stores destination metadata there, and creates bucket notifications. For v2, it writes `RGW_ATTR_BUCKET_NOTIFICATION` on the bucket under `retry_raced_bucket_write()` and updates bucket-topic mapping. Empty configuration deletes all notifications. `DELETE` removes one notification or all notifications, using v2 attr removal when available and legacy `RGWPubSub::Bucket` operations otherwise. `GET` loads the bucket, chooses v2 attr read or legacy topic listing, filters to S3 notifications, and emits XML.

## State and persistence behavior

Topic state is persisted through `RGWPubSub::create_topic()`, `get_topic()`, `get_topics_v1()`, `get_topics_v2()`, and `remove_topic()`. Persistent notification queue state is managed through driver calls `add_persistent_topic()` and `remove_persistent_topic()` using shard names from `rgw_pubsub_dest`. In v1 bucket notifications, the code creates internal per-notification topics and subscription records under `RGWPubSub::Bucket`. In v2, bucket notification configuration is encoded into `RGW_ATTR_BUCKET_NOTIFICATION` on bucket attrs and stored with `merge_and_store_attrs()`, with `retry_raced_bucket_write()` protecting against concurrent bucket metadata updates. Topic-to-bucket reverse mappings are updated with `driver->update_bucket_topic_mapping()`.

The file also persists security-relevant metadata: `stored_secret` marks topics whose endpoint config includes credentials, and topic policy text is stored with topic metadata for later resource-policy evaluation.

## Dependencies and integration points

This file depends on `rgw_pubsub.h`, `rgw_arn.h`, `rgw_iam_policy.h`, `rgw_auth_s3.h`, `rgw_rest_s3.h`, `rgw_process_env.h`, SAL driver APIs, zone feature checks, XML decoding, Ceph formatter/XML output, and notification helper functions such as `get_bucket_notifications()`, `remove_notification_v2()`, `topic_to_unique()`, and `find_unique_topic()`. It is integrated into RGW REST routing through `RGWHandler_REST_PSTopic_AWS` and `RGWHandler_REST_PSNotifs_S3`, with static factory methods allowing other handlers to construct S3 notification ops.

## Risks and edge cases

- Secret-bearing topic metadata is intentionally blocked on insecure transport, but the bypass config is high risk and logs only a warning.
- `SetTopicAttributes` rewrites `push_endpoint_args` by substring search; malformed or overlapping endpoint arg names could be a maintenance-sensitive area.
- Several forwarded operations mutate `s->info.args` before forwarding or local processing. Iterator erasure inside loops over `get_params()` appears delicate and should be tested for skipped entries or invalidation.
- Persistent queue creation/removal is not fully transactional with topic metadata writes. Failures after shard creation or removal can leave queue/topic state needing cleanup.
- V1/v2 migration guards return service unavailable when v1 topics still exist or migration state is unknown. Mixed-version zonegroup behavior is a key compatibility risk.
- `ListTopics` v2/v1 selection uses `stat_topics_v1()` as a migration signal; incorrect signal values would change listing source.
- Permission semantics differ for account and non-account identities and for missing legacy owners. Regression tests should cover cross-account and legacy-owner compatibility.

## Test signals

Useful tests include SNS create/list/get/set/delete topic flows; topic creation with endpoint credentials over HTTP and HTTPS; topic policies for same-owner, cross-account, deny, and allow cases; persistent topic shard creation, idempotent create without resharding, transition to non-persistent, and failure cleanup; S3 `PUT/GET/DELETE ?notification` with empty config, one config, multiple configs, filters, invalid events, missing topics, and specific notification deletion; v1 versus v2 notification storage selection; metadata-master forwarding from secondary zones; and migration-block behavior when v1 topics are present.
