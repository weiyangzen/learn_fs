# sources/distributed-fs/beegfs-go/.github/workflows/contributors.yml

## Purpose
This workflow enforces ThinkParQ contributor policy on pull requests by checking CLA approval and allowed author/committer identities.

## Control Flow
On opened or synchronized pull requests, the job checks out full history. The first shell step compares the PR creator login against the space-separated `APPROVED_CONTRIBUTORS` repository variable. The second step gathers commits unique to the PR base branch, parses `APPROVED_COMMITTERS` JSON with `jq`, masks actual emails in logs, and verifies author and committer names map to the expected emails.

## Dependencies and Integration
Dependencies include GitHub repository variables, `jq` on the runner image, `git log`, and `git show`. The workflow integrates with PR status checks and GitHub log annotations through `::error::`, `::notice::`, and `::add-mask::`.

## Risks and Test Signals
An unset or malformed `APPROVED_COMMITTERS` variable will fail all or many commits. It trusts names as JSON keys, so unusual characters may need careful encoding. Full checkout is required for base comparisons; forks or rewritten histories can expose edge cases.
