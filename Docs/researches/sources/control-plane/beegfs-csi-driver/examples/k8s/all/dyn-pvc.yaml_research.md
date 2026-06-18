<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml

Purpose: demo PersistentVolumeClaim for dynamically provisioned BeeGFS storage in the combined example.

Important APIs and flow: requests `ReadWriteMany` access and `100Gi` storage from `storageClassName: csi-beegfs-dyn-sc`. Kubernetes binds it through the BeeGFS CSI provisioner.

State and persistence: persists as a PVC and, after provisioning, a dynamically created PV and BeeGFS directory under the StorageClass base path.

Dependencies and integration points: depends on `dyn-sc.yaml`, the CSI external provisioner, and BeeGFS management connectivity.

Risks and test signals: requested capacity is mostly a Kubernetes binding signal for BeeGFS and not an enforced quota in this manifest. Test PVC binding, PV creation, and successful Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml -->
