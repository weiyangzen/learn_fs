
# sources/control-plane/rook/deploy/examples/cosi/bucketaccess.yaml

Purpose: defines a sample COSI `BucketAccess` that requests S3 credentials for an existing bucket claim.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketAccess`, metadata namespace `default`, `spec.bucketClaimName: sample-bucket`, `bucketAccessClassName: sample-bac`, `credentialsSecretName: sample-access-secret`, and `protocol: s3`.

Control flow: the COSI controller and Rook Ceph COSI driver reconcile the access request, use the referenced access class for authentication details, and create/update the named credentials secret.

State and persistence: the BucketAccess object and generated secret persist in Kubernetes. Actual bucket/user permissions are managed in Ceph RGW by the driver.

Dependencies/integration: depends on `bucketclaim.yaml`, `bucketaccessclass.yaml`, installed COSI CRDs/controllers, `CephCOSIDriver`, and the referenced object store user secret.

Risks: namespace mismatch with the bucket claim or secret expectations breaks provisioning. The named secret contains credentials and needs normal secret access controls. Alpha COSI APIs may change.

Test signals: apply with the paired class/claim/driver, verify status, confirm `sample-access-secret` exists, and test S3 access using the generated credentials.
