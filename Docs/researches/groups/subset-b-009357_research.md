# subset-b-009357 research

Grouped research report for 169 strace scheduler, socket, seccomp, signal, SysV IPC, credential, xattr, namespace, stat, and stack-call test sources. Each section preserves the exact source path and is wrapped for deterministic reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetattr.c -->
# sources/test-tools/strace/tests/sched_xetattr.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `sys_sched_getattr`, `sys_sched_setattr`, `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, plus 2 more. Preprocessor knobs/macros are none visible in this file. The file has 463 source lines and was read from `sources/test-tools/strace/tests/sched_xetattr.c`.

Control flow: `main` and helpers (`sys_sched_getattr`, `sys_sched_setattr`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 13 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It exercises both `sched_getattr` and `sched_setattr`, including null pointers, bogus pids, oversized and undersized `struct sched_attr`, util-clamp fields, flag decoding, f8-filled high bits, and pid namespace print leaders.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `sched.h`, `unistd.h`, `linux/sched/types.h`, `pidns.h`, `xlat.h`, `xlat/schedulers.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; pid namespace runs include translated leader lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetparam--pidns-translation.c -->
# sources/test-tools/strace/tests/sched_xetparam--pidns-translation.c

Purpose: Macro-variant wrapper for `sched_xetparam.c`. It sets `PIDNS_TRANSLATION` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`. Preprocessor knobs/macros are `PIDNS_TRANSLATION`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetparam--pidns-translation.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetparam.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetparam.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetparam--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetparam.c -->
# sources/test-tools/strace/tests/sched_xetparam.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_sched_getparam`, `__NR_sched_setparam`. Preprocessor knobs/macros are none visible in this file. The file has 44 source lines and was read from `sources/test-tools/strace/tests/sched_xetparam.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It targets `sched_getparam`/`sched_setparam` with live pid, pid-zero, bogus pid, `struct sched_param`, invalid pointers, and optional pid namespace translation.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `pidns.h`, `sched.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive.

Test signals: successful self-test prints `+++ exited with 0 +++`; pid namespace runs include translated leader lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xabbrev.c -->
# sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xabbrev.c

Purpose: Macro-variant wrapper for `sched_xetscheduler--pidns-translation.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler--pidns-translation.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler--pidns-translation.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xraw.c -->
# sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xraw.c

Purpose: Macro-variant wrapper for `sched_xetscheduler--pidns-translation.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler--pidns-translation.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler--pidns-translation.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xverbose.c -->
# sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xverbose.c

Purpose: Macro-variant wrapper for `sched_xetscheduler--pidns-translation.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler--pidns-translation.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler--pidns-translation.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation.c -->
# sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation.c

Purpose: Macro-variant wrapper for `sched_xetscheduler.c`. It sets `PIDNS_TRANSLATION` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`. Preprocessor knobs/macros are `PIDNS_TRANSLATION`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xabbrev.c -->
# sources/test-tools/strace/tests/sched_xetscheduler-Xabbrev.c

Purpose: Macro-variant wrapper for `sched_xetscheduler.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xraw.c -->
# sources/test-tools/strace/tests/sched_xetscheduler-Xraw.c

Purpose: Macro-variant wrapper for `sched_xetscheduler.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xverbose.c -->
# sources/test-tools/strace/tests/sched_xetscheduler-Xverbose.c

Purpose: Macro-variant wrapper for `sched_xetscheduler.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sched_xetscheduler.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sched_xetscheduler.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler.c -->
# sources/test-tools/strace/tests/sched_xetscheduler.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `scheduler_str`, `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, plus 2 more. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 123 source lines and was read from `sources/test-tools/strace/tests/sched_xetscheduler.c`.

Control flow: `main` and helpers (`scheduler_str`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It covers `sched_getscheduler` and `sched_setscheduler`, policy xlat modes, reset-on-fork flag handling, pid rendering, and errno/result formatting.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `pidns.h`, `sched.h`, `stdio.h`, `unistd.h`, `xlat/schedulers.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; pid namespace runs include translated leader lines; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetscheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_yield.c -->
# sources/test-tools/strace/tests/sched_yield.c

Purpose: Standalone or shared strace regression test for scheduler syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sched_getattr`, `sched_setattr`, `sched_getparam`, `sched_setparam`, `sched_getscheduler`, `sched_setscheduler`, `sched_yield`, `__NR_sched_yield`. Preprocessor knobs/macros are none visible in this file. The file has 23 source lines and was read from `sources/test-tools/strace/tests/sched_yield.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/scm_credentials.c -->
# sources/test-tools/strace/tests/scm_credentials.c

Purpose: Standalone or shared strace regression test for ancillary socket message decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `print_ucred`, `main`. Important syscall/test APIs and data types are `sendmsg`, `recvmsg`, `cmsghdr`, `SCM_CREDENTIALS`, `SCM_RIGHTS`, `SCM_PIDFD`, `msghdr`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 114 source lines and was read from `sources/test-tools/strace/tests/scm_credentials.c`.

Control flow: `main` and helpers (`print_ucred`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 11 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It builds UNIX datagram ancillary data carrying `SCM_CREDENTIALS` and verifies decoded `struct ucred` fields for pid, uid, and gid.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/scm_credentials.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/scm_pidfd-success.c -->
# sources/test-tools/strace/tests/scm_pidfd-success.c

Purpose: Standalone or shared strace regression test for ancillary socket message decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendmsg`, `recvmsg`, `cmsghdr`, `SCM_CREDENTIALS`, `SCM_RIGHTS`, `SCM_PIDFD`, `msghdr`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 71 source lines and was read from `sources/test-tools/strace/tests/scm_pidfd-success.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `xlat/scmvals.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/scm_pidfd-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/scm_pidfd.c -->
# sources/test-tools/strace/tests/scm_pidfd.c

Purpose: Standalone or shared strace regression test for ancillary socket message decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `print_pidfd`, `main`. Important syscall/test APIs and data types are `sendmsg`, `recvmsg`, `cmsghdr`, `SCM_CREDENTIALS`, `SCM_RIGHTS`, `SCM_PIDFD`, `msghdr`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 116 source lines and was read from `sources/test-tools/strace/tests/scm_pidfd.c`.

Control flow: `main` and helpers (`print_pidfd`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 10 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It creates ancillary `SCM_PIDFD` control messages and checks pidfd formatting through success, failure, and fd-path variants.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `xlat/sock_options.h`, `xlat/scmvals.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/scm_pidfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/scm_rights.c -->
# sources/test-tools/strace/tests/scm_rights.c

Purpose: Standalone or shared strace regression test for ancillary socket message decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendmsg`, `recvmsg`, `cmsghdr`, `SCM_CREDENTIALS`, `SCM_RIGHTS`, `SCM_PIDFD`, `msghdr`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 86 source lines and was read from `sources/test-tools/strace/tests/scm_rights.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It sends fd rights through UNIX socket ancillary data and validates fd array printing, truncation behavior, and path-qualified descriptor output.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `fcntl.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/scm_rights.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/scno_tampering.sh -->
# sources/test-tools/strace/tests/scno_tampering.sh

Purpose: Shell harness for a strace self-test scenario. It runs compiled test programs through the local test-driver helpers and validates strace output behavior from the shell layer.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 13 source lines and was read from `sources/test-tools/strace/tests/scno_tampering.sh`.

Control flow: The shell flow sources the test framework, chooses the compiled test program and strace options, runs the trace, then compares normalized output against expectations.

State and persistence behavior: state is limited to temporary trace/output files managed by the test framework.

Dependencies: Direct dependencies are `init.sh`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: shell comparison succeeds through the shared strace test harness.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/scno_tampering.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-filter-v.c -->
# sources/test-tools/strace/tests/seccomp-filter-v.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `get_thread_area`, `__NR_seccomp`. Preprocessor knobs/macros are `SOCK_FILTER_KILL_PROCESS=\`. The file has 188 source lines and was read from `sources/test-tools/strace/tests/seccomp-filter-v.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It is the verbose-oriented seccomp filter test, emphasizing BPF instruction formatting and SECCOMP return/action names.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `errno.h`, `stddef.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`, `linux/seccomp.h`, `linux/filter.h`, `scno.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-filter-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-filter.c -->
# sources/test-tools/strace/tests/seccomp-filter.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_seccomp`. Preprocessor knobs/macros are `N=7`. The file has 48 source lines and was read from `sources/test-tools/strace/tests/seccomp-filter.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It installs seccomp filters through `prctl`/`seccomp` paths and verifies filter instruction decoding and verbose flag variants.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/seccomp.h`, `linux/filter.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-strict.c -->
# sources/test-tools/strace/tests/seccomp-strict.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `exit`, `__NR_seccomp`, `__NR_exit`. Preprocessor knobs/macros are none visible in this file. The file has 47 source lines and was read from `sources/test-tools/strace/tests/seccomp-strict.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp-strict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_action_avail.c -->
# sources/test-tools/strace/tests/seccomp_get_action_avail.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_seccomp`, `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_seccomp`. Preprocessor knobs/macros are none visible in this file. The file has 77 source lines and was read from `sources/test-tools/strace/tests/seccomp_get_action_avail.c`.

Control flow: `main` and helpers (`k_seccomp`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/seccomp.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_action_avail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_notif_sizes-success.c -->
# sources/test-tools/strace/tests/seccomp_get_notif_sizes-success.c

Purpose: Macro-variant wrapper for `seccomp_get_notif_sizes.c`. It sets `INJECT_RETVAL=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`. Preprocessor knobs/macros are `INJECT_RETVAL=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/seccomp_get_notif_sizes-success.c`.

Control flow: At compile time this wrapper defines its knobs and includes `seccomp_get_notif_sizes.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `seccomp_get_notif_sizes.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; seccomp behavior depends on kernel support and filter side effects.

Test signals: injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_notif_sizes-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_notif_sizes.c -->
# sources/test-tools/strace/tests/seccomp_get_notif_sizes.c

Purpose: Standalone or shared strace regression test for seccomp syscall and filter decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_seccomp`, `main`. Important syscall/test APIs and data types are `seccomp`, `prctl`, `SECCOMP_*`, `sock_filter`, `BPF_STMT`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_seccomp`. Preprocessor knobs/macros are `SECCOMP_GET_NOTIF_SIZES=3`, `INJECT_RETVAL=0`, `INJ_STR=" (INJECTED)"`, `INJ_STR=""`. The file has 97 source lines and was read from `sources/test-tools/strace/tests/seccomp_get_notif_sizes.c`.

Control flow: `main` and helpers (`k_seccomp`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/seccomp.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; seccomp behavior depends on kernel support and filter side effects.

Test signals: successful self-test prints `+++ exited with 0 +++`; injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/seccomp_get_notif_sizes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/secontext.c -->
# sources/test-tools/strace/tests/secontext.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `secontext_format`, `strip_trailing_newlines`, `get_secontext_field`, `raw_expected_secontext_full_file`, `raw_expected_secontext_short_file`, `raw_secontext_full_file`, `raw_secontext_full_fd`, `get_secontext_field_file`, `get_secontext_field_fd`, `raw_secontext_short_file`, `raw_secontext_short_fd`, `raw_secontext_full_pid`, plus 9 more. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are `TEST_SECONTEXT`. The file has 338 source lines and was read from `sources/test-tools/strace/tests/secontext.c`.

Control flow: `main` and helpers (`secontext_format`, `strip_trailing_newlines`, `get_secontext_field`, `raw_expected_secontext_full_file`, `raw_expected_secontext_short_file`, `raw_secontext_full_file`, `raw_secontext_full_fd`, `get_secontext_field_file`, `get_secontext_field_fd`, `raw_secontext_short_file`, plus 11 more) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 3 explicit `for` loops and 19 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It implements the SELinux/security-context helper test body, including formatting wrappers for fd, file, process, and missing-context cases.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `errno.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`, `selinux/selinux.h`, `selinux/label.h`, `xmalloc.h`, `secontext.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/secontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/secontext.h -->
# sources/test-tools/strace/tests/secontext.h

Purpose: Shared test header that provides inline helpers and macros for related strace decoder tests. It is included by companion tests rather than run directly; the code centralizes repeated helper behavior so output formatting stays consistent across the suite.

Important APIs/types/functions: Visible local functions are `get_secontext_field`, `get_secontext_field_fd`, `get_secontext_field_file`, `reset_secontext_file`, `update_secontext_field`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 105 source lines and was read from `sources/test-tools/strace/tests/secontext.h`.

Control flow: No `main` is present. Including tests call the inline helpers/macros, which branch on build-time feature macros and either call real helpers or return empty test strings.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `xmalloc.h`, `errno.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/secontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/segv_accerr.c -->
# sources/test-tools/strace/tests/segv_accerr.c

Purpose: Standalone or shared strace regression test for signal fault detail decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `SIGSEGV`, `si_code`, `SEGV_*`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are none visible in this file. The file has 53 source lines and was read from `sources/test-tools/strace/tests/segv_accerr.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/mman.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/segv_accerr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/segv_pkuerr.c -->
# sources/test-tools/strace/tests/segv_pkuerr.c

Purpose: Standalone or shared strace regression test for signal fault detail decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `SIGSEGV`, `si_code`, `SEGV_*`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are none visible in this file. The file has 55 source lines and was read from `sources/test-tools/strace/tests/segv_pkuerr.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/mman.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/segv_pkuerr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/select-P.c -->
# sources/test-tools/strace/tests/select-P.c

Purpose: Macro-variant wrapper for `select.c`. It sets `PATH_TRACING_FD=9` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`. Preprocessor knobs/macros are `PATH_TRACING_FD=9`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/select-P.c`.

Control flow: At compile time this wrapper defines its knobs and includes `select.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `select.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/select-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7-9.c -->
# sources/test-tools/strace/tests/select-trace-fd-7-9.c

Purpose: Macro-variant wrapper for `select.c`. It sets `TRACING_FD=7`, `PATH_TRACING_FD=9` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`. Preprocessor knobs/macros are `TRACING_FD=7`, `PATH_TRACING_FD=9`. The file has 3 source lines and was read from `sources/test-tools/strace/tests/select-trace-fd-7-9.c`.

Control flow: At compile time this wrapper defines its knobs and includes `select.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `select.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7-P.c -->
# sources/test-tools/strace/tests/select-trace-fd-7-P.c

Purpose: Macro-variant wrapper for `select.c`. It sets `TRACING_FD=7`, `PATH_TRACING_FD=9` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`. Preprocessor knobs/macros are `TRACING_FD=7`, `PATH_TRACING_FD=9`. The file has 3 source lines and was read from `sources/test-tools/strace/tests/select-trace-fd-7-P.c`.

Control flow: At compile time this wrapper defines its knobs and includes `select.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `select.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7.c -->
# sources/test-tools/strace/tests/select-trace-fd-7.c

Purpose: Macro-variant wrapper for `select.c`. It sets `TRACING_FD=7` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`. Preprocessor knobs/macros are `TRACING_FD=7`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/select-trace-fd-7.c`.

Control flow: At compile time this wrapper defines its knobs and includes `select.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `select.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/select-trace-fd-7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/select.c -->
# sources/test-tools/strace/tests/select.c

Purpose: Standalone or shared strace regression test for select fd-set/path-tracing decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `select`, `fd_set`, `FD_SET`, `timeval`, `SKIP_MAIN_UNDEFINED`, `_newselect`. Preprocessor knobs/macros are `TEST_SYSCALL_NR=__NR_select`, `TEST_SYSCALL_STR="select"`. The file has 22 source lines and was read from `sources/test-tools/strace/tests/select.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xselect.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/select.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semop-common.c -->
# sources/test-tools/strace/tests/semop-common.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semop`, `cleanup`, `main`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 96 source lines and was read from `sources/test-tools/strace/tests/semop-common.c`.

Control flow: `main` and helpers (`k_semop`, `cleanup`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; a static SysV IPC id is cleaned up through an exit handler; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `sys/ipc.h`, `sys/sem.h`, `stdint.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `xlat/semop_flags.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semop-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semop-indirect.c -->
# sources/test-tools/strace/tests/semop-indirect.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semop`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `ipc`, `__NR_ipc`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 39 source lines and was read from `sources/test-tools/strace/tests/semop-indirect.c`.

Control flow: `main` and helpers (`k_semop`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semop-common.c`, `xlat/ipccalls.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semop-indirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semop.c -->
# sources/test-tools/strace/tests/semop.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semop`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `SKIP_MAIN_UNDEFINED`, `__NR_semop`. Preprocessor knobs/macros are none visible in this file. The file has 34 source lines and was read from `sources/test-tools/strace/tests/semop.c`.

Control flow: `main` and helpers (`k_semop`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semop-common.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-common.c -->
# sources/test-tools/strace/tests/semtimedop-common.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semtimedop_imp`, `k_semtimedop`, `cleanup`, `main`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 168 source lines and was read from `sources/test-tools/strace/tests/semtimedop-common.c`.

Control flow: `main` and helpers (`k_semtimedop_imp`, `k_semtimedop`, `cleanup`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 6 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; a static SysV IPC id is cleaned up through an exit handler; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `sys/ipc.h`, `sys/sem.h`, `stdint.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `kernel_timespec.h`, `xlat/semop_flags.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-ipc.c -->
# sources/test-tools/strace/tests/semtimedop-ipc.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semtimedop_imp`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `ipc`, `__NR_ipc`. Preprocessor knobs/macros are `SYSCALL_NAME="semtimedop"`, `semtimedop_timespec_t=kernel_timespec64_t`, `semtimedop_timespec_t=kernel_timespec32_t`, `XLAT_MACROS_ONLY`. The file has 50 source lines and was read from `sources/test-tools/strace/tests/semtimedop-ipc.c`.

Control flow: `main` and helpers (`k_semtimedop_imp`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semtimedop-common.c`, `xlat/ipccalls.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-syscall.c -->
# sources/test-tools/strace/tests/semtimedop-syscall.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_semtimedop_imp`. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`. Preprocessor knobs/macros are none visible in this file. The file has 18 source lines and was read from `sources/test-tools/strace/tests/semtimedop-syscall.c`.

Control flow: `main` and helpers (`k_semtimedop_imp`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `semtimedop-common.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop.c -->
# sources/test-tools/strace/tests/semtimedop.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `SKIP_MAIN_UNDEFINED`, `semtimedop_time64`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_semtimedop`, `SYSCALL_NAME="semtimedop"`, `semtimedop_timespec_t=kernel_timespec32_t`, `semtimedop_timespec_t=kernel_timespec64_t`. The file has 30 source lines and was read from `sources/test-tools/strace/tests/semtimedop.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semtimedop-syscall.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop_time64.c -->
# sources/test-tools/strace/tests/semtimedop_time64.c

Purpose: Standalone or shared strace regression test for System V semaphore decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `semop`, `semtimedop`, `semget`, `semctl`, `sembuf`, `SKIP_MAIN_UNDEFINED`, `semtimedop_time64`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_semtimedop_time64`, `SYSCALL_NAME="semtimedop_time64"`, `semtimedop_timespec_t=kernel_timespec64_t`. The file has 25 source lines and was read from `sources/test-tools/strace/tests/semtimedop_time64.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `semtimedop-syscall.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/semtimedop_time64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sendfile.c -->
# sources/test-tools/strace/tests/sendfile.c

Purpose: Standalone or shared strace regression test for sendfile offset/count decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendfile`, `sendfile64`, `off_t`, `loff_t`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sendfile`. Preprocessor knobs/macros are none visible in this file. The file has 97 source lines and was read from `sources/test-tools/strace/tests/sendfile.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 7 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sendfile64.c -->
# sources/test-tools/strace/tests/sendfile64.c

Purpose: Standalone or shared strace regression test for sendfile offset/count decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sendfile`, `sendfile64`, `off_t`, `loff_t`, `getsockopt`, `setsockopt`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sendfile64`. Preprocessor knobs/macros are none visible in this file. The file has 96 source lines and was read from `sources/test-tools/strace/tests/sendfile64.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 7 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sendfile64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xabbrev.c -->
# sources/test-tools/strace/tests/set_mempolicy-Xabbrev.c

Purpose: Macro-variant wrapper for `set_mempolicy.c`. It sets none visible in this file before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`. Preprocessor knobs/macros are none visible in this file. The file has 1 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `set_mempolicy.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `set_mempolicy.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xraw.c -->
# sources/test-tools/strace/tests/set_mempolicy-Xraw.c

Purpose: Macro-variant wrapper for `set_mempolicy.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `set_mempolicy.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `set_mempolicy.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xverbose.c -->
# sources/test-tools/strace/tests/set_mempolicy-Xverbose.c

Purpose: Macro-variant wrapper for `set_mempolicy.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `set_mempolicy.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `set_mempolicy.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy.c -->
# sources/test-tools/strace/tests/set_mempolicy.c

Purpose: Standalone or shared strace regression test for NUMA memory policy decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_set_mempolicy`, `print_nodes`, `test_offset`, `main`. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `__NR_set_mempolicy`. Preprocessor knobs/macros are `MAX_STRLEN=3`, `out_str=raw`, `out_str=verbose`, `out_str=abbrev`. The file has 201 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy.c`.

Control flow: `main` and helpers (`k_set_mempolicy`, `print_nodes`, `test_offset`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 8 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It drives `set_mempolicy` with many modes, nodemask sizes, offsets, and xlat styles to validate NUMA policy and node-list decoding.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy_home_node.c -->
# sources/test-tools/strace/tests/set_mempolicy_home_node.c

Purpose: Standalone or shared strace regression test for NUMA memory policy decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `sys_set_mempolicy_home_node`, `main`. Important syscall/test APIs and data types are `set_mempolicy`, `set_mempolicy_home_node`, `nodemask`, `MPOL_*`, `__NR_set_mempolicy_home_node`. Preprocessor knobs/macros are `KUL_1=((unsigned long long) (kernel_ulong_t) -1ULL)`. The file has 58 source lines and was read from `sources/test-tools/strace/tests/set_mempolicy_home_node.c`.

Control flow: `main` and helpers (`sys_set_mempolicy_home_node`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_mempolicy_home_node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_ptracer_any.c -->
# sources/test-tools/strace/tests/set_ptracer_any.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 30 source lines and was read from `sources/test-tools/strace/tests/set_ptracer_any.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `unistd.h`, `sys/prctl.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_ptracer_any.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_sigblock.c -->
# sources/test-tools/strace/tests/set_sigblock.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 33 source lines and was read from `sources/test-tools/strace/tests/set_sigblock.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`, `stdlib.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_sigblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/set_sigign.c -->
# sources/test-tools/strace/tests/set_sigign.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 29 source lines and was read from `sources/test-tools/strace/tests/set_sigign.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`, `stdlib.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/set_sigign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setdomainname.c -->
# sources/test-tools/strace/tests/setdomainname.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `setdomainname`, `__NR_setdomainname`. Preprocessor knobs/macros are none visible in this file. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setdomainname.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setdomainname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setfsgid.c -->
# sources/test-tools/strace/tests/setfsgid.c

Purpose: Standalone or shared strace regression test for filesystem credential syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setfsuid`, `setfsgid`, `setfsgid32`, `getegid`, `__NR_getegid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setfsgid`, `SYSCALL_NAME="setfsgid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_getegid)`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setfsgid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setfsugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setfsgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setfsgid32.c -->
# sources/test-tools/strace/tests/setfsgid32.c

Purpose: Standalone or shared strace regression test for filesystem credential syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setfsuid`, `setfsgid`, `SKIP_MAIN_UNDEFINED`, `setfsgid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setfsgid32`, `SYSCALL_NAME="setfsgid32"`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 23 source lines and was read from `sources/test-tools/strace/tests/setfsgid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setfsugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setfsgid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setfsugid.c -->
# sources/test-tools/strace/tests/setfsugid.c

Purpose: Standalone or shared strace regression test for filesystem credential syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `printuid`, `main`. Important syscall/test APIs and data types are `setfsuid`, `setfsgid`. Preprocessor knobs/macros are none visible in this file. The file has 55 source lines and was read from `sources/test-tools/strace/tests/setfsugid.c`.

Control flow: `main` and helpers (`printuid`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setfsugid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setfsuid.c -->
# sources/test-tools/strace/tests/setfsuid.c

Purpose: Standalone or shared strace regression test for filesystem credential syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setfsuid`, `setfsgid`, `setfsuid32`, `geteuid`, `__NR_geteuid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setfsuid`, `SYSCALL_NAME="setfsuid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_geteuid)`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setfsuid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setfsugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setfsuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setfsuid32.c -->
# sources/test-tools/strace/tests/setfsuid32.c

Purpose: Standalone or shared strace regression test for filesystem credential syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setfsuid`, `setfsgid`, `SKIP_MAIN_UNDEFINED`, `setfsuid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setfsuid32`, `SYSCALL_NAME="setfsuid32"`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 23 source lines and was read from `sources/test-tools/strace/tests/setfsuid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setfsugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setfsuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setgid.c -->
# sources/test-tools/strace/tests/setgid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setgid`, `getgid`, `overflowgid`, `setgid32`, `getegid`, `__NR_getegid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setgid`, `SYSCALL_NAME="setgid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_getegid)`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 26 source lines and was read from `sources/test-tools/strace/tests/setgid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: credential tests must avoid assuming privilege changes succeed.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setgid32.c -->
# sources/test-tools/strace/tests/setgid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setgid`, `getgid`, `overflowgid`, `SKIP_MAIN_UNDEFINED`, `setgid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setgid32`, `SYSCALL_NAME="setgid32"`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setgid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; credential tests must avoid assuming privilege changes succeed.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setgid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setgroups.c -->
# sources/test-tools/strace/tests/setgroups.c

Purpose: Standalone or shared strace regression test for supplementary group syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `printuid`, `main`. Important syscall/test APIs and data types are `setgroups`, `gid_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `setgroups32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setgroups32`, `SYSCALL_NAME="setgroups32"`, `GID_TYPE=unsigned int`, `SYSCALL_NR=__NR_setgroups`, `SYSCALL_NAME="setgroups"`, `GID_TYPE=unsigned short`. The file has 157 source lines and was read from `sources/test-tools/strace/tests/setgroups.c`.

Control flow: `main` and helpers (`printuid`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; credential tests must avoid assuming privilege changes succeed.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setgroups32.c -->
# sources/test-tools/strace/tests/setgroups32.c

Purpose: Standalone or shared strace regression test for supplementary group syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setgroups`, `gid_t`, `SKIP_MAIN_UNDEFINED`, `setgroups32`. Preprocessor knobs/macros are none visible in this file. The file has 19 source lines and was read from `sources/test-tools/strace/tests/setgroups32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setgroups.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; credential tests must avoid assuming privilege changes succeed.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setgroups32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sethostname.c -->
# sources/test-tools/strace/tests/sethostname.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `sethostname`, `__NR_sethostname`. Preprocessor knobs/macros are none visible in this file. The file has 45 source lines and was read from `sources/test-tools/strace/tests/sethostname.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/utsname.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sethostname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setns-report-ns-id.c -->
# sources/test-tools/strace/tests/setns-report-ns-id.c

Purpose: Standalone or shared strace regression test for namespace switching decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `setns`, `open`, `/proc/self/ns`, `CLONE_NEW*`, `unshare`, `__NR_unshare`, `__NR_setns`. Preprocessor knobs/macros are none visible in this file. The file has 49 source lines and was read from `sources/test-tools/strace/tests/setns-report-ns-id.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`, `fcntl.h`, `errno.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setns-report-ns-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setns.c -->
# sources/test-tools/strace/tests/setns.c

Purpose: Standalone or shared strace regression test for namespace switching decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_setns`, `main`. Important syscall/test APIs and data types are `setns`, `open`, `/proc/self/ns`, `CLONE_NEW*`, `__NR_setns`. Preprocessor knobs/macros are none visible in this file. The file has 63 source lines and was read from `sources/test-tools/strace/tests/setns.c`.

Control flow: `main` and helpers (`k_setns`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setpgrp-exec.c -->
# sources/test-tools/strace/tests/setpgrp-exec.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 22 source lines and was read from `sources/test-tools/strace/tests/setpgrp-exec.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setpgrp-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setregid.c -->
# sources/test-tools/strace/tests/setregid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setreuid`, `setregid`, `setregid32`, `getegid`, `__NR_getegid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setregid`, `SYSCALL_NAME="setregid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_getegid)`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 26 source lines and was read from `sources/test-tools/strace/tests/setregid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setreugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setregid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setregid32.c -->
# sources/test-tools/strace/tests/setregid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setregid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setregid32`, `SYSCALL_NAME="setregid32"`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setregid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setreugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setregid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setresgid.c -->
# sources/test-tools/strace/tests/setresgid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setresgid32`, `getegid`, `__NR_getegid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setresgid`, `SYSCALL_NAME="setresgid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_getegid)`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 32 source lines and was read from `sources/test-tools/strace/tests/setresgid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setresugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setresgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setresgid32.c -->
# sources/test-tools/strace/tests/setresgid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setresgid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setresgid32`, `SYSCALL_NAME="setresgid32"`, `UGID_TYPE=int`, `GETUGID=getegid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setresgid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setresugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setresgid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setresugid.c -->
# sources/test-tools/strace/tests/setresugid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `ugid2int`, `print_int`, `num_matches_id`, `main`. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`. Preprocessor knobs/macros are none visible in this file. The file has 91 source lines and was read from `sources/test-tools/strace/tests/setresugid.c`.

Control flow: `main` and helpers (`ugid2int`, `print_int`, `num_matches_id`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `errno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setresugid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setresuid.c -->
# sources/test-tools/strace/tests/setresuid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setresuid32`, `geteuid`, `__NR_geteuid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setresuid`, `SYSCALL_NAME="setresuid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_geteuid)`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 32 source lines and was read from `sources/test-tools/strace/tests/setresuid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setresugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setresuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setresuid32.c -->
# sources/test-tools/strace/tests/setresuid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setresuid`, `setresgid`, `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setresuid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setresuid32`, `SYSCALL_NAME="setresuid32"`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setresuid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setresugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setresuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setreugid.c -->
# sources/test-tools/strace/tests/setreugid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `ugid2int`, `print_int`, `num_matches_id`, `main`. Important syscall/test APIs and data types are `setreuid`, `setregid`. Preprocessor knobs/macros are none visible in this file. The file has 84 source lines and was read from `sources/test-tools/strace/tests/setreugid.c`.

Control flow: `main` and helpers (`ugid2int`, `print_int`, `num_matches_id`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `errno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setreugid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setreuid.c -->
# sources/test-tools/strace/tests/setreuid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setreuid`, `setregid`, `setreuid32`, `geteuid`, `__NR_geteuid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setreuid`, `SYSCALL_NAME="setreuid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_geteuid)`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 26 source lines and was read from `sources/test-tools/strace/tests/setreuid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setreugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setreuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setreuid32.c -->
# sources/test-tools/strace/tests/setreuid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setreuid`, `setregid`, `SKIP_MAIN_UNDEFINED`, `setreuid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setreuid32`, `SYSCALL_NAME="setreuid32"`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setreuid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setreugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setreuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xabbrev.c -->
# sources/test-tools/strace/tests/setrlimit-Xabbrev.c

Purpose: Macro-variant wrapper for `setrlimit.c`. It sets none visible in this file before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setrlimit`, `rlimit`, `RLIMIT_*`. Preprocessor knobs/macros are none visible in this file. The file has 1 source lines and was read from `sources/test-tools/strace/tests/setrlimit-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setrlimit.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setrlimit.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xraw.c -->
# sources/test-tools/strace/tests/setrlimit-Xraw.c

Purpose: Macro-variant wrapper for `setrlimit.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setrlimit`, `rlimit`, `RLIMIT_*`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/setrlimit-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setrlimit.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setrlimit.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xverbose.c -->
# sources/test-tools/strace/tests/setrlimit-Xverbose.c

Purpose: Macro-variant wrapper for `setrlimit.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setrlimit`, `rlimit`, `RLIMIT_*`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/setrlimit-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setrlimit.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setrlimit.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit.c -->
# sources/test-tools/strace/tests/setrlimit.c

Purpose: Standalone or shared strace regression test for resource limit decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `setrlimit`, `rlimit`, `RLIMIT_*`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `__NR_setrlimit`. Preprocessor knobs/macros are none visible in this file. The file has 77 source lines and was read from `sources/test-tools/strace/tests/setrlimit.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xgetrlimit.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setrlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setugid.c -->
# sources/test-tools/strace/tests/setugid.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `printuid`, `main`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 73 source lines and was read from `sources/test-tools/strace/tests/setugid.c`.

Control flow: `main` and helpers (`printuid`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall.

Dependencies: Direct dependencies are `errno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setugid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setuid.c -->
# sources/test-tools/strace/tests/setuid.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setuid`, `getuid`, `overflowuid`, `setuid32`, `geteuid`, `__NR_geteuid`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setuid`, `SYSCALL_NAME="setuid"`, `UGID_TYPE=short`, `GETUGID=syscall(__NR_geteuid)`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 26 source lines and was read from `sources/test-tools/strace/tests/setuid.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: credential tests must avoid assuming privilege changes succeed.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setuid32.c -->
# sources/test-tools/strace/tests/setuid32.c

Purpose: Standalone or shared strace regression test for credential-changing syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setuid`, `getuid`, `overflowuid`, `SKIP_MAIN_UNDEFINED`, `setuid32`. Preprocessor knobs/macros are `SYSCALL_NR=__NR_setuid32`, `SYSCALL_NAME="setuid32"`, `UGID_TYPE=int`, `GETUGID=geteuid()`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/setuid32.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `setugid.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; credential tests must avoid assuming privilege changes succeed.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setuid32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-P.c -->
# sources/test-tools/strace/tests/setxattrat-P.c

Purpose: Macro-variant wrapper for `setxattrat.c`. It sets `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setxattrat`, `xattr_args`, `XATTR_*`, `AT_*`. Preprocessor knobs/macros are `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/setxattrat-P.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setxattrat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setxattrat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-y.c -->
# sources/test-tools/strace/tests/setxattrat-y.c

Purpose: Macro-variant wrapper for `setxattrat.c`. It sets `FD_PATH="</dev/full>"`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setxattrat`, `xattr_args`, `XATTR_*`, `AT_*`. Preprocessor knobs/macros are `FD_PATH="</dev/full>"`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/setxattrat-y.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setxattrat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setxattrat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-yy.c -->
# sources/test-tools/strace/tests/setxattrat-yy.c

Purpose: Macro-variant wrapper for `setxattrat.c`. It sets `FD_PATH="</dev/full<char 1:7>>"`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `setxattrat`, `xattr_args`, `XATTR_*`, `AT_*`. Preprocessor knobs/macros are `FD_PATH="</dev/full<char 1:7>>"`, `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/setxattrat-yy.c`.

Control flow: At compile time this wrapper defines its knobs and includes `setxattrat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `setxattrat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat.c -->
# sources/test-tools/strace/tests/setxattrat.c

Purpose: Standalone or shared strace regression test for extended attribute syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_setxattrat`, `main`. Important syscall/test APIs and data types are `setxattrat`, `xattr_args`, `XATTR_*`, `AT_*`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `__NR_setxattrat`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`, `XATTR_SIZE_MAX=65536`, `XATTR_ARGS_SIZE_VER0=16`, `FD_PATH=""`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`. The file has 275 source lines and was read from `sources/test-tools/strace/tests/setxattrat.c`.

Control flow: `main` and helpers (`k_setxattrat`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 4 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It tests `setxattrat` argument-structure decoding, xattr flag translation, value string truncation, dirfd/path combinations, `AT_*` flags, and path-tracing variants.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases; temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/xattr.h`, `xlat/xattrat_flags.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`; path-tracing/fd-decoding variants filter or annotate descriptor output; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/setxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/shmxt.c -->
# sources/test-tools/strace/tests/shmxt.c

Purpose: Standalone or shared strace regression test for System V shared memory decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `cleanup`, `main`. Important syscall/test APIs and data types are `shmat`, `shmdt`, `shmget`, `SHM_*`. Preprocessor knobs/macros are `SHMAT="osf_shmat"`, `SHMAT="shmat"`, `SHM_EXEC=0100000`. The file has 91 source lines and was read from `sources/test-tools/strace/tests/shmxt.c`.

Control flow: `main` and helpers (`cleanup`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: a static SysV IPC id is cleaned up through an exit handler.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `stdlib.h`, `sys/shm.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/shmxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/shutdown.c -->
# sources/test-tools/strace/tests/shutdown.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 22 source lines and was read from `sources/test-tools/strace/tests/shutdown.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/shutdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigaction.c -->
# sources/test-tools/strace/tests/sigaction.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_sigaction`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sigaction`. Preprocessor knobs/macros are `ADDR_INT=((unsigned int) -0xdefaced)`, `SIGNO_INT=((unsigned int) -SIGUSR1)`, `SIG_STR="-SIGUSR1"`, `ADDR_INT=((unsigned int) 0xdefaced)`, `SIGNO_INT=((unsigned int) SIGUSR1)`, `SIG_STR="SIGUSR1"`, `SA_RESTORER_FMT=", sa_flags=SA_RESTORER, sa_restorer=%#lx"`, `SA_RESTORER_ARGS=, new_act->restorer`, `SA_RESTORER_FMT=", sa_flags=SA_NODEFER"`, `SA_RESTORER_ARGS`. The file has 186 source lines and was read from `sources/test-tools/strace/tests/sigaction.c`.

Control flow: `main` and helpers (`k_sigaction`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdint.h`, `stdio.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigaltstack.c -->
# sources/test-tools/strace/tests/sigaltstack.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 22 source lines and was read from `sources/test-tools/strace/tests/sigaltstack.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: signal delivery and sigset layout are architecture dependent.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigaltstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/siginfo.c -->
# sources/test-tools/strace/tests/siginfo.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 177 source lines and was read from `sources/test-tools/strace/tests/siginfo.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 9 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: child process state is synchronized with wait/signal helpers.

Dependencies: Direct dependencies are `tests.h`, `assert.h`, `signal.h`, `string.h`, `unistd.h`, `sys/wait.h`, `time_enjoyment.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/siginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signal.c -->
# sources/test-tools/strace/tests/signal.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_signal`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`, `SKIP_MAIN_UNDEFINED`, `__NR_signal`. Preprocessor knobs/macros are none visible in this file. The file has 113 source lines and was read from `sources/test-tools/strace/tests/signal.c`.

Control flow: `main` and helpers (`k_signal`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 11 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `errno.h`, `signal.h`, `stdio.h`, `stdint.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signal2name.c -->
# sources/test-tools/strace/tests/signal2name.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `signal2name`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`. Preprocessor knobs/macros are none visible in this file. The file has 63 source lines and was read from `sources/test-tools/strace/tests/signal2name.c`.

Control flow: `main` and helpers (`signal2name`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `signal.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; signal delivery and sigset layout are architecture dependent.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signal2name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signal_receive--pidns-translation.c -->
# sources/test-tools/strace/tests/signal_receive--pidns-translation.c

Purpose: Macro-variant wrapper for `signal_receive.c`. It sets `PIDNS_TRANSLATION` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`. Preprocessor knobs/macros are `PIDNS_TRANSLATION`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/signal_receive--pidns-translation.c`.

Control flow: At compile time this wrapper defines its knobs and includes `signal_receive.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `signal_receive.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive; signal delivery and sigset layout are architecture dependent.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signal_receive--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signal_receive.c -->
# sources/test-tools/strace/tests/signal_receive.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`. Preprocessor knobs/macros are none visible in this file. The file has 117 source lines and was read from `sources/test-tools/strace/tests/signal_receive.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 7 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `pidns.h`, `signal.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; pid namespace runs include translated leader lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signal_receive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signalfd4-yy.c -->
# sources/test-tools/strace/tests/signalfd4-yy.c

Purpose: Macro-variant wrapper for `signalfd4.c`. It sets `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `PRINT_SIGNALFD` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `PRINT_SIGNALFD`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/signalfd4-yy.c`.

Control flow: At compile time this wrapper defines its knobs and includes `signalfd4.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `signalfd4.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; signal delivery and sigset layout are architecture dependent.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signalfd4-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/signalfd4.c -->
# sources/test-tools/strace/tests/signalfd4.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `signal`, `kill`, `siginfo_t`, `SIG*`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE`. The file has 73 source lines and was read from `sources/test-tools/strace/tests/signalfd4.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdio.h`, `unistd.h`, `sys/signalfd.h`, `kernel_fcntl.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/signalfd4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigpending.c -->
# sources/test-tools/strace/tests/sigpending.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_sigpending`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sigpending`. Preprocessor knobs/macros are none visible in this file. The file has 87 source lines and was read from `sources/test-tools/strace/tests/sigpending.c`.

Control flow: `main` and helpers (`k_sigpending`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdint.h`, `stdio.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigpending.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigprocmask.c -->
# sources/test-tools/strace/tests/sigprocmask.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_sigprocmask`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `__NR_sigprocmask`. Preprocessor knobs/macros are none visible in this file. The file has 132 source lines and was read from `sources/test-tools/strace/tests/sigprocmask.c`.

Control flow: `main` and helpers (`k_sigprocmask`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdint.h`, `stdio.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigprocmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigreturn.c -->
# sources/test-tools/strace/tests/sigreturn.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `SKIP_MAIN_UNDEFINED`, `sigreturn`. Preprocessor knobs/macros are `RT_0=ASM_SIGRTMIN`, `RT_0=32`. The file has 73 source lines and was read from `sources/test-tools/strace/tests/sigreturn.c`.

Control flow: `main` and helpers (`handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `signal.h`, `stdio.h`, `stdlib.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sigsuspend.c -->
# sources/test-tools/strace/tests/sigsuspend.c

Purpose: Standalone or shared strace regression test for signal syscall and signal-info decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_sigsuspend`, `handler`, `main`. Important syscall/test APIs and data types are `sigaction`, `sigaltstack`, `sigprocmask`, `sigsuspend`, `signalfd`, `sigpending`, `SKIP_MAIN_UNDEFINED`, `__NR_sigsuspend`. Preprocessor knobs/macros are `SIGNAL_MASK_BY_REF=1`, `SIGNAL_MASK_BY_REF=0`. The file has 98 source lines and was read from `sources/test-tools/strace/tests/sigsuspend.c`.

Control flow: `main` and helpers (`k_sigsuspend`, `handler`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `signal.h`, `stdio.h`, `stdint.h`, `string.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI; signal delivery and sigset layout are architecture dependent.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sigsuspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/skip_unavailable.c -->
# sources/test-tools/strace/tests/skip_unavailable.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `skip_if_unavailable`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 20 source lines and was read from `sources/test-tools/strace/tests/skip_unavailable.c`.

Control flow: `main` and helpers (`skip_if_unavailable`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `sys/stat.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/skip_unavailable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sleep-timing.c -->
# sources/test-tools/strace/tests/sleep-timing.c

Purpose: Standalone or shared strace regression test for sleep/timing trace test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `timespec_sub`, `timespec_to_sec`, `write_timing_file`, `main`. Important syscall/test APIs and data types are `sleep`, `nanosleep`, `time`, `SKIP_MAIN_UNDEFINED`, `__NR_nanosleep`. Preprocessor knobs/macros are none visible in this file. The file has 106 source lines and was read from `sources/test-tools/strace/tests/sleep-timing.c`.

Control flow: `main` and helpers (`timespec_sub`, `timespec_to_sec`, `write_timing_file`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 11 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: temporary opened descriptors are used to force fd/path rendering.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `time.h`, `unistd.h`, `kernel_old_timespec.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sleep-timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sleep.c -->
# sources/test-tools/strace/tests/sleep.c

Purpose: Standalone or shared strace regression test for sleep/timing trace test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `sleep`, `nanosleep`, `time`, `SKIP_MAIN_UNDEFINED`, `__NR_nanosleep`. Preprocessor knobs/macros are none visible in this file. The file has 42 source lines and was read from `sources/test-tools/strace/tests/sleep.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdlib.h`, `unistd.h`, `kernel_old_timespec.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_error.c -->
# sources/test-tools/strace/tests/so_error.c

Purpose: Standalone or shared strace regression test for SOL_SOCKET option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `reserve_ephemeral_port`, `main`. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `socklen_t`, `connect`, `sockaddr decoding`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 134 source lines and was read from `sources/test-tools/strace/tests/so_error.c`.

Control flow: `main` and helpers (`reserve_ephemeral_port`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 14 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `errno.h`, `fcntl.h`, `netinet/in.h`, `stdio.h`, `sys/select.h`, `sys/socket.h`, `sys/types.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_linger.c -->
# sources/test-tools/strace/tests/so_linger.c

Purpose: Standalone or shared strace regression test for SOL_SOCKET option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_linger`, `set_linger`, `main`. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are none visible in this file. The file has 161 source lines and was read from `sources/test-tools/strace/tests/so_linger.c`.

Control flow: `main` and helpers (`get_linger`, `set_linger`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `sys/socket.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_linger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred--pidns-translation.c -->
# sources/test-tools/strace/tests/so_peercred--pidns-translation.c

Purpose: Macro-variant wrapper for `so_peercred.c`. It sets `PIDNS_TRANSLATION` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`. Preprocessor knobs/macros are `PIDNS_TRANSLATION`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/so_peercred--pidns-translation.c`.

Control flow: At compile time this wrapper defines its knobs and includes `so_peercred.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `so_peercred.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; pid namespace translations are architecture/runtime sensitive.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xabbrev.c -->
# sources/test-tools/strace/tests/so_peercred-Xabbrev.c

Purpose: Macro-variant wrapper for `so_peercred.c`. It sets none visible in this file before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`. Preprocessor knobs/macros are none visible in this file. The file has 1 source lines and was read from `sources/test-tools/strace/tests/so_peercred-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `so_peercred.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `so_peercred.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xraw.c -->
# sources/test-tools/strace/tests/so_peercred-Xraw.c

Purpose: Macro-variant wrapper for `so_peercred.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/so_peercred-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `so_peercred.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `so_peercred.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xverbose.c -->
# sources/test-tools/strace/tests/so_peercred-Xverbose.c

Purpose: Macro-variant wrapper for `so_peercred.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/so_peercred-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `so_peercred.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `so_peercred.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred.c -->
# sources/test-tools/strace/tests/so_peercred.c

Purpose: Standalone or shared strace regression test for SOL_SOCKET option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_peercred`, `so_str`, `main`. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `socklen_t`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are none visible in this file. The file has 224 source lines and was read from `sources/test-tools/strace/tests/so_peercred.c`.

Control flow: `main` and helpers (`get_peercred`, `so_str`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 2 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `pidns.h`, `stddef.h`, `stdio.h`, `string.h`, `sys/socket.h`, `unistd.h`, `print_fields.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: pid namespace translations are architecture/runtime sensitive; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; pid namespace runs include translated leader lines; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peercred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/so_peerpidfd.c -->
# sources/test-tools/strace/tests/so_peerpidfd.c

Purpose: Standalone or shared strace regression test for SOL_SOCKET option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_peerpidfd`, `print_pidfd`, `print_optlen`, `main`. Important syscall/test APIs and data types are `getsockopt`, `setsockopt`, `SO_*`, `SOL_SOCKET`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 110 source lines and was read from `sources/test-tools/strace/tests/so_peerpidfd.c`.

Control flow: `main` and helpers (`get_peerpidfd`, `print_pidfd`, `print_optlen`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `unistd.h`, `sys/socket.h`, `xlat/sock_options.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/so_peerpidfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xabbrev.c -->
# sources/test-tools/strace/tests/sock_filter-v-Xabbrev.c

Purpose: Macro-variant wrapper for `sock_filter-v.c`. It sets none visible in this file before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are none visible in this file. The file has 1 source lines and was read from `sources/test-tools/strace/tests/sock_filter-v-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sock_filter-v.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sock_filter-v.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xraw.c -->
# sources/test-tools/strace/tests/sock_filter-v-Xraw.c

Purpose: Macro-variant wrapper for `sock_filter-v.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sock_filter-v-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sock_filter-v.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sock_filter-v.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xverbose.c -->
# sources/test-tools/strace/tests/sock_filter-v-Xverbose.c

Purpose: Macro-variant wrapper for `sock_filter-v.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sock_filter-v-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sock_filter-v.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sock_filter-v.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v.c -->
# sources/test-tools/strace/tests/sock_filter-v.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `print_filter`, `get_filter`, `set_filter`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `SO_GET_FILTER=SO_ATTACH_FILTER`, `HEX_FMT="%#x"`. The file has 200 source lines and was read from `sources/test-tools/strace/tests/sock_filter-v.c`.

Control flow: `main` and helpers (`print_filter`, `get_filter`, `set_filter`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `unistd.h`, `netinet/in.h`, `sys/socket.h`, `linux/filter.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sock_filter-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev-y.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev-y.c

Purpose: Macro-variant wrapper for `sockaddr_xlat-Xabbrev.c`. It sets `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev-y.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat-Xabbrev.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat-Xabbrev.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev.c

Purpose: Macro-variant wrapper for `sockaddr_xlat.c`. It sets none visible in this file before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are none visible in this file. The file has 1 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c

Purpose: Macro-variant wrapper for `sockaddr_xlat-Xraw.c`. It sets `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat-Xraw.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat-Xraw.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xraw-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c

Purpose: Macro-variant wrapper for `sockaddr_xlat.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xverbose-y.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xverbose-y.c

Purpose: Macro-variant wrapper for `sockaddr_xlat-Xverbose.c`. It sets `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are `SKIP_IF_PROC_IS_UNAVAILABLE=skip_if_unavailable("/proc/self/fd/")`, `FD0_PATH="</dev/null>"`, `FD7_PATH="</dev/zero>"`. The file has 4 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xverbose-y.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat-Xverbose.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat-Xverbose.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: unsupported ABI paths skip rather than fail; path-tracing/fd-decoding variants filter or annotate descriptor output; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xverbose-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xverbose.c -->
# sources/test-tools/strace/tests/sockaddr_xlat-Xverbose.c

Purpose: Macro-variant wrapper for `sockaddr_xlat.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockaddr_xlat.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockaddr_xlat.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat.c -->
# sources/test-tools/strace/tests/sockaddr_xlat.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `check_ll`, `check_in`, `validate_in6`, `check_in6`, `check_tipc`, `check_sco`, `check_rc`, `check_rxrpc`, `check_ieee802154`, `check_alg`, `check_nfc`, `check_vsock`, plus 4 more. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `sockaddr decoding`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `IEEE802154_ADDR_LEN=8`, `IEEE802154_PANID_BROADCAST=0xffff`, `IEEE802154_ADDR_BROADCAST=0xffff`, `IEEE802154_ADDR_UNDEF=0xfffe`, `CRYPTO_ALG_KERN_DRIVER_ONLY=0x1000`, `SVM_FLAGS=svm_flags`, `SVM_ZERO=svm_zero`, `SVM_ZERO_FIRST=svm_zero[0]`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_PATH=""`, plus 1 more. The file has 1267 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat.c`.

Control flow: `main` and helpers (`check_ll`, `check_in`, `validate_in6`, `check_in6`, `check_tipc`, `check_sco`, `check_rc`, `check_rxrpc`, `check_ieee802154`, `check_alg`, plus 6 more) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 13 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It is a broad socket-address xlat test using `connect(-1, ...)` against AF_PACKET, IPv4, IPv6, TIPC, Bluetooth, RXRPC, IEEE802154, AF_ALG, NFC, VSOCK, QRTR, XDP, and MCTP structures.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `arpa/inet.h`, `netinet/in.h`, `linux/ax25.h`, `linux/if_arp.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/mctp.h`, `linux/tipc.h`, `bluetooth/bluetooth.h`, plus 13 more. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockaddr_xlat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/socketcall.c -->
# sources/test-tools/strace/tests/socketcall.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `xlookup_uint`, `test_socketcall`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `SKIP_MAIN_UNDEFINED`, `socketcall`, `__NR_socketcall`. Preprocessor knobs/macros are none visible in this file. The file has 75 source lines and was read from `sources/test-tools/strace/tests/socketcall.c`.

Control flow: `main` and helpers (`xlookup_uint`, `test_socketcall`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `unistd.h`, `xlat.h`, `xlat/socketcalls.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/socketcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockname.c -->
# sources/test-tools/strace/tests/sockname.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `test_sockname_syscall`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are `TEST_SYSCALL_STR=STRINGIFY_VAL(TEST_SYSCALL_NAME)`, `TEST_SOCKET=TEST_SYSCALL_STR ".socket"`, `PREPARE_TEST_SYSCALL_INVOCATION=do { TEST_SYSCALL_PREPARE; } while (0)`, `PREPARE_TEST_SYSCALL_INVOCATION=do {} while (0)`, `PREFIX_S_ARGS`, `PREFIX_F_ARGS`, `PREFIX_S_STR=""`, `PREFIX_F_STR=""`, `SUFFIX_ARGS`, `SUFFIX_STR=""`. The file has 153 source lines and was read from `sources/test-tools/strace/tests/sockname.c`.

Control flow: `main` and helpers (`test_sockname_syscall`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 4 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases; child process state is synchronized with wait/signal helpers.

Dependencies: Direct dependencies are `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `signal.h`, `unistd.h`, `sys/wait.h`, `sys/socket.h`, `sys/un.h`, `secontext.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_netlink.c -->
# sources/test-tools/strace/tests/sockopt-sol_netlink.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_sockopt`, `set_sockopt`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`. Preprocessor knobs/macros are `SOL_NETLINK=270`. The file has 197 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_netlink.c`.

Control flow: `main` and helpers (`get_sockopt`, `set_sockopt`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 11 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `netlink.h`, `stdio.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xabbrev.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-Xabbrev.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xraw.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-Xraw.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xverbose.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-Xverbose.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xabbrev.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-success-Xabbrev.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket-success.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-success-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xraw.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-success-Xraw.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket-success.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-success-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xverbose.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-success-Xverbose.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket-success.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-success-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; socket option/address constants vary by kernel headers and architecture.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket-success.c

Purpose: Macro-variant wrapper for `sockopt-sol_socket.c`. It sets `INJECT_RETVAL=42` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`. Preprocessor knobs/macros are `INJECT_RETVAL=42`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket-success.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sockopt-sol_socket.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sockopt-sol_socket.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; socket option/address constants vary by kernel headers and architecture.

Test signals: injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket.c -->
# sources/test-tools/strace/tests/sockopt-sol_socket.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `get_sockopt`, `set_sockopt`, `print_optval`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`, `INJSTR=" (INJECTED)"`, `INJSTR=""`. The file has 321 source lines and was read from `sources/test-tools/strace/tests/sockopt-sol_socket.c`.

Control flow: `main` and helpers (`get_sockopt`, `set_sockopt`, `print_optval`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 4 explicit `for` loops and 15 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It loops over many `SOL_SOCKET` options, driving both `getsockopt` and `setsockopt` with normal, short, long, zero, and faulting optval/optlen cases.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `sys/un.h`, `k_sockopt.h`, `xlat/sock_options.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-sol_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-timestamp.c -->
# sources/test-tools/strace/tests/sockopt-timestamp.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `k_recvmsg`, `print_timestamp_old`, `print_timestampns_old`, `print_timestamp_new`, `print_timestampns_new`, `test_sockopt`, `main`. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `sendmsg`, `recvmsg`, `msghdr`, `socklen_t`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`, `SKIP_MAIN_UNDEFINED`, `__NR_recvmsg`. Preprocessor knobs/macros are `XLAT_MACROS_ONLY`. The file has 234 source lines and was read from `sources/test-tools/strace/tests/sockopt-timestamp.c`.

Control flow: `main` and helpers (`k_recvmsg`, `print_timestamp_old`, `print_timestampns_old`, `print_timestamp_new`, `print_timestampns_new`, `test_sockopt`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 15 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It constructs timestamp control messages and socket option combinations for old/new timeval/timespec layouts and recvmsg ancillary-data decoding.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; temporary sockets/fds exist only for the test process.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `kernel_time_types.h`, `kernel_timeval.h`, `kernel_old_timespec.h`, `k_sockopt.h`, `xlat/sock_options.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; unsupported ABI paths skip rather than fail; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sockopt-timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xabbrev.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-Xabbrev.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xraw.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-Xraw.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xverbose.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-Xverbose.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xabbrev.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-success-Xabbrev.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join-success.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-success-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xraw.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-success-Xraw.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join-success.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-success-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xverbose.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-success-Xverbose.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join-success.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-success-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join-success.c

Purpose: Macro-variant wrapper for `sol_tipc-group_join.c`. It sets `INJECT_RETVAL=42` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`. Preprocessor knobs/macros are `INJECT_RETVAL=42`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join-success.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-group_join.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-group_join.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join.c -->
# sources/test-tools/strace/tests/sol_tipc-group_join.c

Purpose: Standalone or shared strace regression test for TIPC socket option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `set_group_req`, `get_group_req`, `main`. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are none visible in this file. The file has 167 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-group_join.c`.

Control flow: `main` and helpers (`set_group_req`, `get_group_req`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `linux/tipc.h`, `xmalloc.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-group_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xabbrev.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-Xabbrev.c

Purpose: Macro-variant wrapper for `sol_tipc-importance.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xraw.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-Xraw.c

Purpose: Macro-variant wrapper for `sol_tipc-importance.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xverbose.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-Xverbose.c

Purpose: Macro-variant wrapper for `sol_tipc-importance.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xabbrev.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-success-Xabbrev.c

Purpose: Macro-variant wrapper for `sol_tipc-importance-success.c`. It sets `XLAT_ABBREV=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_ABBREV=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-success-Xabbrev.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xraw.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-success-Xraw.c

Purpose: Macro-variant wrapper for `sol_tipc-importance-success.c`. It sets `XLAT_RAW=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_RAW=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-success-Xraw.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xverbose.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-success-Xverbose.c

Purpose: Macro-variant wrapper for `sol_tipc-importance-success.c`. It sets `XLAT_VERBOSE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `XLAT_VERBOSE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-success-Xverbose.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance-success.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance-success.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test; raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables.

Test signals: xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success.c -->
# sources/test-tools/strace/tests/sol_tipc-importance-success.c

Purpose: Macro-variant wrapper for `sol_tipc-importance.c`. It sets `INJECT_RETVAL=42` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`. Preprocessor knobs/macros are `INJECT_RETVAL=42`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance-success.c`.

Control flow: At compile time this wrapper defines its knobs and includes `sol_tipc-importance.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `sol_tipc-importance.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance.c -->
# sources/test-tools/strace/tests/sol_tipc-importance.c

Purpose: Standalone or shared strace regression test for TIPC socket option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `set_importance`, `get_importance`, `main`. Important syscall/test APIs and data types are `TIPC_*`, `getsockopt`, `setsockopt`, `SOL_TIPC`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are none visible in this file. The file has 164 source lines and was read from `sources/test-tools/strace/tests/sol_tipc-importance.c`.

Control flow: `main` and helpers (`set_importance`, `get_importance`, `main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 2 explicit `for` loops and 5 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `linux/tipc.h`, `xmalloc.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; injection variants append expected injected-result markers; xlat mode variants validate raw, abbreviated, and verbose representations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sol_tipc-importance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/splice.c -->
# sources/test-tools/strace/tests/splice.c

Purpose: Standalone or shared strace regression test for splice pipe/file syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `splice`, `pipe`, `SPLICE_F_*`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `__NR_splice`. Preprocessor knobs/macros are none visible in this file. The file has 38 source lines and was read from `sources/test-tools/strace/tests/splice.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: successful self-test prints `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sprintrc.c -->
# sources/test-tools/strace/tests/sprintrc.c

Purpose: Standalone or shared strace regression test for a Linux syscall decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `sprintrc_ex`, `sprintrc`, `sprintrc_grep`. Important syscall/test APIs and data types are none visible in this file. Preprocessor knobs/macros are none visible in this file. The file has 65 source lines and was read from `sources/test-tools/strace/tests/sprintrc.c`.

Control flow: `main` and helpers (`sprintrc_ex`, `sprintrc`, `sprintrc_grep`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 3 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `errno.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sprintrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-0.c -->
# sources/test-tools/strace/tests/stack-fcall-0.c

Purpose: Standalone or shared strace regression test for stack trace function-call test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `f0`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are none visible in this file. The file has 16 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-0.c`.

Control flow: `main` and helpers (`f0`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-1.c -->
# sources/test-tools/strace/tests/stack-fcall-1.c

Purpose: Standalone or shared strace regression test for stack trace function-call test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `f1`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are none visible in this file. The file has 16 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-1.c`.

Control flow: `main` and helpers (`f1`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-2.c -->
# sources/test-tools/strace/tests/stack-fcall-2.c

Purpose: Standalone or shared strace regression test for stack trace function-call test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `f2`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are none visible in this file. The file has 16 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-2.c`.

Control flow: `main` and helpers (`f2`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-3.c -->
# sources/test-tools/strace/tests/stack-fcall-3.c

Purpose: Standalone or shared strace regression test for stack trace function-call test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `f3`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`, `exit`, `__NR_exit`. Preprocessor knobs/macros are none visible in this file. The file has 28 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-3.c`.

Control flow: `main` and helpers (`f3`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `signal.h`, `stack-fcall.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: fault-address tests depend on tail allocation and pointer-width behavior.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-attach.c -->
# sources/test-tools/strace/tests/stack-fcall-attach.c

Purpose: Macro-variant wrapper for `stack-fcall.c`. It sets `ATTACH_MODE=1` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `ATTACH_MODE=1`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-attach.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-0.c -->
# sources/test-tools/strace/tests/stack-fcall-mangled-0.c

Purpose: Macro-variant wrapper for `stack-fcall-0.c`. It sets `MANGLE` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `MANGLE`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-mangled-0.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall-0.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall-0.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-1.c -->
# sources/test-tools/strace/tests/stack-fcall-mangled-1.c

Purpose: Macro-variant wrapper for `stack-fcall-1.c`. It sets `MANGLE` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `MANGLE`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-mangled-1.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall-1.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall-1.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-2.c -->
# sources/test-tools/strace/tests/stack-fcall-mangled-2.c

Purpose: Macro-variant wrapper for `stack-fcall-2.c`. It sets `MANGLE` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `MANGLE`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-mangled-2.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall-2.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall-2.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-3.c -->
# sources/test-tools/strace/tests/stack-fcall-mangled-3.c

Purpose: Macro-variant wrapper for `stack-fcall-3.c`. It sets `MANGLE` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `MANGLE`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-mangled-3.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall-3.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall-3.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled-3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled.c -->
# sources/test-tools/strace/tests/stack-fcall-mangled.c

Purpose: Macro-variant wrapper for `stack-fcall.c`. It sets `MANGLE` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `MANGLE`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/stack-fcall-mangled.c`.

Control flow: At compile time this wrapper defines its knobs and includes `stack-fcall.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `stack-fcall.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall-mangled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall.c -->
# sources/test-tools/strace/tests/stack-fcall.c

Purpose: Standalone or shared strace regression test for stack trace function-call test. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `main`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`. Preprocessor knobs/macros are `ATTACH_MODE=0`. The file has 26 source lines and was read from `sources/test-tools/strace/tests/stack-fcall.c`.

Control flow: `main` and helpers (`main`) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 1 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `unistd.h`, `stack-fcall.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall.h -->
# sources/test-tools/strace/tests/stack-fcall.h

Purpose: Shared test header that provides inline helpers and macros for related strace decoder tests. It is included by companion tests rather than run directly; the code centralizes repeated helper behavior so output formatting stays consistent across the suite.

Important APIs/types/functions: Visible local functions are `f0`, `f1`, `f2`, `f3`. Important syscall/test APIs and data types are `backtrace`, `stack trace`, `fcall`, `mangled names`, `gettid`, `__NR_gettid`. Preprocessor knobs/macros are `f0=_ZN2ns2f0Ei`, `f1=_ZN2ns2f1Ei`, `f2=_ZN2ns2f2Ei`, `f3=_ZN2ns2f3Ei`. The file has 45 source lines and was read from `sources/test-tools/strace/tests/stack-fcall.h`.

Control flow: No `main` is present. Including tests call the inline helpers/macros, which branch on build-time feature macros and either call real helpers or return empty test strings.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `unistd.h`, `scno.h`, `gcc_compat.h`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: main risk is expected-output drift when strace formatting or kernel ABI constants change.

Test signals: test passes when actual strace output matches the printf-generated expectation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stack-fcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stat.c -->
# sources/test-tools/strace/tests/stat.c

Purpose: Standalone or shared strace regression test for stat/statfs/statmount decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `TEST_SYSCALL_NR=__NR_stat`, `TEST_SYSCALL_STR="stat"`, `SAMPLE_SIZE=((libc_off_t) (kernel_ulong_t) 43147718418ULL)`. The file has 23 source lines and was read from `sources/test-tools/strace/tests/stat.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `lstatx.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/stat64.c -->
# sources/test-tools/strace/tests/stat64.c

Purpose: Standalone or shared strace regression test for stat/statfs/statmount decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `TEST_SYSCALL_NR=__NR_stat64`, `TEST_SYSCALL_STR="stat64"`, `STRUCT_STAT=struct stat64`, `STRUCT_STAT_STR="struct stat64"`, `STRUCT_STAT_IS_STAT64=1`. The file has 25 source lines and was read from `sources/test-tools/strace/tests/stat64.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `lstatx.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/stat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statfs.c -->
# sources/test-tools/strace/tests/statfs.c

Purpose: Standalone or shared strace regression test for stat/statfs/statmount decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `SYSCALL_ARG_FMT="\"%s\""`, `SYSCALL_NR=__NR_statfs`, `SYSCALL_NAME="statfs"`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/statfs.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xstatfs.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statfs64.c -->
# sources/test-tools/strace/tests/statfs64.c

Purpose: Standalone or shared strace regression test for stat/statfs/statmount decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`, `SKIP_MAIN_UNDEFINED`. Preprocessor knobs/macros are `SYSCALL_ARG_FMT="\"%s\""`, `SYSCALL_NR=__NR_statfs64`, `SYSCALL_NAME="statfs64"`. The file has 24 source lines and was read from `sources/test-tools/strace/tests/statfs64.c`.

Control flow: `main` and helpers (none visible in this file) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 0 explicit `for` loops and 0 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `tests.h`, `scno.h`, `xstatfs64.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: feature guards must skip cleanly on kernels/libcs without the ABI.

Test signals: unsupported ABI paths skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statfs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statmount-success.c -->
# sources/test-tools/strace/tests/statmount-success.c

Purpose: Macro-variant wrapper for `statmount.c`. It sets `INJECT_RETVAL` before including the shared implementation, so the same decoder scenario is rebuilt with a different strace mode, pid namespace translation setting, success injection, path tracing, or availability guard.

Important APIs/types/functions: Visible local functions are none visible in this file. Important syscall/test APIs and data types are `stat`, `stat64`, `statfs`, `statfs64`, `statmount`. Preprocessor knobs/macros are `INJECT_RETVAL`. The file has 2 source lines and was read from `sources/test-tools/strace/tests/statmount-success.c`.

Control flow: At compile time this wrapper defines its knobs and includes `statmount.c`; runtime control flow is inherited from that implementation. The variant changes expected output formatting, not the kernel scenario itself.

State and persistence behavior: no persistent repository or system state is kept; all data is process-local test setup.

Dependencies: Direct dependencies are `statmount.c`. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: wrapper macro drift can desynchronize expected output from the included base test.

Test signals: injection variants append expected injected-result markers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statmount-success.c -->
