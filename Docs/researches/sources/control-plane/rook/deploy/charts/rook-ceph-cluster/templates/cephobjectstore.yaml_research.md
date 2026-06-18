## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore.yaml

Purpose: renders CephObjectStore CRs and optional Object Bucket Claim StorageClasses from `.Values.cephObjectStores`.

Important template behavior: for each object store, creates `CephObjectStore` in the release namespace with raw `.spec`. If `storageClass.enabled`, creates a StorageClass with provisioner `<release-namespace>.ceph.rook.io/bucket`, objectStoreName/objectStoreNamespace parameters, optional labels/annotations, reclaim policy, binding mode, and user-supplied parameters.

Control flow: range over object stores with optional StorageClass document.

State and persistence: causes the Rook operator to create RGW/object-store resources and creates a cluster-scoped bucket provisioner StorageClass for ObjectBucketClaims.

Dependencies and integration points: depends on CephObjectStore CRD, lib-bucket-provisioner/Rook bucket provisioning, and RGW service naming used by ingress/route templates. Risks: StorageClass provisioner uses release namespace directly rather than operator namespace; incorrect region or store names break bucket provisioning; object store specs can preserve pools on delete, affecting cleanup expectations. Tests should include object store with storage class enabled and disabled.
