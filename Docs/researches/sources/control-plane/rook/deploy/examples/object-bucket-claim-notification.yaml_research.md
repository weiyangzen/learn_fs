# sources/control-plane/rook/deploy/examples/object-bucket-claim-notification.yaml

Purpose: demonstrates adding bucket notification association labels to an object bucket claim.

Important APIs/types/functions: `ObjectBucketClaim/ceph-notification-bucket` with label `bucket-notification-my-notification: my-notification`, `generateBucketName: ceph-bkt`, and `storageClassName: rook-ceph-delete-bucket`.

Control flow: bucket provisioning creates the bucket, and Rook notification logic can use the label convention to associate the bucket with a named notification configuration.

State and persistence: bucket contents persist in RGW; notification metadata is stored in RGW/bucket configuration and referenced by Kubernetes labels.

Dependencies/integration: requires bucket storage class and a separately defined bucket notification named `my-notification`.

Risks: label-based association is easy to mistype and may not be validated at admission time.

Test signals: OBC bound and RGW bucket notification configuration visible through S3 notification APIs or Rook status.
