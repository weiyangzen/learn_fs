<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart.go -->
# sources/cloud-native/containerd/core/runtime/restart/restart.go

## Purpose
Defines restart policy labels, policy parsing, reconciliation rules, and container option helpers used by the restart monitor.

## Important APIs, Types, And Functions
- Labels: `StatusLabel`, `LogURILabel`, `PolicyLabel`, `CountLabel`, and `ExplicitlyStoppedLabel`.
- `Policy` stores policy name and maximum retry count.
- `NewPolicy` parses `no`, `always`, `on-failure[:max-retries]`, and `unless-stopped`, defaulting empty policy to `always`.
- `Reconcile(status, labels)` decides whether a task should be restarted.
- `WithLogURI`, `WithLogURIString`, `WithStatus`, `WithPolicy`, and `WithNoRestarts` mutate container labels.
- `ensureLabels` initializes `containers.Container.Labels`.

## Control Flow
`NewPolicy` splits the policy on `:` and validates which policies may have a retry suffix. `Reconcile` parses the configured policy and applies policy-specific rules: `always` restarts, `on-failure` restarts only for non-zero exits and below retry limit, and `unless-stopped` restarts unless explicitly stopped. Option helpers are returned as functions compatible with container creation/update option patterns.

## State And Persistence
Desired restart state is persisted in container labels. The code itself holds no process-global state.

## Dependencies And Integration Points
Integrates with the containerd client status model, container metadata, and restart monitor plugin. Log URI labels affect task IO setup in restart-managed tasks.

## Risks And Edge Cases
Invalid policies or invalid restart counts log errors and suppress restarts. `WithNoRestarts` removes status, policy, and log URI labels but does not remove count or explicitly-stopped labels, leaving historical metadata.

## Test Signals
`restart_test.go` covers policy parsing, string formatting, and reconciliation outcomes for always, on-failure with counts, invalid counts, and unless-stopped explicit stops.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart.go -->
