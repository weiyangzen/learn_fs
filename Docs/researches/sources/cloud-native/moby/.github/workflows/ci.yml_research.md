<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/ci.yml -->
# sources/cloud-native/moby/.github/workflows/ci.yml

## Purpose
Main build CI workflow for Moby. It validates DCO, builds static and dynamic Linux binaries on amd64 and arm64, builds cross-platform binaries, runs `govulncheck` with SARIF upload, builds the dind image, and exposes aggregate success checks including a legacy `build (binary)` check name.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build`, `prepare-cross`, `cross`, `govulncheck`, `build-dind`, `success`, and `build-binary`.
- Uses Docker Buildx/Bake with BuildKit `moby/buildkit:latest`.
- `prepare-cross` uses `docker/bake-action/subaction/matrix` to derive platforms from `binary-cross`.
- `govulncheck` writes SARIF and uploads it on non-PR `moby/moby` runs.

## Control Flow
DCO gates most jobs. The build matrix runs `binary` and `dynbinary` on amd64/arm64 runners and validates artifacts with `file`. Cross builds generate a platform matrix then build each target with platform override. Security scanning runs regardless of `ci/validate-only`. The `success` job fails if any dependency failed or was cancelled, and `build-binary` preserves the old required check name.

## State And Persistence
No long-lived build artifacts are uploaded in this workflow; outputs are inspected in-place. SARIF may persist in GitHub code scanning on accepted branches.

## Dependencies And Integration Points
Depends on Bake target definitions, the root Dockerfile, GitHub CodeQL SARIF upload, and DCO workflow. It is a high-level required check for build health.

## Risks And Edge Cases
The aggregate `success` job must include all required dependencies or failures may be missed. `govulncheck` has long timeout and security-events permission. Validate-only PRs skip cross and dind but not vulnerability scanning.

## Test Signals
Signals are successful binary/dynbinary file inspection, cross-build matrix completion, SARIF upload where applicable, dind cache-only build, and aggregate success jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/ci.yml -->
