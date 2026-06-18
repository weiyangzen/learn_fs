# sources/distributed-fs/ipfs-kubo/.github/workflows/generated-pr.yml

## Purpose
This scheduled/manual workflow delegates cleanup of generated pull requests to `ipdxco/unified-github-workflows`.

## Important APIs, Types, And Functions
It grants `issues: write` and `pull-requests: write` and runs a single `stale` job using `reusable-generated-pr.yml@v1`.

## Control Flow
The workflow triggers daily at midnight UTC or by manual dispatch, then the reusable workflow performs all policy logic externally.

## State And Persistence Behavior
It can mutate GitHub PR/issue state through the reusable workflow. The local repository tree is not touched.

## Dependencies And Integration Points
The file depends entirely on the external reusable workflow contract and GitHub token permissions.

## Risks And Test Signals
The main risk is external workflow behavior changing or requiring additional permissions. Signals are scheduled job success and generated PRs being closed or updated as expected.
