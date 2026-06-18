
# sources/control-plane/rook/deploy/examples/bucket-notification.yaml

Purpose: defines a sample `CephBucketNotification` that subscribes to object creation events on a named topic with key, metadata, and tag filters.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephBucketNotification`, `spec.topic`, `spec.filter.keyFilters`, `metadataFilters`, `tagFilters`, and S3 event names `s3:ObjectCreated:Put` and `s3:ObjectCreated:Copy`.

Control flow: the Rook/RGW notification controller reconciles the CR in the application namespace, finds topic `my-topic`, and configures RGW notification rules. All listed filters must match for the notification to apply, while any listed event can trigger it.

State and persistence: the CR persists desired notification state in Kubernetes; RGW stores corresponding bucket notification configuration. Filter choices affect future object events but not existing objects.

Dependencies/integration: depends on a compatible CephObjectStore/RGW, topic `my-topic` from `bucket-topic.yaml`, bucket notification CRDs, and Ceph support for the selected S3 notification events and filter syntax.

Risks: regex and suffix/prefix filters are easy to mis-specify, leading to silent non-delivery. Topic namespace/name mismatch blocks reconciliation. Metadata and tag filters only match objects carrying the expected fields.

Test signals: create the topic and notification, upload objects that match and do not match each filter, then inspect RGW/topic delivery and CR status/events for reconciliation errors.
