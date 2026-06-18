<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml

Purpose: standalone static read-only BeeGFS PV.

Important APIs and flow: declares `ReadOnlyMany`, required capacity `5Gi`, `Retain`, driver `beegfs.csi.netapp.com`, and `volumeHandle: beegfs://localhost/k8s/all/static-ro`.

State and persistence: uses an existing BeeGFS directory and does not delete it through Kubernetes.

Dependencies and integration points: binds to `static-ro-pvc.yaml`; mount semantics are completed by the Pod's `readOnly: true`.

Risks and test signals: wrong management host/path or missing directory prevents staging. Test bind, mount, read, and write rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml -->
