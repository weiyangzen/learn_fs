# sources/cloud-native/cri-o/scripts/release-branch-forward/release_branch_forward.go

This automation finds the latest CRI-O release branch and merges `main` into it when no tag exists for that release branch. It is intended to keep unreleased release branches forward with main until the release tag lands.

Important APIs are `main` and `run`. `run` checks for `git`, `grep`, and `tail`, determines dry-run mode from the `DRY_RUN` environment variable and `-dry-run` flag, uses `git ls-remote --sort=v:refname --heads` piped through grep/tail to pick the latest `release-*` branch, checks for matching remote tags, and exits if any exist. Otherwise it opens the local repo, optionally sets dry mode, records the current branch, checks out the release branch, merges `origin/main`, pushes the release branch, and triggers the GitHub `test` workflow via `gh workflow run`.

State changes are git checkout, merge commit or dry-run equivalent, remote push, and workflow dispatch. Dependencies include release-sdk git, release-utils command/env helpers, logrus, shell commands, network, and GitHub CLI. Risks include selecting the wrong branch if remote naming changes, treating any matching tag output as completion, hidden checkout errors in deferred restore, and the broad impact of automatically merging main into a release branch. There are no direct tests in this subset.
