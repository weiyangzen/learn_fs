# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object that advertises the NFS CSI driver to Kubernetes.

## APIs, Control Flow, and State
The object name is `driver.name`, normally `nfs.csi.k8s.io`. It declares `attachRequired: false`, which tells Kubernetes no attach/detach controller operation is required for NFS volumes. It always lists `Persistent` in `volumeLifecycleModes`, optionally adds `Ephemeral` when `feature.enableInlineVolume` is true, and sets `fsGroupPolicy: File` when `feature.enableFSGroupPolicy` is true.

## Dependencies and Integration Points
The CSIDriver object must match the `--drivername` argument used by both controller and node NFS containers and the `provisioner` field in generated StorageClasses. Kubelet and CSI sidecars use it for capability discovery and volume lifecycle decisions.

## Risks and Test Signals
A driver name mismatch prevents provisioning and node registration from lining up. Enabling inline ephemeral volumes changes Kubernetes admission and kubelet behavior. Test by rendering values combinations, checking `kubectl get csidriver nfs.csi.k8s.io`, and verifying pod mounts with FSGroup-sensitive workloads.
