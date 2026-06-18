<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml -->
# sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml

Purpose: object bucket StorageClass that deletes externally provisioned buckets when claims are deleted.
Important APIs/types/functions: `StorageClass` `rook-ceph-delete-bucket`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, `objectStoreName`, `objectStoreNamespace`, and optional existing `bucketName`.
Control flow: OBC creation calls the Rook bucket provisioner, which creates or binds a bucket in the named object store and returns credentials. Deletion follows the StorageClass reclaim policy and removes bucket data. State lives in OBC/OB resources, generated Secrets/ConfigMaps, and RGW buckets/users. Dependencies are `object-external.yaml`, object bucket CRDs, and RGW admin credentials. Risks: file references `objectStoreName: my-store` while the object store example is named `external-store`, so users must align names; delete policy is destructive. Test signals: OBC binds, bucket exists in RGW, credentials work, and deletion behavior matches policy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml -->
