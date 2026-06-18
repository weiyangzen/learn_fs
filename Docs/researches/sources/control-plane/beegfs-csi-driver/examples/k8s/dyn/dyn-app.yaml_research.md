<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml

Purpose: standalone demo Pod for a dynamically provisioned BeeGFS volume.

Important APIs and flow: Alpine Pod mounts PVC `csi-beegfs-dyn-pvc` at `/mnt/dyn`, writes a marker file named with `metadata.uid`, and sleeps for seven days. Optional OpenShift nodeSelector comments guide scheduling onto RHEL nodes when the driver is not installed on RHCOS.

State and persistence: marker file persists in the dynamically provisioned BeeGFS directory until reclaim cleanup. Pod runtime is transient.

Dependencies and integration points: depends on `dyn-pvc.yaml`, `dyn-sc.yaml`, the CSI node plugin, and BeeGFS client availability on the selected node.

Risks and test signals: placeholder StorageClass parameters must be fixed. Test with `kubectl exec csi-beegfs-dyn-app -- ls /mnt/dyn` and PVC/PV events.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml -->
