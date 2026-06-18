
# sources/control-plane/rook/deploy/examples/cosi/cephcosidriver.yaml

Purpose: enables the Rook Ceph COSI driver and creates a privileged RGW user for provisioning COSI buckets and access credentials.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCOSIDriver` with `spec.deploymentStrategy: "Auto"` and `CephObjectStoreUser` named `cosi` in `rook-ceph` with `store: my-store`, display name, and wildcard `user` and `bucket` capabilities.

Control flow: the Rook operator reconciles `CephCOSIDriver` by deploying or configuring the COSI driver automatically. It reconciles `CephObjectStoreUser` by creating an RGW user and Kubernetes secret that BucketClass and BucketAccessClass parameters can reference.

State and persistence: the driver CR and object store user CR persist in Kubernetes. RGW user credentials and capabilities persist in Ceph and in generated Kubernetes secrets.

Dependencies/integration: depends on a CephObjectStore named `my-store`, COSI CRDs/controllers, RBAC for `objectstorage-provisioner`, and the bucket class/access class manifests that reference the generated secret.

Risks: wildcard user and bucket capabilities are intentionally high privilege and should be scoped carefully in production. Store name mismatch prevents user creation. Automatic deployment depends on operator support for the COSI driver.

Test signals: apply after object store creation, verify driver pods/resources, confirm the object user secret exists, and provision a bucket/access pair using the sample COSI classes.
