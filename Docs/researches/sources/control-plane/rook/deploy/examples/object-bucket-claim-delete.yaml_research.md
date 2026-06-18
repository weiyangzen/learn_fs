# sources/control-plane/rook/deploy/examples/object-bucket-claim-delete.yaml

Purpose: requests a bucket from a delete-reclaim bucket storage class.

Important APIs/types/functions: `ObjectBucketClaim/ceph-delete-bucket`, `storageClassName: rook-ceph-delete-bucket`, and optional `additionalConfig` placeholder.

Control flow: bucket provisioning creates a Ceph RGW bucket and binding resources. When the OBC is deleted, the storage class reclaim policy controls deletion of the backend bucket.

State and persistence: the RGW bucket holds object data; Kubernetes OBC/ObjectBucket resources track binding lifecycle.

Dependencies/integration: requires `storageclass-bucket-delete.yaml`, Rook bucket provisioner, and `CephObjectStore/my-store`.

Risks: delete reclaim policy can remove bucket data when the claim is deleted.

Test signals: bound OBC and backend bucket removal after deleting the claim.
