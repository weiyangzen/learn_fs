# subset-b-009304 research

Grouped research report for LTP syscall tests covering open_tree through pwritev. Each section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c

Purpose: Basic :manpage:`open_tree(2)` test.

Important APIs/types/functions: includes `tst_test.h`, `lapi/fsmount.h`; exercises `open_tree`, `move_mount`; defines `cleanup`, `setup`, `run`; uses flags/constants `AT_FDCWD`, `MOVE_MOUNT_F_EMPTY_PATH`, `OPEN_TREE_CLOEXEC`, `OPEN_TREE_CLONE`.

Control flow centers on `cleanup`, `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `fuse`, `Flag `.

State and persistence behavior: Runtime state is mount topology: the mounted fixture at `MNTPOINT`, cloned mount file descriptors returned by `open_tree()`, and the destination mountpoint used by `move_mount()`.

Dependencies and integration points: Depends on `lapi/fsmount.h`, the fsopen/open_tree/move_mount wrappers, root privileges, mounted test devices, and filesystem skip lists. Direct include dependencies include `tst_test.h`, `lapi/fsmount.h`.

Risks and test signals: Mount API tests are kernel-version and filesystem sensitive; cleanup must close mount fds and unmount cloned mounts or later cases inherit stale topology. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree02.c

Purpose: Basic :manpage:`open_tree(2)` failure tests.

Important APIs/types/functions: includes `tst_test.h`, `lapi/fsmount.h`; exercises `open_tree`; defines `run`; uses flags/constants `AT_FDCWD`, `OPEN_TREE_CLONE`.

Control flow centers on `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `invalid-fd`, `invalid-path`, `invalid-flags`, `fuse`. Error-path expectations include `EBADF`, `EINVAL`, `ENOENT`.

State and persistence behavior: Runtime state is mount topology: the mounted fixture at `MNTPOINT`, cloned mount file descriptors returned by `open_tree()`, and the destination mountpoint used by `move_mount()`.

Dependencies and integration points: Depends on `lapi/fsmount.h`, the fsopen/open_tree/move_mount wrappers, root privileges, mounted test devices, and filesystem skip lists. Direct include dependencies include `tst_test.h`, `lapi/fsmount.h`.

Risks and test signals: Mount API tests are kernel-version and filesystem sensitive; cleanup must close mount fds and unmount cloned mounts or later cases inherit stale topology. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EINVAL`, `ENOENT`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk; CFLAGS += -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local compiler/preprocessor flags. It is the build entry point for the `openat` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h

Purpose: Compatibility header for `openat` syscall tests; it provides a raw `tst_syscall(__NR_openat, ...)` fallback when libc does not expose `openat()`.

Important APIs/types/functions: includes `sys/types.h`, `config.h`, `lapi/syscalls.h`; defines `openat`; touches `openat`, `write`, `raw syscall path`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `config.h`, `lapi/syscalls.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c

Purpose: This test case will verify basic function of :manpage:`openat(2)`. - pathname is relative, then it is interpreted relative to the directory referred to by the file descriptor dirfd - pathname is absolute, then dirfd is ignored - ENODIR pathname is a relative pathname and dirfd is a file descriptor referring to a file other than a directory - EBADF dirfd is not a valid file descriptor - pathname is relative and dirfd is the special value AT_FDCWD, then pathname is interpreted relative to the current working directory of the calling process

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`, `tst_test.h`; exercises `openat`; defines `verify_openat`, `setup`, `cleanup`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `verify_openat`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `ENODIR`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TST_EXP_FAIL2`, `TST_EXP_FD`, `TST_RET`; checks errno values `EBADF`, `ENODIR`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c

Purpose: This test case will verify following scenarios of :manpage:`openat(2)`. - openat() succeeds to open a file in append mode, when 'flags' is set to O_APPEND. - openat() succeeds to enable the close-on-exec flag for a file descriptor, when 'flags' is set to O_CLOEXEC. - openat() succeeds to allow files whose sizes cannot be represented in an off_t but can be represented in an off_t to be opened, when 'flags' is set to O_LARGEFILE. - openat() succeeds to not update the file last access time (st_atime in the inode) when the file is read, when 'flags' is set to O_NOATIME. - openat() succeeds to open the file failed if

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`, `lapi/mount.h`, `tst_test.h`; exercises `openat`, `fork`, `execlp`, `mount`, `read`, `lseek`; defines `testfunc_append`, `testfunc_cloexec`, `testfunc_largefile`, `testfunc_noatime`, `testfunc_nofollow`, `testfunc_trunc`, `verify_openat`, `setup`, `cleanup`; uses flags/constants `AT_FDCWD`, `O_APPEND`, `O_CLOEXEC`, `O_CREAT`, `O_LARGEFILE`, `O_NOATIME`, `O_NOFOLLOW`, `O_RDONLY`, `O_RDWR`, `O_TRUNC`.

Control flow centers on `testfunc_append`, `testfunc_cloexec`, `testfunc_largefile`, `testfunc_noatime`, `testfunc_nofollow`, `testfunc_trunc`, `verify_openat`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.forks_child`, `.all_filesystems`, `.needs_root`, `.mount_device`, `.mntpoint`, `.filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `noatime`, `vfat`. Error-path expectations include `ELOOP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_EXP_FD`, `TST_EXP_FD_OR_FAIL`, `TST_RET`, `TTERRNO`; checks errno values `ELOOP`; uses child exit/wait status as part of the signal; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c

Purpose: Companion exec helper for `openat02.c`; it attempts to write through a descriptor number after exec so the parent can verify `O_CLOEXEC` closed the descriptor.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `unistd.h`; exercises `write`; defines `main`.

Control flow centers on `main`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `unistd.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: compile success and consumer test behavior are the available signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat02_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c

Purpose: the License, or (at your option) any later version.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/fcntl.h`, `openat.h`; exercises `openat`, `read`, `fcntl`; defines `cleanup`, `setup`, `openat_tmp`, `write_file`, `test01`, `read_file`, `test02`, `link_tmp_file`, `test03`, `main`; uses flags/constants `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `O_RDWR`, `O_TMPFILE`.

Control flow centers on `cleanup`, `setup`, `openat_tmp`, `write_file`, `test01`, `read_file`, `test02`, `link_tmp_file`, `test03`, `main`. Error-path expectations include `EISDIR`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `unistd.h`, `errno.h`, `test.h`, `tso_safe_macros.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`; checks errno values `EISDIR`, `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c

Purpose: Regression test for `O_TMPFILE` setgid/umask stripping on noacl filesystems, ensuring group execute and setgid bits are filtered correctly.

Important APIs/types/functions: includes `stdlib.h`, `sys/types.h`, `pwd.h`, `sys/mount.h`, `unistd.h`, `stdio.h`, `tst_test.h`, `lapi/fcntl.h`; exercises `openat`, `mount`, `umount`, `fcntl`; defines `do_mount`, `open_tmpfile_supported`, `setup`, `file_test`, `run`, `cleanup`; uses flags/constants `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `O_DIRECTORY`, `O_RDONLY`, `O_RDWR`, `O_TMPFILE`.

Control flow centers on `do_mount`, `open_tmpfile_supported`, `setup`, `file_test`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.all_filesystems`, `.mntpoint`, `.skip_filesystems` into the LTP runner. Named case hints include `exfat`, `linux-git`. Error-path expectations include `EINVAL`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `stdlib.h`, `sys/types.h`, `pwd.h`, `sys/mount.h`, `unistd.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_EXP_EQ_LI`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `openat2` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c

Purpose: Basic :manpage:`openat2(2)` test.

Important APIs/types/functions: includes `fcntl.h`, `tst_test.h`, `lapi/openat2.h`; exercises `openat2`, `fcntl`; defines `cleanup`, `setup`, `run`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_DIRECTORY`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_NO_XDEV`.

Control flow centers on `cleanup`, `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state is `struct open_how` resolution policy, directory file descriptors, symlink/magic-link fixtures, mount boundaries, and file descriptors returned by the raw `openat2` syscall.

Dependencies and integration points: Depends on `lapi/openat2.h`, raw syscall availability, `struct open_how`, root/mount fixtures for resolution flags, and Linux 5.6-era openat2 semantics. Direct include dependencies include `fcntl.h`, `tst_test.h`, `lapi/openat2.h`.

Risks and test signals: Resolution-constraint failures depend on exact kernel `openat2()` semantics and fixture layout; unsupported kernels must skip rather than fail. Test signals: reports through `TFAIL`, `TPASS`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat202.c

Purpose: :manpage:`openat2(2)` tests with various resolve flags. Success cases

Important APIs/types/functions: includes `fcntl.h`, `tst_test.h`, `lapi/openat2.h`; exercises `openat2`, `fcntl`; defines `setup`, `run`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_RDONLY`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_NO_XDEV`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the LTP runner. Named case hints include `open /proc/version`, `open magiclinks`, `open symlinks`, `resolve-no-xdev`, `resolve-no-magiclinks`, `resolve-no-symlinks`, `resolve-beneath`, `resolve-no-in-root`. Error-path expectations include `ELOOP`, `ENOENT`, `EXDEV`.

State and persistence behavior: Runtime state is `struct open_how` resolution policy, directory file descriptors, symlink/magic-link fixtures, mount boundaries, and file descriptors returned by the raw `openat2` syscall.

Dependencies and integration points: Depends on `lapi/openat2.h`, raw syscall availability, `struct open_how`, root/mount fixtures for resolution flags, and Linux 5.6-era openat2 semantics. Direct include dependencies include `fcntl.h`, `tst_test.h`, `lapi/openat2.h`.

Risks and test signals: Resolution-constraint failures depend on exact kernel `openat2()` semantics and fixture layout; unsupported kernels must skip rather than fail. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `ELOOP`, `ENOENT`, `EXDEV`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c

Purpose: Basic :manpage:`openat2(2)` test to check various failures.

Important APIs/types/functions: includes `fcntl.h`, `tst_test.h`, `lapi/openat2.h`; exercises `openat2`, `fcntl`; defines `setup`, `run`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the LTP runner. Named case hints include `invalid-dfd`, `invalid-pathname`, `invalid-flags`, `invalid-mode`, `invalid-resolve`, `invalid-size-zero`, `invalid-size-small`, `invalid-size-big`, `invalid-size-big-with-pad`. Error-path expectations include `E2BIG`, `EBADF`, `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is `struct open_how` resolution policy, directory file descriptors, symlink/magic-link fixtures, mount boundaries, and file descriptors returned by the raw `openat2` syscall.

Dependencies and integration points: Depends on `lapi/openat2.h`, raw syscall availability, `struct open_how`, root/mount fixtures for resolution flags, and Linux 5.6-era openat2 semantics. Direct include dependencies include `fcntl.h`, `tst_test.h`, `lapi/openat2.h`.

Risks and test signals: Resolution-constraint failures depend on exact kernel `openat2()` semantics and fixture layout; unsupported kernels must skip rather than fail. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `E2BIG`, `EBADF`, `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat2/openat203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pathconf` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf01.c

Purpose: Authors: William Roske, Dave Fenner Check the basic functionality of the pathconf(2) system call.

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`; exercises `pathconf`; defines `verify_pathconf`.

Control flow centers on `verify_pathconf`. The `struct tst_test` registration wires `.needs_tmpdir`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is filesystem/path configuration queried from temporary files, directories, FIFOs, pipes, and error-path pathname fixtures.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf02.c

Purpose: Verify that, - pathconf() fails with ENOTDIR if a component used as a directory in path is not in fact a directory. - pathconf() fails with ENOENT if path is an empty string. - pathconf() fails with ENAMETOOLONG if path is too long. - pathconf() fails with EINVA if name is invalid. - pathconf() fails with EACCES if search permission is denied for one of the directories in the path prefix of path. - pathconf() fails with ELOOP if too many symbolic links were encountered while resolving path.

Important APIs/types/functions: includes `stdlib.h`, `pwd.h`, `tst_test.h`; exercises `pathconf`; defines `verify_fpathconf`, `setup`.

Control flow centers on `verify_fpathconf`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir`, `.needs_root` into the LTP runner. Error-path expectations include `EACCES`, `EINVA`, `EINVAL`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem/path configuration queried from temporary files, directories, FIFOs, pipes, and error-path pathname fixtures.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `pwd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EACCES`, `EINVA`, `EINVAL`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pathconf/pathconf02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pause/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pause` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause01.c

Purpose: Verify that, pause() returns -1 and sets errno to EINTR after receipt of a signal which is caught by the calling process.

Important APIs/types/functions: includes `tst_test.h`; exercises `pause`; defines `sig_handler`, `do_child`, `run`, `run_all`.

Control flow centers on `sig_handler`, `do_child`, `run`, `run_all`. The `struct tst_test` registration wires `.forks_child`, `.test_all` into the LTP runner. Error-path expectations include `EINTR`.

State and persistence behavior: Runtime state is signal delivery to the current process and the fact that `pause()` only returns after an unblocked handled signal interrupts it.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FAIL`, `TST_PROCESS_STATE_WAIT`; checks errno values `EINTR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause02.c

Purpose: 07/2001 Ported by Wayne Boyer Verifies that pause() does not return after proccess receives a SIGKILL signal.

Important APIs/types/functions: includes `tst_test.h`; exercises `pause`; defines `do_child`, `run`.

Control flow centers on `do_child`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is signal delivery to the current process and the fact that `pause()` only returns after an unblocked handled signal interrupts it.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_PROCESS_STATE_WAIT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pause/pause02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir	?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `perf_event_open` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h

Purpose: Shared wrapper header for perf event tests; it exposes `perf_event_open()` through the raw syscall and centralizes perf-related constants used by sibling tests.

Important APIs/types/functions: includes `linux/types.h`, `linux/perf_event.h`, `inttypes.h`; defines `perf_event_open`; touches `perf_event_open`, `raw syscall path`; uses constants/macros such as `ENODEV`, `ENOENT`, `TBROK`, `TCONF`, `TERRNO`, `TINFO`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `linux/types.h`, `linux/perf_event.h`, `inttypes.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open01.c

Purpose: / /* Ingo Molnar <mingo@elte.hu>, 2009

Important APIs/types/functions: includes `sys/types.h`, `sys/ioctl.h`, `sys/stat.h`, `sys/time.h`, `sys/uio.h`, `linux/unistd.h`, `assert.h`, `unistd.h`; exercises `perf_event_open`, `read`, `write`, `fcntl`, `ioctl`, `raw syscall path`; defines `setup`, `cleanup`, `verify`, `main`, `perf_event_open`, `do_work`.

Control flow centers on `setup`, `cleanup`, `verify`, `main`, `perf_event_open`, `do_work`. Error-path expectations include `EINVAL`, `ENODEV`, `ENOENT`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `sys/types.h`, `sys/ioctl.h`, `sys/stat.h`, `sys/time.h`, `sys/uio.h`, `linux/unistd.h`.

Risks and test signals: Perf tests are sensitive to kernel perf permissions, PMU availability, virtualization, CPU scheduling, and multiplexing precision. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`, `TTERRNO`; checks errno values `EINVAL`, `ENODEV`, `ENOENT`, `EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c

Purpose: Here's a little test program that checks whether software counters (specifically, the task clock counter) work correctly when they're in a group with hardware counters. What it does is to create several groups, each with one hardware counter, counting instructions, plus a task clock counter. It needs to know an upper bound N on the number of hardware counters you have (N defaults to 8), and it creates N+4 groups to force them to be multiplexed. It also creates an overall task clock counter. Then it spins for a while, and then stops all the counters and reads them. It takes the total of the task clock counters in

Important APIs/types/functions: includes `errno.h`, `sched.h`, `signal.h`, `stddef.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`; exercises `perf_event_open`, `prctl`, `read`, `ioctl`, `sched_setaffinity`; defines `all_counters_set`, `alarm_handler`, `bench_work`, `do_work`, `count_hardware_counters`, `bind_to_current_cpu`, `setup`, `cleanup`, `verify`; uses flags/constants `PR_TASK_PERF_EVENTS_DISABLE`, `PR_TASK_PERF_EVENTS_ENABLE`.

Control flow centers on `all_counters_set`, `alarm_handler`, `bench_work`, `do_work`, `count_hardware_counters`, `bind_to_current_cpu`, `setup`, `cleanup`, `verify`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.needs_root`, `.timeout` into the LTP runner.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `errno.h`, `sched.h`, `signal.h`, `stddef.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: Perf tests are sensitive to kernel perf permissions, PMU availability, virtualization, CPU scheduling, and multiplexing precision. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c

Purpose: CVE-2020-25704 Check for memory leak in PERF_EVENT_IOC_SET_FILTER ioctl command. Fixed in: commit 7bdb157cdebbf95a1cd94ed2e01b338714075d00 Date: Wed Nov 4 08:23:22 2020 +0300 perf/core: Fix a memory leak in perf_event_parse_addr_filter() intel_pt is currently the only event source that supports filters Check how fast we can do the iterations after 5 seconds of runtime. If the rate is too small to complete for current runtime then stop the test.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `tst_timer.h`, `lapi/syscalls.h`, `perf_event_open.h`; exercises `perf_event_open`, `ioctl`; defines `setup`, `check_progress`, `run`, `cleanup`.

Control flow centers on `setup`, `check_progress`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root` into the LTP runner. Named case hints include `linux-git`, `CVE`.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `config.h`, `tst_test.h`, `tst_timer.h`, `lapi/syscalls.h`, `perf_event_open.h`.

Risks and test signals: Perf tests are sensitive to kernel perf permissions, PMU availability, virtualization, CPU scheduling, and multiplexing precision. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/personality/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `personality` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c

Purpose: 03/2001 - Written by Wayne Boyer Tries to set different personalities. We set the personality in a child process since it's not guaranteed that we can set it back in some cases. I.e. PER_LINUX32 cannot be unset on some 64 bit archs.

Important APIs/types/functions: includes `tst_test.h`, `lapi/personality.h`; exercises `personality`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the process execution-domain/personality word, including architecture-specific flags that must be restored after each test.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/personality.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EXPR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c

Purpose: This test checks if select() timeout is not updated when personality with STICKY_TIMEOUTS is used.

Important APIs/types/functions: includes `tst_test.h`, `lapi/personality.h`, `sys/select.h`; exercises `personality`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process execution-domain/personality word, including architecture-specific flags that must be restored after each test.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/personality.h`, `sys/select.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TST_EXP_EQ_LI`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pidfd_getfd` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c

Purpose: Basic pidfd_getfd() test: - the close-on-exec flag is set on the file descriptor returned by pidfd_getfd - use kcmp to check whether a file descriptor idx1 in the process pid1 refers to the same open file description as file descriptor idx2 in the process pid2

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/kcmp.h`, `tst_safe_macros.h`, `lapi/pidfd.h`; exercises `pidfd_getfd`; defines `do_child`, `run`, `setup`, `cleanup`.

Control flow centers on `do_child`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is pidfd references to child processes plus source and duplicated file descriptors guarded by ptrace-style permission checks.

Dependencies and integration points: Depends on pidfd and pidfd_getfd syscall wrappers, forked children, file descriptor passing expectations, and ptrace-like permission policy. Direct include dependencies include `unistd.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/kcmp.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FD_SILENT`, `TST_EXP_VAL_SILENT`, `TST_PROCESS_STATE_WAIT`, `TST_RET`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c

Purpose: Tests basic error handling of the pidfd_open syscall. - EBADF pidfd is not a valid PID file descriptor - EBADF targetfd is not an open file descriptor in the process referred to by pidfd - EINVAL flags is not 0 - ESRCH the process referred to by pidfd does not exist (it has terminated and been waited on) - EPERM the calling process doesn't have PTRACE_MODE_ATTACH_REALCREDS permissions over the process referred to by pidfd

Important APIs/types/functions: includes `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/pidfd.h`; exercises `pidfd_getfd`, `pidfd_open`; defines `setup`, `cleanup`, `run`; uses flags/constants `PTRACE_MODE_ATTACH_REALCREDS`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_root`, `.forks_child` into the LTP runner. Named case hints include `invalid pidfd`, `invalid targetfd`, `invalid flags`, `the process referred to by pidfd doesn't exist`, `lack of required permission`. Error-path expectations include `EBADF`, `EINVAL`, `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is pidfd references to child processes plus source and duplicated file descriptors guarded by ptrace-style permission checks.

Dependencies and integration points: Depends on pidfd and pidfd_getfd syscall wrappers, forked children, file descriptor passing expectations, and ptrace-like permission policy. Direct include dependencies include `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FAIL2`; checks errno values `EBADF`, `EINVAL`, `EPERM`, `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pidfd_open` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c

Purpose: Basic pidfd_open() test: - Fetch the PID of the current process and try to get its file descriptor. - Check that the close-on-exec flag is set on the file descriptor.

Important APIs/types/functions: includes `unistd.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `unistd.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_FD_SILENT`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c

Purpose: Tests basic error handling of the pidfd_open syscall. - ESRCH the process specified by pid does not exist - EINVAL pid is not valid - EINVAL flags is not valid

Important APIs/types/functions: includes `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `setup`, `run`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup` into the LTP runner. Named case hints include `expired pid`, `invalid pid`, `invalid flags`. Error-path expectations include `EINVAL`, `ESRCH`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EINVAL`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c

Purpose: This program opens the PID file descriptor of the child process created with fork(). It then uses poll to monitor the file descriptor for process exit, as indicated by an EPOLLIN event.

Important APIs/types/functions: includes `poll.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`, `poll`, `fork`; defines `run`; uses flags/constants `POLLIN`.

Control flow centers on `run`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child` into the LTP runner. Error-path expectations include `EPOLLIN`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `poll.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FD_SILENT`, `TST_RET`; checks errno values `EPOLLIN`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c

Purpose: Verify that the PIDFD_NONBLOCK flag works with pidfd_open() and that waitid() with a non-blocking pidfd returns EAGAIN.

Important APIs/types/functions: includes `unistd.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`; exercises `pidfd_open`; defines `run`, `setup`, `cleanup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EAGAIN`, `EINVAL`.

State and persistence behavior: Runtime state is live process identity represented as pidfds, polling state when children exit, and error handling for invalid PIDs or flags.

Dependencies and integration points: Depends on pidfd syscall wrappers, fork/wait/poll helpers, kernel pidfd support, and process lifetime handling. Direct include dependencies include `unistd.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_EXP_FAIL`, `TST_EXP_FD_SILENT`, `TST_RET`, `TST_RETRY_FUNC`, `TST_RETVAL_EQ0`, `TTERRNO`; checks errno values `EAGAIN`, `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/pidfd_open04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk; pidfd_send_signal01: CFLAGS += -pthread`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local compiler/preprocessor flags. It is the build entry point for the `pidfd_send_signal` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c

Purpose: Tests if the pidfd_send_signal syscall behaves like rt_sigqueueinfo when a pointer to a siginfo_t struct is passed.

Important APIs/types/functions: includes `signal.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `received_signal`, `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_DIRECTORY`.

Control flow centers on `received_signal`, `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `signal.h`, `stdlib.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c

Purpose: Tests basic error handling of the pidfd_send_signal system call. - EINVAL Pass invalid flag value to syscall (value chosen to be unlikely to collide with future extensions) - EBADF Pass a file descriptor that is corresponding to a regular file instead of a pid directory - EINVAL Pass a signal that is different from the one used to initialize the siginfo_t struct - EPERM Try to send signal to other process (init) with missing privileges

Important APIs/types/functions: includes `pwd.h`, `signal.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `pwd.h`, `signal.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TTERRNO`; checks errno values `EBADF`, `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c

Purpose: This test checks if the pidfd_send_signal syscall wrongfully sends a signal to a new process which inherited the PID of the actual target process. In order to do so it is necessary to start a process with a pre- determined PID. This is accomplished by writing to the /proc/sys/kernel/ns_last_pid file. By utilizing this, this test forks two children with the same PID. It is then checked, if the syscall will send a signal to the second child using the pidfd of the first one.

Important APIs/types/functions: includes `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `get_inode_number`, `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_DIRECTORY`.

Control flow centers on `get_inode_number`, `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.forks_child` into the LTP runner. Error-path expectations include `ESRCH`.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; FILTER_OUT_MAKE_TARGETS	+= pipe06 pipe07; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pipe` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe01.c

Purpose: Basic test for pipe().

Important APIs/types/functions: includes `errno.h`, `string.h`, `tst_test.h`; exercises `pipe`, `read`; defines `verify_pipe`.

Control flow centers on `verify_pipe`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `errno.h`, `string.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c

Purpose: Check that if a child has a "broken pipe", this information is transmitted to the waiting parent.

Important APIs/types/functions: includes `errno.h`, `string.h`, `unistd.h`, `stdlib.h`, `sys/wait.h`, `tst_test.h`; exercises `pipe`, `read`, `write`; defines `do_child`, `verify_pipe`.

Control flow centers on `do_child`, `verify_pipe`. The `struct tst_test` registration wires `.forks_child`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `errno.h`, `string.h`, `unistd.h`, `stdlib.h`, `sys/wait.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_RET`, `TTERRNO`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c

Purpose: Verify that, an attempt to write to the read end of a pipe fails with EBADF and an attempt to read from the write end of a pipe also fails with EBADF.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `read`, `write`; defines `verify_pipe`, `cleanup`.

Control flow centers on `verify_pipe`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the LTP runner. Error-path expectations include `EBADF`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EBADF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c

Purpose: Legacy pipe test checking that writer children blocked or busy writing to a pipe remain killable and are reaped by the parent.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `test.h`, `tso_safe_macros.h`; exercises `pipe`, `fork`, `waitpid`, `read`, `write`; defines `setup`, `cleanup`, `c1func`, `c2func`, `alarmfunc`, `do_read`, `main`.

Control flow centers on `setup`, `cleanup`, `c1func`, `c2func`, `alarmfunc`, `do_read`, `main`. Error-path expectations include `EINTR`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EINTR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c

Purpose: Legacy negative pipe test that passes an invalid userspace descriptor array pointer and expects `pipe()` to fail with `EFAULT`.

Important APIs/types/functions: includes `fcntl.h`, `errno.h`, `setjmp.h`, `test.h`; exercises `pipe`, `write`, `fcntl`; defines `setup`, `cleanup`, `sig11_handler`, `main`.

Control flow centers on `setup`, `cleanup`, `sig11_handler`, `main`. Error-path expectations include `EFAULT`, `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `fcntl.h`, `errno.h`, `setjmp.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EFAULT`, `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, pipe(2) syscall fails with errno EMFILE when limit on the number of open file descriptors has been reached.

Important APIs/types/functions: includes `tst_test.h`, `stdlib.h`; exercises `pipe`; defines `setup`, `run`, `cleanup`.

Control flow centers on `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TINFO`, `TST_EXP_FAIL`; checks errno values `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c

Purpose: Ported by Paul Larson Verify that, pipe(2) syscall can open the maximum number of file descriptors permitted.

Important APIs/types/functions: includes `tst_test.h`, `stdlib.h`; exercises `pipe`; defines `record_open_fds`, `setup`, `run`, `cleanup`.

Control flow centers on `record_open_fds`, `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner. Error-path expectations include `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TINFO`, `TST_EXP_EQ_LI`, `TST_RET`; checks errno values `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, on any attempt to write to a pipe which is closed for reading will generate a SIGPIPE signal and write will fail with EPIPE errno.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `write`; defines `sighandler`, `run`, `setup`, `cleanup`.

Control flow centers on `sighandler`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the LTP runner. Error-path expectations include `EPIPE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EQ_LI`, `TST_EXP_FAIL2_SILENT`; checks errno values `EPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c

Purpose: Legacy functional pipe test checking that two writer children can use the same pipe and the parent receives data from both writers.

Important APIs/types/functions: includes `unistd.h`, `signal.h`, `sys/wait.h`, `errno.h`, `test.h`, `tso_safe_macros.h`; exercises `pipe`, `fork`, `read`, `write`; defines `setup`, `cleanup`, `do_read`, `main`.

Control flow centers on `setup`, `cleanup`, `do_read`, `main`. Error-path expectations include `EINTR`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `signal.h`, `sys/wait.h`, `errno.h`, `test.h`, `tso_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EINTR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c

Purpose: 07/2001 Ported by Wayne Boyer Verify that, when a parent process opens a pipe, a child process can read from it.

Important APIs/types/functions: includes `stdio.h`, `tst_test.h`; exercises `pipe`, `read`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.forks_child`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `stdio.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EQ_LU`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c

Purpose: Ported to LTP: Wayne Boyer Check if many children can read what is written to a pipe by the parent. ALGORITHM For a different nchilds number: 1. Open a pipe and write nchilds * (PIPE_BUF/nchilds) bytes into it 2. Fork nchilds children 3. Each child reads PIPE_BUF/nchilds characters and checks that the bytes read are correct

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`; exercises `pipe`, `read`, `write`; defines `do_child`, `run`.

Control flow centers on `do_child`, `run`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c

Purpose: Test Description: A pipe has a limited capacity. If the pipe with non block mode is full, then a write(2) will fail and get EAGAIN error. Otherwise, from 1 to PIPE_BUF bytes may be written. For a non-empty(unaligned page size) pipe, the sequent large size write(>page_size)will use new pages. So it may exist a hole in page and we print this value instead of checking it.

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`; exercises `pipe`, `write`, `fcntl`; defines `verify_pipe`, `cleanup`, `setup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `verify_pipe`, `cleanup`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.cleanup`, `.tcnt` into the LTP runner. Error-path expectations include `EAGAIN`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c

Purpose: Test Description: This case is designed to test whether pipe can wakeup all readers when last writer closes. This is also a regression test for commit 6551d5c56eb0 ("pipe: make sure to wake up everybody when the last reader/writer closes"). This bug was introduced by commit 0ddad21d3e99 ("pipe: use exclusive waits when reading or writing").

Important APIs/types/functions: includes `unistd.h`, `sys/types.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`; exercises `pipe`, `waitpid`, `read`; defines `do_child`, `verify_pipe`.

Control flow centers on `do_child`, `verify_pipe`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner. Named case hints include `linux-git`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `sys/types.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_PROCESS_STATE_WAIT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c

Purpose: Verify that, if the write end of a pipe is closed, then a process reading from the pipe will see end-of-file (i.e., read() returns 0) once it has read all remaining data in the pipe.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `read`, `write`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_VAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c

Purpose: This is a regression test for hangup on pipe operations. See https://www.spinics.net/lists/linux-api/msg49762.html for additional context. It tests that pipe operations do not block indefinitely when going to the soft limit on the total size of all pipes created by a single user.

Important APIs/types/functions: includes `fcntl.h`, `stdlib.h`, `unistd.h`, `tst_test.h`, `tst_safe_stdio.h`, `tst_safe_macros.h`; exercises `pipe`, `fcntl`; defines `run`, `setup`, `cleanup`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the LTP runner. Named case hints include `linux-git`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `fcntl.h`, `stdlib.h`, `unistd.h`, `tst_test.h`, `tst_safe_stdio.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pipe2` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c

Purpose: History: Created - Jan 13 2009 - Ulrich Drepper <drepper@redhat.com> Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> Converted into new api - Apri 15 2020 - Yang Xu <xuyang2018.jy@cn.fujitsu.com> It may get EINVAL error on older kernel because this flag was introduced since kernel 3.4. We only test flag in write end because this flag was used to make pipe buffer marked with the PIPE_BUF_FLAG_PACKET flag. In read end, kernel also checks buffer flag instead of O_DIRECT. So it make no sense to check this flag in fds[0].

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe2`, `pipe`, `read`, `write`, `fcntl`; defines `cleanup`, `verify_pipe2`; uses flags/constants `O_CLOEXEC`, `O_DIRECT`, `O_NONBLOCK`.

Control flow centers on `cleanup`, `verify_pipe2`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.cleanup` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `unistd.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c

Purpose: This case is designed to test the basic functionality about the O_CLOEXEC flag of pipe2.

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe2`, `execlp`, `fcntl`; defines `cleanup`, `verify_pipe2`; uses flags/constants `O_CLOEXEC`.

Control flow centers on `cleanup`, `verify_pipe2`. The `struct tst_test` registration wires `.cleanup`, `.forks_child`, `.needs_root`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c

Purpose: Companion exec helper for the pipe2 close-on-exec test; it attempts descriptor use after exec to distinguish inherited fds from `O_CLOEXEC` fds.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `fcntl.h`; exercises `fcntl`; defines `main`.

Control flow centers on `main`. Error-path expectations include `EBADF`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: checks errno values `EBADF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c

Purpose: Test Description: This Program tests getting and setting the pipe size. It also tests what happen when you write to a full pipe depending on whether O_NONBLOCK is set or not. This ensures parent process is still in non-block mode when using -i parameter. Subquent writes hould return -1 and errno set to either EAGAIN or EWOULDBLOCK because pipe is already full. A pipe has two file descriptors. But in the kernel these two file descriptors point to the same pipe. So setting size from first file handle set size for the pipe.

Important APIs/types/functions: includes `stdlib.h`, `features.h`, `unistd.h`, `stdio.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe`, `write`, `fcntl`; defines `test_pipe2`, `setup`, `cleanup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `test_pipe2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.forks_child` into the LTP runner. Error-path expectations include `EAGAIN`, `EWOULDBLOCK`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdlib.h`, `features.h`, `unistd.h`, `stdio.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_PROCESS_STATE_WAIT`; checks errno values `EAGAIN`, `EWOULDBLOCK`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; LDLIBS += $(CAP_LIBS); include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local linker libraries declared by `LDLIBS`. It is the build entry point for the `pivot_root` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c

Purpose: Test consists of a series of steps that allow pivot_root to succeed, which is run when param is NORMAL. All other values tweak one of the steps to induce a failure, and check the errno is as expected. EBUSY new_root or put_old are on the current root file system EINVAL put_old is not underneath new_root Note: if put_old and new_root are on the same fs, pivot_root fails with EBUSY before testing reachability

Important APIs/types/functions: includes `config.h`, `errno.h`, `lapi/syscalls.h`, `sched.h`, `stdlib.h`, `tst_test.h`, `lapi/mount.h`, `sys/capability.h`; exercises `pivot_root`, `mount`, `raw syscall path`; defines `drop_cap_sys_admin`, `run`, `setup`.

Control flow centers on `drop_cap_sys_admin`, `run`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.needs_tmpdir`, `.needs_root`, `.forks_child`, `.setup` into the LTP runner. Error-path expectations include `EBUSY`, `EINVAL`, `ENOTDIR`, `EPERM`.

State and persistence behavior: Runtime state is the process mount namespace root/cwd plus old-root and new-root mountpoints that must be bind-mounted and later unwound.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `errno.h`, `lapi/syscalls.h`, `sched.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EBUSY`, `EINVAL`, `ENOTDIR`, `EPERM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; pkey01: CFLAGS += -falign-functions=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local compiler/preprocessor flags. It is the build entry point for the `pkeys` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c

Purpose: Memory Protection Keys for Userspace (PKU aka PKEYs) is a Skylake-SP server feature that provides a mechanism for enforcing page-based protections, but without requiring modification of the page tables when an application changes protection domains. It works by dedicating 4 previously ignored bits in each page table entry to a "protection key", giving 16 possible keys. Basic method for PKEYs testing: 1. test allocates a pkey(e.g. PKEY_DISABLE_ACCESS) via pkey_alloc() 2. pkey_mprotect() apply this pkey to a piece of memory(buffer) 3. check if access right of the buffer has been changed and take effect 4. remove th

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `errno.h`, `stdlib.h`, `sys/syscall.h`, `sys/mman.h`, `sys/wait.h`, `lapi/pkey.h`; exercises `pkey_alloc`, `pkey_free`, `pkey_mprotect`, `read`, `write`; defines `setup`, `__attribute__`, `pkey_test`, `verify_pkey`; uses flags/constants `O_CREAT`, `O_RDWR`, `PKEY_DISABLE_ACCESS`, `PKEY_DISABLE_EXECUTE`, `PKEY_DISABLE_WRITE`.

Control flow centers on `setup`, `__attribute__`, `pkey_test`, `verify_pkey`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.needs_tmpdir`, `.forks_child`, `.test`, `.setup`, `.hugepages` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is allocated protection keys, PKRU-enforced permissions, mmap-backed buffers, optional huge pages, and forked children used to provoke SIGSEGV safely.

Dependencies and integration points: Depends on `lapi/pkey.h`, x86/architecture PKU support, root privileges, optional huge pages, mmap/mprotect, and forked SIGSEGV probes. Direct include dependencies include `stdio.h`, `unistd.h`, `errno.h`, `stdlib.h`, `sys/syscall.h`, `sys/mman.h`.

Risks and test signals: PKU behavior is architecture-specific and deliberately causes SIGSEGV in children; execute-disable and huge-page cases may be unsupported. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_REQUEST`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; poll02: LDLIBS+=-lrt; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local linker libraries declared by `LDLIBS`. It is the build entry point for the `poll` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c

Purpose: Ported to LTP: Wayne Boyer Check that :manpage:`poll(2)` works for POLLOUT and POLLIN and that revents is set correctly.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_test.h`; exercises `poll`, `fcntl`; defines `verify_pollout`, `verify_pollin`, `verify_poll`, `setup`, `cleanup`; uses flags/constants `POLLIN`, `POLLOUT`.

Control flow centers on `verify_pollout`, `verify_pollin`, `verify_poll`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_EXPR`, `TST_EXP_VAL`, `TST_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c

Purpose: Check that :manpage:`poll(2)` timeouts correctly.

Important APIs/types/functions: includes `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_timer_test.h`; exercises `poll`, `fcntl`; defines `sample_fn`, `setup`, `cleanup`; uses flags/constants `POLLIN`.

Control flow centers on `sample_fn`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `fcntl.h`, `sys/wait.h`, `sys/poll.h`, `tst_timer_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll03.c

Purpose: Check that poll() reports POLLHUP on a pipe read end after the write end has been closed.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`; exercises `pipe`, `poll`, `read`, `write`; defines `verify_pollhup`, `setup`, `cleanup`; uses flags/constants `POLLHUP`, `POLLIN`.

Control flow centers on `verify_pollhup`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_EXPR`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c

Purpose: Check that poll() reports POLLNVAL for invalid file descriptors.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`; exercises `poll`; defines `verify_pollnval`, `setup`, `cleanup`; uses flags/constants `POLLIN`, `POLLNVAL`.

Control flow centers on `verify_pollnval`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is `struct pollfd` arrays, regular-file and pipe readiness, timeout accounting, signal interruption, invalid descriptors, and `revents` flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `unistd.h`, `errno.h`, `sys/poll.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_EXPR`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/poll/poll04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `ppoll` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c

Purpose: Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Older versions of glibc don't publish this constant's value. test type (enum)

Important APIs/types/functions: includes `errno.h`, `poll.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `tso_signal.h`, `time64_variants.h`; exercises `poll`, `ppoll`, `raw syscall path`; defines `libc_ppoll`, `sys_ppoll`, `sys_ppoll_time64`, `sighandler`, `setup`, `cleanup`, `do_test`; uses flags/constants `O_CREAT`, `O_RDWR`, `POLLIN`, `POLLNVAL`, `POLLOUT`, `POLLPRI`, `POLLRDHUP`.

Control flow centers on `libc_ppoll`, `sys_ppoll`, `sys_ppoll_time64`, `sighandler`, `setup`, `cleanup`, `do_test`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup`, `.cleanup`, `.forks_child`, `.needs_tmpdir` into the LTP runner. Named case hints include `x`, `NORMAL`, `MASK_SIGNAL`, `TIMEOUT`, `FD_ALREADY_CLOSED`, `SEND_SIGINT`, `SEND_SIGINT_RACE_TEST`, `INVALID_NFDS`, `INVALID_FDS`. Error-path expectations include `EBADF`, `EFAULT`, `EINTR`, `EINVAL`, `ENOMEM`.

State and persistence behavior: Runtime state is `struct pollfd` arrays, optional signal masks atomically installed by `ppoll`, timespec variants, and signal-generator children.

Dependencies and integration points: Depends on time64 variants, raw ppoll syscall numbers, signal-generator helpers, pollfd fixtures, and sigset/timespec ABI conversion. Direct include dependencies include `errno.h`, `poll.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`.

Risks and test signals: Signal and timeout races are intentional; variants must preserve sigset and timespec ABI handling across libc, old syscall, and time64 syscall paths. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`; checks errno values `EBADF`, `EFAULT`, `EINTR`, `EINVAL`, `ENOMEM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ppoll/ppoll01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; prctl07: LDLIBS += $(CAP_LIBS); prctl09: LDLIBS += -lrt; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus local linker libraries declared by `LDLIBS`. It is the build entry point for the `prctl` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c

Purpose: Basic test for PR_SET_PDEATHSIG/PR_GET_PDEATHSIG Use PR_SET_PDEATHSIG to set SIGUSR2 signal and PR_GET_PDEATHSIG should receive this signal.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`; exercises `prctl`; defines `verify_prctl`; uses flags/constants `PR_GET_PDEATHSIG`, `PR_SET_PDEATHSIG`.

Control flow centers on `verify_prctl`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c

Purpose: - EINVAL when an invalid value is given for option - EINVAL when option is PR_SET_PDEATHSIG & arg2 is not zero or a valid signal number - EINVAL when option is PR_SET_DUMPABLE & arg2 is neither SUID_DUMP_DISABLE nor SUID_DUMP_USER - EFAULT when arg2 is an invalid address - EFAULT when option is PR_SET_SECCOMP & arg2 is SECCOMP_MODE_FILTER & arg3 is an invalid address - EACCES when option is PR_SET_SECCOMP & arg2 is SECCOMP_MODE_FILTER & the process does not have the CAP_SYS_ADMIN capability - EINVAL when option is PR_SET_TIMING & arg2 is not PR_TIMING_STATISTICAL - EINVAL when option is PR_SET_NO_NEW_PRIVS & arg2

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/prctl.h`, `linux/filter.h`, `linux/capability.h`, `unistd.h`, `stdlib.h`, `stddef.h`; exercises `prctl`; defines `verify_prctl`, `setup`; uses flags/constants `PR_CAPBSET_DROP`, `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_LOWER`, `PR_CAP_AMBIENT_RAISE`, `PR_GET_NO_NEW_PRIVS`, `PR_GET_SECCOMP`, `PR_GET_SPECULATION_CTRL`, `PR_GET_THP_DISABLE`, `PR_SET_DUMPABLE`, `PR_SET_NAME`, `PR_SET_NO_NEW_PRIVS`, `PR_SET_PDEATHSIG`.

Control flow centers on `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test`, `.caps` into the LTP runner. Error-path expectations include `EACCES`, `EFAULT`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `signal.h`, `sys/prctl.h`, `linux/filter.h`, `linux/capability.h`, `unistd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CAP`, `TST_CAP_DROP`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EACCES`, `EFAULT`, `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c

Purpose: Test PR_SET_CHILD_SUBREAPER and PR_GET_CHILD_SUBREAPER of prctl(2). - If PR_SET_CHILD_SUBREAPER marks a process as a child subreaper, it fulfills the role of init(1) for its descendant orphaned process. The PPID of its orphaned process will be reparented to the subreaper process, and the subreaper process can receive a SIGCHLD signal and wait(2) on the orphaned process to discover corresponding termination status. - The setting of PR_SET_CHILD_SUBREAPER is not inherited by children reated by fork(2). - PR_GET_CHILD_SUBREAPER can get the setting of PR_SET_CHILD_SUBREAPER. These flags was added by kernel commit ebe

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `unistd.h`, `sys/types.h`, `sys/wait.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`; exercises `prctl`, `fork`; defines `check_get_subreaper`, `verify_prctl`, `sighandler`, `setup`; uses flags/constants `PR_GET_CHILD_SUBREAPER`, `PR_SET_CHILD_SUBREAPER`.

Control flow centers on `check_get_subreaper`, `verify_prctl`, `sighandler`, `setup`. The `struct tst_test` registration wires `.setup`, `.forks_child`, `.test_all` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `stdlib.h`, `unistd.h`, `sys/types.h`, `sys/wait.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c

Purpose: Test PR_GET_NAME and PR_SET_NAME of prctl(2). - Set the name of the calling thread, the name can be up to 16 bytes long, including the terminating null byte. If exceeds 16 bytes, the string is silently truncated. - Return the name of the calling thread, the buffer should allow space for up to 16 bytes, the returned string will be null-terminated. - Check /proc/self/task/[tid]/comm and /proc/self/comm name whether matches the thread name.

Important APIs/types/functions: includes `sys/prctl.h`, `string.h`, `stdio.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/prctl.h`; exercises `prctl`, `raw syscall path`; defines `verify_prctl`; uses flags/constants `PR_GET_NAME`, `PR_SET_NAME`.

Control flow centers on `verify_prctl`. The `struct tst_test` registration wires `.test`, `.tcnt` into the LTP runner. Named case hints include `prctl05_test`, `prctl05_test_xxxxx`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `string.h`, `stdio.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/prctl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ASSERT_STR`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c

Purpose: Test PR_GET_NO_NEW_PRIVS and PR_SET_NO_NEW_PRIVS of prctl(2). - Return the value of the no_new_privs bit for the calling thread. A value of 0 indicates the regular execve(2) behavior. A value of 1 indicates execve(2) will operate in the privilege-restricting mode. - With no_new_privs set to 1, diables privilege granting operations at execve-time. For example, a process will not be able to execute a setuid binary to change their uid or gid if this bit is set. The same is true for file capabilities. - The setting of this bit is inherited by children created by fork(2), and preserved across execve(2). We also check

Important APIs/types/functions: includes `prctl06.h`; exercises `prctl`, `fork`, `execve`; defines `do_prctl`, `verify_prctl`, `setup`; uses flags/constants `PR_GET`, `PR_GET_NO_NEW_PRIVS`, `PR_SET_NO_NEW_PRIVS`.

Control flow centers on `do_prctl`, `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child`, `.needs_root`, `.mount_device`, `.mntpoint` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `prctl06.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h

Purpose: Shared constants and helpers for the `prctl06` no-new-privs/seccomp exec tests.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `stdlib.h`, `sys/prctl.h`, `pwd.h`, `sys/types.h`, `unistd.h`, `lapi/prctl.h`; defines `check_no_new_privs`; touches `prctl`; uses constants/macros such as `PR_GET_NO_NEW_PRIVS`, `TFAIL`, `TPASS`, `TST_ASSERT_FILE_INT`, `TST_RET`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `stdio.h`, `stdlib.h`, `sys/prctl.h`, `pwd.h`, `sys/types.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c

Purpose: Companion exec target for `prctl06.c`; it observes process attributes across exec so the parent can validate prctl inheritance semantics.

Important APIs/types/functions: includes `prctl06.h`; defines `main`.

Control flow centers on `main`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `prctl06.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_NO_DEFAULT_MAIN`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c

Purpose: Test the PR_CAP_AMBIENT of prctl(2). Reads or changes the ambient capability set of the calling thread, according to the value of arg2, which must be one of the following: - PR_CAP_AMBIENT_RAISE: The capability specified in arg3 is added to the ambient set. The specified capability must already be present in both pE and pI. If we set SECBIT_NO_CAP_AMBIENT_RAISE bit, raise option will be rejected and return EPERM. We also raise a CAP twice. - PR_CAP_AMBIENT_LOWER: The capability specified in arg3 is removed from the ambient set. Even though this cap is not in set, it also should return 0. - PR_CAP_AMBIENT_IS_SET:

Important APIs/types/functions: includes `sys/prctl.h`, `stdlib.h`, `config.h`, `lapi/syscalls.h`, `lapi/prctl.h`, `lapi/securebits.h`, `tst_test.h`; exercises `prctl`; defines `check_cap_raise`, `check_cap_is_set`, `check_cap_lower`, `verify_prctl`, `setup`; uses flags/constants `PR_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_CLEAR`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_LORWER`, `PR_CAP_AMBIENT_LOWER`, `PR_CAP_AMBIENT_RAISE`, `PR_SET_SECUREBITS`.

Control flow centers on `check_cap_raise`, `check_cap_is_set`, `check_cap_lower`, `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_root` into the LTP runner. Error-path expectations include `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `stdlib.h`, `config.h`, `lapi/syscalls.h`, `lapi/prctl.h`, `lapi/securebits.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ASSERT_FILE_STR`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl08.c

Purpose: Test PR_GET_TIMERSLACK and PR_SET_TIMERSLACK of prctl(2). - Each thread has two associated timer slack values: a "default" value, and a "current" value. PR_SET_TIMERSLACK sets the "current" timer slack value for the calling thread. - When a new thread is created, the two timer slack values are made the same as the "current" value of the creating thread. - The maximum timer slack value is ULONG_MAX. On 32bit machines, it is a valid value(about 4s). On 64bit machines, it is about 500 years and no person will set this over 4s. prctl return value is int, so we test themaximum value is INT_MAX. - we also check current

Important APIs/types/functions: includes `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `linux/limits.h`, `lapi/syscalls.h`, `lapi/prctl.h`, `tst_test.h`; exercises `prctl`; defines `check_reset_timerslack`, `check_get_timerslack`, `check_inherit_timerslack`, `verify_prctl`, `setup`; uses flags/constants `PR_GET_TIMERSLACK`, `PR_SET_TIMERSLACK`.

Control flow centers on `check_reset_timerslack`, `check_get_timerslack`, `check_inherit_timerslack`, `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `linux/limits.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ASSERT_INT`, `TST_RET`, `TTERRNO`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl09.c

Purpose: This is a timer sample test that timer slack is 200us.

Important APIs/types/functions: includes `errno.h`, `sys/prctl.h`, `lapi/prctl.h`, `tst_timer_test.h`; exercises `prctl`; defines `sample_fn`, `setup`; uses flags/constants `PR_SET_TIMERSLACK`.

Control flow centers on `sample_fn`, `setup`. The `struct tst_test` registration wires `.setup` into the LTP runner.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `sys/prctl.h`, `lapi/prctl.h`, `tst_timer_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c

Purpose: Basic test to test behaviour of PR_GET_TSC and PR_SET_TSC. Set the state of the flag determining whether the timestamp counter can be read by the process. - Pass PR_TSC_ENABLE to arg2 to allow it to be read. - Pass PR_TSC_SIGSEGV to arg2 to generate a SIGSEGV when read. We cannot use "=A", since this would use %rax on x86_64

Important APIs/types/functions: includes `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/prctl.h`; exercises `prctl`, `read`; defines `expected_status`, `verify_prctl`; uses flags/constants `PR_GET_TSC`, `PR_SET_TSC`, `PR_TSC_ENABLE`, `PR_TSC_SIGSEGV`.

Control flow centers on `expected_status`, `verify_prctl`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt` into the LTP runner. Named case hints include `x86`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/prctl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pread/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local compiler/preprocessor flags. It is the build entry point for the `pread` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify the functionality of pread() by writing known data using pwrite() to the file at various specified offsets and later read from the file from various specified offsets, comparing the data read against the data written.

Important APIs/types/functions: includes `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `pread`, `pwrite`, `read`, `write`; defines `l_seek`, `compare_bufers`, `verify_pread`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `l_seek`, `compare_bufers`, `verify_pread`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is file content and descriptor offsets: `pread()` must read from supplied offsets without changing the current file position.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c

Purpose: 07/2001 Ported by Wayne Boyer Tests basic error handling of the pread syscall. - ESPIPE when attempted to read from an unnamed pipe - EINVAL if the specified offset position was invalid - EISDIR when fd refers to a directory

Important APIs/types/functions: includes `fcntl.h`, `stdlib.h`, `tst_test.h`; exercises `pipe`, `pread`, `read`, `fcntl`; defines `verify_pread`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `verify_pread`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.test` into the LTP runner. Error-path expectations include `EINVAL`, `EISDIR`, `ESPIPE`.

State and persistence behavior: Runtime state is file content and descriptor offsets: `pread()` must read from supplied offsets without changing the current file position.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `fcntl.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EINVAL`, `EISDIR`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pread/pread02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local compiler/preprocessor flags. It is the build entry point for the `preadv` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv01.c

Purpose: Testcase to check the basic functionality of the preadv(2). Preadv(2) should succeed to read the expected content of data and after reading the file, the file offset is not changed.

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`; exercises `preadv`, `read`; defines `verify_preadv`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_preadv`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state is vector I/O buffers, file content, offsets, and descriptor position, including error-path descriptors and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c

Purpose: - EINVAL when iov_len is invalid. - EINVAL when the vector count iovcnt is less than zero. - EINVAL when offset is negative. - EFAULT when attempts to read into a invalid address. - EBADF when file descriptor is invalid. - EBADF when file descriptor is not open for reading. - EISDIR when fd refers to a directory. - ESPIPE when fd is associated with a pipe.

Important APIs/types/functions: includes `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`; exercises `pipe`, `preadv`, `read`; defines `verify_preadv`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`.

Control flow centers on `verify_preadv`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `ESPIPE`.

State and persistence behavior: Runtime state is vector I/O buffers, file content, offsets, and descriptor position, including error-path descriptors and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c

Purpose: Check the basic functionality of the preadv(2) for the file opened with O_DIRECT in all filesystem. preadv(2) should succeed to read the expected content of data and after reading the file, the file offset is not changed.

Important APIs/types/functions: includes `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`, `lapi/uio.h`; exercises `preadv`, `mount`, `read`, `ioctl`; defines `verify_direct_preadv`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_DIRECT`, `O_RDWR`.

Control flow centers on `verify_direct_preadv`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is vector I/O buffers, file content, offsets, and descriptor position, including error-path descriptors and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv/preadv03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; preadv203 preadv203_64: CFLAGS += -pthread; preadv203_64: LDFLAGS += -pthread; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local compiler/preprocessor flags. It is the build entry point for the `preadv2` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c

Purpose: Verify the basic functionality of the preadv2(2): 1. If the file offset argument is not -1, preadv2() should succeed in reading the expected content of data and the file offset is not changed after reading. 2. If the file offset argument is -1, preadv2() should succeed in reading the expected content of data and the current file offset is used and changed after reading.

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`; exercises `preadv2`, `read`; defines `verify_preadv2`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_preadv2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c

Purpose: Verify that, preadv2(2) fails and sets errno to 1. EINVAL if iov_len is invalid. 2. EINVAL if the vector count iovcnt is less than zero. 3. EOPNOTSUPP if flag is invalid. 4. EFAULT when attempting to read into an invalid address. 5. EBADF if file descriptor is invalid. 6. EBADF if file descriptor is not open for reading. 7. EISDIR when fd refers to a directory. 8. ESPIPE if fd is associated with a pipe.

Important APIs/types/functions: includes `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`; exercises `pipe`, `preadv2`, `read`; defines `verify_preadv2`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`, `O_WRONLY`.

Control flow centers on `verify_preadv2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `EOPNOTSUPP`, `ESPIPE`.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `EISDIR`, `EOPNOTSUPP`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c

Purpose: This is a basic functional test for RWF_NOWAIT flag, we are attempting to force preadv2() either to return a short read or EAGAIN with three concurently running threads: nowait_reader: reads from a random offset from a random file with RWF_NOWAIT flag and expects to get EAGAIN and short read sooner or later writer_thread: rewrites random file in order to keep the underlying device busy so that pages evicted from cache cannot be faulted immediately cache_dropper: attempts to evict pages from a cache in order for reader to hit evicted page sooner or later

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `stdio.h`, `stdlib.h`, `ctype.h`, `pthread.h`, `tst_test.h`, `tst_safe_pthread.h`; exercises `preadv2`, `pwritev`, `read`, `raw syscall path`; defines `drop_caches`, `verify_short_read`, `verify_preadv2`, `check_preadv2_nowait`, `setup`, `do_cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`, `RWF_NOWAIT`.

Control flow centers on `drop_caches`, `verify_short_read`, `verify_preadv2`, `check_preadv2_nowait`, `setup`, `do_cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.min_runtime`, `.needs_root` into the LTP runner. Error-path expectations include `EAGAIN`, `EBADF`, `EOF`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state extends `preadv` with Linux `RWF_*` flags, cache residency, append/nowait behavior, and threaded I/O pressure for NOWAIT coverage.

Dependencies and integration points: Depends on `lapi/uio.h`, preadv2 syscall/libc wrappers, RWF flag support, mounted filesystems, pthread helpers, and cache-drop privileges for NOWAIT testing. Direct include dependencies include `string.h`, `sys/uio.h`, `stdio.h`, `stdlib.h`, `ctype.h`, `pthread.h`.

Risks and test signals: NOWAIT and HIPRI/RWF behavior varies by filesystem, block device, libc wrapper, and cache pressure, so skips and timing-sensitive failures are expected signals. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_DECLARE_ONCE_FN`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`, `EBADF`, `EOF`, `EOPNOTSUPP`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/preadv2/preadv203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `process_madvise` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h

Purpose: Shared wrapper header for process_madvise tests; it provides raw syscall access and feature detection for kernels/libc without a native wrapper.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `tst_safe_stdio.h`; defines `read_address_mapping`; uses constants/macros such as `SAFE_FCLOSE`, `SAFE_FOPEN`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is a remote process address space referenced through pidfd plus iovec ranges and advice values passed to `process_madvise()`.

Dependencies and integration points: integrates with the LTP test framework, lapi syscall wrappers, and local syscall test sources. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `tst_safe_stdio.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c

Purpose: Allocate anonymous memory pages inside child and reclaim it with MADV_PAGEOUT. Then check if memory pages have been swapped out by looking at smaps information. The advice might be ignored for some pages in the range when it is not applicable, so test passes if swap memory increases after reclaiming memory with MADV_PAGEOUT.

Important APIs/types/functions: includes `sys/mman.h`, `tst_test.h`, `lapi/mmap.h`, `lapi/syscalls.h`, `process_madvise.h`; exercises `process_madvise`, `mmap`, `raw syscall path`; defines `child_alloc`, `setup`, `cleanup`, `run`.

Control flow centers on `child_alloc`, `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.forks_child`, `.needs_root` into the LTP runner. Named case hints include `memory`, `CONFIG_SWAP=y`.

State and persistence behavior: Runtime state is a remote process address space referenced through pidfd plus iovec ranges and advice values passed to `process_madvise()`.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/mman.h`, `tst_test.h`, `lapi/mmap.h`, `lapi/syscalls.h`, `process_madvise.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_EXP_EXPR`, `TST_KB`, `TST_MB`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/profil/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/profil/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `profil` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/profil/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/profil/profil01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/profil/profil01.c

Purpose: Functional `profil()` test that enables PC sampling around the current text address, spins until an alarm fires, and checks that the profiling buffer received concentrated samples.

Important APIs/types/functions: includes `stdio.h`, `signal.h`, `unistd.h`, `errno.h`, `sys/types.h`, `test.h`, `tso_safe_macros.h`, `lapi/abisize.h`; exercises `profil`; defines `alrm_handler`, `__attribute__`, `test_profil`, `main`.

Control flow centers on `alrm_handler`, `__attribute__`, `test_profil`, `main`.

State and persistence behavior: Runtime state is libc/kernel profiling sample buffers and interval-timer-style PC sampling while a busy loop executes.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `signal.h`, `unistd.h`, `errno.h`, `sys/types.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ABI32`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/profil/profil01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pselect/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; LDLIBS			+= -lpthread -lrt; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local linker libraries declared by `LDLIBS`, plus local compiler/preprocessor flags. It is the build entry point for the `pselect` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect01.c

Purpose: LTP coverage for the `pselect` syscall/API in `pselect01.c`.

Important APIs/types/functions: includes `sys/select.h`, `sys/time.h`, `sys/types.h`, `errno.h`, `tst_timer_test.h`; exercises `pselect`; defines `sample_fn`.

Control flow centers on `sample_fn`.

State and persistence behavior: Runtime state is `fd_set` readiness, signal masks, pselect timeout values, and child processes used to deliver signals or produce I/O.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/select.h`, `sys/time.h`, `sys/types.h`, `errno.h`, `tst_timer_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c

Purpose: Verify that pselect() fails with: - EBADF if a file descriptor that was already closed - EINVAL if nfds was negative - EINVAL if the value contained within timeout was invalid

Important APIs/types/functions: includes `tst_test.h`; exercises `pselect`; defines `setup`, `pselect_verify`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `pselect_verify`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EINVAL`.

State and persistence behavior: Runtime state is `fd_set` readiness, signal masks, pselect timeout values, and child processes used to deliver signals or produce I/O.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EBADF`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect03.c

Purpose: This is basic test for pselect() returning without error.

Important APIs/types/functions: includes `stdio.h`, `fcntl.h`, `sys/select.h`, `sys/time.h`, `sys/types.h`, `time.h`, `unistd.h`, `errno.h`; exercises `pselect`, `fcntl`; defines `verify_pselect`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_pselect`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is `fd_set` readiness, signal masks, pselect timeout values, and child processes used to deliver signals or produce I/O.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdio.h`, `fcntl.h`, `sys/select.h`, `sys/time.h`, `sys/types.h`, `time.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pselect/pselect03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `ptrace` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c

Purpose: Ported to new library: Jorik Cronenberg <jcronenberg@suse.de> Test the functionality of ptrace() for PTRACE_TRACEME in combination with PTRACE_KILL and PTRACE_CONT requests. Forked child does ptrace(PTRACE_TRACEME, ...). Then a signal is delivered to the child and verified that parent is notified via wait(). Afterwards parent does ptrace(PTRACE_KILL, ..)/ptrace(PTRACE_CONT, ..) and then parent does wait() for child to finish. Test passes if child exits with SIGKILL for PTRACE_KILL. Test passes if child exits normally for PTRACE_CONT. Testing two cases for each: 1) child ignore SIGUSR2 signal 2) using a signal han

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `signal.h`, `sys/wait.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `child_handler`, `parent_handler`, `do_child`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_KILL`, `PTRACE_TRACEME`.

Control flow centers on `child_handler`, `parent_handler`, `do_child`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `errno.h`, `signal.h`, `sys/wait.h`, `sys/ptrace.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c

Purpose: Ptrace register-consistency test that compares `PTRACE_PEEKUSER` register values with `PTRACE_GETREGS` around an `execl()` syscall stop.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `pause`, `ptrace`; defines `verify_ptrace`, `setup`; uses flags/constants `PTRACE_ATTACH`.

Control flow centers on `verify_ptrace`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child`, `.needs_root` into the LTP runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c

Purpose: AUTHOR: Saji Kumar.V.R <saji.kumar@wipro.com> 1) ptrace() returns -1 and sets errno to ESRCH if process with specified pid does not exist. 2) ptrace() returns -1 and sets errno to EPERM if we are trying to trace a process which is already been traced

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `verify_ptrace`, `setup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_TRACEME`.

Control flow centers on `verify_ptrace`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.forks_child` into the LTP runner. Error-path expectations include `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`, `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c

Purpose: make sure PEEKUSER matches GETREGS first compare register states when execl() syscall starts then compare register states after execl() syscall finishes

Important APIs/types/functions: includes `errno.h`, `stdbool.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ptrace.h`, `test.h`, `spawn_ptrace_child.h`; exercises `ptrace`; defines `cleanup`, `compare_registers`, `main`; uses flags/constants `PTRACE_GETREGS`, `PTRACE_KILL`, `PTRACE_PEEKUSER`, `PTRACE_SYSCALL`.

Control flow centers on `cleanup`, `compare_registers`, `main`. Named case hints include `PT_`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `stdbool.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c

Purpose: This test ptraces itself as per arbitrarily specified signals, over 0 to SIGRTMAX range. All other processes should be stopped.

Important APIs/types/functions: includes `stdlib.h`, `sys/ptrace.h`, `lapi/signal.h`, `tst_test.h`; exercises `ptrace`; defines `test_signal`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_TRACEME`.

Control flow centers on `test_signal`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `sys/ptrace.h`, `lapi/signal.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c

Purpose: Check out-of-bound/unaligned addresses given to - {PEEK,POKE}{DATA,TEXT,USER} - {GET,SET}{,FG}REGS - {GET,SET}SIGINFO this should be sizeof(struct user), but that info is only found in the kernel asm/user.h which is not exported to userspace.

Important APIs/types/functions: includes `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `child`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_GETFGREGS`, `PTRACE_GETREGS`, `PTRACE_GETSIGINFO`, `PTRACE_PEEKDATA`, `PTRACE_PEEKTEXT`, `PTRACE_PEEKUSER`, `PTRACE_POKEDATA`, `PTRACE_POKETEXT`, `PTRACE_POKEUSER`, `PTRACE_SETFGREGS`, `PTRACE_SETREGS`, `PTRACE_SETSIGINFO`, `PTRACE_TRACEME`.

Control flow centers on `child`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner. Error-path expectations include `EFAULT`, `EIO`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `sys/ptrace.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TST_EXP_FAIL_ARR`; checks errno values `EFAULT`, `EIO`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c

Purpose: Regression test for commit 814fb7bb7db5 ("x86/fpu: Don't let userspace set bogus xcomp_bv"), or CVE-2017-15537. This bug allowed ptrace(pid, PTRACE_SETREGSET, NT_X86_XSTATE, &iov) to assign a task an invalid FPU state --- specifically, by setting reserved bits in xstate_header.xcomp_bv. This made restoring the FPU registers fail when switching to the task, causing the FPU registers to take on the values from other tasks. To detect the bug, we have a subprocess run a loop checking its xmm0 register for corruption. This detects the case where the FPU state became invalid and the kernel is not restoring the process'

Important APIs/types/functions: includes `tst_test.h`, `errno.h`, `inttypes.h`, `sched.h`, `stdbool.h`, `stdlib.h`, `sys/uio.h`, `sys/wait.h`; exercises `ptrace`; defines `check_regs_loop`, `do_test`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_GETREGSET`, `PTRACE_SETREGSET`.

Control flow centers on `check_regs_loop`, `do_test`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner. Named case hints include `x86_64`, `linux-git`, `CVE`. Error-path expectations include `EAX`, `EBX`, `ECX`, `EDX`, `EINVAL`, `EIO`, `ENODEV`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `tst_test.h`, `errno.h`, `inttypes.h`, `sched.h`, `stdbool.h`, `stdlib.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EAX`, `EBX`, `ECX`, `EDX`, `EINVAL`, `EIO`, `ENODEV`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c

Purpose: CVE-2018-1000199 Test error handling when ptrace(POKEUSER) modified x86 debug registers even when the call returned error. When the bug was present we could create breakpoint in the kernel code, which shoudn't be possible at all. The original CVE caused a kernel crash by setting a breakpoint on do_debug kernel function which, when triggered, caused an infinite loop. However we do not have to crash the kernel in order to assert if kernel has been fixed or not. On newer kernels all we have to do is to try to set a breakpoint, on any kernel address, then read it back and check if the value has been set or not. The o

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`, `tst_safe_stdio.h`; exercises `ptrace`, `read`, `write`; defines `child_main`, `ptrace_try_kern_addr`, `run`, `cleanup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`.

Control flow centers on `child_main`, `ptrace_try_kern_addr`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`, `CVE`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c

Purpose: CVE-2018-8897 Test that the MOV SS instruction touching a ptrace watchpoint followed by INT3 breakpoint is handled correctly by the kernel. Kernel crash fixed in: commit d8ba61ba58c88d5207c1ba2f7d9a2280e7d03be9 Date: Thu Jul 23 15:37:48 2015 -0700 x86/entry/64: Don't use IST entry for #BP stack wait for SIGCONT from parent Main process terminated by tst_brk() with child still paused

Important APIs/types/functions: includes `stdlib.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`; exercises `ptrace`; defines `child_main`, `run`, `cleanup`; uses flags/constants `PTRACE_CONT`, `PTRACE_POKEUSER`, `PTRACE_TRACEME`.

Control flow centers on `child_main`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`, `CVE`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c

Purpose: After fix for CVE-2018-1000199 (see ptrace08.c) subsequent calls to POKEUSER for x86 debug registers were ignored silently. This is a regression test for commit: commit bd14406b78e6daa1ea3c1673bda1ffc9efdeead0 Date: Mon Aug 27 11:12:25 2018 +0200 perf/hw_breakpoint: Modify breakpoint even if the new attr has disabled set Main process terminated by tst_brk() with child still paused

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`; exercises `ptrace`; defines `child_main`, `run`, `cleanup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`, `PTRACE_POKEUSR`.

Control flow centers on `child_main`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c

Purpose: Before kernel 2.6.26 we could not trace init(1) process and ptrace() would fail with EPERM. This case just checks whether we can trace init(1) process successfully. Wait until tracee is stopped by SIGSTOP otherwise detach will fail with ESRCH.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `verify_ptrace`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`.

Control flow centers on `verify_ptrace`. The `struct tst_test` registration wires `.test_all`, `.needs_root` into the LTP runner. Error-path expectations include `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h

Purpose: Reusable legacy ptrace helper that vforks a child, asks it to `PTRACE_TRACEME`, execs itself in child mode, and exposes `pid`, `vptrace()`, and request-name helpers to ptrace tests.

Important APIs/types/functions: includes `spawn_ptrace_child.c`, `errno.h`, `signal.h`, `stdbool.h`, `string.h`, `unistd.h`, `sys/ptrace.h`, `sys/wait.h`; defines `make_a_baby`; touches `ptrace`, `vfork`, `execlp`; uses constants/macros such as `PTRACE_GETFGREGS`, `PTRACE_GETREGS`, `PTRACE_GETSIGINFO`, `PTRACE_SETFGREGS`, `PTRACE_SETREGS`, `PTRACE_SETSIGINFO`, `PTRACE_TRACEME`, `TBROK`, `TERRNO`, `TFAIL`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `spawn_ptrace_child.c`, `errno.h`, `signal.h`, `stdbool.h`, `string.h`, `unistd.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; CPPFLAGS+=		-Wno-error; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local compiler/preprocessor flags. It is the build entry point for the `pwrite` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify the functionality of pwrite() by writing known data using pwrite() to the file at various specified offsets and later read from the file from various specified offsets, comparing the data written aganist the data read using read().

Important APIs/types/functions: includes `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `pwrite`, `read`, `write`; defines `l_seek`, `check_file_contents`, `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `l_seek`, `check_file_contents`, `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c

Purpose: Test basic error handling of the pwrite syscall. - ESPIPE when attempted to write to an unnamed pipe - EINVAL the specified offset position was invalid - EBADF fd is not a valid file descriptor - EBADF fd is not open for writing - EFAULT when attempted to write with buf outside accessible address space sighandler - handle SIGXFSZ This is here to start looking at a failure in test case #2. This test case passes on a machine running RedHat 6.2 but it will fail on a machine running RedHat 7.1.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `string.h`, `tst_test.h`; exercises `pipe`, `pwrite`, `write`; defines `sighandler`, `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `sighandler`, `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`, `.tcnt` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `string.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL2`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite03.c

Purpose: Tests for a special case NULL buffer with size 0 is expected to return 0.

Important APIs/types/functions: includes `errno.h`, `tst_test.h`; exercises `pwrite`; defines `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c

Purpose: ported from SPIE, section2/filesuite/pread_pwrite.c, by Airong Zhang Test the pwrite() system call with O_APPEND. Writing 2k data to the file, close it and reopen it with O_APPEND. POSIX requires that opening a file with the O_APPEND flag should have no effect on the location at which pwrite() writes data. However, on Linux, if a file is opened with O_APPEND, pwrite() appends data to the end of the file, regardless of the value of offset.

Important APIs/types/functions: includes `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `pwrite`, `lseek`; defines `l_seek`, `verify_pwrite`, `setup`, `cleanup`; uses flags/constants `O_APPEND`, `O_CREAT`, `O_RDWR`, `O_TRUNC`.

Control flow centers on `l_seek`, `verify_pwrite`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is file content written at explicit offsets, descriptor offsets that should not move for `pwrite()`, and Linux `O_APPEND` behavior.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `inttypes.h`, `tst_test.h`, `tst_safe_prw.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwrite/pwrite04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(abs_srcdir)/../utils/newer_64.mk; %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`, plus `../utils/newer_64.mk` for 64-bit large-file variants, plus local compiler/preprocessor flags. It is the build entry point for the `pwritev` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev01.c

Purpose: Testcase to check the basic functionality of the pwritev(2). pwritev(2) should succeed to write the expected content of data and after writing the file, the file offset is not changed.

Important APIs/types/functions: includes `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`, `tst_safe_prw.h`; exercises `pwritev`, `write`; defines `verify_pwritev`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_pwritev`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner.

State and persistence behavior: Runtime state is vector write buffers, file content, explicit offsets, descriptor position, and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `string.h`, `sys/uio.h`, `tst_test.h`, `lapi/uio.h`, `tst_safe_prw.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev02.c

Purpose: - EINVAL when iov_len is invalid. - EINVAL when the vector count iovcnt is less than zero. - EINVAL when offset is negative. - EFAULT when attempts to write from a invalid address - EBADF when file descriptor is invalid. - EBADF when file descriptor is not open for writing. - ESPIPE when fd is associated with a pipe.

Important APIs/types/functions: includes `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`; exercises `pipe`, `pwritev`, `write`; defines `verify_pwritev`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `verify_pwritev`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.

State and persistence behavior: Runtime state is vector write buffers, file content, explicit offsets, descriptor position, and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/uio.h`, `unistd.h`, `tst_test.h`, `lapi/uio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev03.c

Purpose: Check the basic functionality of the pwritev(2) for the file opened with O_DIRECT in all filesystem. pwritev(2) should succeed to write the expected content of data and after writing the file, the file offset is not changed.

Important APIs/types/functions: includes `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`, `lapi/uio.h`, `tst_safe_prw.h`; exercises `pwritev`, `mount`, `write`, `ioctl`; defines `verify_direct_pwritev`, `setup`, `cleanup`; uses flags/constants `O_CREAT`, `O_DIRECT`, `O_RDWR`.

Control flow centers on `verify_direct_pwritev`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is vector write buffers, file content, explicit offsets, descriptor position, and direct-I/O alignment where tested.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `stdlib.h`, `string.h`, `sys/uio.h`, `sys/ioctl.h`, `sys/mount.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev/pwritev03.c -->
