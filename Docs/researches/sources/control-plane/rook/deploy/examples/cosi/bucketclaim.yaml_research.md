
# sources/control-plane/rook/deploy/examples/cosi/bucketclaim.yaml

Purpose: defines a sample COSI `BucketClaim` requesting an S3 bucket using the sample bucket class.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketClaim`, metadata namespace `default`, `spec.bucketClassName: sample-bcc`, and `protocols: [s3]`.

Control flow: the COSI controller watches the claim, resolves `BucketClass/sample-bcc`, asks the Rook Ceph COSI driver to provision a bucket, and records binding/status information for the claim.

State and persistence: the claim persists desired bucket state in Kubernetes; the driver creates corresponding RGW bucket state in Ceph. Deletion behavior is controlled by the referenced bucket class.

Dependencies/integration: depends on `bucketclass.yaml`, COSI CRDs/controllers, the Ceph COSI driver, and an object store user with bucket capabilities.

Risks: alpha API stability, missing bucket class, or missing driver prevents provisioning. Namespace-local application code still needs a BucketAccess to obtain credentials.

Test signals: apply with the bucket class and driver installed, verify claim status/binding, list the bucket in RGW, then delete and confirm behavior follows the class deletion policy.
