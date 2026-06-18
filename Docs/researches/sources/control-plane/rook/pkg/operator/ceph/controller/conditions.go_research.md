# sources/control-plane/rook/pkg/operator/ceph/controller/conditions.go

## Purpose
`conditions.go` centralizes CephCluster condition and phase updates, including backward-compatible translation from newer condition phases to the older `Status.State` values.

## Important APIs, Types, and Functions
`UpdateCondition()` fetches a `CephCluster` from the controller-runtime client and delegates to `UpdateClusterCondition()`. `UpdateClusterCondition()` filters existing conditions, updates or creates the requested condition, refreshes heartbeat/transition times, sets observed generation for Ready conditions, updates phase/state/message, and persists status through `reporting.UpdateStatus()`. `translatePhasetoState()` maps `Connecting`, `Connected`, `Progressing`, `Ready`, and `Deleting` to legacy cluster states, returning `Error` for false conditions.

## Control Flow, State, and Persistence
Condition updates are persisted to the CephCluster status subresource via the reporting helper. Long-term conditions such as created/connected and deletion-related conditions are preserved; transient conditions are discarded unless `preserveAllConditions` is true. Once phase is `Deleting`, later updates do not revert phase/message/state.

## Dependencies and Integration Points
The file depends on `clusterd.Context.Client`, Ceph API status types, Kubernetes condition timestamps, `k8sutil.ObservedGenerationNotAvailable`, and `pkg/operator/ceph/reporting`. All controllers that report cluster progress or health use this behavior indirectly.

## Risks
Status update errors are logged but not returned, so callers cannot requeue directly from failure. Time comparisons in tests can be difficult because timestamps are generated inline. The retention rules can drop transient conditions unexpectedly if callers do not pass `preserveAllConditions`. The phase lock on Deleting is intentional but means later recovery-like messages will not surface in `Status.Phase`.

## Test Signals
No direct test file is included for this source in the subset. Useful coverage would assert condition retention, transition-time changes only on status/message changes, observed generation updates only for Ready, Deleting phase stickiness, and reporting failure behavior.
