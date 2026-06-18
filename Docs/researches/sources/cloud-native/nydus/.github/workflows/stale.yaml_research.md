# sources/cloud-native/nydus/.github/workflows/stale.yaml

## Purpose
This scheduled/manual workflow marks inactive issues and PRs stale and closes them after additional inactivity.

## Important APIs, Types, and Functions
It grants `issues: write` and `pull-requests: write` and uses `actions/stale@v10`. Configuration marks both issues and PRs after 60 idle days, closes after 7 stale days, labels stale items with `stale`, exempts `bug` and `wip` labels, exempts all milestones, and posts configured stale/close messages.

## Control Flow
The workflow runs daily at midnight UTC or manually. The stale action scans issues and PRs, applies labels/messages based on age and exemptions, then closes stale items that remain inactive.

## State and Persistence
Persistent state is GitHub issue/PR labels, comments, and closed status. The repository tree is unchanged.

## Dependencies and Integration Points
This integrates with GitHub Issues/PRs and the repository labeling/milestone conventions. It relies on maintainers applying `bug`, `wip`, or milestones to prevent stale handling.

## Risks and Edge Cases
The workflow can close valid but inactive work if labels or milestones are missing. It treats PRs and issues with the same timing. It has no operation limit configured, so default action limits apply.

## Test Signals
Manual dispatch on a test repository or dry-run-style review of action logs validates behavior. In production, labels/comments/closures are the signal.
