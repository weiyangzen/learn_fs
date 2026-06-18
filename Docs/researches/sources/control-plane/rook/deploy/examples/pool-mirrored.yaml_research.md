# sources/control-plane/rook/deploy/examples/pool-mirrored.yaml

Purpose: creates a replicated block pool with RBD mirroring enabled.

Important APIs/types/functions: `CephBlockPool/mirrored-pool`, replicated size 3, `mirroring.enabled: true`, and `mode: image`.

Control flow: Rook creates the pool and enables image-mode mirroring so individual RBD images can be mirrored.

State and persistence: RBD image data persists in the pool; mirroring state is stored in Ceph RBD metadata.

Dependencies/integration: pairs with `rbdmirror.yaml` and remote peer secrets/config.

Risks: mirroring without a configured peer or mirror daemon does not replicate data.

Test signals: `rbd mirror pool status` and active `CephRBDMirror` daemon health.
