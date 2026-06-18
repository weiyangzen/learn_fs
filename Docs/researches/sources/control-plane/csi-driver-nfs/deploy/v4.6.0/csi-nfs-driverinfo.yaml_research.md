# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.6.0 NFS CSI driver identity in Kubernetes. It is unchanged from the other release directories in this subset.

## Important APIs, Types, and Functions
The single `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io` declares `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
Kubernetes persists this cluster-scoped object and uses it during volume admission, scheduling, attach decisions, and kubelet mount behavior. There is no runtime loop inside the manifest.

## Dependencies and Integration Points
It must match the driver name registered by `nfsplugin:v4.6.0` and the storage classes used by workloads. It integrates with the node DaemonSet's registrar and controller-side provisioner.

## Risks and Test Signals
Risks are driver-name mismatch, unsupported fsGroup policy on older clusters, and mismatched assumptions about NFS permissions. Test signals are a present `CSIDriver`, no attach objects for NFS volumes, matching `CSINode` entries, and successful pod mounts with fsGroup.
