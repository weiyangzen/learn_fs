<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml

## Purpose
Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

## Important APIs, Types, And Objects
The object sets `attachRequired: false`, declares `volumeLifecycleModes: [Persistent]`, and uses `fsGroupPolicy: File`. This tells Kubernetes that volumes from this driver do not require a CSI attach/detach phase, are persistent-volume oriented, and may have file ownership adjusted according to pod `fsGroup`.

## Control Flow
The scheduler, attach/detach controller, kubelet, and CSI sidecars consult this object when handling volumes provisioned by `nfs.csi.k8s.io`. Because attach is disabled, pods can proceed without waiting for a `VolumeAttachment` object. Node publishing is handled by the node daemonset rather than a separate attach controller.

## State And Persistence Behavior
This is a durable cluster-scoped API object persisted in etcd. It stores driver capability metadata only; it does not persist volume state or runtime sockets.

## Dependencies And Integration Points
Integrates with `StorageClass.provisioner`, `VolumeSnapshotClass.driver`, the node-driver-registrar registration path, and the NFS controller/node plugin identity. The name must match the CSI driver name returned by the plugin.

## Risks And Edge Cases
If the plugin reports a different driver name, provisioning and snapshot resources will not bind correctly. `fsGroupPolicy: File` can introduce recursive permission work on large NFS trees, depending on Kubernetes behavior and volume contents. Persistent-only mode means ephemeral inline CSI use is not declared.

## Test Signals
After applying, verify `kubectl get csidriver nfs.csi.k8s.io -o yaml`. Provision a pod using an NFS CSI PVC and confirm no `VolumeAttachment` is created for the volume. Test pod `fsGroup` behavior on files written through the mounted NFS volume.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml -->
