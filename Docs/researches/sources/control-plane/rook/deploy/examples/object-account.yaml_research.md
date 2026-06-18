# sources/control-plane/rook/deploy/examples/object-account.yaml

Purpose: creates a Ceph RGW account object for account-oriented object user management.

Important APIs/types/functions: `CephObjectStoreAccount/my-account` in `rook-ceph` with `spec.store` pointing at the object store.

Control flow: the Rook object controller reconciles the account against RGW admin APIs after the target store is available.

State and persistence: the account exists in RGW metadata and desired state persists as a Kubernetes CR.

Dependencies/integration: requires a running `CephObjectStore` and RGW admin credentials managed by Rook.

Risks: account creation will fail or remain pending if the referenced store is absent or not ready.

Test signals: CR status ready and the corresponding RGW account present via `radosgw-admin account list/show`.
