# sources/control-plane/mayastor/.github/workflows/image.yml

## Purpose
Builds and pushes Mayastor release/dev images on branch pushes and as a reusable workflow for staging releases.

## Important Jobs and Steps
Triggers on pushes to `develop` and `release/**`, plus `workflow_call` with required `tag`, `registry`, and `namespace`. Job checks out full history/submodules, refetches tags for tag builds, installs Nix, logs into Docker Hub and GHCR, then runs `./scripts/release.sh` with workflow inputs for dispatch-style events or no args for push events.

## Control Flow
Event name decides whether to pass explicit tag/registry or rely on release script defaults. The workflow sets `TAG` from inputs.

## State and Persistence
Builds images and pushes them to registries. No repo files are changed.

## Dependencies and Integration Points
Requires Docker Hub credentials, GHCR token, Nix, recursive submodules, and release script. Called by `staging.yml`.

## Risks
The branch for explicit args checks `workflow_dispatch`, but this workflow declares `workflow_call`, not `workflow_dispatch`; called workflows may therefore skip explicit args and run default push behavior unless GitHub event semantics are accounted for. Registry credentials are broad. Tag refetch workaround is specific to checkout behavior.

## Test Signals
For push builds, verify expected image tags appear in registries. For reusable calls, verify inputs are actually honored; this deserves explicit CI audit because of the event-name condition.
