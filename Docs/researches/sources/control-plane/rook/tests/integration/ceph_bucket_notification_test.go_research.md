# sources/control-plane/rook/tests/integration/ceph_bucket_notification_test.go

End-to-end bucket notification coverage for RGW-backed OBCs. It validates HTTP topic/notification creation, OBC label-driven backend notification configuration, S3 put/delete event delivery, update ordering, and cleanup.

`testBucketNotifications` creates an HTTP receiver, `CephBucketTopic`, `CephBucketNotification`, OBC with notification label, S3 client from OBC credentials, and checks notifications through `NotificationClient.CheckNotificationFromHTTPEndPoint`. It also mutates OBC labels, adds a second notification, tests reverse OBC/notification/topic creation order, and deletes OBCs/topics/notifications/object store.

State includes HTTP server resources, CephBucketTopic/Notification CRs, ObjectBucketClaims/ObjectBuckets, bucket StorageClasses, RGW bucket notification config, S3 objects, and a dedicated object store. Dependencies are Rook topic/notification/bucket clients, RGW object helpers, `client.AdminTestClusterInfo`, `K8sHelper`, and shared object constants.

Risks: several intended removal/invariance checks call `t.Skipped()` inside retry callbacks, leaving gaps; fixed names/default namespace limit parallelism; the helper deletes the object store passed to it, so callers must isolate it. Signals include CR existence, OBC bound, RGW bucket presence/absence, S3 operation success, HTTP event presence/absence, backend notification configuration, and cleanup success.
