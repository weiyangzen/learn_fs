<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml

## Purpose
Registers `nfs.csi.k8s.io` as a Kubernetes CSI driver for the v4.12.1 manifest set.

## Important APIs, Types, And Objects
The `CSIDriver` disables attach with `attachRequired: false`, declares only `Persistent` lifecycle mode, and sets `fsGroupPolicy: File`.

## Control Flow
Kubernetes control loops use this metadata when scheduling and mounting PVCs provisioned by the NFS CSI driver. No `VolumeAttachment` objects are needed; kubelet works directly with the node plugin after scheduling.

## State And Persistence Behavior
The object is cluster-scoped persistent metadata in etcd. It has no status section and does not hold per-volume runtime state.

## Dependencies And Integration Points
The name must match the controller and node plugin identity, `StorageClass.provisioner`, and `VolumeSnapshotClass.driver`. It complements node-driver-registrar registration in the DaemonSet.

## Risks And Edge Cases
Driver-name mismatch breaks storage and snapshot routing. File fsGroup handling can be costly for large NFS-backed trees. Persistent-only lifecycle excludes inline ephemeral CSI declarations.

## Test Signals
Verify `kubectl get csidriver nfs.csi.k8s.io`, provision a PVC-backed pod without VolumeAttachment creation, and check file ownership behavior for pods with an `fsGroup`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml -->
