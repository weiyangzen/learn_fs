# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete.c

Purpose: implements `ostree remote delete`, removing a remote configuration.

Important APIs/functions: `ot_remote_builtin_delete()` parses `--if-exists`, `--repo`, and `--sysroot`, opens the target through `ostree_parse_sysroot_or_repo_option()`, validates `NAME`, and calls `ostree_repo_remote_change()` with delete or delete-if-exists operation.

Control flow: parse options, resolve repo/sysroot, validate one positional remote name, invoke remote-change API, return success/failure.

State/persistence: mutates remote configuration in the selected repository/sysroot. `--if-exists` suppresses missing-remote errors through the libostree change operation.

Dependencies/integration: uses the same special sysroot-or-repo path as remote add, so it participates in deployment-local versus physical repo config behavior.

Risks: wrong target selection via `--sysroot` versus `--repo` deletes from a different config scope. There is no confirmation prompt.

Test signals: remote delete behavior is likely covered in remote/config tests outside this subset; `admin-test.sh` indirectly validates remote config scoping via add.
