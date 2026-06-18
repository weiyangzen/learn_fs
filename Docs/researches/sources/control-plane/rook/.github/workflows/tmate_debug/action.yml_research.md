# sources/control-plane/rook/.github/workflows/tmate_debug/action.yml

## Purpose

Composite action that conditionally starts a detached tmate SSH session for CI debugging.

## Important APIs, Types, and Functions

Inputs are required `use-tmate` and optional `debug-ci`. The first step sets `ENABLE_TMATE=1` when runner debug or `debug-ci` is true and the repository owner is `rook`, `use-tmate` is non-empty, or the run attempt is greater than one. The second step uses `mxschmitt/action-tmate` with `detached: true`.

## Control Flow

Callers place this near the beginning of a job. If conditions are met, environment state is exported and the tmate action starts an SSH session.

## State and Persistence Behavior

It writes `ENABLE_TMATE` to `$GITHUB_ENV` and creates an external interactive SSH session for the live job only.

## Dependencies and Integration Points

It integrates with runner debug mode, PR `debug-ci` labels, repository secrets, GitHub run attempt metadata, and many integration/canary workflows.

## Risks and Edge Cases

`limit-access-to-actor: false` allows broader access than actor-only sessions. This is intentionally powerful and must stay gated by repository/secret/rerun conditions.

## Test Signals

When enabled, logs should show a detached tmate connection string; otherwise the action should be a no-op.
