<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/sample.sh -->
# sources/control-plane/longhorn/dev/scale-test/sample.sh

Purpose: simple scale helper that scales all StatefulSets to a per-node replica count and waits until a requested number of pods report ready.

Important APIs/types/functions: shell variables `requested`, `node_count`, `required_scale`; `kubectl scale --replicas=<required_scale> statefulset --all`; readiness counting via `kubectl get pods ... containerStatuses[*].ready | grep -c true`.

Control flow: computes `requested / node_count`, logs initial ready count, scales all StatefulSets in the current namespace/context, then polls every 60 seconds until ready count equals the requested total.

State and persistence: mutates live Kubernetes StatefulSet replica counts. It persists no local state.

Dependencies/integration points: depends on `kubectl`, current kube context, shell arithmetic, and pod readiness fields. It is intended to pair with generated scale-test StatefulSets.

Risks/test signals: integer division can under-scale, `grep -c true` can miscount multi-container pods, and `statefulset --all` is broad. Test signals are dry-run/manual namespace scoping, observed replica counts, and readiness convergence for generated workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scale-test/sample.sh -->
