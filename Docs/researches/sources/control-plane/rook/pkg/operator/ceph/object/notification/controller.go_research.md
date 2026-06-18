# sources/control-plane/rook/pkg/operator/ceph/object/notification/controller.go

## Purpose
`notification/controller.go` reconciles `CephBucketNotification` CRs by provisioning RGW bucket notification configuration for labeled ObjectBucketClaims and their ObjectBuckets.

## Important APIs, Types, and Functions
`Add()` skips notification/OBC label controllers when `ROOK_DISABLE_OBJECT_BUCKET_CLAIM=true`; otherwise it registers both. `addNotificationReconciler()` watches `CephBucketNotification`. `Reconcile()` updates status and reports events. `reconcile()` fetches the notification, handles deletion/no-op, marks Reconciling, gets a provisioned topic via `topic.GetProvisioned()`, loads a ready CephCluster for the topic object-store namespace, lists OBCs matching `bucket-notification-<name>`, waits for ObjectBucket creation, resolves the bucket's CephObjectStore via `bucket.GetObjectStoreNameFromBucket()`, validates it matches the topic, and calls `createNotificationFunc()`.

## Control Flow, State, and Persistence
Status is persisted on the notification as Reconciling, Ready, or failed. RGW notification configuration is persisted externally through the provisioner/Admin Ops path. The controller itself does not label OBCs; that is handled by the companion OBC label reconciler registered from the same `Add()`.

## Dependencies and Integration Points
It integrates CephBucketTopic status/ARNs, ObjectBucketClaim/ObjectBucket CRs, Rook cluster readiness and cluster-info loading, bucket ownership helpers, notification provisioner functions, events/reporting, and OBC label conventions.

## Risks and Test Signals
Risks include topic ARN nil/not ready, cluster namespace mismatches, OBCs selected by labels before their ObjectBucket exists, fallback object-store parsing for older OBs, and status being marked failed for expected requeues. Tests cover missing topic, missing/not-ready cluster, unprovisioned topic, no OBCs, OBC without OB, successful OB notification, and bucket-host parsing.
