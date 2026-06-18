# sources/control-plane/rook/deploy/examples/volume-replication-class.yaml

Purpose: defines an OpenShift volume replication class for RBD mirroring.

Important APIs/types/functions: `replication.storage.openshift.io/v1alpha1` `VolumeReplicationClass/rbd-volumereplicationclass`, provisioner, and parameters for the RBD CSI replication driver.

Control flow: VolumeReplication resources reference this class to tell the CSI replication sidecar how to promote/demote mirrored volumes.

State and persistence: class stores static driver parameters; replication state is in PVC/RBD metadata.

Dependencies/integration: requires OpenShift replication CRDs, Ceph CSI with mirroring support, and mirrored RBD pool.

Risks: provisioner/parameter mismatch prevents replication operations.

Test signals: class accepted and referenced by `volume-replication.yaml` without controller errors.
