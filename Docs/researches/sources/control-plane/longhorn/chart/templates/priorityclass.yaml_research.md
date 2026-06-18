# sources/control-plane/longhorn/chart/templates/priorityclass.yaml

Purpose: creates the `longhorn-critical` PriorityClass used by Longhorn workloads to reduce eviction risk under node pressure.

Important APIs/types/functions: Kubernetes `scheduling.k8s.io/v1` `PriorityClass`, `globalDefault: false`, `preemptionPolicy: PreemptLowerPriority`, value `1000000000`, chart labels, and the name referenced from `values.yaml` via the `defaultSettings.priorityClass` anchor and component priority defaults.

Control flow: the template always renders one PriorityClass with a fixed name and high numeric priority.

State and persistence: PriorityClass is cluster-scoped persistent scheduling policy. Deleting or renaming it affects pods that reference `longhorn-critical`.

Dependencies/integration: component templates such as UI, driver, and hook jobs conditionally set `priorityClassName` from values that default to this name. Longhorn default settings can also propagate priority to system-managed components.

Risks: very high priority with preemption can evict lower-priority workloads to preserve Longhorn availability. Name collisions occur if multiple releases install the same chart into one cluster. Cluster-scoped resource ownership can be awkward for namespace-scoped Helm releases.

Test signals: render and install into clusters with and without existing `longhorn-critical`; confirm pods using default priorities schedule; test uninstall/upgrade ownership behavior for the cluster-scoped object.
