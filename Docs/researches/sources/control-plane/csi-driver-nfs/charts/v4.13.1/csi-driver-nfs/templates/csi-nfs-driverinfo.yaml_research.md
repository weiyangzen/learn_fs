# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template declares the cluster `CSIDriver` object for the NFS CSI driver. It tells Kubernetes how the driver participates in attachment, volume lifecycle modes, and filesystem group ownership handling.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` with `metadata.name` from `.Values.driver.name`, `attachRequired: false`, and `volumeLifecycleModes` containing `Persistent` plus optional `Ephemeral` when `feature.enableInlineVolume` is true. `fsGroupPolicy: File` is conditionally emitted when `feature.enableFSGroupPolicy` is true.

## Control Flow, State, and Persistence
The manifest is unconditional. It persists as cluster-scoped driver metadata and is reconciled by Kubernetes storage components and kubelet plugin registration. There is no pod-local state, but changes affect how future pods and PVCs interact with the driver.

## Dependencies and Integration Points
It must match the `--drivername` passed to controller and node `nfsplugin` containers and the `provisioner` field in generated `StorageClass` objects. Kubelet registration from the node DaemonSet should advertise the same CSI driver name.

## Risks and Test Signals
Risks are driver-name drift, enabling inline ephemeral volume mode without testing node behavior, and changing `fsGroupPolicy` in a way that affects workload permissions. Signals include `kubectl get csidriver nfs.csi.k8s.io -o yaml`, node plugin registration success, PVC mount tests with `fsGroup`, and optional inline CSI pod volume tests.
