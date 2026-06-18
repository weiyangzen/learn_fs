<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml

## Purpose
This manifest defines the Kubernetes `CSIDriver` object for BeeGFS CSI.

## Important Objects and Fields
The `CSIDriver` name is `beegfs.csi.netapp.com`. `attachRequired: false` indicates the driver does not require controller publish/attach operations. `fsGroupPolicy: None` declares no Kubernetes fsGroup ownership management. `volumeLifecycleModes` lists `Persistent`.

## Control Flow
The object informs Kubernetes storage behavior rather than running containers. Kubelet and controller components use it to understand attach and lifecycle capabilities for the driver name.

## State and Persistence
The object is persisted in the Kubernetes API server. It has no local filesystem state.

## Dependencies and Integration Points
It is included in base Kustomize resources and embedded in Go via `deploy.go` for operator deployments. Comments mention version overlays may remove `fsGroupPolicy` for Kubernetes 1.18 validation compatibility.

## Risks
Changing the driver name breaks StorageClass/PV references and sidecar registration expectations. Keeping `fsGroupPolicy` in versions that reject the field requires correct version-specific Kustomize patches.

## Test Signals
Signals include strict unmarshal through `GetCSIDriver()`, `kubectl apply` against supported Kubernetes versions, CSI node registration, and successful persistent volume lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml -->
