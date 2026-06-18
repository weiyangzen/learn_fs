## sources/control-plane/csi-driver-host-path/release-tools/pull-test.sh

Purpose: validates csi-release-tools changes by importing the current checkout into another repository and running that repository's Prow script.

Control flow enables lazy blob fetches for Prow partial clones, records the current release-tools directory, changes to `$PULL_TEST_REPO_DIR`, hard-resets the target repo, pulls the release-tools subtree from the local directory, prints recent commits, and execs `./.prow.sh`.

State and persistence include destructive target repo working tree reset and subtree merge commit state. Dependencies are git subtree, environment variable `PULL_TEST_REPO_DIR`, and the target repo's `.prow.sh`. Risks include the explicit `git reset --hard`, assuming target repo has clean disposable checkout, and testing only one consuming repo at a time. Test signal is downstream `.prow.sh` outcome.
