<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml

## Purpose
Registers cluster-level metadata for the NFS CSI driver using a `CSIDriver` object.

## Important APIs, Types, and Functions
The `storage.k8s.io/v1` `CSIDriver` is named `nfs.csi.k8s.io`, sets `attachRequired: false`, declares `volumeLifecycleModes: [Persistent]`, and sets `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The object is read by Kubernetes storage components to decide attach behavior and fsGroup handling. Because NFS does not need a block-device attach phase, the attach/detach controller can skip controller publish flows.

## Dependencies and Integration Points
It integrates with kubelet, external provisioner behavior, pod security context fsGroup application, and the driver name returned by CSI identity APIs.

## Risks and Test Signals
Risks include driver name mismatch, unsupported lifecycle modes for ephemeral use, and fsGroup behavior surprises on NFS permissions. Signals are discovery of the `CSIDriver` object, PVs referencing the same driver name, and pod volume setup without attach operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml -->
