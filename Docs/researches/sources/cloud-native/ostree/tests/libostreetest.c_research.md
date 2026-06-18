<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.c -->
## sources/cloud-native/ostree/tests/libostreetest.c

Purpose: C helper library that bridges GLib/GIO tests to the shell test harness and creates test repos/sysroots.

Important APIs/functions: `ot_test_tmpdir_template()`, `ot_test_run_libtest()`, `ot_test_setup_repo()`, `ot_check_relabeling()`, `ot_check_user_xattrs()`, and `ot_test_setup_sysroot()`. It uses GLib spawning, libglnx tmpfiles/xattrs, and OSTree repo/sysroot APIs.

Control flow/state: `ot_test_run_libtest()` spawns bash, sources `tests/libtest.sh`, and runs an arbitrary command. Repo/sysroot setup delegates to shell functions, then opens resulting `repo` or `sysroot`. Relabel/user-xattr checks create linkable tmpfiles and probe xattr get/set behavior. Sysroot setup sets `OSTREE_SYSROOT_DEBUG` to mutable deployments and maybe `no-xattrs`.

Dependencies/integration: used by C tests needing canonical shell fixtures. Depends on `G_TEST_SRCDIR`, GLib, libglnx, OSTree headers/libs, and shell tests.

Risks/test signals: shell command construction is string-based. Signals are GError propagation, opened `OstreeRepo`, xattr booleans, and sysroot object creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.c -->
