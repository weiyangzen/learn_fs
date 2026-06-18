# sources/control-plane/mayastor/.github/bors.toml

## Purpose
Bors merge queue policy for Mayastor.

## Important Settings
Required status is `bors-ci`; PR statuses are `commitlint` and `DCO`; timeout is 10000 seconds; two approvals are required; merged branches are deleted; block labels are `DO NOT MERGE` and `wip`; bot committer identity is configured.

## Control Flow
Bors reads this policy when handling commands such as `bors merge`, checks statuses/approvals/labels, creates staging/trying branches, waits for `bors-ci`, and merges on success.

## State and Persistence
Mutates GitHub PR/branch state via bors. This config persists policy only.

## Dependencies and Integration Points
Integrates with `.github/workflows/pr-ci.yml` producing `bors-ci`, `pr-commitlint.yml`, `staging-dco.yml`, and GitHub review approvals.

## Risks
If workflow names or required statuses drift, bors blocks all merges. Required approvals overlap with GitHub branch protection and can confuse maintainers if inconsistent. Long timeout reflects heavy CI but can delay feedback.

## Test Signals
Submit a test PR through bors and verify staging triggers `bors-ci`, commitlint, and DCO as expected. Confirm block labels prevent queueing.
