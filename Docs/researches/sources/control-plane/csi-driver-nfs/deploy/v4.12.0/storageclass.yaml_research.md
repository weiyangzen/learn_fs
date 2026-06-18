<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml

## Purpose
Defines a sample Kubernetes `StorageClass` named `nfs-csi` for dynamic provisioning through the NFS CSI driver.

## Important APIs, Types, And Objects
The class sets `provisioner: nfs.csi.k8s.io`, `parameters.server: nfs-server.default.svc.cluster.local`, `parameters.share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`. Comments show optional provisioner secret parameters for mount options during `DeleteVolume`.

## Control Flow
PVCs referencing this class are picked up by the CSI provisioner sidecar, which calls the NFS CSI controller plugin to create a subdirectory or backing path under the configured share. Kubelet/node plugin later mounts the NFS export into pods using the declared mount option.

## State And Persistence Behavior
The StorageClass is durable cluster configuration. PVs dynamically created from it persist their NFS volume handle and reclaim behavior; actual data persists on the configured NFS server/share.

## Dependencies And Integration Points
Depends on a reachable NFS service at `nfs-server.default.svc.cluster.local`, the controller Deployment, node DaemonSet, RBAC, and `CSIDriver` identity. Expansion depends on the resizer sidecar and driver support.

## Risks And Edge Cases
The server value is an example default and may not exist in production. `reclaimPolicy: Delete` can remove backing data when PVCs are deleted. `Immediate` binding may provision before pod scheduling constraints are known. NFS v4.1 must be supported by the server and nodes.

## Test Signals
Create a PVC with this class, verify PV provisioning and pod mount success, write data through the mount, expand the PVC, and delete the PVC to confirm reclaim behavior on the NFS share.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml -->
