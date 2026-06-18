# sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent and Ephemeral; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
