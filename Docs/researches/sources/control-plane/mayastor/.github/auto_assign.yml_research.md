# sources/control-plane/mayastor/.github/auto_assign.yml

## Purpose
Configuration for a GitHub auto-assign action to add reviewers to pull requests.

## Important Settings
`addReviewers: true`, `addAssignees: false`, four reviewer usernames, `skipKeywords: [wip]`, and `numberOfReviewers: 2`.

## Control Flow
The external auto-assign action reads this file on PR events and randomly or deterministically chooses two reviewers unless the PR includes a skip keyword.

## State and Persistence
No repo runtime state. It mutates PR metadata by requesting reviewers.

## Dependencies and Integration Points
Depends on whichever GitHub Action/app is configured to consume `auto_assign.yml`. Integrates with code review workflow and bors-required approvals.

## Risks
Reviewer list can become stale. Only `wip` is skipped, so draft or other blocked PR labels may still request reviewers depending on action behavior. It does not assign issue owners.

## Test Signals
Open a test PR and verify two reviewers are requested; include `wip` and confirm reviewer assignment is skipped.
