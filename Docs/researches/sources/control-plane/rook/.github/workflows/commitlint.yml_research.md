# sources/control-plane/rook/.github/workflows/commitlint.yml

## Purpose

Validates commit message format for pushes and pull requests using the repository commitlint config.

## Important APIs, Types, and Functions

The `lint` job grants `contents: read` and `pull-requests: read`, exports `GITHUB_TOKEN`, checks out full history, and runs `wagoid/commitlint-github-action` with `.commitlintrc.json` and a Rook docs help URL.

## Control Flow

The workflow triggers on master/release pushes, tags, and PRs. Concurrency cancels older PR runs. Commitlint reads PR commit metadata through the token and reports violations.

## State and Persistence Behavior

No repository state is written. Results live as GitHub check status and logs.

## Dependencies and Integration Points

It integrates with `.commitlintrc.json`, GitHub PR APIs, branch protection, and contributor documentation.

## Risks and Edge Cases

Fetch depth is zero to expose commit history. Misconfigured PR permissions or token scope would prevent the action from reading commits.

## Test Signals

Passing `lint` means all commits in scope comply with Rook's commit message convention.
