<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest.sh -->
## sources/cloud-native/ostree/tests/libtest.sh

Purpose: main shell harness for OSTree source tests, extending `libtest-core.sh` with repo setup, feature detection, GPG fixtures, webserver setup, boot/sysroot fixtures, and object-path helpers.

Important APIs/functions: initializes `test_srcdir`, `top_builddir`, `test_builddir`, `test_tmpdir`, exit hooks, GPG homes, feature flags, and `OSTREE_SYSROOT_DEBUG`. Key functions include `have_selinux_relabel()`, `can_create_whiteout_devices()`, `setup_test_repository()`, `ostree_repo_init()`, `run_webserver()`, `setup_fake_remote_repo1/2()`, `setup_os_repository()`, `os_repository_new_commit()`, `have_user_xattrs()`, skip helpers, signing key generators, bare-user predicates, and object path/checksum helpers.

Control flow/state: when sourced, validates/marks the tempdir, copies `gpghome`, probes xattr/whiteout support, sets `OSTREE_SKIP_CACHE=1`, may set `OSTREE_NO_XATTRS`/`OSTREE_NO_WHITEOUTS`, and exports test key variables. Setup functions create repos, sysroots, fake remotes, HTTP dirs, bootloader stubs, and multiple commits.

Dependencies/integration: used by most shell tests, C helpers, JS helpers, and installed tests. Requires OSTree CLI, xattr tools, optional HTTP daemon, GPG/OpenSSL, system utilities, and generated test fixture archives.

Risks/test signals: broad global side effects; sourcing outside an empty tempdir intentionally fails. Strong signals include skip decisions, constructed refs/content, fsck, exported `OSTREE`, and object path helpers used by corruption/hardlink checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libtest.sh -->
