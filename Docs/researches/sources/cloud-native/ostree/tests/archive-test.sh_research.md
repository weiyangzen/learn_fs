# sources/cloud-native/ostree/tests/archive-test.sh

Purpose: sourced integration test for archive/repo checkout and commit behavior.

Important operations: checks out `test2`, validates files and contents, creates `repo2`, initializes it, pulls local repo content, checks out from the clone, tests user-mode checkout `-U`, commits a uid/gid 0 tree, verifies `ostree ls` ownership output, reads file content with `ostree cat`, runs `ostree fsck`, and commits overlay content with base/owner overrides while checking recursive listing counts and ownership.

Control flow: linear shell assertions under `set -euo pipefail`, with `echo "ok ..."` markers after each tested behavior.

State/persistence: creates checkout directories, a secondary repo, commits new branches (`test2-uid0`, `test-base`), output files such as `uid0-ls-output.txt`, `cow-contents`, and `ls.txt`, and temporary overlay directories.

Dependencies/integration: relies on harness variables/functions such as `$OSTREE`, `CMD_PREFIX`, `COMMIT_ARGS`, `test_tmpdir`, `ostree_repo_init`, `assert_*`, and `can_create_whiteout_devices`.

Risks: line-count expectations depend on whiteout device capability. It is sourced and assumes fixture branch `test2` exists. It mutates current directory repeatedly.

Test signals: covers checkout, pull-local clone, user checkout, commit ownership metadata, `ls`, `cat`, `fsck`, and overlay-base commit behavior; useful as a sanity signal for archive-mode object persistence and checkout correctness.
