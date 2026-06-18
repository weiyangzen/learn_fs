# sources/control-plane/mayastor/scripts/set-submodule-branches.sh

Purpose: helper for setting or updating git submodule tracking branches based on the current or requested branch.

Important APIs/types/functions: `submodule_set_branch_all` runs `git submodule set-branch`; `submodule_update` runs `git submodule update --remote` and recursive update inside modules. Options include `--branch`, `--clear`, `--update`, and `--update-modules`.

Control flow: defaults branch to current branch. It sets branch tracking only for `develop` or `release/*`, updates modules when requested, clears branch tracking when requested, otherwise prints no modification.

State/persistence: mutates `.gitmodules` branch settings and/or submodule worktrees.

Dependencies/integration: supports release/develop submodule maintenance and pairs with `check-submodule-branches.sh`.

Risks: bug `CLEAR_BRANCH=="y"` is a comparison-like command, not assignment, so `--clear` may not work. Unquoted module paths and command substitution are fragile for unusual paths.

Test signals: after setting/updating, `check-submodule-branches.sh` should pass.
