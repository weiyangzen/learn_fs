<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml

## Purpose
Provides an example `StorageClass` named `nfs-csi` for dynamic provisioning through `nfs.csi.k8s.io`.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `StorageClass` with `provisioner: nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`. Commented secret parameters show how DeleteVolume mount options can be supplied.

## Control Flow, State, and Persistence
PVCs referencing this class trigger the external provisioner to call `CreateVolume`, which creates a subdirectory on the configured NFS share. The reclaim policy asks the driver to remove the directory on PV deletion unless driver-specific `onDelete` behavior overrides it.

## Dependencies and Integration Points
It integrates with the CSI NFS controller, the NFS service named in `server`, Kubernetes storage class admission/defaulting, and mount option handling in node/controller publish paths.

## Risks and Test Signals
Risks include placeholder server/share values being used unchanged, immediate binding before workload scheduling, NFS version incompatibility, and destructive delete semantics. Signals are a bound PVC, a PV with `nfs.csi.k8s.io`, a created subdirectory on the share, and successful pod mount using NFSv4.1.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml -->
