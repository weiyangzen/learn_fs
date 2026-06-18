# sources/control-plane/rook/deploy/examples/object-bucket-claim-a.yaml

Purpose: requests an object bucket from the `store-a` bucket storage class.

Important APIs/types/functions: `objectbucket.io/v1alpha1` `ObjectBucketClaim/ceph-bucket-a`, `generateBucketName: ceph-bkt`, and `storageClassName: rook-ceph-bucket-a`.

Control flow: the lib-bucket-provisioner watches the OBC, calls Rook's bucket provisioner, creates an ObjectBucket, and writes connection credentials into a Secret/ConfigMap.

State and persistence: bucket data is persisted in Ceph RGW; the OBC and generated objects persist Kubernetes-side binding state.

Dependencies/integration: requires `storageclass-bucket-a.yaml` and `CephObjectStore/store-a`.

Risks: bucket names are generated, so consumers must read the generated config rather than assume a literal name.

Test signals: OBC `Bound` phase and generated Secret/ConfigMap with RGW endpoint and credentials.
