# sources/control-plane/rook/deploy/examples/object-bucket-claim-retain.yaml

Purpose: requests a bucket from a retain-reclaim bucket storage class.

Important APIs/types/functions: `ObjectBucketClaim/ceph-retain-bucket`, generated bucket prefix `ceph-bkt`, `storageClassName: rook-ceph-retain-bucket`, and optional `additionalConfig`.

Control flow: the bucket provisioner creates the bucket and binding objects; deleting the OBC should leave the backend bucket according to the retain reclaim policy.

State and persistence: RGW bucket data persists beyond claim deletion; Kubernetes binding state is removed or released.

Dependencies/integration: requires `storageclass-bucket-retain.yaml` and target `CephObjectStore/my-store`.

Risks: retained buckets can become orphaned and need manual cleanup or re-import.

Test signals: OBC binds, deleting it does not delete the RGW bucket, and credentials cleanup behaves as expected.
