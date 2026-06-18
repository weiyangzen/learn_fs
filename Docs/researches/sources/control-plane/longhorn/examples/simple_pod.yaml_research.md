<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pod.yaml -->
# sources/control-plane/longhorn/examples/simple_pod.yaml

Purpose: simple consumer pod for the companion Longhorn PVC example.

Important APIs/types/functions: Pod `longhorn-simple-pod` mounts PVC `longhorn-simple-pvc` at `/data`, uses nginx stable-alpine, and probes `/data/lost+found`.

Control flow: once the PVC exists and is bound, kubelet attaches/mounts it into the pod and liveness checks the mounted filesystem.

State and persistence: data persists in `longhorn-simple-pvc`.

Dependencies/integration points: depends on companion PVC, Longhorn CSI, and default namespace.

Risks/test signals: pod fails until PVC exists; probe is mount-only. Test signals are PVC binding, pod running, mount path visibility, and persistence after pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pod.yaml -->
