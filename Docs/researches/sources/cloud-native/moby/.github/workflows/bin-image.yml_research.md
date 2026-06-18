<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/bin-image.yml -->
# sources/cloud-native/moby/.github/workflows/bin-image.yml

## Purpose
Builds and publishes the `moby/moby-bin` binary image using the shared Docker GitHub builder workflow, with DCO validation on non-tag runs and PR-safe no-push behavior.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to `master`/release branches/tags, and pull requests.
- Concurrency cancels stale PR runs only.
- `validate-dco` reuses `.dco.yml` unless the ref is a tag.
- `build` uses `docker/github-builder/.github/workflows/bake.yml` with target `bin-image-cross`.
- Grants `id-token: write` for signing attestations.
- Provides version/product metadata and semver tag rules matching `docker-*` tags.

## Control Flow
After DCO validation, the builder workflow runs unless the PR has `ci/validate-only`. It sets up QEMU, uses cache scope `bin-image`, builds cross-platform output, pushes only outside PRs, and authenticates to Docker Hub through repository secrets.

## State And Persistence
Push runs publish image tags to Docker Hub. PR runs build without push. Build cache persists through the external builder workflow.

## Dependencies And Integration Points
Depends on the root Dockerfile/Bake targets, Docker Hub credentials, GitHub OIDC, and DCO reusable workflow.

## Risks And Edge Cases
Secrets must be present for publishing. Tag strategy is tied to `docker-v*` tag names. Skipping DCO on tags is intentional but means tag workflows trust prior branch checks.

## Test Signals
Successful builder workflow completion, image metadata, and published `moby/moby-bin` tags are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/bin-image.yml -->
