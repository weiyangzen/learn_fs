<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/pod_with_pvc.yaml

Purpose: basic pod plus PVC example for a Longhorn filesystem volume.

Important APIs/types/functions: PVC `longhorn-volv-pvc` requests 2Gi RWO storage from `longhorn`; pod `volume-test` mounts it at `/data` and probes `/data/lost+found`.

Control flow: Longhorn provisions the PVC, Kubernetes schedules the pod, attaches/mounts the volume, and the liveness probe verifies mount presence.

State and persistence: filesystem data persists in the PVC across pod restarts/deletion.

Dependencies/integration points: depends on Longhorn StorageClass and kubelet CSI mount.

Risks/test signals: liveness only checks filesystem scaffold, not application IO. Test signals are PVC bound, pod running, data write/read after pod recreation, and volume detach on pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_pvc.yaml -->
