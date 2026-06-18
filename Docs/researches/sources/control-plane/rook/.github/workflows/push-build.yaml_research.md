# sources/control-plane/rook/.github/workflows/push-build.yaml

## Purpose

Builds, signs, and releases Rook images on pushes to master, release branches, and version tags.

## Important APIs, Types, and Functions

The `push-image-to-container-registry` job runs only in `rook/rook`, grants `contents: read`, `packages: write`, and `id-token: write`, logs into Docker Hub, Quay, and GHCR, configures AWS credentials, installs cosign and Python dependencies, configures git identity, then runs `tests/scripts/build-release.sh`.

## Control Flow

Checkout disables persisted credentials, Go 1.26 and QEMU are set up, registry and AWS credentials are configured from secrets, `BRANCH_NAME` and `GITHUB_REF` are exported, Python dependencies are installed, git identity is set to Rook, and the release script handles the actual build/publish flow.

## State and Persistence Behavior

State is written outside the runner to registries, AWS-backed release destinations, GitHub packages, signatures, and possibly release metadata. Runner-local build state is ephemeral.

## Dependencies and Integration Points

It integrates with Docker/QEMU, cosign OIDC keyless signing, Docker Hub, Quay, GHCR, AWS, Python `pygit2`, and the release script.

## Risks and Edge Cases

This workflow has high-impact credentials and publish permissions. Failures can leave partial registry state. The release script is the main behavior owner, so reviewing only this YAML is insufficient for release safety.

## Test Signals

Successful completion means the release script built and published images/artifacts for the pushed ref.
