# subset-b-009305 Research

Grouped source research for LTP syscall tests from `pwritev2` through `sched_getattr`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/Makefile` is the LTP leaf Makefile for the `pwritev2` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: pwritev2 vector-positioned write coverage, including offset handling, iovec validation, flags, bad descriptors, and pipe errors.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(abs_srcdir)/../utils/newer_64.mk`, `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `pwritev2` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev201.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev201.c` is a 120-line LTP source file in the `pwritev2` syscall test area. pwritev2 vector-positioned write coverage, including offset handling, iovec validation, flags, bad descriptors, and pipe errors. Source description: Author: Jinhui Huang <huangjh.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `pwritev2`, `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_PREAD`, `SAFE_PWRITE`, `TEST`; local functions: `verify_pwritev2`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `CHUNK`.

## Control Flow

Function-level flow is organized around `verify_pwritev2`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<string.h>`, `<sys/uio.h>`, `"tst_test.h"`, `"lapi/uio.h"`, `"tst_safe_prw.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `pwritev2() failed`; `pwritev2() wrote %li bytes, expected %zi`; `buffer wrong at %i have %c expected 'a'`; `with content 'a' expectedly `.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c` is a 118-line LTP source file in the `pwritev2` syscall test area. pwritev2 vector-positioned write coverage, including offset handling, iovec validation, flags, bad descriptors, and pipe errors. Source description: Author: Jinhui Huang <huangjh.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `pwritev2`, `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_OPEN`, `SAFE_PIPE`, `TEST`; local functions: `verify_pwritev2`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `CHUNK`.

## Control Flow

Function-level flow is organized around `verify_pwritev2`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/uio.h>`, `<unistd.h>`, `"tst_test.h"`, `"lapi/uio.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.setup`, `.cleanup`, `.test`, `.needs_tmpdir`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EOPNOTSUPP`, `EFAULT`, `EBADF`, `ESPIPE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `pwritev2() succeeded unexpectedly`; `pwritev2() failed as expected`; `pwritev2() failed unexpectedly, expected %s`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pwritev2/pwritev202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/Makefile` is the LTP leaf Makefile for the `quotactl` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `quotactl` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl01.c` is a 233-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com> Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_ACCESS`, `SAFE_CMD`, `SAFE_UNLINK`, `TEST`, `TST_EXP_PASS_SILENT`; local functions: `setup`, `cleanup`, `verify_quota`; struct/table types referenced: `struct dqblk`, `struct dqinfo`, `struct if_nextdqblk`, `struct tcase`, `struct quotactl_fmt_variant`, `struct tst_test`, `struct tst_fs`, `struct tst_cmd`; important macros/constants: `USRPATH`, `GRPPATH`, `MNTPOINT`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `verify_quota`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<string.h>`, `<unistd.h>`, `<stdio.h>`, `"tst_test.h"`, `"quotactl_fmt_var.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.dqb_bsoftlimit`, `.dqb_valid`, `.dqi_bgrace`, `.dqi_valid`, `.needs_root`, `.needs_kconfigs`, `.test`, `.tcnt`, `.mount_device`, `.filesystems`, `.type`, `.mnt_data`, `.mntpoint`, `.needs_cmds`, `.setup`, `.cleanup`, `.test_variants`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_fmt_var.h`; `/aquota.user`; `/aquota.group`; `turn on quota for user`; `QCMD(Q_QUOTAON, USRQUOTA)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.c` is a 165-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: DAN LI <li.dan@cn.fujitsu.com> Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_CLOSE`, `SAFE_OPEN`, `TST_EXP_PASS_SILENT`, `TST_TEST_TCONF`; local functions: `setup`, `cleanup`, `verify_quota`; struct/table types referenced: `struct t_case`, `struct tst_test`, `struct tst_fs`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `verify_quota`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `"quotactl02.h"`, `"quotactl_syscall_var.h"`. Designated initializer fields seen include `.needs_root`, `.needs_kconfigs`, `.test`, `.tcnt`, `.mount_device`, `.filesystems`, `.type`, `.mnt_data`, `.mntpoint`, `.setup`, `.cleanup`, `.test_variants`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly.

## Test Signals

TPASS/TST_EXP_PASS success reports; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl02.h`; `quotactl_syscall_var.h`; `turn off xfs quota and get xfs quota off status for user`; `QCMD(Q_XGETQSTAT, USRQUOTA) off`; `turn on xfs quota and get xfs quota on status for user`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h` is a 149-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `TEST`, `TST_EXP_PASS_SILENT`; local functions: `check_support_cmd`, `check_qoff`, `check_qon`, `check_qoffv`, `check_qonv`, `check_qlim`; struct/table types referenced: `struct fs_disk_quota`, `struct fs_quota_statv`, `struct fs_quota_stat`; important macros/constants: `QUOTACTL02_H`, `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `check_support_cmd`, `check_qoff`, `check_qon`, `check_qoffv`, `check_qonv`, `check_qlim`.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<unistd.h>`, `<stdio.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`, `<xfs/xqm.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.d_rtb_softlimit`, `.d_fieldmask`, `.qs_version`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `quotactl_syscall_var.h`; `do_quotactl() to %s`; `xfs quota enforcement was on unexpectedly`; `quotactl() succeeded to %s`; `xfs quota enforcement was off unexpectedly`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl02.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl03.c` is a 101-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_CLOSE`, `SAFE_OPEN`, `TEST`, `TST_TEST_TCONF`; local functions: `verify_quota`, `setup`, `cleanup`; struct/table types referenced: `struct fs_disk_quota`, `struct tst_test`, `struct tst_fs`, `struct tst_tag`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `verify_quota`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<unistd.h>`, `<stdio.h>`, `<sys/quota.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`, `<xfs/xqm.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.cleanup`, `.needs_root`, `.needs_kconfigs`, `.test_all`, `.mount_device`, `.filesystems`, `.type`, `.mnt_data`, `.mntpoint`, `.test_variants`, `.tags`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `ENOENT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_syscall_var.h`; `quotactl() found the next active ID: %u unexpectedly`; `Q_XGETNEXTQUOTA wasn't supported in quotactl()`; `quotactl() failed unexpectedly with %s expected ENOENT`; `quotactl() failed with ENOENT as expected`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl04.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl04.c` is a 172-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_CLOSE`, `SAFE_OPEN`, `TEST`, `TST_EXP_PASS_SILENT`; local functions: `setup`, `cleanup`, `verify_quota`; struct/table types referenced: `struct dqblk`, `struct dqinfo`, `struct if_nextdqblk`, `struct tcase`, `struct tst_test`, `struct tst_fs`, `struct tst_cmd`; important macros/constants: `FMTID`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `verify_quota`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<string.h>`, `<unistd.h>`, `<sys/stat.h>`, `<sys/mount.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.dqb_bsoftlimit`, `.dqb_valid`, `.dqi_bgrace`, `.dqi_valid`, `.needs_root`, `.needs_kconfigs`, `.min_kver`, `.test`, `.tcnt`, `.setup`, `.cleanup`, `.mount_device`, `.filesystems`, `.type`, `.mkfs_opts`, `.mntpoint`, `.test_variants`, `.needs_cmds`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_syscall_var.h`; `turn on quota for project`; `QCMD(Q_QUOTAON, PRJQUOTA)`; `set disk quota limit for project`; `QCMD(Q_SETQUOTA, PRJQUOTA)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl05.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl05.c` is a 129-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_CLOSE`, `SAFE_OPEN`, `TST_EXP_PASS_SILENT`, `TST_TEST_TCONF`; local functions: `setup`, `cleanup`, `verify_quota`; struct/table types referenced: `struct t_case`, `struct tst_test`, `struct tst_fs`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `verify_quota`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `"quotactl02.h"`, `"quotactl_syscall_var.h"`. Designated initializer fields seen include `.needs_root`, `.needs_kconfigs`, `.test`, `.tcnt`, `.mount_device`, `.filesystems`, `.type`, `.mnt_data`, `.mntpoint`, `.setup`, `.cleanup`, `.test_variants`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly.

## Test Signals

TPASS/TST_EXP_PASS success reports; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl02.h`; `quotactl_syscall_var.h`; `turn off xfs quota and get xfs quota off status for project`; `QCMD(Q_XGETQSTAT, PRJQUOTA) off`; `turn on xfs quota and get xfs quota on status for project`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl06.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl06.c` is a 239-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_ACCESS`, `SAFE_CMD`, `SAFE_MKDIR`, `SAFE_RMDIR`, `SAFE_UNLINK`, `TEST`, `TST_EXP_FAIL`, `TST_EXP_PASS_SILENT`; local functions: `verify_quotactl`, `setup`, `cleanup`; struct/table types referenced: `struct if_nextdqblk`, `struct dqblk`, `struct tst_cap`, `struct tcase`, `struct quotactl_fmt_variant`, `struct tst_test`, `struct tst_fs`, `struct tst_cmd`, `struct tst_tag`; important macros/constants: `OPTION_INVALID`, `USRPATH`, `MNTPOINT`, `TESTDIR1`, `TESTDIR2`.

## Control Flow

Function-level flow is organized around `verify_quotactl`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/quota.h>`, `"tst_test.h"`, `"quotactl_fmt_var.h"`, `"tst_capability.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.dqb_bsoftlimit`, `.dqb_valid`, `.action`, `.id`, `.name`, `.setup`, `.cleanup`, `.needs_kconfigs`, `.tcnt`, `.test`, `.filesystems`, `.type`, `.mnt_data`, `.mntpoint`, `.mount_device`, `.needs_cmds`, `.needs_root`, `.test_variants`, `.tags`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EACCES`, `ENOENT`, `EBUSY`, `EFAULT`, `EINVAL`, `ENOTBLK`, `ESRCH`, `ERANGE`, `EPERM`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_fmt_var.h`; `/aquota.user`; `EACCES when cmd is Q_QUOTAON and addr existed but not a regular file`; `EBUSY when cmd is Q_QUOTAON and another Q_QUOTAON had already been performed`; `ESRCH is for Q_SETQUOTA but no quota found for the user or quotas are off`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl07.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl07.c` is a 99-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `umount`, `SAFE_CLOSE`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_STATFS`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_TEST_TCONF`; local functions: `verify_quota`, `setup`, `cleanup`; struct/table types referenced: `struct statfs`, `struct tst_test`, `struct tst_fs`, `struct tst_tag`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `verify_quota`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<fcntl.h>`, `<errno.h>`, `<unistd.h>`, `<stdio.h>`, `<sys/quota.h>`, `<sys/statvfs.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`, `<xfs/xqm.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.cleanup`, `.needs_root`, `.needs_kconfigs`, `.test_all`, `.format_device`, `.filesystems`, `.mntpoint`, `.test_variants`, `.tags`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `xfs: Sanity check flags of Q_XQUOTARM call`; `quotactl_syscall_var.h`; `do_quotactl(Q_XQUOTARM,valid_type)`; `Q_XQUOTARM to free space, delta(%lu)`; `Q_XQUOTARM to free space, delta(-%lu)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl08.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl08.c` is a 227-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `SAFE_CLOSE`, `SAFE_OPEN`, `TEST`, `TST_EXP_PASS_SILENT`; local functions: `setup`, `cleanup`, `verify_quota`; struct/table types referenced: `struct dqblk`, `struct dqinfo`, `struct if_nextdqblk`, `struct tcase`, `struct tst_test`, `struct tst_fs`, `struct tst_cmd`; important macros/constants: `MNTPOINT`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `verify_quota`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<string.h>`, `<unistd.h>`, `"tst_test.h"`, `"quotactl_syscall_var.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.dqb_bsoftlimit`, `.dqb_valid`, `.dqi_bgrace`, `.dqi_valid`, `.needs_root`, `.needs_kconfigs`, `.test`, `.tcnt`, `.mntpoint`, `.filesystems`, `.type`, `.mkfs_opts`, `.mount_device`, `.setup`, `.cleanup`, `.test_variants`, `.needs_cmds`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EINVAL`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_syscall_var.h`; `turn on quota for user`; `QCMD(Q_QUOTAON, USRQUOTA)`; `set disk quota limit for user`; `QCMD(Q_SETQUOTA, USRQUOTA)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl09.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl09.c` is a 192-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `quotactl_fd`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SOCKET`, `TEST`, `TST_EXP_FAIL`, `TST_EXP_PASS_SILENT`; local functions: `verify_quotactl`, `setup`, `cleanup`; struct/table types referenced: `struct if_nextdqblk`, `struct dqblk`, `struct tst_cap`, `struct tcase`, `struct tst_test`, `struct tst_fs`, `struct tst_cmd`; important macros/constants: `OPTION_INVALID`.

## Control Flow

Function-level flow is organized around `verify_quotactl`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/quota.h>`, `<sys/socket.h>`, `"tst_test.h"`, `"tst_capability.h"`, `"quotactl_syscall_var.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.dqb_bsoftlimit`, `.dqb_valid`, `.action`, `.id`, `.name`, `.setup`, `.cleanup`, `.needs_kconfigs`, `.tcnt`, `.test`, `.filesystems`, `.type`, `.mkfs_opts`, `.mntpoint`, `.mount_device`, `.needs_root`, `.test_variants`, `.needs_cmds`.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly. Explicit errno expectations include `EFAULT`, `EINVAL`, `ENOTBLK`, `ERANGE`, `EPERM`, `ENOSYS`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `quotactl_syscall_var.h`; `ERANGE when cmd is Q_SETQUOTA, but the specified limits are out of the range`; `EINVAL when cmd is Q_QUOTAON, but the fd refers to a socket`; `current system doesn't support Q_GETNEXTQUOTA`; `do_quotactl(QCMD(Q_QUOTAON, USRQUOTA))`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_fmt_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_fmt_var.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_fmt_var.h` is a 22-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

struct/table types referenced: `struct quotactl_fmt_variant`; important macros/constants: `LTP_QUOTACTL_FMT_VAR_H`, `QUOTACTL_FMT_VARIANTS`.

## Control Flow

Control flow is minimal and handled by the LTP harness around the declared test callback.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates.

## Dependencies and Integration Points

Direct includes: `"lapi/quotactl.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly.

## Test Signals

notable reported messages include `lapi/quotactl.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_fmt_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_syscall_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_syscall_var.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_syscall_var.h` is a 32-line LTP source file in the `quotactl` syscall test area. quota-control coverage for VFS and XFS quota commands, visible and hidden quota files, quota formats, project quotas, capability failures, and quotactl_fd variants. Source description: Author: Yang Xu <xuyang2018.jy@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `quotactl`, `quotactl_fd`; local functions: `do_quotactl`, `quotactl_info`; important macros/constants: `LTP_QUOTACTL_SYSCALL_VAR_H`, `QUOTACTL_SYSCALL_VARIANTS`, `MNTPOINT`.

## Control Flow

Function-level flow is organized around `do_quotactl`, `quotactl_info`.

## State and Persistence Behavior

State is quota metadata on a mounted scratch filesystem: aquota files or hidden quota state, XFS quota flags, project/user/group ids, and device or mount-point file descriptors. The tests intentionally enable and disable quota accounting/enforcement and compare returned quota structs against expected in-memory templates.

## Dependencies and Integration Points

Direct includes: `"lapi/quotactl.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Quota tests are sensitive to kernel config, filesystem support, mkfs/mount options, root/capability state, quota format support, and command availability. Struct comparisons can fail if padding or unsupported fields are not gated correctly.

## Test Signals

notable reported messages include `lapi/quotactl.h`; `Test quotactl()`; `Test quotactl_fd()`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/quotactl/quotactl_syscall_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/read/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/Makefile` is the LTP leaf Makefile for the `read` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `read` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c` is a 45-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct tst_test`; important macros/constants: `SIZE`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `read(2) failed`; `read(2) returned %ld`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c` is a 130-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths. Source description: Ported to LTP: Wayne Boyer 04/2017 Modified by Jinhui Huang

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MEMALIGN`, `SAFE_MMAP`, `SAFE_OPEN`, `TEST`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EBADF`, `EISDIR`, `EFAULT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `O_DIRECT not supported on %s filesystem`; `O_DIRECT unaligned reads fallbacks to buffered I/O`; `read() succeeded unexpectedly`; `read() failed as expected`; `read() failed unexpectedly, `.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c` is a 54-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_MKNOD`, `SAFE_OPEN`, `SAFE_STAT`, `SAFE_UNLINK`, `TST_EXP_FAIL`; local functions: `verify_read`, `setup`, `cleanup`; struct/table types referenced: `struct stat`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<fcntl.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_tmpdir`, `.setup`, `.cleanup`, `.test_all`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EAGAIN`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `read() when nothing is written to a pipe`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/read/read04.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/read/read04.c` is a 58-line LTP source file in the `read` syscall test area. read syscall coverage for ordinary files, directories, invalid buffers, O_DIRECT, FIFOs, short/complete reads, and expected errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`; local functions: `verify_read`, `setup`; struct/table types referenced: `struct tst_test`; important macros/constants: `PALFA_LEN`.

## Control Flow

Function-level flow is organized around `verify_read`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `<sys/stat.h>`, `<stdio.h>`, `<fcntl.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_tmpdir`, `.setup`, `.test_all`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Bad read count - got %ld - expected %zu`; `read buffer not equal to write buffer`; `read() data correctly`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/read/read04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readahead/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readahead/Makefile` is the LTP leaf Makefile for the `readahead` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: readahead and POSIX_FADV_WILLNEED coverage for invalid descriptors and page-cache effectiveness on mounted filesystems and overlayfs.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `readahead` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c` is a 88-line LTP source file in the `readahead` syscall test area. readahead and POSIX_FADV_WILLNEED coverage for invalid descriptors and page-cache effectiveness on mounted filesystems and overlayfs.

## Important APIs, Types, and Functions

called APIs/macros: `readahead`, `SAFE_CLOSE`, `SAFE_PIPE`, `TST_EXP_FAIL`, `TST_EXP_FAIL_ARR`, `TST_FD_FOREACH`, `TST_TEST_TCONF`; local functions: `test_bad_fd`, `test_invalid_fd`, `test_readahead`, `setup`; struct/table types referenced: `struct tst_fd`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `test_bad_fd`, `test_invalid_fd`, `test_readahead`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is a generated test file, page-cache residency observed with mincore(), /proc/self/io byte counters, optional overlayfs mounts, and the block-device bdi read_ahead_kb sysfs knob. Persistence is limited to temporary files and restored sysfs settings.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/socket.h>`, `<sys/stat.h>`, `<sys/syscall.h>`, `<sys/types.h>`, `"config.h"`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_tmpdir`, `.setup`, `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

The performance signal depends on cache size, storage speed, overlayfs support, /proc/self/io, mincore accuracy, bdi limits, and drop-caches behavior; the test must report TCONF rather than false failures when the platform cannot expose the signal. Explicit errno expectations include `EBADF`, `EINVAL`, `ESPIPE`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `readahead() with fd = -1`; `readahead() with invalid fd`; `readahead() on %s`; `System doesn't support __NR_readahead`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c` is a 472-line LTP source file in the `readahead` syscall test area. readahead and POSIX_FADV_WILLNEED coverage for invalid descriptors and page-cache effectiveness on mounted filesystems and overlayfs.

## Important APIs, Types, and Functions

called APIs/macros: `readahead`, `posix_fadvise`, `mincore`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_FILE_LINES_SCANF`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FSYNC`, `SAFE_LSEEK`, `SAFE_LSTAT`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READLINK`, `SAFE_STRTOL`, `SAFE_UMOUNT`, `SAFE_WRITE`; local functions: `libc_readahead`, `fadvise_willneed`, `has_file`, `drop_caches`, `create_testfile`, `read_testfile`, `test_readahead`, `setup_readahead_length`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct stat`, `struct tst_test`, `struct tst_option`, `struct tst_tag`; important macros/constants: `_GNU_SOURCE`, `PROC_IO_FNAME`, `DEFAULT_FILESIZE`, `SHORT_SLEEP_US`, `MIN_RETRY_LIMIT`.

## Control Flow

Function-level flow is organized around `libc_readahead`, `fadvise_willneed`, `has_file`, `drop_caches`, `create_testfile`, `read_testfile`, `test_readahead`, `setup_readahead_length`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is a generated test file, page-cache residency observed with mincore(), /proc/self/io byte counters, optional overlayfs mounts, and the block-device bdi read_ahead_kb sysfs knob. Persistence is limited to temporary files and restored sysfs settings. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `<sys/syscall.h>`, `<sys/mman.h>`, `<sys/mount.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<errno.h>`, `<stdio.h>`, `<stdlib.h>`, `<stdint.h>`, `<unistd.h>`, `<fcntl.h>`, `"config.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_root`, `.mount_device`, `.mntpoint`, `.setup`, `.cleanup`, `.options`, `.test`, `.tcnt`, `.timeout`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

The performance signal depends on cache size, storage speed, overlayfs support, /proc/self/io, mincore accuracy, bdi limits, and drop-caches behavior; the test must report TCONF rather than false failures when the platform cannot expose the signal. Explicit errno expectations include `ENOENT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `readahead on file`; `readahead on overlayfs file`; `read_bytes: %lu`; `readahead calls made: %zu`; `offset is still at 0 as expected`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readahead/readahead02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readdir/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readdir/Makefile` is the LTP leaf Makefile for the `readdir` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: legacy readdir syscall coverage for directory enumeration and descriptor/type errors across mounted filesystems.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `readdir` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c` is a 73-line LTP source file in the `readdir` syscall test area. legacy readdir syscall coverage for directory enumeration and descriptor/type errors across mounted filesystems. Source description: Contact information: Silicon Graphics, Inc., 1600 Amphitheatre Pkwy, Mountain View, CA  94043, or: http://www.sgi.com For further information regarding this notice, see: http://oss.sgi.com/projects/GenInfo/NoticeExplan/

## Important APIs, Types, and Functions

called APIs/macros: `readdir`, `SAFE_CLOSE`, `SAFE_CLOSEDIR`, `SAFE_OPEN`, `SAFE_OPENDIR`, `SAFE_READDIR`, `SAFE_WRITE`; local functions: `setup`, `verify_readdir`; struct/table types referenced: `struct dirent`, `struct tst_test`; important macros/constants: `MNTPOINT`.

## Control Flow

Function-level flow is organized around `setup`, `verify_readdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readdirfile`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c` is a 81-line LTP source file in the `readdir` syscall test area. legacy readdir syscall coverage for directory enumeration and descriptor/type errors across mounted filesystems. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `readdir`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_RMDIR`, `TST_EXP_FAIL`; local functions: `setup`, `verify_readdir`; struct/table types referenced: `struct old_linux_dirent`, `struct tcase`, `struct tst_test`; important macros/constants: `MNTPOINT`, `TEST_DIR`, `TEST_DIR4`, `TEST_FILE`, `DIR_MODE`.

## Control Flow

Function-level flow is organized around `setup`, `verify_readdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<sys/stat.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"lapi/readdir.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.setup`, `.test`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`, `ENOTDIR`, `EBADFD`, `EFAULT`, `EBADF`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/readdir.h`; `readdir() with %s`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readdir/readdir21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlink/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlink/Makefile` is the LTP leaf Makefile for the `readlink` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: readlink coverage for symlink target reads, access through changed credentials, and pathname error handling.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `readlink` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c` is a 90-line LTP source file in the `readlink` syscall test area. readlink coverage for symlink target reads, access through changed credentials, and pathname error handling. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `readlink`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_OPEN`, `SAFE_SETUID`, `SAFE_SYMLINK`, `TEST`; local functions: `test_readlink`, `verify_readlink`, `setup`; struct/table types referenced: `struct passwd`, `struct tst_test`; important macros/constants: `TESTFILE`, `SYMFILE`.

## Control Flow

Function-level flow is organized around `test_readlink`, `verify_readlink`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<errno.h>`, `<string.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.tcnt`, `.setup`, `.forks_child`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink() on %s failed`; `readlink() returned value %ld `; `did't match, Expected %d`; `readlink() functionality on '%s' was correct`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c` is a 121-line LTP source file in the `readlink` syscall test area. readlink coverage for symlink target reads, access through changed credentials, and pathname error handling. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `readlink`, `SAFE_CHMOD`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `verify_readlink`, `setup`; struct/table types referenced: `struct tcase`, `struct passwd`, `struct tst_test`; important macros/constants: `DIR_TEMP`, `TEST_FILE1`, `SYM_FILE1`, `TEST_FILE2`, `SYM_FILE2`, `TEST_FILE3`, `SYM_FILE3`, `ELOOPFILE`, `TESTFILE`, `SYMFILE`.

## Control Flow

Function-level flow is organized around `verify_readlink`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<errno.h>`, `<string.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.setup`, `.needs_tmpdir`, `.needs_root`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EACCES`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `ELOOP`, `EFAULT`, `ELOOPFILE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink() sueeeeded unexpectedly`; `readlink() failed unexpectedly; expected: %d - %s, got`; `readlink() failed as expected`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/Makefile` is the LTP leaf Makefile for the `readlinkat` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: readlinkat coverage for dirfd-relative symlink reads and invalid path, descriptor, and buffer cases.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `readlinkat` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c` is a 98-line LTP source file in the `readlinkat` syscall test area. readlinkat coverage for dirfd-relative symlink reads and invalid path, descriptor, and buffer cases. Source description: Author: Yi Yang <yyangcdl@cn.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `readlinkat`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SYMLINK`, `TST_EXP_POSITIVE`; local functions: `verify_readlinkat`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`, `struct tst_buffers`; important macros/constants: `TEST_FILE`, `TEST_SYMLINK`.

## Control Flow

Function-level flow is organized around `verify_readlinkat`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdlib.h>`, `<stdio.h>`, `"tst_test.h"`, `"lapi/fcntl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.bufs`, `.tcnt`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink_file`; `readlink_symlink`; `readlinkat(%d, %s, %s, %ld)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c` is a 83-line LTP source file in the `readlinkat` syscall test area. readlinkat coverage for dirfd-relative symlink reads and invalid path, descriptor, and buffer cases. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `readlinkat`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SYMLINK`, `TST_EXP_FAIL`; local functions: `verify_readlinkat`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `TEST_FILE`, `SYMLINK_FILE`, `BUFF_SIZE`.

## Control Flow

Function-level flow is organized around `verify_readlinkat`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.tcnt`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`, `ENOTDIR`, `EBADF`, `ENOENT`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlinkat(%d, %s, NULL, %ld)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readlinkat/readlinkat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readv/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readv/Makefile` is the LTP leaf Makefile for the `readv` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: readv vector-read coverage for normal reads and invalid iovec/count/descriptor cases.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `readv` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv01.c` is a 124-line LTP source file in the `readv` syscall test area. readv vector-read coverage for normal reads and invalid iovec/count/descriptor cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `readv`, `SAFE_CLOSE`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`; local functions: `test_readv`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct testcase`, `struct tst_test`, `struct tst_tag`, `struct tst_buffers`; important macros/constants: `CHUNK`.

## Control Flow

Function-level flow is organized around `test_readv`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<stdlib.h>`, `<sys/types.h>`, `<sys/uio.h>`, `<fcntl.h>`, `<memory.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.cleanup`, `.test`, `.tcnt`, `.needs_tmpdir`, `.tags`, `.bufs`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readv() with 0 I/O vectors`; `readv() with NULL I/O vectors`; `readv() with too big I/O vectors`; `readv() with multiple I/O vectors`; `readv() with zero-len buffer`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c` is a 103-line LTP source file in the `readv` syscall test area. readv vector-read coverage for normal reads and invalid iovec/count/descriptor cases. Source description: 07/2001 Ported by Wayne Boyer 05/2002 Ported by Jacky Malcles

## Important APIs, Types, and Functions

called APIs/macros: `readv`, `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`, `TST_EXP_FAIL2`; local functions: `verify_readv`, `setup`, `cleanup`; struct/table types referenced: `struct iovec`, `struct tcase`, `struct tst_test`; important macros/constants: `K_1`, `MODES`, `CHUNK`.

## Control Flow

Function-level flow is organized around `verify_readv`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/uio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.needs_tmpdir`, `.setup`, `.cleanup`, `.test`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EFAULT`, `EISDIR`, `EBADF`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readv(%d, %p, %d)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/readv/readv02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/realpath/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/realpath/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/realpath/Makefile` is the LTP leaf Makefile for the `realpath` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: realpath libc path canonicalization coverage for success and error paths over temporary filesystem fixtures.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `realpath` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/realpath/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c` is a 45-line LTP source file in the `realpath` syscall test area. realpath libc path canonicalization coverage for success and error paths over temporary filesystem fixtures. Source description: Based on the reproducer posted upstream so other copyrights may apply. Author: Dmitry V. Levin <ldv@altlinux.org> LTP conversion from glibc source: Petr Vorel <pvorel@suse.cz>

## Important APIs, Types, and Functions

called APIs/macros: `realpath`, `SAFE_CHROOT`, `SAFE_MKDIR`, `TST_EXP_FAIL_PTR_NULL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`, `struct tst_tag`; important macros/constants: `CHROOT_DIR`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `<errno.h>`, `<stdlib.h>`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.needs_root`, `.needs_tmpdir`, `.tags`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOENT`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/realpath/realpath01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/reboot/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/reboot/Makefile` is the LTP leaf Makefile for the `reboot` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: reboot syscall coverage for permission, magic-number, and command validation without actually rebooting the test host.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `reboot` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot01.c` is a 39-line LTP source file in the `reboot` syscall test area. reboot syscall coverage for permission, magic-number, and command validation without actually rebooting the test host. Source description: Author: Aniruddha Marathe <aniruddha.marathe@wipro.com>

## Important APIs, Types, and Functions

called APIs/macros: `reboot`, `TST_EXP_PASS`; local functions: `run`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `CMD_DESC`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<sys/reboot.h>`, `<linux/reboot.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_root`, `.test`, `.tcnt`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c` is a 56-line LTP source file in the `reboot` syscall test area. reboot syscall coverage for permission, magic-number, and command validation without actually rebooting the test host. Source description: Author: Aniruddha Marathe <aniruddha.marathe@wipro.com>

## Important APIs, Types, and Functions

called APIs/macros: `reboot`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`; local functions: `run`; struct/table types referenced: `struct passwd`, `struct tcase`, `struct tst_test`; important macros/constants: `INVALID_CMD`, `CMD_DESC`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<sys/reboot.h>`, `<linux/reboot.h>`, `<pwd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.needs_root`, `.test`, `.tcnt`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EINVAL`, `EPERM`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/reboot/reboot02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recv/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recv/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recv/Makefile` is the LTP leaf Makefile for the `recv` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: recv socket syscall coverage across stream/datagram descriptors, invalid arguments, and expected network errno paths.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `recv` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c` is a 281-line LTP source file in the `recv` syscall test area. recv socket syscall coverage across stream/datagram descriptors, invalid arguments, and expected network errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `recv`, `socket`, `connect`, `bind`, `listen`, `accept`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`; local functions: `do_child`, `start_server`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`; struct/table types referenced: `struct sockaddr_in`, `struct test_case_t`, `struct timeval`, `struct sockaddr`.

## Control Flow

Function-level flow is organized around `do_child`, `start_server`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket state: file descriptors, sockaddr structures, send/receive buffers, optional child servers, and errno values returned by the network stack.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<fcntl.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<sys/signal.h>`, `<sys/un.h>`, `<netinet/in.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; signal or child-process synchronization must avoid races Explicit errno expectations include `EBADF`, `ENOTSOCK`, `EFAULT`, `EINVAL`, `EAGAIN`, `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `invalid socket`; ` %ld (expected %d), errno %d (expected`; `connect failed`; `client setup1 failed - no message ready in 2 sec`; `server socket failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/Makefile` is the LTP leaf Makefile for the `recvfrom` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: recvfrom socket syscall coverage with address buffers, message buffers, descriptor states, and expected errno behavior.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `recvfrom` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/recvfrom01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/recvfrom01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/recvfrom01.c` is a 312-line LTP source file in the `recvfrom` syscall test area. recvfrom socket syscall coverage with address buffers, message buffers, descriptor states, and expected errno behavior.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `recvfrom`, `socket`, `connect`, `bind`, `listen`, `accept`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`; local functions: `do_child`, `setup`, `setup0`, `setup1`, `setup2`, `cleanup`, `cleanup0`, `cleanup1`, `start_server`, `main`; struct/table types referenced: `struct sockaddr_in`, `struct test_case_t`, `struct sockaddr`, `struct timeval`.

## Control Flow

Function-level flow is organized around `do_child`, `setup`, `setup0`, `setup1`, `setup2`, `cleanup`, `cleanup0`, `cleanup1`, `start_server`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket state: file descriptors, sockaddr structures, send/receive buffers, optional child servers, and errno values returned by the network stack.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<fcntl.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<sys/signal.h>`, `<sys/un.h>`, `<netinet/in.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; signal or child-process synchronization must avoid races Explicit errno expectations include `EBADF`, `ENOTSOCK`, `EINVAL`, `EFAULT`, `EAGAIN`, `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `invalid socket`; `invalid socket buffer`; `invalid socket addr length`; ` %ld (expected %d), errno %d (expected`; `open(/dev/null) failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvfrom/recvfrom01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/Makefile` is the LTP leaf Makefile for the `recvmmsg` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: recvmmsg multi-message receive coverage for datagram sockets, timeout handling, and kernel feature availability.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `recvmmsg` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c` is a 179-line LTP source file in the `recvmmsg` syscall test area. recvmmsg multi-message receive coverage for datagram sockets, timeout handling, and kernel feature availability. Source description: \ Test recvmmsg() errors: - EBADF  Bad socket file descriptor - EFAULT Bad message vector address - EINVAL Bad seconds value for the timeout argument - EINVAL Bad nanoseconds value for the timeout argument - EFAULT Bad timeout address

## Important APIs, Types, and Functions

called APIs/macros: `recvmmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_SOCKET`, `SAFE_WAITPID`, `TEST`, `TST_EXP_FAIL2`, `TST_GET_UNUSED_PORT`; local functions: `verify_recvmmsg`, `test_bad_addr`, `do_test`, `setup`, `cleanup`; struct/table types referenced: `struct mmsghdr`, `struct iovec`, `struct tst_ts`, `struct test_case`, `struct time64_variants`, `struct sockaddr_in`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; important macros/constants: `_GNU_SOURCE`, `VLEN`.

## Control Flow

Function-level flow is organized around `verify_recvmmsg`, `test_bad_addr`, `do_test`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket state: file descriptors, sockaddr structures, send/receive buffers, optional child servers, and errno values returned by the network stack.

## Dependencies and Integration Points

Direct includes: `"../sendmmsg/sendmmsg.h"`. Designated initializer fields seen include `.desc`, `.fd`, `.exp_errno`, `.msg_vec`, `.tv_sec`, `.tv_nsec`, `.bad_ts_addr`, `.test`, `.tcnt`, `.setup`, `.cleanup`, `.test_variants`, `.forks_child`, `.bufs`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; signal or child-process synchronization must avoid races Explicit errno expectations include `EBADF`, `EFAULT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `bad socket file descriptor`; `Child killed by expected signal`; `sendmmsg() failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/Makefile` is the LTP leaf Makefile for the `recvmsg` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `CPPFLAGS		+= -I$(abs_srcdir)/../utils`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `recvmsg` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c` is a 486-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `recvmsg`, `SAFE_ACCEPT`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_GETSOCKNAME`, `SAFE_LISTEN`, `SAFE_OPEN`, `SAFE_SEND`, `SAFE_SENDMSG`, `SAFE_SIGNAL`, `SAFE_SOCKET`, `SAFE_UNLINK`, `TEST`; local functions: `setup_all`, `setup_invalid_sock`, `setup_valid_sock`, `setup_valid_msg_control`, `setup_large_msg_control`, `cleanup_all`, `cleanup_invalid_sock`, `cleanup_close_sock`, `cleanup_reset_all`, `do_child`, `start_server`, `run`, `sender`; struct/table types referenced: `struct sockaddr_in`, `struct sockaddr_un`, `struct msghdr`, `struct cmsghdr`, `struct iovec`, `struct tcase`, `struct sockaddr`, `struct timeval`, `struct tst_test`; important macros/constants: `MSG`, `BUF_SIZE`, `CONTROL_LEN`.

## Control Flow

Function-level flow is organized around `setup_all`, `setup_invalid_sock`, `setup_valid_sock`, `setup_valid_msg_control`, `setup_large_msg_control`, `cleanup_all`, `cleanup_invalid_sock`, `cleanup_close_sock`, `cleanup_reset_all`, `do_child`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.domain`, `.type`, `.iov`, `.iovcnt`, `.recv_buf`, `.buflen`, `.msg`, `.from`, `.fromlen`, `.exp_errno`, `.setup`, `.cleanup`, `.desc`, `.flags`, `.test`, `.tcnt`, `.forks_child`, `.needs_tmpdir`.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths. Explicit errno expectations include `EBADF`, `ENOTSOCK`, `EINVAL`, `EFAULT`, `EMSGSIZE`, `EAGAIN`, `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `invalid socket`; `invalid socket length`; `%s: expected %d, returned %ld`; `%s: expected %s`; `%s passed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c` is a 103-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths.

## Important APIs, Types, and Functions

called APIs/macros: `recvmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`; local functions: `verify_recvmsg`, `cleanup`; struct/table types referenced: `struct sockaddr_in6`, `struct iovec`, `struct msghdr`, `struct sockaddr`, `struct tst_test`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `verify_recvmsg`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<string.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<netinet/in.h>`, `"tst_test.h"`, `"lapi/socket.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.sin6_family`, `.sin6_port`, `.sin6_addr`, `.iov_base`, `.iov_len`, `.msg_name`, `.msg_namelen`, `.msg_iov`, `.msg_iovlen`, `.msg_control`, `.msg_controllen`, `.msg_flags`, `.test_all`, `.cleanup`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/socket.h`; `recvmsg(..., MSG_PEEK) failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c` is a 156-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `recvmsg`, `socket`, `sendmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_RECVMSG`, `SAFE_SOCKET`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`; local functions: `setup`, `client`, `server`, `verify_recvmsg`; struct/table types referenced: `struct sockaddr_in`, `struct msghdr`, `struct iovec`, `struct sockaddr`, `struct tst_test`, `struct tst_tag`; important macros/constants: `AF_RDS`.

## Control Flow

Function-level flow is organized around `setup`, `client`, `server`, `verify_recvmsg`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<string.h>`, `<sys/types.h>`, `<sys/socket.h>`, `"tst_safe_net.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.forks_child`, `.needs_checkpoints`, `.setup`, `.test_all`, `.tags`.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths. Explicit errno expectations include `EAFNOSUPPORT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `rds was not supported`; `socket() failed with rds`; `sendmsg() failed to send data to server`; `expected %lu`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/Makefile` is the LTP leaf Makefile for the `remap_file_pages` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: remap_file_pages virtual-memory coverage for file-backed mappings, page remapping, and invalid parameter/error behavior.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `remap_file_pages` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages01.c` is a 273-line LTP source file in the `remap_file_pages` syscall test area. remap_file_pages virtual-memory coverage for file-backed mappings, page remapping, and invalid parameter/error behavior.

## Important APIs, Types, and Functions

called APIs/macros: `remap_file_pages`, `mmap`; local functions: `setup`, `cleanup`, `test_nonlinear`, `main`; important macros/constants: `_GNU_SOURCE`, `WINDOW_START`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `test_nonlinear`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `<sys/mman.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<fcntl.h>`, `<errno.h>`, `<stdlib.h>`, `<sys/times.h>`, `<sys/wait.h>`, `<sys/ioctl.h>`, `<sys/syscall.h>`, `<linux/unistd.h>`, `<lapi/mmap.h>`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `mmap Error, errno=%d : %s`; `open(%s, O_RDWR|O_CREAT|O_TRUNC,S_IRWXU) Failed, errno=%d : %s`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c` is a 158-line LTP source file in the `remap_file_pages` syscall test area. remap_file_pages virtual-memory coverage for file-backed mappings, page remapping, and invalid parameter/error behavior. Source description: DESCRIPTION The remap_file_pages() system call is used to create a non-linear mapping, that is, a mapping in which the pages of the file are mapped into a non-sequential order in memory.  The advantage of using remap_file_pages() over using repeated calls to mmap(2) is that the former  approach  does  not require the kernel to create additional VMA (Virtual Memory Area) data structures. Runs remap_file_pages with wrong values and see if got the expected error

## Important APIs, Types, and Functions

called APIs/macros: `remap_file_pages`, `mmap`, `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TEST`; local functions: `setup01`, `setup02`, `setup03`, `setup04`, `run`, `setup`, `cleanup`; struct/table types referenced: `struct tcase`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `WINDOW_START`.

## Control Flow

Function-level flow is organized around `setup01`, `setup02`, `setup03`, `setup04`, `run`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<sys/mman.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<sys/syscall.h>`, `<linux/unistd.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`, `.cleanup`, `.setup`, `.needs_tmpdir`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `remap_file_pages(2) %s expected %s got`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/remap_file_pages/remap_file_pages02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/Makefile` is the LTP leaf Makefile for the `removexattr` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: removexattr extended-attribute coverage for successful removals and missing/invalid xattr or pathname errors.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `removexattr` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr01.c` is a 124-line LTP source file in the `removexattr` syscall test area. removexattr extended-attribute coverage for successful removals and missing/invalid xattr or pathname errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `removexattr`, `SAFE_TOUCH`, `TEST`; local functions: `verify_removexattr`, `setup`, `cleanup`, `main`; important macros/constants: `USER_KEY`, `VALUE`, `VALUE_SIZE`.

## Control Flow

Function-level flow is organized around `verify_removexattr`, `setup`, `cleanup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"config.h"`, `<errno.h>`, `<sys/types.h>`, `<sys/xattr.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOTSUP`, `ENODATA`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `no xattr support in fs or `; `setxattr() failed`; `removexattr() failed`; `getxattr() succeeded for deleted key`; `getxattr() failed unexpectedly`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c` is a 128-line LTP source file in the `removexattr` syscall test area. removexattr extended-attribute coverage for successful removals and missing/invalid xattr or pathname errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `removexattr`, `SAFE_TOUCH`, `TEST`; local functions: `verify_removexattr`, `setup`, `cleanup`, `main`; struct/table types referenced: `struct test_case`.

## Control Flow

Function-level flow is organized around `verify_removexattr`, `setup`, `cleanup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"config.h"`, `<errno.h>`, `<sys/types.h>`, `<sys/xattr.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `ENODATA`, `ENOENT`, `EFAULT`, `ENOTSUP`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `No xattr support in fs or `; `removexattr() succeeded unexpectedly`; `removexattr() failed unexpectedly,`; ` expected %s`; `removexattr() failed as expected`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/removexattr/removexattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/Makefile` is the LTP leaf Makefile for the `rename` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rename` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename01.c` is a 81-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_STAT`, `SAFE_TOUCH`, `TST_EXP_EQ_LU`, `TST_EXP_FAIL`, `TST_EXP_PASS`; local functions: `swap`, `setup`, `run`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `MNT_POINT`.

## Control Flow

Function-level flow is organized around `swap`, `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename(%s, %s)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename03.c` is a 71-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_MKDIR`, `SAFE_RMDIR`, `SAFE_STAT`, `SAFE_TOUCH`, `SAFE_UNLINK`, `TST_EXP_EQ_LU`, `TST_EXP_FAIL`, `TST_EXP_PASS`; local functions: `run`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `MNT_POINT`, `OLD_FILE_NAME`, `NEW_FILE_NAME`, `OLD_DIR_NAME`, `NEW_DIR_NAME`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<sys/stat.h>`, `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename(%s, %s)`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename04.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename04.c` is a 48-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `DIR1`, `DIR2`, `TEMP_FILE`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EEXIST`, `ENOTEMPTY`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename() failed as expected`; `rename() succeeded unexpectedly`; `rename() failed, but not with expected errno`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename05.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename05.c` is a 40-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_FILE`, `TEMP_DIR`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EISDIR`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename06.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename06.c` is a 40-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_MKDIR`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `DIR1`, `DIR2`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EINVAL`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename07.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename07.c` is a 41-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_DIR`, `TEMP_FILE`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOTDIR`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename08.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename08.c` is a 41-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_FILE`, `INVALID_PATH`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EFAULT`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c` is a 61-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHOWN`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `SRCDIR`, `DESTDIR`, `SRCFILE`, `DESTFILE`, `PERMS`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<sys/types.h>`, `"tst_test.h"`, `"tst_safe_file_ops.h"`, `"tst_uid.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EACCES`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename()`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename10.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename10.c` is a 48-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_TOUCH`, `TST_EXP_FAIL`; local functions: `setup`, `run`; struct/table types referenced: `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_FILE`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENAMETOOLONG`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c` is a 187-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_RMDIR`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `SAFE_UNLINK`, `TEST`; local functions: `cleanup`, `setup`, `test_eloop`, `test_erofs`, `test_emlink`, `main`, `check_and_print`; important macros/constants: `MNTPOINT`, `TEST_EROFS`, `TEST_NEW_EROFS`, `TEST_EMLINK`, `TEST_NEW_EMLINK`, `TEST_NEW_ELOOP`, `ELOPFILE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `test_eloop`, `test_erofs`, `test_emlink`, `main`, `check_and_print`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<errno.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<sys/mount.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ELOOP`, `EROFS`, `EMLINK`, `ELOPFILE`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `rename11`; `Failed to obtain block device`; `failed as expected`; `failed unexpectedly; expected - %d : %s`; `rename succeeded unexpectedly`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c` is a 67-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CHDIR`, `SAFE_CHMOD`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `SAFE_STAT`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `run`; struct/table types referenced: `struct stat`, `struct passwd`, `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_DIR`, `TEMP_FILE1`, `TEMP_FILE2`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<pwd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EPERM`, `EACCES`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rename() failed as expected`; `rename() succeeded unexpectedly`; `rename() failed, but not with expected errno`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename13.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename13.c` is a 52-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: 07/2001 Ported by Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_LINK`, `SAFE_STAT`, `SAFE_TOUCH`, `TST_EXP_EQ_LU`, `TST_EXP_PASS`; local functions: `setup`, `run`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `MNT_POINT`, `TEMP_FILE1`, `TEMP_FILE2`.

## Control Flow

Function-level flow is organized around `setup`, `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating

## Test Signals

TPASS/TST_EXP_PASS success reports.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c` is a 166-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases.

## Important APIs, Types, and Functions

called APIs/macros: `rename`; local functions: `term`, `al`, `dochild1`, `dochild2`, `main`; struct/table types referenced: `struct sigaction`; important macros/constants: `FAILED`, `PASSED`, `RUNTIME`.

## Control Flow

Function-level flow is organized around `term`, `al`, `dochild1`, `dochild2`, `main`. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<errno.h>`, `<signal.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/wait.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `"test.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `rename14`; `./rename14`; `./rename14xyz`; `Test Passed`; `Test Failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c` is a 129-line LTP source file in the `rename` syscall test area. rename filesystem semantics coverage for success, replacement, directory constraints, sticky permissions, hard links, and errno cases. Source description: Authors: David Fenner, Jon Hendrickson

## Important APIs, Types, and Functions

called APIs/macros: `rename`, `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_RENAME`, `SAFE_STAT`, `SAFE_SYMLINK`, `SAFE_UNLINK`, `TST_EXP_EQ_LI`, `TST_EXP_FAIL`, `TST_EXP_PASS`; local functions: `test_existing`, `test_non_existing`, `test_creat`, `run`, `setup`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `MNTPOINT`, `OLDNAME`, `NEWNAME`, `OBJNAME`.

## Control Flow

Function-level flow is organized around `test_existing`, `test_non_existing`, `test_creat`, `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem structure: files, directories, links, permissions, mount points, and expected post-rename path existence/content. Most cases mutate dentries and then validate the resulting tree. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `"tst_tmpdir.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`, `.all_filesystems`, `.mntpoint`, `.format_device`, `.needs_root`.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOENT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Test rename() on symlink pointing to an existent path`; `Test rename() on symlink pointing to a non-existent path`; `Test rename() on symlink pointing to a path created lately`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rename/rename15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat/Makefile` is the LTP leaf Makefile for the `renameat` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: renameat dirfd-relative filesystem rename coverage for success and descriptor/path error behavior.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `renameat` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c` is a 245-line LTP source file in the `renameat` syscall test area. renameat dirfd-relative filesystem rename coverage for success and descriptor/path error behavior. Source description: Author: Yi Yang <yyangcdl@cn.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `renameat`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `cleanup`, `renameat_verify`, `main`; struct/table types referenced: `struct test_case_t`; important macros/constants: `_GNU_SOURCE`, `MNTPOINT`, `TESTDIR`, `NEW_TESTDIR`, `TESTDIR2`, `NEW_TESTDIR2`, `TESTDIR3`, `NEW_TESTDIR3`, `TESTFILE`, `NEW_TESTFILE`, `TESTFILE2`, `NEW_TESTFILE2`, `TESTFILE3`, `TESTFILE4`, `TESTFILE5`, `NEW_TESTFILE5`, `DIRMODE`, `FILEMODE`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `renameat_verify`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `<sys/stat.h>`, `<sys/time.h>`, `<stdlib.h>`, `<errno.h>`, `<string.h>`, `<signal.h>`, `<sys/mount.h>`, `"test.h"`, `"tso_safe_macros.h"`, `"lapi/fcntl.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

filesystem-specific behavior can require TCONF gating Explicit errno expectations include `EBADF`, `ENOTDIR`, `ELOOP`, `EROFS`, `EMLINK`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `renameat01`; `Failed to obtain block device`; `renameat() succeeded unexpectedly`; `renameat() failed unexpectedly`; `renameat() returned the expected value`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat/renameat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/Makefile` is the LTP leaf Makefile for the `renameat2` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `renameat2` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h` is a 35-line LTP source file in the `renameat2` syscall test area. renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

called APIs/macros: `renameat2`; local functions: `renameat2`; important macros/constants: `RENAMEAT2_H`.

## Control Flow

Function-level flow is organized around `renameat2`.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `"config.h"`, `"lapi/syscalls.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

renameat2 tests depend on syscall and filesystem flag support; filesystems that do not implement exchange/noreplace semantics must be detected cleanly.

## Test Signals

Build and LTP result output are the primary test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c` is a 163-line LTP source file in the `renameat2` syscall test area. renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

called APIs/macros: `renameat2`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `cleanup`, `renameat2_verify`, `main`; struct/table types referenced: `struct test_case`; important macros/constants: `_GNU_SOURCE`, `TEST_DIR`, `TEST_DIR2`, `TEST_FILE`, `TEST_FILE2`, `TEST_FILE3`, `NON_EXIST`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `renameat2_verify`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"test.h"`, `"tso_safe_macros.h"`, `"lapi/fcntl.h"`, `"renameat2.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

renameat2 tests depend on syscall and filesystem flag support; filesystems that do not implement exchange/noreplace semantics must be detected cleanly. Explicit errno expectations include `EEXIST`, `ENOENT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `renameat2.h`; `renameat201`; `close olddirfd failed`; `close newdirfd failed`; `RENAME_EXCHANGE flag is not implemeted on %s`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat202.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat202.c` is a 166-line LTP source file in the `renameat2` syscall test area. renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

called APIs/macros: `renameat2`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_STAT`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `cleanup`, `renameat2_verify`, `main`; struct/table types referenced: `struct stat`; important macros/constants: `_GNU_SOURCE`, `TEST_DIR`, `TEST_DIR2`, `TEST_FILE`, `TEST_FILE2`.

## Control Flow

Function-level flow is organized around `setup`, `cleanup`, `renameat2_verify`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `"test.h"`, `"tso_safe_macros.h"`, `"lapi/fcntl.h"`, `"renameat2.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

renameat2 tests depend on syscall and filesystem flag support; filesystems that do not implement exchange/noreplace semantics must be detected cleanly. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `renameat2.h`; `renameat202`; `close olddirfd failed`; `close newdirfd failed`; `close fd failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/Makefile` is the LTP leaf Makefile for the `request_key` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `LDLIBS		+= $(KEYUTILS_LIBS)`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `request_key` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key01.c` is a 46-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `TST_EXP_POSITIVE`; local functions: `verify_request_key`, `setup`; struct/table types referenced: `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_request_key`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `keyring`; `request_key() succeed`; `add_key() failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c` is a 83-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `keyctl`, `TST_EXP_FAIL2`; local functions: `verify_request_key`, `init_key`, `setup`; struct/table types referenced: `struct test_case`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_request_key`, `init_key`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `ENOKEY`, `EKEYREVOKED`, `EKEYEXPIRED`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `keyring`; `request_key(\`; `add_key() failed`; `failed to revoke a key`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c` is a 228-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `keyctl`, `SAFE_FORK`, `SAFE_WAITPID`, `TEST`; local functions: `run_child_add`, `run_child_request`, `do_test`; struct/table types referenced: `struct test_case`, `struct tst_test`, `struct tst_option`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `run_child_add`, `run_child_request`, `do_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<stdbool.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.tcnt`, `.forks_child`, `.runtime`, `.options`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `EINVAL`, `ENOKEY`, `EDQUOT`, `ENOENT`, `ENODEV`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `unexpected error adding key of type '%s'`; `unable to clear keyring`; `add_key() process runtime exceeded`; `unexpected error requesting key of type '%s'`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key04.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key04.c` is a 81-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `keyctl`, `TEST`; local functions: `do_test`; struct/table types referenced: `struct tst_test`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `do_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `EACCES`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/keyctl.h`; `failed to join new session keyring`; `failed to set permissions on session keyring`; `failed to set request-key default keyring`; `failed to read from session keyring`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c` is a 40-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors.

## Important APIs, Types, and Functions

called APIs/macros: `request_key`; local functions: `run`; struct/table types referenced: `struct tst_test`, `struct tst_tag`; important macros/constants: `ATTEMPTS`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<sys/syscall.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels.

## Test Signals

TPASS/TST_EXP_PASS success reports; notable reported messages include `Requesting dead key`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key06.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key06.c` is a 50-line LTP source file in the `request_key` syscall test area. request_key/keyring syscall coverage for key lookup, destination keyrings, permissions, regressions, and invalid argument errors. Source description: Author: Ma Xinjian <maxj.fnst@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `request_key`, `TST_EXP_FAIL2`; local functions: `verify_request_key`; struct/table types referenced: `struct test_case_t`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `verify_request_key`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is kernel keyring state: session keyrings, user keys, permissions, request destination policy, and child-process attempts to trigger request_key behavior. Keys are transient kernel objects scoped to the test session.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`, `"lapi/keyctl.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Keyring tests depend on kernel keyring support, capability and permission semantics, and historical CVE fixes. Some cases deliberately stress failure paths that could hang or crash buggy kernels. Explicit errno expectations include `EFAULT`, `EPERM`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/keyctl.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/request_key/request_key06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/Makefile` is the LTP leaf Makefile for the `rmdir` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rmdir` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c` is a 40-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts.

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_MKDIR`, `TEST`; local functions: `verify_rmdir`; struct/table types referenced: `struct stat`, `struct tst_test`; important macros/constants: `TESTDIR`.

## Control Flow

Function-level flow is organized around `verify_rmdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<unistd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.needs_tmpdir`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir(%s) failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c` is a 110-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `TEST`; local functions: `setup`, `verify_rmdir`; struct/table types referenced: `struct testcase`, `struct tst_test`; important macros/constants: `DIR_MODE`, `FILE_MODE`, `TESTDIR`, `TESTDIR2`, `TESTDIR3`, `TESTDIR4`, `MNT_POINT`, `TESTDIR5`, `TESTFILE`, `TESTFILE2`.

## Control Flow

Function-level flow is organized around `setup`, `verify_rmdir`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities. It integrates with LTP device mounting or filesystem-matrix execution.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`, `.needs_root`, `.needs_rofs`, `.mntpoint`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; filesystem-specific behavior can require TCONF gating Explicit errno expectations include `ENOTEMPTY`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EFAULT`, `ELOOP`, `EROFS`, `EBUSY`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir() succeeded unexpectedly (%li)`; `rmdir() failed as expected`; `rmdir() failed unexpectedly; expected: %d - %s`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c` is a 93-line LTP source file in the `rmdir` syscall test area. rmdir filesystem coverage for successful directory removal and error paths such as non-empty directories, loops, permissions, and read-only mounts.

## Important APIs, Types, and Functions

called APIs/macros: `rmdir`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_SETEUID`, `TEST`; local functions: `do_rmdir`, `setup`, `cleanup`; struct/table types referenced: `struct testcase`, `struct passwd`, `struct tst_test`; important macros/constants: `DIR_MODE`, `NOEXCUTE_MODE`, `TESTDIR`, `TESTDIR2`, `TESTDIR3`, `TESTDIR4`.

## Control Flow

Function-level flow is organized around `do_rmdir`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sys/stat.h>`, `<sys/types.h>`, `<pwd.h>`, `<unistd.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.cleanup`, `.tcnt`, `.test`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits Explicit errno expectations include `EPERM`, `EACCES`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `rmdir() succeeded unexpectedly`; `rmdir() got expected errno`; `expected EPERM, but got`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rmdir/rmdir03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/Makefile` is the LTP leaf Makefile for the `rt_sigaction` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_sigaction signal handler ABI coverage for normal installs and invalid user pointers or sigset sizes.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `LDLIBS			+= -lrt -lpthread`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_sigaction` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction01.c` is a 133-line LTP source file in the `rt_sigaction` syscall test area. rt_sigaction signal handler ABI coverage for normal installs and invalid user pointers or sigset sizes. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `TEST`; local functions: `cleanup`, `setup`, `handler`, `set_handler`, `main`; struct/table types referenced: `struct sigaction`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `handler`, `set_handler`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`, `<errno.h>`, `<sys/syscall.h>`, `<string.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Legacy signal tests are ABI-sensitive: signal numbers, SIGSETSIZE, bad user pointers, and direct syscall wrappers can vary by architecture.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Signal Handler Called with signal number %d`; `signal: %d `; `failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction02.c` is a 128-line LTP source file in the `rt_sigaction` syscall test area. rt_sigaction signal handler ABI coverage for normal installs and invalid user pointers or sigset sizes. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `TEST`; local functions: `cleanup`, `setup`, `main`; struct/table types referenced: `struct test_case_t`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`, `<errno.h>`, `<sys/syscall.h>`, `<string.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Legacy signal tests are ABI-sensitive: signal numbers, SIGSETSIZE, bad user pointers, and direct syscall wrappers can vary by architecture. Explicit errno expectations include `EFAULT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Signal %d`; `%s failure with sig: %d as expected errno  = %s : %s`; `rt_sigaction call succeeded: result = %ld got error %d:but expected  %d`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c` is a 146-line LTP source file in the `rt_sigaction` syscall test area. rt_sigaction signal handler ABI coverage for normal installs and invalid user pointers or sigset sizes. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `TEST`; local functions: `cleanup`, `setup`, `handler`, `set_handler`, `main`; struct/table types referenced: `struct test_case_t`, `struct sigaction`; important macros/constants: `_GNU_SOURCE`, `INVAL_SIGSETSIZE`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `handler`, `set_handler`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`, `<errno.h>`, `<sys/syscall.h>`, `<string.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Legacy signal tests are ABI-sensitive: signal numbers, SIGSETSIZE, bad user pointers, and direct syscall wrappers can vary by architecture. Explicit errno expectations include `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `Signal Handler Called with signal number %d`; `Signal %d`; `%s failure with sig: %d as expected errno  = %s : %s`; `rt_sigaction call succeeded: result = %ld got error %d:but expected  %d`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigaction/rt_sigaction03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/Makefile` is the LTP leaf Makefile for the `rt_sigprocmask` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_sigprocmask signal mask coverage for block/unblock/pending signal behavior and invalid argument handling.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_sigprocmask` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c` is a 169-line LTP source file in the `rt_sigprocmask` syscall test area. rt_sigprocmask signal mask coverage for block/unblock/pending signal behavior and invalid argument handling. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `ltp_rt_sigaction`, `rt_sigprocmask`, `TEST`; local functions: `cleanup`, `setup`, `sig_handler`, `main`; struct/table types referenced: `struct sigaction`; important macros/constants: `TEST_SIG`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `sig_handler`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<signal.h>`, `<errno.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"lapi/rt_sigaction.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Signal-mask tests can be flaky if pending signals leak between iterations or if the direct rt_sigprocmask sigset size is wrong for the architecture.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `sigemptyset call failed`; `sigaddset call failed`; `rt_sigaction call failed`; `rt_sigprocmask call failed`; `call to kill() failed`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c` is a 123-line LTP source file in the `rt_sigprocmask` syscall test area. rt_sigprocmask signal mask coverage for block/unblock/pending signal behavior and invalid argument handling. Source description: ***************************************************************************

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigprocmask`, `TEST`; local functions: `cleanup`, `setup`, `main`; struct/table types referenced: `struct test_case_t`.

## Control Flow

Function-level flow is organized around `cleanup`, `setup`, `main`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<signal.h>`, `<errno.h>`, `"test.h"`, `"lapi/syscalls.h"`, `"tso_signal.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Signal-mask tests can be flaky if pending signals leak between iterations or if the direct rt_sigprocmask sigset size is wrong for the architecture. Explicit errno expectations include `EINVAL`, `EFAULT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `tso_signal.h`; `Call to sigfillset() failed.`; `but should failed`; `Got expected errno`; `Got unexpected errno`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigprocmask/rt_sigprocmask02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/Makefile` is the LTP leaf Makefile for the `rt_sigqueueinfo` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`, `rt_sigqueueinfo01: CFLAGS += -pthread`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_sigqueueinfo` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h` is a 17-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Christian Amann <camann@suse.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`; local functions: `sys_rt_sigqueueinfo`; important macros/constants: `__RT_SIGQUEUEINFO_H__`.

## Control Flow

Function-level flow is organized around `sys_rt_sigqueueinfo`.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `"lapi/syscalls.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

Build and LTP result output are the primary test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c` is a 116-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Christian Amann <camann@suse.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`, `SAFE_MALLOC`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `TEST`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_TEST_TCONF`; local functions: `received_signal`, `verify_sigqueueinfo`, `setup`, `cleanup`; struct/table types referenced: `struct sigaction`, `struct tst_test`; important macros/constants: `SIGNAL`, `DATA`.

## Control Flow

Function-level flow is organized around `received_signal`, `verify_sigqueueinfo`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<signal.h>`, `<stdlib.h>`, `"config.h"`, `"tst_test.h"`, `"tst_safe_pthread.h"`, `"rt_sigqueueinfo.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `tst_safe_pthread.h`; `Received correct signal and data!`; `Received wrong signal and/or data!`; `Signal handling went wrong!`; `Failed to set sigaction for handler thread!`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c` is a 97-line LTP source file in the `rt_sigqueueinfo` syscall test area. rt_sigqueueinfo signal delivery coverage for siginfo payloads, threads, and invalid pid/signal/permission cases. Source description: Author: Ma Xinjian <maxj.fnst@fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigqueueinfo`, `SAFE_FORK`, `SAFE_WAITPID`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FAIL`, `TST_TEST_TCONF`; local functions: `setup`, `parent_do`, `child_do`, `verify_rt_sigqueueinfo`; struct/table types referenced: `struct test_case_t`, `struct tst_test`, `struct tst_buffers`.

## Control Flow

Function-level flow is organized around `setup`, `parent_do`, `child_do`, `verify_rt_sigqueueinfo`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<signal.h>`, `"config.h"`, `"tst_test.h"`, `"rt_sigqueueinfo.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.tcnt`, `.test`, `.forks_child`, `.needs_checkpoints`, `.bufs`. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; signal or child-process synchronization must avoid races Explicit errno expectations include `EINVAL`, `EPERM`, `ESRCH`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; notable reported messages include `no thread group matching tgid is found`; `This system does not support rt_sigqueueinfo()`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigqueueinfo/rt_sigqueueinfo02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/Makefile` is the LTP leaf Makefile for the `rt_sigsuspend` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_sigsuspend coverage for EINTR wakeup and restoration of the process signal mask.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_sigsuspend` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c` is a 63-line LTP source file in the `rt_sigsuspend` syscall test area. rt_sigsuspend coverage for EINTR wakeup and restoration of the process signal mask. Source description: Porting from Crackerjack to LTP is done by Manas Kumar Nayak maknayak@in.ibm.com> Waits for SIGALRM in rt_sigsuspend() then checks that process mask wasn't modified.

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigsuspend`, `SAFE_RT_SIGACTION`, `SAFE_RT_SIGPROCMASK`, `TEST`; local functions: `sig_handler`, `verify_rt_sigsuspend`; struct/table types referenced: `struct sigaction`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `sig_handler`, `verify_rt_sigsuspend`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `<signal.h>`, `<errno.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"lapi/safe_rt_signal.h"`, `"lapi/signal.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races Explicit errno expectations include `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/safe_rt_signal.h`; `lapi/signal.h`; `sigemptyset failed`; `rt_sigsuspend() failed unexpectedly`; `signal mask not preserved`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigsuspend/rt_sigsuspend01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/Makefile` is the LTP leaf Makefile for the `rt_sigtimedwait` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_sigtimedwait and time64 variant coverage through the shared signal-wait test executor.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_sigtimedwait` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/rt_sigtimedwait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/rt_sigtimedwait01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/rt_sigtimedwait01.c` is a 74-line LTP source file in the `rt_sigtimedwait` syscall test area. rt_sigtimedwait and time64 variant coverage through the shared signal-wait test executor.

## Important APIs, Types, and Functions

called APIs/macros: `rt_sigtimedwait`; local functions: `my_rt_sigtimedwait`, `my_rt_sigtimedwait_time64`, `run`, `setup`; struct/table types referenced: `struct sigwait_test_desc`, `struct time64_variants`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `my_rt_sigtimedwait`, `my_rt_sigtimedwait_time64`, `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process/thread signal state: signal masks, handlers, pending signals, siginfo payloads, and thread ids.

## Dependencies and Integration Points

Direct includes: `"time64_variants.h"`, `"tse_sigwait.h"`. Designated initializer fields seen include `.test`, `.tcnt`, `.test_variants`, `.setup`, `.forks_child`.

## Risks and Edge Cases

signal or child-process synchronization must avoid races Explicit errno expectations include `EINTR`.

## Test Signals

Build and LTP result output are the primary test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_sigtimedwait/rt_sigtimedwait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/Makefile` is the LTP leaf Makefile for the `rt_tgsigqueueinfo` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: rt_tgsigqueueinfo targeted thread-group signal delivery coverage for self, parent-to-thread, and thread-to-thread paths.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `rt_tgsigqueueinfo01: CFLAGS+=-pthread`, `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `rt_tgsigqueueinfo` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c` is a 181-line LTP source file in the `rt_tgsigqueueinfo` syscall test area. rt_tgsigqueueinfo targeted thread-group signal delivery coverage for self, parent-to-thread, and thread-to-thread paths. Source description: Author: Sumit Garg <sumit.garg@linaro.org>

## Important APIs, Types, and Functions

called APIs/macros: `rt_tgsigqueueinfo`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_SIGACTION`, `TEST`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`; local functions: `sigusr1_handler`, `verify_signal_self`, `verify_signal_parent_thread`, `verify_signal_inter_thread`, `run`, `setup`; struct/table types referenced: `struct tcase`, `struct sigaction`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `sigusr1_handler`, `verify_signal_self`, `verify_signal_parent_thread`, `verify_signal_inter_thread`, `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is thread identity and pending signal delivery: pthread-created sender/receiver threads, gettid results, a SIGUSR1 sigaction with SA_SIGINFO, and volatile globals recording the received signum and sigval pointer.

## Dependencies and Integration Points

Direct includes: `<err.h>`, `<pthread.h>`, `"tst_safe_pthread.h"`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.sa_flags`, `.sa_sigaction`, `.tcnt`, `.needs_checkpoints`, `.setup`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `tst_safe_pthread.h`; `rt_tgsigqueueinfo failed`; `Test signal to self succeeded`; `Failed to deliver signal/data to self thread`; `Test signal to different thread succeeded`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/rt_tgsigqueueinfo/rt_tgsigqueueinfo01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/Makefile` is the LTP leaf Makefile for the `sbrk` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sbrk` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk01.c` is a 34-line LTP source file in the `sbrk` syscall test area. sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior. Source description: AUTHOR : William Roske, CO-PILOT : Dave Fenner

## Important APIs, Types, and Functions

called APIs/macros: `sbrk`, `TST_EXP_PASS_PTR_VOID`; local functions: `run`; struct/table types referenced: `struct tcase`, `struct tst_test`.

## Control Flow

Function-level flow is organized around `run`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.tcnt`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

TPASS/TST_EXP_PASS success reports.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c` is a 37-line LTP source file in the `sbrk` syscall test area. sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior. Source description: Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `sbrk`, `TST_EXP_FAIL_PTR_VOID`; local functions: `run`, `setup`; struct/table types referenced: `struct tst_test`; important macros/constants: `INC`.

## Control Flow

Function-level flow is organized around `run`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.setup`.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOMEM`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c` is a 70-line LTP source file in the `sbrk` syscall test area. sbrk/brk coverage for heap growth/shrink success, ENOMEM failure, and 32-bit overflow regression behavior.

## Important APIs, Types, and Functions

called APIs/macros: `sbrk`, `brk`; local functions: `sbrk_test`; struct/table types referenced: `struct tst_test`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `sbrk_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `"lapi/abisize.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`, `.supported_archs`, `.needs_abi_bits`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `ENOMEM`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sbrk/sbrk03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/Makefile` is the LTP leaf Makefile for the `sched_get_priority_max` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sched_get_priority_max scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sched_get_priority_max` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max01.c` is a 47-line LTP source file in the `sched_get_priority_max` syscall test area. sched_get_priority_max scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_max`, `TST_EXP_VAL`; local functions: `run_test`; struct/table types referenced: `struct test_case`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `POLICY_DESC`.

## Control Flow

Function-level flow is organized around `run_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<sched.h>`, `"tst_test.h"`, `"lapi/sched.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

notable reported messages include `lapi/sched.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c` is a 26-line LTP source file in the `sched_get_priority_max` syscall test area. sched_get_priority_max scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_max`, `TST_EXP_FAIL`; local functions: `verif_sched_get_priority_max02`; struct/table types referenced: `struct tst_test`; important macros/constants: `SCHED_INVALID`.

## Control Flow

Function-level flow is organized around `verif_sched_get_priority_max02`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sched.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_max/sched_get_priority_max02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile` is the LTP leaf Makefile for the `sched_get_priority_min` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sched_get_priority_min scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sched_get_priority_min` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c` is a 47-line LTP source file in the `sched_get_priority_min` syscall test area. sched_get_priority_min scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_min`, `TST_EXP_VAL`; local functions: `run_test`; struct/table types referenced: `struct test_case`, `struct tst_test`; important macros/constants: `_GNU_SOURCE`, `POLICY_DESC`.

## Control Flow

Function-level flow is organized around `run_test`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<sched.h>`, `"tst_test.h"`, `"lapi/sched.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.tcnt`, `.test`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability.

## Test Signals

notable reported messages include `lapi/sched.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min02.c` is a 26-line LTP source file in the `sched_get_priority_min` syscall test area. sched_get_priority_min scheduling-policy priority-range coverage for valid policies and invalid-policy EINVAL.

## Important APIs, Types, and Functions

called APIs/macros: `sched_get_priority_min`, `TST_EXP_FAIL`; local functions: `verif_sched_get_priority_min02`; struct/table types referenced: `struct tst_test`; important macros/constants: `SCHED_INVALID`.

## Control Flow

Function-level flow is organized around `verif_sched_get_priority_min02`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sched.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

The main risk is errno drift or unsupported syscall behavior across architectures, kernel versions, and libc wrapper availability. Explicit errno expectations include `EINVAL`.

## Test Signals

TFAIL/TST_EXP_FAIL errno or invariant checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_get_priority_min/sched_get_priority_min02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/Makefile` is the LTP leaf Makefile for the `sched_getaffinity` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sched_getaffinity CPU-mask coverage for valid masks and EFAULT/EINVAL/ESRCH error behavior.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sched_getaffinity` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c` is a 96-line LTP source file in the `sched_getaffinity` syscall test area. sched_getaffinity CPU-mask coverage for valid masks and EFAULT/EINVAL/ESRCH error behavior. Source description: Description: This case tests the sched_getaffinity() syscall History:     Porting from Crackerjack to LTP is done by Manas Kumar Nayak maknayak@in.ibm.com>

## Important APIs, Types, and Functions

called APIs/macros: `sched_getaffinity`, `SAFE_SYSCONF`, `TEST`; local functions: `errno_test`, `do_test`, `setup`; struct/table types referenced: `struct tst_test`; important macros/constants: `_GNU_SOURCE`.

## Control Flow

Function-level flow is organized around `errno_test`, `do_test`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is the process program break and virtual address space. The tests do not persist data beyond the process lifetime.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<sched.h>`, `<stdlib.h>`, `<string.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`, `"lapi/cpuset.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.setup`, `.test_all`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive Explicit errno expectations include `EINVAL`, `EFAULT`, `ESRCH`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `sched_getaffinity() returned %ld, expected -1`; `sched_getaffinity() should fail with %s`; `sched_getaffinity() failed`; `fail to get cpu affinity`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getaffinity/sched_getaffinity01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/Makefile

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/Makefile` is the LTP leaf Makefile for the `sched_getattr` syscall test directory. It connects the local tests to the common LTP syscall build rules so the cases in this directory are built and installed as part of the kernel syscall suite. Directory purpose: sched_getattr scheduler attribute readback coverage after setting SCHED_DEADLINE parameters.

## Important APIs, Types, and Functions

This Makefile has no C APIs. It contributes make variables and include relationships. Notable build lines: `include $(top_srcdir)/include/mk/testcases.mk`, `CFLAGS			+= -pthread`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

## Control Flow

Build flow is declarative: the LTP make recursion enters this directory, evaluates this file, then uses the included common rules to compile each C test in the folder. Any per-target flags here affect only the named local executable.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. Its state is build metadata: target-specific compiler flags, library links, or inclusion of shared LTP make rules.

## Dependencies and Integration Points

The integration point is the LTP build system under `testcases/kernel/syscalls`. It depends on the surrounding make include stack and on the C sources in the same directory.

## Risks and Edge Cases

Missing target-specific flags can silently break tests that need pthreads, realtime libraries, filesystem helpers, or generated syscall wrappers. Over-broad flags here would affect unrelated test binaries in the same directory.

## Test Signals

The signal is build/install coverage: the `sched_getattr` tests compile through the LTP syscall build and any special targets receive their required flags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c` is a 105-line LTP source file in the `sched_getattr` syscall test area. sched_getattr scheduler attribute readback coverage after setting SCHED_DEADLINE parameters.

## Important APIs, Types, and Functions

called APIs/macros: `sched_getattr`, `sched_setattr`; local functions: `main`; struct/table types referenced: `struct sched_attr`; important macros/constants: `_GNU_SOURCE`, `RUNTIME_VAL`, `PERIOD_VAL`, `DEADLINE_VAL`.

## Control Flow

Function-level flow is organized around `main`. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is scheduler state for the current process/thread: the test sets a SCHED_DEADLINE policy and reads back a `struct sched_attr` to compare runtime, period, and deadline fields. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<unistd.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<time.h>`, `<linux/unistd.h>`, `<linux/kernel.h>`, `<linux/types.h>`, `<sys/syscall.h>`, `<pthread.h>`, `<errno.h>`, `"test.h"`, `"lapi/sched.h"`. Uses the older LTP `test.h` harness and legacy result macros. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Scheduler deadline tests require privileges and kernel SCHED_DEADLINE support; systems without the policy or with constrained runtime/deadline settings should fail setup rather than misreporting readback behavior.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `lapi/sched.h`; `sched_getattr01`; `sched_setattr() failed`; `sched_getattr() failed`; `sched_runtime is incorrect (%`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr01.c -->
