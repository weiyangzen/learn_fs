<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml

## Purpose
Provides the v4.8.0 example `StorageClass` for dynamic NFS CSI provisioning.

## Important APIs, Types, and Functions
The `StorageClass` is named `nfs-csi`, uses provisioner `nfs.csi.k8s.io`, sets parameters `server` and `share`, uses `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`.

## Control Flow, State, and Persistence
When a PVC references the class, the external provisioner calls the driver controller to create a subdirectory under the configured NFS share. Delete reclaim policy triggers directory cleanup unless driver parameters or defaults choose retain/archive behavior.

## Dependencies and Integration Points
It depends on a real NFS server at the example DNS name or a user-modified value, the NFS CSI controller, node plugin mount support, and optional secret parameters for delete-time mount options.

## Risks and Test Signals
Risks include placeholder configuration, destructive delete semantics, immediate binding before scheduling constraints are known, and NFSv4.1 incompatibility. Signals are a bound PVC/PV, correct PV volume context, directory creation under the share, and a pod successfully mounting the volume.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml -->
