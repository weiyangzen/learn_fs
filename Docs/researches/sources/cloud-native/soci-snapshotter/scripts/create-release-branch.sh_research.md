# sources/cloud-native/soci-snapshotter/scripts/create-release-branch.sh

Purpose: creates and optionally pushes a `release/<major>.<minor>` branch from a chosen base commit.

Important APIs/types/functions: parses `--assert`, `--base`, and `--dry-run` plus version argument. `sanitize_input` validates version and base commit. `assert_create_branch` verifies current branch and base commit.

Control flow: parse flags, strip leading `v`, validate semantic major/minor, resolve or validate base commit, checkout new release branch, optionally assert branch state, then either validate push command in dry-run mode or push to origin.

State and persistence: mutates local git branch state and may push a branch to origin.

Dependencies/integration points: requires git history and remote named `origin`; intended for release automation.

Risks: `git checkout -b` is stateful and fails if branch exists or worktree is dirty in incompatible ways. `grep "$BASE_COMMIT"` may match multiple commits but only checks non-empty. Dry-run does not exercise remote permission or branch existence.

Test signals: assert mode validates branch name and commit after checkout; no standalone tests.
