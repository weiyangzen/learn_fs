
# sources/control-plane/rook/deploy/examples/cosi/bucketclass.yaml

Purpose: defines a sample COSI `BucketClass` for provisioning RGW buckets through the Rook Ceph COSI driver.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketClass`, `driverName: rook-ceph.ceph.objectstorage.k8s.io`, `deletionPolicy: Delete`, and parameters pointing to `objectStoreUserSecretName` and namespace.

Control flow: BucketClaim objects reference this class. The COSI controller invokes the matching driver with the parameters, and the driver provisions/deletes RGW buckets according to the deletion policy.

State and persistence: the class persists cluster-level provisioning policy. Referenced buckets persist in Ceph RGW until deleted by claim lifecycle and policy.

Dependencies/integration: depends on COSI CRDs/controllers, the Rook Ceph COSI driver, and a privileged object store user secret created by the `cephcosidriver.yaml` sample or equivalent.

Risks: `deletionPolicy: Delete` can remove buckets when claims are deleted. Wrong secret namespace/name blocks provisioning. Driver-name drift leaves claims unhandled.

Test signals: create a BucketClaim using `sample-bcc`, verify bucket creation in RGW, then delete the claim in a test environment and confirm bucket deletion behavior.
