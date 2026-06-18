<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml

Purpose: standalone demo Pod for Kubernetes generic ephemeral BeeGFS volumes.

Important APIs and flow: Alpine Pod defines an `ephemeral.volumeClaimTemplate` requesting `ReadWriteMany`, `100Gi`, and `storageClassName: csi-beegfs-ge-sc`. The container writes a UID marker under `/mnt/ge` and sleeps.

State and persistence: Kubernetes creates an owner-linked PVC/PV for the Pod; BeeGFS backing storage should be deleted with the ephemeral volume lifecycle.

Dependencies and integration points: depends on generic ephemeral volume support, the `ge-sc.yaml` StorageClass, CSI provisioner, and node driver.

Risks and test signals: cleanup correctness is the key behavior. Test by creating/deleting the Pod and confirming generated PVC/PV and BeeGFS directory lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml -->
