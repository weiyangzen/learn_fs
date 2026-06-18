# subset-b-009301 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr03.c

Purpose: Test for returning the current size of the list of extended attribute names, with size specified as zero.

Important APIs/types/functions: listxattr, setxattr, tst_test, TST_RET, tst_res, SAFE_TOUCH, SAFE_SETXATTR, TST_TEST_TCONF; local functions detected: check_suitable_buf, verify_listxattr, setup; key constants/macros: SECURITY_KEY, VALUE, VALUE_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_suitable_buf, verify_listxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr04.c

Purpose: Test reproducer for a bug introduced in 8b0ba61df5a1 ("fs/xattr.c: fix simple_xattr_list to always include security.* xattrs") and fixed in 800d0b9b6a8b (fs/xattr.c: fix simple_xattr_list()). Bug can be reproduced when SELinux and ACL are activated on inodes as following: $ touch testfile $ setfacl -m u:myuser:rwx testfile $ getfattr -dm. /tmp/testfile Segmentation fault (core dumped) The reason why this happens is that simple_xattr_list() always includes security.* xattrs without resetting error flag after security_inode_listsecurity(). This results into an incorrect length of the returned xattr name if POSIX ACL is also applied on the in...

Important APIs/types/functions: listxattr, acl_from_text, acl_set_file, memset, tst_test, tst_brk, tst_res, tst_lsm_enabled, SAFE_TOUCH, tst_tag, TST_TEST_TCONF; local functions detected: verify_xattr, run, setup, cleanup; key constants/macros: ACL_PERM, TEST_FILE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: verify_xattr, run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability; libacl/POSIX ACL support; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: HAVE_SYS_XATTR_H && HAVE_LIBACL
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/Makefile

Purpose: Build recipe for the LTP `llistxattr` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr01.c

Purpose: Basic test for llistxattr(2), retrieves the list of extended attribute names associated with the link itself in the filesystem.

Important APIs/types/functions: llistxattr, lsetxattr, symlink, tst_test, TST_RET, tst_res, SAFE_TOUCH, SAFE_SYMLINK, SAFE_LSETXATTR, TST_TEST_TCONF; local functions detected: has_attribute, verify_llistxattr, setup; key constants/macros: SECURITY_KEY1, SECURITY_KEY2, VALUE, VALUE_SIZE, KEY_SIZE, TESTFILE, SYMLINK

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: has_attribute, verify_llistxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr02.c

Purpose: Verify llistxattr(2) returns -1 and set proper errno: - ERANGE if the size of the list buffer is too small to hold the result - ENOENT if path is an empty string - EFAULT when attempted to read from a invalid address - ENAMETOOLONG if path is longer than allowed

Important APIs/types/functions: llistxattr, lsetxattr, symlink, memset, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_TOUCH, SAFE_SYMLINK, SAFE_LSETXATTR, TST_TEST_TCONF; local functions detected: verify_llistxattr, setup; key constants/macros: SECURITY_KEY, VALUE, VALUE_SIZE, TESTFILE, SYMLINK

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_llistxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr03.c

Purpose: Verify that llistxattr(2) call with zero size returns the current size of the list of extended attribute names, which can be used to determine the size of the buffer that should be supplied in a subsequent llistxattr(2) call.

Important APIs/types/functions: llistxattr, lsetxattr, tst_test, TST_RET, tst_res, SAFE_TOUCH, SAFE_LSETXATTR, TST_TEST_TCONF; local functions detected: check_suitable_buf, verify_llistxattr, setup; key constants/macros: SECURITY_KEY, VALUE, VALUE_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_suitable_buf, verify_llistxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/Makefile

Purpose: Build recipe for the LTP `llseek` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., CFLAGS += -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek01.c

Purpose: Verify that lseek() call succeeds to set the file pointer position to an offset larger than file size limit (RLIMIT_FSIZE). Also, verify that any attempt to write to this location fails.

Important APIs/types/functions: lseek, write, open, setrlimit, tst_test, TST_RET, tst_res, tst_brk, SAFE_SIGACTION, SAFE_SETRLIMIT, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL; local functions detected: verify_llseek, setup; key constants/macros: TEMP_FILE, FILE_MODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_llseek, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; process resource limits adjusted during setup. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek02.c

Purpose: Description: 1) lseek(2) fails and sets errno to EINVAL when whence is invalid. 2) lseek(2) fails ans sets errno to EBADF when fd is not an open file descriptor.

Important APIs/types/functions: lseek, open, close, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_OPEN; local functions detected: verify_llseek, setup; key constants/macros: TEMP_FILE1, TEMP_FILE2, FILE_MODE, SEEK_TOP

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_llseek, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek03.c

Purpose: Description: For each of SEEK_SET, SEEK_CUR and SEEK_END verify that, 1. llseek() succeeds to set file position in the middle of the data. The file offset is checked by reading from a file and comparing the data. 2. llseek() succeeds to set file postion to the end of the data, reading this postion returns 0. 3. llseek() succeeds to set file position after the end of the data, reading from this postion returns 0 as well.

Important APIs/types/functions: lseek, write, read, open, close, creat, memset, tst_test, SAFE_CREAT, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, SAFE_OPEN, SAFE_READ, TST_RET, tst_res; local functions detected: setup, verify_lseek; key constants/macros: TEST_FILE, STR

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, verify_lseek.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Seek somewhere in the middle of data Seek to the end of data
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/Makefile

Purpose: Build recipe for the LTP `lremovexattr` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/lremovexattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/lremovexattr01.c

Purpose: lremovexattr(2) removes the extended attribute identified by a name and associated with a given path in the filesystem. Unlike removexattr(2), lremovexattr(2) removes the attribute from the symbolic link only, and not the file. This test verifies that a simple call to lremovexattr(2) removes, indeed, a previously set attribute key/value from a symbolic link, and the symbolic link _only_. Note: According to attr(5), extended attributes are interpreted differently from regular files, directories and symbolic links. User attributes are only allowed for regular files and directories, thus the need of using trusted. attributes for this test.

Important APIs/types/functions: lremovexattr, lsetxattr, setxattr, getxattr, removexattr, symlink, memset, tst_test, SAFE_SETXATTR, SAFE_LSETXATTR, TST_RET, tst_res, TST_ERR, tst_brk, SAFE_REMOVEXATTR, SAFE_TOUCH, TST_TEST_TCONF; local functions detected: verify_lremovexattr, setup; key constants/macros: ENOATTR, XATTR_KEY, XATTR_VALUE, XATTR_VALUE_SIZE, MNTPOINT, FILENAME, SYMLINK

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_lremovexattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: set attribute on both: file and symlink remove attribute from symlink only
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/lremovexattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/Makefile

Purpose: Build recipe for the LTP `lseek` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek01.c

Purpose: Description: lseek() succeeds to set the specified offset according to whence and read valid data from this location.

Important APIs/types/functions: lseek, write, read, open, close, memset, tst_test, SAFE_READ, TST_RET, tst_res, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE; local functions detected: verify_lseek, setup, cleanup; key constants/macros: WRITE_STR, TFILE

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: verify_lseek, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek02.c

Purpose: DESCRIPTION 1) lseek(2) fails and sets errno to EBADF when fd is invalid. 2) lseek(2) fails ans sets errno to EINVAL when whence is invalid. 3) lseek(2) fails and sets errno to ESPIPE when fd is associated with a pipe or FIFO.

Important APIs/types/functions: lseek, open, close, mknod, pipe, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_OPEN, SAFE_MKFIFO, SAFE_PIPE, SAFE_MKNOD, SAFE_CLOSE; local functions detected: verify_lseek, setup, cleanup; key constants/macros: TFILE, TFIFO1, TFIFO2

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: verify_lseek, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek07.c

Purpose: Description: lseek() succeeds to set the specified offset according to whence and write valid data from this location.

Important APIs/types/functions: lseek, write, read, open, close, memset, tst_test, TST_RET, tst_res, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, SAFE_OPEN, SAFE_READ; local functions detected: verify_lseek, setup, cleanup; key constants/macros: TFILE1, TFILE2, WR_STR1, WR_STR2

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: verify_lseek, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek11.c

Purpose: This case create 3 holes and 4 data fields, every (data) is 12 bytes, every UNIT has UNIT_BLOCKS * block_size bytes. The structure as below: ---------------------------------------------------------------------------------------------- data01suffix (hole) data02suffix (hole) data03suffix (hole) data04sufix ---------------------------------------------------------------------------------------------- |<--- UNIT_BLOCKS blocks --->||<--- UNIT_BLOCKS blocks --->||<--- UNIT_BLOCKS blocks --->|

Important APIs/types/functions: lseek, write, read, open, close, ftruncate, memset, fstat, fsync, pwrite, tst_test, tst_safe_prw, SAFE_CLOSE, SAFE_FSTAT, SAFE_FTRUNCATE, SAFE_PWRITE, SAFE_FSYNC, tst_brk, SAFE_LSEEK, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_OPEN, tst_res, SAFE_READ; local functions detected: cleanup, get_blocksize, write_data, setup, test_lseek; key constants/macros: UNIT_COUNT, UNIT_BLOCKS, FILE_BLOCKS

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, get_blocksize, write_data, setup, test_lseek.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: SEEK from "startblock * block_size - offset", "whence" as the directive whence. startblock * block_size - offset: as offset of lseek() whence: as whence of lseek() data: as the expected result read from file offset. NULL means expect the end of file. count: as the count read from file SEEK_DATA from starting of file
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/Makefile

Purpose: Build recipe for the LTP `lsm` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_common.h

Purpose: Shared header/support code for the `lsm` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: read, open, close, memset, tst_test, tst_res, SAFE_OPEN, SAFE_CLOSE, tst_lsm_enabled, tst_brk; local functions detected: read_proc_attr, count_supported_attr_current, verify_supported_attr_current; key constants/macros: LSM_GET_SELF_ATTR_H

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: read_proc_attr, count_supported_attr_current, verify_supported_attr_current.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr01.c

Purpose: Verify that lsm_get_self_attr syscall is raising errors when invalid data is provided.

Important APIs/types/functions: lsm_get_self_attr, memset, TST_EXP_FAIL, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr02.c

Purpose: Verify that lsm_get_self_attr syscall is acting correctly when ctx is NULL. The syscall can behave in different ways according to the current system status: - if any LSM is running inside the system, the syscall will pass and it will provide a size as big as the attribute - if no LSM(s) are running inside the system, the syscall will fail with -1 return code

Important APIs/types/functions: lsm_get_self_attr, TST_EXP_POSITIVE, TST_EXP_EXPR, TST_EXP_FAIL, SAFE_SYSCONF, tst_test; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr03.c

Purpose: Verify that LSM_ATTR_CURRENT attribute is correctly recognizing the current, active security context of the process. This is done by checking that /proc/self/attr/current matches with the obtained value.

Important APIs/types/functions: lsm_get_self_attr, memset, tst_res, TST_EXP_POSITIVE, TST_RET, TST_EXP_EQ_STR, TST_EXP_EXPR, SAFE_SYSCONF, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules01.c

Purpose: Verify that lsm_list_modules syscall is raising errors when invalid data is provided.

Important APIs/types/functions: lsm_list_modules, memset, TST_EXP_FAIL, SAFE_SYSCONF, tst_test; local functions detected: run, setup; key constants/macros: MAX_LSM_NUM

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules02.c

Purpose: Verify that lsm_list_modules syscall is correctly recognizing LSM(s) enabled inside the system. [Algorithm] - read enabled LSM(s) inside /sys/kernel/security/lsm file - collect LSM IDs using lsm_list_modules syscall - compare the results, verifying that LSM(s) IDs are correct

Important APIs/types/functions: read, open, close, lsm_list_modules, memset, TST_EXP_POSITIVE, TST_EXP_EQ_LI, tst_brk, tst_res, SAFE_SYSCONF, SAFE_OPEN, SAFE_READ, SAFE_CLOSE, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: MAX_LSM_NUM

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; sysfs/securityfs/cgroup files used as capability or state sources. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_* value comparisons; explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_set_self_attr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_set_self_attr01.c

Purpose: Verify that lsm_set_self_attr syscall is raising errors when invalid data is provided.

Important APIs/types/functions: lsm_get_self_attr, lsm_set_self_attr, memcpy, TST_EXP_EXPR, SAFE_SYSCONF, tst_brk, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_* value comparisons; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: just in case lsm_set_self_attr() pass , we won't change LSM configuration for the following process
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_set_self_attr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/Makefile

Purpose: Build recipe for the LTP `lstat` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., %_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat01.c

Purpose: Basic test for lstat(): Tests if lstat() writes correct information about a symlink into the stat structure.

Important APIs/types/functions: lstat, symlink, unlink, memset, tst_test, tst_file, tst_syml, TST_RET, tst_res, SAFE_TOUCH, SAFE_SYMLINK, SAFE_UNLINK; local functions detected: run, setup, cleanup; key constants/macros: TESTFILE, TESTSYML

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat02.c

Purpose: This test verifies that: 1) lstat(2) returns -1 and sets errno to EACCES if search permission is denied on a component of the path prefix. 2) lstat(2) returns -1 and sets errno to ENOENT if the specified file does not exists or empty string. 3) lstat(2) returns -1 and sets errno to EFAULT if pathname points outside user's accessible address space. 4) lstat(2) returns -1 and sets errno to ENAMETOOLONG if the pathname component is too long. 5) lstat(2) returns -1 and sets errno to ENOTDIR if the directory component in pathname is not a directory. 6) lstat(2) returns -1 and sets errno to ELOOP if the pathname has too many symbolic links encou...

Important APIs/types/functions: mkdir, lstat, symlink, seteuid, memset, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_GETPWNAM, SAFE_SETEUID, SAFE_MKDIR, SAFE_TOUCH, SAFE_CHMOD, SAFE_SYMLINK; local functions detected: run, setup, cleanup; key constants/macros: MODE_RWX, MODE_RW0, TEST_DIR, TEST_FILE, TEST_ELOOP, TEST_ENOENT, TEST_EACCES, TEST_ENOTDIR

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Drop privileges for EACCES test NOTE: The ELOOP test is written based on the fact that the consecutive symlinks limit in the kernel is hardwired to 40.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat03.c

Purpose: This test verifies that lstat() provides correct information according with device, access time, block size, ownership, etc. The implementation provides a set of tests which are specific for each one of the `struct stat` used to read file and symlink information.

Important APIs/types/functions: open, close, lstat, stat, symlink, mount, umount, tst_test, SAFE_LSTAT, TST_EXP_EXPR, SAFE_STAT, SAFE_MKFS, tst_device, SAFE_MOUNT, SAFE_TOUCH, SAFE_LINK, SAFE_CHOWN, SAFE_OPEN, tst_fill_fd, TST_KB, SAFE_CLOSE, SAFE_SYMLINK, tst_is_mounted, SAFE_UMOUNT, tst_buffers; local functions detected: run, setup, cleanup; key constants/macros: FILENAME, MNTPOINT, SYMBNAME

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; spare block device or loop-backed LTP device. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: change st_blksize / st_dev change st_uid and st_gid
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/Makefile

Purpose: Build recipe for the LTP `madvise` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., madvise11: CFLAGS += -pthread.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; process/thread timing is part of the signal and can make failures noisy; build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise01.c

Purpose: This is a test case for madvise(2) system call. It tests madvise(2) with combinations of advice values. No error should be returned.

Important APIs/types/functions: write, open, close, mmap, munmap, madvise, mkdir, mount, umount, fstat, tst_test, SAFE_MKDIR, SAFE_MOUNT, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_FSTAT, SAFE_MMAP, SAFE_CLOSE, SAFE_MUNMAP, SAFE_UMOUNT, TST_RET, TST_ERR, tst_res, tst_strerrno; local functions detected: setup, cleanup, verify_madvise; key constants/macros: TMP_DIR, TEST_FILE, STR

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, verify_madvise.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Writing 40 KB of random data into this file [32 * 1280 = 40960] Map the input file into shared memory
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise02.c

Purpose: This is a test for the madvise(2) system call. It is intended to provide a complete exposure of the system call. It tests madvise(2) for all error conditions to occur correctly. (A) Test Case for EINVAL 1. start is not page-aligned 2. advice is not a valid value 3. application is attempting to release locked or shared pages (with MADV_DONTNEED) 4. MADV_MERGEABLE or MADV_UNMERGEABLE was specified in advice, but the kernel was not configured with CONFIG_KSM. 8|9. The MADV_FREE & MADV_WIPEONFORK operation can be applied only to private anonymous pages. (B) Test Case for ENOMEM 5|6. addresses in the specified range are not currently mapped or...

Important APIs/types/functions: write, open, close, mmap, munmap, mlock, madvise, fstat, tst_test, tst_brk, tst_kvercmp, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_FSTAT, SAFE_MMAP, SAFE_MALLOC, SAFE_MUNMAP, SAFE_CLOSE, tst_res, TST_RET, TST_ERR, tst_strerrno; local functions detected: tcases_filter, setup, advice_test, cleanup; key constants/macros: MAP_SIZE, TEST_FILE, STR, TCASE

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: tcases_filter, setup, advice_test, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: kernel configured with CONFIG_KSM, skip EINVAL test for MADV_MERGEABLE. In kernel commit 1998cc0, madvise(MADV_WILLNEED) to anon mem doesn't return -EBADF now, as now we support swap prefretch.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise03.c

Purpose: Check that successful madvise(2) MADV_DONTNEED operation will result in zero-fill-on-demand pages for anonymous private mappings.

Important APIs/types/functions: mmap, munmap, madvise, memset, tst_test, TST_RET, tst_brk, tst_res, SAFE_MMAP, SAFE_MUNMAP; local functions detected: run, setup, cleanup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise05.c

Purpose: This is a regression test for madvise(2) system call. It tests kernel for NULL ptr deref Oops fixed by: commit ee53664bda169f519ce3c6a22d378f0b946c8178 Author: Kirill A. Shutemov <kirill.shutemov@linux.intel.com> Date: Fri Dec 20 15:10:03 2013 +0200 mm: Fix NULL pointer dereference in madvise(MADV_WILLNEED) support On buggy kernel with CONFIG_TRANSPARENT_HUGEPAGE=y CONFIG_DEBUG_LOCK_ALLOC=y this testcase should produce Oops and/or be killed. On fixed/good kernel this testcase runs to completion (retcode is 0)

Important APIs/types/functions: mmap, munmap, madvise, mprotect, tst_test, SAFE_MMAP, TST_RET, tst_brk, SAFE_MUNMAP, tst_res, TST_ERR, tst_tag; local functions detected: verify_madvise; key constants/macros: ALLOC_SIZE

Control flow: test_all runs one whole-file scenario; tags link the test to kernel commits/regressions. Local helper functions: verify_madvise.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise06.c

Purpose: Page fault occurs in spite that madvise(WILLNEED) system call is called to prefetch the page. This issue is reproduced by running a program which sequentially accesses to a shared memory and calls madvise(WILLNEED) to the next page on a page fault. This bug is present in all RHEL7 versions. It looks like this was fixed in kernel v3.15 by 55231e5c898c5 ("mm: madvise: fix MADV_WILLNEED on shmem swapouts") Two checks are performed, the first looks at how SwapCache changes during madvise. When the pages are dirtied, about half will be accounted for under Cached and the other half will be moved into Swap. When madvise is run it will cause the p...

Important APIs/types/functions: mmap, munmap, madvise, tst_test, tst_brk, SAFE_CG_HAS, tst_cg, SAFE_CG_SCANF, tst_res, SAFE_FILE_PRINTF, SAFE_READ_MEMINFO, SAFE_CG_PRINTF, SAFE_CG_PRINT, SAFE_FILE_SCANF, SAFE_MMAP, SAFE_FILE_LINES_SCANF, TST_RET, SAFE_MUNMAP, tst_taint_check, TST_TAINT_W, TST_TAINT_D, tst_path_val, TST_SR_SKIP_MISSING, TST_SR_TCONF_RO, TST_MB, tst_tag; local functions detected: check_path, print_cgmem, meminfo_diag, setup, dirty_pages, get_page_fault_num, test_advice_willneed; key constants/macros: CHUNK_SZ, MEM_LIMIT, MEMSW_LIMIT, PASS_THRESHOLD, PASS_THRESHOLD_KB

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; tags link the test to kernel commits/regressions. Local helper functions: check_path, print_cgmem, meminfo_diag, setup, dirty_pages, get_page_fault_num, test_advice_willneed.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state; sysfs/securityfs/cgroup files used as capability or state sources; memory cgroup limits and counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag; configured cgroup memory controller. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise07.c

Purpose: Check that accessing a page marked with MADV_HWPOISON results in SIGBUS. Test flow: create child process, map and write to memory, mark memory with MADV_HWPOISON, access memory, if SIGBUS is delivered to child the test passes else it fails If the underlying page type of the memory we have mapped does not support poisoning then the test will fail. We try to map and write to the memory in such a way that by the time madvise is called the virtual memory address points to a supported page. However there may be some rare circumstances where the test produces the wrong result because we have somehow obtained an unsupported page. In such cases ma...

Important APIs/types/functions: mmap, madvise, fork, waitpid, memset, tst_test, tst_res, SAFE_MMAP, SAFE_FORK, SAFE_WAITPID, tst_strstatus; local functions detected: run_child, run; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: run_child, run.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise08.c

Purpose: Check that memory marked with MADV_DONTDUMP is not included in a core dump and check that the same memory then marked with MADV_DODUMP is included in a core dump. In order to reliably find the core dump this test temporarily changes the system wide core_pattern setting. Meaning all core dumps will be sent to the test's temporary dir until the setting is restored during cleanup. Test flow: map memory, write generated character sequence to memory, start child process, mark memory with MADV_DONTDUMP in child, abort child, scan child's core dump for character sequence, if the sequence is not found it is a pass otherwise a fail,

Important APIs/types/functions: read, open, close, mmap, munmap, madvise, setrlimit, fork, waitpid, tst_test, SAFE_SETRLIMIT, tst_brk, SAFE_FILE_SCANF, SAFE_GETCWD, tst_res, SAFE_FILE_PRINTF, SAFE_MMAP, SAFE_MUNMAP, SAFE_CLOSE, SAFE_ACCESS, SAFE_OPEN, SAFE_READ, SAFE_FORK, SAFE_WAITPID, tst_path_val, TST_SR_TCONF; local functions detected: setup, cleanup, find_sequence, run_child, run; key constants/macros: CORE_FILTER, YCOUNT, FMEMSIZE, CORENAME_MAX_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, find_sequence, run_child, run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; process resource limits adjusted during setup; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Write a generated character sequence to the mapped memory, which we later look for in the core dump.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise09.c

Purpose: Check that memory marked with MADV_FREE is freed on memory pressure. o Fork a child and move it into a memory cgroup o Allocate pages and fill them with a pattern o Madvise pages with MADV_FREE o Check that madvised pages were not freed immediately o Write to some of the madvised pages again, these must not be freed o Set memory limits - memory.max = 8MB - memory.swap.max = 16MB The reason for doubling the memory.max is to have safe margin for forking the memory hungy child etc. And the reason to setting memory.swap.max to twice of that is to give the system chance to try to free some memory before cgroup OOM kicks in and kills the memory...

Important APIs/types/functions: mmap, munmap, madvise, fork, wait, tst_test, SAFE_FILE_LINES_SCANF, tst_res, SAFE_CG_PRINTF, tst_cg, SAFE_MMAP, tst_brk, SAFE_FORK, SAFE_WAIT, SAFE_MUNMAP, tst_strstatus, SAFE_CG_HAS, TST_MB; local functions detected: memory_pressure_child, count_freed, check_page_baaa, check_page, child, run, setup; key constants/macros: PAGES, TOUCHED_PAGE1, TOUCHED_PAGE2, MEM_LIMIT, SWAP_LIMIT

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: memory_pressure_child, count_freed, check_page_baaa, check_page, child, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state; memory cgroup limits and counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag; configured cgroup memory controller. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: If swap accounting is disabled exit after process swapped out 100MB Only show memory map if there are issues or for debugging
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise10.c

Purpose: test cases for madvise(2) system call, advise value as "MADV_WIPEONFORK". DESCRIPTION Present the child process with zero-filled memory in this range after a fork(2). The MADV_WIPEONFORK operation can be applied only to private anonymous pages. Within the child created by fork(2), the MADV_WIPEONFORK setting remains in place on the specified map_address range. The MADV_KEEPONFORK operation undo the effect of MADV_WIPEONFORK. Test-Case 1 : madvise with "MADV_WIPEONFORK" flow : Map memory area as private anonymous page. Mark memory area as wipe-on-fork. On fork, child process memory should be zeroed. Test-Case 2 : madvise with "MADV_WIPEONFO...

Important APIs/types/functions: mmap, munmap, madvise, fork, memcpy, tst_test, tst_safe_macros, tst_res, TST_RET, TST_ERR, SAFE_MMAP, SAFE_FORK, tst_reap_children, SAFE_MUNMAP; local functions detected: cmp_area, set_advice, test_madvise, setup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: cmp_area, set_advice, test_madvise, setup.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise11.c

Purpose: Stress a possible race condition between memory pages allocation and soft-offline of unrelated pages as explained in the commit from v4.18: d4ae9916ea29 (mm: soft-offline: close the race against page allocation) Control that soft-offlined pages get correctly replaced: with the same content and without SIGBUS generation when accessed.

Important APIs/types/functions: write, read, open, close, mmap, munmap, madvise, tst_test, tst_safe_pthread, tst_safe_stdio, tst_res, SAFE_MMAP, SAFE_MUNMAP, tst_remaining_runtime, TST_CHECKPOINT_WAIT, SAFE_PTHREAD_CREATE, TST_CHECKPOINT_WAKE2, SAFE_PTHREAD_JOIN, SAFE_OPEN, SAFE_CLOSE, SAFE_FOPEN, SAFE_FCLOSE, SAFE_WRITE, tst_check_builtin_driver, SAFE_CMD, tst_brk, TST_RET, TST_ERR; local functions detected: my_yield, sigbus_handler, verif_unmap, allocate_offline, stress_alloc_offl, parse_kmsg_soft_offlined_pfn, populate_from_klog, find_in_file, unpoison_this_pfn, open_unpoison_pfn, unpoison_pfn, write_beginning_tag_to_kmsg, setup, cleanup; key constants/macros: NUM_LOOPS, NUM_PAGES, NUM_PAGES_OFFSET, HW_MODULE, OFFLINE_PATTERN, OFFLINE_PATTERN_LEN

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: my_yield, sigbus_handler, verif_unmap, allocate_offline, stress_alloc_offl, parse_kmsg_soft_offlined_pfn, populate_from_klog, find_in_file, unpoison_this_pfn, open_unpoison_pfn, unpoison_pfn, write_beginning_tag_to_kmsg.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Needed module to online back memory pages a SIGBUS received is a confirmation of test failure
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise12.c

Purpose: Verify that MADV_GUARD_INSTALL is causing SIGSEGV when someone is accessing memory advised with it. This is a test for feature implemented in 662df3e5c376 ("mm: madvise: implement lightweight guard page mechanism") [Algorithm] - allocate a certain amount of memory - advise memory with MADV_GUARD_INSTALL - access to memory from within a child and verify it gets killed by SIGSEGV - release memory with MADV_GUARD_REMOVE - verify that memory has not been modified before child got killed - modify memory within a new child - verify that memory is accessable and child was not killed by SIGSEGV

Important APIs/types/functions: mmap, munmap, madvise, fork, waitpid, memset, tst_test, TST_KB, TST_EXP_PASS, SAFE_FORK, tst_res, SAFE_WAITPID, tst_strstatus, SAFE_MMAP, SAFE_MUNMAP; local functions detected: run, setup, cleanup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases; process/thread timing is part of the signal and can make failures noisy.

Test signals: TST_EXP_PASS success assertions; explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/Makefile

Purpose: Build recipe for the LTP `mallinfo` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo01.c

Purpose: Basic mallinfo() test. Refer to glibc test mallinfo2 test https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/tst-mallinfo2.c

Important APIs/types/functions: mallinfo, tst_safe_macros, SAFE_MALLOC, tst_res, tst_test, TST_TEST_TCONF; local functions detected: cleanup, test_mallinfo, setup; key constants/macros: M_NUM

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, test_mallinfo, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo02.c

Purpose: Basic mallinfo() test for malloc() using sbrk or mmap. It size > MMAP_THRESHOLD, it will use mmap. Otherwise, use sbrk.

Important APIs/types/functions: mallinfo, mallopt, tst_safe_macros, SAFE_MALLOC, tst_res, tst_test, TST_TEST_TCONF; local functions detected: test_mallinfo, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test_mallinfo, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo_common.h

Purpose: Shared header/support code for the `mallinfo` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: tst_test, tst_res; local functions detected: print_mallinfo, print_mallinfo2; key constants/macros: MALLINFO_COMMON_H, P, P2

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: print_mallinfo, print_mallinfo2.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/Makefile

Purpose: Build recipe for the LTP `mallinfo2` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., CFLAGS += -I$(abs_srcdir)/../mallinfo.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/mallinfo2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/mallinfo2_01.c

Purpose: Basic mallinfo2() test. Test hblkhd member of struct mallinfo2 whether overflow when setting 2G size. Deprecated mallinfo() overflow in this case, that was the point for creating mallinfo2().

Important APIs/types/functions: mallinfo, mallinfo2, tst_safe_macros, tst_brk, tst_res, tst_test, TST_TEST_TCONF; local functions detected: test_mallinfo2; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: test_mallinfo2.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/mallinfo2_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/Makefile

Purpose: Build recipe for the LTP `mallopt` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/mallopt01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/mallopt01.c

Purpose: Basic mallinfo() and mallopt() testing.

Important APIs/types/functions: mallinfo, mallopt, tst_safe_macros, SAFE_MALLOC, tst_res, tst_test, TST_TEST_TCONF; local functions detected: test_mallopt; key constants/macros: MAX_FAST_SIZE

Control flow: test_all runs one whole-file scenario. Local helper functions: test_mallopt.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mallopt/mallopt01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/Makefile

Purpose: Build recipe for the LTP `mbind` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., CPPFLAGS		+= -I$(abs_srcdir)/../utils/, LDLIBS  += $(NUMA_LIBS).

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind.h

Purpose: Shared header/support code for the `mbind` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: MBIND_H__

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: preprocessor definitions and declarations only.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind01.c

Purpose: use invalid nodemask (64 MiB after heap)

Important APIs/types/functions: mmap, mbind, tst_test, tst_res, tst_brk, tst_kvercmp, SAFE_MMAP, TST_RET, tst_res_hexd, TST_ERR, tst_strerrno, TST_TEST_TCONF; local functions detected: check_policy_pref_or_local, test_default, test_none, test_invalid_nodemask, setup, setup_node, do_test; key constants/macros: MEM_LENGTH, UNKNOWN_POLICY, POLICY_DESC, POLICY_DESC_TEXT

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_policy_pref_or_local, test_default, test_none, test_invalid_nodemask, setup, setup_node, do_test.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Check policy of the allocated memory
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind02.c

Purpose: We are testing mbind() EIO error. We first fault a allocated page, then attempt to mbind it to a different node. This is a regression test for: a7f40cfe3b7a mm: mempolicy: make mbind() return -EIO when MPOL_MF_STRICT is specified

Important APIs/types/functions: mbind, tst_test, TST_NUMA_MEM, tst_brk, tst_res, TST_RET, TST_ERR, tst_tag, TST_TEST_TCONF; local functions detected: setup, cleanup, verify_policy, verify_mbind; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: setup, cleanup, verify_policy, verify_mbind.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind03.c

Purpose: We are testing mbind() MPOL_MF_MOVE and MPOL_MF_MOVE_ALL. If one of these flags is passed along with the policy kernel attempts to move already faulted pages to match the requested policy.

Important APIs/types/functions: mbind, tst_test, TST_NUMA_MEM, tst_brk, tst_res, TST_RET, TST_TEST_TCONF; local functions detected: setup, cleanup, verify_policy, verify_mbind; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, verify_policy, verify_mbind.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind04.c

Purpose: We are testing mbind() with MPOL_BIND, MPOL_PREFERRED and MPOL_INTERLEAVE For each node with memory we set its bit in nodemask with set_mempolicy() and verify that memory has been faulted accordingly.

Important APIs/types/functions: mbind, fork, tst_test, TST_NUMA_MEM, tst_brk, TST_RET, tst_res, SAFE_FORK, tst_reap_children, TST_TEST_TCONF; local functions detected: setup, cleanup, verify_policy, verify_mbind; key constants/macros: PAGES_ALLOCATED

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, verify_policy, verify_mbind.

State and persistence behavior: child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/Makefile

Purpose: Build recipe for the LTP `membarrier` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/membarrier01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/membarrier01.c

Purpose: Basic tests for membarrier(2) syscall. Tests below are responsible for testing the membarrier(2) interface only, without checking if the barrier was successful or not. Check test_case structure for each test description.

Important APIs/types/functions: fork, waitpid, membarrier, tst_test, tst_res, tst_syscall, tst_brk, TST_RET, TST_ERR, SAFE_FORK, SAFE_WAITPID, tst_kvercmp; local functions detected: sys_membarrier, verify_membarrier, wrap_verify_membarrier, setup; key constants/macros: passed_ok, passed_unexpec, failed_ok, failed_ok_unsupported, failed_not_ok, failed_unexpec, skipped, skipped_fail

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: sys_membarrier, verify_membarrier, wrap_verify_membarrier, setup.

State and persistence behavior: child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; membarrier syscall command support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: membarrier cmd needs register cmd flags for given membarrier cmd
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/membarrier01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/Makefile

Purpose: Build recipe for the LTP `memcmp` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/memcmp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/memcmp01.c

Purpose: The testcase for buffer comparison by check boundary conditions.

Important APIs/types/functions: memcmp, tst_test, tst_res; local functions detected: fill, setup, verify_memcmp, run_test; key constants/macros: BSIZE, LEN

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: fill, setup, verify_memcmp, run_test.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcmp/memcmp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/Makefile

Purpose: Build recipe for the LTP `memcpy` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/memcpy01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/memcpy01.c

Purpose: The testcase for buffer copy by check boundary conditions.

Important APIs/types/functions: memcpy, tst_test, tst_res; local functions detected: clearit, fill, checkit, setup, verify_memcpy, run_test; key constants/macros: BSIZE, LEN

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: clearit, fill, checkit, setup, verify_memcpy, run_test.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/memcpy01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/Makefile

Purpose: Build recipe for the LTP `memfd_create` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., FILTER_OUT_MAKE_TARGETS         := memfd_create_common.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create01.c

Purpose: Test based on :kselftest:`memfd/memfd_test.c`.

Important APIs/types/functions: open, close, mmap, munmap, memfd_create, tst_test, SAFE_DUP, SAFE_CLOSE, SAFE_MMAP, SAFE_MUNMAP, tst_res, tst_brk; local functions detected: test_basic, test_no_sealing_without_flag, test_seal_write, test_seal_shrink, test_seal_grow, test_seal_resize, test_share_dup, test_share_mmap, test_share_open, verify_memfd_create, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: test_basic, test_no_sealing_without_flag, test_seal_write, test_seal_shrink, test_seal_grow, test_seal_resize, test_share_dup, test_share_mmap, test_share_open, verify_memfd_create, setup.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Do few basic sealing tests to see whether setting/retrieving seals works. add more seals and seal against sealing
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create02.c

Purpose: Test based on :kselftest:`memfd/memfd_test.c`.

Important APIs/types/functions: close, memfd_create, memset, tst_test, tst_res, TST_ERR, tst_brk, TST_RET, SAFE_CLOSE; local functions detected: setup, verify_memfd_create_errno; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, verify_memfd_create_errno.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Test memfd_create() syscall Verify syscall-argument validation, including name checks, flag validation and more.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create03.c

Purpose: Test: Validating memfd_create() with MFD_HUGETLB flag. Test case 1: --WRITE CALL IN HUGEPAGES TEST-- Huge pages are write protected. Any writes to the file should return EINVAL error. Test case 2: --PAGE SIZE OF CREATED FILE TEST-- Default huge page sized pages are created with MFD_HUGETLB flag. Any attempt to unmap memory-mapped huge pages with an unmapping length less than huge page size should return EINVAL error. Test case 3: --HUGEPAGE ALLOCATION LIMIT TEST-- Number of huge pages currently available to use should be atmost total number of allowed huge pages. Memory-mapping more than allowed huge pages should return ENOMEM error.

Important APIs/types/functions: write, close, mmap, munmap, memfd_create, memset, tst_test, SAFE_MMAP, tst_res, SAFE_READ_MEMINFO, SAFE_MUNMAP, tst_brk, SAFE_CLOSE, TST_NEEDS; local functions detected: test_write_protect, test_def_pagesize, test_max_hugepages, memfd_huge_controller; key constants/macros: No prominent local constants beyond included headers.

Control flow: test iterates over the testcase table. Local helper functions: test_write_protect, test_def_pagesize, test_max_hugepages, memfd_huge_controller.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create04.c

Purpose: Validating memfd_create() with MFD_HUGETLB and MFD_HUGE_x flags. Attempt to create files in the hugetlbfs filesystem using different huge page sizes. [Algorithm] memfd_create() should return non-negative value (fd) if the system supports that particular huge page size. On success, fd is returned. On failure, -1 is returned with ENODEV error.

Important APIs/types/functions: close, memfd_create, tst_test, tst_res, tst_brk, SAFE_CLOSE; local functions detected: check_hugepage_support, memfd_huge_x_controller, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_hugepage_support, memfd_huge_x_controller, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.c

Purpose: verify PROT_READ *is* allowed

Important APIs/types/functions: write, read, open, close, mmap, munmap, memfd_create, ftruncate, fallocate, fcntl, mprotect, fstat, pwrite, TST_NO_DEFAULT_MAIN, tst_test, tst_brk_, tst_res_, TST_RET, TST_ERR, SAFE_CLOSE, SAFE_FCNTL; local functions detected: check_fallocate, check_fallocate_fail, check_ftruncate, check_ftruncate_fail, get_mfd_all_available_flags, mfd_flags_available, check_mfd_new, check_mfd_fail_new, check_mmap_fail, check_munmap, check_mfd_has_seals, check_mprotect, check_mfd_fail_add_seals, check_mfd_size, check_mfd_open, check_mfd_fail_open; key constants/macros: TST_NO_DEFAULT_MAIN

Control flow: Control is centered on local helpers check_fallocate, check_fallocate_fail, check_ftruncate, check_ftruncate_fail, get_mfd_all_available_flags, mfd_flags_available, check_mfd_new, check_mfd_fail_new, check_mmap_fail, check_munmap, check_mfd_has_seals, check_mprotect and the surrounding LTP harness.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: verify MAP_PRIVATE is *always* allowed (even writable) verify write() succeeds
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.h

Purpose: change macros accordingly if any flags need to be added in the future

Important APIs/types/functions: fcntl, SAFE_FCNTL, tst_res; local functions detected: none; key constants/macros: MEMFD_TEST_COMMON, FLAGS_ALL_ARRAY_INITIALIZER, FLAGS_ALL_MASK, MFD_DEF_SIZE, GET_MFD_ALL_AVAILABLE_FLAGS, MFD_FLAGS_AVAILABLE, CHECK_MFD_NEW, CHECK_MFD_FAIL_NEW, CHECK_MMAP, CHECK_MMAP_FAIL, CHECK_MUNMAP, CHECK_MFD_HAS_SEALS, CHECK_MFD_ADD_SEALS, CHECK_MFD_FAIL_ADD_SEALS, CHECK_MFD_SIZE, CHECK_MFD_OPEN, CHECK_MFD_FAIL_OPEN, CHECK_MFD_READABLE...

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: preprocessor definitions and declarations only.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memset/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memset/Makefile

Purpose: Build recipe for the LTP `memset` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memset/memset01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/memset/memset01.c

Purpose: The testcase for test setting of buffer by check boundary conditions.

Important APIs/types/functions: memset, tst_test, tst_res; local functions detected: fill, checkit, setup, verify_memset; key constants/macros: BSIZE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: fill, checkit, setup, verify_memset.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/memset/memset01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/Makefile

Purpose: Build recipe for the LTP `migrate_pages` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., MAKE_TARGETS		:= $(patsubst $(abs_srcdir)/%.c,%,$(sort $(wildcard $(abs_srcdir)/*[0-9].c))), CPPFLAGS		+= -I$(abs_srcdir)/../utils/.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages01.c

Purpose: errno tests for migrate_pages() syscall

Important APIs/types/functions: mmap, munmap, migrate_pages, fork, waitpid, setuid, memcpy, memset, TST_TOTAL, tst_resm, tst_syscall, tst_get_unused_pid, tst_brkm, SAFE_MUNMAP, SAFE_MALLOC, SAFE_SETUID, SAFE_WAITPID, tst_parse_opts, tst_count, tst_exit, tst_require_root; local functions detected: test_sane_nodes, test_invalid_pid, test_invalid_masksize, test_invalid_mem, test_invalid_nodes, test_invalid_perm, main, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: test_sane_nodes, test_invalid_pid, test_invalid_masksize, test_invalid_mem, test_invalid_nodes, test_invalid_perm, main, setup, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions; process/thread timing is part of the signal and can make failures noisy.

Test signals: TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: get first node which is not in nodes
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages02.c

Purpose: use migrate_pages() and check that address is on correct node 1. process A can migrate its non-shared mem with CAP_SYS_NICE 2. process A can migrate its non-shared mem without CAP_SYS_NICE 3. process A can migrate shared mem only with CAP_SYS_NICE 4. process A can migrate non-shared mem in process B with same effective uid 5. process A can migrate non-shared mem in process B with CAP_SYS_NICE

Important APIs/types/functions: mmap, munmap, migrate_pages, fork, waitpid, seteuid, setuid, memset, tst_test, tst_res, SAFE_MALLOC, tst_syscall, TST_RET, SAFE_MMAP, SAFE_MUNMAP, SAFE_FORK, SAFE_SETEUID, SAFE_WAITPID, SAFE_SETUID, tst_brk, TST_CHECKPOINT_WAKE, TST_CHECKPOINT_WAIT, tst_path_val, TST_SR_SKIP_MISSING, TST_SR_TCONF_RO, TST_TEST_TCONF; local functions detected: print_mem_stats, migrate_to_node, addr_on_node, check_addr_on_node, test_migrate_current_process, test_migrate_other_process, run, setup; key constants/macros: NODE_MIN_FREEMEM

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: print_mem_stats, migrate_to_node, addr_on_node, check_addr_on_node, test_migrate_current_process, test_migrate_other_process, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: This is an estimated minimum of free mem required to migrate this process to another node as migrate_pages will fail if there is not enough free space on node. While running this test on x86_64 it used ~2048 pages (total VM, not just RSS). Considering ia64 as architecture with largest (non-huge) page size (16k), this limit is set to 2048*16k == 32M. parent can migrate its non-shared memory
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages03.c

Purpose: Description: This is a regression test for ksm page migration which is miscalculated. The kernel bug has been fixed by: commit 4b0ece6fa0167b22c004ff69e137dc94ee2e469e Author: Naoya Horiguchi <n-horiguchi@ah.jp.nec.com> Date: Fri Mar 31 15:11:44 2017 -0700 mm: migrate: fix remove_migration_pte() for ksm pages

Important APIs/types/functions: mmap, munmap, madvise, mbind, migrate_pages, seteuid, memset, tst_test, tst_brk, SAFE_GETPWNAM, SAFE_MALLOC, SAFE_MMAP, SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_MUNMAP, SAFE_SETEUID, tst_syscall, tst_res, tst_remaining_runtime, tst_tag, TST_TEST_TCONF; local functions detected: setup, cleanup, migrate_test; key constants/macros: N_PAGES, N_LOOPS, TEST_NODES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: setup, cleanup, migrate_test.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.c

Purpose: LTP testcase for `migrate_pages` behavior in `migrate_pages_common.c`. The file uses table-driven or harness-driven checks around the relevant syscall/library API.

Important APIs/types/functions: tst_resm; local functions detected: set_bit, check_ret, check_errno; key constants/macros: No prominent local constants beyond included headers.

Control flow: Control is centered on local helpers set_bit, check_ret, check_errno and the surrounding LTP harness.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.h

Purpose: Shared header/support code for the `migrate_pages` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: MIGRATE_PAGES_COMMON_H

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: preprocessor definitions and declarations only.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/Makefile

Purpose: Build recipe for the LTP `mincore` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore01.c

Purpose: test1: Invoke mincore() when the start address is not multiple of page size. EINVAL test2: Invoke mincore() when the vector points to an invalid address. EFAULT test3: Invoke mincore() when the starting address + length contained unmapped memory. ENOMEM test4: Invoke mincore() when length is greater than (TASK_SIZE - addr). ENOMEM In Linux 2.6.11 and earlier, the error EINVAL was returned for this condition.

Important APIs/types/functions: write, open, close, mmap, munmap, mincore, setrlimit, getrlimit, memset, TST_TOTAL, tst_parse_opts, tst_count, tst_exit, SAFE_MMAP, SAFE_MUNMAP, tst_brkm, SAFE_GETRLIMIT, tst_sig, tst_tmpdir, SAFE_MALLOC, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, tst_resm, tst_rmdir; local functions detected: main, setup1, setup2, setup3, setup4, setup, mincore_verify, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: main, setup1, setup2, setup3, setup4, setup, mincore_verify, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; process resource limits adjusted during setup. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: set stack limit so that the unmaped pointer is invalid for architectures like s390 global_pointer will point to a mmapped area of global_len bytes
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore02.c

Purpose: This test case provides a functional validation for mincore system call. We mmap a file of known size (multiple of page size) and lock it in memory. Then we obtain page location information via mincore and compare the result with the expected value.

Important APIs/types/functions: write, open, close, mmap, munmap, mlock, munlock, mincore, memset, tst_test, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_CLOSE, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_MMAP, SAFE_MLOCK, TST_EXP_PASS, TST_EXP_EQ_SZ; local functions detected: cleanup, setup, check_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, check_mincore.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore03.c

Purpose: mincore03 Testcase 1: Test shows that pages mapped as anonymous and not faulted, are reported as not resident in memory by mincore(). Testcase 2: Test shows that pages mapped as anonymous and faulted, are reported as resident in memory by mincore().

Important APIs/types/functions: mmap, munmap, mlock, munlock, mincore, tst_test, SAFE_MUNMAP, SAFE_MMAP, SAFE_MLOCK, tst_brk, tst_res, SAFE_MUNLOCK; local functions detected: cleanup, setup, test_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, test_mincore.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore04.c

Purpose: mincore04 Test shows that pages mapped in one process(parent) and faulted in another(child) results in mincore(in parent) reporting that all mapped pages are resident.

Important APIs/types/functions: open, close, mmap, munmap, mlock, munlock, mincore, ftruncate, fork, fsync, tst_test, SAFE_CLOSE, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_OPEN, SAFE_FTRUNCATE, SAFE_FSYNC, tst_brk, SAFE_MLOCK, TST_CHECKPOINT_WAKE, TST_CHECKPOINT_WAIT, SAFE_MMAP, SAFE_FORK, tst_reap_children, tst_res; local functions detected: cleanup, setup, lock_file, count_pages_in_cache, test_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, lock_file, count_pages_in_cache, test_mincore.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: File pages from file creation are cleared from cache.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/Makefile

Purpose: Build recipe for the LTP `mkdir` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../.., mkdir09: CFLAGS += -pthread.

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: process/thread timing is part of the signal and can make failures noisy; build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir02.c

Purpose: Verify that new directory created by mkdir(2) inherites the group ID from the parent directory and S_ISGID bit, if the S_ISGID bit is set in the parent directory.

Important APIs/types/functions: mkdir, stat, tst_test, tst_uid, SAFE_MKDIR, SAFE_STAT, tst_res, SAFE_RMDIR, SAFE_GETPWNAM, tst_get_free_gid, SAFE_CHMOD, SAFE_CHOWN, SAFE_SETREGID, SAFE_SETREUID; local functions detected: verify_mkdir, setup; key constants/macros: TESTDIR1, TESTDIR2

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir03.c

Purpose: Check mkdir() with various error conditions that should produce EFAULT, ENAMETOOLONG, EEXIST, ENOENT, ENOTDIR, ELOOP and EROFS. Testing on various types of files (symlinks, directories, pipes, devices, etc).

Important APIs/types/functions: mkdir, symlink, tst_test, TST_EEXIST, tst_eexist, TST_PIPE, tst_pipe, TST_FOLDER, tst_folder, TST_SYMLINK, tst_symlink, TST_NULLDEV, TST_ENOENT, tst_enoent, TST_ENOTDIR_FILE, tst_enotdir, TST_ENOTDIR_DIR, TST_EROFS, tst_erofs, TST_RET, tst_res, TST_ERR, SAFE_SYMLINK, tst_tmpdir_path, SAFE_MKFIFO, SAFE_MKDIR, SAFE_TOUCH, tst_get_bad_addr; local functions detected: verify_mkdir, setup; key constants/macros: TST_EEXIST, TST_PIPE, TST_FOLDER, TST_SYMLINK, TST_NULLDEV, TST_ENOENT, TST_ENOTDIR_FILE, TST_ENOTDIR_DIR, MODE, MNT_POINT, DIR_MODE, TST_EROFS

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir04.c

Purpose: Verify that user cannot create a directory inside directory owned by another user with restrictive permissions and that the errno is set to EACCESS.

Important APIs/types/functions: mkdir, tst_test, tst_uid, tst_res, tst_get_uids, SAFE_MKDIR, SAFE_CHOWN, SAFE_SETREUID; local functions detected: verify_mkdir, setup; key constants/macros: TESTDIR, TESTSUBDIR

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir05.c

Purpose: DESCRIPTION This test will verify the mkdir(2) creates a new directory successfully and it is owned by the effective UID and GID of the process.

Important APIs/types/functions: mkdir, stat, setuid, tst_test, TST_RET, tst_res, SAFE_STAT, SAFE_RMDIR, SAFE_GETPWNAM, SAFE_SETUID; local functions detected: verify_mkdir, setup; key constants/macros: PERMS, TESTDIR

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir09.c

Purpose: Create multiple processes which create subdirectories in the same directory multiple times within test time.

Important APIs/types/functions: mkdir, tst_test, tst_safe_pthread, TST_EXP_FAIL_SILENT, TST_PASS, tst_res, TST_EXP_PASS_SILENT, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN, SAFE_MKDIR; local functions detected: test1, test2, test3, verify_mkdir, setup; key constants/macros: MNTPOINT, MODE_RWX, DIR_NAME, DIR_NAME_GROUP, NCHILD

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test1, test2, test3, verify_mkdir, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases; process/thread timing is part of the signal and can make failures noisy.

Test signals: TST_EXP_PASS success assertions; TST_EXP_FAIL errno assertions; explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Routine which attempts to create directories in the test directory that already exist. Child routine which attempts to remove directories from the test directory which do not exist.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/Makefile

Purpose: Build recipe for the LTP `mkdirat` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat01.c

Purpose: DESCRIPTION This test case will verify basic function of mkdirat added by kernel 2.6.16 or up.

Important APIs/types/functions: open, close, mkdir, mkdirat, TST_TOTAL, tst_resm, tst_get_tmpdir, SAFE_MKDIR, SAFE_OPEN, SAFE_CLOSE, tst_parse_opts, tst_count, tst_exit, tst_tmpdir, tst_rmdir; local functions detected: verify_mkdirat, setup_iteration, cleanup_iteration, main, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: verify_mkdirat, setup_iteration, cleanup_iteration, main, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Initialize test dir and file names
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat02.c

Purpose: DESCRIPTION check mkdirat() with various error conditions that should produce ELOOP and EROFS.

Important APIs/types/functions: open, mkdir, mkdirat, symlink, tst_test, SAFE_OPEN, SAFE_MKDIR, SAFE_SYMLINK, TST_RET, tst_res, TST_ERR, tst_strerrno; local functions detected: setup, mkdirat_verify; key constants/macros: MNT_POINT, TEST_DIR, DIR_MODE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, mkdirat_verify.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: NOTE: the ELOOP test is written based on that the consecutive symlinks limits in kernel is hardwired to 40.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/Makefile

Purpose: Build recipe for the LTP `mknod` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod01.c

Purpose: Verify that mknod(2) successfully creates a filesystem node with various modes.

Important APIs/types/functions: mknod, unlink, tst_test, TST_EXP_PASS, SAFE_UNLINK; local functions detected: run; key constants/macros: PATH

Control flow: test iterates over the testcase table. Local helper functions: run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod02.c

Purpose: Verify that if mknod(2) creates a filesystem node in a directory which does not have the set-group-ID bit set, new node will not inherit the group ownership from its parent directory and its group ID will be the effective group ID of the process.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_test, SAFE_GETPWNAM, SAFE_MKDIR, SAFE_CHOWN, TST_EXP_PASS, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK; local functions detected: setup, run; key constants/macros: MODE_DIR, MODE1, MODE_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: setup, run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_PASS success assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod03.c

Purpose: Verify that mknod(2) succeeds when used to create a filesystem node with set-group-ID bit set on a directory with set-group-ID bit set. The node created should have set-group-ID bit set and its gid should be equal to the "nobody" gid.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_uid, tst_test, SAFE_MKNOD, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK, SAFE_GETPWNAM, tst_get_free_gid, SAFE_MKDIR, SAFE_CHOWN, SAFE_CHMOD, SAFE_SETGID, SAFE_SETREUID; local functions detected: run, setup; key constants/macros: MODE_RWX, MODE_FIFO_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod04.c

Purpose: Verify that mknod(2) succeeds when used to create a filesystem node on a directory with set-group-ID bit set. The node created should not have set-group-ID bit set and its gid should be equal to the effective gid of the process.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_uid, tst_test, SAFE_MKNOD, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK, SAFE_GETPWNAM, tst_get_free_gid, SAFE_MKDIR, SAFE_CHOWN, SAFE_CHMOD, SAFE_SETGID, SAFE_SETREUID; local functions detected: run, setup; key constants/macros: MODE_RWX, MODE_FIFO, MODE_FIFO_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod05.c

Purpose: Verify that mknod(2) succeeds when used to create a filesystem node with set-group-ID bit set on a directory with set-group-ID bit set. The node created should have set-group-ID bit set and its gid should be equal to that of its parent directory.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_uid, tst_test, SAFE_MKNOD, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK, SAFE_GETPWNAM, tst_get_free_gid, SAFE_MKDIR, SAFE_CHOWN, SAFE_CHMOD; local functions detected: run, setup; key constants/macros: MODE_RWX, MODE_FIFO_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod06.c

Purpose: Verify that mknod(2) fails with the correct error codes: - ENAMETOOLONG if the pathname component was too long. - EEXIST if specified path already exists. - EFAULT if pathname points outside user's accessible address space. - ENOENT if the directory component in pathname does not exist. - ENOENT if the pathname is empty. - ENOTDIR if the directory component in pathname is not a directory.

Important APIs/types/functions: mknod, tst_test, TST_EXP_FAIL, SAFE_MKNOD, tst_buffers; local functions detected: run, setup; key constants/macros: MODE_FIFO_RWX

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod07.c

Purpose: Verify that mknod(2) fails with the correct error codes: - EACCES if parent directory does not allow write permission to the process. - EPERM if the process id of the caller is not super-user. - EROFS if pathname refers to a file on a read-only file system. - ELOOP if too many symbolic links were encountered in resolving pathname.

Important APIs/types/functions: mknod, mkdir, symlink, seteuid, tst_test, TST_EXP_FAIL, SAFE_GETPWNAM, SAFE_SETEUID, SAFE_MKDIR, SAFE_SYMLINK, tst_buffers; local functions detected: run, setup; key constants/macros: TEMP_MNT, TEMP_DIR, TEMP_DIR_MODE, ELOOP_DIR, ELOOP_FILE, ELOOP_DIR_MODE, ELOOP_MAX, FIFO_MODE, SOCKET_MODE, CHR_MODE, BLK_MODE, TEST_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases; requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: The kernel limits symlink resolution hop amount to 40, create a pathname with more than that
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod08.c

Purpose: Verify that mknod(2) succeeds when used to create a filesystem node on a directory without set group-ID bit set. The node created should not have set group-ID bit set and its gid should be equal to that of its parent directory.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_uid, tst_test, SAFE_MKNOD, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK, SAFE_GETPWNAM, tst_get_free_gid, SAFE_MKDIR, SAFE_CHOWN, SAFE_SETGID; local functions detected: run, setup; key constants/macros: MODE_RWX, MODE_FIFO_RWX, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod09.c

Purpose: Verify that mknod() fails with -1 and sets errno to EINVAL if the mode is different than a normal file, device special file or FIFO.

Important APIs/types/functions: mknod, tst_test, TST_EXP_FAIL; local functions detected: check_mknod; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: check_mknod.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/Makefile

Purpose: Build recipe for the LTP `mknodat` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat01.c

Purpose: clean created nodes before next run

Important APIs/types/functions: open, close, mknodat, mkdir, unlink, TST_TOTAL, tst_resm, tst_parse_opts, tst_count, tst_exit, tst_sig, tst_tmpdir, tst_get_tmpdir, SAFE_MKDIR, SAFE_OPEN, SAFE_UNLINK, tst_rmdir; local functions detected: verify_mknodat, main, setup, clean, cleanup; key constants/macros: PATHNAME

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: verify_mknodat, main, setup, clean, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Initialize test dir and file names
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat02.c

Purpose: Description: Verify that, 1) mknod(2) returns -1 and sets errno to EROFS if pathname refers to a file on a read-only file system. 2) mknod(2) returns -1 and sets errno to ELOOP if Too many symbolic links were encountered in resolving pathname.

Important APIs/types/functions: open, close, mknod, mknodat, mkdir, symlink, unlinkat, mount, TST_TOTAL, tst_parse_opts, tst_count, tst_exit, tst_require_root, tst_sig, tst_tmpdir, tst_dev_fs_type, tst_acquire_device, tst_brkm, tst_mkfs, SAFE_MKDIR, SAFE_MOUNT, SAFE_OPEN, SAFE_SYMLINK, tst_resm, tst_syscall, tst_umount, tst_release_device, tst_rmdir; local functions detected: main, setup, mknodat_verify, cleanup; key constants/macros: DIR_MODE, MNT_POINT, FIFOMODE, FREGMODE, SOCKMODE, ELOPFILE

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: main, setup, mknodat_verify, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; spare block device or loop-backed LTP device. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: mount a read-only file system for EROFS test NOTE: the ELOOP test is written based on that the consecutive symlinks limits in kernel is hardwired to 40.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/Makefile

Purpose: Build recipe for the LTP `mlock` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock01.c

Purpose: Test mlock with various valid addresses and lengths.

Important APIs/types/functions: mlock, tst_test, tst_res, SAFE_MALLOC, TST_EXP_PASS; local functions detected: do_mlock, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: do_mlock, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock02.c

Purpose: Test for ENOMEM, EPERM errors. 1) mlock(2) fails with ENOMEM if some of the specified address range does not correspond to mapped pages in the address space of the process. 2) mlock(2) fails with ENOMEM if the caller had a non-zero RLIMIT_MEMLOCK soft resource limit, but tried to lock more memory than the limit permitted. This limit is not enforced if the process is privileged (CAP_IPC_LOCK). 3) mlock(2) fails with EPERM if the caller was not privileged (CAP_IPC_LOCK) and its RLIMIT_MEMLOCK soft resource limit was 0.

Important APIs/types/functions: mmap, munmap, mlock, setrlimit, getrlimit, seteuid, tst_test, SAFE_MMAP, SAFE_MUNMAP, TST_EXP_FAIL, SAFE_SETRLIMIT, SAFE_SETEUID, SAFE_GETPWNAM, SAFE_GETRLIMIT; local functions detected: test_enomem1, test_enomem2, test_eperm, run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test_enomem1, test_enomem2, test_eperm, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; process resource limits adjusted during setup; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock03.c

Purpose: This case is a regression test on old RHEL5. Stack size mapping is decreased through mlock/munlock call. See the following url: https://bugzilla.redhat.com/show_bug.cgi?id=643426 This is to test kernel if it has a problem with shortening [stack] mapping through several loops of mlock/munlock of /proc/self/maps. From: munlock 76KiB bfef2000-bff05000 rw-p 00000000 00:00 0 [stack] To: munlock 44KiB bfefa000-bff05000 rw-p 00000000 00:00 0 [stack] with more iterations - could drop to 0KiB.

Important APIs/types/functions: mlock, munlock, tst_test, tst_safe_stdio, TST_KB, SAFE_FOPEN, tst_brk, tst_res, SAFE_FCLOSE; local functions detected: verify_mlock; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: verify_mlock.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Record the initial stack size. Record the final stack size.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock04.c

Purpose: This is a reproducer copied from one of LKML patch submission https://lore.kernel.org/lkml/1296371720-4176-1-git-send-email-tm@tao.ma/ "In 5ecfda0, we do some optimization in mlock, but it causes a very basic test case(attached below) of mlock to fail. So this patch revert it with some tiny modification so that it apply successfully with the lastest 38-rc2 kernel." This bug was fixed by kernel commit fdf4c587a7 ("mlock: operate on any regions with protection != PROT_NONE") As this case does, mmaps a file with PROT_WRITE permissions but without PROT_READ, so attempt to not unnecessarity break COW during mlock ended up causing mlock to fail...

Important APIs/types/functions: open, close, mmap, munmap, mlock, munlock, ftruncate, tst_test, tst_safe_macros, SAFE_MMAP, TST_EXP_PASS, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_OPEN, SAFE_FTRUNCATE, SAFE_CLOSE, tst_tag; local functions detected: verify_mlock, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: verify_mlock, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock05.c

Purpose: Verify mlock() causes pre-faulting of PTEs and prevent memory to be swapped out. Find the new mapping in /proc/$pid/smaps and check Rss and Locked fields after mlock syscall: Rss and Locked size should be equal to the size of the memory allocation

Important APIs/types/functions: mmap, munmap, mlock, munlock, tst_test, tst_safe_stdio, SAFE_FOPEN, SAFE_FCLOSE, tst_brk, SAFE_MMAP, SAFE_MLOCK, TST_EXP_EQ_LU, SAFE_MUNLOCK, SAFE_MUNMAP; local functions detected: get_proc_smaps_info, verify_mlock; key constants/macros: MMAPLEN, LINELEN

Control flow: test_all runs one whole-file scenario. Local helper functions: get_proc_smaps_info, verify_mlock.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_* value comparisons; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/Makefile

Purpose: Build recipe for the LTP `mlock2` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock201.c

Purpose: Description: Check the basic functionality of the mlock2(2) since kernel v2.6.9: 1) When we use mlock2() without MLOCK_ONFAULT to lock memory in the specified range that is multiples of page size or not, we can show correct size of locked memory by VmLck from /proc/PID/status and lock all pages including non-present. 2) When we use mlock2() with MLOCK_ONFAULT to lock memory in the specified range that is multiples of page size or not, we can show correct size of locked memory by VmLck from /proc/PID/status and just lock present pages.

Important APIs/types/functions: mmap, munmap, munlock, mlock2, mincore, memset, tst_test, SAFE_MINCORE, SAFE_MMAP, SAFE_FILE_LINES_SCANF, tst_syscall, TST_RET, TST_ERR, tst_res, SAFE_MUNLOCK, SAFE_MUNMAP; local functions detected: check_locked_pages, verify_mlock2, setup; key constants/macros: PAGES, HPAGES

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_locked_pages, verify_mlock2, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; mlock2 syscall and MLOCK_ONFAULT support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: lock single page, expect it to be locked and present lock all pages, expect all to be locked and present
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock201.c -->
