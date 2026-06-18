# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement_test.go

Purpose: tests Kubernetes scheduling placement parsing, merging, and application behavior for Rook Ceph API placement helpers.

Important APIs/types/functions: exercises `Placement`, `PlacementSpec`, `Placement.ApplyToPodSpec`, `Placement.mergeNodeAffinity`, `Placement.Merge`, `Placement.mergeTolerations`, and helper fixtures `placementTestGetTolerations`, `placementTestGetTopologySpreadConstraints`, `placementAntiAffinity`, and `placementTestGenerateNodeAffinity`.

Control flow: `TestPlacementSpec` converts YAML to JSON and verifies a typed `Placement` with node affinity, tolerations, and topology spread constraints. `TestMergeNodeAffinity` covers nil existing affinity, existing preferred affinity without required selector, and merging required selector expressions. `TestPlacementApplyToPodSpec` applies full and partial placements to pod specs, verifies topology replacement, preferred-affinity merging, anti-affinity deep copy behavior, and toleration append order. `TestPlacementMerge` covers overlaying tolerations, node affinity, and topology constraints. `TestMergeToleration` validates nil and non-nil toleration merging.

State and persistence: test-only local scheduling structs; no persistence or external Kubernetes API calls.

Dependencies/integration: depends on testify, Kubernetes core `v1`, `metav1.LabelSelector`, and Kubernetes YAML conversion. Tests protect the scheduling contract used by multiple Rook Ceph daemons.

Risks: expected values encode current merge limitations, such as first-term required affinity merging and no toleration deduplication. Tests check anti-affinity deep-copy behavior but do not similarly protect topology spread constraints from aliasing.

Test signals: strong coverage for placement helper edge cases and merge order. Daemon-specific getter functions are not directly tested in this file.
