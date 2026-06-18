<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-pr.yml -->
# sources/cloud-native/moby/.github/workflows/validate-pr.yml

## Purpose
Validates PR metadata and changelog hygiene: impact labels must be paired with area/kind labels, changelog code blocks must match impact labels, commit messages must reference GitHub issues correctly, and release-branch PR titles must match the target branch.

## Important APIs, Types, And Functions
- Jobs: `check-labels`, `check-changelog`, `check-commit-references`, and `check-pr-branch`.
- `check-changelog` extracts a fenced `markdown changelog` block from the PR body using `awk`.
- `check-commit-references` runs `bash hack/validate/pr-gh-references` with full history.
- `check-pr-branch` parses a leading bracketed title prefix and compares it with `GITHUB_BASE_REF`.

## Control Flow
On PR open/edit/label/sync events, label checks run simple GitHub expression predicates. Changelog validation ensures impact-labeled PRs include a non-trivial changelog block and non-impact PRs do not. Commit reference validation checks out full history and runs the repository script. Branch validation allows master PRs without a prefix but requires non-master PR title prefix to equal the base branch after removing ` backport`.

## State And Persistence
The workflow writes no state; it produces PR check results.

## Dependencies And Integration Points
Integrates with labeler output, release-note conventions in PR templates, and `hack/validate/pr-gh-references`.

## Risks And Edge Cases
Changelog extraction is sensitive to exact fence text. Label checks are string containment over comma-joined label names, which is simple but can produce surprising matches if label names overlap. Branch prefix parsing requires maintainers to follow a precise title convention.

## Test Signals
Failures produce GitHub Actions error annotations explaining missing labels, changelog mismatch, bad references, or branch-title mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-pr.yml -->
