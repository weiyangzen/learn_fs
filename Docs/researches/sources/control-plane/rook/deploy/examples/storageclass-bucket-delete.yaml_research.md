# sources/control-plane/rook/deploy/examples/storageclass-bucket-delete.yaml

Purpose: bucket provisioning class for `my-store` with delete reclaim behavior.

Important APIs/types/functions: `StorageClass/rook-ceph-delete-bucket`, bucket provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, and object store parameters.

Control flow: OBCs using this class create RGW buckets and delete them when claims are removed.

State and persistence: the class persists provisioning defaults; RGW stores bucket data until reclaim deletion.

Dependencies/integration: used by delete and notification OBC examples.

Risks: accidental OBC deletion can remove object data.

Test signals: bound OBC and backend bucket deletion on claim removal.
