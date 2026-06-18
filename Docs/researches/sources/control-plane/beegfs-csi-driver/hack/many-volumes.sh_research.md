<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh -->
# sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh

Purpose: manual stress-manifest generator for flooding Kubernetes and the BeeGFS CSI controller with many dynamic PVCs.

Important APIs and flow: defines `NUM_PVCS=100` and `SYS_MGMTD_HOST`, writes `many-volumes.yaml` with one StorageClass and a loop-generated series of PVCs named `many-volumes-pvc-N`. The StorageClass uses `permissions/mode: "1644"` to force a mount and slow the driver.

State and persistence: writes a local generated YAML file and, when applied, creates many PVC/PV objects and BeeGFS directories under `k8s/many-volumes`.

Dependencies and integration points: depends on kubectl apply/delete by the operator, BeeGFS CSI dynamic provisioning, and a reachable management host.

Risks and test signals: no cleanup trap and hard-coded output name can overwrite prior manifests. Test by applying/deleting the manifest and watching controller logs for concurrency behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh -->
