# sources/control-plane/mayastor/.github/workflows/pr-submodule-branch.yml

## Purpose
Checks that submodule branch metadata matches the target branch and that submodule HEADs point to expected branches.

## Important Jobs and Steps
On PRs and pushes to `develop`, `release/**`, and `staging`, the job conditionally checks out with either default token or `ORG_CI_GITHUB`, recursive submodules, determines `check_branch` from PR base ref or current ref, runs `./scripts/set-submodule-branches.sh --branch "$check_branch"`, prints `.gitmodules`, checks no diff in `.gitmodules`, then runs `./scripts/check-submodule-branches.sh`.

## Control Flow
The dual checkout steps use an environment probe for secret presence. The first validation step fails if `.gitmodules` would need changes for the target branch.

## State and Persistence
May mutate `.gitmodules` in the runner while testing, but requires diff to be empty. No repo changes are pushed.

## Dependencies and Integration Points
Depends on submodule scripts and recursive checkout permissions. Integrates with release/develop branch management.

## Risks
Secret-based conditional checkout is unusual and should be checked carefully; unavailable secrets on forked PRs can alter behavior. `.gitmodules` diff check catches branch metadata but not all submodule pointer issues, hence second script.

## Test Signals
PR targeting develop/release with correct and incorrect submodule branch metadata. Verify fork PRs work without privileged token.
