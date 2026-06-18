<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml

## Purpose
Provides the sample `nfs-csi` StorageClass for v4.12.1 dynamic NFS CSI provisioning.

## Important APIs, Types, And Objects
The class uses provisioner `nfs.csi.k8s.io`, server `nfs-server.default.svc.cluster.local`, share `/`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

## Control Flow
PVCs select this class, the external provisioner calls the v4.12.1 NFS controller, and node plugins mount resulting PVs into pods with NFS v4.1.

## State And Persistence Behavior
StorageClass settings persist cluster-wide. Dynamically provisioned PVs and data on the NFS export are the durable operational state created from this configuration.

## Dependencies And Integration Points
Depends on the NFS server DNS name, NFS export availability, controller/node plugin deployments, RBAC, and the `CSIDriver` object.

## Risks And Edge Cases
The example server may not exist outside a sample cluster. Delete reclaim can remove data, Immediate binding can pre-provision before a pod is scheduled, and expansion requires working driver and NFS backend behavior.

## Test Signals
Provision a PVC, mount it in a pod, validate read/write, expand the claim, and observe PV/backing directory cleanup after deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml -->
