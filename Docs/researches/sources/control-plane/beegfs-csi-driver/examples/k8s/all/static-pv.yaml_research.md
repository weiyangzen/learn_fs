<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml

Purpose: statically provisioned read/write BeeGFS PersistentVolume for the combined examples.

Important APIs and flow: declares a `PersistentVolume` with `ReadWriteMany`, `100Gi`, `Retain`, and a CSI source using driver `beegfs.csi.netapp.com`. The `volumeHandle` encodes BeeGFS management host and path as `beegfs://localhost/k8s/all/static`.

State and persistence: Kubernetes retains the PV and BeeGFS directory after PVC deletion. The driver does not create the target directory for static volumes.

Dependencies and integration points: binds to `static-pvc.yaml` by `volumeName`; depends on pre-existing BeeGFS directory and a valid management host.

Risks and test signals: stale or missing directories cause mount failure. Test PV/PVC binding and Pod write/read of marker files.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml -->
