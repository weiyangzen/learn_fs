# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/resolve_test.c

Purpose: matrix test for openat2 path-resolution flags using a crafted directory tree with regular directories, relative and absolute symlinks, procfs magic links, a tmpfs mount point, and paths designed to escape or be scoped to a dirfd.

Important APIs/types/functions: `setup_testdir()` unshares the mount namespace, makes `/tmp` private, builds the test tree, mounts tmpfs at `mnt`, and creates all links/files. `struct basic_test` describes a case: optional starting directory, path, `open_how`, expected pass/fail, and expected fd target or errno. `test_openat2_opath_tests()` iterates 88 cases.

Control flow: `main()` requires effective root, sets a plan of 88, and runs the matrix. Tests auto-add `O_PATH` unless using `O_CREAT`, open the starting dirfd, duplicate it into a hardcoded fd used by procfs magic-link cases, then call `sys_openat2()`. Passing cases are checked with `fdequal()`, failing cases with negative errno. Unsupported openat2 converts all cases to skip.

State and persistence: creates a temp tree under `/tmp`, unshares/mutates the mount namespace, mounts tmpfs, creates files through `O_CREAT`, opens `/dev/null`, and allocates strings. It does not explicitly unmount/remove the tree, relying on process/mount namespace lifetime.

Dependencies/integration: requires root or CAP_SYS_ADMIN for `unshare(CLONE_NEWNS)` and mount operations, procfs for magic links and fd paths, and helper wrappers. It validates `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, and `RESOLVE_NO_SYMLINKS`.

Risks: mount namespace and `/proc` assumptions make this unsuitable for restricted containers. Textual path comparison can be brittle under unusual `/tmp` or procfs configurations. The root requirement is enforced even though the file notes capability-specific checks would be more precise.

Test signals: kselftest prints one pass/fail/skip line per named resolver case. Any mismatch in fd target or errno increments fail count and exits nonzero.
