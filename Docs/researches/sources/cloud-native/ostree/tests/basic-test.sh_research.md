<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/basic-test.sh -->
## sources/cloud-native/ostree/tests/basic-test.sh

Purpose: sourced TAP-style integration body for the core `ostree` CLI, covering checkout, commit, pull-local, fsck, metadata, refs, remotes, cache behavior, whiteouts, and repository modes. It expects `libtest.sh` to have created `repo`, `test_tmpdir`, assertion helpers, `OSTREE`, `CMD_PREFIX`, and feature-skip helpers.

Important APIs/functions: local `validate_checkout_basic()` and `assert_trees_identical()` wrap repeated expectations; the script heavily exercises `ostree checkout`, `commit`, `diff`, `pull-local`, `prune`, `cat`, `ls`, `show`, `log`, `reset`, `remote`, and `fsck`. It branches on `is_bare_user_only_repo`, repo config mode, xattr support, SELinux relabel support, whiteout device support, and strace fault injection.

Control flow/state: the script mutates a single test repository through many refs (`test2`, `test3-*`, `branch-with-commitmsg`, etc.), repeatedly checking out trees, committing changes, resetting refs, pruning unreferenced content, and constructing auxiliary repos. Persistent state is local to the test tempdir except exported feature variables and temporary `repo/tmp/staging-*` assertions.

Dependencies/integration: requires a functioning uninstalled or installed `ostree`, GNU shell tools, `stat`, `sha256sum`, xattr tools, optional `strace`, optional SELinux, and helpers from `libtest.sh`. It is a broad regression net for repository object layout, metadata byte order via `get-byte-order`, and boot/cache semantics.

Risks/test signals: high brittleness around filesystem features, root/user mode, and exact English error strings. Strong test signals are TAP `ok` lines, explicit negative-command assertions, hardlink checks, object checksum validation, and fsck after risky operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/basic-test.sh -->
