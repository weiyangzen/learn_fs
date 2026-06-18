# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.7.0 NFS CSI driver with Kubernetes. It is the same `CSIDriver` manifest used in the earlier release directories in this subset.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io`. It declares no attach requirement, persistent lifecycle support, and file-based fsGroup policy.

## Control Flow, State, and Persistence
The `CSIDriver` is persistent cluster metadata consulted by Kubernetes and kubelet during volume admission, scheduling, and mount handling. It does not execute logic, but it changes the control-plane path by avoiding attach/detach for NFS volumes.

## Dependencies and Integration Points
It must match the v4.7.0 node plugin registration and storage class provisioner name. It integrates with `csi-nfs-controller.yaml`, `csi-nfs-node.yaml` from the same release, and user workloads consuming NFS PVCs.

## Risks and Test Signals
Risks include name mismatches during upgrades, old clusters lacking the selected `fsGroupPolicy` behavior, and NFS export permissions conflicting with fsGroup expectations. Test signals are a present `CSIDriver`, matching `CSINode` registrations, no VolumeAttachment resources for NFS PVs, and successful pod mount tests using a v4.7.0 provisioned PVC.
