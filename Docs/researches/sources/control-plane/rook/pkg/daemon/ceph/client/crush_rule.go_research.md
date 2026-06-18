# sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule.go

Purpose: builds CRUSH rules used by stretch-cluster and two-step replicated placement workflows, and retrieves named CRUSH rule JSON from Ceph.

Important APIs: `buildTwoStepPlainCrushRule()` and `buildTwoStepHybridCrushRule()` render textual CRUSH rule snippets with generated rule IDs, root, failure domain, sub-failure domain, and optional device class/hybrid storage classes. `buildTwoStepCrushRule()` returns a structured `ruleSpec` equivalent. `buildTwoStepCrushSteps()` creates `take`, `chooseleaf_firstn`, and `emit` steps. `generateRuleID()` and `checkIfRuleIDExists()` choose an unused rule ID. `getCrushRule()` runs `ceph osd crush rule dump <name>` and unmarshals a `ruleSpec`.

Control flow and state: rule construction is pure except for using the passed `CrushMap.Rules` as the existing ID set. `generateRuleID()` starts from the last rule's ID plus one and increments until unused, so it assumes the rules slice is non-empty and that the last rule is a reasonable starting point. `getCrushRule()` reads cluster state only.

Dependencies and integration: depends on `cephv1.PoolSpec` fields such as `CrushRoot`, `FailureDomain`, `DeviceClass`, `Replicated.ReplicasPerFailureDomain`, `SubFailureDomain`, and `HybridStorage`. `mon.go` uses rule generation for default stretch rules through related helpers. Risks include panic on empty rule lists, text-template drift from Ceph CRUSH syntax, and subtle differences between plain and structured rule construction. Tests cover step construction, ID generation with ordered/unordered rules, and compile/decompile/inject/set helpers in adjacent files.
