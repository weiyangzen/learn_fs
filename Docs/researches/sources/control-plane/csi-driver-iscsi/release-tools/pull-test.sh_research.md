# sources/control-plane/csi-driver-iscsi/release-tools/pull-test.sh

Purpose: validates a `csi-release-tools` PR by importing the changed subtree into another repository and running that repository's Prow entrypoint.

Important APIs and types: uses `PULL_TEST_REPO_DIR` as the target repository directory and `CSI_RELEASE_TOOLS_DIR` as the current release-tools checkout.

Control flow: enables lazy blob fetching for Prow partial clones, records the release-tools directory, moves to the target repo, hard-resets it, pulls the current release-tools directory as a git subtree into `release-tools`, prints recent log entries, and `exec`s `./.prow.sh`.

State and persistence: destructively resets and mutates the target test repo workspace, then replaces the shell process with target Prow tests.

Dependencies and integration: depends on git subtree, Prow environment, and a target repo with `.prow.sh`.

Risks: `git reset --hard` is destructive by design in the target checkout. It assumes the subtree prefix is exactly `release-tools` and branch name `master`.

Test signals: downstream `.prow.sh` results in the importing repository.
