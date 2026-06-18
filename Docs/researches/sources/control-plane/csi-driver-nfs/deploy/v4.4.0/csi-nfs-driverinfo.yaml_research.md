# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the NFS CSI driver with Kubernetes through a `CSIDriver` object. It tells Kubernetes that `nfs.csi.k8s.io` does not require attach/detach and supports persistent volumes.

## Important APIs, Types, and Functions
The only object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io`. Its key fields are `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The object is cluster-scoped and persistent. Kubernetes admission and kubelet CSI plumbing consult it when scheduling and mounting volumes, skipping attach-controller workflows and applying file-based fsGroup ownership policy when requested by pods.

## Dependencies and Integration Points
It integrates with the controller and node plugin deployments, storage classes that name `nfs.csi.k8s.io`, and kubelet plugin registration under `/var/lib/kubelet/plugins/csi-nfsplugin`. It depends on Kubernetes support for `storage.k8s.io/v1` `CSIDriver`.

## Risks and Test Signals
Risks include driver-name mismatch with storage classes or node registration, incorrect fsGroup policy expectations for NFS exports, and applying the object before a cluster version supports the selected fields. Test signals are `kubectl get csidriver nfs.csi.k8s.io`, successful PVC scheduling without VolumeAttachment objects, node-driver-registrar reporting the same name, and pod mounts honoring requested fsGroup behavior.
