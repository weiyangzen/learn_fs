# sources/control-plane/mayastor/.github/workflows/develop-to-release.yml

## Purpose
Automates preparation of release branches by updating submodule branch metadata and creating/approving/queueing a PR.

## Important Jobs and Steps
On push to `release/**`, job `prepareReleaseBranch` checks out, runs `./scripts/set-submodule-branches.sh --branch "$branch"`, creates a signed-off PR with `peter-evans/create-pull-request@v5`, labels it, approves it using two tokens, and comments `bors merge`.

## Control Flow
The create-pull-request step may or may not produce a PR; approval and bors steps are conditional on a PR number output.

## State and Persistence
Mutates git branches/PRs in GitHub. No cluster/runtime state.

## Dependencies and Integration Points
Requires secrets `ORG_CI_GITHUB` and `ORG_CI_GITHUB_2`, GitHub CLI availability, bors, and submodule scripts.

## Risks
Automated self-approval and merge commands must be tightly permissioned. If submodule script produces unintended diffs, automation can queue them quickly. Uses older create-pull-request major than `mod-update.yml`.

## Test Signals
Push a release branch in a controlled repo and verify PR contents, approvals, labels, signoff, and bors queueing.
