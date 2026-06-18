<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/statefulset.yaml -->
# sources/control-plane/longhorn/examples/statefulset.yaml

Purpose: StatefulSet example where each nginx replica gets its own Longhorn PVC.

Important APIs/types/functions: NodePort Service `nginx`, StatefulSet `web` with two replicas, `registry.k8s.io/nginx-slim:0.8`, liveness probe on mounted path, and `volumeClaimTemplates` requesting 1Gi RWO Longhorn volumes.

Control flow: StatefulSet controller creates stable pod identities and per-replica PVCs; Longhorn provisions and attaches each volume.

State and persistence: each replica's web data persists in its own PVC.

Dependencies/integration points: depends on Longhorn StorageClass, StatefulSet volume claim templates, and NodePort service exposure.

Risks/test signals: old image and NodePort exposure are example-only. Test signals are two PVCs bound, ordered pod startup, volume persistence per ordinal, and service reachability.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/statefulset.yaml -->
