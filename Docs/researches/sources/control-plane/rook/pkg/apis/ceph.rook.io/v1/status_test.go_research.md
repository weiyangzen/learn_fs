# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status_test.go

Purpose: tests shared condition list update and lookup behavior.

Important APIs/types/functions: exercises `SetStatusCondition` and `FindStatusCondition` with `Condition`, `ConditionType`, Kubernetes condition statuses, and `metav1.Time`.

Control flow: `TestSetStatusCondition` constructs table cases for appending a new condition, updating an existing condition with a status change using supplied transition/heartbeat times, updating reason/message/heartbeat without changing transition time when status is unchanged, and appending to an empty list. It compares whole slices with `reflect.DeepEqual`. `TestFindStatusCondition` checks absent and present condition-type lookup.

State and persistence: test-only local slices; no persistence.

Dependencies/integration: depends on standard `reflect`, `testing`, `time`, and Kubernetes core/metav1 types. The cases are modeled after Kubernetes apimachinery condition behavior.

Risks: tests avoid cases where callers omit timestamps and `SetStatusCondition` uses current time, because those are harder to compare deterministically. Nil `conditions` pointer behavior is not tested. New-condition append with supplied transition but missing heartbeat is not tested.

Test signals: solid deterministic coverage for key condition update semantics and lookup.
