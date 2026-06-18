
# sources/control-plane/rook/deploy/examples/cosi/bucketaccessclass.yaml

Purpose: defines a COSI `BucketAccessClass` that tells the COSI controller how to grant S3 access through the Rook Ceph driver.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketAccessClass`, `driverName: rook-ceph.ceph.objectstorage.k8s.io`, `authenticationType: KEY`, and parameters `objectStoreUserSecretName` and `objectStoreUserSecretNamespace`.

Control flow: BucketAccess objects reference this class. The controller passes the driver name and parameters to the Rook Ceph COSI driver, which uses the privileged object store user secret to create credentials.

State and persistence: the class is cluster-scoped COSI configuration. It does not contain credentials directly, but it points to a secret that authorizes bucket access management.

Dependencies/integration: depends on COSI CRDs/controllers, the Rook Ceph COSI driver, and secret `rook-ceph-object-user-my-store-cosi` in namespace `rook-ceph`.

Risks: stale or wrong secret references prevent access provisioning. KEY authentication exposes long-lived credentials through generated secrets. The driver name must exactly match the installed driver.

Test signals: apply with the driver and secret present, create a BucketAccess using `sample-bac`, and verify credentials are generated and work against RGW.
