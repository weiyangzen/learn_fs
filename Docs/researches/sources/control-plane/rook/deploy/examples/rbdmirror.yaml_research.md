# sources/control-plane/rook/deploy/examples/rbdmirror.yaml

Purpose: deploys RBD mirror daemon(s) for mirrored pools.

Important APIs/types/functions: `CephRBDMirror/my-rbd-mirror` with `count`, placement, annotations, and CPU/memory resource requests/limits.

Control flow: Rook creates mirror daemon deployments that connect to local and remote peers and replay image journal/snapshot changes.

State and persistence: mirror daemon pods are stateless; mirroring state is in Ceph/RBD metadata and remote peer configuration.

Dependencies/integration: requires mirrored pools such as `pool-mirrored.yaml` and configured peers/secrets.

Risks: insufficient resources or peer misconfiguration stalls replication.

Test signals: daemon pod ready and `rbd mirror pool status` reports healthy replay.
