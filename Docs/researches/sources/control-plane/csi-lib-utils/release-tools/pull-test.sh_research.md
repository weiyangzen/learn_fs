# sources/control-plane/csi-lib-utils/release-tools/pull-test.sh

## Purpose

This script tests a pull request against `csi-release-tools` by importing the updated release-tools subtree into another CSI repository and then running that repository's Prow entrypoint.

## Important Behavior

It enables `GIT_NO_LAZY_FETCH=0` because Prow's blobless checkout can break `git subtree pull`. It records the current release-tools directory, changes to `$PULL_TEST_REPO_DIR`, hard-resets the target worktree, pulls the release-tools subtree from the PR checkout into `release-tools`, prints recent log entries, and `exec`s `./.prow.sh`.

## State, Dependencies, and Integration

It mutates the target test repository's worktree and history. It depends on `PULL_TEST_REPO_DIR`, git subtree, Prow checkout layout, and a target repo with `.prow.sh`. It integrates release-tools PR validation with real consumer repository tests.

## Risks and Test Signals

`git reset --hard` is destructive in the target checkout but expected in disposable Prow workspaces. Subtree conflicts or missing blob fetch support fail early. The test signal is the target repository's Prow run after importing the PR version of release-tools.
