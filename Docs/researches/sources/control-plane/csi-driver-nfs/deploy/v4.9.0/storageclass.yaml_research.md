<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml

## Purpose
Provides the v4.9.0 example `StorageClass` for NFS CSI dynamic provisioning.

## Important APIs, Types, and Functions
The `StorageClass` `nfs-csi` uses `provisioner: nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`.

## Control Flow, State, and Persistence
PVCs using this class cause the external provisioner to call the NFS CSI controller, which creates a directory under the configured share and records parameters in PV volume context. On deletion, reclaim policy requests cleanup unless driver policy retains or archives.

## Dependencies and Integration Points
It depends on a reachable NFS server, NFS CSI controller and node pods, correct RBAC, and Linux NFS client compatibility with the configured mount options.

## Risks and Test Signals
Risks include example DNS/share values being left unchanged, delete reclaim removing user data, immediate binding limitations, and NFS version mismatch. Signals include bound PVCs, created NFS subdirectories, correct PV driver name, and pod mount success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml -->
