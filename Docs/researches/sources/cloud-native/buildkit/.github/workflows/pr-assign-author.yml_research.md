# sources/cloud-native/buildkit/.github/workflows/pr-assign-author.yml

## Purpose
Automatically assigns pull request authors on opened or reopened PRs.

## APIs, Flow, And State
Triggered by `pull_request_target` for `opened` and `reopened`. It delegates to the reusable `crazy-max/.github` workflow and grants `pull-requests: write` for assignment updates. State persists as GitHub assignee metadata.

## Dependencies And Integration
Depends on the pinned external reusable workflow. It complements labeler and triage automation by ensuring a PR has an assignee.

## Risks And Test Signals
The external workflow owns behavior, so changes require updating the pinned SHA. The same `pull_request_target` safety principle applies: avoid adding untrusted code checkout. Test signal is assignee mutation on new/reopened PRs.
