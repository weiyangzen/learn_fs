<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml


## Purpose
GitHub Actions workflow enforcing changelog entries on relevant Go dependency/source PRs.


## Important APIs, Types, and Functions
Workflow Changelog triggers on pull_request opened/edited/synchronize/reopened/labeled/unlabeled for Go files/go.mod/go.sum. Job uses gh api to count files under docs/changelogs/ and fails unless modified or PR opts out by title/label.


## Control Flow
The job writes a modified count to GITHUB_OUTPUT, then emits a GitHub error and exits nonzero when no changelog entry is present.


## State and Persistence Behavior
State is workflow run status and PR check result. It reads PR labels/title/files through the GitHub API.


## Dependencies and Integration Points
Depends on GitHub Actions, gh CLI, github.token, PR file API, and shell jq selector support in gh.


## Risks and Test Signals
Risks are false positives for internal-only changes and reliance on title/label skip conventions. Signal enforces release-note hygiene.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml -->
