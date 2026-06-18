# sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.cc

## Purpose
Migrates legacy v1 pubsub topic and bucket notification metadata to the v2 metadata layout introduced for the Squid release once the notification_v2 feature is enabled.

## Important APIs, types, and functions
- `deconstruct_topics_oid()` parses legacy bucket notification oids of the form `pubsub.{tenant}.bucket.{name}/{marker}`.
- `migrate_notification()` migrates one bucket notification object into the bucket's `RGW_ATTR_BUCKET_NOTIFICATION` attr, merging with existing v2 notification config and then removing the v1 object.
- `migrate_topics()` migrates one tenant topics object into v2 topic metadata through `driver->write_topic_v2()` and then removes the v1 tenant topics object.
- Public `migrate()` lists legacy `pubsub.` objects from the log pool, migrates bucket notifications first, then tenant topic objects.

## Control flow
`migrate()` initializes an ioctx on the zone log pool and pages through objects with the legacy pubsub prefix. Objects containing the bucket infix are migrated immediately; other topic oids are queued and migrated after all bucket notifications. Bucket notification migration reads v1 topics through `RadosBucket::read_topics()`, loads the bucket by tenant/name/marker, merges topics into existing v2 attrs, retries attr storage up to 15 times on `-ECANCELED`, then deletes the v1 object. Tenant topic migration reads v1 topics, skips auto-generated topics where `topic.name != topic.dest.arn_topic`, writes v2 topics exclusively, tolerates `-EEXIST`, then removes v1 topics.

## State and persistence behavior
Reads legacy metadata from the zone log pool and bucket topic objects. Writes v2 bucket notification state into bucket instance attrs under `RGW_ATTR_BUCKET_NOTIFICATION`; writes v2 topic objects via the driver. Deletes v1 bucket/tenant topic objects with version trackers so repeated runs become mostly idempotent.

## Dependencies and integration points
Depends on `RadosStore`, `RadosBucket`, zone service, RADOS pool listing, pubsub structures, cluster log warnings, bucket attr merge/store, and v2 topic writer/remover driver methods. It is intended to run during gateway startup feature migration.

## Risks and edge cases
Parsing is strict and logs cluster warnings on unexpected oid shapes. Migration can be partial: some bucket notifications or topics may migrate before a later error aborts. The bucket attr merge does not override existing v2 topics with the same keys. If the bucket is deleted or marker changes, migration skips directly to deleting the legacy object. After 15 `-ECANCELED` retries it returns the error for a later retry. In `migrate()`, per-object errors are logged but the loop continues and later topic migration overwrites `r`; final return is always 0 after the loops, so some individual failures may not propagate.

## Test signals
Tests should cover oid parsing, empty v1 notifications, merge with existing v2 attrs, deleted bucket, marker mismatch, repeated `-ECANCELED`, corrupt v2 attr decode, tenant topic skip for generated topics, exclusive v2 topic conflict, removal idempotence, listing pagination, and failure propagation expectations.
