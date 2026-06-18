# sources/control-plane/rook/deploy/examples/storageclass-bucket-a.yaml

Purpose: defines a bucket provisioner `StorageClass` for object store `store-a`.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass/rook-ceph-bucket-a`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, and parameters `objectStoreName: store-a`, `objectStoreNamespace: rook-ceph`.

Control flow: OBCs referencing this class invoke Rook's bucket provisioner for `store-a`.

State and persistence: StorageClass stores provisioning parameters; buckets are persisted in RGW.

Dependencies/integration: requires `CephObjectStore/store-a` and objectbucket CRDs.

Risks: delete reclaim policy removes backend buckets with claims.

Test signals: `object-bucket-claim-a.yaml` binds and produces credentials.
