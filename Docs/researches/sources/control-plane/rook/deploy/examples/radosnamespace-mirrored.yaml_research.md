# sources/control-plane/rook/deploy/examples/radosnamespace-mirrored.yaml

Purpose: defines an RBD RADOS namespace with mirroring configuration.

Important APIs/types/functions: `CephBlockPoolRadosNamespace/namespace-a`, `blockPoolName`, mirroring `remoteNamespace`, mode `image`, and snapshot schedule interval/start time.

Control flow: Rook creates the namespace under the pool and configures RBD namespace mirroring metadata.

State and persistence: namespace and mirror scheduling state persist in Ceph RBD metadata.

Dependencies/integration: requires the referenced block pool and RBD mirror daemon/peer setup.

Risks: remote namespace mismatch prevents replication; schedules can create unexpected snapshot load.

Test signals: namespace exists, mirror schedule appears through `rbd mirror snapshot schedule ls`, and mirror status is healthy.
