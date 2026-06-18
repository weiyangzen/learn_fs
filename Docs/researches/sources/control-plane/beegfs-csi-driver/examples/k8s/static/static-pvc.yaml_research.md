<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml

Purpose: standalone PVC binding to the static read/write BeeGFS PV.

Important APIs and flow: requests `ReadWriteMany`, `100Gi`, disables dynamic provisioning with an empty StorageClass, and pins `volumeName: csi-beegfs-static-pv`.

State and persistence: holds Kubernetes binding state; underlying BeeGFS storage remains external and retained.

Dependencies and integration points: requires the named PV to exist with compatible access modes and capacity.

Risks and test signals: missing empty `storageClassName` could select a default StorageClass unexpectedly. Test PVC `Bound` phase and Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml -->
