<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml

Purpose: statically provisioned read-only BeeGFS PersistentVolume for the combined example.

Important APIs and flow: declares `ReadOnlyMany`, placeholder capacity `5Gi`, `Retain`, and CSI `volumeHandle: beegfs://localhost/k8s/all/static-ro`. Comments clarify capacity is required for binding but not meaningful for read-only static usage.

State and persistence: does not create or delete the BeeGFS directory; Kubernetes retains the PV.

Dependencies and integration points: binds to `static-ro-pvc.yaml` and is mounted read-only by the Pod claim reference.

Risks and test signals: accessModes alone do not enforce read-only at mount time; the Pod volume reference must set `readOnly: true`. Test by attempting a write and expecting failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml -->
