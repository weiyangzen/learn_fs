# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.5.0 bundle's CSI driver identity. It is the same `CSIDriver` definition used in adjacent releases.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io` with `attachRequired: false`, persistent lifecycle support, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The `CSIDriver` persists cluster-wide and changes Kubernetes volume behavior by suppressing attach/detach and advertising fsGroup handling. There is no executable flow in the YAML.

## Dependencies and Integration Points
It must match the driver name returned by `nfsplugin:v4.5.0`, the kubelet registration path in `csi-nfs-node.yaml`, and storage classes referencing `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks are name drift, unsupported cluster versions, and fsGroup behavior not matching export permissions. Test signals include a present `CSIDriver`, no VolumeAttachment creation for NFS PVs, successful node registration, and pods mounting NFS PVCs under the expected group ownership.
