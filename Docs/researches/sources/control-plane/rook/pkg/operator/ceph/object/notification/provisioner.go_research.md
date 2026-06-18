# sources/control-plane/rook/pkg/operator/ceph/object/notification/provisioner.go

Purpose: adapts Rook/Ceph object-store context into AWS SDK S3 operations for bucket notification creation, listing, and deletion.

Important APIs/types: `provisioner`, `getUserCredentials`, `newS3Agent`, `createS3FilterRules`, `createS3Filter`, `createS3Events`, `createNotification`, `getAllRGWNotifications`, and `deleteNotification`. Package-level variables allow the create/list/delete functions to be replaced in tests.

Control flow: `newS3Agent` retrieves the `CephObjectStore`, builds a multisite object context, creates an Admin Ops context, fetches the bucket owner user's RGW credentials, optionally obtains TLS CA/insecure settings, and returns an `object.S3Agent`. Create builds a `PutBucketNotificationConfigurationInput` with one topic configuration whose ID is the notification CR name, events default to object-created and object-removed wildcards when unspecified, and filters are translated from Rook CRD key rules. List calls `GetBucketNotificationConfiguration` and returns topic configuration IDs. Delete delegates to the custom Ceph S3 extension in `s3ext.go`.

State and persistence: reads Kubernetes `CephObjectStore`; reads Ceph RGW user credentials through Admin Ops; writes bucket notification configuration through S3 APIs; deletes notification state through a manually signed Ceph extension request. It does not store local state.

Dependencies and integration points: depends on AWS SDK v2 S3 types, go-ceph RGW admin user data, Rook object context/Admin Ops helpers, bucket owner metadata from `ObjectBucket.Spec.AdditionalState`, topic ARNs from notification controller flow, and TLS helper `GetTlsCaCert`.

Risks: `getUserCredentials` assumes `u.Keys[0]` exists; `createNotification` submits a configuration containing only one topic configuration and may replace preexisting configurations depending on RGW semantics; list dereferences `tc.Id`; delete uses `context.TODO()` instead of the operator manager context. Defaulting empty event lists to both create/remove events is significant and should remain explicit in CRD docs.

Test signals: direct unit tests are primarily through the OBC label controller's function overrides. There is no focused test here for credential edge cases, filter/event conversion, preservation of multiple topic configurations, or TLS S3 agent creation through the provisioner.
