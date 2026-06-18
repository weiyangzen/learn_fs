<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml

## Purpose
Registers the v4.13.0 NFS CSI driver identity and capabilities through the Kubernetes `CSIDriver` API.

## Important APIs, Types, And Objects
The `CSIDriver` is named `nfs.csi.k8s.io`, with `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow
Kubernetes skips attach/detach controller work for this driver and relies on kubelet plus the node plugin for volume publishing. The object is consulted for scheduling and mount-time policy.

## State And Persistence Behavior
The object is persistent cluster metadata. It stores no runtime status or volume inventory.

## Dependencies And Integration Points
The name aligns with `StorageClass.provisioner`, `VolumeSnapshotClass.driver`, node-driver-registrar registration, and the plugin-reported CSI name.

## Risks And Edge Cases
Any mismatch in driver naming breaks class routing and kubelet registration. `fsGroupPolicy: File` can affect mount latency or file ownership behavior on large shares. The manifest does not declare ephemeral lifecycle support.

## Test Signals
Verify the `CSIDriver` object, mount a PVC-backed pod without `VolumeAttachment`, and test `fsGroup` behavior on mounted NFS files after v4.13.0 rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml -->
