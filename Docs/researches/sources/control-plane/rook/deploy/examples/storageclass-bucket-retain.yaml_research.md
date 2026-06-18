# sources/control-plane/rook/deploy/examples/storageclass-bucket-retain.yaml

Purpose: bucket provisioning class for `my-store` with retain reclaim behavior.

Important APIs/types/functions: `StorageClass/rook-ceph-retain-bucket`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Retain`, and object store namespace/name parameters.

Control flow: OBCs using this class create RGW buckets but leave backend buckets after claim deletion.

State and persistence: retained bucket data persists in RGW after Kubernetes claim cleanup.

Dependencies/integration: used by `object-bucket-claim-retain.yaml`.

Risks: retained buckets can accumulate and need manual management.

Test signals: OBC binds and bucket remains after claim deletion.
