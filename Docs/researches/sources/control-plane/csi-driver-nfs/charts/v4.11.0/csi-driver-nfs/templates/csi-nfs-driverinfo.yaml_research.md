# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: 4.11.0 CSIDriver registration.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name and feature gates for inline volumes and FSGroup policy.

Control flow: Emits `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle, and optional File FSGroup policy.

State and persistence: Cluster-scoped driver capabilities.

Dependencies and integration points: Must match NFS controller/node `--drivername`, StorageClass provisioner, and VolumeSnapshotClass driver.

Risks: Incorrectly advertised lifecycle or FSGroup support causes runtime mount or scheduling issues. Test signals: dry-run plus pod mount tests.
