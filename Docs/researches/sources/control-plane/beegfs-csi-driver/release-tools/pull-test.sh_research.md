# sources/control-plane/beegfs-csi-driver/release-tools/pull-test.sh

Purpose: Prow helper for testing changes to `csi-release-tools` by importing them into another repository and running that repository's Prow script.

Important APIs/types/functions: Uses `CSI_RELEASE_TOOLS_DIR="$(pwd)"` and required `PULL_TEST_REPO_DIR`. Runs git subtree pull and then `exec ./.prow.sh`.

Control flow: Assumes it starts inside the updated release-tools repository. It changes to the target repo, hard-resets the target working tree, pulls the release-tools repo into `release-tools` prefix with `--squash`, prints recent log entries, and hands off to the target repo's `.prow.sh`.

State and persistence: Destructively resets the target repo working tree, updates its release-tools subtree, and may leave merge commits or working tree changes before tests.

Dependencies and integration points: Used by PR jobs for release-tools itself. Requires `PULL_TEST_REPO_DIR`, git subtree support, and a target repository with `.prow.sh`.

Risks: The `git reset --hard` is intentionally destructive. It assumes the source branch name `master` in subtree pull. Target repo local changes are discarded.

Test signals: The final test signal is the target repository's `.prow.sh` result after importing the release-tools changes.
