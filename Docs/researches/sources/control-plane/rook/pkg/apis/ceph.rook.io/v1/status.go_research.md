# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status.go

Purpose: provides shared condition-list helpers for Rook Ceph CRD status fields.

Important APIs/types/functions: `SetStatusCondition(conditions *[]Condition, newCondition Condition)` and `FindStatusCondition(conditions []Condition, conditionType ConditionType) *Condition`.

Control flow: `SetStatusCondition` is nil-pointer safe and returns immediately when the conditions pointer is nil. It captures `now`, finds an existing condition of the same type, and either appends a new condition or updates the existing one. New conditions get `LastTransitionTime` and `LastHeartbeatTime` set to now when the supplied transition time is zero. Existing conditions update status and transition time only when status changes; transition time uses the supplied value if non-zero, otherwise now. Reason and message are always updated. Heartbeat time uses the supplied value if non-zero, otherwise now. `FindStatusCondition` linearly scans and returns a pointer to the matching slice element.

State and persistence: mutates the provided in-memory condition slice. No direct persistence, but callers later persist status through Kubernetes status updates.

Dependencies/integration: depends on `time` and Kubernetes `metav1.Time`. Status accessors in other files return condition pointers intended for this helper.

Risks: returned pointers from `FindStatusCondition` point into the provided slice and can become stale after slice reallocation. `SetStatusCondition` preserves transition time when status is unchanged even if a new transition time is supplied. New-condition logic sets heartbeat only when transition time is zero; if the caller supplies a transition time but no heartbeat, heartbeat remains zero on append.

Test signals: `status_test.go` is based on Kubernetes condition helper tests and covers append, status-change transition update, same-status field update, empty lists, and find present/absent.
