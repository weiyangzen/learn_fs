# sources/control-plane/mayastor/.github/workflows/mod-update.yml

## Purpose
Manual workflow to update selected or all git submodules and create an automated PR.

## Important Jobs and Steps
`workflow_dispatch` input `submodules` accepts comma-separated module names. Job checks out full history with recursive submodules, runs `./utils/dependencies/scripts/git/submodule-branches.sh -u -m "<input>"`, creates a signed-off PR with `peter-evans/create-pull-request@v7`, then approves it with the default GitHub token if a PR exists.

## Control Flow
Manual trigger only. PR branch is `update-submodules/<ref_name>` and is deleted after merge.

## State and Persistence
Mutates submodule pointers and creates PR branches. No runtime state.

## Dependencies and Integration Points
Requires `ORG_CI_GITHUB` for PR creation and submodule helper scripts. Ties into bors/approval workflow externally.

## Risks
Automated approval by CI bot may not satisfy all branch protections. Submodule updates can bring large behavioral changes; this workflow does not run validation itself beyond PR creation. Input parsing is delegated to the script.

## Test Signals
Dispatch with a small submodule set and verify PR diff, labels/metadata if any, signoff, and subsequent CI.
