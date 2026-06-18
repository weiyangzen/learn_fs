<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml

## Purpose
Defines the v4.13.0 sample `nfs-csi` StorageClass for dynamic provisioning through the NFS CSI driver.

## Important APIs, Types, And Objects
The class uses `provisioner: nfs.csi.k8s.io`, server `nfs-server.default.svc.cluster.local`, share `/`, reclaim policy `Delete`, immediate binding, volume expansion enabled, and mount option `nfsvers=4.1`.

## Control Flow
PVCs referencing this class are reconciled by `csi-provisioner:v6.1.0`, which calls the v4.13.0 NFS controller. Pods mount the resulting PVs through node plugins using NFS v4.1.

## State And Persistence Behavior
The class is durable cluster configuration. Created PVs persist volume handles and reclaim behavior; data persists on the configured NFS export until deleted by reclaim/driver behavior.

## Dependencies And Integration Points
Requires a reachable NFS server at the configured DNS name, v4.13.0 controller/node deployments, RBAC, and `CSIDriver`. Expansion relies on `csi-resizer:v2.0.0` and driver support.

## Risks And Edge Cases
The server/share are sample values and can accidentally point to a broad root export. Delete reclaim can remove data. Immediate binding may not suit topology-sensitive clusters. NFS v4.1 support must be present on client nodes and server.

## Test Signals
Provision and mount a PVC, verify read/write and mount options, expand the PVC, delete the claim, and confirm expected cleanup on the NFS share after the v4.13.0 upgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml -->
