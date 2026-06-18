# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement.go

Purpose: provides placement merging and application helpers that map Rook `PlacementSpec` CRD fields into Kubernetes `PodSpec` scheduling fields for Ceph daemons.

Important APIs/types/functions: `PlacementSpec.All`, `Placement.ApplyToPodSpec`, `Placement.mergeNodeAffinity`, `Placement.mergeTolerations`, `Placement.Merge`, `GetMgrPlacement`, `GetMonPlacement`, `GetArbiterPlacement`, and `GetOSDPlacement`.

Control flow: `ApplyToPodSpec` ensures `PodSpec.Affinity` exists, then applies placement fields. Node affinity is merged with any existing pod node affinity; pod affinity and anti-affinity are deep-copied and overwrite existing values; tolerations are prepended/merged; topology spread constraints replace the pod's existing constraints. `mergeNodeAffinity` starts from a deep copy of placement affinity, appends preferred terms from existing and placement affinities, and for required node selectors merges only the first selector term's match expressions and fields when both sides have required terms. `Merge` overlays a more specific placement onto a base placement, with specific affinity and topology fields replacing base fields and tolerations merged. Daemon-specific getters merge `all` with mgr, mon, or osd placement; arbiter deliberately returns only the arbiter placement without `all`.

State and persistence: no persistence. Methods return or mutate in-memory Kubernetes scheduling structs. `ApplyToPodSpec` mutates the provided pod spec.

Dependencies/integration: depends on Kubernetes core `v1` scheduling types. This logic is used by Rook reconcilers when creating deployments, jobs, daemonsets, and pods for Ceph components.

Risks: required node affinity merging only considers the first `NodeSelectorTerm`, which cannot represent all Kubernetes OR/AND combinations. `mergeTolerations` appends existing tolerations after placement tolerations without deduplication. `ApplyToPodSpec` assigns topology spread constraints directly rather than deep-copying. `Merge` starts with a shallow copy, so pointer fields may alias original placement structs.

Test signals: `placement_test.go` covers YAML unmarshalling, node-affinity merge variants, pod-spec application, deep copy of anti-affinity, toleration ordering, topology replacement, and daemon-independent merge behavior.
