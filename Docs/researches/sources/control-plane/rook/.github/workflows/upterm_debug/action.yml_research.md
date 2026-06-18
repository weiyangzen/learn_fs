# sources/control-plane/rook/.github/workflows/upterm_debug/action.yml

## Purpose

Composite action that conditionally starts an upterm SSH debugging session near job completion.

## Important APIs, Types, and Functions

Input `debug-ci` enables the action when runner debug or the PR label is true and the repository owner is `rook` or the run attempt is greater than one. It uses `owenthereal/action-upterm` with `limit-access-to-actor: false` and a five-minute wait timeout.

## Control Flow

Callers invoke this as a post-job step. The first step exports `ENABLE_UPTERM`, and the second starts the session if that env var is set.

## State and Persistence Behavior

It only affects the live runner by opening an interactive session. No repository state is written.

## Dependencies and Integration Points

It integrates with PR labels, runner debug, reruns, GitHub repository owner metadata, and canary/integration workflows.

## Risks and Edge Cases

Because detached mode is not implemented and access is not actor-limited, this action is security-sensitive and can hold jobs for interactive access until timeout.

## Test Signals

When enabled, logs show an upterm session; otherwise the action is skipped.
