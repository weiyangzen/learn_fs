# sources/control-plane/csi-driver-nfs/release-tools/pull-test.sh

Purpose: tests changes to `csi-release-tools` by importing the current checkout into another repository and running that repository's Prow checks.

Important variables and commands: `PULL_TEST_REPO_DIR`, `CSI_RELEASE_TOOLS_DIR`, `GIT_NO_LAZY_FETCH=0`, `git subtree pull --squash --prefix=release-tools`, and final `exec ./.prow.sh`.

Control flow: runs with `set -ex`, records the current release-tools directory, changes to the target repo, resets the target working tree, pulls the current release-tools checkout as a subtree on `master`, shows recent commits, and then executes the target repo's `.prow.sh`.

State and persistence behavior: mutates the target repository checkout by resetting it and creating a subtree merge commit or working tree change. It does not return to the original checkout because it `exec`s the target test script.

Dependencies and integration points: used by pull Prow jobs for csi-release-tools. Depends on git subtree, Prow checkout behavior, and `PULL_TEST_REPO_DIR` pointing at a suitable consumer repo.

Risks: `git reset --hard` is destructive to the target checkout by design. It assumes the release-tools branch is `master` and that the target repo has a compatible `.prow.sh`.

Test signals: downstream `.prow.sh` success after subtree import proves release-tools changes work in a consumer repo.
