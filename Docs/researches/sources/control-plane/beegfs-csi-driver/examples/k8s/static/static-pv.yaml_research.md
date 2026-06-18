<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml

Purpose: standalone static read/write BeeGFS PV.

Important APIs and flow: declares `ReadWriteMany`, `100Gi`, `Retain`, driver `beegfs.csi.netapp.com`, and `volumeHandle: beegfs://localhost/k8s/all/static`.

State and persistence: points at an existing BeeGFS directory; Kubernetes retains the PV and does not create the directory.

Dependencies and integration points: binds to `static-pvc.yaml`; depends on management host replacement and BeeGFS path existence.

Risks and test signals: static path mismatch causes mount failures, while `Retain` can leave stale claims/data for later runs. Test bind and Pod write/read.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml -->
