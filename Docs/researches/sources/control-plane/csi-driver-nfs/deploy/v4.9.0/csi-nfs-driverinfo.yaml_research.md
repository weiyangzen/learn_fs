<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml

## Purpose
Declares cluster-level CSI driver metadata for `nfs.csi.k8s.io` in the v4.9.0 manifest set.

## Important APIs, Types, and Functions
The file defines a `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, persistent lifecycle mode only, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
Kubernetes control-plane and kubelet components read this object to skip attach workflows and apply fsGroup semantics for mounted files where supported. The object persists as cluster configuration.

## Dependencies and Integration Points
It must match the driver name registered by the node DaemonSet and returned by CSI identity. It integrates with PV provisioning, pod volume setup, and security context fsGroup handling.

## Risks and Test Signals
Risks include name mismatch, lack of ephemeral lifecycle declaration, and fsGroup behavior depending on NFS server permissions. Signals include the `CSIDriver` object existing, no attach attempts for NFS PVs, and successful pod volume setup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml -->
