# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.c

Purpose: shared implementation for openat2 selftests. It normalizes raw syscall return values to either file descriptors or negative errno values and provides path comparison helpers.

Important APIs/functions: `needs_openat2()` currently returns true when `how->resolve` is nonzero. `raw_openat2()`, `sys_openat2()`, `sys_openat()`, and `sys_renameat2()` wrap syscalls or libc calls. `touchat()` creates a file relative to a directory fd. `fdreadlink()` reads `/proc/self/fd/<fd>`. `fdequal()` compares a returned fd target with an expected directory/path combination. The constructor `init()` asserts `struct open_how` size and sets global `openat2_supported`.

Control flow: constructor runs before test `main()`, calls `sys_openat2(AT_FDCWD, ".")`, closes the fd on success, and stores support status. Test files branch on `openat2_supported` to skip or fall back.

State and persistence: no persistent files except those created by callers through `touchat()`. It allocates strings for fd paths and requires callers to free `fdreadlink()` results.

Dependencies/integration: depends on procfs for fd link comparison and kselftest `ksft_exit_fail_msg()` via helper macros. It is linked into all openat2 test binaries through the Makefile rule.

Risks: `fdequal()` compares textual `/proc/self/fd` link targets, so mount namespace changes, deleted paths, or procfs absence can produce false negatives. `touchat()` uses `O_CREAT` without an explicit access mode, relying on default flag behavior used by these tests.

Test signals: this file has no standalone tests; failures surface as immediate kselftest exits from `E_*` helpers or as pass/fail decisions in openat2 test binaries.
