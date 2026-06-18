# subset-b-009355 Research

Grouped source research for strace test-suite files covering process control, pidfds, pid namespaces, polling/select, prctl operation families, cross-process memory, ptrace, and printer helper decoding. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/orphaned_process_group.c -->
# sources/test-tools/strace/tests/orphaned_process_group.c

## Purpose

`sources/test-tools/strace/tests/orphaned_process_group.c` is a C test program in the strace tests tree. It provides terminal/job-control fixture that creates an orphaned process group and checks strace behavior around stopped or signalled children. The source was read as a complete 155-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/wait.h`. functions: `alarm_handler`, `main`. types: `sigaction`. macros: `TIMEOUT`. notable constants/xlats: `SIG_SETMASK`, `SIG_DFL`. Source size: 155 lines, 3502 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/orphaned_process_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/osf_utimes.c -->
# sources/test-tools/strace/tests/osf_utimes.c

## Purpose

`sources/test-tools/strace/tests/osf_utimes.c` is a C test program in the strace tests tree. It provides Alpha OSF utimes compatibility decoder coverage for legacy utimes argument formatting. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `xutimes.c`. functions: none found in this file. types: `timeval32`. macros: `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_STRUCT`. direct syscall numbers: `__NR_osf_utimes`. wrapper include: `xutimes.c`. Source size: 26 lines, 534 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `xutimes.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/osf_utimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/overflowuid.c -->
# sources/test-tools/strace/tests/overflowuid.c

## Purpose

`sources/test-tools/strace/tests/overflowuid.c` is a C test program in the strace tests tree. It provides UID/GID overflow value decoder coverage that checks how strace prints kernel overflow IDs and related proc/sysctl state. The source was read as a complete 76-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `errno.h`, `fcntl.h`, `limits.h`, `stdlib.h`, `unistd.h`. functions: `read_int_from_file`, `check_overflow_id`, `check_overflowuid`, `check_overflowgid`. types: none found in this file. macros: none found in this file. notable constants/xlats: `O_RDONLY`. Source size: 76 lines, 1370 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/overflowuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pause.c -->
# sources/test-tools/strace/tests/pause.c

## Purpose

`sources/test-tools/strace/tests/pause.c` is a C test program in the strace tests tree. It provides pause syscall decoder coverage for interrupted blocking syscall output and signal handling behavior. The source was read as a complete 60-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `signal.h`, `stdio.h`, `sys/time.h`, `unistd.h`. functions: `handler`, `main`. types: `sigaction`, `itimerval`. macros: none found in this file. direct syscall numbers: `__NR_pause`. notable constants/xlats: `SIG_UNBLOCK`. Source size: 60 lines, 1183 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pause`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pause.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pc.c -->
# sources/test-tools/strace/tests/pc.c

## Purpose

`sources/test-tools/strace/tests/pc.c` is a C test program in the strace tests tree. It provides program-counter reporting test that checks strace instruction pointer / PC annotation output around a controlled syscall. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `assert.h`, `dlfcn.h`, `fcntl.h`, `unistd.h`, `sys/mman.h`, `sys/wait.h`, `sys/sendfile.h`, `sys/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_write`. notable constants/xlats: `PR_SET_DUMPABLE`, `O_RDONLY`. Source size: 83 lines, 1821 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_write`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open.c -->
# sources/test-tools/strace/tests/perf_event_open.c

## Purpose

`sources/test-tools/strace/tests/perf_event_open.c` is a C test program in the strace tests tree. It provides perf_event_open decoder coverage for struct perf_event_attr, perf flags, abbreviated versus verbose attribute printing, and unknown or version-dependent fields. The source was read as a complete 732-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `limits.h`, `stddef.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `linux/perf_event.h`, `xlat.h`, `xlat/perf_event_open_flags.h`. functions: `printaddr`, `print_event_attr`, `main`. types: `pea_flags`, `perf_event_attr`, `strval64`, `strval32`, `strival32`. macros: `LONG_STR_PREFIX`, `PRINT_FLAG`, `ATTR_REC`, `BRANCH_TYPE_ALL`. direct syscall numbers: `__NR_perf_event_open`. notable constants/xlats: `PERF_ATTR_SIZE_VER0`, `PERF_ATTR_SIZE_`, `PERF_TYPE_BREAKPOINT`, `PERF_SAMPLE_BRANCH_STACK`, `PERF_SAMPLE_STACK_USER`, `PERF_SAMPLE_BRANCH_USER`, `PERF_SAMPLE_BRANCH_KERNEL`, `PERF_SAMPLE_BRANCH_HV`, `PERF_SAMPLE_BRANCH_ANY`, `PERF_SAMPLE_BRANCH_ANY_CALL`, `PERF_SAMPLE_BRANCH_ANY_RETURN`, `PERF_SAMPLE_BRANCH_IND_CALL`, `PERF_SAMPLE_BRANCH_ABORT_TX`, `PERF_SAMPLE_BRANCH_IN_TX`, `PERF_SAMPLE_BRANCH_NO_TX`, `PERF_SAMPLE_BRANCH_COND`, `PERF_SAMPLE_BRANCH_CALL_STACK`, `PERF_SAMPLE_BRANCH_IND_JUMP`. Source size: 732 lines, 19583 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_perf_event_open`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_nonverbose.c -->
# sources/test-tools/strace/tests/perf_event_open_nonverbose.c

## Purpose

`sources/test-tools/strace/tests/perf_event_open_nonverbose.c` is a C test program in the strace tests tree. It provides perf_event_open decoder coverage for struct perf_event_attr, perf flags, abbreviated versus verbose attribute printing, and unknown or version-dependent fields. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/perf_event.h`, `xlat.h`, `xlat/perf_event_open_flags.h`. functions: `printaddr`, `main`. types: `perf_event_attr`. macros: `LONG_STR_PREFIX`. direct syscall numbers: `__NR_perf_event_open`. notable constants/xlats: `PERF_TYPE_HARDWARE`, `PERF_FLAG_FD_NO_GROUP`, `PERF_FLAG_FD_OUTPUT`, `PERF_FLAG_PID_CGROUP`, `PERF_FLAG_FD_CLOEXEC`. variant settings: uses non-verbose or unabbreviated compile-time mode. Source size: 85 lines, 2026 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_perf_event_open`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_nonverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_unabbrev.c -->
# sources/test-tools/strace/tests/perf_event_open_unabbrev.c

## Purpose

`sources/test-tools/strace/tests/perf_event_open_unabbrev.c` is a C test program in the strace tests tree. It provides perf_event_open decoder coverage for struct perf_event_attr, perf flags, abbreviated versus verbose attribute printing, and unknown or version-dependent fields. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `perf_event_open.c`. functions: none found in this file. types: none found in this file. macros: `VERBOSE`. wrapper include: `perf_event_open.c`. variant settings: uses verbose structure decoding; uses non-verbose or unabbreviated compile-time mode. Source size: 2 lines, 47 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `perf_event_open.c`. It sets: uses verbose structure decoding; uses non-verbose or unabbreviated compile-time mode. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_unabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xabbrev.c -->
# sources/test-tools/strace/tests/personality-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/personality-Xabbrev.c` is a C test program in the strace tests tree. It provides personality syscall decoder coverage for personality flags and xlat output modes. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `personality.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `personality.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 1 lines, 25 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `personality.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xraw.c -->
# sources/test-tools/strace/tests/personality-Xraw.c

## Purpose

`sources/test-tools/strace/tests/personality-Xraw.c` is a C test program in the strace tests tree. It provides personality syscall decoder coverage for personality flags and xlat output modes. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `personality.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `personality.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 44 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `personality.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xverbose.c -->
# sources/test-tools/strace/tests/personality-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/personality-Xverbose.c` is a C test program in the strace tests tree. It provides personality syscall decoder coverage for personality flags and xlat output modes. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `personality.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `personality.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 48 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `personality.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/personality-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/personality.c -->
# sources/test-tools/strace/tests/personality.c

## Purpose

`sources/test-tools/strace/tests/personality.c` is a C test program in the strace tests tree. It provides personality syscall decoder coverage for personality flags and xlat output modes. The source was read as a complete 125-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `sys/personality.h`. functions: `main`. types: none found in this file. macros: `linux_type_str`, `good_type_str`, `bad_type_str`, `good_flags_str`, `bad_flags_str`, `good_bad_flags_str`. Source size: 125 lines, 4023 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-y.c -->
# sources/test-tools/strace/tests/pidfd_getfd-y.c

## Purpose

`sources/test-tools/strace/tests/pidfd_getfd-y.c` is a C test program in the strace tests tree. It provides pidfd_getfd decoder coverage for pidfd arguments, target file descriptors, optional fd path and pidfd annotations, and invalid flag handling. The source was read as a complete 5-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_getfd.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PIDFD_PATH`, `FD0_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. wrapper include: `pidfd_getfd.c`. variant settings: enables pidfd fd annotation output. Source size: 5 lines, 158 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_getfd.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-yy.c -->
# sources/test-tools/strace/tests/pidfd_getfd-yy.c

## Purpose

`sources/test-tools/strace/tests/pidfd_getfd-yy.c` is a C test program in the strace tests tree. It provides pidfd_getfd decoder coverage for pidfd arguments, target file descriptors, optional fd path and pidfd annotations, and invalid flag handling. The source was read as a complete 5-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_getfd.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PIDFD_PID`, `FD0_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. wrapper include: `pidfd_getfd.c`. variant settings: enables pidfd fd annotation output. Source size: 5 lines, 167 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_getfd.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd.c -->
# sources/test-tools/strace/tests/pidfd_getfd.c

## Purpose

`sources/test-tools/strace/tests/pidfd_getfd.c` is a C test program in the strace tests tree. It provides pidfd_getfd decoder coverage for pidfd arguments, target file descriptors, optional fd path and pidfd annotations, and invalid flag handling. The source was read as a complete 103-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `xmalloc.h`, `assert.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/wait.h`. functions: `k_pidfd_getfd`, `main`. types: none found in this file. macros: `FD0_PATH`, `PRINT_PIDFD_PATH`, `PRINT_PIDFD_PID`, `SKIP_IF_PROC_IS_UNAVAILABLE`. direct syscall numbers: `__NR_pidfd_getfd`, `__NR_pidfd_open`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 103 lines, 2295 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pidfd_getfd`, `__NR_pidfd_open`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-all.c -->
# sources/test-tools/strace/tests/pidfd_open--decode-fd-all.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--decode-fd-all.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open--decode-fd-pidfd.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `pidfd_open--decode-fd-pidfd.c`. Source size: 1 lines, 41 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open--decode-fd-pidfd.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-none.c -->
# sources/test-tools/strace/tests/pidfd_open--decode-fd-none.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--decode-fd-none.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `pidfd_open.c`. Source size: 1 lines, 24 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-path.c -->
# sources/test-tools/strace/tests/pidfd_open--decode-fd-path.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--decode-fd-path.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open-y.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `pidfd_open-y.c`. variant settings: enables path tracing or decoded path output. Source size: 1 lines, 26 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open-y.c`. It sets: enables path tracing or decoded path output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-pidfd.c -->
# sources/test-tools/strace/tests/pidfd_open--decode-fd-pidfd.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--decode-fd-pidfd.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open-y.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PIDFD`. wrapper include: `pidfd_open-y.c`. variant settings: enables pidfd fd annotation output. Source size: 2 lines, 48 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open-y.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-pidfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-socket.c -->
# sources/test-tools/strace/tests/pidfd_open--decode-fd-socket.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--decode-fd-socket.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open--decode-fd-none.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `pidfd_open--decode-fd-none.c`. Source size: 1 lines, 40 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open--decode-fd-none.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--decode-fd-socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--pidns-translation.c -->
# sources/test-tools/strace/tests/pidfd_open--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open--pidns-translation.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `pidfd_open.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 50 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-P.c -->
# sources/test-tools/strace/tests/pidfd_open-P.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open-P.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open.c`. functions: none found in this file. types: none found in this file. macros: `PATH_TRACING`. wrapper include: `pidfd_open.c`. variant settings: enables path tracing or decoded path output. Source size: 2 lines, 45 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open.c`. It sets: enables path tracing or decoded path output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-y.c -->
# sources/test-tools/strace/tests/pidfd_open-y.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open-y.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PATHS`. wrapper include: `pidfd_open.c`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 2 lines, 44 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open.c`. It sets: enables path tracing or decoded path output; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-yy.c -->
# sources/test-tools/strace/tests/pidfd_open-yy.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open-yy.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_open-y.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PIDFD`. wrapper include: `pidfd_open-y.c`. variant settings: enables pidfd fd annotation output. Source size: 2 lines, 48 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_open-y.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open.c -->
# sources/test-tools/strace/tests/pidfd_open.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 130-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`, `pidns.h`. functions: `k_pidfd_open`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pidfd_open`. notable constants/xlats: `O_WRONLY`, `O_NONBLOCK`, `PIDFD_NONBLOCK`, `O_EXCL`, `PIDFD_THREAD`, `PIDFD_AUTOKILL`, `O_TRUNC`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 130 lines, 2943 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pidfd_open`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal--pidns-translation.c -->
# sources/test-tools/strace/tests/pidfd_send_signal--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/pidfd_send_signal--pidns-translation.c` is a C test program in the strace tests tree. It provides pidfd_send_signal decoder coverage for pidfd arguments, signal names, siginfo_t decoding, PID translation, and PIDFD signal flag masks. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_send_signal.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `pidfd_send_signal.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_send_signal.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal.c -->
# sources/test-tools/strace/tests/pidfd_send_signal.c

## Purpose

`sources/test-tools/strace/tests/pidfd_send_signal.c` is a C test program in the strace tests tree. It provides pidfd_send_signal decoder coverage for pidfd arguments, signal names, siginfo_t decoding, PID translation, and PIDFD signal flag masks. The source was read as a complete 73-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `unistd.h`, `scno.h`, `pidns.h`, `fcntl.h`, `stdio.h`, `signal.h`. functions: `sys_pidfd_send_signal`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pidfd_send_signal`. notable constants/xlats: `O_RDONLY`, `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, `PIDFD_SIGNAL_PROCESS_GROUP`. Source size: 73 lines, 1842 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pidfd_send_signal`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns-cache.c -->
# sources/test-tools/strace/tests/pidns-cache.c

## Purpose

`sources/test-tools/strace/tests/pidns-cache.c` is a C test program in the strace tests tree. It provides pid namespace cache test that stresses reuse and invalidation of strace pid translation state. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `pidns.h`, `stdio.h`, `unistd.h`, `sys/time.h`. functions: `execute_syscalls`, `main`. types: `timeval`. macros: `SYSCALL_COUNT`, `MAX_TIME_RATIO`. direct syscall numbers: `__NR_getpid`, `__NR_getxpid`. Source size: 68 lines, 1304 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_getpid`, `__NR_getxpid`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.c -->
# sources/test-tools/strace/tests/pidns.c

## Purpose

`sources/test-tools/strace/tests/pidns.c` is a C test program in the strace tests tree. It provides pid namespace executable fixture that exercises namespace setup and PID translation helpers used by syscall decoder tests. The source was read as a complete 244-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `pidns.h`, `linux/nsfs.h`, `errno.h`, `stdio.h`, `string.h`, `sys/types.h`, `signal.h`, `stdlib.h`, `sched.h`, `unistd.h`, `sys/wait.h`. functions: `pidns_print_leader`, `pidns_pid2str`, `pidns_fork`, `create_init_process`, `check_ns_ioctl`, `pidns_test_init`. types: `pid_type`. macros: none found in this file. notable constants/xlats: `O_RDONLY`. Source size: 244 lines, 5618 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `pidns.h` PID namespace setup and translated PID suffix rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.h -->
# sources/test-tools/strace/tests/pidns.h

## Purpose

`sources/test-tools/strace/tests/pidns.h` is a shared header in the strace tests tree. It provides shared pid namespace support header used by strace tests that need stable printing of translated PIDs, pid types, and pid namespace leaders. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

includes: `sys/types.h`. functions: `pidns_print_leader`, `pidns_pid2str`, `check_ns_ioctl`, `pidns_test_init`. types: `pid_type`. macros: `STRACE_PIDNS_H`, `PIDNS_TEST_INIT`. variant settings: enables pid namespace translation output. Source size: 57 lines, 1321 bytes.

## Control Flow

There is no standalone runtime flow in this header. It declares macros, helpers, or shared types that the compiled C tests use to normalize PID namespace setup and expected output rendering.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

The file integrates with the strace test build and comparison harness through local includes and generated expected-output rules.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pipe.c -->
# sources/test-tools/strace/tests/pipe.c

## Purpose

`sources/test-tools/strace/tests/pipe.c` is a C test program in the strace tests tree. It provides pipe/pipe2 decoder coverage for returned descriptor arrays, pipe flags, and maximum-fd edge cases. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `fcntl.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pipe`. Source size: 36 lines, 551 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pipe`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pipe2.c -->
# sources/test-tools/strace/tests/pipe2.c

## Purpose

`sources/test-tools/strace/tests/pipe2.c` is a C test program in the strace tests tree. It provides pipe/pipe2 decoder coverage for returned descriptor arrays, pipe flags, and maximum-fd edge cases. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pipe2`. notable constants/xlats: `O_NONBLOCK`. Source size: 42 lines, 966 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pipe2`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pipe2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pipe_maxfd.c -->
# sources/test-tools/strace/tests/pipe_maxfd.c

## Purpose

`sources/test-tools/strace/tests/pipe_maxfd.c` is a C test program in the strace tests tree. It provides pipe/pipe2 decoder coverage for returned descriptor arrays, pipe flags, and maximum-fd edge cases. The source was read as a complete 47-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `limits.h`, `unistd.h`, `sys/resource.h`. functions: `move_fd`, `pipe_maxfd`. types: `rlimit`. macros: none found in this file. notable constants/xlats: `RLIMIT_NOFILE`. Source size: 47 lines, 945 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pipe_maxfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_alloc.c -->
# sources/test-tools/strace/tests/pkey_alloc.c

## Purpose

`sources/test-tools/strace/tests/pkey_alloc.c` is a C test program in the strace tests tree. It provides memory protection key syscall decoder coverage for pkey allocation, free, and pkey_mprotect argument rendering. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pkey_alloc`. notable constants/xlats: `PKEY_DISABLE_WRITE`, `PKEY_DISABLE_ACCESS`, `PKEY_DISABLE_EXECUTE`, `PKEY_UNRESTRICTED`. Source size: 55 lines, 1348 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pkey_alloc`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_free.c -->
# sources/test-tools/strace/tests/pkey_free.c

## Purpose

`sources/test-tools/strace/tests/pkey_free.c` is a C test program in the strace tests tree. It provides memory protection key syscall decoder coverage for pkey allocation, free, and pkey_mprotect argument rendering. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pkey_free`. Source size: 36 lines, 735 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pkey_free`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_free.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_mprotect.c -->
# sources/test-tools/strace/tests/pkey_mprotect.c

## Purpose

`sources/test-tools/strace/tests/pkey_mprotect.c` is a C test program in the strace tests tree. It provides memory protection key syscall decoder coverage for pkey allocation, free, and pkey_mprotect argument rendering. The source was read as a complete 90-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `sys/mman.h`. functions: `sprintptr`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pkey_mprotect`. Source size: 90 lines, 2052 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pkey_mprotect`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_mprotect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/poke-sendfile.c -->
# sources/test-tools/strace/tests/poke-sendfile.c

## Purpose

`sources/test-tools/strace/tests/poke-sendfile.c` is a C test program in the strace tests tree. It provides strace poke/injection test coverage for modifying syscall data paths, including sendfile-specific data movement. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `assert.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, `sys/socket.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_sendfile64`, `__NR_sendfile`. notable constants/xlats: `O_RDWR`. Source size: 55 lines, 1374 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_sendfile64`, `__NR_sendfile`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/poke-sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/poke.c -->
# sources/test-tools/strace/tests/poke.c

## Purpose

`sources/test-tools/strace/tests/poke.c` is a C test program in the strace tests tree. It provides strace poke/injection test coverage for modifying syscall data paths, including sendfile-specific data movement. The source was read as a complete 124-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `string.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_getcwd`. Source size: 124 lines, 2797 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_getcwd`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/poke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/poll-P.c -->
# sources/test-tools/strace/tests/poll-P.c

## Purpose

`sources/test-tools/strace/tests/poll-P.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `poll.c`. functions: none found in this file. types: none found in this file. macros: `PATH_TRACING_FD`. wrapper include: `poll.c`. variant settings: enables path tracing or decoded path output. Source size: 2 lines, 44 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `poll.c`. It sets: enables path tracing or decoded path output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/poll-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/poll.c -->
# sources/test-tools/strace/tests/poll.c

## Purpose

`sources/test-tools/strace/tests/poll.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 293-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `assert.h`, `errno.h`, `poll.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`. functions: `print_pollfd_entering`, `print_pollfd_array_entering`, `print_pollfd_exiting`, `print_pollfd_array_exiting`, `main`. types: `pollfd`. macros: `PRINT_EVENT`. direct syscall numbers: `__NR_poll`. variant settings: enables path tracing or decoded path output. Source size: 293 lines, 7244 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_poll`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-P.c -->
# sources/test-tools/strace/tests/ppoll-P.c

## Purpose

`sources/test-tools/strace/tests/ppoll-P.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ppoll.c`. functions: none found in this file. types: none found in this file. macros: `PATH_TRACING_FD`. wrapper include: `ppoll.c`. variant settings: enables path tracing or decoded path output. Source size: 2 lines, 45 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ppoll.c`. It sets: enables path tracing or decoded path output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-23-42.c -->
# sources/test-tools/strace/tests/ppoll-e-trace-fds-23-42.c

## Purpose

`sources/test-tools/strace/tests/ppoll-e-trace-fds-23-42.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `ppoll.c`. functions: none found in this file. types: none found in this file. macros: `TRACING_FDS`, `TRACING_FD1`, `TRACING_FD2`. wrapper include: `ppoll.c`. Source size: 4 lines, 87 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ppoll.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-23-42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-23.c -->
# sources/test-tools/strace/tests/ppoll-e-trace-fds-23.c

## Purpose

`sources/test-tools/strace/tests/ppoll-e-trace-fds-23.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

includes: `ppoll.c`. functions: none found in this file. types: none found in this file. macros: `TRACING_FDS`, `TRACING_FD1`. wrapper include: `ppoll.c`. Source size: 3 lines, 72 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ppoll.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-not-9-42-P.c -->
# sources/test-tools/strace/tests/ppoll-e-trace-fds-not-9-42-P.c

## Purpose

`sources/test-tools/strace/tests/ppoll-e-trace-fds-not-9-42-P.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 7-line file for this report.

## Important APIs, Types, and Functions

includes: `ppoll.c`. functions: none found in this file. types: none found in this file. macros: `PATH_TRACING_FD`, `TRACING_FDS`, `TRACING_FD1`, `TRACING_FD2`, `TRACE_FD2`, `TRACE_OTHER_FDS`. wrapper include: `ppoll.c`. variant settings: enables path tracing or decoded path output. Source size: 7 lines, 177 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ppoll.c`. It sets: enables path tracing or decoded path output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-e-trace-fds-not-9-42-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-v.c -->
# sources/test-tools/strace/tests/ppoll-v.c

## Purpose

`sources/test-tools/strace/tests/ppoll-v.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

includes: `ppoll.c`. functions: none found in this file. types: none found in this file. macros: `VERBOSE`. wrapper include: `ppoll.c`. variant settings: uses verbose structure decoding. Source size: 3 lines, 85 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ppoll.c`. It sets: uses verbose structure decoding. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll.c -->
# sources/test-tools/strace/tests/ppoll.c

## Purpose

`sources/test-tools/strace/tests/ppoll.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 294-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `poll.h`, `signal.h`, `stdio.h`, `string.h`, `unistd.h`. functions: `sys_ppoll`, `main`. types: `pollfd`. macros: `PATH_TRACING_FD`, `TRACING_FDS`, `TRACING_FD1`, `TRACING_FD2`, `TRACE_FD1`, `TRACE_FD2`, `TRACE_OTHER_FDS`. direct syscall numbers: `__NR_ppoll`. variant settings: enables path tracing or decoded path output. Source size: 294 lines, 9141 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_ppoll`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-arg2-intptr.c -->
# sources/test-tools/strace/tests/prctl-arg2-intptr.c

## Purpose

`sources/test-tools/strace/tests/prctl-arg2-intptr.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 94-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdint.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_CHILD_SUBREAPER`, `PR_GET_ENDIAN`, `PR_GET_FPEMU`, `PR_GET_FPEXC`. Source size: 94 lines, 2550 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-arg2-intptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-cap-ambient.c -->
# sources/test-tools/strace/tests/prctl-cap-ambient.c

## Purpose

`sources/test-tools/strace/tests/prctl-cap-ambient.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 80-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`, `linux/capability.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_RAISE`, `CAP_NET_RAW`, `CAP_AUDIT_CONTROL`, `PR_CAP_AMBIENT_LOWER`, `CAP_KILL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_`. Source size: 80 lines, 2665 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-cap-ambient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-capbset.c -->
# sources/test-tools/strace/tests/prctl-capbset.c

## Purpose

`sources/test-tools/strace/tests/prctl-capbset.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`, `linux/capability.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_CAPBSET_READ`, `PR_CAPBSET_DROP`, `CAP_AUDIT_CONTROL`, `CAP_NET_RAW`. Source size: 50 lines, 1238 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-capbset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-dumpable.c -->
# sources/test-tools/strace/tests/prctl-dumpable.c

## Purpose

`sources/test-tools/strace/tests/prctl-dumpable.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `linux/prctl.h`, `stdio.h`, `unistd.h`. functions: `prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_DUMPABLE`, `PR_SET_DUMPABLE`. Source size: 87 lines, 2095 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-dumpable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-fp-mode.c -->
# sources/test-tools/strace/tests/prctl-fp-mode.c

## Purpose

`sources/test-tools/strace/tests/prctl-fp-mode.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 119-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `do_prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_FP_MODE`, `PR_SET_FP_MODE`, `PR_FP_MODE_FR`, `PR_FP_MODE_FRE`, `PR_FP_MODE_`. variant settings: uses success or retval injection path. Source size: 119 lines, 2784 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-fp-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-mce-kill.c -->
# sources/test-tools/strace/tests/prctl-mce-kill.c

## Purpose

`sources/test-tools/strace/tests/prctl-mce-kill.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_MCE_KILL`, `PR_MCE_KILL_GET`, `PR_MCE_KILL_CLEAR`, `PR_MCE_KILL_SET`, `PR_MCE_KILL_EARLY`, `PR_MCE_KILL_LATE`, `PR_MCE_KILL_`, `PR_MCE_KILL_DEFAULT`. Source size: 61 lines, 1866 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-mce-kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-mdwe.c -->
# sources/test-tools/strace/tests/prctl-mdwe.c

## Purpose

`sources/test-tools/strace/tests/prctl-mdwe.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 153-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `do_prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_MDWE`, `PR_SET_MDWE`, `PR_MDWE_REFUSE_EXEC_GAIN`, `PR_MDWE_NO_INHERIT`, `PR_MDWE_`, `PR_SET_FP_MODE`. variant settings: uses success or retval injection path. Source size: 153 lines, 3905 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-mdwe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-name.c -->
# sources/test-tools/strace/tests/prctl-name.c

## Purpose

`sources/test-tools/strace/tests/prctl-name.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PR_GET_NAME`, `PR_SET_NAME`. Source size: 74 lines, 1796 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-no-args-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-no-args.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 49 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xraw.c -->
# sources/test-tools/strace/tests/prctl-no-args-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-no-args.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 46 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-no-args-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-no-args.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 50 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-no-args-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-no-args-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-no-args-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-no-args-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-no-args-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-no-args-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 58 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success.c -->
# sources/test-tools/strace/tests/prctl-no-args-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-no-args.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-no-args.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 49 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-no-args.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args.c -->
# sources/test-tools/strace/tests/prctl-no-args.c

## Purpose

`sources/test-tools/strace/tests/prctl-no-args.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 204-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: `strval32`. macros: `INJ_STR`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_KEEPCAPS`, `PR_GET_SECCOMP`, `PR_GET_TIMERSLACK`, `PR_GET_TIMING`, `PR_TASK_PERF_EVENTS_DISABLE`, `PR_TASK_PERF_EVENTS_ENABLE`, `PR_GET_NO_NEW_PRIVS`, `PR_GET_THP_DISABLE`, `PR_MPX_DISABLE_MANAGEMENT`, `PR_MPX_ENABLE_MANAGEMENT`, `PR_GET_IO_FLUSHER`, `PR_GET_MEMORY_MERGE`, `PR_SET_MEMORY_MERGE`. variant settings: uses success or retval injection path. Source size: 204 lines, 6929 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-no-args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-pac-enabled-keys.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 58 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xraw.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-pac-enabled-keys.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 55 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-pac-enabled-keys.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 59 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-pac-enabled-keys-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 66 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-pac-enabled-keys-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 63 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-pac-enabled-keys-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 67 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-pac-enabled-keys.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 58 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 128-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`, `xlat.h`, `xlat/pr_pac_enabled_keys.h`. functions: `main`. types: none found in this file. macros: `INJ_STR`, `PR_PAC_ENABLE_FLAGS_MASK`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_PAC_RESET_KEYS`, `PR_PAC_ENABLE_FLAGS_MASK`, `PR_PAC_APIAKEY`, `PR_PAC_APIBKEY`, `PR_PAC_APDAKEY`, `PR_PAC_APDBKEY`, `PR_PAC_`, `PR_PAC_SET_ENABLED_KEYS`, `PR_PAC_GET_ENABLED_KEYS`. variant settings: uses success or retval injection path. Source size: 128 lines, 2799 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-reset-keys.c -->
# sources/test-tools/strace/tests/prctl-pac-reset-keys.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-reset-keys.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`, `linux/capability.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_PAC_RESET_KEYS`, `PR_PAC_`, `PR_PAC_APIAKEY`, `PR_PAC_APIBKEY`, `PR_PAC_APDAKEY`, `PR_PAC_APDBKEY`, `PR_PAC_APGAKEY`. Source size: 55 lines, 1267 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-reset-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pdeathsig.c -->
# sources/test-tools/strace/tests/prctl-pdeathsig.c

## Purpose

`sources/test-tools/strace/tests/prctl-pdeathsig.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `signal.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_PDEATHSIG`, `PR_SET_PDEATHSIG`. Source size: 55 lines, 1462 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pdeathsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-ppc-dexcr.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 51 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xraw.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-ppc-dexcr.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 48 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-ppc-dexcr.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 52 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-ppc-dexcr-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 59 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-ppc-dexcr-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 56 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-ppc-dexcr-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 60 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-ppc-dexcr.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-ppc-dexcr.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 51 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-ppc-dexcr.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr.c -->
# sources/test-tools/strace/tests/prctl-ppc-dexcr.c

## Purpose

`sources/test-tools/strace/tests/prctl-ppc-dexcr.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 151-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`, `xlat.h`, `xlat/pr_ppc_dexcr_ctrl_flags.h`. functions: `main`. types: `strval_klong`. macros: `INJ_STR`, `HIBITS`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_PPC_GET_DEXCR`, `PR_PPC_SET_DEXCR`, `PR_PPC_DEXCR_SBHE`, `PR_PPC_DEXCR_IBRTPD`, `PR_PPC_DEXCR_SRAPD`, `PR_PPC_DEXCR_NPHIE`, `PR_PPC_DEXCR_CTRL_EDITABLE`, `PR_PPC_DEXCR_CTRL_SET`, `PR_PPC_DEXCR_CTRL_CLEAR`, `PR_PPC_DEXCR_CTRL_CLEAR_ONEXEC`, `PR_PPC_DEXCR_CTRL_SET_ONEXEC`, `PR_PPC_DEXCR_`, `PR_PPC_DEXCR_CTRL_`, `PR_PPC_DEXCR_CTRL_MASK`. variant settings: uses success or retval injection path. Source size: 151 lines, 3646 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-ppc-dexcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-icache-flush-ctx.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-riscv-icache-flush-ctx.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 64 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-icache-flush-ctx.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xraw.c -->
# sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-icache-flush-ctx.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-riscv-icache-flush-ctx.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 61 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-icache-flush-ctx.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-icache-flush-ctx.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-riscv-icache-flush-ctx.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 65 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-icache-flush-ctx.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c -->
# sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 65-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: `strval_klong`. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_RISCV_V_SET_CONTROL`, `PR_RISCV_V_GET_CONTROL`, `PR_RISCV_CTX_SW_FENCEI_ON`, `PR_RISCV_CTX_SW_FENCEI_OFF`, `PR_RISCV_SCOPE_PER_PROCESS`, `PR_RISCV_SCOPE_PER_THREAD`, `PR_RISCV_SET_ICACHE_FLUSH_CTX`, `PR_RISCV_CTX_`, `PR_RISCV_SCOPE_`. Source size: 65 lines, 1526 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-riscv-v-ctrl.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xraw.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-riscv-v-ctrl.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 51 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-riscv-v-ctrl.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 55 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-riscv-v-ctrl-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 62 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-riscv-v-ctrl-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 59 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-riscv-v-ctrl-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 63 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-riscv-v-ctrl.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-riscv-v-ctrl.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-riscv-v-ctrl.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl.c -->
# sources/test-tools/strace/tests/prctl-riscv-v-ctrl.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-v-ctrl.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 165-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `print_riscv_v_ctrl_val`, `print_riscv_v_ctrl`, `main`. types: none found in this file. macros: `INJ_STR`, `HIBITS`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_RISCV_V_SET_CONTROL`, `PR_RISCV_V_GET_CONTROL`, `PR_RISCV_V_VSTATE_CTRL_DEFAULT`, `PR_RISCV_V_VSTATE_CTRL_OFF`, `PR_RISCV_V_VSTATE_CTRL_ON`, `PR_RISCV_V_VSTATE_CTRL_CUR_MASK`, `PR_RISCV_V_VSTATE_CTRL_NEXT_MASK`, `PR_RISCV_V_VSTATE_CTRL_INHERIT`, `PR_RISCV_V_VSTATE_CTRL_MASK`. variant settings: uses success or retval injection path. Source size: 165 lines, 4155 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-v-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sched-core--pidns-translation.c`. variant settings: compiled with abbreviated xlat rendering; enables pid namespace translation output. Source size: 2 lines, 71 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core--pidns-translation.c`. It sets: compiled with abbreviated xlat rendering; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sched-core--pidns-translation.c`. variant settings: compiled with raw numeric xlat rendering; enables pid namespace translation output. Source size: 2 lines, 68 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core--pidns-translation.c`. It sets: compiled with raw numeric xlat rendering; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sched-core--pidns-translation.c`. variant settings: compiled with verbose xlat rendering; enables pid namespace translation output. Source size: 2 lines, 72 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core--pidns-translation.c`. It sets: compiled with verbose xlat rendering; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-sched-core--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-sched-core.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 56 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sched-core-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sched-core.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 52 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sched-core-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sched-core.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 49 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sched-core-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sched-core.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 53 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sched-core-success--pidns-translation.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 79 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success--pidns-translation.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sched-core-success--pidns-translation.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 76 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success--pidns-translation.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success--pidns-translation.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sched-core-success--pidns-translation.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 80 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success--pidns-translation.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-sched-core-success.c`. variant settings: uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 64 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success.c`. It sets: uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sched-core-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 60 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sched-core-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sched-core-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 61 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success.c -->
# sources/test-tools/strace/tests/prctl-sched-core-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sched-core.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-sched-core.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 52 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sched-core.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core.c -->
# sources/test-tools/strace/tests/prctl-sched-core.c

## Purpose

`sources/test-tools/strace/tests/prctl-sched-core.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 150-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `stdint.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`, `pidns.h`. functions: `main`. types: `strval32`. macros: `NUM_SKIP`, `INJ_STR`. direct syscall numbers: `__NR_gettid`, `__NR_prctl`. notable constants/xlats: `PR_SCHED_CORE`, `PR_SCHED_CORE_GET`, `PR_SCHED_CORE_CREATE`, `PR_SCHED_CORE_SHARE_TO`, `PR_SCHED_CORE_SHARE_FROM`, `PR_SCHED_CORE_`. variant settings: uses success or retval injection path; enables pid namespace translation output. Source size: 150 lines, 3329 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_gettid`, `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sched-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-filter-v.c -->
# sources/test-tools/strace/tests/prctl-seccomp-filter-v.c

## Purpose

`sources/test-tools/strace/tests/prctl-seccomp-filter-v.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 119-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stddef.h`, `unistd.h`, `stdio.h`, `errno.h`, `sys/prctl.h`, `linux/seccomp.h`, `linux/filter.h`, `scno.h`. functions: `main`. types: `sock_filter`, `seccomp_data`, `sock_fprog`. macros: `SOCK_FILTER_ALLOW_SYSCALL`, `SOCK_FILTER_DENY_SYSCALL`, `SOCK_FILTER_KILL_PROCESS`, `PRINT_ALLOW_SYSCALL`, `PRINT_DENY_SYSCALL`. direct syscall numbers: `__NR_get_thread_area`. notable constants/xlats: `PR_SET_SECCOMP`, `SECCOMP_MODE_FILTER`, `SECCOMP_RET_ALLOW`, `SECCOMP_RET_ERRNO`, `SECCOMP_RET_DATA`, `SECCOMP_RET_KILL`, `PR_SET_NO_NEW_PRIVS`, `SECCOMP_RET_KILL_THREAD`. variant settings: uses verbose structure decoding. Source size: 119 lines, 2933 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_get_thread_area`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-filter-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-strict.c -->
# sources/test-tools/strace/tests/prctl-seccomp-strict.c

## Purpose

`sources/test-tools/strace/tests/prctl-seccomp-strict.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_exit`. notable constants/xlats: `PR_SET_SECCOMP`, `SECCOMP_MODE_STRICT`, `SECCOMP_MODE_`. Source size: 46 lines, 1108 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_exit`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-strict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-securebits-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-securebits-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-securebits-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 60 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-securebits-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-securebits-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-securebits-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-securebits-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-securebits-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-securebits-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-securebits-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-securebits-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 61 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-securebits-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success.c -->
# sources/test-tools/strace/tests/prctl-securebits-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-securebits.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-securebits.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 52 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-securebits.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits.c -->
# sources/test-tools/strace/tests/prctl-securebits.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 125-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`, `linux/securebits.h`, `xlat.h`, `xlat/secbits.h`. functions: `prctl`, `main`. types: none found in this file. macros: `INJ_STR`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_SECUREBITS`, `PR_SET_SECUREBITS`. variant settings: uses success or retval injection path. Source size: 125 lines, 3513 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-set-ptracer-success.c`. variant settings: uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 65 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success.c`. It sets: uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success-Xabbrev.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-set-ptracer-success-Xabbrev.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 73 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success-Xabbrev.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-set-ptracer-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 61 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success-Xraw.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-set-ptracer-success-Xraw.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 70 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success-Xraw.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-set-ptracer-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 58 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose--pidns-translation.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose--pidns-translation.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success-Xverbose.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prctl-set-ptracer-success-Xverbose.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 74 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success-Xverbose.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-set-ptracer-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-set-ptracer-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 62 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-set-ptracer-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success.c -->
# sources/test-tools/strace/tests/prctl-set-ptracer-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-set-ptracer-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 81-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`, `pidns.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_PTRACER`, `PR_SET_PTRACER_ANY`. variant settings: uses success or retval injection path; enables pid namespace translation output. Source size: 81 lines, 1919 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set-ptracer-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set_vma.c -->
# sources/test-tools/strace/tests/prctl-set_vma.c

## Purpose

`sources/test-tools/strace/tests/prctl-set_vma.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 82-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `pr_set_vma`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_VMA`, `PR_SET_VMA_ANON_NAME`, `PR_SET_VMA_`. Source size: 82 lines, 2332 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-set_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sme-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sme.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 45 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sme-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sme.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 42 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sme-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sme.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 46 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sme-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sme-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 53 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sme-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sme-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 50 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sme-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sme-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success.c -->
# sources/test-tools/strace/tests/prctl-sme-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-sme.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 45 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme.c -->
# sources/test-tools/strace/tests/prctl-sme.c

## Purpose

`sources/test-tools/strace/tests/prctl-sme.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 156-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `print_sme_vl_arg`, `main`. types: none found in this file. macros: `INJ_STR`, `EXT`, `EXT_STR`, `GLUE_`, `GLUE`, `_`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SME_SET_VL`, `PR_SME_GET_VL`. variant settings: uses success or retval injection path. Source size: 156 lines, 3519 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-spec-inject.c -->
# sources/test-tools/strace/tests/prctl-spec-inject.c

## Purpose

`sources/test-tools/strace/tests/prctl-spec-inject.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 165-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `do_prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_SPECULATION_CTRL`, `PR_GET_SPECULATION_CTRL`, `PR_SPEC_STORE_BYPASS`, `PR_SPEC_INDIRECT_BRANCH`, `PR_SPEC_L1D_FLUSH`, `PR_SPEC_NOT_AFFECTED`, `PR_SPEC_PRCTL`, `PR_SPEC_ENABLE`, `PR_SPEC_FORCE_DISABLE`, `PR_SPEC_DISABLE_NOEXEC`, `PR_SPEC_`. variant settings: uses success or retval injection path. Source size: 165 lines, 4237 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-spec-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-success.sh -->
# sources/test-tools/strace/tests/prctl-success.sh

## Purpose

`sources/test-tools/strace/tests/prctl-success.sh` is a shell harness in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

includes: none found in this file. functions: none found in this file. types: none found in this file. macros: none found in this file. variant settings: uses success or retval injection path. Source size: 67 lines, 1894 bytes.

## Control Flow

The shell harness sources the strace test framework, configures command-line options or injection parameters, runs the compiled test binary under strace, and compares the trace against generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-success.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sve-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`, `EXT`. wrapper include: `prctl-sme.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 4 lines, 109 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sve-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`, `EXT`. wrapper include: `prctl-sme.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 4 lines, 106 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sve-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`, `EXT`. wrapper include: `prctl-sme.c`. variant settings: compiled with verbose xlat rendering. Source size: 4 lines, 110 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-sve-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sve-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-sve-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 53 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sve-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-sve-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sve-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-sve-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 50 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sve-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-sve-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sve-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-sve-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sve-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success.c -->
# sources/test-tools/strace/tests/prctl-sve-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-sme.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`, `EXT`. wrapper include: `prctl-sme.c`. variant settings: uses success or retval injection path. Source size: 4 lines, 109 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-sme.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve.c -->
# sources/test-tools/strace/tests/prctl-sve.c

## Purpose

`sources/test-tools/strace/tests/prctl-sve.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SVE_SET_VL`, `PR_SVE_GET_VL`, `PR_SVE_SET_VL_ONEXEC`, `PR_SVE_VL_INHERIT`. Source size: 71 lines, 1799 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-sve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-syscall-user-dispatch.c -->
# sources/test-tools/strace/tests/prctl-syscall-user-dispatch.c

## Purpose

`sources/test-tools/strace/tests/prctl-syscall-user-dispatch.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`, `linux/capability.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_SYSCALL_USER_DISPATCH`, `PR_SYS_DISPATCH_EXCLUSIVE_ON`, `PR_SYS_DISPATCH_INCLUSIVE_ON`, `PR_SYS_DISPATCH_OFF`, `PR_SYS_DISPATCH_`. Source size: 66 lines, 2128 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-syscall-user-dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-tagged-addr.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 53 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xraw.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-tagged-addr.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 50 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-tagged-addr.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 54 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-tagged-addr-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 61 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xraw.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-success-Xraw.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-success-Xraw.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `prctl-tagged-addr-success.c`. variant settings: compiled with raw numeric xlat rendering; uses success or retval injection path. Source size: 2 lines, 58 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr-success.c`. It sets: compiled with raw numeric xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xverbose.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-success-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-success-Xverbose.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `prctl-tagged-addr-success.c`. variant settings: compiled with verbose xlat rendering; uses success or retval injection path. Source size: 2 lines, 62 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr-success.c`. It sets: compiled with verbose xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-tagged-addr.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-tagged-addr.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 53 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-tagged-addr.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr.c -->
# sources/test-tools/strace/tests/prctl-tagged-addr.c

## Purpose

`sources/test-tools/strace/tests/prctl-tagged-addr.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 143-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `print_tagged_addr_arg`, `main`. types: none found in this file. macros: `INJ_STR`, `HIBITS`. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_TAGGED_ADDR_CTRL`, `PR_GET_TAGGED_ADDR_CTRL`, `PR_TAGGED_ADDR_ENABLE`, `PR_MTE_TCF_MASK`, `PR_MTE_TCF_NONE`, `PR_MTE_TCF_SYNC`, `PR_MTE_TCF_ASYNC`, `PR_MTE_TAG_MASK`, `PR_MTE_TAG_SHIFT`. variant settings: uses success or retval injection path. Source size: 143 lines, 3599 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tagged-addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tid_address.c -->
# sources/test-tools/strace/tests/prctl-tid_address.c

## Purpose

`sources/test-tools/strace/tests/prctl-tid_address.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `sprintaddr`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`, `__NR_set_tid_address`. notable constants/xlats: `PR_GET_TID_ADDRESS`. Source size: 77 lines, 1810 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`, `__NR_set_tid_address`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tid_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tsc.c -->
# sources/test-tools/strace/tests/prctl-tsc.c

## Purpose

`sources/test-tools/strace/tests/prctl-tsc.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_TSC`, `PR_SET_TSC`, `PR_TSC_`, `PR_TSC_SIGSEGV`. Source size: 54 lines, 1447 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-unalign.c -->
# sources/test-tools/strace/tests/prctl-unalign.c

## Purpose

`sources/test-tools/strace/tests/prctl-unalign.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_UNALIGN`, `PR_SET_UNALIGN`, `PR_UNALIGN_NOPRINT`, `PR_UNALIGN_SIGBUS`, `PR_UNALIGN_`. Source size: 50 lines, 1391 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-unalign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl.sh -->
# sources/test-tools/strace/tests/prctl.sh

## Purpose

`sources/test-tools/strace/tests/prctl.sh` is a shell harness in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

includes: none found in this file. functions: none found in this file. types: none found in this file. macros: none found in this file. Source size: 16 lines, 417 bytes.

## Control Flow

The shell harness sources the strace test framework, configures command-line options or injection parameters, runs the compiled test binary under strace, and compares the trace against generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl_marker.c -->
# sources/test-tools/strace/tests/prctl_marker.c

## Purpose

`sources/test-tools/strace/tests/prctl_marker.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `unistd.h`. functions: `prctl_marker`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. Source size: 22 lines, 445 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl_marker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pread64-pwrite64.c -->
# sources/test-tools/strace/tests/pread64-pwrite64.c

## Purpose

`sources/test-tools/strace/tests/pread64-pwrite64.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 203-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`. functions: `dump_str`, `print_hex`, `test_dump`, `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `O_CREAT`, `O_RDONLY`, `O_TRUNC`, `O_WRONLY`. Source size: 203 lines, 4936 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pread64-pwrite64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/preadv-pwritev.c -->
# sources/test-tools/strace/tests/preadv-pwritev.c

## Purpose

`sources/test-tools/strace/tests/preadv-pwritev.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 164-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `fcntl.h`, `stdio.h`, `sys/uio.h`, `unistd.h`. functions: `main`. types: `iovec`. macros: none found in this file. notable constants/xlats: `O_CREAT`, `O_RDONLY`, `O_TRUNC`, `O_WRONLY`. Source size: 164 lines, 4336 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/preadv-pwritev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/preadv.c -->
# sources/test-tools/strace/tests/preadv.c

## Purpose

`sources/test-tools/strace/tests/preadv.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 140-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `fcntl.h`, `stdio.h`, `sys/uio.h`, `unistd.h`. functions: `print_iov`, `print_iovec`, `main`. types: `iovec`. macros: `LEN`. notable constants/xlats: `O_RDONLY`, `O_RDWR`. Source size: 140 lines, 3280 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/preadv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/preadv2-pwritev2.c -->
# sources/test-tools/strace/tests/preadv2-pwritev2.c

## Purpose

`sources/test-tools/strace/tests/preadv2-pwritev2.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 225-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `sys/uio.h`, `unistd.h`. functions: `pr`, `pw`, `dumpio`, `main`. types: `iovec`. macros: none found in this file. direct syscall numbers: `__NR_preadv2`, `__NR_pwritev2`. notable constants/xlats: `O_CREAT`, `O_RDONLY`, `O_TRUNC`, `O_WRONLY`. Source size: 225 lines, 6033 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_preadv2`, `__NR_pwritev2`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/preadv2-pwritev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_maxfd.c -->
# sources/test-tools/strace/tests/print_maxfd.c

## Purpose

`sources/test-tools/strace/tests/print_maxfd.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `sys/resource.h`. functions: `main`. types: none found in this file. macros: none found in this file. Source size: 21 lines, 343 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_maxfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_ppid_tracerpid.c -->
# sources/test-tools/strace/tests/print_ppid_tracerpid.c

## Purpose

`sources/test-tools/strace/tests/print_ppid_tracerpid.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. Source size: 42 lines, 820 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_ppid_tracerpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_quoted_string.c -->
# sources/test-tools/strace/tests/print_quoted_string.c

## Purpose

`sources/test-tools/strace/tests/print_quoted_string.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 143-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `stdlib.h`, `string.h`. functions: `print_quoted_string_ex`, `print_quoted_string`, `print_quoted_cstring`, `print_quoted_stringn`, `print_octal`, `print_quoted_memory_ex`, `print_quoted_memory`, `print_quoted_hex`. types: none found in this file. macros: none found in this file. Source size: 143 lines, 2550 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_quoted_string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_scno_getcwd.sh -->
# sources/test-tools/strace/tests/print_scno_getcwd.sh

## Purpose

`sources/test-tools/strace/tests/print_scno_getcwd.sh` is a shell harness in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

includes: none found in this file. functions: none found in this file. types: none found in this file. macros: none found in this file. Source size: 30 lines, 569 bytes.

## Control Flow

The shell harness sources the strace test framework, configures command-line options or injection parameters, runs the compiled test binary under strace, and compares the trace against generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

The file integrates with the strace test build and comparison harness through local includes and generated expected-output rules.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_scno_getcwd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_time.c -->
# sources/test-tools/strace/tests/print_time.c

## Purpose

`sources/test-tools/strace/tests/print_time.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `time.h`. functions: `print_time_t_ex`, `print_time_t_nsec`, `print_time_t_usec`. types: `tm`. macros: none found in this file. Source size: 54 lines, 1134 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_user_desc.c -->
# sources/test-tools/strace/tests/print_user_desc.c

## Purpose

`sources/test-tools/strace/tests/print_user_desc.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `asm/ldt.h`. functions: `print_user_desc`. types: `user_desc`. macros: none found in this file. Source size: 58 lines, 1265 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_user_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printflags.c -->
# sources/test-tools/strace/tests/printflags.c

## Purpose

`sources/test-tools/strace/tests/printflags.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 63-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `xlat.h`, `stdio.h`. functions: `printflags`. types: `xlat`, `xlat_data`. macros: none found in this file. Source size: 63 lines, 1251 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printflags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-peekdata.c -->
# sources/test-tools/strace/tests/printpath-umovestr-peekdata.c

## Purpose

`sources/test-tools/strace/tests/printpath-umovestr-peekdata.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `test_ucopy.h`, `stdio.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PTRACE_PEEKDATA`. Source size: 27 lines, 535 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-peekdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-undumpable.c -->
# sources/test-tools/strace/tests/printpath-umovestr-undumpable.c

## Purpose

`sources/test-tools/strace/tests/printpath-umovestr-undumpable.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`, `test_ucopy.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PR_SET_DUMPABLE`, `PTRACE_PEEKDATA`. Source size: 39 lines, 824 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-undumpable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr.c -->
# sources/test-tools/strace/tests/printpath-umovestr.c

## Purpose

`sources/test-tools/strace/tests/printpath-umovestr.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `test_ucopy.h`, `limits.h`, `stdio.h`. functions: `main`. types: none found in this file. macros: none found in this file. Source size: 26 lines, 471 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xabbrev.c -->
# sources/test-tools/strace/tests/printsignal-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/printsignal-Xabbrev.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

includes: `printsignal.c`. functions: none found in this file. types: none found in this file. macros: none found in this file. wrapper include: `printsignal.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 1 lines, 25 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printsignal.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xraw.c -->
# sources/test-tools/strace/tests/printsignal-Xraw.c

## Purpose

`sources/test-tools/strace/tests/printsignal-Xraw.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `printsignal.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `printsignal.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 44 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printsignal.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xverbose.c -->
# sources/test-tools/strace/tests/printsignal-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/printsignal-Xverbose.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `printsignal.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `printsignal.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 48 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printsignal.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal.c -->
# sources/test-tools/strace/tests/printsignal.c

## Purpose

`sources/test-tools/strace/tests/printsignal.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `signal.h`, `stdio.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. Source size: 33 lines, 777 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printsignal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printstr.c -->
# sources/test-tools/strace/tests/printstr.c

## Purpose

`sources/test-tools/strace/tests/printstr.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/uio.h`. functions: `main`. types: `iovec`. macros: none found in this file. Source size: 53 lines, 1161 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printstr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven-peekdata.c -->
# sources/test-tools/strace/tests/printstrn-umoven-peekdata.c

## Purpose

`sources/test-tools/strace/tests/printstrn-umoven-peekdata.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `test_ucopy.h`, `stdio.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PTRACE_PEEKDATA`. Source size: 27 lines, 531 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven-peekdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven-undumpable.c -->
# sources/test-tools/strace/tests/printstrn-umoven-undumpable.c

## Purpose

`sources/test-tools/strace/tests/printstrn-umoven-undumpable.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`, `test_ucopy.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PR_SET_DUMPABLE`, `PTRACE_PEEKDATA`. Source size: 39 lines, 822 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven-undumpable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven.c -->
# sources/test-tools/strace/tests/printstrn-umoven.c

## Purpose

`sources/test-tools/strace/tests/printstrn-umoven.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `test_ucopy.h`, `stdio.h`. functions: `main`. types: none found in this file. macros: none found in this file. Source size: 24 lines, 400 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printstrn-umoven.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xabbrev.c -->
# sources/test-tools/strace/tests/printxval-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/printxval-Xabbrev.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `printxval.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_NAME`. wrapper include: `printxval.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printxval.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xraw.c -->
# sources/test-tools/strace/tests/printxval-Xraw.c

## Purpose

`sources/test-tools/strace/tests/printxval-Xraw.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

includes: `printxval.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`, `XLAT_NAME`. wrapper include: `printxval.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 3 lines, 73 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printxval.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xverbose.c -->
# sources/test-tools/strace/tests/printxval-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/printxval-Xverbose.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

includes: `printxval.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`, `XLAT_NAME`. wrapper include: `printxval.c`. variant settings: compiled with verbose xlat rendering. Source size: 3 lines, 81 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `printxval.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printxval-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printxval.c -->
# sources/test-tools/strace/tests/printxval.c

## Purpose

`sources/test-tools/strace/tests/printxval.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 100-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `xlat.h`, `stdio.h`. functions: `lookup_xlat`, `XLAT_NAME`. types: `xlat`, `xlat_data`. macros: none found in this file. Source size: 100 lines, 2044 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printxval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64--pidns-translation.c -->
# sources/test-tools/strace/tests/prlimit64--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prlimit64--pidns-translation.c` is a C test program in the strace tests tree. It provides prlimit64 decoder coverage for resource limits, success paths, and pid namespace translation variants. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prlimit64.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prlimit64.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 49 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prlimit64.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64-success--pidns-translation.c -->
# sources/test-tools/strace/tests/prlimit64-success--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/prlimit64-success--pidns-translation.c` is a C test program in the strace tests tree. It provides prlimit64 decoder coverage for resource limits, success paths, and pid namespace translation variants. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prlimit64-success.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `prlimit64-success.c`. variant settings: uses success or retval injection path; enables pid namespace translation output. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prlimit64-success.c`. It sets: uses success or retval injection path; enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64-success--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64-success.c -->
# sources/test-tools/strace/tests/prlimit64-success.c

## Purpose

`sources/test-tools/strace/tests/prlimit64-success.c` is a C test program in the strace tests tree. It provides prlimit64 decoder coverage for resource limits, success paths, and pid namespace translation variants. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prlimit64.c`. functions: none found in this file. types: none found in this file. macros: `RETVAL_INJECTED`. wrapper include: `prlimit64.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 49 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prlimit64.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64.c -->
# sources/test-tools/strace/tests/prlimit64.c

## Purpose

`sources/test-tools/strace/tests/prlimit64.c` is a C test program in the strace tests tree. It provides prlimit64 decoder coverage for resource limits, success paths, and pid namespace translation variants. The source was read as a complete 111-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `sys/resource.h`, `unistd.h`, `pidns.h`, `xlat.h`, `xlat/resources.h`. functions: `sprint_rlim`, `main`. types: `xlat_data`. macros: `RETVAL_INJECTED`, `INJ_STR`, `INJECT_RETVAL`. direct syscall numbers: `__NR_prlimit64`. notable constants/xlats: `RLIMIT_AS`. variant settings: uses success or retval injection path. Source size: 111 lines, 2567 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prlimit64`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-y.c -->
# sources/test-tools/strace/tests/process_madvise-y.c

## Purpose

`sources/test-tools/strace/tests/process_madvise-y.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_madvise` syscall or printer behavior. The source was read as a complete 5-line file for this report.

## Important APIs, Types, and Functions

includes: `process_madvise.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PATHS`, `FD0_PATH`. wrapper include: `process_madvise.c`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 5 lines, 105 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_madvise.c`. It sets: enables path tracing or decoded path output; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-yy.c -->
# sources/test-tools/strace/tests/process_madvise-yy.c

## Purpose

`sources/test-tools/strace/tests/process_madvise-yy.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_madvise` syscall or printer behavior. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `process_madvise-y.c`. functions: none found in this file. types: none found in this file. macros: `FD0_PATH`. wrapper include: `process_madvise-y.c`. variant settings: enables pidfd fd annotation output. Source size: 2 lines, 72 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_madvise-y.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise.c -->
# sources/test-tools/strace/tests/process_madvise.c

## Purpose

`sources/test-tools/strace/tests/process_madvise.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_madvise` syscall or printer behavior. The source was read as a complete 86-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/mman.h`, `sys/uio.h`. functions: `k_process_madvise`, `main`. types: `iovec`. macros: `FD0_PATH`. direct syscall numbers: `__NR_process_madvise`. notable constants/xlats: `O_WRONLY`. variant settings: enables path tracing or decoded path output. Source size: 86 lines, 2431 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_process_madvise`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_mrelease-y.c -->
# sources/test-tools/strace/tests/process_mrelease-y.c

## Purpose

`sources/test-tools/strace/tests/process_mrelease-y.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_mrelease` syscall or printer behavior. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

includes: `process_mrelease.c`. functions: none found in this file. types: none found in this file. macros: `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`. wrapper include: `process_mrelease.c`. variant settings: enables pidfd fd annotation output. Source size: 4 lines, 135 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_mrelease.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_mrelease-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_mrelease.c -->
# sources/test-tools/strace/tests/process_mrelease.c

## Purpose

`sources/test-tools/strace/tests/process_mrelease.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_mrelease` syscall or printer behavior. The source was read as a complete 59-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`. functions: `sys_process_mrelease`, `main`. types: none found in this file. macros: `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`. direct syscall numbers: `__NR_process_mrelease`. Source size: 59 lines, 1274 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_process_mrelease`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_mrelease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv--pidns-translation.c -->
# sources/test-tools/strace/tests/process_vm_readv--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/process_vm_readv--pidns-translation.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `process_vm_readv.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `process_vm_readv.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 56 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_vm_readv.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv.c -->
# sources/test-tools/strace/tests/process_vm_readv.c

## Purpose

`sources/test-tools/strace/tests/process_vm_readv.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `process_vm_readv_writev.c`. functions: none found in this file. types: none found in this file. macros: `OP`, `OP_NR`, `OP_STR`, `OP_WR`. direct syscall numbers: `__NR_process_vm_readv`. wrapper include: `process_vm_readv_writev.c`. Source size: 18 lines, 376 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_vm_readv_writev.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv_writev.c -->
# sources/test-tools/strace/tests/process_vm_readv_writev.c

## Purpose

`sources/test-tools/strace/tests/process_vm_readv_writev.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 292-line file for this report.

## Important APIs, Types, and Functions

includes: `inttypes.h`, `stdio.h`, `unistd.h`, `sys/uio.h`, `pidns.h`. functions: `print_iov`, `do_call`, `ptr_cast`, `main`. types: `iovec`, `print_iov_arg`, `pid_type`. macros: `in_iovec`, `out_iovec`, `in_iov`, `out_iov`. Source size: 292 lines, 7345 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

`pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv_writev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev--pidns-translation.c -->
# sources/test-tools/strace/tests/process_vm_writev--pidns-translation.c

## Purpose

`sources/test-tools/strace/tests/process_vm_writev--pidns-translation.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `process_vm_writev.c`. functions: none found in this file. types: none found in this file. macros: `PIDNS_TRANSLATION`. wrapper include: `process_vm_writev.c`. variant settings: enables pid namespace translation output. Source size: 2 lines, 57 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_vm_writev.c`. It sets: enables pid namespace translation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev.c -->
# sources/test-tools/strace/tests/process_vm_writev.c

## Purpose

`sources/test-tools/strace/tests/process_vm_writev.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `process_vm_readv_writev.c`. functions: none found in this file. types: none found in this file. macros: `OP`, `OP_NR`, `OP_STR`, `OP_WR`. direct syscall numbers: `__NR_process_vm_writev`. wrapper include: `process_vm_readv_writev.c`. Source size: 18 lines, 380 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_vm_readv_writev.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6-common.c -->
# sources/test-tools/strace/tests/pselect6-common.c

## Purpose

`sources/test-tools/strace/tests/pselect6-common.c` is a C test program in the strace tests tree. It provides pselect6 decoder coverage for fd sets, timeout structures, signal masks, and time64 or common helper variants. The source was read as a complete 180-line file for this report.

## Important APIs, Types, and Functions

includes: `nsig.h`, `assert.h`, `stdio.h`, `unistd.h`, `sys/select.h`, `sys/time.h`, `kernel_timespec.h`. functions: `pselect6`, `handler`, `main`. types: `sigset_argpack`, `sigaction`, `itimerval`. macros: none found in this file. notable constants/xlats: `FD_SET`, `FD_ZERO`, `FD_SETSIZE`. Source size: 180 lines, 5327 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6.c -->
# sources/test-tools/strace/tests/pselect6.c

## Purpose

`sources/test-tools/strace/tests/pselect6.c` is a C test program in the strace tests tree. It provides pselect6 decoder coverage for fd sets, timeout structures, signal masks, and time64 or common helper variants. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `pselect6-common.c`. functions: none found in this file. types: none found in this file. macros: `SYSCALL_NR`, `SYSCALL_NAME`, `pselect6_timespec_t`. direct syscall numbers: `__NR_pselect6`, `__NR_pselect6_time64`. wrapper include: `pselect6-common.c`. Source size: 30 lines, 528 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pselect6-common.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6_time64.c -->
# sources/test-tools/strace/tests/pselect6_time64.c

## Purpose

`sources/test-tools/strace/tests/pselect6_time64.c` is a C test program in the strace tests tree. It provides pselect6 decoder coverage for fd sets, timeout structures, signal masks, and time64 or common helper variants. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `pselect6-common.c`. functions: none found in this file. types: none found in this file. macros: `SYSCALL_NR`, `SYSCALL_NAME`, `pselect6_timespec_t`. direct syscall numbers: `__NR_pselect6_time64`. wrapper include: `pselect6-common.c`. Source size: 25 lines, 462 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pselect6-common.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6_time64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xabbrev.c -->
# sources/test-tools/strace/tests/ptrace-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/ptrace-Xabbrev.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `ptrace.c`. variant settings: compiled with abbreviated xlat rendering. Source size: 2 lines, 42 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace.c`. It sets: compiled with abbreviated xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xraw.c -->
# sources/test-tools/strace/tests/ptrace-Xraw.c

## Purpose

`sources/test-tools/strace/tests/ptrace-Xraw.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `ptrace.c`. variant settings: compiled with raw numeric xlat rendering. Source size: 2 lines, 39 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace.c`. It sets: compiled with raw numeric xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xverbose.c -->
# sources/test-tools/strace/tests/ptrace-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/ptrace-Xverbose.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `ptrace.c`. variant settings: compiled with verbose xlat rendering. Source size: 2 lines, 43 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace.c`. It sets: compiled with verbose xlat rendering. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xabbrev.c -->
# sources/test-tools/strace/tests/ptrace-y-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/ptrace-y-Xabbrev.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace-y.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `ptrace-y.c`. variant settings: compiled with abbreviated xlat rendering; enables pidfd fd annotation output. Source size: 2 lines, 44 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace-y.c`. It sets: compiled with abbreviated xlat rendering; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xraw.c -->
# sources/test-tools/strace/tests/ptrace-y-Xraw.c

## Purpose

`sources/test-tools/strace/tests/ptrace-y-Xraw.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace-y.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_RAW`. wrapper include: `ptrace-y.c`. variant settings: compiled with raw numeric xlat rendering; enables pidfd fd annotation output. Source size: 2 lines, 41 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace-y.c`. It sets: compiled with raw numeric xlat rendering; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xverbose.c -->
# sources/test-tools/strace/tests/ptrace-y-Xverbose.c

## Purpose

`sources/test-tools/strace/tests/ptrace-y-Xverbose.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace-y.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_VERBOSE`. wrapper include: `ptrace-y.c`. variant settings: compiled with verbose xlat rendering; enables pidfd fd annotation output. Source size: 2 lines, 45 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace-y.c`. It sets: compiled with verbose xlat rendering; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y.c -->
# sources/test-tools/strace/tests/ptrace-y.c

## Purpose

`sources/test-tools/strace/tests/ptrace-y.c` is a C test program in the strace tests tree. It provides ptrace decoder coverage for request xlat modes, pid/fd annotation variants, raw versus verbose output, and architecture-sensitive ptrace structures. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

includes: `ptrace.c`. functions: none found in this file. types: none found in this file. macros: `NULL_FD_STR`, `SKIP_IF_PROC_IS_UNAVAILABLE`. wrapper include: `ptrace.c`. variant settings: enables pidfd fd annotation output. Source size: 3 lines, 131 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `ptrace.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace-y.c -->
