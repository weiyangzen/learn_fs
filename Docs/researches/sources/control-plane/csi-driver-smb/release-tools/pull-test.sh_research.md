<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/pull-test.sh -->
# sources/control-plane/csi-driver-smb/release-tools/pull-test.sh

Purpose: Prow helper for testing release-tools changes after importing them into another repository through `git subtree`.

Important behavior: Enables `GIT_NO_LAZY_FETCH=0` to work around blobless Prow checkouts, records the current release-tools directory, resets the target repo, pulls the current release-tools subtree into `$PULL_TEST_REPO_DIR`, prints recent logs, then execs the target repo's `.prow.sh`.

Control flow: `set -ex` aborts on failures. It falls through from subtree update into the consumer repo's own test script.

State and persistence behavior: Destructively resets the target repo worktree, mutates its `release-tools` subtree, and runs its CI tests.

Dependencies and integration points: Requires `PULL_TEST_REPO_DIR`, git subtree support, Prow checkout layout, and a target `.prow.sh`.

Risks: `git reset --hard` is intentional but destructive; it must run only in disposable Prow workspaces. Blobless checkout handling depends on Git behavior.

Test signals: Provides integration signal that release-tools changes still work when imported by a real CSI repo.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/pull-test.sh -->
