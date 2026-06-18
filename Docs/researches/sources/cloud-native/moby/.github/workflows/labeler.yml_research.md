<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/labeler.yml -->
# sources/cloud-native/moby/.github/workflows/labeler.yml

## Purpose
Runs `actions/labeler` on pull requests to apply labels from `.github/labeler.yml`.

## Important APIs, Types, And Functions
- Trigger: `pull_request_target`, annotated for zizmor because it only labels and does not checkout or execute PR code.
- Job permission elevates `pull-requests: write` while keeping `contents: read`.
- Uses pinned `actions/labeler@v6.1.0`.
- `sync-labels: false` avoids removing labels that no longer match.

## Control Flow
For each PR target event, the workflow runs a single labeler step. Concurrency is per PR number and cancels in-progress label runs.

## State And Persistence
Applied labels persist on the pull request. No repository files or artifacts are produced.

## Dependencies And Integration Points
Consumes `.github/labeler.yml` and feeds validation/triage workflows that rely on label taxonomy.

## Risks And Edge Cases
`pull_request_target` has elevated token context; safety relies on never checking out or executing PR code. Because sync is disabled, stale labels may remain after file changes.

## Test Signals
Expected labels appearing on PRs after file changes are the observable signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/labeler.yml -->
