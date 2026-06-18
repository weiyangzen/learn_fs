# sources/control-plane/rook/pkg/util/dependents/dependents.go

## Purpose
`dependents.go` models resources that block deletion and builds standard Ceph CR status conditions for blocked deletion scenarios.

## Important APIs, Types, and Functions
Condition builders are `DeletionBlockedDueToDependentsCondition()`, `DeletionBlockedDueToNonEmptyPoolCondition()`, and `DeletionBlockedDueToNonEmptyRadosNSCondition()`. `DependentList` stores plural resource kinds to dependent names. Methods include `NewDependentList()`, `Empty()`, `Add()`, `PluralKinds()`, `OfKind()`, and `StringWithHeader()`.

## Control Flow, State, and Persistence
Conditions are returned in memory for callers to persist to CR status. `DependentList` stores state in a map. `StringWithHeader()` sorts formatted kind groups alphabetically for deterministic messages.

## Dependencies and Integration Points
It depends on Rook Ceph condition constants and Kubernetes core condition statuses. Reconciler code can use it to report deletion blockers on Ceph resources.

## Risks
Dependent names are not deduplicated or sorted within a kind. `PluralKinds()` returns map iteration order, so callers should not rely on ordering. Condition timestamps are not set here.

## Test Signals
`dependents_test.go` covers empty, single-kind, multi-dependent, multi-kind, missing-kind, string formatting, and alphabetical kind ordering. Condition builders are not directly tested.
