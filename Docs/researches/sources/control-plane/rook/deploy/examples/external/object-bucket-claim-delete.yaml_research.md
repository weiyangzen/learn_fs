<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml -->
# sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml

Purpose: example ObjectBucketClaim that creates a bucket through an external object store StorageClass with delete reclaim semantics.
Important APIs/types/functions: `objectbucket.io/v1alpha1` `ObjectBucketClaim`, `generateBucketName: ceph-bkt`, `storageClassName: rook-ceph-delete-bucket`, and optional quota fields in `additionalConfig`.
Control flow: the bucket provisioner creates a bucket or grants access according to the referenced StorageClass, then writes Secret/ConfigMap connection details for the claim. State persists in OBC/OB resources, bucket credentials, and the external RGW bucket. Dependencies are object bucket CRDs/provisioner, `storageclass-bucket-delete.yaml`, and external object store configuration. Risks: delete reclaim can delete bucket data when the claim is removed, generated names are non-deterministic, and quotas are commented out. Test signals: OBC Bound, connection Secret exists, bucket is reachable via S3, and deleting the OBC removes the bucket when expected.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml -->
