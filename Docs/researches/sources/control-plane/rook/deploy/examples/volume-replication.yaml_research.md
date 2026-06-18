# sources/control-plane/rook/deploy/examples/volume-replication.yaml

Purpose: declares desired replication state for a PVC.

Important APIs/types/functions: `VolumeReplication/pvc-volumereplication`, `volumeReplicationClass`, `replicationState`, and `dataSource` referencing a PVC.

Control flow: the replication controller calls CSI replication operations to make the PVC primary or secondary according to `replicationState`.

State and persistence: Kubernetes stores desired state and status; RBD image mirror state persists in Ceph.

Dependencies/integration: requires `volume-replication-class.yaml`, a mirrored RBD PVC, and replication controller/CSI sidecars.

Risks: promoting the wrong PVC can create split-brain in disaster recovery scenarios.

Test signals: status conditions reflect completed promote/demote and RBD mirror status agrees.
