# sources/control-plane/mayastor/.github/workflows/image-pr.yml

## Purpose
Reusable CI workflow that verifies Mayastor release images can be built without publishing.

## Important Jobs and Steps
`image-build-test` checks out recursive submodules, installs Nix, and runs `./scripts/release.sh --skip-publish --build-bins`.

## Control Flow
Triggered by `workflow_call`, consumed by `pr-ci.yml`. Failure blocks the aggregate `bors-ci`.

## State and Persistence
Builds local artifacts/images on the runner but does not push because `--skip-publish` is used.

## Dependencies and Integration Points
Depends on Nix, release script, Docker/build tooling implied by the script, and submodules.

## Risks
Only validates build path, not registry auth or publish path. Running on `ubuntu-latest` may differ from release runners.

## Test Signals
Successful `release.sh --skip-publish --build-bins` is the gate.
