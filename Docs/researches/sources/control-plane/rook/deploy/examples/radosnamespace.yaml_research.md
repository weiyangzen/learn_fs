# sources/control-plane/rook/deploy/examples/radosnamespace.yaml

Purpose: creates a basic RBD RADOS namespace inside a block pool.

Important APIs/types/functions: `CephBlockPoolRadosNamespace/namespace-a` with `spec.blockPoolName`.

Control flow: Rook reconciles the namespace into the named Ceph pool.

State and persistence: RBD images created in the namespace persist separately from the default pool namespace.

Dependencies/integration: requires the referenced `CephBlockPool` to exist.

Risks: consumers must set namespace-aware storage class parameters or they will use the default namespace.

Test signals: `rbd namespace ls <pool>` includes `namespace-a` and PVC provisioning works with namespace config.
