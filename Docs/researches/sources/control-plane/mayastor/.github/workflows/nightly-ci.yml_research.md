# sources/control-plane/mayastor/.github/workflows/nightly-ci.yml

## Purpose
Manual wrapper that runs the standard PR CI as a nightly-style check.

## Important Jobs and Steps
Workflow has `ci` job using `./.github/workflows/pr-ci.yml`, then `nightly-ci` job that depends on it and exits zero if successful.

## Control Flow
Triggered by `workflow_dispatch`. The second job is gated by `if: success()` and `needs: ci`.

## State and Persistence
No repo state. It creates whatever artifacts the underlying PR CI workflows create.

## Dependencies and Integration Points
Depends entirely on `pr-ci.yml` reusable workflow and its child lint/unit/bdd/image workflows.

## Risks
Despite the name, there is no scheduled trigger. It only runs when manually dispatched. The final job provides a simple green status but no extra coverage beyond PR CI.

## Test Signals
Successful completion of underlying `pr-ci.yml` and final `nightly-ci` step.
