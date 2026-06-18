# subset-b-009358 Research

Grouped research for the 171 source files assigned to `subset-b-009358`. Each source file was read from the local tree in full, and each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statmount.c -->
# sources/test-tools/strace/tests/statmount.c

## Purpose
Covers strace decoder coverage for `statmount`. Source comments/macros state: Check decoding of statmount syscall. End of VALID_STATMOUNT_STR STATMOUNT_??? bytes %zu..%zu MS_??? MS_??? MOUNT_ATTR_??? STATMOUNT_??? Source read: 666 lines, 19991 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>, <linux/mount.h>; defines/undefs: INJ_STR, VALID_STATMOUNT, VALID_STATMOUNT_STR, INVALID_STATMOUNT, INVALID_STATMOUNT_STR, ALL_STATMOUNT, ALL_STATMOUNT_STR, VALID_SB_MAGIC, VALID_SB_MAGIC_STR, INVALID_SB_MAGIC, INVALID_SB_MAGIC_STR, VALID_SB_FLAGS, VALID_SB_FLAGS_STR, INVALID_SB_FLAGS, INVALID_SB_FLAGS_STR, ALL_SB_FLAGS, ALL_SB_FLAGS_STR, VALID_MOUNT_ATTR, VALID_MOUNT_ATTR_STR, INVALID_MOUNT_ATTR, INVALID_MOUNT_ATTR_STR, ALL_MOUNT_ATTR, ALL_MOUNT_ATTR_STR, VALID_MNT_PROPAGATION, VALID_MNT_PROPAGATION_STR, INVALID_MNT_PROPAGATION, INVALID_MNT_PROPAGATION_STR, ALL_MNT_PROPAGATION; C functions: k_statmount, test_req, test_stm_bad, test_stm_all_ops, test_stm_str_ops, test_stm_array_ops, main; syscall numbers/wrappers: statmount, __NR_statmount; struct types: mnt_id_req, statmount, stm_ops_t.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: statmount, __NR_statmount.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-all.c -->
# sources/test-tools/strace/tests/status-all.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=all filtering for failed and successful syscalls. Source read: 24 lines, 518 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-detached-threads.c -->
# sources/test-tools/strace/tests/status-detached-threads.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=detached filtering when a non-leader thread invokes execve. Source read: 56 lines, 1205 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <stdio.h>, <time.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettid, __NR_gettid; struct types: timespec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: gettid, __NR_gettid.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-detached-threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed-long.c -->
# sources/test-tools/strace/tests/status-failed-long.c

## Purpose
Variant wrapper for `status-failed.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 27 bytes.

## Important APIs, Types, And Functions
includes/imports: "status-failed.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `status-failed.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `status-failed.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed-long.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed-status.c -->
# sources/test-tools/strace/tests/status-failed-status.c

## Purpose
Variant wrapper for `status-failed.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 27 bytes.

## Important APIs, Types, And Functions
includes/imports: "status-failed.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `status-failed.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `status-failed.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed.c -->
# sources/test-tools/strace/tests/status-failed.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=failed filtering for failed and successful syscalls. Source read: 24 lines, 521 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-failed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-none-f.c -->
# sources/test-tools/strace/tests/status-none-f.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check basic seccomp filtering with large number of traced syscalls. Source read: 19 lines, 344 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-none-f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-none-threads.c -->
# sources/test-tools/strace/tests/status-none-threads.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=none filtering when a non-leader thread invokes execve. Source read: 53 lines, 1059 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <errno.h>, <pthread.h>, <stdio.h>, <unistd.h>, "scno.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettid, __NR_gettid; struct types: timespec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: gettid, __NR_gettid.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-none-threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-none.c -->
# sources/test-tools/strace/tests/status-none.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check basic -e status=none syscall filtering. Source read: 18 lines, 278 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-long.c -->
# sources/test-tools/strace/tests/status-successful-long.c

## Purpose
Variant wrapper for `status-successful.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 31 bytes.

## Important APIs, Types, And Functions
includes/imports: "status-successful.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `status-successful.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `status-successful.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-long.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-status.c -->
# sources/test-tools/strace/tests/status-successful-status.c

## Purpose
Variant wrapper for `status-successful.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 31 bytes.

## Important APIs, Types, And Functions
includes/imports: "status-successful.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `status-successful.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `status-successful.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-threads.c -->
# sources/test-tools/strace/tests/status-successful-threads.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=successful filtering when a non-leader thread invokes execve. wait for execve Source read: 71 lines, 1504 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <stdio.h>, <unistd.h>, <sys/uio.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettid, __NR_gettid; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: gettid, __NR_gettid.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful-threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful.c -->
# sources/test-tools/strace/tests/status-successful.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=successful filtering for failed and successful syscalls. Source read: 24 lines, 525 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-successful.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-unfinished-threads.c -->
# sources/test-tools/strace/tests/status-unfinished-threads.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=unfinished filtering when a non-leader thread invokes execve. Source read: 67 lines, 1430 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <stdio.h>, <unistd.h>, "kernel_old_timespec.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: nanosleep, gettid, __NR_nanosleep, __NR_gettid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: nanosleep, gettid, __NR_nanosleep, __NR_gettid.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-unfinished-threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-unfinished.c -->
# sources/test-tools/strace/tests/status-unfinished.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check basic -e status=unfinished syscall filtering. Source read: 19 lines, 329 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-unfinished.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status.c -->
# sources/test-tools/strace/tests/status.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Helper function to check -e status option. Source read: 21 lines, 509 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: test_status_chdir.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statx.c -->
# sources/test-tools/strace/tests/statx.c

## Purpose
Covers strace decoder coverage for `statx`. Source read: 42 lines, 1238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <linux/stat.h>, "xlat.h", "xlat/statx_masks.h", "xlat/statx_attrs.h", "xlat/at_statx_sync_types.h", "xstatx.c"; defines/undefs: IS_STATX, TEST_SYSCALL_STR, STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64, TEST_SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, PRINT_SYSCALL_FOOTER; syscall numbers/wrappers: statx, __NR_statx; struct types: statx.

## Control Flow
primary syscall coverage: statx, __NR_statx.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--always-show-pid.c -->
# sources/test-tools/strace/tests/strace--always-show-pid.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Check the PID prefix output with --always-show-pid option. Source read: 22 lines, 415 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--always-show-pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--decode-pids-comm.c -->
# sources/test-tools/strace/tests/strace--decode-pids-comm.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Test -Y/--decode-pids=comm option. The executable built from this source file should have a long name (> 16) to test how strace reports the initial value of /proc/$pid/comm. Even if linux returns a longer name, strace should not crash. Source read: 123 lines, 3042 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <signal.h>, <stdio.h>, <stdlib.h>, <string.h>, <sys/prctl.h>, <unistd.h>, <sys/types.h>, <sys/wait.h>; defines/undefs: NEW_NAME; C functions: do_default_action, do_execve_action, main; syscall numbers/wrappers: tgkill, __NR_tgkill.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: tgkill, __NR_tgkill.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--decode-pids-comm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-all.c -->
# sources/test-tools/strace/tests/strace--strings-in-hex-all.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii-chars.c -->
# sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii-chars.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii-chars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii.c -->
# sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-non-ascii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-none.c -->
# sources/test-tools/strace/tests/strace--strings-in-hex-none.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex-none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex.c -->
# sources/test-tools/strace/tests/strace--strings-in-hex.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--strings-in-hex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-c.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-c.c

## Purpose
Variant wrapper for `strace--syscall-limit.c`. It defines `PRINT_VALID, PRINT_INVALID, PRINT_STATS` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 4 lines, 103 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID, PRINT_INVALID, PRINT_STATS.

## Control Flow
Preprocessor-only flow: set `PRINT_VALID, PRINT_INVALID, PRINT_STATS`, include `strace--syscall-limit.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--syscall-limit.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-path.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-path.c

## Purpose
Covers the `--syscall-limit` option and related summary/status interactions. Source comments/macros state: Test --syscall-limit option in combination with --trace-path option. Source read: 11 lines, 257 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-c.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-status-c.c

## Purpose
Variant wrapper for `strace--syscall-limit.c`. It defines `PRINT_VALID, PRINT_INVALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 6 lines, 146 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID, PRINT_INVALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT.

## Control Flow
Preprocessor-only flow: set `PRINT_VALID, PRINT_INVALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT`, include `strace--syscall-limit.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--syscall-limit.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c

## Purpose
Variant wrapper for `strace--syscall-limit.c`. It defines `PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 5 lines, 122 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT.

## Control Flow
Preprocessor-only flow: set `PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT`, include `strace--syscall-limit.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--syscall-limit.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-status.c

## Purpose
Covers the `--syscall-limit` option and related summary/status interactions. Source comments/macros state: Test --syscall-limit option in combination with --status option. Source read: 11 lines, 253 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-summary.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-summary.c

## Purpose
Variant wrapper for `strace--syscall-limit.c`. It defines `PRINT_STATS` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 57 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_STATS.

## Control Flow
Preprocessor-only flow: set `PRINT_STATS`, include `strace--syscall-limit.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--syscall-limit.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit.c -->
# sources/test-tools/strace/tests/strace--syscall-limit.c

## Purpose
Covers the `--syscall-limit` option and related summary/status interactions. Source comments/macros state: Test --syscall-limit option. !PRINT_VALID PRINT_VALID print print print the tracer is expected to detach at this point if TOTAL_CNT < 4. print the tracer is expected to detach at this point print PRINT_STATS Source read: 151 lines, 3181 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <fcntl.h>, <stdio.h>, <stdlib.h>, <unistd.h>, <sys/types.h>, <sys/wait.h>; defines/undefs: PRINT_VALID, PRINT_INVALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT, AT_FDCWD, AT_REMOVEDIR; C functions: write_status, test_chdir, test_rmdir, main; syscall numbers/wrappers: unlinkat, __NR_unlinkat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: unlinkat, __NR_unlinkat.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-Y-0123456789.c -->
# sources/test-tools/strace/tests/strace-Y-0123456789.c

## Purpose
Variant wrapper for `strace--decode-pids-comm.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 38 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--decode-pids-comm.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `strace--decode-pids-comm.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--decode-pids-comm.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-Y-0123456789.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-k-z.c -->
# sources/test-tools/strace/tests/strace-k-z.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Check that stack tracing combined with syscall status filtering does not abort strace with "bug: unprinted entries in queue". Source read: 22 lines, 461 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-k-z.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-n.c -->
# sources/test-tools/strace/tests/strace-n.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Test strace's -n option. Source read: 38 lines, 684 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, <errno.h>; defines/undefs: SC_listen; C functions: main; syscall numbers/wrappers: socketcall, listen, __NR_socketcall, __NR_listen.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: socketcall, listen, __NR_socketcall, __NR_listen.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-n.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-no-x.c -->
# sources/test-tools/strace/tests/strace-no-x.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-no-x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p-Y-p2.c -->
# sources/test-tools/strace/tests/strace-p-Y-p2.c

## Purpose
Variant wrapper for `strace-p1-Y-p.c`. It defines `MY_COMM` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 59 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-p1-Y-p.c"; defines/undefs: MY_COMM.

## Control Flow
Preprocessor-only flow: set `MY_COMM`, include `strace-p1-Y-p.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-p1-Y-p.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p-Y-p2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p1-Y-p.c -->
# sources/test-tools/strace/tests/strace-p1-Y-p.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: This file is part of strace-p-Y-p strace test. Source read: 43 lines, 827 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <stdlib.h>, <unistd.h>; defines/undefs: MY_COMM; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p1-Y-p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-x.c -->
# sources/test-tools/strace/tests/strace-x.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Test strace's -x option. Source read: 100 lines, 2890 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines/undefs: STRACE_X, XOUT; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-xx.c -->
# sources/test-tools/strace/tests/strace-xx.c

## Purpose
Variant wrapper for `strace-x.c`. It defines `STRACE_X` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace-x.c"; defines/undefs: STRACE_X.

## Control Flow
Preprocessor-only flow: set `STRACE_X`, include `strace-x.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace-x.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/subdir.c -->
# sources/test-tools/strace/tests/subdir.c

## Purpose
Covers strace decoder coverage for `subdir`. Source read: 40 lines, 745 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <dirent.h>, <unistd.h>, <sys/stat.h>; defines/undefs: none; C functions: create_and_enter_subdir, leave_and_remove_subdir.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/subdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/swap.c -->
# sources/test-tools/strace/tests/swap.c

## Purpose
Covers strace decoder coverage for `swap`. Source comments/macros state: Check decoding of swapon and swapoff tests. Source read: 52 lines, 1264 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/swap.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: swapon, swapoff, __NR_swapon, __NR_swapoff.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: swapon, swapoff, __NR_swapon, __NR_swapoff.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sxetmask.c -->
# sources/test-tools/strace/tests/sxetmask.c

## Purpose
Covers strace decoder coverage for `sxetmask`. Source comments/macros state: Check decoding of sgetmask and ssetmask syscalls. Block, reset, and raise SIGUSR1. If a subsequent ssetmask call fails to set the proper mask, the process will be terminated by SIGUSR1. Use a regular sigprocmask call to check the value returned by the ssetmask call being tested. Source read: 105 lines, 2525 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <signal.h>, <stdio.h>, <stdint.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: k_sgetmask, k_ssetmask, main; syscall numbers/wrappers: sgetmask, ssetmask, __NR_sgetmask, __NR_ssetmask.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: sgetmask, ssetmask, __NR_sgetmask, __NR_ssetmask.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sxetmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/symlink-P.c -->
# sources/test-tools/strace/tests/symlink-P.c

## Purpose
Variant wrapper for `symlink.c`. It defines `PATH_TRACING` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 42 bytes.

## Important APIs, Types, And Functions
includes/imports: "symlink.c"; defines/undefs: PATH_TRACING.

## Control Flow
Preprocessor-only flow: set `PATH_TRACING`, include `symlink.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `symlink.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/symlink-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/symlink.c -->
# sources/test-tools/strace/tests/symlink.c

## Purpose
Covers strace decoder coverage for `symlink`. Source read: 69 lines, 1787 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: symlink, __NR_symlink.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: symlink, __NR_symlink.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/symlinkat.c -->
# sources/test-tools/strace/tests/symlinkat.c

## Purpose
Covers strace decoder coverage for `symlinkat`. Source comments/macros state: Check decoding of symlinkat syscall. Source read: 29 lines, 619 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: symlinkat, __NR_symlinkat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: symlinkat, __NR_symlinkat.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/symlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sync.c -->
# sources/test-tools/strace/tests/sync.c

## Purpose
Covers strace decoder coverage for `sync`. Source comments/macros state: Check decoding of sync syscall. Source read: 23 lines, 356 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: sync, __NR_sync.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: sync, __NR_sync.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sync_file_range.c -->
# sources/test-tools/strace/tests/sync_file_range.c

## Purpose
Covers strace decoder coverage for `sync_file_range`. Source comments/macros state: Check decoding of sync_file_range syscall. Source read: 44 lines, 988 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, "scno.h", <stdio.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: sync_file_range.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: sync_file_range.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sync_file_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sync_file_range2.c -->
# sources/test-tools/strace/tests/sync_file_range2.c

## Purpose
Covers strace decoder coverage for `sync_file_range2`. Source comments/macros state: Check decoding of sync_file_range2 syscall. Source read: 44 lines, 987 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, "scno.h", <stdio.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: sync_file_range2.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: sync_file_range2.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sync_file_range2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syntax.sh -->
# sources/test-tools/strace/tests/syntax.sh

## Purpose
Covers the `syntax.sh` shell harness test. Source comments/macros state: # Define syntax testing primitives. # Copyright (c) 2016 Dmitry V. Levin <ldv@strace.io> Copyright (c) 2016-2024 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 89 lines, 1753 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none; shell functions: log_sfx, check_zero, check_exit_status_and_stderr, check_exit_status_and_stderr_using_grep, check_e, check_e_using_grep, check_h; harness commands: check_zero(), $STRACE "$@" 2> "$LOG.$sfx" > /dev/null || {, check_exit_status_and_stderr(), $STRACE "$@" 2> "$LOG.$sfx" && {, match_diff "$LOG.$sfx" "$EXP.$sfx" \, check_exit_status_and_stderr_using_grep(), match_grep "$LOG.$sfx" "$EXP.$sfx" \, check_e(), $STRACE_EXE: $pattern, check_exit_status_and_stderr "$sfx" "$@".

## Control Flow
Shell flow runs top to bottom through harness initialization, feature checks, strace invocation, and result matching. The script contains 2 loop(s), 0 case block(s), and exits through harness skip/fail helpers when prerequisites are absent.

## State And Persistence Behavior
Shell state is process-local variables, temporary files, generated expected-output logs, and harness-controlled exit status.

## Dependencies And Integration Points
Depends on `init.sh`, built `strace` binary and shell harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: harness performs exact diff comparison; harness performs regex/grep matching.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syntax.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syscall-success.sh -->
# sources/test-tools/strace/tests/syscall-success.sh

## Purpose
Covers the `syscall-success.sh` shell harness test. Source comments/macros state: # Check decoding of a syscall using syscall injection. # Accepts a list of retvals to inject as the first INJECT_RETVALS= argument Accepts a syscall to inject retvals to as the first INJECT_SYSCALL= argument # Copyright (c) 2018-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later We avoid messing with arguments by accepting arguments we understand only at the beginning of. Source read: 46 lines, 1126 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none; harness commands: check_prog sed, run_strace -e "inject=${INJECT_SYSCALL}:retval=${i}" "$@" \, match_diff "$LOG.$i" "$EXP.$i".

## Control Flow
Shell flow runs top to bottom through harness initialization, feature checks, strace invocation, and result matching. The script contains 2 loop(s), 2 case block(s), and exits through harness skip/fail helpers when prerequisites are absent.

## State And Persistence Behavior
Shell state is process-local variables, temporary files, generated expected-output logs, and harness-controlled exit status.

## Dependencies And Integration Points
Depends on built `strace` binary and shell harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: unsupported environments skip rather than fail; harness performs exact diff comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syscall-success.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sysctl.c -->
# sources/test-tools/strace/tests/sysctl.c

## Purpose
Covers strace decoder coverage for `sysctl`. Source comments/macros state: Check decoding of sysctl syscall. Source read: 63 lines, 1362 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>, <linux/sysctl.h>; defines/undefs: none; C functions: k_sysctl, main; syscall numbers/wrappers: _sysctl, __NR__sysctl; struct types: __sysctl_args.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: _sysctl, __NR__sysctl.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sysinfo.c -->
# sources/test-tools/strace/tests/sysinfo.c

## Purpose
Covers strace decoder coverage for `sysinfo`. Source comments/macros state: This file is part of sysinfo strace test. Source read: 57 lines, 1356 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/sysinfo.h>; defines/undefs: none; C functions: main; struct types: sysinfo.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sysinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syslog-success.c -->
# sources/test-tools/strace/tests/syslog-success.c

## Purpose
Variant wrapper for `syslog.c`. It defines `RETVAL_INJECTED` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "syslog.c"; defines/undefs: RETVAL_INJECTED.

## Control Flow
Preprocessor-only flow: set `RETVAL_INJECTED`, include `syslog.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `syslog.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syslog-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syslog.c -->
# sources/test-tools/strace/tests/syslog.c

## Purpose
Covers strace decoder coverage for `syslog`. Source comments/macros state: Check decoding of syslog syscall. SYSLOG_ACTION_CLOSE SYSLOG_ACTION_OPEN Avoid commands with side effects without syscall injection SYSLOG_ACTION_CLEAR SYSLOG_ACTION_CONSOLE_OFF SYSLOG_ACTION_CONSOLE_ON SYSLOG_ACTION_SIZE_UNREAD SYSLOG_ACTION_SIZE_BUFFER SYSLOG_ACTION_??? SYSLOG_ACTION_??? Avoid commands with side effects without syscall injection SYSLOG_ACTION_READ SYSLOG_ACTION_READ_ALL SYSLOG_ACTION_READ_CLEAR. Source read: 143 lines, 3941 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: RET_SFX; C functions: valid_cmd, printstr, main; syscall numbers/wrappers: syslog, __NR_syslog; struct types: strval32.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: syslog, __NR_syslog.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tail_alloc.c -->
# sources/test-tools/strace/tests/tail_alloc.c

## Purpose
Covers strace decoder coverage for `tail_alloc`. Source read: 43 lines, 1029 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <string.h>, <sys/mman.h>; defines/undefs: none.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tail_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tampering-notes.c -->
# sources/test-tools/strace/tests/tampering-notes.c

## Purpose
Covers strace decoder coverage for `tampering-notes`. Source comments/macros state: Check tampering notes. Check the return value to pacify the compiler. Source read: 67 lines, 1359 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <limits.h>, <stdio.h>, <stdlib.h>, <string.h>, <unistd.h>; defines/undefs: PATH_LEN; C functions: main; syscall numbers/wrappers: getcwd, __NR_getcwd.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: getcwd, __NR_getcwd.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tampering-notes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tcp_ao.c -->
# sources/test-tools/strace/tests/tcp_ao.c

## Purpose
Covers strace decoder coverage for `tcp_ao`. Source comments/macros state: Check decoding of TCP_AO_ADD_KEY socket option. Source read: 116 lines, 3409 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <linux/tcp.h>, <netinet/in.h>, <stddef.h>, <stdio.h>, <string.h>, <sys/socket.h>, <unistd.h>; defines/undefs: KEY1, KEY2; C functions: add_key, main; struct types: tcp_ao_add, sockaddr_in6, sockaddr_in.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; creates transient socket state for local decoding.

## Dependencies And Integration Points
Depends on `tests.h`, Linux UAPI headers. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tcp_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tee.c -->
# sources/test-tools/strace/tests/tee.c

## Purpose
Covers strace decoder coverage for `tee`. Source comments/macros state: Check decoding of tee syscall. Source read: 33 lines, 799 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: tee, __NR_tee.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: tee, __NR_tee.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_fs_xflags.h -->
# sources/test-tools/strace/tests/test_fs_xflags.h

## Purpose
Covers shared strace test helper definitions for `test_fs_xflags`. Source read: 30 lines, 750 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: VALID_FS_XFLAGS, INVALID_FS_XFLAGS, INVALID_FS_XFLAGS64, VALID_FS_XFLAGS_STR, INVALID_FS_XFLAGS_STR.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_fs_xflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_netlink.h -->
# sources/test-tools/strace/tests/test_netlink.h

## Purpose
Covers shared strace test helper definitions for `test_netlink`. Source comments/macros state: len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) Source read: 104 lines, 3169 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "print_fields.h", <stdio.h>, <stdint.h>, <string.h>, <sys/socket.h>, "netlink.h"; defines/undefs: TEST_NETLINK_, TEST_NETLINK, TEST_NETLINK_OBJECT_EX_, TEST_NETLINK_OBJECT_EX, TEST_NETLINK_OBJECT; struct types: nlmsghdr.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_nlattr.h -->
# sources/test-tools/strace/tests/test_nlattr.h

## Purpose
Covers shared strace test helper definitions for `test_nlattr`. Source comments/macros state: len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) len < sizeof((obj_)[0]) sizeof((obj_)[0]) < len < sizeof(obj_) short read of sizeof(obj_) %p sizeof(obj_) len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) len < sizeof((obj_)[0]) sizeof((obj_)[0]) < len < sizeof(obj_) short read of sizeof(obj_) %p sizeof(obj_) Checks for specific typical decoders %.*f s %.*f s Source read: 526 lines, 17238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "print_fields.h", <inttypes.h>, <stdio.h>, <stdint.h>, <string.h>, <sys/socket.h>, <unistd.h>, "netlink.h", <linux/rtnetlink.h>; defines/undefs: PRINT_SOCK, TEST_NLATTR_EX_, TEST_NLATTR_, TEST_NLATTR, TEST_NLATTR_OBJECT_EX_, TEST_NLATTR_OBJECT_EX, TEST_NLATTR_OBJECT, TEST_NLATTR_OBJECT_, TEST_NLATTR_OBJECT_MINSZ, TEST_NLATTR_ARRAY_, TEST_NLATTR_ARRAY, TEST_NESTED_NLATTR_, TEST_NESTED_NLATTR_OBJECT_EX_MINSZ_, TEST_NESTED_NLATTR_OBJECT_EX_, TEST_NESTED_NLATTR_OBJECT_EX, TEST_NESTED_NLATTR_OBJECT, TEST_NESTED_NLATTR_ARRAY_EX_, TEST_NESTED_NLATTR_ARRAY_EX, TEST_NESTED_NLATTR_ARRAY, DEF_NLATTR_INTEGER_CHECK_, TEST_NLATTR_VAL; C functions: init_nlattr, print_nlattr, print_sockfd, check_clock_t_nlattr; struct types: nlattr, nlmsghdr; harness commands: check_##nla_data_name_##_nlattr(int fd, void *nlh0, size_t hdrlen, \, check_##type_##_nlattr((fd_), (nlh0_), (hdrlen_), \, check_clock_t_nlattr(int fd, void *nlh0, size_t hdrlen,.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on `tests.h`, Linux UAPI headers. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_nlattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_printpath.c -->
# sources/test-tools/strace/tests/test_printpath.c

## Purpose
Covers strace decoder coverage for `test_printpath`. Source comments/macros state: Test printpath/umovestr. / /. /.. /../ /../. /../.. /../../ /../..| /../.|. /../|.. /..|/.. /.|./.. /|../.. |/../.. Source read: 89 lines, 1761 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <limits.h>, <stdio.h>, <string.h>, <unistd.h>, "test_ucopy.h"; defines/undefs: none; C functions: test_printpath_at, test_efault, test_enametoolong, test_printpath.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `test_ucopy.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_printpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_printstrn.c -->
# sources/test-tools/strace/tests/test_printstrn.c

## Purpose
Covers strace decoder coverage for `test_printstrn`. Source comments/macros state: Test printstrn/umoven. abcdefgh| abcdefg|h abcdef|gh abcde|fgh abcd|efgh abc|defgh ab|cdefgh a|bcdefgh |abcdefgh Test corner cases when octal quoting goes before digit Source read: 93 lines, 2216 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <string.h>, <unistd.h>, "scno.h", "test_ucopy.h"; defines/undefs: none; C functions: add_key, test_printstrn_at, test_efault, test_print_memory, test_printstrn; syscall numbers/wrappers: add_key, __NR_add_key.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: add_key, __NR_add_key.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `test_ucopy.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_printstrn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.c -->
# sources/test-tools/strace/tests/test_ucopy.c

## Purpose
Covers strace decoder coverage for `test_ucopy`. Source comments/macros state: Test whether process_vm_readv and PTRACE_PEEKDATA work. !HAVE_PROCESS_VM_READV Source read: 142 lines, 2716 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <errno.h>, <sys/ptrace.h>, <signal.h>, <stdlib.h>, <unistd.h>, <sys/uio.h>, <sys/wait.h>, "test_ucopy.h", "scno.h"; defines/undefs: process_vm_readv; C functions: call_process_vm_readv, call_ptrace_peekdata, test_ucopy, test_process_vm_readv, test_ptrace_peekdata; syscall numbers/wrappers: process_vm_readv, __NR_process_vm_readv; struct types: iovec.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: process_vm_readv, __NR_process_vm_readv.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `test_ucopy.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.h -->
# sources/test-tools/strace/tests/test_ucopy.h

## Purpose
Covers shared strace test helper definitions for `test_ucopy`. Source read: 20 lines, 348 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdbool.h>; defines/undefs: none.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_ucopy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tests.h -->
# sources/test-tools/strace/tests/tests.h

## Purpose
Covers shared strace test helper definitions for `tests`. Source comments/macros state: Tests of "strace -v" are expected to define VERBOSE to 1. xlat verbosity defaults " str_ " " dflt_ " " str_ " " dflt_ " %s %s %s %s %s %s !XLAT_RAW && !XLAT_VERBOSE " dflt_ " " dflt_ " XLAT_RAW, XLAT_VERBOSE Default maximum # of bytes printed in printstr et al. Cached sysconf(_SC_PAGESIZE). The size of kernel's sigset_t. Print message and strerror(errno) to stderr, then exit(1). Print message to stderr, then. Source read: 522 lines, 16179 bytes.

## Important APIs, Types, And Functions
includes/imports: "config.h", <stdbool.h>, <stdint.h>, <sys/types.h>, "kernel_types.h", "kernel_old_timespec.h", "gcc_compat.h", "macros.h"; defines/undefs: STRACE_TESTS_H, SIZEOF_KERNEL_LONG_T, SIZEOF_LONG, VERBOSE, XLAT_RAW, XLAT_VERBOSE, XLAT_name, XLAT_KNOWN, XLAT_UNKNOWN, XLAT_KNOWN_FMT, XLAT_UNKNOWN_FMT, XLAT_FMT, XLAT_FMT_D, XLAT_FMT_JD, XLAT_FMT_U, XLAT_FMT_L, XLAT_FMT_LL, XLAT_ARGS, XLAT_ARGS_U, XLAT_SEL, ABBR, RAW, VERB, NABBR, NRAW, NVERB, XLAT_STR, ARG_XLAT_KNOWN; C functions: get_page_size, get_sigset_size, perror_msg_and_fail, error_msg_and_fail, error_msg_and_skip, perror_msg_and_skip, skip_if_unavailable, get_dir_fd, create_and_enter_subdir, leave_and_remove_subdir, lock_file_by_dirname, fill_memory_ex, fill_memory, fill_memory16_ex, fill_memory16, fill_memory32_ex, fill_memory32, fill_memory64_ex, fill_memory64, tprintf, inode_of_sockfd, print_quoted_string_ex, print_quoted_string, print_quoted_cstring, print_quoted_stringn, print_quoted_memory_ex, print_quoted_memory, print_quoted_hex, print_time_t_nsec, print_time_t_usec; syscall numbers/wrappers: socketcall; struct types: strval8, strval16, strval32, strival32, strval_klong, strval64, xlat, mmsghdr; harness commands: void check_overflowuid(const int);, void check_overflowgid(const int);.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: socketcall.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail; harness performs regex/grep matching; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tgkill--pidns-translation.c -->
# sources/test-tools/strace/tests/tgkill--pidns-translation.c

## Purpose
Variant wrapper for `tgkill.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "tgkill.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `tgkill.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `tgkill.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tgkill--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tgkill.c -->
# sources/test-tools/strace/tests/tgkill.c

## Purpose
Covers strace decoder coverage for `tgkill`. Source comments/macros state: Check decoding of tgkill syscall. Source read: 80 lines, 1971 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <signal.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: k_tgkill, main; syscall numbers/wrappers: tgkill, gettid, __NR_tgkill, __NR_gettid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: tgkill, gettid, __NR_tgkill, __NR_gettid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tgkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve--quiet-thread-execve.c -->
# sources/test-tools/strace/tests/threads-execve--quiet-thread-execve.c

## Purpose
Variant wrapper for `threads-execve.c`. It defines `PRINT_SUPERSEDED` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 55 bytes.

## Important APIs, Types, And Functions
includes/imports: "threads-execve.c"; defines/undefs: PRINT_SUPERSEDED.

## Control Flow
Preprocessor-only flow: set `PRINT_SUPERSEDED`, include `threads-execve.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `threads-execve.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve--quiet-thread-execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-q.c -->
# sources/test-tools/strace/tests/threads-execve-q.c

## Purpose
Variant wrapper for `threads-execve.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 28 bytes.

## Important APIs, Types, And Functions
includes/imports: "threads-execve.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `threads-execve.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `threads-execve.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-qq.c -->
# sources/test-tools/strace/tests/threads-execve-qq.c

## Purpose
Variant wrapper for `threads-execve.c`. It defines `PRINT_EXITED` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 51 bytes.

## Important APIs, Types, And Functions
includes/imports: "threads-execve.c"; defines/undefs: PRINT_EXITED.

## Control Flow
Preprocessor-only flow: set `PRINT_EXITED`, include `threads-execve.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `threads-execve.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-qq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-qqq.c -->
# sources/test-tools/strace/tests/threads-execve-qqq.c

## Purpose
Variant wrapper for `threads-execve.c`. It defines `PRINT_SUPERSEDED, PRINT_EXITED` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 78 bytes.

## Important APIs, Types, And Functions
includes/imports: "threads-execve.c"; defines/undefs: PRINT_SUPERSEDED, PRINT_EXITED.

## Control Flow
Preprocessor-only flow: set `PRINT_SUPERSEDED, PRINT_EXITED`, include `threads-execve.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `threads-execve.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve-qqq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve.c -->
# sources/test-tools/strace/tests/threads-execve.c

## Purpose
Covers threaded execve tracing and quietness modes. Source comments/macros state: Check decoding of threads when a non-leader thread invokes execve. %u vars %u vars %u vars %u vars Source read: 245 lines, 5742 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <signal.h>, <stdio.h>, <stdlib.h>, <time.h>, <unistd.h>, "kernel_old_timespec.h"; defines/undefs: PRINT_EXITED, PRINT_SUPERSEDED; C functions: handler, k_sigsuspend, k_gettid, get_sigsetsize, arglen, main; syscall numbers/wrappers: nanosleep, rt_sigsuspend, gettid, clock_nanosleep, exit, __NR_rt_sigsuspend, __NR_gettid, __NR_clock_nanosleep, __NR_nanosleep, __NR_exit; struct types: sigaction.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: nanosleep, rt_sigsuspend, gettid, clock_nanosleep, exit, __NR_rt_sigsuspend, __NR_gettid, __NR_clock_nanosleep, __NR_nanosleep, __NR_exit.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/time.c -->
# sources/test-tools/strace/tests/time.c

## Purpose
Covers strace decoder coverage for `time`. Source comments/macros state: This file is part of time strace test. Source read: 75 lines, 1558 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: time, __NR_time.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: time, __NR_time.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/time_enjoyment.h -->
# sources/test-tools/strace/tests/time_enjoyment.h

## Purpose
Covers shared strace test helper definitions for `time_enjoyment`. Source comments/macros state: Enjoying my user time Enjoying my system time We are fine even if the calls fail. Working around "ignoring return value of 'read' declared with attribute 'warn_unused_result'". !STRACE_TESTS_TIME_ENJOYMENT_H Source read: 70 lines, 1525 bytes.

## Important APIs, Types, And Functions
includes/imports: <fcntl.h>, <sched.h>, <time.h>, <sys/types.h>, <sys/stat.h>; defines/undefs: STRACE_TESTS_TIME_ENJOYMENT_H; C functions: nsecs, enjoy_time; struct types: timespec.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/time_enjoyment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/timer_create.c -->
# sources/test-tools/strace/tests/timer_create.c

## Purpose
Covers strace decoder coverage for `timer_create`. Source comments/macros state: Check decoding of timer_create syscall. SIGEV_??? Source read: 99 lines, 3268 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <signal.h>, <time.h>, <unistd.h>, "sigevent.h"; defines/undefs: SIGEV_THREAD_ID; C functions: main; syscall numbers/wrappers: timer_create, __NR_timer_create.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: timer_create, __NR_timer_create.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/timer_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/timer_xettime.c -->
# sources/test-tools/strace/tests/timer_xettime.c

## Purpose
Covers strace decoder coverage for `timer_xettime`. Source comments/macros state: This file is part of timer_xettime strace test. Source read: 104 lines, 3463 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <signal.h>, <time.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: timer_gettime, timer_settime, timer_create, __NR_timer_settime, __NR_timer_create, __NR_timer_gettime; struct types: sigevent, itimerspec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: timer_gettime, timer_settime, timer_create, __NR_timer_settime, __NR_timer_create, __NR_timer_gettime.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/timer_xettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/timerfd_xettime.c -->
# sources/test-tools/strace/tests/timerfd_xettime.c

## Purpose
Covers strace decoder coverage for `timerfd_xettime`. Source comments/macros state: Check decoding of timerfd_create, timerfd_gettime, and timerfd_settime syscalls. Source read: 95 lines, 3255 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <time.h>, <unistd.h>, "kernel_fcntl.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: timerfd_gettime, timerfd_settime, timerfd_create, __NR_timerfd_create, __NR_timerfd_settime, __NR_timerfd_gettime; struct types: itimerspec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: timerfd_gettime, timerfd_settime, timerfd_create, __NR_timerfd_create, __NR_timerfd_settime, __NR_timerfd_gettime.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/timerfd_xettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xabbrev.c -->
# sources/test-tools/strace/tests/times-Xabbrev.c

## Purpose
Variant wrapper for `times.c`. It defines `XLAT_ABBREV` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "times.c"; defines/undefs: XLAT_ABBREV.

## Control Flow
Preprocessor-only flow: set `XLAT_ABBREV`, include `times.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `times.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xraw.c -->
# sources/test-tools/strace/tests/times-Xraw.c

## Purpose
Variant wrapper for `times.c`. It defines `XLAT_RAW` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 38 bytes.

## Important APIs, Types, And Functions
includes/imports: "times.c"; defines/undefs: XLAT_RAW.

## Control Flow
Preprocessor-only flow: set `XLAT_RAW`, include `times.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `times.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xverbose.c -->
# sources/test-tools/strace/tests/times-Xverbose.c

## Purpose
Variant wrapper for `times.c`. It defines `XLAT_VERBOSE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 42 bytes.

## Important APIs, Types, And Functions
includes/imports: "times.c"; defines/undefs: XLAT_VERBOSE.

## Control Flow
Preprocessor-only flow: set `XLAT_VERBOSE`, include `times.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `times.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-fail.c -->
# sources/test-tools/strace/tests/times-fail.c

## Purpose
Covers strace decoder coverage for `times-fail`. Source read: 22 lines, 368 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <unistd.h>, "scno.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: times, __NR_times.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: times, __NR_times.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times.c -->
# sources/test-tools/strace/tests/times.c

## Purpose
Covers strace decoder coverage for `times`. Source comments/macros state: Check decoding of times syscall. @file This test burns some CPU cycles in user space and kernel space in order to get some non-zero values returned by times(2). On systems where user's and kernel's long types are the same, prefer direct times syscall over libc's times function because the latter is more prone to return value truncation. %.*f s %.*f s %.*f s %.*f s Source read: 128 lines, 3180 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <sched.h>, <stdio.h>, <time.h>, <unistd.h>, "scno.h", <sys/stat.h>, <sys/times.h>, <sys/types.h>, <sys/wait.h>, "time_enjoyment.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: times, __NR_times; struct types: tms.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: times, __NR_times.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `time_enjoyment.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tkill--pidns-translation.c -->
# sources/test-tools/strace/tests/tkill--pidns-translation.c

## Purpose
Variant wrapper for `tkill.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 45 bytes.

## Important APIs, Types, And Functions
includes/imports: "tkill.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `tkill.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `tkill.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tkill--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tkill.c -->
# sources/test-tools/strace/tests/tkill.c

## Purpose
Covers strace decoder coverage for `tkill`. Source comments/macros state: Check decoding of tkill syscall. Source read: 69 lines, 1512 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <signal.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: k_tkill, main; syscall numbers/wrappers: tkill, gettid, __NR_tkill, __NR_gettid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: tkill, gettid, __NR_tkill, __NR_gettid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tprintf.c -->
# sources/test-tools/strace/tests/tprintf.c

## Purpose
Covers strace decoder coverage for `tprintf`. Source comments/macros state: Close stdin, move stdout to a non-standard descriptor, and print. Source read: 70 lines, 1192 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <errno.h>, <stdarg.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: write_loop, tprintf.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_clock.in -->
# sources/test-tools/strace/tests/trace_clock.in

## Purpose
Covers trace-expression parser input coverage. Source read: 7 lines, 121 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 7 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_clock.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_creds.in -->
# sources/test-tools/strace/tests/trace_creds.in

## Purpose
Covers trace-expression parser input coverage. Source read: 8 lines, 136 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 8 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_creds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_fstat.in -->
# sources/test-tools/strace/tests/trace_fstat.in

## Purpose
Covers trace-expression parser input coverage. Source read: 12 lines, 246 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 12 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_fstat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_fstatfs.in -->
# sources/test-tools/strace/tests/trace_fstatfs.in

## Purpose
Covers trace-expression parser input coverage. Source read: 2 lines, 28 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 2 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_fstatfs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_lstat.in -->
# sources/test-tools/strace/tests/trace_lstat.in

## Purpose
Covers trace-expression parser input coverage. Source read: 3 lines, 38 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 3 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_lstat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_32.in -->
# sources/test-tools/strace/tests/trace_personality_32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_64.in -->
# sources/test-tools/strace/tests/trace_personality_64.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_64.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_32.in -->
# sources/test-tools/strace/tests/trace_personality_number_32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_64.in -->
# sources/test-tools/strace/tests/trace_personality_number_64.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_64.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_x32.in -->
# sources/test-tools/strace/tests/trace_personality_number_x32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_number_x32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_32.in -->
# sources/test-tools/strace/tests/trace_personality_regex_32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 5 lines, 96 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 5 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_64.in -->
# sources/test-tools/strace/tests/trace_personality_regex_64.in

## Purpose
Covers trace-expression parser input coverage. Source read: 5 lines, 96 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 5 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_64.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_x32.in -->
# sources/test-tools/strace/tests/trace_personality_regex_x32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 5 lines, 96 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 5 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_regex_x32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_32.in -->
# sources/test-tools/strace/tests/trace_personality_statfs_32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 2 lines, 26 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 2 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_64.in -->
# sources/test-tools/strace/tests/trace_personality_statfs_64.in

## Purpose
Covers trace-expression parser input coverage. Source read: 2 lines, 26 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 2 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_64.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_x32.in -->
# sources/test-tools/strace/tests/trace_personality_statfs_x32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 2 lines, 26 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 2 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_statfs_x32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_x32.in -->
# sources/test-tools/strace/tests/trace_personality_x32.in

## Purpose
Covers trace-expression parser input coverage. Source read: 1 lines, 12 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 1 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_personality_x32.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_question.in -->
# sources/test-tools/strace/tests/trace_question.in

## Purpose
Covers trace-expression parser input coverage. Source read: 4 lines, 66 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 4 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_question.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_stat.in -->
# sources/test-tools/strace/tests/trace_stat.in

## Purpose
Covers trace-expression parser input coverage. Source read: 3 lines, 35 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 3 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_stat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_stat_like.in -->
# sources/test-tools/strace/tests/trace_stat_like.in

## Purpose
Covers trace-expression parser input coverage. Source read: 18 lines, 319 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 18 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_stat_like.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_statfs.in -->
# sources/test-tools/strace/tests/trace_statfs.in

## Purpose
Covers trace-expression parser input coverage. Source read: 2 lines, 26 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 2 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_statfs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trace_statfs_like.in -->
# sources/test-tools/strace/tests/trace_statfs_like.in

## Purpose
Covers trace-expression parser input coverage. Source read: 5 lines, 65 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines/undefs: none.

## Control Flow
Declarative input with 5 active row(s). The generated tests consume each row as a trace expression or regex fragment rather than executing control flow inside this file.

## State And Persistence Behavior
The file is checked-in declarative state. Runtime persistence is limited to generated tests or parser results outside this input file.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: parser/generator coverage comes from consuming each input row.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trace_statfs_like.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tracer_ppid_pgid_sid.c -->
# sources/test-tools/strace/tests/tracer_ppid_pgid_sid.c

## Purpose
Covers strace decoder coverage for `tracer_ppid_pgid_sid`. Source comments/macros state: Helper program for strace-DDD.test Source read: 90 lines, 1829 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "xmalloc.h", <ctype.h>, <stdio.h>, <stdlib.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: fetch_tracer_pid, get_tracer_pid, get_ppid_pgid_sid, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `xmalloc.h`, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tracer_ppid_pgid_sid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trie_for_tests.c -->
# sources/test-tools/strace/tests/trie_for_tests.c

## Purpose
Variant wrapper for `trie.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 18 bytes.

## Important APIs, Types, And Functions
includes/imports: "trie.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `trie.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `trie.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trie_for_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/trie_test.c -->
# sources/test-tools/strace/tests/trie_test.c

## Purpose
Covers strace decoder coverage for `trie_test`. Source read: 121 lines, 2991 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "trie.h", <stdio.h>, <inttypes.h>; defines/undefs: none; C functions: assert_equals, iterate_fn, test_trie_iterate_fn, test_trie_get, main; struct types: trie, key_value_pair.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/trie_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/truncate.c -->
# sources/test-tools/strace/tests/truncate.c

## Purpose
Covers strace decoder coverage for `truncate`. Source read: 41 lines, 797 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: truncate, __NR_truncate.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: truncate, __NR_truncate.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/truncate64.c -->
# sources/test-tools/strace/tests/truncate64.c

## Purpose
Covers strace decoder coverage for `truncate64`. Source read: 36 lines, 691 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: truncate64.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: truncate64.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/truncate64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ugetrlimit.c -->
# sources/test-tools/strace/tests/ugetrlimit.c

## Purpose
Covers strace decoder coverage for `ugetrlimit`. Source read: 21 lines, 346 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetrlimit.c"; defines/undefs: NR_GETRLIMIT, STR_GETRLIMIT; syscall numbers/wrappers: ugetrlimit.

## Control Flow
primary syscall coverage: ugetrlimit.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ugetrlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/uio.c -->
# sources/test-tools/strace/tests/uio.c

## Purpose
Covers strace decoder coverage for `uio`. Source read: 43 lines, 874 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <unistd.h>, <sys/uio.h>, <assert.h>; defines/undefs: none; C functions: main; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/uio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umask.c -->
# sources/test-tools/strace/tests/umask.c

## Purpose
Covers strace decoder coverage for `umask`. Source read: 31 lines, 513 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdio.h>, <sys/stat.h>; defines/undefs: none; C functions: test_umask, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umode_t.c -->
# sources/test-tools/strace/tests/umode_t.c

## Purpose
Covers strace decoder coverage for `umode_t`. Source comments/macros state: Check decoding of umode_t type syscall arguments. Source read: 59 lines, 1350 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdio.h>, <unistd.h>, <sys/stat.h>; defines/undefs: TEST_SYSCALL_PREFIX_ARGS, TEST_SYSCALL_PREFIX_STR; C functions: test_syscall, main; syscall numbers/wrappers: TEST_SYSCALL_NR.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: TEST_SYSCALL_NR.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umode_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umount.c -->
# sources/test-tools/strace/tests/umount.c

## Purpose
Covers strace decoder coverage for `umount`. Source read: 47 lines, 933 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/stat.h>, <sys/mount.h>, "scno.h", <unistd.h>; defines/undefs: TEST_SYSCALL_STR, __NR_oldumount; C functions: main; syscall numbers/wrappers: oldumount, umount, umount2, __NR_oldumount.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: oldumount, umount, umount2, __NR_oldumount.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umount2.c -->
# sources/test-tools/strace/tests/umount2.c

## Purpose
Covers strace decoder coverage for `umount2`. Source read: 36 lines, 933 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, <sys/stat.h>, <sys/mount.h>, "scno.h"; defines/undefs: TEST_SYSCALL_NR, TEST_SYSCALL_STR; C functions: main; syscall numbers/wrappers: umount2, umount, TEST_SYSCALL_NR.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: umount2, umount, TEST_SYSCALL_NR.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umount2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umoven-illptr.c -->
# sources/test-tools/strace/tests/umoven-illptr.c

## Purpose
Covers strace decoder coverage for `umoven-illptr`. Source comments/macros state: Check decoding of invalid pointer by umoven. Source read: 57 lines, 1181 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_old_timespec.h"; defines/undefs: none; C functions: k_nanosleep, main; syscall numbers/wrappers: nanosleep, __NR_nanosleep.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: nanosleep, __NR_nanosleep.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umoven-illptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr-illptr.c -->
# sources/test-tools/strace/tests/umovestr-illptr.c

## Purpose
Covers strace decoder coverage for `umovestr-illptr`. Source comments/macros state: Check decoding of invalid pointer by umovestr. Source read: 34 lines, 738 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, "scno.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: chdir, __NR_chdir.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: chdir, __NR_chdir.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr-illptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr.c -->
# sources/test-tools/strace/tests/umovestr.c

## Purpose
Covers strace decoder coverage for `umovestr`. Source read: 22 lines, 407 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <string.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr2.c -->
# sources/test-tools/strace/tests/umovestr2.c

## Purpose
Covers strace decoder coverage for `umovestr2`. Source read: 33 lines, 657 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <string.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr3.c -->
# sources/test-tools/strace/tests/umovestr3.c

## Purpose
Covers strace decoder coverage for `umovestr3`. Source read: 28 lines, 545 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <limits.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr_cached.c -->
# sources/test-tools/strace/tests/umovestr_cached.c

## Purpose
Covers strace decoder coverage for `umovestr_cached`. Source comments/macros state: Check effectiveness of umovestr memory caching. Source read: 47 lines, 1046 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <string.h>, <unistd.h>, <sys/uio.h>; defines/undefs: none; C functions: main; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr_cached.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr_cached_adjacent.c -->
# sources/test-tools/strace/tests/umovestr_cached_adjacent.c

## Purpose
Covers strace decoder coverage for `umovestr_cached_adjacent`. Source comments/macros state: Check effectiveness of umovestr memory caching. Source read: 48 lines, 1097 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <string.h>, <unistd.h>, <sys/uio.h>; defines/undefs: none; C functions: main; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umovestr_cached_adjacent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/uname.c -->
# sources/test-tools/strace/tests/uname.c

## Purpose
Covers strace decoder coverage for `uname`. Source comments/macros state: Check decoding of uname syscall. Source read: 44 lines, 966 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/utsname.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: uname, __NR_uname; struct types: utsname.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: uname, __NR_uname.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/uname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unblock_reset_raise.c -->
# sources/test-tools/strace/tests/unblock_reset_raise.c

## Purpose
Covers strace decoder coverage for `unblock_reset_raise`. Source comments/macros state: Unblock, reset, and raise a signal. Source read: 34 lines, 746 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <stdlib.h>, <unistd.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unblock_reset_raise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-send-recv.c -->
# sources/test-tools/strace/tests/unix-pair-send-recv.c

## Purpose
Covers strace decoder coverage for `unix-pair-send-recv`. Source read: 89 lines, 1871 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <errno.h>, <string.h>, <unistd.h>, <sys/socket.h>, "scno.h"; defines/undefs: __NR_send, SC_send, __NR_recv, SC_recv; C functions: sys_send, sys_recv, transpose, main; syscall numbers/wrappers: send, recv.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: send, recv.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; creates transient socket state for local decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-send-recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c -->
# sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c

## Purpose
Covers strace decoder coverage for `unix-pair-sendto-recvfrom`. Source comments/macros state: Check decoding and dumping of sendto and recvfrom syscalls. Source read: 66 lines, 1432 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <string.h>, <unistd.h>, <sys/socket.h>, <sys/wait.h>; defines/undefs: none; C functions: transpose, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding.

## State And Persistence Behavior
creates transient socket state for local decoding; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unix-pair-sendto-recvfrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unlink.c -->
# sources/test-tools/strace/tests/unlink.c

## Purpose
Covers strace decoder coverage for `unlink`. Source read: 32 lines, 489 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: unlink, __NR_unlink.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: unlink, __NR_unlink.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unlinkat.c -->
# sources/test-tools/strace/tests/unlinkat.c

## Purpose
Covers strace decoder coverage for `unlinkat`. Source comments/macros state: Check decoding of unlinkat syscall. Source read: 35 lines, 814 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: unlinkat, __NR_unlinkat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: unlinkat, __NR_unlinkat.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unshare-report-ns-id.c -->
# sources/test-tools/strace/tests/unshare-report-ns-id.c

## Purpose
Variant wrapper for `unshare.c`. It defines `PRINT_NAMESPACE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 45 bytes.

## Important APIs, Types, And Functions
includes/imports: "unshare.c"; defines/undefs: PRINT_NAMESPACE.

## Control Flow
Preprocessor-only flow: set `PRINT_NAMESPACE`, include `unshare.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `unshare.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unshare-report-ns-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unshare.c -->
# sources/test-tools/strace/tests/unshare.c

## Purpose
Covers strace decoder coverage for `unshare`. Source comments/macros state: Check decoding of unshare syscall. CLONE_??? CLONE_??? Source read: 93 lines, 2430 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <limits.h>, <stdio.h>, <unistd.h>; defines/undefs: LINE_END; C functions: main; syscall numbers/wrappers: unshare, __NR_unshare.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: unshare, __NR_unshare.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/userfaultfd.c -->
# sources/test-tools/strace/tests/userfaultfd.c

## Purpose
Covers strace decoder coverage for `userfaultfd`. Source comments/macros state: Check decoding of userfaultfd syscall. Source read: 59 lines, 1476 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_fcntl.h"; defines/undefs: UFFD_USER_MODE_ONLY; C functions: k_userfaultfd, main; syscall numbers/wrappers: userfaultfd, __NR_userfaultfd; struct types: strval32.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: userfaultfd, __NR_userfaultfd.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/userfaultfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ustat.c -->
# sources/test-tools/strace/tests/ustat.c

## Purpose
Covers strace decoder coverage for `ustat`. Source comments/macros state: HAVE_USTAT_H Source read: 66 lines, 1505 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/stat.h>, <sys/sysmacros.h>, <unistd.h>, <ustat.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: ustat, __NR_ustat; struct types: ustat, stat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: ustat, __NR_ustat.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ustat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utime.c -->
# sources/test-tools/strace/tests/utime.c

## Purpose
Covers strace decoder coverage for `utime`. Source comments/macros state: Check decoding of utime syscall. Source read: 66 lines, 1599 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <time.h>, <utime.h>, <errno.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: k_utime, main; syscall numbers/wrappers: utime, __NR_utime; struct types: utimbuf, tm.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: utime, __NR_utime.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xabbrev.c -->
# sources/test-tools/strace/tests/utimensat-Xabbrev.c

## Purpose
Variant wrapper for `utimensat.c`. It defines `mode macros` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 1 lines, 23 bytes.

## Important APIs, Types, And Functions
includes/imports: "utimensat.c"; defines/undefs: none.

## Control Flow
Preprocessor-only flow: set `variant macro`, include `utimensat.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on shared implementation `utimensat.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xraw.c -->
# sources/test-tools/strace/tests/utimensat-Xraw.c

## Purpose
Variant wrapper for `utimensat.c`. It defines `XLAT_RAW` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 42 bytes.

## Important APIs, Types, And Functions
includes/imports: "utimensat.c"; defines/undefs: XLAT_RAW.

## Control Flow
Preprocessor-only flow: set `XLAT_RAW`, include `utimensat.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on shared implementation `utimensat.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xverbose.c -->
# sources/test-tools/strace/tests/utimensat-Xverbose.c

## Purpose
Variant wrapper for `utimensat.c`. It defines `XLAT_VERBOSE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "utimensat.c"; defines/undefs: XLAT_VERBOSE.

## Control Flow
Preprocessor-only flow: set `XLAT_VERBOSE`, include `utimensat.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on shared implementation `utimensat.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat.c -->
# sources/test-tools/strace/tests/utimensat.c

## Purpose
Covers strace decoder coverage for `utimensat`. Source comments/macros state: Check decoding of utimensat syscall. AT_FDCWD AT_SYMLINK_NOFOLLOW AT_REMOVEDIR AT_REMOVEDIR|AT_SYMLINK_FOLLOW AT_SYMLINK_NOFOLLOW|AT_REMOVEDIR|AT_SYMLINK_FOLLOW" \ "|AT_NO_AUTOMOUNT|AT_EMPTY_PATH|AT_RECURSIVE|0xffff60ff UTIME_NOW UTIME_OMIT dirfd pathname times flags Source read: 227 lines, 7026 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <stdint.h>, <stdio.h>, <sys/stat.h>, <sys/time.h>, <unistd.h>, "scno.h"; defines/undefs: big_tv_sec, huge_tv_sec, str_at_fdcwd, str_at_symlink_nofollow, str_at_removedir, str_flags1, str_flags2, str_utime_now_omit; C functions: print_ts, k_utimensat, main; syscall numbers/wrappers: utimensat, __NR_utimensat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: utimensat, __NR_utimensat.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimensat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimes.c -->
# sources/test-tools/strace/tests/utimes.c

## Purpose
Covers strace decoder coverage for `utimes`. Source comments/macros state: Check decoding of utimes syscall. Source read: 26 lines, 503 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", "xutimes.c"; defines/undefs: TEST_SYSCALL_NR, TEST_SYSCALL_STR, TEST_STRUCT; syscall numbers/wrappers: utimes.

## Control Flow
primary syscall coverage: utimes.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/vfork-f.c -->
# sources/test-tools/strace/tests/vfork-f.c

## Purpose
Covers strace decoder coverage for `vfork-f`. Source read: 89 lines, 1868 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <fcntl.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/wait.h>; defines/undefs: prefix, logit; C functions: logit_, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/vfork-f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/vhangup.c -->
# sources/test-tools/strace/tests/vhangup.c

## Purpose
Covers strace decoder coverage for `vhangup`. Source comments/macros state: Check decoding of vhangup syscall. On setsid() success, the new session has no controlling terminal, therefore a subsequent vhangup() has nothing to hangup. The system call, however, returns 0 iff the calling process has CAP_SYS_TTY_CONFIG capability. Source read: 35 lines, 691 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: vhangup, __NR_vhangup.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: vhangup, __NR_vhangup.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/vhangup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/vmsplice.c -->
# sources/test-tools/strace/tests/vmsplice.c

## Purpose
Covers strace decoder coverage for `vmsplice`. Source comments/macros state: Check decoding of vmsplice syscall. Source read: 80 lines, 1964 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <assert.h>, <stdio.h>, <unistd.h>, <sys/uio.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: vmsplice, __NR_vmsplice; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: vmsplice, __NR_vmsplice.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/vmsplice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/wait4-v.c -->
# sources/test-tools/strace/tests/wait4-v.c

## Purpose
Variant wrapper for `wait4.c`. It defines `VERBOSE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 85 bytes.

## Important APIs, Types, And Functions
includes/imports: "wait4.c"; defines/undefs: VERBOSE.

## Control Flow
Preprocessor-only flow: set `VERBOSE`, include `wait4.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `wait4.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/wait4-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/wait4.c -->
# sources/test-tools/strace/tests/wait4.c

## Purpose
Covers strace decoder coverage for `wait4`. Source comments/macros state: Check decoding of wait4 syscall. WCONTINUED && WIFCONTINUED __NR_wait4 Source read: 207 lines, 5371 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <assert.h>, <signal.h>, <stdio.h>, <unistd.h>, <sys/wait.h>, "kernel_rusage.h"; defines/undefs: none; C functions: sprint_rusage, k_wait4, do_wait4, main; syscall numbers/wrappers: wait4, __NR_wait4.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: wait4, __NR_wait4.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/wait4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-Y.c -->
# sources/test-tools/strace/tests/waitid-Y.c

## Purpose
Variant wrapper for `waitid.c`. It defines `MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 123 bytes.

## Important APIs, Types, And Functions
includes/imports: "waitid.c"; defines/undefs: MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor-only flow: set `MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE`, include `waitid.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on procfs, shared implementation `waitid.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile; kernel configuration, procfs visibility, or privileges can change availability. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-Y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-v.c -->
# sources/test-tools/strace/tests/waitid-v.c

## Purpose
Variant wrapper for `waitid.c`. It defines `VERBOSE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 87 bytes.

## Important APIs, Types, And Functions
includes/imports: "waitid.c"; defines/undefs: VERBOSE.

## Control Flow
Preprocessor-only flow: set `VERBOSE`, include `waitid.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `waitid.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid.c -->
# sources/test-tools/strace/tests/waitid.c

## Purpose
Covers strace decoder coverage for `waitid`. Source comments/macros state: Check decoding of waitid syscall. WCONTINUED Source read: 274 lines, 6552 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <signal.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/wait.h>, "kernel_rusage.h", "scno.h"; defines/undefs: MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE, CASE; C functions: sprint_rusage, si_code_2_name, sprint_siginfo, poison, do_waitid, main; syscall numbers/wrappers: waitid, __NR_waitid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: waitid, __NR_waitid.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitpid.c -->
# sources/test-tools/strace/tests/waitpid.c

## Purpose
Covers strace decoder coverage for `waitpid`. Source comments/macros state: Check decoding of waitpid syscall. Source read: 36 lines, 691 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, <sys/wait.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: waitpid, __NR_waitpid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: waitpid, __NR_waitpid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xattr-strings.c -->
# sources/test-tools/strace/tests/xattr-strings.c

## Purpose
Covers strace decoder coverage for `xattr-strings`. Source read: 37 lines, 721 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/xattr.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
may create temporary extended attributes for successful xattr decoding.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xattr-strings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xattr.c -->
# sources/test-tools/strace/tests/xattr.c

## Purpose
Covers strace decoder coverage for `xattr`. Source read: 130 lines, 3951 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/xattr.h>; defines/undefs: XATTR_SIZE_MAX; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; may create temporary extended attributes for successful xattr decoding.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xchownx.c -->
# sources/test-tools/strace/tests/xchownx.c

## Purpose
Covers strace decoder coverage for `xchownx`. Source comments/macros state: Check decoding of chown/chown32/lchown/lchown32/fchown/fchown32 syscalls. Source read: 139 lines, 2925 bytes.

## Important APIs, Types, And Functions
includes/imports: <fcntl.h>, <stdio.h>, <unistd.h>; defines/undefs: UGID_TYPE, GETEUID, GETEGID, CHECK_OVERFLOWUID, CHECK_OVERFLOWGID, UNLINK_SAMPLE, CLOSE_SAMPLE, SYSCALL_ARG1, FMT_ARG1, EOK_CMD, CLEANUP_CMD, PAIR; C functions: ugid2int, print_int, num_matches_id, main; syscall numbers/wrappers: geteuid, getegid, __NR_geteuid, __NR_getegid, SYSCALL_NR; harness commands: # define CHECK_OVERFLOWUID(arg) check_overflowuid(arg), # define CHECK_OVERFLOWGID(arg) check_overflowgid(arg).

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: geteuid, getegid, __NR_geteuid, __NR_getegid, SYSCALL_NR.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xchownx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list--pidns-translation.c -->
# sources/test-tools/strace/tests/xet_robust_list--pidns-translation.c

## Purpose
Variant wrapper for `xet_robust_list.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 55 bytes.

## Important APIs, Types, And Functions
includes/imports: "xet_robust_list.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `xet_robust_list.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `xet_robust_list.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list.c -->
# sources/test-tools/strace/tests/xet_robust_list.c

## Purpose
Covers strace decoder coverage for `xet_robust_list`. Source comments/macros state: Check decoding of get_robust_list and set_robust_list syscalls. It has dual-use as a marker of the beginning of the test output Source read: 71 lines, 1839 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: sprintaddr, main; syscall numbers/wrappers: get_robust_list, set_robust_list, __NR_get_robust_list, __NR_set_robust_list.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: get_robust_list, set_robust_list, __NR_get_robust_list, __NR_set_robust_list.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xet_robust_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xet_thread_area_x86.c -->
# sources/test-tools/strace/tests/xet_thread_area_x86.c

## Purpose
Covers strace decoder coverage for `xet_thread_area_x86`. Source comments/macros state: Check decoding of set_thread_area and get_thread_area syscalls on x86 architecture. Perform set_thread_area call along with printing the expected output. @param ptr_val Pointer to thread area argument. @param ptr_str Explicit string representation of the argument. @param valid Whether argument points to the valid memory and its contents should be decoded. @param entry_number_str explicit decoding of the. Source read: 206 lines, 5588 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <assert.h>, <errno.h>, <stdio.h>, <stdint.h>, <string.h>, <unistd.h>, "print_user_desc.c"; defines/undefs: none; C functions: printptr, set_thread_area, get_thread_area, main; syscall numbers/wrappers: get_thread_area, set_thread_area, reboot, __NR_set_thread_area, __NR_get_thread_area, __NR_reboot; struct types: user_desc.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: get_thread_area, set_thread_area, reboot, __NR_set_thread_area, __NR_get_thread_area, __NR_reboot.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xet_thread_area_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetitimer.c -->
# sources/test-tools/strace/tests/xetitimer.c

## Purpose
Covers strace decoder coverage for `xetitimer`. Source comments/macros state: Check decoding of setitimer and getitimer syscalls. ITIMER_??? ITIMER_??? Source read: 173 lines, 6568 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <stdint.h>, <sys/time.h>, <unistd.h>, "scno.h", "kernel_timeval.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: setitimer, getitimer, __NR_setitimer, __NR_getitimer.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: setitimer, getitimer, __NR_setitimer, __NR_getitimer.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetitimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetpgid--pidns-translation.c -->
# sources/test-tools/strace/tests/xetpgid--pidns-translation.c

## Purpose
Variant wrapper for `xetpgid.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "xetpgid.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `xetpgid.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `xetpgid.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetpgid--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetpgid.c -->
# sources/test-tools/strace/tests/xetpgid.c

## Purpose
Covers strace decoder coverage for `xetpgid`. Source comments/macros state: Check decoding of getpgid and setpgid syscalls. Source read: 38 lines, 836 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: getpgid, setpgid, __NR_getpgid, __NR_setpgid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: getpgid, setpgid, __NR_getpgid, __NR_setpgid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetpgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority--pidns-translation.c -->
# sources/test-tools/strace/tests/xetpriority--pidns-translation.c

## Purpose
Variant wrapper for `xetpriority.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 51 bytes.

## Important APIs, Types, And Functions
includes/imports: "xetpriority.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `xetpriority.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `xetpriority.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority.c -->
# sources/test-tools/strace/tests/xetpriority.c

## Purpose
Covers strace decoder coverage for `xetpriority`. Source comments/macros state: Check decoding of getpriority and setpriority syscalls. Source read: 47 lines, 1075 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <sys/resource.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: getpriority, setpriority, __NR_getpriority, __NR_setpriority.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: getpriority, setpriority, __NR_getpriority, __NR_setpriority.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xetpriority.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xettimeofday.c -->
# sources/test-tools/strace/tests/xettimeofday.c

## Purpose
Covers strace decoder coverage for `xettimeofday`. Source comments/macros state: __NR_gettimeofday Source read: 77 lines, 2298 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", <assert.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/time.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettimeofday, settimeofday, __NR_gettimeofday, __NR_settimeofday; struct types: timezone.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: gettimeofday, settimeofday, __NR_gettimeofday, __NR_settimeofday.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xgetdents.c -->
# sources/test-tools/strace/tests/xgetdents.c

## Purpose
Covers strace decoder coverage for `xgetdents`. Source comments/macros state: Check decoding of getdents and getdents64 syscalls. %lu entries 0 entries Source read: 141 lines, 3310 bytes.

## Important APIs, Types, And Functions
includes/imports: <dirent.h>, <fcntl.h>, <stdio.h>, <unistd.h>, <sys/stat.h>, "kernel_dirent.h", "print_fields.h"; defines/undefs: none; C functions: str_d_type, print_dirent, k_getdents, ls, main; syscall numbers/wrappers: NR_getdents.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: NR_getdents.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xgetdents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xgetrlimit.c -->
# sources/test-tools/strace/tests/xgetrlimit.c

## Purpose
Covers strace decoder coverage for `xgetrlimit`. Source comments/macros state: Check decoding of getrlimit/ugetrlimit syscall. space for 2 llu strings space for XLAT_STYLE_ABBREV decoding space for C style comments RLIM64_INFINITY XLAT_ABBREV RLIM_INFINITY XLAT_ABBREV %llu*1024 XLAT_ABBREV !XLAT_RAW RLIMIT_??? NR_GETRLIMIT Source read: 113 lines, 2654 bytes.

## Important APIs, Types, And Functions
includes/imports: <errno.h>, <stdint.h>, <stdio.h>, <sys/resource.h>, <unistd.h>, "xlat.h", "xlat/resources.h"; defines/undefs: none; C functions: sprint_rlim, main; syscall numbers/wrappers: NR_GETRLIMIT; struct types: xlat_data.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: NR_GETRLIMIT.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `xlat.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xgetrlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xmalloc_for_tests.c -->
# sources/test-tools/strace/tests/xmalloc_for_tests.c

## Purpose
Variant wrapper for `xmalloc.c`. It defines `error_msg_and_die` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 66 bytes.

## Important APIs, Types, And Functions
includes/imports: "xmalloc.c"; defines/undefs: error_msg_and_die.

## Control Flow
Preprocessor-only flow: set `error_msg_and_die`, include `xmalloc.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `xmalloc.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xmalloc_for_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xselect.c -->
# sources/test-tools/strace/tests/xselect.c

## Purpose
Covers strace decoder coverage for `xselect`. Source comments/macros state: Check decoding of select/_newselect syscalls. Based on test by Dr. David Alan Gilbert <dave@treblig.org> End of XSELECT definition. PATH_TRACING_FD || TRACING_FD An equivalent of nanosleep. EFAULT on tv argument Start with a nice simple select with the same set. PATH_TRACING_FD || TRACING_FD !PATH_TRACING_FD && !TRACING_FD PATH_TRACING_FD && TRACING_FD Odd timeout. PATH_TRACING_FD && TRACING_FD PATH_TRACING_FD &&. Source read: 499 lines, 15449 bytes.

## Important APIs, Types, And Functions
includes/imports: <errno.h>, <limits.h>, <stdint.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/select.h>, "kernel_timeval.h"; defines/undefs: XSELECT; C functions: xselect, main; syscall numbers/wrappers: TEST_SYSCALL_NR.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: TEST_SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `kernel_timeval.h`, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xselect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs.c -->
# sources/test-tools/strace/tests/xstatfs.c

## Purpose
Covers strace decoder coverage for `xstatfs`. Source read: 26 lines, 715 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatfsx.c"; defines/undefs: SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, STRUCT_STATFS, PRINT_F_FRSIZE, PRINT_F_FLAGS, PRINT_F_FSID; syscall numbers/wrappers: SYSCALL_NR; struct types: statfs.

## Control Flow
primary syscall coverage: SYSCALL_NR.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs64.c -->
# sources/test-tools/strace/tests/xstatfs64.c

## Purpose
Covers strace decoder coverage for `xstatfs64`. Source read: 28 lines, 785 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatfsx.c"; defines/undefs: SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, STRUCT_STATFS, PRINT_F_FRSIZE, PRINT_F_FLAGS, PRINT_F_FSID, CHECK_ODD_SIZE; syscall numbers/wrappers: SYSCALL_NR; struct types: statfs64.

## Control Flow
primary syscall coverage: SYSCALL_NR.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on the C library/shell runtime and local strace test harness. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfsx.c -->
# sources/test-tools/strace/tests/xstatfsx.c

## Purpose
Covers strace decoder coverage for `xstatfsx`. Source read: 108 lines, 2647 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdio.h>, <fcntl.h>, <unistd.h>, <linux/types.h>, <asm/statfs.h>, "xlat.h", "xlat/fsmagic.h", "xlat/statfs_flags.h"; defines/undefs: PRINT_NUM; C functions: print_statfs_type, print_statfs, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `xlat.h`, Linux UAPI headers, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatx.c -->
# sources/test-tools/strace/tests/xstatx.c

## Purpose
Covers strace decoder coverage for `xstatx`. Source comments/macros state: MPERS_IS_m32 || MPERS_IS_mx32 || HAVE_STRUCT_STAT64_ST_MTIME_NSEC !STRUCT_STAT_IS_STAT64 MPERS_IS_m32 || MPERS_IS_mx32 STRUCT_STAT_IS_STAT64 Fixes -Wunused warning ", mode); print_ftype(mode); printf("|"); print_perms(mode); printf(" makedev(%#x, %#x) XLAT_ABBREV !OLD_STAT OLD_STAT !IS_STATX !IS_STATX !OLD_STAT IS_STATX We're done playing with flags. STATX_??? ...and with mask. IS_STATX error TEST_SYSCALL_STR must. Source read: 550 lines, 13885 bytes.

## Important APIs, Types, And Functions
includes/imports: <errno.h>, <stdio.h>, <stddef.h>, <time.h>, <unistd.h>, <sys/sysmacros.h>, "print_fields.h", <fcntl.h>, <sys/stat.h>, "asm_stat.h"; defines/undefs: STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64, SAMPLE_SIZE, stat, stat64, statx, statx_timestamp, st_atime, st_mtime, st_ctime, HAVE_STRUCT_STAT_ST_MTIME_NSEC, TEST_BOGUS_STRUCT_STAT, IS_FSTAT, OLD_STAT, IS_STATX, TIME_NSEC, HAVE_NSEC, PRINT_ST_TIME, PRINT_FIELD_U32_UID, PRINT_FIELD_TIME, ST_SIZE_FIELD, LOG_STAT_OFFSETOF_SIZEOF, INVOKE, SET_FLAGS_INVOKE, SET_MASK_INVOKE; C functions: print_ftype, print_perms, print_st_mode, sprint_makedev, print_stat, create_sample, main; struct types: stat, statx, timespec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatx.c -->
