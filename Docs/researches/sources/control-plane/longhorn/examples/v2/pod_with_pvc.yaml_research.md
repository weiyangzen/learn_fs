<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml -->
# sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml

Purpose: pod plus PVC example using Longhorn v2 data engine StorageClass.

Important APIs/types/functions: PVC `longhorn-volv-pvc` requests 2Gi from `longhorn-v2-data-engine`; pod `volume-test` mounts it at `/data` and probes `/data/lost+found`.

Control flow: Longhorn provisions a v2 data engine volume, Kubernetes attaches/mounts it, and the pod validates mount presence through liveness.

State and persistence: data persists in the v2 Longhorn volume.

Dependencies/integration points: depends on v2 data engine being enabled/supported on the cluster, v2 StorageClass, and node prerequisites.

Risks/test signals: v2 data engine has different node/kernel/SPDK-style prerequisites than v1. Test signals are PVC Bound, Longhorn Volume `dataEngine: v2`, attach/mount success, and workload IO.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/pod_with_pvc.yaml -->
