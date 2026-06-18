<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml

Purpose: standalone dynamic BeeGFS PVC.

Important APIs and flow: requests `ReadWriteMany`, `100Gi`, and `storageClassName: csi-beegfs-dyn-sc`, causing the external CSI provisioner to call `CreateVolume`.

State and persistence: Kubernetes stores PVC/PV state; BeeGFS stores the provisioned directory under the StorageClass base path.

Dependencies and integration points: requires the dynamic StorageClass and a running BeeGFS CSI controller.

Risks and test signals: capacity is a Kubernetes request and may not reflect real BeeGFS quota. Test `Bound` phase, PV CSI volume handle, and Pod write.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml -->
