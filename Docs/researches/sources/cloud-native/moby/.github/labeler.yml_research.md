<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/labeler.yml -->
# sources/cloud-native/moby/.github/labeler.yml

## Purpose
Maps changed file globs to repository labels for `actions/labeler`, classifying PRs by module, daemon area, builder implementation, networking, volumes, swarm, images, logging, security subareas, systemd, contrib, packaging, containerd integration, rootless, testing, docs, dependencies, CI, Windows platform, and changelog impact.

## Important APIs, Types, And Functions
- Uses `changed-files` with `any-glob-to-any-file`, `all-globs-to-all-files`, and `any-glob-to-all-files`.
- Many labels exclude `vendor/**` to avoid dependency changes triggering source-area labels.
- Labels such as `area/builder` aggregate more specific BuildKit and classic-builder paths.
- `impact/changelog` is tied to `api/docs/CHANGELOG.md`.

## Control Flow
The `labeler.yml` workflow feeds this config to `actions/labeler` on `pull_request_target`. The action evaluates changed files and applies matching labels without executing PR code.

## State And Persistence
Matching labels are persisted on the pull request. The config itself has no runtime state.

## Dependencies And Integration Points
Integrates with `validate-pr.yml`, which enforces `kind/*` and `area/*` labels when `impact/*` labels are present. It also feeds maintainer triage and release-note workflows.

## Risks And Edge Cases
Glob drift is likely as directories move. The Windows rule uses `any-glob-to-all-files`, which can behave differently from most entries. Labeling on `pull_request_target` is intentionally limited to label application; safety depends on no checkout/execution of untrusted PR code.

## Test Signals
PRs touching known paths should receive expected labels. Mislabeling or missing labels are visible through `validate-pr.yml` failures and maintainer triage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/labeler.yml -->
