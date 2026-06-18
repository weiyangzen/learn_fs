# subset-b-009356 research

Grouped research report for strace tests under `sources/test-tools/strace/tests`. Every section below preserves the exact source path in its title and reconciliation delimiters, and was generated after complete reads of the listed source files. The set covers ptrace, quota, read/write, socket receive, xattr, signal, scheduler, personality, and s390/RISC-V syscall decoder tests.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace.c -->
# sources/test-tools/strace/tests/ptrace.c

## Purpose

This is the broad ptrace decoder exerciser. It drives `__NR_ptrace` through request/value combinations including register access, regset access, signal-info decoding, peeksiginfo, compat request handling, and architecture-specific ptrace requests so strace output can be compared against the test program's generated expectations. Source read: complete file, 2335 lines, 67297 bytes, sha256 `04e1138214c9f3be`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"print_fields.h"`, `<errno.h>`, `"ptrace.h"`, `<inttypes.h>`, `<fcntl.h>`, `<signal.h>`, `<stdint.h>`, `<stdio.h>`, `<string.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`. Compile-time macros: `XLAT_MACROS_ONLY`, `NULL_FD`, `NULL_STR`. Functions/helpers: `check_compat_ptrace_req`, `do_getfpregs_setfpregs`, `do_getregs64_setregs64`, `do_getregs_setregs`, `do_getregset_setregset`, `do_ptrace`, `do_ptrace_regs`, `main`, `print_fpregset`, `print_prstatus_regset`, `print_pt_fpregs`, `print_pt_regs`, `print_pt_regs64`, `test_compat_ptrace`, `test_getregset_setregset`, `test_peeksiginfo`. Direct syscall numbers: `__NR_gettid`, `__NR_ptrace`, `__NR_read`. Notable constants/xlats: `AUDIT_ARCH_`, `AUDIT_ARCH_X86_64`, `PTRACE_`, `PTRACE_ATTACH`, `PTRACE_CONT`, `PTRACE_DETACH`, `PTRACE_GETEVENTMSG`, `PTRACE_GETFPREGS`, `PTRACE_GETREGS`, `PTRACE_GETREGS64`, `PTRACE_GETREGSET`, `PTRACE_GETSIGINFO`, `PTRACE_GETSIGMASK`, `PTRACE_INTERRUPT`, `PTRACE_KILL`, `PTRACE_LISTEN`, `PTRACE_O_TRACECLONE`, `PTRACE_O_TRACEFORK`, `PTRACE_O_TRACESYSGOOD`, `PTRACE_PEEKDATA`.

## Control Flow

The test first probes simple invalid/current-process ptrace calls, then forks a tracee, coordinates `PTRACE_TRACEME`, signal stops, `waitpid`, and ptrace request execution. Helper families print expected request names, pointer arguments, register structs, `iovec`/regset content, `siginfo_t` fields, and errno strings. Large conditional blocks compile only when the architecture exposes the corresponding ptrace structures or constants.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_gettid`, `__NR_ptrace`, `__NR_read`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risks are architecture drift in register layouts, optional `siginfo_t` fields, ptrace request availability, and kernel behavior differences around compat tracing. The test intentionally uses invalid addresses and request numbers, so expected output must distinguish decoder fallback from syscall failure.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xabbrev.c -->
# sources/test-tools/strace/tests/ptrace_set_syscall_info-Xabbrev.c

## Purpose

This is a thin compile-time wrapper around `ptrace_set_syscall_info.c`. Its local purpose is to rebuild the shared test body in abbreviated xlat mode, so expected output favors symbolic names without verbose numeric expansion. Source read: complete file, 2 lines, 59 bytes, sha256 `6f353d02cca530d1`.

## Important APIs, Types, and Functions

Includes: `"ptrace_set_syscall_info.c"`. Compile-time macros: `XLAT_ABBREV`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_ABBREV` and then includes `ptrace_set_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xraw.c -->
# sources/test-tools/strace/tests/ptrace_set_syscall_info-Xraw.c

## Purpose

This is a thin compile-time wrapper around `ptrace_set_syscall_info.c`. Its local purpose is to rebuild the shared test body in raw xlat mode, so symbolic constants are expected as numeric values where the shared body uses xlat formatting. Source read: complete file, 2 lines, 56 bytes, sha256 `9caaa38e56c06cea`.

## Important APIs, Types, and Functions

Includes: `"ptrace_set_syscall_info.c"`. Compile-time macros: `XLAT_RAW`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_RAW` and then includes `ptrace_set_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xverbose.c -->
# sources/test-tools/strace/tests/ptrace_set_syscall_info-Xverbose.c

## Purpose

This is a thin compile-time wrapper around `ptrace_set_syscall_info.c`. Its local purpose is to rebuild the shared test body in verbose xlat mode, so expected output includes numeric values plus symbolic comments/details. Source read: complete file, 2 lines, 60 bytes, sha256 `475c91e8ac204791`.

## Important APIs, Types, and Functions

Includes: `"ptrace_set_syscall_info.c"`. Compile-time macros: `XLAT_VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_VERBOSE` and then includes `ptrace_set_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info.c -->
# sources/test-tools/strace/tests/ptrace_set_syscall_info.c

## Purpose

This test verifies strace decoding of the `PTRACE_SET_SYSCALL_INFO` request, including deliberately partial user buffers. Source read: complete file, 318 lines, 8429 bytes, sha256 `2479444aed6df008`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"ptrace.h"`, `"scno.h"`, `<errno.h>`, `<stddef.h>`, `<stdio.h>`, `<string.h>`, `<signal.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`, `"cur_audit_arch.h"`, `"xlat.h"`. Compile-time macros: `XLAT_MACROS_ONLY`, `OOB`, `OOE`. Functions/helpers: `main`, `ptrace_set_syscall_info`, `test_entry`, `test_exit`, `test_none`. Direct syscall numbers: `__NR_gettid`, `__NR_ptrace`. Notable constants/xlats: `AUDIT_ARCH_`, `AUDIT_ARCH_CRIS`, `PTRACE_SET_SYSCALL_INFO`, `PTRACE_SYSCALL_INFO_`, `PTRACE_SYSCALL_INFO_ENTRY`, `PTRACE_SYSCALL_INFO_EXIT`, `PTRACE_SYSCALL_INFO_NONE`, `PTRACE_SYSCALL_INFO_SECCOMP`.

## Control Flow

It allocates a tail-page buffer, fills `struct_ptrace_syscall_info` with known bytes, then loops over buffer sizes and value tables for op, audit arch, syscall numbers, seccomp ret data, and exit status. Each call prints the expected decoded form for present fields only.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_gettid`, `__NR_ptrace`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The test is sensitive to `struct_ptrace_syscall_info` layout, xlat rendering mode, and kernel availability of the synthetic ptrace request.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xabbrev.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info-Xabbrev.c

## Purpose

This is a thin compile-time wrapper around `ptrace_syscall_info.c`. Its local purpose is to rebuild the shared test body in abbreviated xlat mode, so expected output favors symbolic names without verbose numeric expansion. Source read: complete file, 2 lines, 55 bytes, sha256 `10aa3744073c67f7`.

## Important APIs, Types, and Functions

Includes: `"ptrace_syscall_info.c"`. Compile-time macros: `XLAT_ABBREV`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_ABBREV` and then includes `ptrace_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c

## Purpose

This is a thin compile-time wrapper around `ptrace_syscall_info.c`. Its local purpose is to rebuild the shared test body in raw xlat mode, so symbolic constants are expected as numeric values where the shared body uses xlat formatting. Source read: complete file, 2 lines, 52 bytes, sha256 `345fa34ccaf99349`.

## Important APIs, Types, and Functions

Includes: `"ptrace_syscall_info.c"`. Compile-time macros: `XLAT_RAW`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_RAW` and then includes `ptrace_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xverbose.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info-Xverbose.c

## Purpose

This is a thin compile-time wrapper around `ptrace_syscall_info.c`. Its local purpose is to rebuild the shared test body in verbose xlat mode, so expected output includes numeric values plus symbolic comments/details. Source read: complete file, 2 lines, 56 bytes, sha256 `f3b8e60ef9c4810a`.

## Important APIs, Types, and Functions

Includes: `"ptrace_syscall_info.c"`. Compile-time macros: `XLAT_VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_VERBOSE` and then includes `ptrace_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info.c

## Purpose

This test verifies strace decoding of `PTRACE_GET_SYSCALL_INFO` across none, syscall-entry, and syscall-exit stops. Source read: complete file, 473 lines, 12790 bytes, sha256 `1a683c8010a65328`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"ptrace.h"`, `"scno.h"`, `<errno.h>`, `<stddef.h>`, `<stdio.h>`, `<string.h>`, `<signal.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`, `"xlat.h"`, `"xlat/audit_arch.h"`. Compile-time macros: `XLAT_MACROS_ONLY`, `FAIL`, `PFAIL`. Functions/helpers: `do_ptrace`, `kill_tracee`, `main`, `test_entry`, `test_exit`, `test_none`. Direct syscall numbers: `__NR_chdir`, `__NR_exit_group`, `__NR_gettid`, `__NR_ptrace`. Notable constants/xlats: `AUDIT_ARCH_`, `PTRACE_GET_SYSCALL_INFO`, `PTRACE_O_TRACESYSGOOD`, `PTRACE_SETOPTIONS`, `PTRACE_SYSCALL`, `PTRACE_SYSCALL_INFO_ENTRY`, `PTRACE_SYSCALL_INFO_EXIT`, `PTRACE_SYSCALL_INFO_NONE`, `PTRACE_TRACEME`, `SIGKILL`, `SIGSTOP`, `SIGTRAP`.

## Control Flow

It forks a tracee, enables `PTRACE_O_TRACESYSGOOD`, steps through `chdir`, `gettid`, and `exit_group` with `PTRACE_SYSCALL`, and for every stop reads `struct_ptrace_syscall_info` with sizes from 0 through the full struct size. The expected line printer checks op, audit arch, instruction and stack pointers, syscall numbers, argument arrays, return values, and `is_error`.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_chdir`, `__NR_exit_group`, `__NR_gettid`, `__NR_ptrace`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Kernel support for `PTRACE_GET_SYSCALL_INFO`, syscall-stop sequencing, audit-arch values, and struct-size changes are the key compatibility risks.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pwritev.c -->
# sources/test-tools/strace/tests/pwritev.c

## Purpose

`sources/test-tools/strace/tests/pwritev.c` validates `pwritev` iovec and offset decoding, including multiple vector entries and invalid pointer handling in the strace tests tree. Source read: complete file, 131 lines, 2737 bytes, sha256 `05c80f422ccbb921`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`. Compile-time macros: none found. Functions/helpers: `main`, `print_iov`, `print_iovec`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main`, `print_iov`, `print_iovec` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pwritev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_fault.c -->
# sources/test-tools/strace/tests/qual_fault.c

## Purpose

`sources/test-tools/strace/tests/qual_fault.c` checks strace fault injection across traced syscalls and child process behavior in the strace tests tree. Source read: complete file, 193 lines, 3925 bytes, sha256 `1f86fab06957454c`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<errno.h>`, `<fcntl.h>`, `<limits.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<unistd.h>`, `<sys/stat.h>`, `<sys/uio.h>`, `<sys/wait.h>`. Compile-time macros: `DEFAULT_ERRNO`. Functions/helpers: `invoke`, `main`, `open_file`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `invoke`, `main`, `open_file` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-error-signal.c -->
# sources/test-tools/strace/tests/qual_inject-error-signal.c

## Purpose

`sources/test-tools/strace/tests/qual_inject-error-signal.c` checks combined errno and signal injection qualification in the strace tests tree. Source read: complete file, 50 lines, 1025 bytes, sha256 `dfbbde1ab64f28ec`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<unistd.h>`, `<sys/stat.h>`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `handler`, `main`. Direct syscall numbers: `__NR_chdir`, `__NR_exit_group`. Notable constants/xlats: `SIGUSR1`, `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_chdir`, `__NR_exit_group` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_chdir`, `__NR_exit_group`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-error-signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-retval.c -->
# sources/test-tools/strace/tests/qual_inject-retval.c

## Purpose

`sources/test-tools/strace/tests/qual_inject-retval.c` checks success-return injection qualification in the strace tests tree. Source read: complete file, 46 lines, 961 bytes, sha256 `5cda970b57841e24`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/stat.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_chdir`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_chdir` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_chdir`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-retval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-signal.c -->
# sources/test-tools/strace/tests/qual_inject-signal.c

## Purpose

`sources/test-tools/strace/tests/qual_inject-signal.c` checks signal injection qualification in the strace tests tree. Source read: complete file, 38 lines, 747 bytes, sha256 `cf3976e5c257925f`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<unistd.h>`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `handler`, `main`. Direct syscall numbers: `__NR_chdir`, `__NR_exit_group`. Notable constants/xlats: `SIGUSR1`, `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_chdir`, `__NR_exit_group` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_chdir`, `__NR_exit_group`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_signal.c -->
# sources/test-tools/strace/tests/qual_signal.c

## Purpose

`sources/test-tools/strace/tests/qual_signal.c` checks `-e signal=set` signal filtering behavior in the strace tests tree. Source read: complete file, 61 lines, 1148 bytes, sha256 `8fa0549ae644fee5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<signal.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `handler`, `main`, `test_sig`. Direct syscall numbers: none found. Notable constants/xlats: `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main`, `test_sig` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality.sh -->
# sources/test-tools/strace/tests/qualify_personality.sh

## Purpose

`sources/test-tools/strace/tests/qualify_personality.sh` is shared shell logic for per-personality `-e trace=...@personality` tests in the strace tests tree. Source read: complete file, 52 lines, 1157 bytes, sha256 `d6969d709264cba3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, validates a requested personality designator, computes supported personalities from `STRACE_NATIVE_ARCH`, resets `NAME` to an empty fixture for non-current personalities, and calls `test_trace_expr` with `trace_expr@personality`.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_all.sh -->
# sources/test-tools/strace/tests/qualify_personality_all.sh

## Purpose

`sources/test-tools/strace/tests/qualify_personality_all.sh` is shared shell logic for `--trace=all@personality` qualification tests in the strace tests tree. Source read: complete file, 91 lines, 1940 bytes, sha256 `2da01f17734d21e3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, validates a target personality, skips unsupported or all-matching cases, and for native-personality all-trace checks iterates `pure_executables.list`, running each program under strace and asserting that only the expected execve line appears.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_empty.in -->
# sources/test-tools/strace/tests/qualify_personality_empty.in

## Purpose

`sources/test-tools/strace/tests/qualify_personality_empty.in` is an intentionally empty fixture used when a non-current personality should produce no syscall matches in the strace tests tree. Source read: complete file, 0 lines, 0 bytes, sha256 `e3b0c44298fc1c14`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

There is no executable control flow. The harness reads each non-comment row as a test selector or option line and feeds it into the surrounding shell/test runner.

## State and Persistence Behavior

The file is static fixture data and stores no runtime state. Its only persistence effect is the checked-in input rows consumed by the test harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks are malformed rows, stale test names, or option changes that cause the harness to run the wrong executable or argument-count mode.

## Test Signals

Test signals are the harness accepting the fixture rows, invoking the referenced tests with the listed options, and producing no unexpected extra trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_empty.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xabbrev.c -->
# sources/test-tools/strace/tests/quotactl-Xabbrev.c

## Purpose

This is a thin compile-time wrapper around `quotactl.c`. Its local purpose is to rebuild the shared test body in default mode with no local behavior override. Source read: complete file, 1 lines, 22 bytes, sha256 `374453cbc116a2a0`.

## Important APIs, Types, and Functions

Includes: `"quotactl.c"`. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines no local macros and then includes `quotactl.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xraw.c -->
# sources/test-tools/strace/tests/quotactl-Xraw.c

## Purpose

This is a thin compile-time wrapper around `quotactl.c`. Its local purpose is to rebuild the shared test body in raw xlat mode, so symbolic constants are expected as numeric values where the shared body uses xlat formatting. Source read: complete file, 2 lines, 41 bytes, sha256 `68b9b56df2604e95`.

## Important APIs, Types, and Functions

Includes: `"quotactl.c"`. Compile-time macros: `XLAT_RAW`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_RAW` and then includes `quotactl.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xverbose.c -->
# sources/test-tools/strace/tests/quotactl-Xverbose.c

## Purpose

This is a thin compile-time wrapper around `quotactl.c`. Its local purpose is to rebuild the shared test body in verbose xlat mode, so expected output includes numeric values plus symbolic comments/details. Source read: complete file, 2 lines, 45 bytes, sha256 `2fcd3f4cf65ded71`.

## Important APIs, Types, and Functions

Includes: `"quotactl.c"`. Compile-time macros: `XLAT_VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_VERBOSE` and then includes `quotactl.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success-v.c -->
# sources/test-tools/strace/tests/quotactl-success-v.c

## Purpose

This is a thin compile-time wrapper around `quotactl-v.c`. Its local purpose is to rebuild the shared test body in success-injection mode, usually forcing a synthetic successful return value. Source read: complete file, 2 lines, 49 bytes, sha256 `fad8685117b78987`.

## Important APIs, Types, and Functions

Includes: `"quotactl-v.c"`. Compile-time macros: `INJECT_RETVAL`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `INJECT_RETVAL` and then includes `quotactl-v.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; syscall retval injection producing the synthetic success path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success.c -->
# sources/test-tools/strace/tests/quotactl-success.c

## Purpose

This is a thin compile-time wrapper around `quotactl.c`. Its local purpose is to rebuild the shared test body in success-injection mode, usually forcing a synthetic successful return value. Source read: complete file, 2 lines, 47 bytes, sha256 `e28dc515893ad58c`.

## Important APIs, Types, and Functions

Includes: `"quotactl.c"`. Compile-time macros: `INJECT_RETVAL`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `INJECT_RETVAL` and then includes `quotactl.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; syscall retval injection producing the synthetic success path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-v.c -->
# sources/test-tools/strace/tests/quotactl-v.c

## Purpose

This is a thin compile-time wrapper around `quotactl.c`. Its local purpose is to rebuild the shared test body in verbose structure-printing mode for the included shared test body. Source read: complete file, 3 lines, 91 bytes, sha256 `2fd50624fd2ad512`.

## Important APIs, Types, and Functions

Includes: `"quotactl.c"`. Compile-time macros: `VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `VERBOSE` and then includes `quotactl.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-success-v.c -->
# sources/test-tools/strace/tests/quotactl-xfs-success-v.c

## Purpose

This is a thin compile-time wrapper around `quotactl-xfs-v.c`. Its local purpose is to rebuild the shared test body in success-injection mode, usually forcing a synthetic successful return value. Source read: complete file, 2 lines, 53 bytes, sha256 `fdb09f23edfc94ce`.

## Important APIs, Types, and Functions

Includes: `"quotactl-xfs-v.c"`. Compile-time macros: `INJECT_RETVAL`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `INJECT_RETVAL` and then includes `quotactl-xfs-v.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; syscall retval injection producing the synthetic success path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-success.c -->
# sources/test-tools/strace/tests/quotactl-xfs-success.c

## Purpose

This is a thin compile-time wrapper around `quotactl-xfs.c`. Its local purpose is to rebuild the shared test body in success-injection mode, usually forcing a synthetic successful return value. Source read: complete file, 2 lines, 51 bytes, sha256 `0fe69be8c006dc1c`.

## Important APIs, Types, and Functions

Includes: `"quotactl-xfs.c"`. Compile-time macros: `INJECT_RETVAL`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `INJECT_RETVAL` and then includes `quotactl-xfs.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; syscall retval injection producing the synthetic success path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-v.c -->
# sources/test-tools/strace/tests/quotactl-xfs-v.c

## Purpose

This is a thin compile-time wrapper around `quotactl-xfs.c`. Its local purpose is to rebuild the shared test body in verbose structure-printing mode for the included shared test body. Source read: complete file, 3 lines, 99 bytes, sha256 `cb39fb8f3252f140`.

## Important APIs, Types, and Functions

Includes: `"quotactl-xfs.c"`. Compile-time macros: `VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `VERBOSE` and then includes `quotactl-xfs.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs.c -->
# sources/test-tools/strace/tests/quotactl-xfs.c

## Purpose

This is the XFS quota `quotactl` decoder test. It targets XFS-specific subcommands and structures from `linux/dqblk_xfs.h`. Source read: complete file, 344 lines, 8808 bytes, sha256 `6efc5d76600bc42e`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `<linux/dqblk_xfs.h>`, `"quotactl.h"`, `"xlat.h"`, `"xlat/xfs_dqblk_flags.h"`. Compile-time macros: none found. Functions/helpers: `main`, `print_xdisk_quota`, `print_xquota_stat`, `print_xquota_statv`. Direct syscall numbers: none found. Notable constants/xlats: `QCMD`, `QCMD_TYPE`, `Q_XGETNEXTQUOTA`, `Q_XGETQSTAT`, `Q_XGETQSTATV`, `Q_XGETQUOTA`, `Q_XQUOTAOFF`, `Q_XQUOTAON`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XSETQLIM`.

## Control Flow

The test prints XFS disk quota, quota stat, and quota statv structures, then exercises XFS quota command variants through the common `check_quota` helper. `VERBOSE` builds include full structure payloads; success-injection wrappers force successful return formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; shared quota test helper `quotactl.h`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

XFS quota struct shape, flag xlat tables, and verbose/non-verbose differences are the main sources of expected-output drift.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.c -->
# sources/test-tools/strace/tests/quotactl.c

## Purpose

This is the Linux quota `quotactl` syscall decoder test. It exercises command composition, quota ids, device pointers, quota format values, and the structures returned by or passed to common quota commands. Source read: complete file, 390 lines, 9773 bytes, sha256 `2f7699325849049e`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<inttypes.h>`, `<stdint.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `"quotactl.h"`, `"xlat.h"`, `"xlat/quota_formats.h"`, `"xlat/if_dqblk_valid.h"`, `"xlat/if_dqinfo_flags.h"`, `"xlat/if_dqinfo_valid.h"`. Compile-time macros: `QUOTA_STR`, `QUOTA_ID_STR`, `QUOTA_STR_INVALID`. Functions/helpers: `gen_quotacmd`, `gen_quotaid`, `main`, `print_dqblk`, `print_dqfmt`, `print_dqinfo`, `print_nextdqblk`. Direct syscall numbers: none found. Notable constants/xlats: `QCMD`, `QCMD_CMD`, `QCMD_TYPE`, `Q_`, `Q_GETFMT`, `Q_GETINFO`, `Q_GETNEXTQUOTA`, `Q_GETQUOTA`, `Q_QUOTAOFF`, `Q_QUOTAON`, `Q_SETINFO`, `Q_SETQUOTA`, `Q_SYNC`.

## Control Flow

Helper functions generate human-readable `QCMD` and quota-id strings, print `if_dqblk`, `if_dqinfo`, `if_nextdqblk`, and quota-format payloads, and `main` calls shared `check_quota` cases from `quotactl.h` across valid, invalid, NULL, unterminated, verbose, raw, and injected-success scenarios.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; shared quota test helper `quotactl.h`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Quota command bit packing, host-header xlat availability, struct-field formatting, and injected-success behavior can all change expected traces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.h -->
# sources/test-tools/strace/tests/quotactl.h

## Purpose

This header centralizes shared Linux and XFS quota test machinery for `quotactl`-family tests. Source read: complete file, 204 lines, 7018 bytes, sha256 `6b99f8bbb23cf567`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: `check_quota`. Direct syscall numbers: `__NR_quotactl`. Notable constants/xlats: `QCMD_CMD`, `QCMD_TYPE`.

## Control Flow

`check_quota` performs the direct `__NR_quotactl` syscall with command, id, device, and address arguments, captures `sprintrc`, and prints the expected trace line. It supports flag combinations controlling whether command bits, ids, device strings, addresses, and output strings are printed as raw, xlat, or verbose forms.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

kernel syscall availability for `__NR_quotactl`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Because this header owns the shared expected-line contract, mistakes here would affect every quota wrapper in this subset.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd-P.c -->
# sources/test-tools/strace/tests/quotactl_fd-P.c

## Purpose

This is a thin compile-time wrapper around `quotactl_fd.c`. Its local purpose is to rebuild the shared test body in path-tracing mode for descriptor/path qualification. Source read: complete file, 4 lines, 121 bytes, sha256 `ab091beead74c3bc`.

## Important APIs, Types, and Functions

Includes: `"quotactl_fd.c"`. Compile-time macros: `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `quotactl_fd.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd-y.c -->
# sources/test-tools/strace/tests/quotactl_fd-y.c

## Purpose

This is a thin compile-time wrapper around `quotactl_fd.c`. Its local purpose is to rebuild the shared test body in fd-decoding mode for descriptor qualification. Source read: complete file, 4 lines, 121 bytes, sha256 `4cefcc29ed669cba`.

## Important APIs, Types, and Functions

Includes: `"quotactl_fd.c"`. Compile-time macros: `DECODE_FDS`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `DECODE_FDS`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `quotactl_fd.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd.c -->
# sources/test-tools/strace/tests/quotactl_fd.c

## Purpose

This test covers the newer `quotactl_fd` syscall, including descriptor/path rendering variants. Source read: complete file, 84 lines, 1972 bytes, sha256 `8c0bb3d585e534af`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"xmalloc.h"`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<linux/quota.h>`, `"xlat.h"`, `"xlat/quota_formats.h"`. Compile-time macros: none found. Functions/helpers: `k_quotactl_fd`, `main`. Direct syscall numbers: `__NR_quotactl_fd`. Notable constants/xlats: `QCMD`, `Q_GETFMT`.

## Control Flow

It opens candidate files, invokes `__NR_quotactl_fd` through `k_quotactl_fd`, and prints expected command, file descriptor, quota id, format, and errno output. `-P` and `-y` wrappers enable path tracing or fd decoding and require `/proc/self/fd`.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_quotactl_fd`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

`quotactl_fd` availability, `/proc` fd symlink availability, and descriptor decoding mode can alter expected traces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/read-write.c -->
# sources/test-tools/strace/tests/read-write.c

## Purpose

This test validates read/write syscall decoding and byte dumping behavior. Source read: complete file, 294 lines, 7093 bytes, sha256 `124a05ab32ae0326`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `dump_str`, `dump_str_ex`, `k_read`, `k_write`, `main`, `print_hex`, `test_dump`. Direct syscall numbers: `__NR_read`, `__NR_write`. Notable constants/xlats: none found.

## Control Flow

It uses direct `__NR_read`/`__NR_write`, helper printers for hex/escaped strings, and fixture data to check normal strings, truncated dump output, failed reads/writes, and printable/non-printable byte formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_read`, `__NR_write`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Dump length options, string escaping, partial read/write behavior, and fd availability are the key regression surfaces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/read-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readahead.c -->
# sources/test-tools/strace/tests/readahead.c

## Purpose

`sources/test-tools/strace/tests/readahead.c` checks `readahead` syscall argument formatting for fd, offset, and count values in the strace tests tree. Source read: complete file, 85 lines, 1706 bytes, sha256 `bcd1a2250385edbc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readdir.c -->
# sources/test-tools/strace/tests/readdir.c

## Purpose

`sources/test-tools/strace/tests/readdir.c` checks legacy `readdir` syscall decoding and directory-entry pointer/count rendering in the strace tests tree. Source read: complete file, 81 lines, 2298 bytes, sha256 `fb81f1ca7c13e2b4`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_readdir`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_readdir` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_readdir`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readlink.c -->
# sources/test-tools/strace/tests/readlink.c

## Purpose

`sources/test-tools/strace/tests/readlink.c` checks `readlink` path, buffer, and size decoding using direct syscall invocations in the strace tests tree. Source read: complete file, 62 lines, 1366 bytes, sha256 `471cd719b44f01cb`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_readlink`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_readlink` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_readlink`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readlinkat.c -->
# sources/test-tools/strace/tests/readlinkat.c

## Purpose

`sources/test-tools/strace/tests/readlinkat.c` checks `readlinkat` path, dirfd, buffer, and size decoding with a generated symlink fixture in the strace tests tree. Source read: complete file, 56 lines, 1374 bytes, sha256 `677d94a5b79b7252`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: `PREFIX`, `TARGET`, `LINKPATH`. Functions/helpers: `main`. Direct syscall numbers: `__NR_readlinkat`. Notable constants/xlats: `AT_FDCWD`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_readlinkat` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

The test creates/removes temporary pathnames for a target and symlink, but it does not persist data beyond the harness run.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_readlinkat`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readv.c -->
# sources/test-tools/strace/tests/readv.c

## Purpose

`sources/test-tools/strace/tests/readv.c` validates `readv` and `writev` iovec decoding, including short buffers, invalid vectors, and string rendering in the strace tests tree. Source read: complete file, 138 lines, 3673 bytes, sha256 `957a124f6209dea3`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<stdio.h>`, `<unistd.h>`, `<sys/uio.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/reboot.c -->
# sources/test-tools/strace/tests/reboot.c

## Purpose

`sources/test-tools/strace/tests/reboot.c` checks `reboot` magic, command, and argument decoding, including invalid magic/cmd fallback in the strace tests tree. Source read: complete file, 100 lines, 3515 bytes, sha256 `59691a65de166230`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<linux/reboot.h>`, `<unistd.h>`. Compile-time macros: `INVALID_MAGIC`, `INVALID_CMD`, `STR32`, `STR128`. Functions/helpers: `main`. Direct syscall numbers: `__NR_reboot`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_reboot` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_reboot`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recv-MSG_TRUNC.c -->
# sources/test-tools/strace/tests/recv-MSG_TRUNC.c

## Purpose

`sources/test-tools/strace/tests/recv-MSG_TRUNC.c` checks `recv` behavior and output formatting when `MSG_TRUNC` is involved in the strace tests tree. Source read: complete file, 59 lines, 1391 bytes, sha256 `66102600c342fc04`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<errno.h>`, `<stdio.h>`, `<sys/socket.h>`, `"scno.h"`. Compile-time macros: `SC_recv`. Functions/helpers: `main`, `sys_recv`. Direct syscall numbers: `__NR_recv`. Notable constants/xlats: `MSG_PEEK`, `MSG_TRUNC`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_recv` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main`, `sys_recv` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_recv`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recv-MSG_TRUNC.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c -->
# sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c

## Purpose

`sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c` checks `recvfrom` buffer and sockaddr output with `MSG_TRUNC` in the strace tests tree. Source read: complete file, 42 lines, 1145 bytes, sha256 `29b4aef83fdb02dc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<stdio.h>`, `<sys/socket.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `MSG_PEEK`, `MSG_TRUNC`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom.c -->
# sources/test-tools/strace/tests/recvfrom.c

## Purpose

`sources/test-tools/strace/tests/recvfrom.c` checks sockaddr-related argument decoding for `recvfrom` through the shared socket-name test body in the strace tests tree. Source read: complete file, 69 lines, 1484 bytes, sha256 `04dd719f256bc34e`.

## Important APIs, Types, and Functions

Includes: `"sockname.c"`. Compile-time macros: `TEST_SYSCALL_NAME`, `TEST_SYSCALL_PREPARE`, `PREFIX_S_ARGS`, `PREFIX_S_STR`, `PREFIX_F_ARGS`, `PREFIX_F_STR`. Functions/helpers: `main`, `send_un`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main`, `send_un` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the shared socket-name test body. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recvmmsg-timeout.c -->
# sources/test-tools/strace/tests/recvmmsg-timeout.c

## Purpose

`sources/test-tools/strace/tests/recvmmsg-timeout.c` checks `recvmmsg` timeout pointer and timespec formatting in the strace tests tree. Source read: complete file, 70 lines, 1943 bytes, sha256 `f42f83f786d0a7fa`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<stdio.h>`, `"msghdr.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recvmmsg-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recvmsg.c -->
# sources/test-tools/strace/tests/recvmsg.c

## Purpose

`sources/test-tools/strace/tests/recvmsg.c` checks `recvmsg`/`sendmsg` msghdr, iovec, control, and length rendering in the strace tests tree. Source read: complete file, 142 lines, 3783 bytes, sha256 `3aaa8c2eaf2f3b0e`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<stdio.h>`, `<unistd.h>`, `<sys/socket.h>`, `<sys/uio.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recvmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/redirect-fds.c -->
# sources/test-tools/strace/tests/redirect-fds.c

## Purpose

`sources/test-tools/strace/tests/redirect-fds.c` checks test-harness fd redirection expectations for stdin/stdout/stderr-style descriptors in the strace tests tree. Source read: complete file, 54 lines, 894 bytes, sha256 `2397a3ac3b921dfe`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<unistd.h>`, `<sys/stat.h>`. Compile-time macros: `N_FDS`. Functions/helpers: `check_fd`, `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `check_fd`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/redirect-fds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/regex.in -->
# sources/test-tools/strace/tests/regex.in

## Purpose

`sources/test-tools/strace/tests/regex.in` is an input list for regex-based strace test cases and argument-count options in the strace tests tree. Source read: complete file, 2 lines, 26 bytes, sha256 `3116b12fb45e6144`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

There is no executable control flow. The harness reads each non-comment row as a test selector or option line and feeds it into the surrounding shell/test runner.

## State and Persistence Behavior

The file is static fixture data and stores no runtime state. Its only persistence effect is the checked-in input rows consumed by the test harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks are malformed rows, stale test names, or option changes that cause the harness to run the wrong executable or argument-count mode.

## Test Signals

Test signals are the harness accepting the fixture rows, invoking the referenced tests with the listed options, and producing no unexpected extra trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/regex.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xabbrev.c -->
# sources/test-tools/strace/tests/remap_file_pages-Xabbrev.c

## Purpose

This is a thin compile-time wrapper around `remap_file_pages.c`. Its local purpose is to rebuild the shared test body in default mode with no local behavior override. Source read: complete file, 1 lines, 30 bytes, sha256 `9b8f1968737ad834`.

## Important APIs, Types, and Functions

Includes: `"remap_file_pages.c"`. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines no local macros and then includes `remap_file_pages.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xraw.c -->
# sources/test-tools/strace/tests/remap_file_pages-Xraw.c

## Purpose

This is a thin compile-time wrapper around `remap_file_pages.c`. Its local purpose is to rebuild the shared test body in raw xlat mode, so symbolic constants are expected as numeric values where the shared body uses xlat formatting. Source read: complete file, 2 lines, 49 bytes, sha256 `94376e5d9a3b0d3e`.

## Important APIs, Types, and Functions

Includes: `"remap_file_pages.c"`. Compile-time macros: `XLAT_RAW`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_RAW` and then includes `remap_file_pages.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xverbose.c -->
# sources/test-tools/strace/tests/remap_file_pages-Xverbose.c

## Purpose

This is a thin compile-time wrapper around `remap_file_pages.c`. Its local purpose is to rebuild the shared test body in verbose xlat mode, so expected output includes numeric values plus symbolic comments/details. Source read: complete file, 2 lines, 53 bytes, sha256 `ce177f0a2ff9b612`.

## Important APIs, Types, and Functions

Includes: `"remap_file_pages.c"`. Compile-time macros: `XLAT_VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_VERBOSE` and then includes `remap_file_pages.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages.c -->
# sources/test-tools/strace/tests/remap_file_pages.c

## Purpose

`sources/test-tools/strace/tests/remap_file_pages.c` checks `remap_file_pages` syscall decoding for address, size, protection, pgoff, and map flags in the strace tests tree. Source read: complete file, 115 lines, 3664 bytes, sha256 `ef5279ba01890375`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<stdint.h>`, `<unistd.h>`, `<linux/mman.h>`. Compile-time macros: `prot1_str`, `flags1_str`. Functions/helpers: `k_remap_file_pages`, `main`. Direct syscall numbers: `__NR_remap_file_pages`. Notable constants/xlats: `MAP_`, `MAP_ANONYMOUS`, `MAP_FIXED`, `MAP_HUGETLB`, `MAP_HUGE_2MB`, `MAP_HUGE_SHIFT`, `MAP_NORESERVE`, `MAP_PRIVATE`, `MAP_SHARED_VALIDATE`, `MAP_TYPE`, `PROT_`, `PROT_EXEC`, `PROT_NONE`, `PROT_READ`, `PROT_WRITE`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_remap_file_pages` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_remap_file_pages`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_remap_file_pages`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-P.c -->
# sources/test-tools/strace/tests/removexattrat-P.c

## Purpose

This is a thin compile-time wrapper around `removexattrat.c`. Its local purpose is to rebuild the shared test body in path-tracing mode for descriptor/path qualification. Source read: complete file, 4 lines, 123 bytes, sha256 `42942c0a8cdfcaa2`.

## Important APIs, Types, and Functions

Includes: `"removexattrat.c"`. Compile-time macros: `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `removexattrat.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-y.c -->
# sources/test-tools/strace/tests/removexattrat-y.c

## Purpose

This is a thin compile-time wrapper around `removexattrat.c`. Its local purpose is to rebuild the shared test body in default mode with no local behavior override. Source read: complete file, 4 lines, 132 bytes, sha256 `29779aef16c298b8`.

## Important APIs, Types, and Functions

Includes: `"removexattrat.c"`. Compile-time macros: `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `removexattrat.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-yy.c -->
# sources/test-tools/strace/tests/removexattrat-yy.c

## Purpose

This is a thin compile-time wrapper around `removexattrat.c`. Its local purpose is to rebuild the shared test body in default mode with no local behavior override. Source read: complete file, 4 lines, 142 bytes, sha256 `3a87fc70b369a857`.

## Important APIs, Types, and Functions

Includes: `"removexattrat.c"`. Compile-time macros: `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `removexattrat.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat.c -->
# sources/test-tools/strace/tests/removexattrat.c

## Purpose

`sources/test-tools/strace/tests/removexattrat.c` checks `removexattrat` syscall decoding for fd/path, xattr name, and flag values in the strace tests tree. Source read: complete file, 150 lines, 3559 bytes, sha256 `1ad4157a2627bcc1`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"xmalloc.h"`, `<fcntl.h>`, `<stdio.h>`, `<unistd.h>`, `<linux/xattr.h>`. Compile-time macros: `XLAT_MACROS_ONLY`. Functions/helpers: `k_removexattrat`, `main`. Direct syscall numbers: `__NR_removexattrat`. Notable constants/xlats: `AT_`, `AT_EMPTY_PATH`, `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_removexattrat` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_removexattrat`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_removexattrat`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rename.c -->
# sources/test-tools/strace/tests/rename.c

## Purpose

`sources/test-tools/strace/tests/rename.c` checks basic `rename` old/new pathname decoding in the strace tests tree. Source read: complete file, 34 lines, 544 bytes, sha256 `d439fd87c0d4d0fc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_rename`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rename` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rename`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/renameat.c -->
# sources/test-tools/strace/tests/renameat.c

## Purpose

`sources/test-tools/strace/tests/renameat.c` checks `renameat` old/new dirfd and pathname decoding in the strace tests tree. Source read: complete file, 38 lines, 735 bytes, sha256 `7cf8aae692ae80d5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_renameat`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_renameat` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_renameat`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/renameat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/renameat2.c -->
# sources/test-tools/strace/tests/renameat2.c

## Purpose

`sources/test-tools/strace/tests/renameat2.c` checks `renameat2` syscall decoding, including flag xlat behavior in the strace tests tree. Source read: complete file, 35 lines, 852 bytes, sha256 `7d7e7f331c3349a7`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_renameat2`. Notable constants/xlats: `AT_FDCWD`, `RENAME_NOREPLACE`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_renameat2` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_renameat2`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/renameat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/request_key.c -->
# sources/test-tools/strace/tests/request_key.c

## Purpose

`sources/test-tools/strace/tests/request_key.c` checks `request_key` syscall decoding for key type, description, callout info, and destination keyring in the strace tests tree. Source read: complete file, 119 lines, 2885 bytes, sha256 `1484c11dd4456169`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<inttypes.h>`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `do_request_key`, `main`, `print_val_str`. Direct syscall numbers: `__NR_request_key`. Notable constants/xlats: `KEY_SPEC_THREAD_KEYRING`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_request_key` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `do_request_key`, `main`, `print_val_str` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_request_key`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/request_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/restart_syscall.c -->
# sources/test-tools/strace/tests/restart_syscall.c

## Purpose

`sources/test-tools/strace/tests/restart_syscall.c` checks interrupted nanosleep restart tracing and restart-syscall rendering in the strace tests tree. Source read: complete file, 69 lines, 2103 bytes, sha256 `d2fe8abfcb04b790`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<stdio.h>`, `<stdint.h>`, `<signal.h>`, `<time.h>`, `<sys/time.h>`. Compile-time macros: `NANOSLEEP_NAME_RE`, `NANOSLEEP_CALL_RE`. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGALRM`, `SIG_IGN`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/restart_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/riscv_flush_icache.c -->
# sources/test-tools/strace/tests/riscv_flush_icache.c

## Purpose

`sources/test-tools/strace/tests/riscv_flush_icache.c` checks RISC-V `riscv_flush_icache` syscall argument decoding in the strace tests tree. Source read: complete file, 72 lines, 1610 bytes, sha256 `2d04d15c2be4a93b`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_riscv_flush_icache`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_riscv_flush_icache` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_riscv_flush_icache`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/riscv_flush_icache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rmdir.c -->
# sources/test-tools/strace/tests/rmdir.c

## Purpose

`sources/test-tools/strace/tests/rmdir.c` checks basic `rmdir` pathname decoding in the strace tests tree. Source read: complete file, 31 lines, 483 bytes, sha256 `35b641bd6f1d3c4f`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_rmdir`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rmdir` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rmdir`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rmdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rseq.c -->
# sources/test-tools/strace/tests/rseq.c

## Purpose

`sources/test-tools/strace/tests/rseq.c` checks `rseq` syscall decoding for registration pointers, lengths, flags, and signatures in the strace tests tree. Source read: complete file, 175 lines, 5883 bytes, sha256 `88c588b56c2433e1`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `<linux/rseq.h>`. Compile-time macros: none found. Functions/helpers: `k_rseq`, `main`. Direct syscall numbers: `__NR_rseq`. Notable constants/xlats: `RSEQ_CPU_ID_REGISTRATION_FAILED`, `RSEQ_CPU_ID_UNINITIALIZED`, `RSEQ_CS_FLAG_`, `RSEQ_CS_FLAG_NO_RESTART_ON_MIGRATE`, `RSEQ_CS_FLAG_NO_RESTART_ON_PREEMPT`, `RSEQ_CS_FLAG_NO_RESTART_ON_SIGNAL`, `RSEQ_CS_FLAG_SLICE_EXT_AVAILABLE`, `RSEQ_CS_FLAG_SLICE_EXT_ENABLED`, `RSEQ_FLAG_`, `RSEQ_FLAG_SLICE_EXT_DEFAULT_ON`, `RSEQ_FLAG_UNREGISTER`, `RSEQ_TEST_ALIGN`, `RSEQ_TEST_MIN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rseq` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_rseq`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rseq`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rseq_slice_yield.c -->
# sources/test-tools/strace/tests/rseq_slice_yield.c

## Purpose

`sources/test-tools/strace/tests/rseq_slice_yield.c` checks `rseq_slice_yield` syscall decoding in the strace tests tree. Source read: complete file, 24 lines, 404 bytes, sha256 `f2a47c2f743c6ca5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_rseq_slice_yield`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rseq_slice_yield` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rseq_slice_yield`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rseq_slice_yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.awk -->
# sources/test-tools/strace/tests/rt_sigaction.awk

## Purpose

`sources/test-tools/strace/tests/rt_sigaction.awk` is the awk postprocessor/generator used by rt_sigaction tests to normalize architecture-specific signal-action traces in the strace tests tree. Source read: complete file, 76 lines, 2114 bytes, sha256 `3d462e72d55de31a`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: `SIGRT`, `SIGUSR2`, `SIG_DFL`, `SIG_IGN`.

## Control Flow

The awk program reads trace lines, applies regular-expression matching and field rewriting, and emits normalized expected output suitable for architecture-independent comparison.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

GNU awk-compatible regex and text-processing behavior. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include regexes that are too broad or too narrow, architecture-specific signal-action formatting changes, and awk portability assumptions.

## Test Signals

Test signals are stable normalized output from representative rt_sigaction traces and successful comparison by the surrounding test.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.c -->
# sources/test-tools/strace/tests/rt_sigaction.c

## Purpose

`sources/test-tools/strace/tests/rt_sigaction.c` sets signal handlers and raises signals to exercise rt_sigaction-related trace normalization in the strace tests tree. Source read: complete file, 48 lines, 983 bytes, sha256 `1f9e3647c201aec3`.

## Important APIs, Types, and Functions

Includes: `<assert.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`. Compile-time macros: none found. Functions/helpers: `handle_signal`, `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGTERM`, `SIGUSR2`, `SIG_DFL`, `SIG_IGN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handle_signal`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigpending.c -->
# sources/test-tools/strace/tests/rt_sigpending.c

## Purpose

`sources/test-tools/strace/tests/rt_sigpending.c` checks `rt_sigpending` syscall decoding for signal-set buffers and sigset sizes in the strace tests tree. Source read: complete file, 101 lines, 2245 bytes, sha256 `0a14fde86ea58f25`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<signal.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `iterate`, `k_sigpending`, `main`. Direct syscall numbers: `__NR_rt_sigpending`. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigpending` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `iterate`, `k_sigpending`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigpending`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigpending.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigprocmask.c -->
# sources/test-tools/strace/tests/rt_sigprocmask.c

## Purpose

`sources/test-tools/strace/tests/rt_sigprocmask.c` checks `rt_sigprocmask` action, old/new signal-set, and sigset-size decoding in the strace tests tree. Source read: complete file, 147 lines, 4235 bytes, sha256 `d9c0bc1cec5c7efc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<signal.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `iterate`, `k_sigprocmask`, `main`. Direct syscall numbers: `__NR_rt_sigprocmask`. Notable constants/xlats: `SIGALRM`, `SIGHUP`, `SIGINT`, `SIGKILL`, `SIGQUIT`, `SIGTERM`, `SIG_BLOCK`, `SIG_SETMASK`, `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigprocmask` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `iterate`, `k_sigprocmask`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigprocmask`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigprocmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigqueueinfo--pidns-translation.c -->
# sources/test-tools/strace/tests/rt_sigqueueinfo--pidns-translation.c

## Purpose

This is a thin compile-time wrapper around `rt_sigqueueinfo.c`. Its local purpose is to rebuild the shared test body in pid-namespace translation mode for expected pid/tid rendering. Source read: complete file, 2 lines, 55 bytes, sha256 `75b100d99c71318b`.

## Important APIs, Types, and Functions

Includes: `"rt_sigqueueinfo.c"`. Compile-time macros: `PIDNS_TRANSLATION`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PIDNS_TRANSLATION` and then includes `rt_sigqueueinfo.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; pid namespace translated and untranslated pid/tid expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigqueueinfo--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigqueueinfo.c -->
# sources/test-tools/strace/tests/rt_sigqueueinfo.c

## Purpose

`sources/test-tools/strace/tests/rt_sigqueueinfo.c` checks `rt_sigqueueinfo` signal-info delivery and pid rendering in the strace tests tree. Source read: complete file, 43 lines, 989 bytes, sha256 `0db999770914fdf4`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"pidns.h"`, `<assert.h>`, `<stdio.h>`, `<signal.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGUSR1`, `SIG_IGN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; pid namespace translation helpers. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigqueueinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigreturn.c -->
# sources/test-tools/strace/tests/rt_sigreturn.c

## Purpose

`sources/test-tools/strace/tests/rt_sigreturn.c` checks sigreturn/rt_sigreturn tracing around an actual signal handler in the strace tests tree. Source read: complete file, 59 lines, 1299 bytes, sha256 `15171691bf5d4b52`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<stdio.h>`, `<stdlib.h>`. Compile-time macros: none found. Functions/helpers: `handler`, `main`. Direct syscall numbers: none found. Notable constants/xlats: `RT_0`, `RT_26`, `RT_27`, `RT_3`, `RT_4`, `RT_5`, `SIGCHLD`, `SIGINT`, `SIGRTMIN`, `SIGUSR1`, `SIGUSR2`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigsuspend.c -->
# sources/test-tools/strace/tests/rt_sigsuspend.c

## Purpose

`sources/test-tools/strace/tests/rt_sigsuspend.c` checks `rt_sigsuspend` syscall decoding and interrupted-signal behavior in the strace tests tree. Source read: complete file, 136 lines, 3440 bytes, sha256 `8bf972cc075b1343`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<errno.h>`, `<signal.h>`, `<stdio.h>`, `<stdint.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `handler`, `iterate`, `k_sigsuspend`, `main`. Direct syscall numbers: `__NR_rt_sigsuspend`. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIGUSR1`, `SIGUSR2`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigsuspend` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `iterate`, `k_sigsuspend`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigsuspend`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigsuspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigtimedwait.c -->
# sources/test-tools/strace/tests/rt_sigtimedwait.c

## Purpose

`sources/test-tools/strace/tests/rt_sigtimedwait.c` checks `rt_sigtimedwait` set, siginfo, timeout, and sigset-size decoding in the strace tests tree. Source read: complete file, 193 lines, 5795 bytes, sha256 `130cdb91396e6d27`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `iterate`, `k_sigtimedwait`, `main`. Direct syscall numbers: `__NR_rt_sigtimedwait`. Notable constants/xlats: `SIGALRM`, `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGTERM`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigtimedwait` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `iterate`, `k_sigtimedwait`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigtimedwait`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigtimedwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_tgsigqueueinfo--pidns-translation.c -->
# sources/test-tools/strace/tests/rt_tgsigqueueinfo--pidns-translation.c

## Purpose

This is a thin compile-time wrapper around `rt_tgsigqueueinfo.c`. Its local purpose is to rebuild the shared test body in pid-namespace translation mode for expected pid/tid rendering. Source read: complete file, 2 lines, 57 bytes, sha256 `1e78de687446b868`.

## Important APIs, Types, and Functions

Includes: `"rt_tgsigqueueinfo.c"`. Compile-time macros: `PIDNS_TRANSLATION`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PIDNS_TRANSLATION` and then includes `rt_tgsigqueueinfo.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; pid namespace translated and untranslated pid/tid expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_tgsigqueueinfo--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_tgsigqueueinfo.c -->
# sources/test-tools/strace/tests/rt_tgsigqueueinfo.c

## Purpose

`sources/test-tools/strace/tests/rt_tgsigqueueinfo.c` checks `rt_tgsigqueueinfo` thread-directed signal-info delivery and pid/tid rendering in the strace tests tree. Source read: complete file, 70 lines, 1739 bytes, sha256 `ff9052975092a072`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"pidns.h"`, `<errno.h>`, `<signal.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `k_tgsigqueueinfo`, `main`. Direct syscall numbers: `__NR_gettid`, `__NR_rt_tgsigqueueinfo`. Notable constants/xlats: `SIGUSR1`, `SIG_IGN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_gettid`, `__NR_rt_tgsigqueueinfo` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_tgsigqueueinfo`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; pid namespace translation helpers; kernel syscall availability for `__NR_gettid`, `__NR_rt_tgsigqueueinfo`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_tgsigqueueinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/run.sh -->
# sources/test-tools/strace/tests/run.sh

## Purpose

`sources/test-tools/strace/tests/run.sh` is the common shell launcher that verifies strace availability, configures timeout, and execs a test command in the strace tests tree. Source read: complete file, 22 lines, 435 bytes, sha256 `9e2388f8d9a299fd`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, checks that `$STRACE -V` works, configures a timeout command when available, validates that a command was supplied, and `exec`s the test command with stdin redirected from `/dev/null`.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/run_expect_termsig.c -->
# sources/test-tools/strace/tests/run_expect_termsig.c

## Purpose

`sources/test-tools/strace/tests/run_expect_termsig.c` executes a command and asserts that it terminates with the requested signal in the strace tests tree. Source read: complete file, 38 lines, 759 bytes, sha256 `c34b6355eed51732`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/wait.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGCHLD`, `SIG_DFL`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/run_expect_termsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage-v.c -->
# sources/test-tools/strace/tests/s390_guarded_storage-v.c

## Purpose

This is a thin compile-time wrapper around `s390_guarded_storage.c`. Its local purpose is to rebuild the shared test body in verbose structure-printing mode for the included shared test body. Source read: complete file, 2 lines, 52 bytes, sha256 `32814f3864455501`.

## Important APIs, Types, and Functions

Includes: `"s390_guarded_storage.c"`. Compile-time macros: `VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `VERBOSE` and then includes `s390_guarded_storage.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage.c -->
# sources/test-tools/strace/tests/s390_guarded_storage.c

## Purpose

`sources/test-tools/strace/tests/s390_guarded_storage.c` checks s390 `s390_guarded_storage` syscall decoding for control-block and event-parameter-list forms in the strace tests tree. Source read: complete file, 208 lines, 5240 bytes, sha256 `e76b2969b5a9f4ba`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `gs_no_arg`, `gs_print_epl`, `gs_set_cb`, `main`. Direct syscall numbers: `__NR_s390_guarded_storage`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_s390_guarded_storage` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `gs_no_arg`, `gs_print_epl`, `gs_set_cb`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_guarded_storage`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_pci_mmio_read_write.c -->
# sources/test-tools/strace/tests/s390_pci_mmio_read_write.c

## Purpose

`sources/test-tools/strace/tests/s390_pci_mmio_read_write.c` checks s390 PCI MMIO read/write syscall decoding for MMIO addresses and byte buffers in the strace tests tree. Source read: complete file, 137 lines, 3011 bytes, sha256 `ed76e1c6098c65fc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `do_call`, `main`. Direct syscall numbers: `__NR_s390_pci_mmio_read`, `__NR_s390_pci_mmio_write`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_s390_pci_mmio_read`, `__NR_s390_pci_mmio_write` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `do_call`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_pci_mmio_read`, `__NR_s390_pci_mmio_write`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_pci_mmio_read_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_runtime_instr.c -->
# sources/test-tools/strace/tests/s390_runtime_instr.c

## Purpose

`sources/test-tools/strace/tests/s390_runtime_instr.c` checks s390 runtime instrumentation syscall command and signum formatting in the strace tests tree. Source read: complete file, 77 lines, 1648 bytes, sha256 `94437b6b9dd3e71b`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_s390_runtime_instr`. Notable constants/xlats: `S390_RUNTIME_INSTR_`, `S390_RUNTIME_INSTR_START`, `S390_RUNTIME_INSTR_STOP`, `SIGALRM`, `SIGRT_1`, `SIGRT_31`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_s390_runtime_instr` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_runtime_instr`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_runtime_instr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi-v.c -->
# sources/test-tools/strace/tests/s390_sthyi-v.c

## Purpose

This is a thin compile-time wrapper around `s390_sthyi.c`. Its local purpose is to rebuild the shared test body in verbose structure-printing mode for the included shared test body. Source read: complete file, 2 lines, 42 bytes, sha256 `e3435825d861384a`.

## Important APIs, Types, and Functions

Includes: `"s390_sthyi.c"`. Compile-time macros: `VERBOSE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `VERBOSE` and then includes `s390_sthyi.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi.c -->
# sources/test-tools/strace/tests/s390_sthyi.c

## Purpose

This s390-specific test validates decoding of the `s390_sthyi` syscall and its nested Store Hypervisor Information data block. Source read: complete file, 845 lines, 20512 bytes, sha256 `9890181aae7d31f5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `ebcdic2ascii`, `is_empty`, `main`, `print_0x8`, `print_ebcdic`, `print_funcs`, `print_guest_header`, `print_hypervisor_header`, `print_sthyi`, `print_u16`, `print_u8`, `print_weight`, `print_x32`. Direct syscall numbers: `__NR_s390_sthyi`. Notable constants/xlats: `STHYI`, `STHYI_FC_`, `STHYI_FC_CP_IFL_CAP`.

## Control Flow

When iconv and the syscall are available, helper printers decode EBCDIC fields, weights, CPU counts, partition/group/header fields, function codes, and reserved/empty blocks. `main` builds representative buffers, invokes `__NR_s390_sthyi`, and compares concise versus verbose output.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_sthyi`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The test depends on s390 UAPI layout, iconv availability, EBCDIC conversion, and verbose output stability across reserved fields.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched.in -->
# sources/test-tools/strace/tests/sched.in

## Purpose

`sources/test-tools/strace/tests/sched.in` is an input list of scheduler test names and strace argument-count options in the strace tests tree. Source read: complete file, 10 lines, 277 bytes, sha256 `689c6ae003e47af3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

There is no executable control flow. The harness reads each non-comment row as a test selector or option line and feeds it into the surrounding shell/test runner.

## State and Persistence Behavior

The file is static fixture data and stores no runtime state. Its only persistence effect is the checked-in input rows consumed by the test harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks are malformed rows, stale test names, or option changes that cause the harness to run the wrong executable or argument-count mode.

## Test Signals

Test signals are the harness accepting the fixture rows, invoking the referenced tests with the listed options, and producing no unexpected extra trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_get_priority_mxx.c -->
# sources/test-tools/strace/tests/sched_get_priority_mxx.c

## Purpose

`sources/test-tools/strace/tests/sched_get_priority_mxx.c` checks `sched_get_priority_max` and `sched_get_priority_min` policy decoding in the strace tests tree. Source read: complete file, 28 lines, 603 bytes, sha256 `7381cba1852f5e38`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<sched.h>`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_sched_get_priority_max`, `__NR_sched_get_priority_min`. Notable constants/xlats: `SCHED_FIFO`, `SCHED_RR`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_sched_get_priority_max`, `__NR_sched_get_priority_min` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_sched_get_priority_max`, `__NR_sched_get_priority_min`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_get_priority_mxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_getscheduler-success.c -->
# sources/test-tools/strace/tests/sched_getscheduler-success.c

## Purpose

`sources/test-tools/strace/tests/sched_getscheduler-success.c` checks `sched_getscheduler` decoding under syscall retval injection in the strace tests tree. Source read: complete file, 79 lines, 1631 bytes, sha256 `0a35779e608eb98d`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"pidns.h"`, `<sched.h>`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: `XLAT_MACROS_ONLY`. Functions/helpers: `main`. Direct syscall numbers: `__NR_sched_getscheduler`. Notable constants/xlats: `SCHED_BATCH`, `SCHED_DEADLINE`, `SCHED_EXT`, `SCHED_FIFO`, `SCHED_IDLE`, `SCHED_ISO`, `SCHED_OTHER`, `SCHED_RESET_ON_FORK`, `SCHED_RR`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_sched_getscheduler` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; pid namespace translation helpers; kernel syscall availability for `__NR_sched_getscheduler`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_getscheduler-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_rr_get_interval.c -->
# sources/test-tools/strace/tests/sched_rr_get_interval.c

## Purpose

`sources/test-tools/strace/tests/sched_rr_get_interval.c` checks `sched_rr_get_interval` pid and timespec decoding in the strace tests tree. Source read: complete file, 51 lines, 1152 bytes, sha256 `e6069a2fdbadf986`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_sched_rr_get_interval`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_sched_rr_get_interval` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_sched_rr_get_interval`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_rr_get_interval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity--pidns-translation.c -->
# sources/test-tools/strace/tests/sched_xetaffinity--pidns-translation.c

## Purpose

This is a thin compile-time wrapper around `sched_xetaffinity.c`. Its local purpose is to rebuild the shared test body in pid-namespace translation mode for expected pid/tid rendering. Source read: complete file, 2 lines, 57 bytes, sha256 `b901e0100594b204`.

## Important APIs, Types, and Functions

Includes: `"sched_xetaffinity.c"`. Compile-time macros: `PIDNS_TRANSLATION`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PIDNS_TRANSLATION` and then includes `sched_xetaffinity.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; pid namespace translated and untranslated pid/tid expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity.c -->
# sources/test-tools/strace/tests/sched_xetaffinity.c

## Purpose

`sources/test-tools/strace/tests/sched_xetaffinity.c` checks `sched_getaffinity` and `sched_setaffinity` cpuset-size and mask decoding in the strace tests tree. Source read: complete file, 155 lines, 4401 bytes, sha256 `32ee58964b01a9e5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"pidns.h"`, `<sched.h>`. Compile-time macros: none found. Functions/helpers: `getaffinity`, `main`, `setaffinity`. Direct syscall numbers: `__NR_sched_getaffinity`, `__NR_sched_setaffinity`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_sched_getaffinity`, `__NR_sched_setaffinity` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `getaffinity`, `main`, `setaffinity` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; pid namespace translation helpers; kernel syscall availability for `__NR_sched_getaffinity`, `__NR_sched_setaffinity`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetattr--pidns-translation.c -->
# sources/test-tools/strace/tests/sched_xetattr--pidns-translation.c

## Purpose

This is a thin compile-time wrapper around `sched_xetattr.c`. Its local purpose is to rebuild the shared test body in pid-namespace translation mode for expected pid/tid rendering. Source read: complete file, 2 lines, 53 bytes, sha256 `a8a1d7425c1f428a`.

## Important APIs, Types, and Functions

Includes: `"sched_xetattr.c"`. Compile-time macros: `PIDNS_TRANSLATION`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `PIDNS_TRANSLATION` and then includes `sched_xetattr.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; pid namespace translated and untranslated pid/tid expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetattr--pidns-translation.c -->
