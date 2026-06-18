<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart_test.go -->
# sources/cloud-native/containerd/core/runtime/restart/restart_test.go

## Purpose
Tests restart policy parsing, rendering, and restart decision logic.

## Important APIs, Types, And Functions
- `TestNewRestartPolicy` validates supported and unsupported policy strings.
- `TestRestartPolicyToString` validates round-trip string formatting.
- `TestRestartPolicyReconcile` validates restart decisions from process status and labels.

## Control Flow
The tests are table-driven. Parsing tests compare returned `Policy` structs. Reconcile tests pass `containerd.Status` and labels to `Reconcile` and compare booleans.

## State And Persistence
No persistent state; labels are in-memory maps.

## Dependencies And Integration Points
Uses the public `containerd.Status` type and restart label constants. Protects behavior consumed by the restart monitor.

## Risks And Edge Cases
Tests capture that empty policy means always, `always` cannot have retry count, `on-failure` needs non-zero exit status, invalid count suppresses restart, and `unless-stopped` respects explicit stop.

## Test Signals
Focused unit coverage for restart policy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart_test.go -->
