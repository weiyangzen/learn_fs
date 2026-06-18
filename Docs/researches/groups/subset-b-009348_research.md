# subset-b-009348 Research

Grouped research for the exact strace test files assigned to subset-b-009348. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/file_xetattr-common.c -->
# sources/test-tools/strace/tests/file_xetattr-common.c

## Purpose
Covers strace decoder coverage for `file_getattr`. Source comments describe: Check decoding of file_getattr and file_setattr syscalls. size < FILE_ATTR_SIZE_VER0, no read size == FILE_ATTR_SIZE_VER0, no read size == FILE_ATTR_SIZE_VER0, short read size > PAGE_SIZE, no read size > sizeof(struct file_attr), short read size > sizeof(struct file_attr), normal read bytes %u..%u size == sizeof(struct file_attr), normal read Source read: 280 lines, 7457 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xmalloc.h", <fcntl.h>, <stdio.h>, <string.h>, <unistd.h>, <linux/fs.h>, "test_fs_xflags.h"; defines: AT_SYMLINK_NOFOLLOW, AT_EMPTY_PATH, FD_PATH, YFLAG, SKIP_IF_PROC_IS_UNAVAILABLE, RETVAL_INJECTED, INJ_STR; C functions: file_xetattr, main; syscall names/numbers: SYSCALL_NR; struct types: file_attr, strval64, strival32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, Linux UAPI headers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/file_xetattr-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fill_memory.c -->
# sources/test-tools/strace/tests/fill_memory.c

## Purpose
Covers strace self-test coverage for `fill_memory`. Source read: 76 lines, 1384 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h"; defines: none; C functions: fill_memory_ex, fill_memory, fill_memory16_ex, fill_memory16, fill_memory32_ex, fill_memory32, fill_memory64_ex, fill_memory64.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fill_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter-unavailable.c -->
# sources/test-tools/strace/tests/filter-unavailable.c

## Purpose
Covers strace self-test coverage for `filter-unavailable`. Source read: 63 lines, 1031 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdlib.h>, <unistd.h>, <pthread.h>, <sys/wait.h>; defines: P, T; C functions: process, main; struct types: timespec.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter-unavailable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-flag.c -->
# sources/test-tools/strace/tests/filter_seccomp-flag.c

## Purpose
Covers that syscall numbers do not conflict with seccomp filter flags. Source comments describe: Check that syscall numbers do not conflict with seccomp filter flags. PERSONALITY*_AUDIT_ARCH definitions depend on AUDIT_ARCH_* constants. Define these shorthand notations to simplify the syscallent files. Source read: 83 lines, 1868 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "arch_defs.h", "sysent.h", "scno.h", <linux/audit.h>, "xlat/elf_em.h", "xlat/audit_arch.h", "sysent_shorthand_defs.h", "syscallent.h", "syscallent1.h", "syscallent2.h"; defines: XLAT_MACROS_ONLY; C functions: main; struct types: audit_arch_t.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-flag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-perf.c -->
# sources/test-tools/strace/tests/filter_seccomp-perf.c

## Purpose
Covers seccomp filter performance. Source comments describe: Check seccomp filter performance. Source read: 39 lines, 589 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <stdbool.h>, <stdio.h>, <unistd.h>; defines: none; C functions: handler, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration; timing/performance checks need tolerance for scheduler noise. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp-perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.in -->
# sources/test-tools/strace/tests/filter_seccomp.in

## Purpose
Covers strace self-test coverage for `filter_seccomp`. Source read: 4 lines, 238 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
shell/table state is file based: generated scripts, logs, expected-output files, and harness variables.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration; concurrency and process ordering can make trace matching fragile. Test signals: generated `.gen.test` scripts and `gen_tests.am` are build outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.sh -->
# sources/test-tools/strace/tests/filter_seccomp.sh

## Purpose
Covers the `filter_seccomp.sh` strace test helper script. Source comments describe: # Skip the test if seccomp filter is not available. # Copyright (c) 2018-2019 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 14 lines, 396 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Shell control flow runs top to bottom with 0 loop(s) and 0 case block(s), using harness helpers for skip/fail behavior and writing generated or probe output as directed.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/finit_module.c -->
# sources/test-tools/strace/tests/finit_module.c

## Purpose
Covers strace decoder coverage for `finit_module`. Source comments describe: Check decoding of finit_module syscall. MODULE_INIT_??? Source read: 100 lines, 2683 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "init_delete_module.h"; defines: none; C functions: main; syscall names/numbers: finit_module, __NR_finit_module.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is finit_module, __NR_finit_module.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; touches module-loading syscalls with invalid or synthetic payloads; durable kernel module state is not expected.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; module syscalls may be blocked by privileges, lockdown, or kernel configuration. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/finit_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/flock.c -->
# sources/test-tools/strace/tests/flock.c

## Purpose
Covers strace decoder coverage for `flock`. Source comments describe: Check decoding of flock syscall. Source read: 28 lines, 514 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/file.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: flock, __NR_flock.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is flock, __NR_flock.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.awk -->
# sources/test-tools/strace/tests/fork--pidns-translation.awk

## Purpose
Covers AWK matching logic for `fork--pidns-translation` strace output. Source read: 15 lines, 283 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; AWK rules: /fork/ {, match($0, "([0-9]+) in strace\x27s PID NS", a);, if (a[1]), fork_pid = a[1], }, /exited with 0/ {, if (!exit_pid), exit_pid = $1.

## Control Flow
AWK control flow evaluates each strace output record, applies regex substitutions/matches, and exits nonzero when a required pid-namespace translation pattern is absent or malformed.

## State And Persistence Behavior
No persistent state is written. AWK state is per-record variables and exit status while validating a trace log stream.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: AWK exit status validates transformed trace output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.c -->
# sources/test-tools/strace/tests/fork--pidns-translation.c

## Purpose
Covers strace self-test coverage for `fork--pidns-translation`. Source comments describe: Test PID namespace translation Source read: 75 lines, 1202 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <errno.h>, <limits.h>, <sched.h>, <signal.h>, <stdio.h>, <stdlib.h>, <sys/wait.h>, <unistd.h>, <linux/sched.h>, <linux/nsfs.h>; defines: none; C functions: fork_chain, main; syscall names/numbers: fork, __NR_fork.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events. primary syscall coverage is fork, __NR_fork.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization; concurrency and process ordering can make trace matching fragile. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork-f.c -->
# sources/test-tools/strace/tests/fork-f.c

## Purpose
Covers strace self-test coverage for `fork-f`. Source read: 77 lines, 1420 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/wait.h>; defines: prefix, logit; C functions: logit_, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork-f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsconfig-P.c -->
# sources/test-tools/strace/tests/fsconfig-P.c

## Purpose
Variant wrapper that includes `fsconfig.c` after defining `PATH_TRACING`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 43 bytes.

## Important APIs, Types, And Functions
includes/imports: "fsconfig.c"; defines: PATH_TRACING.

## Control Flow
Preprocessor control flow only: define `PATH_TRACING`, include `fsconfig.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fsconfig.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsconfig-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsconfig.c -->
# sources/test-tools/strace/tests/fsconfig.c

## Purpose
Covers strace decoder coverage for `fsconfig`. Source comments describe: Check decoding of fsconfig syscall. FSCONFIG_??? FSCONFIG_??? Source read: 291 lines, 8420 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <fcntl.h>, <limits.h>, <stdio.h>, <stdint.h>, <unistd.h>, <linux/mount.h>; defines: none; C functions: k_fsconfig, test_fsconfig_unknown, test_fsconfig_cmd, test_fsconfig_set_flag, test_fsconfig_set_string, test_fsconfig_set_binary, test_fsconfig_set_path, test_fsconfig_set_fd, main; syscall names/numbers: fsconfig, __NR_fsconfig.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is fsconfig, __NR_fsconfig.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsmount.c -->
# sources/test-tools/strace/tests/fsmount.c

## Purpose
Covers strace decoder coverage for `fsmount`. Source comments describe: Check decoding of fsmount syscall. FSMOUNT_??? FSMOUNT_??? MOUNT_ATTR_??? MOUNT_ATTR_??? Source read: 92 lines, 2621 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <fcntl.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fsmount, main; syscall names/numbers: fsmount, __NR_fsmount; struct types: strval32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is fsmount, __NR_fsmount.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsopen.c -->
# sources/test-tools/strace/tests/fsopen.c

## Purpose
Covers strace decoder coverage for `fsopen`. Source comments describe: Check decoding of fsopen syscall. FSOPEN_??? FSOPEN_??? Source read: 59 lines, 1502 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fsopen, main; syscall names/numbers: fsopen, __NR_fsopen.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is fsopen, __NR_fsopen.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fspick-P.c -->
# sources/test-tools/strace/tests/fspick-P.c

## Purpose
Variant wrapper that includes `fspick.c` after defining `PATH_TRACING`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 41 bytes.

## Important APIs, Types, And Functions
includes/imports: "fspick.c"; defines: PATH_TRACING.

## Control Flow
Preprocessor control flow only: define `PATH_TRACING`, include `fspick.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fspick.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fspick-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fspick.c -->
# sources/test-tools/strace/tests/fspick.c

## Purpose
Covers strace decoder coverage for `fspick`. Source comments describe: Check decoding of fspick syscall. FSPICK_??? Source read: 104 lines, 2720 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <fcntl.h>, <limits.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fspick, main; syscall names/numbers: fspick, __NR_fspick.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is fspick, __NR_fspick.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fspick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xabbrev.c -->
# sources/test-tools/strace/tests/fstat-Xabbrev.c

## Purpose
Variant wrapper that includes `fstat.c` after defining `no visible macros`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 1 lines, 19 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat.c"; defines: none.

## Control Flow
Preprocessor control flow only: define `mode macro`, include `fstat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xraw.c -->
# sources/test-tools/strace/tests/fstat-Xraw.c

## Purpose
Variant wrapper that includes `fstat.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 38 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `fstat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xverbose.c -->
# sources/test-tools/strace/tests/fstat-Xverbose.c

## Purpose
Variant wrapper that includes `fstat.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 42 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `fstat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat.c -->
# sources/test-tools/strace/tests/fstat.c

## Purpose
Covers strace self-test coverage for `fstat`. Source read: 23 lines, 455 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "fstatx.c"; defines: TEST_SYSCALL_NR, TEST_SYSCALL_STR, SAMPLE_SIZE; syscall names/numbers: fstat.

## Control Flow
primary syscall coverage is fstat.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `fstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xabbrev.c -->
# sources/test-tools/strace/tests/fstat64-Xabbrev.c

## Purpose
Variant wrapper that includes `fstat64.c` after defining `no visible macros`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 1 lines, 21 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat64.c"; defines: none.

## Control Flow
Preprocessor control flow only: define `mode macro`, include `fstat64.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xraw.c -->
# sources/test-tools/strace/tests/fstat64-Xraw.c

## Purpose
Variant wrapper that includes `fstat64.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 40 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat64.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `fstat64.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xverbose.c -->
# sources/test-tools/strace/tests/fstat64-Xverbose.c

## Purpose
Variant wrapper that includes `fstat64.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 44 bytes.

## Important APIs, Types, And Functions
includes/imports: "fstat64.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `fstat64.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `fstat64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64.c -->
# sources/test-tools/strace/tests/fstat64.c

## Purpose
Covers strace self-test coverage for `fstat64`. Source read: 25 lines, 504 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "fstatx.c"; defines: TEST_SYSCALL_NR, TEST_SYSCALL_STR, STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64; syscall names/numbers: fstat64; struct types: stat64.

## Control Flow
primary syscall coverage is fstat64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `fstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat.c -->
# sources/test-tools/strace/tests/fstatat.c

## Purpose
Covers strace self-test coverage for `fstatat`. Source read: 28 lines, 668 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatx.c"; defines: TEST_SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, PRINT_SYSCALL_FOOTER; syscall names/numbers: TEST_SYSCALL_NR.

## Control Flow
primary syscall coverage is TEST_SYSCALL_NR.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `xstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat64.c -->
# sources/test-tools/strace/tests/fstatat64.c

## Purpose
Covers strace self-test coverage for `fstatat64`. Source read: 25 lines, 513 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "fstatat.c"; defines: TEST_SYSCALL_NR, TEST_SYSCALL_STR, STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64; syscall names/numbers: fstatat64; struct types: stat64.

## Control Flow
primary syscall coverage is fstatat64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `fstatat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs.c -->
# sources/test-tools/strace/tests/fstatfs.c

## Purpose
Covers strace self-test coverage for `fstatfs`. Source read: 24 lines, 462 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xstatfs.c"; defines: SYSCALL_ARG_FMT, SYSCALL_ARG, SYSCALL_NR, SYSCALL_NAME; syscall names/numbers: fstatfs.

## Control Flow
primary syscall coverage is fstatfs.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xstatfs.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs64.c -->
# sources/test-tools/strace/tests/fstatfs64.c

## Purpose
Covers strace self-test coverage for `fstatfs64`. Source read: 24 lines, 472 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xstatfs64.c"; defines: SYSCALL_ARG_FMT, SYSCALL_ARG, SYSCALL_NR, SYSCALL_NAME; syscall names/numbers: fstatfs64.

## Control Flow
primary syscall coverage is fstatfs64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xstatfs64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatx.c -->
# sources/test-tools/strace/tests/fstatx.c

## Purpose
Covers strace self-test coverage for `fstatx`. Source read: 21 lines, 525 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatx.c"; defines: IS_FSTAT, TEST_SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, PRINT_SYSCALL_FOOTER; syscall names/numbers: TEST_SYSCALL_NR.

## Control Flow
primary syscall coverage is TEST_SYSCALL_NR.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `xstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsync-y.c -->
# sources/test-tools/strace/tests/fsync-y.c

## Purpose
Covers printing of file name in strace -y mode. Source comments describe: Check printing of file name in strace -y mode. Source read: 53 lines, 1149 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <limits.h>, <stdio.h>, <unistd.h>; defines: none; C functions: main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsync-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsync.c -->
# sources/test-tools/strace/tests/fsync.c

## Purpose
Covers strace decoder coverage for `fsync`. Source comments describe: Check decoding of fsync syscall. Source read: 26 lines, 455 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: fsync, __NR_fsync.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is fsync, __NR_fsync.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ftruncate.c -->
# sources/test-tools/strace/tests/ftruncate.c

## Purpose
Covers strace self-test coverage for `ftruncate`. Source read: 39 lines, 683 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: ftruncate, __NR_ftruncate.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is ftruncate, __NR_ftruncate.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ftruncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ftruncate64.c -->
# sources/test-tools/strace/tests/ftruncate64.c

## Purpose
Covers strace self-test coverage for `ftruncate64`. Source read: 34 lines, 574 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: ftruncate64.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is ftruncate64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ftruncate64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex.c -->
# sources/test-tools/strace/tests/futex.c

## Purpose
Covers strace self-test coverage for `futex`. Source comments describe: It is here due to EPERM on WAKE_OP on AArch64 Since timeout value is copied before full op check, we should provide some valid timeout address or NULL FUTEX_??? Value which differs from one stored in int *val FUTEX_WAIT - check whether uaddr == val and sleep Possible flags: PRIVATE, CLOCK_RT (since 4.5) 1. uaddr - futex address 2. op - FUTEX_WAIT 3. val -. Source read: 820 lines, 31098 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <stdarg.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/time.h>, "xlat.h", "xlat/futexops.h", "xlat/futexwakeops.h", "xlat/futexwakecmps.h"; defines: FUTEX_PRIVATE_FLAG, FUTEX_CLOCK_REALTIME, FUTEX_CMD_MASK, CHECK_FUTEX_GENERIC, CHECK_FUTEX_ENOSYS, CHECK_FUTEX, CHECK_INVALID_CLOCKRT, VAL, VAL_PR, VALP, VALP_PR, VAL2, VAL2_PR, VAL2P, VAL2P_PR, VAL3, VAL3_PR, VAL3A; C functions: futex_error, invalid_op, main; syscall names/numbers: futex, __NR_futex.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex, __NR_futex.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex2_flags.h -->
# sources/test-tools/strace/tests/futex2_flags.h

## Purpose
Covers strace decoder coverage for `FUTEX2_`. Source comments describe: Check decoding of FUTEX2_* flags. FUTEX2_SIZE_U8 FUTEX2_SIZE_U16 FUTEX2_SIZE_U32 FUTEX2_SIZE_U64 FUTEX2_SIZE_U8|FUTEX2_NUMA FUTEX2_SIZE_U16|FUTEX2_MPOL FUTEX2_SIZE_U32|FUTEX2_PRIVATE FUTEX2_SIZE_U64|FUTEX2_NUMA|FUTEX2_PRIVATE FUTEX2_SIZE_U8|0xffffff70 FUTEX2_SIZE_U64|FUTEX2_NUMA|FUTEX2_MPOL" "|FUTEX2_PRIVATE|0xffffff70 Source read: 65 lines, 1427 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h"; defines: STRACE_TESTS_FUTEX2_FLAGS_H.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
No runtime state is owned here. The header contributes compile-time constants, declarations, or helper macros to including tests.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex2_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xabbrev.c -->
# sources/test-tools/strace/tests/futex_requeue-Xabbrev.c

## Purpose
Variant wrapper that includes `futex_requeue.c` after defining `no visible macros`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 1 lines, 27 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_requeue.c"; defines: none.

## Control Flow
Preprocessor control flow only: define `mode macro`, include `futex_requeue.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_requeue.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xraw.c -->
# sources/test-tools/strace/tests/futex_requeue-Xraw.c

## Purpose
Variant wrapper that includes `futex_requeue.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_requeue.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `futex_requeue.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_requeue.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xverbose.c -->
# sources/test-tools/strace/tests/futex_requeue-Xverbose.c

## Purpose
Variant wrapper that includes `futex_requeue.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 50 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_requeue.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `futex_requeue.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_requeue.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue.c -->
# sources/test-tools/strace/tests/futex_requeue.c

## Purpose
Covers strace decoder coverage for `futex_requeue`. Source comments describe: Check decoding of futex_requeue syscall. FUTEX2_SIZE_U32|FUTEX2_PRIVATE Source read: 97 lines, 2594 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "futex2_flags.h", "scno.h", "xmalloc.h", <stdio.h>, <unistd.h>, <linux/futex.h>; defines: none; C functions: k_futex_requeue, main; syscall names/numbers: futex_requeue, __NR_futex_requeue; struct types: futex_waitv, strval32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_requeue, __NR_futex_requeue.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; expected output depends on xlat raw/abbrev/verbose formatting. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_requeue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xabbrev.c -->
# sources/test-tools/strace/tests/futex_wait-Xabbrev.c

## Purpose
Variant wrapper that includes `futex_wait.c` after defining `no visible macros`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 1 lines, 24 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wait.c"; defines: none.

## Control Flow
Preprocessor control flow only: define `mode macro`, include `futex_wait.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wait.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xraw.c -->
# sources/test-tools/strace/tests/futex_wait-Xraw.c

## Purpose
Variant wrapper that includes `futex_wait.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 43 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wait.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `futex_wait.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wait.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xverbose.c -->
# sources/test-tools/strace/tests/futex_wait-Xverbose.c

## Purpose
Variant wrapper that includes `futex_wait.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wait.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `futex_wait.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wait.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait.c -->
# sources/test-tools/strace/tests/futex_wait.c

## Purpose
Covers strace decoder coverage for `futex_wait`. Source comments describe: Check decoding of futex_wait syscall. FUTEX_BITSET_MATCH_ANY CLOCK_REALTIME CLOCK_MONOTONIC CLOCK_??? CLOCK_??? Source read: 130 lines, 2948 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "futex2_flags.h", "kernel_timespec.h", "scno.h", "xmalloc.h", <stdio.h>, <unistd.h>; defines: none; C functions: k_futex_wait, main; syscall names/numbers: futex_wait, __NR_futex_wait.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_wait, __NR_futex_wait.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, `kernel_timespec.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; expected output depends on xlat raw/abbrev/verbose formatting. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_waitv.c -->
# sources/test-tools/strace/tests/futex_waitv.c

## Purpose
Covers strace decoder coverage for `futex_waitv`. Source comments describe: Check decoding of futex_waitv syscall. CLOCK_??? %p Source read: 136 lines, 4439 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timespec.h", <stdio.h>, <stdlib.h>, <time.h>, <unistd.h>, <linux/futex.h>; defines: none; C functions: k_futex_waitv, main; syscall names/numbers: futex_waitv, __NR_futex_waitv; struct types: futex_waitv.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_waitv, __NR_futex_waitv.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timespec.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_waitv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xabbrev.c -->
# sources/test-tools/strace/tests/futex_wake-Xabbrev.c

## Purpose
Variant wrapper that includes `futex_wake.c` after defining `no visible macros`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 1 lines, 24 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wake.c"; defines: none.

## Control Flow
Preprocessor control flow only: define `mode macro`, include `futex_wake.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wake.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xraw.c -->
# sources/test-tools/strace/tests/futex_wake-Xraw.c

## Purpose
Variant wrapper that includes `futex_wake.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 43 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wake.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `futex_wake.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wake.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xverbose.c -->
# sources/test-tools/strace/tests/futex_wake-Xverbose.c

## Purpose
Variant wrapper that includes `futex_wake.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wake.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `futex_wake.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wake.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake.c -->
# sources/test-tools/strace/tests/futex_wake.c

## Purpose
Covers strace decoder coverage for `futex_wake`. Source comments describe: Check decoding of futex_wake syscall. FUTEX_BITSET_MATCH_ANY Source read: 97 lines, 2047 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "futex2_flags.h", "scno.h", "xmalloc.h", <stdio.h>, <unistd.h>; defines: none; C functions: k_futex_wake, main; syscall names/numbers: futex_wake, __NR_futex_wake.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_wake, __NR_futex_wake.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; expected output depends on xlat raw/abbrev/verbose formatting. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futimesat.c -->
# sources/test-tools/strace/tests/futimesat.c

## Purpose
Covers strace decoder coverage for `futimesat`. Source comments describe: Check decoding of futimesat syscall. dirfd pathname times Source read: 148 lines, 3842 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", <stdint.h>, <stdio.h>, <sys/time.h>, <unistd.h>; defines: none; C functions: print_tv, k_futimesat, main; syscall names/numbers: futimesat, __NR_futimesat.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is futimesat, __NR_futimesat.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futimesat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gen_pure_executables.sh -->
# sources/test-tools/strace/tests/gen_pure_executables.sh

## Purpose
Covers the `gen_pure_executables.sh` strace test helper script. Source comments describe: }/pure_executables.list" [ $# -eq 0 ] || { input="$1"; shift; } output="$(dirname "$input")/pure_executables.am" [ $# -eq 0 ] || { output="$1"; shift; } [ $# -eq 0 ] || usage exec > "$output" echo "# Generated by $0 from $input; do not edit." echo 'PURE_EXECUTABLES = \' sed -n 's/^[^#]. # Copyright (c) 2017-2021 Dmitry V. Levin <ldv@strace.io> All rights. Source read: 30 lines, 666 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; shell functions: usage.

## Control Flow
Shell control flow runs top to bottom with 0 loop(s) and 0 case block(s), using harness helpers for skip/fail behavior and writing generated or probe output as directed.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gen_pure_executables.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gen_secontext.sh -->
# sources/test-tools/strace/tests/gen_secontext.sh

## Purpose
Covers the `gen_secontext.sh` strace test helper script. Source comments describe: }/gen_tests.in" else input="$1" shift fi dir="$(dirname "$input")" [ $# -eq 0 ] || usage { cat <<EOF # Generated by $0 from $input; do not edit. secontext_EXECUTABLES = \\ EOF sed -E -n 's/^([^#[:space:]]+--secontext(_full)?(_mismatch)?)[[:space:]]. # Copyright (c) 2020-2023 The strace developers. All rights reserved. # SPDX-License-Identifier:. Source read: 80 lines, 1671 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "${name%--secontext}.c", "${name%_full}.c", "${name%_mismatch}.c"; defines: TEST_SECONTEXT, PRINT_SECONTEXT_FULL, PRINT_SECONTEXT_MISMATCH; shell functions: usage.

## Control Flow
Shell control flow runs top to bottom with 3 loop(s) and 0 case block(s), using harness helpers for skip/fail behavior and writing generated or probe output as directed.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `tests.h`, shared implementation `${name%_mismatch}.c`, `gen_tests.in` test manifest. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gen_secontext.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.in -->
# sources/test-tools/strace/tests/gen_tests.in

## Purpose
Covers the generated strace test manifest with 1324 active test rows. Source comments describe: RLIMIT_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? PR_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? RLIMIT_??? Input for gen_tests.sh # Copyright (c) 2017-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 1331 lines, 70936 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Declarative table consumed sequentially by `gen_tests.sh`; each row maps a test name to optional argv0/script selector and strace arguments. First active rows include _newselect, _newselect-P, accept, accept4, access, access--secontext, access--secontext_full, access--secontext_full_mismatch, access--secontext_mismatch, acct.

## State And Persistence Behavior
The file is declarative manifest state. It does not execute by itself; persistence is the checked-in table content consumed by `gen_tests.sh` to regenerate test scripts.

## Dependencies And Integration Points
Depends on the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization; seccomp-BPF availability and filter installation can vary by kernel/configuration; module syscalls may be blocked by privileges, lockdown, or kernel configuration; concurrency and process ordering can make trace matching fragile. Test signals: harness uses exact diff matching; generated `.gen.test` scripts and `gen_tests.am` are build outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.sh -->
# sources/test-tools/strace/tests/gen_tests.sh

## Purpose
Covers the `gen_tests.sh` strace test helper script. Source comments describe: }/gen_tests.in" [ $# -eq 0 ] || { input="$1"; shift; } output= [ $# -eq 0 ] || { output="$1"; shift; } [ $# -eq 0 ] || usage if [ -n "$output" ]; then match="${output## # Copyright (c) 2017 Dmitry V. Levin <ldv@strace.io> Copyright (c) 2017-2025 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Generated by $0 from. Source read: 114 lines, 2191 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; shell functions: usage.

## Control Flow
Parses optional input/output arguments, reads `gen_tests.in`, skips comments, chooses one of three generation paths (`+script`, injection/tampering, or normal `init.sh`), writes executable `.gen.test` files, and emits `gen_tests.am` when generating all tests.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `init.sh`, the built `strace` binary and test harness log/diff helpers, `gen_tests.in` test manifest. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: harness uses exact diff matching; generated `.gen.test` scripts and `gen_tests.am` are build outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gen_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_mempolicy.c -->
# sources/test-tools/strace/tests/get_mempolicy.c

## Purpose
Covers strace decoder coverage for `get_mempolicy`. Source comments describe: Check decoding of get_mempolicy syscall. Source read: 105 lines, 2729 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "xlat.h", "xlat/mpol_modes.h"; defines: MAX_STRLEN, NLONGS; C functions: print_nodes, main; syscall names/numbers: get_mempolicy, __NR_get_mempolicy.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is get_mempolicy, __NR_get_mempolicy.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_mempolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_page_size.c -->
# sources/test-tools/strace/tests/get_page_size.c

## Purpose
Covers strace self-test coverage for `get_page_size`. Source read: 20 lines, 302 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <unistd.h>; defines: none; C functions: get_page_size.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_page_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_process_reaper.c -->
# sources/test-tools/strace/tests/get_process_reaper.c

## Purpose
Covers strace self-test coverage for `get_process_reaper`. Source comments describe: Print the process reaper id. PARENT - CHILD - GRANDCHILD wait for notification from PARENT about CHILD completion write ppid to PARENT wait for CHILD completion notify GRANDCHILD about CHILD completion read ppid of GRANDCHILD CHILD PARENT Source read: 108 lines, 2180 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, <sys/wait.h>; defines: parent_read_fd, grandchild_write_fd, grandchild_read_fd, parent_write_fd; C functions: grandchild, child, parent, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_process_reaper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_sigset_size.c -->
# sources/test-tools/strace/tests/get_sigset_size.c

## Purpose
Covers strace self-test coverage for `get_sigset_size`. Source comments describe: Find out the size of kernel's sigset_t. If the sigset size specified to rt_sigprocmask is not equal to the size of kernel's sigset_t, the kernel does not look at anything else and fails with EINVAL. Otherwise, if both pointers specified to rt_sigprocmask are NULL, the kernel just returns 0. This vaguely documented kernel feature can be used to probe the. Source read: 47 lines, 1089 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <signal.h>, <unistd.h>, "scno.h"; defines: none; C functions: get_sigset_size; syscall names/numbers: rt_sigprocmask, __NR_rt_sigprocmask.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is rt_sigprocmask, __NR_rt_sigprocmask.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_sigset_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getcpu.c -->
# sources/test-tools/strace/tests/getcpu.c

## Purpose
Covers strace decoder coverage for `getcpu`. Source comments describe: Check decoding of getcpu syscall. Source read: 48 lines, 1172 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getcpu, __NR_getcpu.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getcpu, __NR_getcpu.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getcwd.c -->
# sources/test-tools/strace/tests/getcwd.c

## Purpose
Covers strace decoder coverage for `getcwd`. Source comments describe: Check decoding of getcwd syscall. Source read: 46 lines, 1005 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <limits.h>, <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getcwd, __NR_getcwd.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getcwd, __NR_getcwd.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getcwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getdents-v.c -->
# sources/test-tools/strace/tests/getdents-v.c

## Purpose
Variant wrapper that includes `getdents.c` after defining `VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 3 lines, 95 bytes.

## Important APIs, Types, And Functions
includes/imports: "getdents.c"; defines: VERBOSE.

## Control Flow
Preprocessor control flow only: define `VERBOSE`, include `getdents.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getdents.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getdents-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getdents.c -->
# sources/test-tools/strace/tests/getdents.c

## Purpose
Covers strace decoder coverage for `getdents`. Source comments describe: Check decoding of getdents syscall. Source read: 48 lines, 1048 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetdents.c"; defines: kernel_dirent_type, NR_getdents, STR_getdents; C functions: print_dirent; syscall names/numbers: getdents.

## Control Flow
primary syscall coverage is getdents.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xgetdents.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getdents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getdents64-v.c -->
# sources/test-tools/strace/tests/getdents64-v.c

## Purpose
Variant wrapper that includes `getdents64.c` after defining `VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 3 lines, 99 bytes.

## Important APIs, Types, And Functions
includes/imports: "getdents64.c"; defines: VERBOSE.

## Control Flow
Preprocessor control flow only: define `VERBOSE`, include `getdents64.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getdents64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getdents64-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getdents64.c -->
# sources/test-tools/strace/tests/getdents64.c

## Purpose
Covers strace decoder coverage for `getdents64`. Source comments describe: Check decoding of getdents64 syscall. Source read: 39 lines, 935 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetdents.c"; defines: kernel_dirent_type, NR_getdents, STR_getdents; C functions: print_dirent; syscall names/numbers: getdents64.

## Control Flow
primary syscall coverage is getdents64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xgetdents.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getdents64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getegid.c -->
# sources/test-tools/strace/tests/getegid.c

## Purpose
Covers strace decoder coverage for `getegid`. Source comments describe: Check decoding of getegid syscall. Source read: 21 lines, 341 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getegid, __NR_getegid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getegid, __NR_getegid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getegid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getegid32.c -->
# sources/test-tools/strace/tests/getegid32.c

## Purpose
Covers strace self-test coverage for `getegid32`. Source read: 27 lines, 374 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getegid32, __NR_getegid32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getegid32, __NR_getegid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getegid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/geteuid.c -->
# sources/test-tools/strace/tests/geteuid.c

## Purpose
Covers strace decoder coverage for `geteuid`. Source comments describe: Check decoding of geteuid syscall. Source read: 21 lines, 341 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: geteuid, __NR_geteuid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is geteuid, __NR_geteuid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/geteuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/geteuid32.c -->
# sources/test-tools/strace/tests/geteuid32.c

## Purpose
Covers strace self-test coverage for `geteuid32`. Source read: 27 lines, 374 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: geteuid32, __NR_geteuid32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is geteuid32, __NR_geteuid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/geteuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgid.c -->
# sources/test-tools/strace/tests/getgid.c

## Purpose
Covers strace self-test coverage for `getgid`. Source read: 27 lines, 425 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getgid, getxgid, __NR_getgid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getgid, getxgid, __NR_getgid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgid32.c -->
# sources/test-tools/strace/tests/getgid32.c

## Purpose
Covers strace self-test coverage for `getgid32`. Source read: 27 lines, 370 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getgid32, __NR_getgid32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getgid32, __NR_getgid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups.c -->
# sources/test-tools/strace/tests/getgroups.c

## Purpose
Covers strace decoder coverage for `getgroups`. Source comments describe: Check decoding of getgroups/getgroups32 syscalls. __NR_getgroups check how the first argument is decoded check how the second argument is decoded Source read: 104 lines, 2517 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: SYSCALL_NR, SYSCALL_NAME, GID_TYPE, MAX_STRLEN; C functions: get_groups, main; syscall names/numbers: getgroups32, getgroups, SYSCALL_NR.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is getgroups32, getgroups, SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups32.c -->
# sources/test-tools/strace/tests/getgroups32.c

## Purpose
Covers strace self-test coverage for `getgroups32`. Source read: 19 lines, 273 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getgroups.c"; defines: none; syscall names/numbers: getgroups32.

## Control Flow
primary syscall coverage is getgroups32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getgroups.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpeername.c -->
# sources/test-tools/strace/tests/getpeername.c

## Purpose
Covers strace decoder coverage for `getpeername`. Source comments describe: Check decoding of getpeername syscall. Source read: 43 lines, 913 bytes.

## Important APIs, Types, And Functions
includes/imports: "sockname.c"; defines: TEST_SYSCALL_NAME; C functions: main; syscall names/numbers: cfd; struct types: sockaddr_un.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is cfd.

## State And Persistence Behavior
creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on shared implementation `sockname.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpeername.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp--pidns-translation.c -->
# sources/test-tools/strace/tests/getpgrp--pidns-translation.c

## Purpose
Variant wrapper that includes `getpgrp.c` after defining `PIDNS_TRANSLATION`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "getpgrp.c"; defines: PIDNS_TRANSLATION.

## Control Flow
Preprocessor control flow only: define `PIDNS_TRANSLATION`, include `getpgrp.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getpgrp.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp.c -->
# sources/test-tools/strace/tests/getpgrp.c

## Purpose
Covers strace self-test coverage for `getpgrp`. Source read: 35 lines, 516 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getpgrp, __NR_getpgrp.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getpgrp, __NR_getpgrp.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpid--pidns-translation.c -->
# sources/test-tools/strace/tests/getpid--pidns-translation.c

## Purpose
Variant wrapper that includes `getpid.c` after defining `PIDNS_TRANSLATION`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "getpid.c"; defines: PIDNS_TRANSLATION.

## Control Flow
Preprocessor control flow only: define `PIDNS_TRANSLATION`, include `getpid.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getpid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpid--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpid.c -->
# sources/test-tools/strace/tests/getpid.c

## Purpose
Covers strace self-test coverage for `getpid`. Source read: 34 lines, 574 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getpid, getxpid, __NR_getpid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getpid, getxpid, __NR_getpid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getppid.c -->
# sources/test-tools/strace/tests/getppid.c

## Purpose
Covers strace decoder coverage for `getppid`. Source comments describe: Check decoding of getppid syscall. Source read: 22 lines, 373 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getppid, __NR_getppid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getppid, __NR_getppid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getppid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrandom.c -->
# sources/test-tools/strace/tests/getrandom.c

## Purpose
Covers strace decoder coverage for `getrandom`. Source comments describe: Check decoding of getrandom syscall. syscall/printf are in the inverted order to trigger tcache initialisation first see glibc-2.33.9000-879-gfc859c3. Source read: 47 lines, 1298 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getrandom, __NR_getrandom.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getrandom, __NR_getrandom.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresgid.c -->
# sources/test-tools/strace/tests/getresgid.c

## Purpose
Covers strace self-test coverage for `getresgid`. Source read: 28 lines, 474 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getresugid.c"; defines: SYSCALL_NR, SYSCALL_NAME, UGID_TYPE; syscall names/numbers: getresgid, getresgid32.

## Control Flow
primary syscall coverage is getresgid, getresgid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getresugid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresgid32.c -->
# sources/test-tools/strace/tests/getresgid32.c

## Purpose
Covers strace self-test coverage for `getresgid32`. Source read: 22 lines, 370 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getresugid.c"; defines: SYSCALL_NR, SYSCALL_NAME, UGID_TYPE; syscall names/numbers: getresgid32.

## Control Flow
primary syscall coverage is getresgid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getresugid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresgid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresugid.c -->
# sources/test-tools/strace/tests/getresugid.c

## Purpose
Covers strace decoder coverage for `getresuid`. Source comments describe: Check decoding of getresuid/getresgid/getresuid32/getresgid32 syscalls. Source read: 39 lines, 1054 bytes.

## Important APIs, Types, And Functions
includes/imports: <assert.h>, <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: SYSCALL_NR.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresugid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresuid.c -->
# sources/test-tools/strace/tests/getresuid.c

## Purpose
Covers strace self-test coverage for `getresuid`. Source read: 28 lines, 474 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getresugid.c"; defines: SYSCALL_NR, SYSCALL_NAME, UGID_TYPE; syscall names/numbers: getresuid, getresuid32.

## Control Flow
primary syscall coverage is getresuid, getresuid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getresugid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getresuid32.c -->
# sources/test-tools/strace/tests/getresuid32.c

## Purpose
Covers strace self-test coverage for `getresuid32`. Source read: 22 lines, 370 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getresugid.c"; defines: SYSCALL_NR, SYSCALL_NAME, UGID_TYPE; syscall names/numbers: getresuid32.

## Control Flow
primary syscall coverage is getresuid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getresugid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getresuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrlimit.c -->
# sources/test-tools/strace/tests/getrlimit.c

## Purpose
Covers strace self-test coverage for `getrlimit`. Source read: 21 lines, 342 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetrlimit.c"; defines: NR_GETRLIMIT, STR_GETRLIMIT; syscall names/numbers: getrlimit.

## Control Flow
primary syscall coverage is getrlimit.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xgetrlimit.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrusage.c -->
# sources/test-tools/strace/tests/getrusage.c

## Purpose
Covers strace decoder coverage for `getrusage`. Source comments describe: Check decoding of getrusage syscall. Source read: 73 lines, 2389 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <sys/resource.h>, <unistd.h>, <errno.h>, "kernel_rusage.h", "xlat.h", "xlat/usagewho.h"; defines: none; C functions: invoke_print, main; syscall names/numbers: getrusage, __NR_getrusage.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getrusage, __NR_getrusage.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getsid--pidns-translation.c -->
# sources/test-tools/strace/tests/getsid--pidns-translation.c

## Purpose
Variant wrapper that includes `getsid.c` after defining `PIDNS_TRANSLATION`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "getsid.c"; defines: PIDNS_TRANSLATION.

## Control Flow
Preprocessor control flow only: define `PIDNS_TRANSLATION`, include `getsid.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getsid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getsid--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getsid.c -->
# sources/test-tools/strace/tests/getsid.c

## Purpose
Covers strace self-test coverage for `getsid`. Source read: 27 lines, 461 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "pidns.h", <stdio.h>, <unistd.h>; defines: none; C functions: main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `pidns.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getsockname.c -->
# sources/test-tools/strace/tests/getsockname.c

## Purpose
Covers strace decoder coverage for `getsockname`. Source comments describe: Check decoding of getsockname syscall. Source read: 36 lines, 658 bytes.

## Important APIs, Types, And Functions
includes/imports: "sockname.c"; defines: TEST_SYSCALL_NAME; C functions: main; syscall names/numbers: lfd; struct types: sockaddr_un.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is lfd.

## State And Persistence Behavior
creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on shared implementation `sockname.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getsockname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gettid--pidns-translation.c -->
# sources/test-tools/strace/tests/gettid--pidns-translation.c

## Purpose
Variant wrapper that includes `gettid.c` after defining `PIDNS_TRANSLATION`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "gettid.c"; defines: PIDNS_TRANSLATION.

## Control Flow
Preprocessor control flow only: define `PIDNS_TRANSLATION`, include `gettid.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `gettid.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gettid--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gettid.c -->
# sources/test-tools/strace/tests/gettid.c

## Purpose
Covers strace self-test coverage for `gettid`. Source read: 25 lines, 436 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, "scno.h", "pidns.h"; defines: none; C functions: main; syscall names/numbers: gettid, __NR_gettid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is gettid, __NR_gettid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gettid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getuid.c -->
# sources/test-tools/strace/tests/getuid.c

## Purpose
Covers strace self-test coverage for `getuid`. Source read: 27 lines, 425 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getuid, getxuid, __NR_getuid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getuid, getxuid, __NR_getuid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getuid32.c -->
# sources/test-tools/strace/tests/getuid32.c

## Purpose
Covers strace self-test coverage for `getuid32`. Source read: 27 lines, 370 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getuid32, __NR_getuid32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getuid32, __NR_getuid32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-P.c -->
# sources/test-tools/strace/tests/getxattrat-P.c

## Purpose
Variant wrapper that includes `getxattrat.c` after defining `PATH_TRACING, SKIP_IF_PROC_IS_UNAVAILABLE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 4 lines, 120 bytes.

## Important APIs, Types, And Functions
includes/imports: "getxattrat.c"; defines: PATH_TRACING, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor control flow only: define `PATH_TRACING, SKIP_IF_PROC_IS_UNAVAILABLE`, include `getxattrat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `/proc/self/fd`, shared implementation `getxattrat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-y.c -->
# sources/test-tools/strace/tests/getxattrat-y.c

## Purpose
Variant wrapper that includes `getxattrat.c` after defining `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 4 lines, 129 bytes.

## Important APIs, Types, And Functions
includes/imports: "getxattrat.c"; defines: FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor control flow only: define `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`, include `getxattrat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `/proc/self/fd`, shared implementation `getxattrat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-yy.c -->
# sources/test-tools/strace/tests/getxattrat-yy.c

## Purpose
Variant wrapper that includes `getxattrat.c` after defining `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 4 lines, 139 bytes.

## Important APIs, Types, And Functions
includes/imports: "getxattrat.c"; defines: FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor control flow only: define `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`, include `getxattrat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `/proc/self/fd`, shared implementation `getxattrat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat.c -->
# sources/test-tools/strace/tests/getxattrat.c

## Purpose
Covers strace decoder coverage for `getxattrat`. Source comments describe: Check decoding of getxattrat syscall. size < XATTR_ARGS_SIZE_VER0 short read of struct xattr_args size > sizeof(struct xattr_args) XATTR_??? bytes %u..%u size > sizeof(struct xattr_args), short read XATTR_??? size == sizeof(struct xattr_args) AT_??? Source read: 310 lines, 8426 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xmalloc.h", <fcntl.h>, <stdio.h>, <unistd.h>, <linux/xattr.h>, "xlat/xattrat_flags.h"; defines: XLAT_MACROS_ONLY, XATTR_SIZE_MAX, XATTR_ARGS_SIZE_VER0, FD_PATH, YFLAG, SKIP_IF_PROC_IS_UNAVAILABLE; C functions: k_getxattrat, k_setxattrat, main; syscall names/numbers: getxattrat, setxattrat, __NR_getxattrat, __NR_setxattrat; struct types: xattr_args, strival32.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is getxattrat, setxattrat, __NR_getxattrat, __NR_setxattrat.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding; temporarily writes an extended attribute on the current directory to make a successful getxattrat value path observable.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xmalloc.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxgid.c -->
# sources/test-tools/strace/tests/getxgid.c

## Purpose
Covers strace self-test coverage for `getxgid`. Source read: 31 lines, 488 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getxgid, __NR_getxgid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getxgid, __NR_getxgid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxpid.c -->
# sources/test-tools/strace/tests/getxpid.c

## Purpose
Covers strace self-test coverage for `getxpid`. Source read: 34 lines, 581 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getxpid, __NR_getxpid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getxpid, __NR_getxpid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxuid.c -->
# sources/test-tools/strace/tests/getxuid.c

## Purpose
Covers strace self-test coverage for `getxuid`. Source read: 31 lines, 488 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getxuid, __NR_getxuid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getxuid, __NR_getxuid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/group_req.c -->
# sources/test-tools/strace/tests/group_req.c

## Purpose
Covers strace decoder coverage for `MCAST_JOIN_GROUP`. Source comments describe: Check decoding of MCAST_JOIN_GROUP/MCAST_LEAVE_GROUP. optlen < 0, EINVAL optlen < sizeof(struct group_req), EINVAL optval EFAULT classic optlen > sizeof(struct group_req), shortened Source read: 148 lines, 4172 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <net/if.h>, <netinet/in.h>, <limits.h>, <stdio.h>, <unistd.h>, <sys/socket.h>, <arpa/inet.h>; defines: multi4addr, multi6addr; C functions: set_opt, main; struct types: group_req, sockaddr_in, sockaddr_in6.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/group_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/hexdump_strdup.c -->
# sources/test-tools/strace/tests/hexdump_strdup.c

## Purpose
Covers strace self-test coverage for `hexdump_strdup`. Source comments describe: Make a hexdump copy of C string Source read: 45 lines, 853 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdlib.h>, <string.h>; defines: none; C functions: hexdump_memdup, hexdump_strdup.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/hexdump_strdup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/hexquote_strndup.c -->
# sources/test-tools/strace/tests/hexquote_strndup.c

## Purpose
Covers strace self-test coverage for `hexquote_strndup`. Source comments describe: Make a hexquoted copy of a string Source read: 37 lines, 746 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdlib.h>, <string.h>; defines: none; C functions: hexquote_strndup.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/hexquote_strndup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ifindex.c -->
# sources/test-tools/strace/tests/ifindex.c

## Purpose
Covers strace self-test coverage for `ifindex`. Source comments describe: Proxy wrappers for if_nametoindex. !HAVE_IF_INDEXTONAME Source read: 35 lines, 453 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <net/if.h>; defines: none; C functions: ifindex_lo.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ifindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inet-cmsg.c -->
# sources/test-tools/strace/tests/inet-cmsg.c

## Purpose
Covers strace self-test coverage for `inet-cmsg`. Source read: 176 lines, 4238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <fcntl.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/socket.h>, <netinet/in.h>, <arpa/inet.h>; defines: SETSOCKOPT; C functions: print_pktinfo, print_ttl, print_tos, print_opts, print_origdstaddr, main; struct types: cmsghdr, sockaddr_in, sockaddr, iovec, msghdr.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding; creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inet-cmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init-once.sh -->
# sources/test-tools/strace/tests/init-once.sh

## Purpose
Covers the shared strace test-shell framework loaded once by generated and handwritten tests. Source comments describe: # Copyright (c) 2011-2016 Dmitry V. Levin <ldv@strace.io> Copyright (c) 2011-2026 The strace developers. All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Starting with glibc 2.43, support for 2MB transparent huge pages has been enabled by default in malloc on AArch64. Disable it to avoid unexpected madvise() and close() invocations that. Source read: 1045 lines, 25142 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; shell functions: warn_, fail_, skip_, framework_failure_, framework_skip_, sed_re_escape, sed_slash_escape, get_prefix_value, sq_root, get_config_str, get_config_option, print_current_personality_designator, check_prog, dump_log_and_fail_with, run_prog, run_prog_skip_if_failed, try_run_prog, run_strace, run_strace_merge, check_gawk, match_awk, match_diff, match_grep, timing_quant_slack.

## Control Flow
Initializes common environment variables, defines skip/fail helpers, program checks, strace execution wrappers, diff/grep/AWK matchers, timing comparators, seccomp/kernel feature probes, and final per-test setup. It is meant to be sourced, not executed as an isolated test body.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `init.sh`, the built `strace` binary and test harness log/diff helpers. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization; timing/performance checks need tolerance for scheduler noise. Test signals: harness uses exact diff matching; harness uses regex/grep matching; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init-once.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init.sh -->
# sources/test-tools/strace/tests/init.sh

## Purpose
Covers the lightweight loader that sources the shared strace test framework once. Source comments describe: # Copyright (c) 2025 Dmitry V. Levin <ldv@strace.io> All rights reserved. # SPDX-License-Identifier: GPL-2.0-or-later Source read: 11 lines, 229 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
Guards on `TESTS_INIT_LOADED`; when not set, computes `srcdir`, sources `init-once.sh`, and prevents duplicate helper definition on later sourcing.

## State And Persistence Behavior
Shell state is process-local variables plus intentional output files such as generated scripts, logs, or expected-output artifacts managed by the strace test harness.

## Dependencies And Integration Points
Depends on `init-once.sh`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init_delete_module.h -->
# sources/test-tools/strace/tests/init_delete_module.h

## Purpose
Covers shared constants and declarations for `init_delete_module` tests. Source comments describe: Helper header containing common code for finit_module, init_module, and delete_module tests. !STRACE_TESTS_INIT_DELETE_MODULE_H Source read: 39 lines, 883 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdbool.h>, <stdio.h>; defines: STRACE_TESTS_INIT_DELETE_MODULE_H; C functions: print_str.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
No runtime state is owned here. The header contributes compile-time constants, declarations, or helper macros to including tests.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: module syscalls may be blocked by privileges, lockdown, or kernel configuration. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init_delete_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/init_module.c -->
# sources/test-tools/strace/tests/init_module.c

## Purpose
Covers strace decoder coverage for `init_module`. Source comments describe: Check decoding of init_module syscall. Source read: 87 lines, 2331 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "init_delete_module.h"; defines: none; C functions: main; syscall names/numbers: init_module, __NR_init_module.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is init_module, __NR_init_module.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; touches module-loading syscalls with invalid or synthetic payloads; durable kernel module state is not expected.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; module syscalls may be blocked by privileges, lockdown, or kernel configuration. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/init_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inject-nf.c -->
# sources/test-tools/strace/tests/inject-nf.c

## Purpose
Covers strace decoder coverage for `return`. Source comments describe: Check decoding of return values injected into a syscall that "never fails". No raw_syscall_0, let's use geteuid() and hope for the best. This prototype is intentionally different from the prototype provided by <unistd.h>. Source read: 64 lines, 1357 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <stdlib.h>, "scno.h", "raw_syscall.h"; defines: SC_NR, SC_NAME, INVOKE_SC; C functions: main; syscall names/numbers: geteuid32, geteuid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is geteuid32, geteuid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inject-nf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inode_of_sockfd.c -->
# sources/test-tools/strace/tests/inode_of_sockfd.c

## Purpose
Covers strace self-test coverage for `inode_of_sockfd`. Source comments describe: This file is part of strace test suite. Source read: 40 lines, 1014 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <limits.h>, <stdio.h>, <stdlib.h>, <string.h>, <unistd.h>; defines: none; C functions: inode_of_sockfd.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inode_of_sockfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify.c -->
# sources/test-tools/strace/tests/inotify.c

## Purpose
Covers strace decoder coverage for `inotify_add_watch`. Source comments describe: Check decoding of inotify_add_watch and inotify_rm_watch syscalls. Source read: 71 lines, 2041 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: inotify_add_watch, inotify_rm_watch, __NR_inotify_add_watch, __NR_inotify_rm_watch.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is inotify_add_watch, inotify_rm_watch, __NR_inotify_add_watch, __NR_inotify_rm_watch.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init-y.c -->
# sources/test-tools/strace/tests/inotify_init-y.c

## Purpose
Variant wrapper that includes `inotify_init.c` after defining `PRINT_PATHS`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "inotify_init.c"; defines: PRINT_PATHS.

## Control Flow
Preprocessor control flow only: define `PRINT_PATHS`, include `inotify_init.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `inotify_init.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init.c -->
# sources/test-tools/strace/tests/inotify_init.c

## Purpose
Covers strace decoder coverage for `inotify_init`. Source comments describe: Check decoding of inotify_init syscall. Source read: 48 lines, 740 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: inotify_init, __NR_inotify_init.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is inotify_init, __NR_inotify_init.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1-y.c -->
# sources/test-tools/strace/tests/inotify_init1-y.c

## Purpose
Variant wrapper that includes `inotify_init1.c` after defining `PRINT_PATHS`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "inotify_init1.c"; defines: PRINT_PATHS.

## Control Flow
Preprocessor control flow only: define `PRINT_PATHS`, include `inotify_init1.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `inotify_init1.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1.c -->
# sources/test-tools/strace/tests/inotify_init1.c

## Purpose
Covers strace decoder coverage for `inotify_init1`. Source comments describe: Check decoding of inotify_init1 syscall. IN_??? Kernels that do not have v2.6.33-rc1~34^2~7 do not have "anon_inode:" prefix. Let's assume that it can be either "inotify" or "anon_inode:inotify" for now, as any change there may be of interest. Source read: 107 lines, 2411 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_fcntl.h"; defines: all_flags, RC_FMT; C functions: main; syscall names/numbers: inotify_init1, __NR_inotify_init1.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is inotify_init1, __NR_inotify_init1.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inotify_init1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/int_0x80.c -->
# sources/test-tools/strace/tests/int_0x80.c

## Purpose
Covers strace decoder coverage for `int`. Source comments describe: Check decoding of int 0x80 on x86_64, x32, and x86. 200 is __NR_getgid32 on x86 and __NR_tkill on x86_64. Source read: 32 lines, 570 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getgid32, tkill.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getgid32, tkill.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/int_0x80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_enter.c -->
# sources/test-tools/strace/tests/io_uring_enter.c

## Purpose
Covers strace decoder coverage for `io_uring_enter`. Source comments describe: Check decoding of io_uring_enter syscall. Test IORING_ENTER_EXT_ARG Test IORING_ENTER_EXT_ARG_REG Source read: 121 lines, 3779 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "kernel_timespec.h", "scno.h", <fcntl.h>, <signal.h>, <stdio.h>, <string.h>, <unistd.h>, "kernel_time_types.h", <linux/io_uring.h>; defines: UAPI_LINUX_IO_URING_H_SKIP_LINUX_TIME_TYPES_H; C functions: sys_io_uring_enter, main; syscall names/numbers: io_uring_enter, __NR_io_uring_enter; struct types: io_uring_getevents_arg, io_uring_reg_wait.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is io_uring_enter, __NR_io_uring_enter.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timespec.h`, Linux UAPI headers, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_enter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xabbrev.c -->
# sources/test-tools/strace/tests/io_uring_register-Xabbrev.c

## Purpose
Variant wrapper that includes `io_uring_register.c` after defining `XLAT_ABBREV`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 53 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register.c"; defines: XLAT_ABBREV.

## Control Flow
Preprocessor control flow only: define `XLAT_ABBREV`, include `io_uring_register.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xraw.c -->
# sources/test-tools/strace/tests/io_uring_register-Xraw.c

## Purpose
Variant wrapper that includes `io_uring_register.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 50 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `io_uring_register.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xverbose.c -->
# sources/test-tools/strace/tests/io_uring_register-Xverbose.c

## Purpose
Variant wrapper that includes `io_uring_register.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 54 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `io_uring_register.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xabbrev.c -->
# sources/test-tools/strace/tests/io_uring_register-success-Xabbrev.c

## Purpose
Variant wrapper that includes `io_uring_register-success.c` after defining `XLAT_ABBREV`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 61 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register-success.c"; defines: XLAT_ABBREV.

## Control Flow
Preprocessor control flow only: define `XLAT_ABBREV`, include `io_uring_register-success.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register-success.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xraw.c -->
# sources/test-tools/strace/tests/io_uring_register-success-Xraw.c

## Purpose
Variant wrapper that includes `io_uring_register-success.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 58 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register-success.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `io_uring_register-success.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register-success.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xverbose.c -->
# sources/test-tools/strace/tests/io_uring_register-success-Xverbose.c

## Purpose
Variant wrapper that includes `io_uring_register-success.c` after defining `XLAT_VERBOSE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 62 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register-success.c"; defines: XLAT_VERBOSE.

## Control Flow
Preprocessor control flow only: define `XLAT_VERBOSE`, include `io_uring_register-success.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register-success.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success.c -->
# sources/test-tools/strace/tests/io_uring_register-success.c

## Purpose
Variant wrapper that includes `io_uring_register.c` after defining `RETVAL_INJECTED`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 57 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register.c"; defines: RETVAL_INJECTED.

## Control Flow
Preprocessor control flow only: define `RETVAL_INJECTED`, include `io_uring_register.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success.c -->
