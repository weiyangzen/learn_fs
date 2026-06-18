# sources/distributed-fs/beegfs-protobuf/.github/workflows/contributors.yml

## Purpose

This workflow enforces ThinkParQ contributor policy on pull requests by checking CLA-approved PR authors and approved commit author/committer identities.

## Important APIs, Types, And Functions

The `verify` job runs on PR opened/synchronize events. It checks out full history, reads `vars.APPROVED_CONTRIBUTORS` as a space-separated user list, checks the PR creator login, then reads `vars.APPROVED_COMMITTERS` as JSON mapping names to emails. For each commit unique to the PR base branch, it extracts author and committer names/emails with `git show`, masks emails in logs, and validates names and emails with `jq`.

## Control Flow

The workflow exits early if there are no PR-specific commits. Otherwise it accumulates `EXIT_CODE=1` for every failed identity check and exits once all commits are processed, allowing all violations to be reported in one run.

## State And Persistence

There is no persistent repository state. Policy state lives in GitHub Actions variables. Full git history is fetched to compute `origin/$BASE_REF..HEAD`.

## Dependencies And Integration Points

It depends on `actions/checkout@v3`, GitHub PR event fields, repository/org Actions variables, git, jq, and GitHub workflow command annotations for errors/notices/masking.

## Risks And Test Signals

If `APPROVED_COMMITTERS` is invalid JSON or jq is unavailable, the workflow will fail during validation. Name-based lookup means approved contributors must use exact configured `user.name`. The workflow masks actual emails before logs but still prints names. This is policy validation, not code validation, and its signal is commit hygiene rather than build correctness.
