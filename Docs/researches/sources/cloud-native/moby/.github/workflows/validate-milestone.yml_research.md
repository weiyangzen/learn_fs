<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-milestone.yml -->
# sources/cloud-native/moby/.github/workflows/validate-milestone.yml

## Purpose
Ensures pull requests have a milestone matching the current Docker next version from `releases/versions.yaml`.

## Important APIs, Types, And Functions
- Triggered on PR open, synchronize, milestone changes, demilestone, and edit events.
- Grants `pull-requests: read`.
- Uses `actions/github-script` to list PR files and read `releases/versions.yaml`.
- If the PR modifies `releases/versions.yaml`, reads it from the PR head SHA; otherwise reads from the base branch.

## Control Flow
The script lists modified files, decides which ref to read, fetches the YAML file through GitHub REST, extracts the line containing `next:`, strips quotes, compares it with the PR milestone title, and fails if absent or mismatched.

## State And Persistence
No state is written. It reads PR metadata and repository contents and emits a check result.

## Dependencies And Integration Points
Tied to release management conventions in `releases/versions.yaml` and PR milestone usage.

## Risks And Edge Cases
The YAML parsing is line-based and looks for `next:` substring, so structural changes could break it. It trusts PR head content when the versions file is changed, which is acceptable because the check is advisory for maintainers, not a security boundary.

## Test Signals
The check passes when the PR milestone exactly equals the extracted next version and fails with explicit messages otherwise.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/validate-milestone.yml -->
