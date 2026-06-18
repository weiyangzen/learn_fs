# sources/control-plane/rook/deploy/examples/object-user.yaml

Purpose: creates an RGW user for an existing object store.

Important APIs/types/functions: `CephObjectStoreUser/my-user` in `rook-ceph`, `spec.store: my-store`, and `displayName`.

Control flow: Rook reconciles the user by calling RGW admin APIs and writes credentials to a Kubernetes Secret.

State and persistence: user metadata persists in RGW; credentials persist in Kubernetes Secret.

Dependencies/integration: requires `CephObjectStore/my-store` and RGW admin connectivity.

Risks: deleting/recreating the user rotates or removes credentials, affecting clients.

Test signals: user CR ready and generated secret can authenticate S3 operations.
