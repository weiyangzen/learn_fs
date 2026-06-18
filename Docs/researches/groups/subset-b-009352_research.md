# subset-b-009352 research

Grouped research report for the requested strace test sources under `sources/test-tools/strace/tests`. Each source file was read from the workspace and receives a source-tree-aligned section wrapped for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl.c -->
# sources/test-tools/strace/tests/keyctl.c

Purpose: `keyctl.c` exercises strace decoding for syscall(s) `keyctl` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 1362 line(s), 41940 byte(s); classification `keyctl syscall decoder exercise`; functions `print_quoted_string_limit`, `print_arg`, `print_flags`, `do_keyctl`, `ATTRIBUTE_FORMAT`, `kckdfp_to_str`, `kcpp_to_str`, `main`; syscall markers `keyctl`. Source-specific note: This is one of the dense decoder tests: `do_keyctl` builds variadic argument cases, `print_quoted_string_limit` handles output buffer truncation/NUL behavior, and `kckdfp_to_str`/`kcpp_to_str` format complex KDF and public-key parameter structures. It probes many `KEYCTL_*` commands and xlat modes. Key includes are `tests.h`, `scno.h`, `xmalloc.h`, `assert.h`, `errno.h`, `inttypes.h`, `stdarg.h`, `stdio.h`, `stdlib.h`, `string.h`, ... (17 total). Key macros/compile switches are `STR32`, `XARG_STR`, `XSTR`, `XARG_STR`, `XSTR`, `XARG_STR`, `XSTR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_quoted_string_limit`, `print_arg`, `print_flags`, `do_keyctl`, `ATTRIBUTE_FORMAT`, `kckdfp_to_str`, `kcpp_to_str`, `main`), invokes syscall targets (`keyctl`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 11 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `xmalloc.h`, `assert.h`, `errno.h`, `inttypes.h`, `stdarg.h`, `stdio.h`, ... (17 total). Important compile-time knobs are `STR32`, `XARG_STR`, `XSTR`, `XARG_STR`, `XSTR`, `XARG_STR`, `XSTR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; syscall availability differs across kernels and personalities; word-size dependent printing can regress on ILP32/LP64 personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 44 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kill--pidns-translation.c -->
# sources/test-tools/strace/tests/kill--pidns-translation.c

Purpose: `kill--pidns-translation.c` is a thin compile-time variant that includes `kill.c` after setting `PIDNS_TRANSLATION`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 44 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `kill.c`. Key macros/compile switches are `PIDNS_TRANSLATION`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `kill.c`. Important compile-time knobs are `PIDNS_TRANSLATION`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: pid namespace translation can make expected PIDs architecture- and harness-sensitive.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: pid-namespace translated expected output, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kill--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kill-on-exit.sh -->
# sources/test-tools/strace/tests/kill-on-exit.sh

Purpose: `kill-on-exit.sh` is an executable shell test harness for strace process-kill behavior at tracee exit. It orchestrates helper processes, invokes the test suite shell utilities, and checks that strace tears down or reports processes with the expected status rather than leaving children running.

Important APIs/types/functions: Complete-read metadata: 94 line(s), 2208 byte(s); classification `shell harness`; functions none visible in this file; syscall markers none visible in this file. Key includes are none visible in this file. Key macros/compile switches are none visible in this file.

Control flow: The shell script sources the common init logic, prepares a child/tracee scenario, runs strace with the requested exit/kill options, waits for process completion, and compares observed behavior with expected status/output. Its branches mainly handle unsupported features and cleanup.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily none visible in this file. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kill-on-exit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kill.c -->
# sources/test-tools/strace/tests/kill.c

Purpose: `kill.c` exercises strace decoding for syscall(s) `kill` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 60 line(s), 1445 byte(s); classification `signal and process termination test`; functions `handler`, `main`; syscall markers `kill`. Key includes are `tests.h`, `scno.h`, `pidns.h`, `signal.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`handler`, `main`), invokes syscall targets (`kill`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `pidns.h`, `signal.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, pid namespace expected-output helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 4 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kill_child.c -->
# sources/test-tools/strace/tests/kill_child.c

Purpose: `kill_child.c` is a focused strace test/helper source in the `signal and process termination test` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 69 line(s), 1310 byte(s); classification `signal and process termination test`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `sched.h`, `signal.h`, `unistd.h`, `sys/mman.h`, `sys/wait.h`. Key macros/compile switches are `ITERS`, `SC_ITERS`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 4 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers; mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `sched.h`, `signal.h`, `unistd.h`, `sys/mman.h`, `sys/wait.h`. Important compile-time knobs are `ITERS`, `SC_ITERS`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kill_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ksysent.c -->
# sources/test-tools/strace/tests/ksysent.c

Purpose: `ksysent.c` is a focused strace test/helper source in the `kernel syscall table consistency test` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 100 line(s), 2346 byte(s); classification `kernel syscall table consistency test`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `sysent.h`, `stdio.h`, `string.h`, `scno.h`, `sysent_shorthand_defs.h`, `syscallent.h`, `sysent_shorthand_undefs.h`, `ksysent.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `sysent.h`, `stdio.h`, `string.h`, `scno.h`, `sysent_shorthand_defs.h`, `syscallent.h`, `sysent_shorthand_undefs.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 5 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ksysent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ksysent.sed -->
# sources/test-tools/strace/tests/ksysent.sed

Purpose: `ksysent.sed` is a sed normalization script used by the `ksysent` test to transform architecture syscall-table names into comparable kernel syscall entry names. It is data-processing glue rather than a C test binary.

Important APIs/types/functions: Complete-read metadata: 31 line(s), 1189 byte(s); classification `sed transformer`; functions none visible in this file; syscall markers `accept4`, `fadvise64_64`, `get`, `get_cpu`, `getcpu`, `getx`, `madvise`, `madvise1`, `osf_`, `osf_shmat`, `paccept`, `shmat`, ... (14 total). Key includes are none visible in this file. Key macros/compile switches are none visible in this file.

Control flow: Input records are processed linearly. Pattern/action rules normalize or match each line and either print transformed records or fail the test when the stream no longer matches expected syscall-output structure.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily none visible in this file. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ksysent.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_add_rule-y.c -->
# sources/test-tools/strace/tests/landlock_add_rule-y.c

Purpose: `landlock_add_rule-y.c` is a thin compile-time variant that includes `landlock_add_rule.c` after setting `FD0_STR, RULESET_FD, RULESET_FD_STR, PARENT_FD, PARENT_FD_STR, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 8 line(s), 252 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `landlock_add_rule.c`. Key macros/compile switches are `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `landlock_add_rule.c`. Important compile-time knobs are `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_add_rule-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_add_rule.c -->
# sources/test-tools/strace/tests/landlock_add_rule.c

Purpose: `landlock_add_rule.c` exercises strace decoding for syscall(s) `landlock_add_rule` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 150 line(s), 4815 byte(s); classification `Landlock syscall decoder exercise`; functions `sys_landlock_add_rule`, `main`; syscall markers `landlock_add_rule`. Key includes are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/landlock.h`. Key macros/compile switches are `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`sys_landlock_add_rule`, `main`), invokes syscall targets (`landlock_add_rule`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 4 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/landlock.h`. Important compile-time knobs are `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_STR`, `RULESET_FD`, `RULESET_FD_STR`, `PARENT_FD`, `PARENT_FD_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, Landlock UAPI.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 8 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_add_rule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-success-y.c -->
# sources/test-tools/strace/tests/landlock_create_ruleset-success-y.c

Purpose: `landlock_create_ruleset-success-y.c` is a thin compile-time variant that includes `landlock_create_ruleset-success.c` after setting `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 150 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `landlock_create_ruleset-success.c`. Key macros/compile switches are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `landlock_create_ruleset-success.c`. Important compile-time knobs are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-success-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-success.c -->
# sources/test-tools/strace/tests/landlock_create_ruleset-success.c

Purpose: `landlock_create_ruleset-success.c` is a thin compile-time variant that includes `landlock_create_ruleset.c` after setting `RETVAL_INJECTED`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 63 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `landlock_create_ruleset.c`. Key macros/compile switches are `RETVAL_INJECTED`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `landlock_create_ruleset.c`. Important compile-time knobs are `RETVAL_INJECTED`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-y.c -->
# sources/test-tools/strace/tests/landlock_create_ruleset-y.c

Purpose: `landlock_create_ruleset-y.c` is a thin compile-time variant that includes `landlock_create_ruleset.c` after setting `DECODE_FD, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 132 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `landlock_create_ruleset.c`. Key macros/compile switches are `DECODE_FD`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `landlock_create_ruleset.c`. Important compile-time knobs are `DECODE_FD`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset.c -->
# sources/test-tools/strace/tests/landlock_create_ruleset.c

Purpose: `landlock_create_ruleset.c` exercises strace decoding for syscall(s) `landlock_create_ruleset` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 225 line(s), 6717 byte(s); classification `Landlock syscall decoder exercise`; functions `sys_landlock_create_ruleset`, `get_fd_str`, `main`; syscall markers `landlock_create_ruleset`. Source-specific note: The ruleset test covers version/errata flags, short and extended struct sizes, filesystem/net/scope access masks, fd-return decoration, and injected success variants. Key includes are `tests.h`, `scno.h`, `xmalloc.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, `linux/landlock.h`. Key macros/compile switches are `RETVAL_INJECTED`, `DECODE_FD`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD_PATH`, `INJ_STR`, `INJ_FD_STR`, `INJ_STR`, `INJ_FD_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`sys_landlock_create_ruleset`, `get_fd_str`, `main`), invokes syscall targets (`landlock_create_ruleset`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 5 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `xmalloc.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `unistd.h`, ... (9 total). Important compile-time knobs are `RETVAL_INJECTED`, `DECODE_FD`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD_PATH`, `INJ_STR`, `INJ_FD_STR`, `INJ_STR`, `INJ_FD_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers, Landlock UAPI.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; word-size dependent printing can regress on ILP32/LP64 personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 11 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_create_ruleset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_restrict_self-y.c -->
# sources/test-tools/strace/tests/landlock_restrict_self-y.c

Purpose: `landlock_restrict_self-y.c` is a thin compile-time variant that includes `landlock_restrict_self.c` after setting `RULESET_FD, RULESET_FD_STR, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 5 line(s), 170 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `landlock_restrict_self.c`. Key macros/compile switches are `RULESET_FD`, `RULESET_FD_STR`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `landlock_restrict_self.c`. Important compile-time knobs are `RULESET_FD`, `RULESET_FD_STR`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_restrict_self-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_restrict_self.c -->
# sources/test-tools/strace/tests/landlock_restrict_self.c

Purpose: `landlock_restrict_self.c` exercises strace decoding for syscall(s) `landlock_restrict_self` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 77 line(s), 1778 byte(s); classification `Landlock syscall decoder exercise`; functions `sys_landlock_restrict_self`, `main`; syscall markers `landlock_restrict_self`. Key includes are `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`. Key macros/compile switches are `SKIP_IF_PROC_IS_UNAVAILABLE`, `RULESET_FD`, `RULESET_FD_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`sys_landlock_restrict_self`, `main`), invokes syscall targets (`landlock_restrict_self`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `unistd.h`. Important compile-time knobs are `SKIP_IF_PROC_IS_UNAVAILABLE`, `RULESET_FD`, `RULESET_FD_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/landlock_restrict_self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lchown.c -->
# sources/test-tools/strace/tests/lchown.c

Purpose: `lchown.c` exercises strace decoding for syscall(s) `lchown`, `lchown32` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 26 line(s), 422 byte(s); classification `ownership syscall wrapper over xchownx`; functions none visible in this file; syscall markers `lchown`, `lchown32`. Key includes are `tests.h`, `scno.h`, `xchownx.c`. Key macros/compile switches are `SYSCALL_NR`, `SYSCALL_NAME`, `UGID_TYPE_IS_SHORT`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`lchown`, `lchown32`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `xchownx.c`. Important compile-time knobs are `SYSCALL_NR`, `SYSCALL_NAME`, `UGID_TYPE_IS_SHORT`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lchown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lchown32.c -->
# sources/test-tools/strace/tests/lchown32.c

Purpose: `lchown32.c` exercises strace decoding for syscall(s) `lchown32` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 21 line(s), 332 byte(s); classification `ownership syscall wrapper over xchownx`; functions none visible in this file; syscall markers `lchown32`. Key includes are `tests.h`, `scno.h`, `xchownx.c`. Key macros/compile switches are `SYSCALL_NR`, `SYSCALL_NAME`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`lchown32`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `xchownx.c`. Important compile-time knobs are `SYSCALL_NR`, `SYSCALL_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lchown32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/libmmsg.c -->
# sources/test-tools/strace/tests/libmmsg.c

Purpose: `libmmsg.c` exercises strace decoding for syscall(s) `recvmmsg`, `sendmmsg` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 50 line(s), 1076 byte(s); classification `test helper library`; functions `recv_mmsg`, `send_mmsg`; syscall markers `recvmmsg`, `sendmmsg`. Key includes are `tests.h`, `errno.h`, `scno.h`. Key macros/compile switches are `__NR_recvmmsg`, `SC_recvmmsg`, `__NR_sendmmsg`, `SC_sendmmsg`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`recv_mmsg`, `send_mmsg`), invokes syscall targets (`recvmmsg`, `sendmmsg`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `scno.h`. Important compile-time knobs are `__NR_recvmmsg`, `SC_recvmmsg`, `__NR_sendmmsg`, `SC_sendmmsg`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/libmmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/libsocketcall.c -->
# sources/test-tools/strace/tests/libsocketcall.c

Purpose: `libsocketcall.c` exercises strace decoding for syscall(s) `socketcall` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 50 line(s), 1043 byte(s); classification `test helper library`; functions `socketcall`; syscall markers `socketcall`. Key includes are `tests.h`, `errno.h`, `unistd.h`, `scno.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`socketcall`), invokes syscall targets (`socketcall`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `unistd.h`, `scno.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/libsocketcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/link-P.c -->
# sources/test-tools/strace/tests/link-P.c

Purpose: `link-P.c` is a thin compile-time variant that includes `link.c` after setting `PATH_TRACING`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 39 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `link.c`. Key macros/compile switches are `PATH_TRACING`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `link.c`. Important compile-time knobs are `PATH_TRACING`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: path filtering changes which syscall lines are expected.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: path-qualified trace filtering, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/link-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/link.c -->
# sources/test-tools/strace/tests/link.c

Purpose: `link.c` exercises strace decoding for syscall(s) `link` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 71 line(s), 1774 byte(s); classification `link path decoder exercise`; functions `main`; syscall markers `link`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`link`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: path filtering changes which syscall lines are expected; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 7 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, path-qualified trace filtering. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/linkat.c -->
# sources/test-tools/strace/tests/linkat.c

Purpose: `linkat.c` exercises strace decoding for syscall(s) `linkat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 288 line(s), 8701 byte(s); classification `linkat path and flag decoder exercise`; functions `mangle_secontext_field`, `main`; syscall markers `linkat`. Key includes are `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `string.h`, `secontext.h`, ... (12 total). Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`mangle_secontext_field`, `main`), invokes syscall targets (`linkat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `errno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, ... (12 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers, SELinux context helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 14 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/linkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/list_sigaction_signum.c -->
# sources/test-tools/strace/tests/list_sigaction_signum.c

Purpose: `list_sigaction_signum.c` is a focused strace test/helper source in the `signal action enumeration helper` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 35 line(s), 756 byte(s); classification `signal action enumeration helper`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `signal.h`, `stdio.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `signal.h`, `stdio.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 1 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/list_sigaction_signum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listmount-success.c -->
# sources/test-tools/strace/tests/listmount-success.c

Purpose: `listmount-success.c` is a thin compile-time variant that includes `listmount.c` after setting `INJECT_RETVAL`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 45 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `listmount.c`. Key macros/compile switches are `INJECT_RETVAL`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `listmount.c`. Important compile-time knobs are `INJECT_RETVAL`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listmount-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listmount.c -->
# sources/test-tools/strace/tests/listmount.c

Purpose: `listmount.c` exercises strace decoding for syscall(s) `listmount` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 157 line(s), 5299 byte(s); classification `listmount syscall decoder exercise`; functions `k_listmount`, `main`; syscall markers `listmount`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/mount.h`. Key macros/compile switches are `INJ_STR`, `INJ_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_listmount`, `main`), invokes syscall targets (`listmount`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/mount.h`. Important compile-time knobs are `INJ_STR`, `INJ_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 20 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listns-success.c -->
# sources/test-tools/strace/tests/listns-success.c

Purpose: `listns-success.c` is a thin compile-time variant that includes `listns.c` after setting `INJECT_RETVAL`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 42 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `listns.c`. Key macros/compile switches are `INJECT_RETVAL`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `listns.c`. Important compile-time knobs are `INJECT_RETVAL`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listns-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listns.c -->
# sources/test-tools/strace/tests/listns.c

Purpose: `listns.c` exercises strace decoding for syscall(s) `listns` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 169 line(s), 5413 byte(s); classification `listns syscall decoder exercise`; functions `k_listns`, `main`; syscall markers `listns`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/nsfs.h`. Key macros/compile switches are `INJ_STR`, `INJ_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_listns`, `main`), invokes syscall targets (`listns`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/nsfs.h`. Important compile-time knobs are `INJ_STR`, `INJ_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 21 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-P.c -->
# sources/test-tools/strace/tests/listxattrat-P.c

Purpose: `listxattrat-P.c` is a thin compile-time variant that includes `listxattrat.c` after setting `PATH_TRACING, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 121 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `listxattrat.c`. Key macros/compile switches are `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `listxattrat.c`. Important compile-time knobs are `PATH_TRACING`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: path filtering changes which syscall lines are expected.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, path-qualified trace filtering, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-y.c -->
# sources/test-tools/strace/tests/listxattrat-y.c

Purpose: `listxattrat-y.c` is a thin compile-time variant that includes `listxattrat.c` after setting `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 130 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `listxattrat.c`. Key macros/compile switches are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `listxattrat.c`. Important compile-time knobs are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-yy.c -->
# sources/test-tools/strace/tests/listxattrat-yy.c

Purpose: `listxattrat-yy.c` is a thin compile-time variant that includes `listxattrat.c` after setting `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 140 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `listxattrat.c`. Key macros/compile switches are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `listxattrat.c`. Important compile-time knobs are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat-yy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat.c -->
# sources/test-tools/strace/tests/listxattrat.c

Purpose: `listxattrat.c` exercises strace decoding for syscall(s) `listxattrat`, `setxattrat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 219 line(s), 5244 byte(s); classification `xattr-at syscall decoder exercise`; functions `k_listxattrat`, `k_setxattrat`, `main`; syscall markers `listxattrat`, `setxattrat`. Source-specific note: The xattr-at test creates an xattr fixture with `setxattrat`, then cross-products dirfds, path pointers, flags, output buffers, and sizes to exercise both pointer and decoded-list output. Key includes are `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/xattr.h`, `xlat/xattrat_flags.h`. Key macros/compile switches are `XLAT_MACROS_ONLY`, `XATTR_LIST_MAX`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_listxattrat`, `k_setxattrat`, `main`), invokes syscall targets (`listxattrat`, `setxattrat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 5 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding; the test writes an xattr fixture before listing it. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `linux/xattr.h`, `xlat/xattrat_flags.h`. Important compile-time knobs are `XLAT_MACROS_ONLY`, `XATTR_LIST_MAX`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; path filtering changes which syscall lines are expected; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 10 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison, path-qualified trace filtering. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/listxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/llseek.c -->
# sources/test-tools/strace/tests/llseek.c

Purpose: `llseek.c` exercises strace decoding for syscall(s) `_llseek` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 37 line(s), 719 byte(s); classification `seek syscall decoder exercise`; functions `main`; syscall markers `_llseek`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`_llseek`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/llseek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/localtime.c -->
# sources/test-tools/strace/tests/localtime.c

Purpose: `localtime.c` exercises strace decoding for syscall(s) `gettid` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 37 line(s), 706 byte(s); classification `timestamp/localtime harness`; functions `main`; syscall markers `gettid`. Key includes are `tests.h`, `assert.h`, `stdio.h`, `time.h`, `unistd.h`, `scno.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`gettid`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `assert.h`, `stdio.h`, `time.h`, `unistd.h`, `scno.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/localtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lock_file.c -->
# sources/test-tools/strace/tests/lock_file.c

Purpose: `lock_file.c` is a focused strace test/helper source in the `file-lock helper` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 37 line(s), 854 byte(s); classification `file-lock helper`; functions `lock_file_by_dirname`; syscall markers none visible in this file. Key includes are `tests.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/file.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`lock_file_by_dirname`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/file.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, allocation helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 1 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lock_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lookup_dcookie.c -->
# sources/test-tools/strace/tests/lookup_dcookie.c

Purpose: `lookup_dcookie.c` exercises strace decoding for syscall(s) `lookup_dcookie` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 68 line(s), 1478 byte(s); classification `lookup_dcookie syscall decoder exercise`; functions `do_lookup_cookie`, `main`; syscall markers `lookup_dcookie`. Key includes are `tests.h`, `scno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`do_lookup_cookie`, `main`), invokes syscall targets (`lookup_dcookie`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 6 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lookup_dcookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/looping_threads.c -->
# sources/test-tools/strace/tests/looping_threads.c

Purpose: `looping_threads.c` is a focused strace test/helper source in the `thread lifecycle helper` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 121 line(s), 2681 byte(s); classification `thread lifecycle helper`; functions `thread`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `assert.h`, `errno.h`, `pthread.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/wait.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`thread`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `assert.h`, `errno.h`, `pthread.h`, `signal.h`, `stdio.h`, `stdlib.h`, `unistd.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/looping_threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lseek.c -->
# sources/test-tools/strace/tests/lseek.c

Purpose: `lseek.c` exercises strace decoding for syscall(s) `lseek` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 44 line(s), 923 byte(s); classification `seek syscall decoder exercise`; functions `main`; syscall markers `lseek`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`lseek`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lseek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_get_self_attr-success.c -->
# sources/test-tools/strace/tests/lsm_get_self_attr-success.c

Purpose: `lsm_get_self_attr-success.c` is a thin compile-time variant that includes `lsm_get_self_attr.c` after setting `INJECT_RETVAL`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 53 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `lsm_get_self_attr.c`. Key macros/compile switches are `INJECT_RETVAL`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `lsm_get_self_attr.c`. Important compile-time knobs are `INJECT_RETVAL`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_get_self_attr-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_get_self_attr.c -->
# sources/test-tools/strace/tests/lsm_get_self_attr.c

Purpose: `lsm_get_self_attr.c` exercises strace decoding for syscall(s) `lsm_get_self_attr` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 197 line(s), 7299 byte(s); classification `LSM syscall decoder exercise`; functions `k_lsm_get_self_attr`, `main`; syscall markers `lsm_get_self_attr`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Key macros/compile switches are `INJ_STR`, `INJ_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_lsm_get_self_attr`, `main`), invokes syscall targets (`lsm_get_self_attr`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Important compile-time knobs are `INJ_STR`, `INJ_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, LSM UAPI.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 21 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_get_self_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_list_modules-success.c -->
# sources/test-tools/strace/tests/lsm_list_modules-success.c

Purpose: `lsm_list_modules-success.c` is a thin compile-time variant that includes `lsm_list_modules.c` after setting `INJECT_RETVAL`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 52 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `lsm_list_modules.c`. Key macros/compile switches are `INJECT_RETVAL`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `lsm_list_modules.c`. Important compile-time knobs are `INJECT_RETVAL`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_list_modules-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_list_modules.c -->
# sources/test-tools/strace/tests/lsm_list_modules.c

Purpose: `lsm_list_modules.c` exercises strace decoding for syscall(s) `lsm_list_modules` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 106 line(s), 2877 byte(s); classification `LSM syscall decoder exercise`; functions `k_lsm_list_modules`, `main`; syscall markers `lsm_list_modules`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Key macros/compile switches are `INJ_STR`, `INJ_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_lsm_list_modules`, `main`), invokes syscall targets (`lsm_list_modules`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 3 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Important compile-time knobs are `INJ_STR`, `INJ_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, LSM UAPI.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_list_modules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_set_self_attr.c -->
# sources/test-tools/strace/tests/lsm_set_self_attr.c

Purpose: `lsm_set_self_attr.c` exercises strace decoding for syscall(s) `lsm_set_self_attr` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 85 line(s), 2703 byte(s); classification `LSM syscall decoder exercise`; functions `k_lsm_set_self_attr`, `main`; syscall markers `lsm_set_self_attr`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_lsm_set_self_attr`, `main`), invokes syscall targets (`lsm_set_self_attr`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `string.h`, `unistd.h`, `linux/lsm.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, LSM UAPI.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 6 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lsm_set_self_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lstat.c -->
# sources/test-tools/strace/tests/lstat.c

Purpose: `lstat.c` exercises strace decoding for syscall(s) `lstat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 23 line(s), 455 byte(s); classification `lstat stat-structure wrapper`; functions none visible in this file; syscall markers `lstat`. Key includes are `tests.h`, `scno.h`, `lstatx.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `SAMPLE_SIZE`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`lstat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `lstatx.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `SAMPLE_SIZE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lstat64.c -->
# sources/test-tools/strace/tests/lstat64.c

Purpose: `lstat64.c` exercises strace decoding for syscall(s) `lstat64` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 25 line(s), 504 byte(s); classification `lstat stat-structure wrapper`; functions none visible in this file; syscall markers `lstat64`. Key includes are `tests.h`, `scno.h`, `lstatx.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `STRUCT_STAT`, `STRUCT_STAT_STR`, `STRUCT_STAT_IS_STAT64`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`lstat64`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `lstatx.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `STRUCT_STAT`, `STRUCT_STAT_STR`, `STRUCT_STAT_IS_STAT64`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lstat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/lstatx.c -->
# sources/test-tools/strace/tests/lstatx.c

Purpose: `lstatx.c` is a focused strace test/helper source in the `lstat stat-structure wrapper` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 20 line(s), 524 byte(s); classification `lstat stat-structure wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `xstatx.c`. Key macros/compile switches are `TEST_SYSCALL_INVOKE`, `PRINT_SYSCALL_HEADER`, `PRINT_SYSCALL_FOOTER`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `xstatx.c`. Important compile-time knobs are `TEST_SYSCALL_INVOKE`, `PRINT_SYSCALL_HEADER`, `PRINT_SYSCALL_FOOTER`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/lstatx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xabbrev.c -->
# sources/test-tools/strace/tests/madvise-Xabbrev.c

Purpose: `madvise-Xabbrev.c` is a thin compile-time variant that includes `madvise.c` after setting `XLAT_ABBREV`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 43 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `madvise.c`. Key macros/compile switches are `XLAT_ABBREV`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `madvise.c`. Important compile-time knobs are `XLAT_ABBREV`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xraw.c -->
# sources/test-tools/strace/tests/madvise-Xraw.c

Purpose: `madvise-Xraw.c` is a thin compile-time variant that includes `madvise.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 40 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `madvise.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `madvise.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xverbose.c -->
# sources/test-tools/strace/tests/madvise-Xverbose.c

Purpose: `madvise-Xverbose.c` is a thin compile-time variant that includes `madvise.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 44 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `madvise.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `madvise.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/madvise-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/madvise.c -->
# sources/test-tools/strace/tests/madvise.c

Purpose: `madvise.c` exercises strace decoding for syscall(s) `madvise` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 152 line(s), 5104 byte(s); classification `madvise decoder exercise`; functions `k_madvise`, `main`; syscall markers `madvise`. Key includes are `tests.h`, `stdint.h`, `stdio.h`, `sys/mman.h`, `unistd.h`, `scno.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_madvise`, `main`), invokes syscall targets (`madvise`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdint.h`, `stdio.h`, `sys/mman.h`, `unistd.h`, `scno.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 6 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xabbrev.c -->
# sources/test-tools/strace/tests/map_shadow_stack-Xabbrev.c

Purpose: `map_shadow_stack-Xabbrev.c` is a thin compile-time variant that includes `map_shadow_stack.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 30 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `map_shadow_stack.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `map_shadow_stack.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xraw.c -->
# sources/test-tools/strace/tests/map_shadow_stack-Xraw.c

Purpose: `map_shadow_stack-Xraw.c` is a thin compile-time variant that includes `map_shadow_stack.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 49 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `map_shadow_stack.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `map_shadow_stack.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xverbose.c -->
# sources/test-tools/strace/tests/map_shadow_stack-Xverbose.c

Purpose: `map_shadow_stack-Xverbose.c` is a thin compile-time variant that includes `map_shadow_stack.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 53 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `map_shadow_stack.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `map_shadow_stack.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack.c -->
# sources/test-tools/strace/tests/map_shadow_stack.c

Purpose: `map_shadow_stack.c` exercises strace decoding for syscall(s) `map_shadow_stack` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 70 line(s), 1705 byte(s); classification `map_shadow_stack decoder exercise`; functions `k_map_shadow_stack`, `main`; syscall markers `map_shadow_stack`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_map_shadow_stack`, `main`), invokes syscall targets (`map_shadow_stack`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/map_shadow_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/match.awk -->
# sources/test-tools/strace/tests/match.awk

Purpose: `match.awk` is an awk output matcher used by shell-driven tests to compare expected and observed strace lines while preserving controlled regex matching semantics.

Important APIs/types/functions: Complete-read metadata: 33 line(s), 578 byte(s); classification `awk matcher`; functions none visible in this file; syscall markers none visible in this file. Key includes are none visible in this file. Key macros/compile switches are none visible in this file.

Control flow: Input records are processed linearly. Pattern/action rules normalize or match each line and either print transformed records or fail the test when the stream no longer matches expected syscall-output structure.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily none visible in this file. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/match.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/maybe_switch_current_tcp--quiet-thread-execve.c -->
# sources/test-tools/strace/tests/maybe_switch_current_tcp--quiet-thread-execve.c

Purpose: `maybe_switch_current_tcp--quiet-thread-execve.c` is a thin compile-time variant that includes `maybe_switch_current_tcp.c` after setting `QUIET_MSG`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 58 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `maybe_switch_current_tcp.c`. Key macros/compile switches are `QUIET_MSG`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `maybe_switch_current_tcp.c`. Important compile-time knobs are `QUIET_MSG`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/maybe_switch_current_tcp--quiet-thread-execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/maybe_switch_current_tcp.c -->
# sources/test-tools/strace/tests/maybe_switch_current_tcp.c

Purpose: `maybe_switch_current_tcp.c` exercises strace decoding for syscall(s) `execveat`, `gettid` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 83 line(s), 1837 byte(s); classification `thread execve/current-tcp regression test`; functions `thread`, `main`; syscall markers `execveat`, `gettid`. Key includes are `tests.h`, `errno.h`, `pthread.h`, `stdio.h`, `unistd.h`, `scno.h`. Key macros/compile switches are `QUIET_MSG`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`thread`, `main`), invokes syscall targets (`execveat`, `gettid`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `pthread.h`, `stdio.h`, `unistd.h`, `scno.h`. Important compile-time knobs are `QUIET_MSG`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/maybe_switch_current_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xabbrev.c -->
# sources/test-tools/strace/tests/mbind-Xabbrev.c

Purpose: `mbind-Xabbrev.c` is a thin compile-time variant that includes `mbind.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 19 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mbind.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mbind.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xraw.c -->
# sources/test-tools/strace/tests/mbind-Xraw.c

Purpose: `mbind-Xraw.c` is a thin compile-time variant that includes `mbind.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 38 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mbind.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mbind.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xverbose.c -->
# sources/test-tools/strace/tests/mbind-Xverbose.c

Purpose: `mbind-Xverbose.c` is a thin compile-time variant that includes `mbind.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 42 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mbind.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mbind.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mbind-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mbind.c -->
# sources/test-tools/strace/tests/mbind.c

Purpose: `mbind.c` exercises strace decoding for syscall(s) `mbind` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 152 line(s), 4399 byte(s); classification `NUMA mbind decoder exercise`; functions `k_mbind`, `main`; syscall markers `mbind`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are `out_str`, `flags_str`, `out_str`, `flags_str`, `out_str`, `flags_str`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_mbind`, `main`), invokes syscall targets (`mbind`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are `out_str`, `flags_str`, `out_str`, `flags_str`, `out_str`, `flags_str`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 4 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/membarrier.c -->
# sources/test-tools/strace/tests/membarrier.c

Purpose: `membarrier.c` exercises strace decoding for syscall(s) `membarrier` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 129 line(s), 4107 byte(s); classification `membarrier decoder exercise`; functions `main`; syscall markers `membarrier`. Key includes are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`membarrier`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `assert.h`, `errno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 4 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/membarrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xabbrev.c -->
# sources/test-tools/strace/tests/memfd_create-Xabbrev.c

Purpose: `memfd_create-Xabbrev.c` is a thin compile-time variant that includes `memfd_create.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 26 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `memfd_create.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `memfd_create.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xraw.c -->
# sources/test-tools/strace/tests/memfd_create-Xraw.c

Purpose: `memfd_create-Xraw.c` is a thin compile-time variant that includes `memfd_create.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 45 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `memfd_create.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `memfd_create.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xverbose.c -->
# sources/test-tools/strace/tests/memfd_create-Xverbose.c

Purpose: `memfd_create-Xverbose.c` is a thin compile-time variant that includes `memfd_create.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 49 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `memfd_create.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `memfd_create.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create.c -->
# sources/test-tools/strace/tests/memfd_create.c

Purpose: `memfd_create.c` exercises strace decoding for syscall(s) `memfd_create` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 96 line(s), 2349 byte(s); classification `memfd_create decoder exercise`; functions `k_memfd_create`, `main`; syscall markers `memfd_create`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/memfd.h`. Key macros/compile switches are `flags1_str`, `memfd_create_fmt`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_memfd_create`, `main`), invokes syscall targets (`memfd_create`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `stdint.h`, `unistd.h`, `linux/memfd.h`. Important compile-time knobs are `flags1_str`, `memfd_create_fmt`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 8 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret-success-y.c -->
# sources/test-tools/strace/tests/memfd_secret-success-y.c

Purpose: `memfd_secret-success-y.c` is a thin compile-time variant that includes `memfd_secret-success.c` after setting `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 139 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `memfd_secret-success.c`. Key macros/compile switches are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `memfd_secret-success.c`. Important compile-time knobs are `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret-success-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret-success.c -->
# sources/test-tools/strace/tests/memfd_secret-success.c

Purpose: `memfd_secret-success.c` is a thin compile-time variant that includes `memfd_secret.c` after setting `RETVAL_INJECTED`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 52 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `memfd_secret.c`. Key macros/compile switches are `RETVAL_INJECTED`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `memfd_secret.c`. Important compile-time knobs are `RETVAL_INJECTED`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret.c -->
# sources/test-tools/strace/tests/memfd_secret.c

Purpose: `memfd_secret.c` exercises strace decoding for syscall(s) `memfd_secret` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 82 line(s), 1794 byte(s); classification `memfd_secret decoder exercise`; functions `sys_memfd_secret`, `main`; syscall markers `memfd_secret`. Key includes are `tests.h`, `kernel_fcntl.h`, `scno.h`, `inttypes.h`, `errno.h`, `stdio.h`, `stdint.h`, `unistd.h`. Key macros/compile switches are `RETVAL_INJECTED`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD_PATH`, `INJ_STR`, `INJ_FD_STR`, `INJ_STR`, `INJ_FD_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`sys_memfd_secret`, `main`), invokes syscall targets (`memfd_secret`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `kernel_fcntl.h`, `scno.h`, `inttypes.h`, `errno.h`, `stdio.h`, `stdint.h`, `unistd.h`. Important compile-time knobs are `RETVAL_INJECTED`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD_PATH`, `INJ_STR`, `INJ_FD_STR`, `INJ_STR`, `INJ_FD_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: injected success paths must not be confused with real kernel support; syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/memfd_secret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/migrate_pages--pidns-translation.c -->
# sources/test-tools/strace/tests/migrate_pages--pidns-translation.c

Purpose: `migrate_pages--pidns-translation.c` is a thin compile-time variant that includes `migrate_pages.c` after setting `PIDNS_TRANSLATION`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 53 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `migrate_pages.c`. Key macros/compile switches are `PIDNS_TRANSLATION`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `migrate_pages.c`. Important compile-time knobs are `PIDNS_TRANSLATION`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: pid namespace translation can make expected PIDs architecture- and harness-sensitive.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: pid-namespace translated expected output, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/migrate_pages--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/migrate_pages.c -->
# sources/test-tools/strace/tests/migrate_pages.c

Purpose: `migrate_pages.c` exercises strace decoding for syscall(s) `migrate_pages` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 33 line(s), 680 byte(s); classification `migrate_pages decoder exercise`; functions `main`; syscall markers `migrate_pages`. Key includes are `tests.h`, `scno.h`, `pidns.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`migrate_pages`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `pidns.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, pid namespace expected-output helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/migrate_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mincore.c -->
# sources/test-tools/strace/tests/mincore.c

Purpose: `mincore.c` is a focused strace test/helper source in the `mincore decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 58 line(s), 1255 byte(s); classification `mincore decoder exercise`; functions `print_mincore`, `test_mincore`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_mincore`, `test_mincore`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 1 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 7 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mincore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mkdir.c -->
# sources/test-tools/strace/tests/mkdir.c

Purpose: `mkdir.c` exercises strace decoding for syscall(s) `mkdir` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 21 line(s), 329 byte(s); classification `mkdir mode wrapper`; functions none visible in this file; syscall markers `mkdir`. Key includes are `tests.h`, `scno.h`, `umode_t.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`mkdir`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `umode_t.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mkdirat.c -->
# sources/test-tools/strace/tests/mkdirat.c

Purpose: `mkdirat.c` exercises strace decoding for syscall(s) `mkdirat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 18 line(s), 413 byte(s); classification `mkdir mode wrapper`; functions none visible in this file; syscall markers `mkdirat`. Key includes are `tests.h`, `scno.h`, `umode_t.c`. Key macros/compile switches are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_SYSCALL_PREFIX_ARGS`, `TEST_SYSCALL_PREFIX_STR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (none visible in this file), invokes syscall targets (`mkdirat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `umode_t.c`. Important compile-time knobs are `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_SYSCALL_PREFIX_ARGS`, `TEST_SYSCALL_PREFIX_STR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mkdirat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mknod.c -->
# sources/test-tools/strace/tests/mknod.c

Purpose: `mknod.c` exercises strace decoding for syscall(s) `mknod` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 81 line(s), 1948 byte(s); classification `mknod decoder exercise`; functions `call_mknod`, `main`; syscall markers `mknod`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `sys/stat.h`, `sys/sysmacros.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`call_mknod`, `main`), invokes syscall targets (`mknod`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `sys/stat.h`, `sys/sysmacros.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mknodat.c -->
# sources/test-tools/strace/tests/mknodat.c

Purpose: `mknodat.c` exercises strace decoding for syscall(s) `mknodat` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 75 line(s), 2039 byte(s); classification `mknod decoder exercise`; functions `call_mknodat`, `main`; syscall markers `mknodat`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `sys/stat.h`, `sys/sysmacros.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`call_mknodat`, `main`), invokes syscall targets (`mknodat`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `sys/stat.h`, `sys/sysmacros.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mknodat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mlock.c -->
# sources/test-tools/strace/tests/mlock.c

Purpose: `mlock.c` exercises strace decoding for syscall(s) `mlock`, `munlock` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 38 line(s), 663 byte(s); classification `memory-locking decoder exercise`; functions `main`; syscall markers `mlock`, `munlock`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`mlock`, `munlock`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mlock2.c -->
# sources/test-tools/strace/tests/mlock2.c

Purpose: `mlock2.c` exercises strace decoding for syscall(s) `mlock2` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 29 line(s), 653 byte(s); classification `memory-locking decoder exercise`; functions `main`; syscall markers `mlock2`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`mlock2`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mlock2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mlockall.c -->
# sources/test-tools/strace/tests/mlockall.c

Purpose: `mlockall.c` is a focused strace test/helper source in the `memory-locking decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 26 line(s), 459 byte(s); classification `memory-locking decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mlockall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xabbrev.c -->
# sources/test-tools/strace/tests/mmap-Xabbrev.c

Purpose: `mmap-Xabbrev.c` is a thin compile-time variant that includes `mmap.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 18 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xraw.c -->
# sources/test-tools/strace/tests/mmap-Xraw.c

Purpose: `mmap-Xraw.c` is a thin compile-time variant that includes `mmap.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 41 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xverbose.c -->
# sources/test-tools/strace/tests/mmap-Xverbose.c

Purpose: `mmap-Xverbose.c` is a thin compile-time variant that includes `mmap.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 41 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap.c -->
# sources/test-tools/strace/tests/mmap.c

Purpose: `mmap.c` is a focused strace test/helper source in the `mmap decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 134 line(s), 3950 byte(s); classification `mmap decoder exercise`; functions `main`; syscall markers none visible in this file. Source-specific note: The mmap test intentionally prints different flag/protection/fd/offset combinations and is reused by `mmap64.c` and xlat wrappers to verify mmap argument rendering. Key includes are `tests.h`, `stdio.h`, `stdint.h`, `unistd.h`, `limits.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `stdint.h`, `unistd.h`, `limits.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 23 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xabbrev.c -->
# sources/test-tools/strace/tests/mmap64-Xabbrev.c

Purpose: `mmap64-Xabbrev.c` is a thin compile-time variant that includes `mmap64.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 20 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap64.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap64.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xraw.c -->
# sources/test-tools/strace/tests/mmap64-Xraw.c

Purpose: `mmap64-Xraw.c` is a thin compile-time variant that includes `mmap64.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 43 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap64.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap64.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xverbose.c -->
# sources/test-tools/strace/tests/mmap64-Xverbose.c

Purpose: `mmap64-Xverbose.c` is a thin compile-time variant that includes `mmap64.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 43 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap64.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap64.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64.c -->
# sources/test-tools/strace/tests/mmap64.c

Purpose: `mmap64.c` is a thin compile-time variant that includes `mmap.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 18 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmap.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmap.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmap64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg-silent.c -->
# sources/test-tools/strace/tests/mmsg-silent.c

Purpose: `mmsg-silent.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 44 line(s), 1014 byte(s); classification `mmsg socket-message decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `msghdr.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `msghdr.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, message-header helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 3 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg-silent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg.c -->
# sources/test-tools/strace/tests/mmsg.c

Purpose: `mmsg.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 181 line(s), 4893 byte(s); classification `mmsg socket-message decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `assert.h`, `unistd.h`, `msghdr.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `assert.h`, `unistd.h`, `msghdr.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, message-header helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 8 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg_name-v.c -->
# sources/test-tools/strace/tests/mmsg_name-v.c

Purpose: `mmsg_name-v.c` is a thin compile-time variant that includes `mmsg_name.c` after setting `VERBOSE, TEST_NAME`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 4 line(s), 125 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mmsg_name.c`. Key macros/compile switches are `VERBOSE`, `TEST_NAME`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mmsg_name.c`. Important compile-time knobs are `VERBOSE`, `TEST_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg_name-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg_name.c -->
# sources/test-tools/strace/tests/mmsg_name.c

Purpose: `mmsg_name.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 219 line(s), 5771 byte(s); classification `mmsg socket-message decoder exercise`; functions `print_msghdr`, `test_mmsg_name`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/un.h`, `msghdr.h`. Key macros/compile switches are `IOV_MAX1`, `TEST_NAME`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_msghdr`, `test_mmsg_name`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 6 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/un.h`, ... (9 total). Important compile-time knobs are `IOV_MAX1`, `TEST_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, message-header helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 30 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mmsg_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/modify_ldt.c -->
# sources/test-tools/strace/tests/modify_ldt.c

Purpose: `modify_ldt.c` exercises strace decoding for syscall(s) `modify_ldt` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 125 line(s), 2902 byte(s); classification `modify_ldt decoder exercise`; functions `printrc`, `main`; syscall markers `modify_ldt`. Key includes are `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `unistd.h`, `print_user_desc.c`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`printrc`, `main`), invokes syscall targets (`modify_ldt`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `unistd.h`, `print_user_desc.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 15 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/modify_ldt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xabbrev.c -->
# sources/test-tools/strace/tests/mount-Xabbrev.c

Purpose: `mount-Xabbrev.c` is a thin compile-time variant that includes `mount.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 19 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mount.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mount.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xraw.c -->
# sources/test-tools/strace/tests/mount-Xraw.c

Purpose: `mount-Xraw.c` is a thin compile-time variant that includes `mount.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 38 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mount.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mount.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xverbose.c -->
# sources/test-tools/strace/tests/mount-Xverbose.c

Purpose: `mount-Xverbose.c` is a thin compile-time variant that includes `mount.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 42 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mount.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mount.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount.c -->
# sources/test-tools/strace/tests/mount.c

Purpose: `mount.c` is a focused strace test/helper source in the `mount decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 116 line(s), 3894 byte(s); classification `mount decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `unistd.h`, `sys/mount.h`. Key macros/compile switches are `MS_MGC_VAL`, `MS_RELATIME`, `str_unknown`, `str_submount_200`, `str_mgc_val`, `str_remount`, `str_bind`, `str_ro_nosuid_nodev_noexec`, `str_ro_nosuid_nodev_noexec_relatime`, `str_unknown`, ... (23 total).

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `unistd.h`, `sys/mount.h`. Important compile-time knobs are `MS_MGC_VAL`, `MS_RELATIME`, `str_unknown`, `str_submount_200`, `str_mgc_val`, `str_remount`, `str_bind`, `str_ro_nosuid_nodev_noexec`, ... (23 total). Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 12 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount_setattr-P.c -->
# sources/test-tools/strace/tests/mount_setattr-P.c

Purpose: `mount_setattr-P.c` is a thin compile-time variant that includes `mount_setattr.c` after setting `PATH_TRACING`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 48 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mount_setattr.c`. Key macros/compile switches are `PATH_TRACING`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mount_setattr.c`. Important compile-time knobs are `PATH_TRACING`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: path filtering changes which syscall lines are expected.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: path-qualified trace filtering, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount_setattr-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mount_setattr.c -->
# sources/test-tools/strace/tests/mount_setattr.c

Purpose: `mount_setattr.c` exercises strace decoding for syscall(s) `mount_setattr` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 175 line(s), 5720 byte(s); classification `mount_setattr decoder exercise`; functions `k_mount_setattr`, `main`; syscall markers `mount_setattr`. Key includes are `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `stdint.h`, `string.h`, `unistd.h`, `linux/fcntl.h`, `linux/mount.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_mount_setattr`, `main`), invokes syscall targets (`mount_setattr`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 2 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `stdint.h`, `string.h`, `unistd.h`, `linux/fcntl.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: path filtering changes which syscall lines are expected; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 18 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison, path-qualified trace filtering. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mount_setattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_mount-P.c -->
# sources/test-tools/strace/tests/move_mount-P.c

Purpose: `move_mount-P.c` is a thin compile-time variant that includes `move_mount.c` after setting `PATH_TRACING`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 45 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `move_mount.c`. Key macros/compile switches are `PATH_TRACING`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `move_mount.c`. Important compile-time knobs are `PATH_TRACING`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: path filtering changes which syscall lines are expected.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: path-qualified trace filtering, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_mount-P.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_mount.c -->
# sources/test-tools/strace/tests/move_mount.c

Purpose: `move_mount.c` exercises strace decoding for syscall(s) `move_mount` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 120 line(s), 4003 byte(s); classification `move_mount decoder exercise`; functions `k_move_mount`, `main`; syscall markers `move_mount`. Key includes are `tests.h`, `scno.h`, `fcntl.h`, `limits.h`, `stdio.h`, `stdint.h`, `unistd.h`. Key macros/compile switches are `f_flags_str`, `t_flags_str`, `set_group_str`, `beneath_str`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_move_mount`, `main`), invokes syscall targets (`move_mount`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `fcntl.h`, `limits.h`, `stdio.h`, `stdint.h`, `unistd.h`. Important compile-time knobs are `f_flags_str`, `t_flags_str`, `set_group_str`, `beneath_str`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: path filtering changes which syscall lines are expected; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 12 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, path-qualified trace filtering. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages--pidns-translation.c -->
# sources/test-tools/strace/tests/move_pages--pidns-translation.c

Purpose: `move_pages--pidns-translation.c` is a thin compile-time variant that includes `move_pages.c` after setting `PIDNS_TRANSLATION`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 50 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `move_pages.c`. Key macros/compile switches are `PIDNS_TRANSLATION`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `move_pages.c`. Important compile-time knobs are `PIDNS_TRANSLATION`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: pid namespace translation can make expected PIDs architecture- and harness-sensitive.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: pid-namespace translated expected output, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xabbrev.c -->
# sources/test-tools/strace/tests/move_pages-Xabbrev.c

Purpose: `move_pages-Xabbrev.c` is a thin compile-time variant that includes `move_pages.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 24 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `move_pages.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `move_pages.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xraw.c -->
# sources/test-tools/strace/tests/move_pages-Xraw.c

Purpose: `move_pages-Xraw.c` is a thin compile-time variant that includes `move_pages.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 43 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `move_pages.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `move_pages.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xverbose.c -->
# sources/test-tools/strace/tests/move_pages-Xverbose.c

Purpose: `move_pages-Xverbose.c` is a thin compile-time variant that includes `move_pages.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 47 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `move_pages.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `move_pages.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages.c -->
# sources/test-tools/strace/tests/move_pages.c

Purpose: `move_pages.c` exercises strace decoding for syscall(s) `move_pages` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 240 line(s), 5444 byte(s); classification `move_pages decoder exercise`; functions `print_page_array`, `print_node_array`, `print_status_array`, `print_stat_pages`, `print_move_pages`, `main`; syscall markers `move_pages`. Source-specific note: The NUMA page-migration test prints page, node, and status arrays with length truncation and pid namespace support, so array decoding and target-pid formatting are both in scope. Key includes are `tests.h`, `scno.h`, `pidns.h`, `errno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are `MAX_STRLEN`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_page_array`, `print_node_array`, `print_status_array`, `print_stat_pages`, `print_move_pages`, `main`), invokes syscall targets (`move_pages`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 3 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `pidns.h`, `errno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are `MAX_STRLEN`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, pid namespace expected-output helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; syscall availability differs across kernels and personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 42 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/move_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mq.c -->
# sources/test-tools/strace/tests/mq.c

Purpose: `mq.c` is a focused strace test/helper source in the `POSIX message-queue open/attribute test` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 60 line(s), 1418 byte(s); classification `POSIX message-queue open/attribute test`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `fcntl.h`, `mqueue.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `xmalloc.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `fcntl.h`, `mqueue.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/stat.h`, `xmalloc.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers, allocation helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 6 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv-read.c -->
# sources/test-tools/strace/tests/mq_sendrecv-read.c

Purpose: `mq_sendrecv-read.c` is a thin compile-time variant that includes `mq_sendrecv.c` after setting `DUMPIO_READ, MQ_NAME`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 3 line(s), 89 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mq_sendrecv.c`. Key macros/compile switches are `DUMPIO_READ`, `MQ_NAME`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mq_sendrecv.c`. Important compile-time knobs are `DUMPIO_READ`, `MQ_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv-write.c -->
# sources/test-tools/strace/tests/mq_sendrecv-write.c

Purpose: `mq_sendrecv-write.c` is a thin compile-time variant that includes `mq_sendrecv.c` after setting `DUMPIO_WRITE, MQ_NAME`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 3 line(s), 91 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `mq_sendrecv.c`. Key macros/compile switches are `DUMPIO_WRITE`, `MQ_NAME`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `mq_sendrecv.c`. Important compile-time knobs are `DUMPIO_WRITE`, `MQ_NAME`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv.c -->
# sources/test-tools/strace/tests/mq_sendrecv.c

Purpose: `mq_sendrecv.c` exercises strace decoding for syscall(s) `mq_getsetattr`, `mq_notify`, `mq_open`, `mq_timedreceive`, `mq_timedsend`, `mq_unlink` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 452 line(s), 13714 byte(s); classification `POSIX message-queue send/receive decoder exercise`; functions `printstr`, `dumpstr`, `cleanup`, `do_send`, `do_recv`, `main`; syscall markers `mq_getsetattr`, `mq_notify`, `mq_open`, `mq_timedreceive`, `mq_timedsend`, `mq_unlink`. Source-specific note: The message-queue send/receive test covers `mq_open`, `mq_timedsend`, `mq_timedreceive`, `mq_notify`, `mq_getsetattr`, cleanup, dumpio read/write variants, signal notification, and timed argument printing. Key includes are `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `time.h`, ... (14 total). Key macros/compile switches are `DUMPIO_READ`, `DUMPIO_WRITE`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`printstr`, `dumpstr`, `cleanup`, `do_send`, `do_recv`, `main`), invokes syscall targets (`mq_getsetattr`, `mq_notify`, `mq_open`, `mq_timedreceive`, `mq_timedsend`, `mq_unlink`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 6 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `signal.h`, `stdio.h`, `stdlib.h`, ... (14 total). Important compile-time knobs are `DUMPIO_READ`, `DUMPIO_WRITE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers, allocation helpers.

Risks: syscall availability differs across kernels and personalities; word-size dependent printing can regress on ILP32/LP64 personalities; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 45 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mq_sendrecv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/mseal.c -->
# sources/test-tools/strace/tests/mseal.c

Purpose: `mseal.c` exercises strace decoding for syscall(s) `mseal` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 29 line(s), 620 byte(s); classification `mseal decoder exercise`; functions `main`; syscall markers `mseal`. Key includes are `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (`mseal`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/mseal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/msg_control-v.c -->
# sources/test-tools/strace/tests/msg_control-v.c

Purpose: `msg_control-v.c` is a thin compile-time variant that includes `msg_control.c` after setting `VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 3 line(s), 97 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `msg_control.c`. Key macros/compile switches are `VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `msg_control.c`. Important compile-time knobs are `VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/msg_control-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/msg_control.c -->
# sources/test-tools/strace/tests/msg_control.c

Purpose: `msg_control.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 1063 line(s), 33383 byte(s); classification `recvmsg control-message decoder exercise`; functions `print_fds`, `test_scm_rights1`, `test_scm_rights2`, `test_scm_rights3`, `test_scm_timestamp_old`, `test_scm_timestampns_old`, `test_scm_timestamping_old`, `test_scm_timestamp_new`, `test_scm_timestampns_new`, `test_scm_timestamping_new`, `print_security`, `test_scm_security`, ... (26 total); syscall markers none visible in this file. Source-specific note: The ancillary-data test builds many `cmsghdr` payload families including `SCM_RIGHTS`, timestamps, security labels, IP/IPV6/TCP options, malformed lengths, and verbose vs abbreviated decoding paths. Key includes are `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `net/if.h`, `netinet/in.h`, ... (18 total). Key macros/compile switches are `XLAT_MACROS_ONLY`, `SOL_IP`, `SOL_TCP`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`print_fds`, `test_scm_rights1`, `test_scm_rights2`, `test_scm_rights3`, `test_scm_timestamp_old`, `test_scm_timestampns_old`, `test_scm_timestamping_old`, `test_scm_timestamp_new`, ... (26 total)), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 11 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries; temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `errno.h`, `limits.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, ... (18 total). Important compile-time knobs are `XLAT_MACROS_ONLY`, `SOL_IP`, `SOL_TCP`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 60 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/msg_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/msg_name.c -->
# sources/test-tools/strace/tests/msg_name.c

Purpose: `msg_name.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 160 line(s), 5172 byte(s); classification `recvmsg address-name decoder exercise`; functions `send_recv`, `test_msg_name`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`. Key macros/compile switches are `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`send_recv`, `test_msg_name`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stddef.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`. Important compile-time knobs are `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`, `TEST_RECVMSG_BOGUS_ADDR`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 9 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/msg_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/munlockall.c -->
# sources/test-tools/strace/tests/munlockall.c

Purpose: `munlockall.c` is a focused strace test/helper source in the `memory-locking decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 20 line(s), 311 byte(s); classification `memory-locking decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 2 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/munlockall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nanosleep.c -->
# sources/test-tools/strace/tests/nanosleep.c

Purpose: `nanosleep.c` exercises strace decoding for syscall(s) `nanosleep` by issuing direct kernel calls with valid, invalid, boundary, and architecture-sensitive arguments, then printing the exact line the strace test harness expects.

Important APIs/types/functions: Complete-read metadata: 132 line(s), 3688 byte(s); classification `nanosleep interrupted-time decoder exercise`; functions `k_nanosleep`, `handler`, `main`; syscall markers `nanosleep`. Key includes are `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `sys/time.h`, `unistd.h`, `kernel_old_timespec.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`k_nanosleep`, `handler`, `main`), invokes syscall targets (`nanosleep`), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `scno.h`, `assert.h`, `stdio.h`, `stdint.h`, `signal.h`, `sys/time.h`, `unistd.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: raw syscall numbers, strace testsuite helpers.

Risks: syscall availability differs across kernels and personalities.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 10 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features, return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-all-netlink.c -->
# sources/test-tools/strace/tests/net--decode-fds-all-netlink.c

Purpose: `net--decode-fds-all-netlink.c` is a thin compile-time variant that includes `net--decode-fds-socket-netlink.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 44 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net--decode-fds-socket-netlink.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net--decode-fds-socket-netlink.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-all-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-dev-netlink.c -->
# sources/test-tools/strace/tests/net--decode-fds-dev-netlink.c

Purpose: `net--decode-fds-dev-netlink.c` is a thin compile-time variant that includes `net--decode-fds-none-netlink.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 42 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net--decode-fds-none-netlink.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net--decode-fds-none-netlink.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-dev-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-none-netlink.c -->
# sources/test-tools/strace/tests/net--decode-fds-none-netlink.c

Purpose: `net--decode-fds-none-netlink.c` is a thin compile-time variant that includes `net-yy-netlink.c` after setting `PRINT_SOCK`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 49 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-yy-netlink.c`. Key macros/compile switches are `PRINT_SOCK`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-yy-netlink.c`. Important compile-time knobs are `PRINT_SOCK`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-none-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-path-netlink.c -->
# sources/test-tools/strace/tests/net--decode-fds-path-netlink.c

Purpose: `net--decode-fds-path-netlink.c` is a thin compile-time variant that includes `net-yy-netlink.c` after setting `PRINT_SOCK`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 49 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-yy-netlink.c`. Key macros/compile switches are `PRINT_SOCK`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-yy-netlink.c`. Important compile-time knobs are `PRINT_SOCK`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-path-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-socket-netlink.c -->
# sources/test-tools/strace/tests/net--decode-fds-socket-netlink.c

Purpose: `net--decode-fds-socket-netlink.c` is a thin compile-time variant that includes `net-yy-netlink.c` after setting `PRINT_SOCK`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 49 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-yy-netlink.c`. Key macros/compile switches are `PRINT_SOCK`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-yy-netlink.c`. Important compile-time knobs are `PRINT_SOCK`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net--decode-fds-socket-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-accept-connect.c -->
# sources/test-tools/strace/tests/net-accept-connect.c

Purpose: `net-accept-connect.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 88 line(s), 1909 byte(s); classification `accept/connect socket lifecycle test`; functions `handler`, `main`; syscall markers none visible in this file. Key includes are `tests.h`, `assert.h`, `stddef.h`, `string.h`, `signal.h`, `unistd.h`, `sys/wait.h`, `sys/socket.h`, `sys/un.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`handler`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. temporary file descriptors, sockets, pipes, or message queues may be opened for realistic fd/path decoding; process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `assert.h`, `stddef.h`, `string.h`, `signal.h`, `unistd.h`, `sys/wait.h`, `sys/socket.h`, ... (9 total). Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: skip paths for unsupported kernel/proc features. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-accept-connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-icmp_filter.c -->
# sources/test-tools/strace/tests/net-icmp_filter.c

Purpose: `net-icmp_filter.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 79 line(s), 2291 byte(s); classification `ICMP filter socket option decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `sys/socket.h`, `linux/icmp.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/socket.h`, `linux/icmp.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 10 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-icmp_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xabbrev.c -->
# sources/test-tools/strace/tests/net-packet_mreq-Xabbrev.c

Purpose: `net-packet_mreq-Xabbrev.c` is a thin compile-time variant that includes `net-packet_mreq.c` after setting `no explicit macro except inclusion`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 1 line(s), 29 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-packet_mreq.c`. Key macros/compile switches are none visible in this file.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-packet_mreq.c`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xraw.c -->
# sources/test-tools/strace/tests/net-packet_mreq-Xraw.c

Purpose: `net-packet_mreq-Xraw.c` is a thin compile-time variant that includes `net-packet_mreq.c` after setting `XLAT_RAW`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 48 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-packet_mreq.c`. Key macros/compile switches are `XLAT_RAW`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-packet_mreq.c`. Important compile-time knobs are `XLAT_RAW`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xverbose.c -->
# sources/test-tools/strace/tests/net-packet_mreq-Xverbose.c

Purpose: `net-packet_mreq-Xverbose.c` is a thin compile-time variant that includes `net-packet_mreq.c` after setting `XLAT_VERBOSE`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 52 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-packet_mreq.c`. Key macros/compile switches are `XLAT_VERBOSE`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-packet_mreq.c`. Important compile-time knobs are `XLAT_VERBOSE`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: symbolic flag/xlat output comparison, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq.c -->
# sources/test-tools/strace/tests/net-packet_mreq.c

Purpose: `net-packet_mreq.c` exercises socket/message decoding paths by constructing kernel-visible sockets, message headers, ancillary data, or socket options and emitting expected output for strace comparison.

Important APIs/types/functions: Complete-read metadata: 206 line(s), 7599 byte(s); classification `packet_mreq socket option decoder exercise`; functions `packet_mreq_membership`, `test_packet_mreq`, `main`; syscall markers none visible in this file. Source-specific note: The packet membership test exercises `packet_mreq` fields and membership constants under xlat raw/verbose/abbrev modes. Key includes are `tests.h`, `stdio.h`, `sys/socket.h`, `linux/if_packet.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`packet_mreq_membership`, `test_packet_mreq`, `main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 9 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `sys/socket.h`, `linux/if_packet.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 43 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-packet_mreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-sockaddr--pidns-translation.c -->
# sources/test-tools/strace/tests/net-sockaddr--pidns-translation.c

Purpose: `net-sockaddr--pidns-translation.c` is a thin compile-time variant that includes `net-sockaddr.c` after setting `PIDNS_TRANSLATION`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 52 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `net-sockaddr.c`. Key macros/compile switches are `PIDNS_TRANSLATION`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `net-sockaddr.c`. Important compile-time knobs are `PIDNS_TRANSLATION`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: pid namespace translation can make expected PIDs architecture- and harness-sensitive.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: pid-namespace translated expected output, successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-sockaddr--pidns-translation.c -->
