<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/statefulset.yaml -->
# sources/control-plane/longhorn/dev/scale-test/statefulset.yaml

Purpose: template for scale-test StatefulSets, using placeholders to create one Longhorn-backed volume workload per target node.

Important APIs/types/functions: `apps/v1` `StatefulSet` with placeholders `@STS_NAME@` and `@NODE_NAME@`, node pinning via `spec.template.spec.nodeName`, BusyBox container, liveness probe on mounted path, and `volumeClaimTemplates` using StorageClass `longhorn`.

Control flow: `scale-test.py` substitutes placeholders into generated YAML. Replicas start at 0; `sample.sh` or manual scaling drives volume creation and attachment.

State and persistence: each generated StatefulSet creates a 1Gi RWO PVC per replica through Longhorn; pods write only probe-visible mount state.

Dependencies/integration points: depends on Longhorn default StorageClass, node names matching the configured prefix, StatefulSet controller, and kubelet volume attach/mount.

Risks/test signals: hard node pinning fails if node names differ, `busybox:latest` is mutable, and the liveness probe assumes mounted filesystem accessibility. Test signals are generated YAML validation, PVC creation, pod scheduling, Longhorn attach latency, and liveness stability.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/statefulset.yaml -->
