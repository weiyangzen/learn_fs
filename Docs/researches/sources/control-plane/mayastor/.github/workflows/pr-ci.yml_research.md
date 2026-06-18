# sources/control-plane/mayastor/.github/workflows/pr-ci.yml

## Purpose
Aggregate reusable and push-triggered CI workflow for bors staging/trying branches.

## Important Jobs
Jobs call reusable workflows: `lint-ci` -> `lint.yml`, `int-ci` -> `unit-int.yml`, `bdd-ci` -> `bdd.yml`, `image-ci` -> `image-pr.yml`. Final `bors-ci` requires all four and exits zero on success.

## Control Flow
Triggered by `workflow_call` or pushes to `staging` and `trying`. GitHub's dependency graph ensures the final status only appears after all child CI completes successfully.

## State and Persistence
Child workflows create build/test artifacts; this file itself persists no state.

## Dependencies and Integration Points
Directly integrates with `bors.toml`, where `bors-ci` is required. Also underpins `nightly-ci.yml`.

## Risks
If any child workflow name/path changes, bors CI breaks. The final job provides no additional validation beyond dependency success. It is not directly configured for pull_request events; bors or other workflows must call/push it.

## Test Signals
Presence of a successful `bors-ci` status after lint, integration, BDD, and image build test pass.
