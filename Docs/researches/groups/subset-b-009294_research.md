# subset-b-009294 Research

Grouped research report for the exact source files assigned to subset-b-009294. Each section preserves the source path in the title and is delimited for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/clock_getres01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/clock_getres01.c

Purpose: LTP regression coverage for `clock_getres` behavior. Source intent: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Authors: Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> LTP authors: Manas Kumar Nayak maknayak@in.ibm.com> Zeng Linggang <zenglg.jy@cn.fujitsu.com> Cyril Hrubis <chrubis@suse.cz> The file was read in full for this report (101 lines, 3269 bytes).

Important APIs/types/functions: Primary functions are `setup`, `do_test`. Important call/API signals are `tst_res`, `TEST`, `tst_ts_get`, `clock_getres`, `tst_strerrno`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct test_variants`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `do_test`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `"tst_timer.h"`, `"lapi/posix_clocks.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clock_getres` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_PROCESS_CPUTIME_ID, CLOCK_THREAD_CPUTIME_ID, CLOCK_MONOTONIC_RAW, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC_COARSE, CLOCK_BOOTTIME, CLOCK_REALTIME_ALARM, CLOCK_BOOTTIME_ALARM`; harness fields `.test, .setup, .tcnt`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/clock_getres01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/Makefile

Purpose: Build integration for the LTP clock_gettime syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `LTPLIBS = vdso`, `LDLIBS+=-lrt`, `clock_gettime04: LTPLDLIBS = -lltpvdso`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime01.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2019 Linaro Limited. Author: Rafael David Tinoco <rafael.tinoco@linaro.org> \ Basic test for clock_gettime(2) on multiple clocks: #. CLOCK_BOOTTIME errors: allow unsupported clock types success: also check if timespec was changed The file was read in full for this report (131 lines, 3111 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_clock_gettime`. Important call/API signals are `clock_gettime`, `tst_res`, `SAFE_FILE_SCANF`, `verify_clock_gettime`, `TEST`, `tst_ts_get`, `tst_clock_name`, `tst_ts_valid`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_PROCESS_CPUTIME_ID, CLOCK_THREAD_CPUTIME_ID, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2019 Linaro Limited. Author: Rafael David Tinoco <rafael.tinoco@linaro.org> \ Bad argument tests for clock_gettime(2) on multiple clocks: #. It justifies testing EFAULT for all. The file was read in full for this report (159 lines, 3721 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_clock_gettime`. Important call/API signals are `clock_gettime`, `tst_res`, `tst_get_bad_addr`, `tst_get_max_clocks`, `verify_clock_gettime`, `tst_ts_get`, `TEST`, `tst_clock_name`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EFAULT, CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_PROCESS_CPUTIME_ID, CLOCK_THREAD_CPUTIME_ID, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2020 Cyril Hrubis <chrubis@suse.cz> \ After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'. The file was read in full for this report (143 lines, 3736 bytes).

Important APIs/types/functions: Primary functions are `child`, `verify_ns_clock`, `setup`, `cleanup`. Important call/API signals are `clock_gettime`, `tst_ts_get`, `tst_res`, `tst_clock_name`, `SAFE_SETNS`, `tst_ts_diff_ms`, `verify_ns_clock`, `SAFE_UNSHARE`, `SAFE_FILE_PRINTF`, `SAFE_FORK`, `tst_is_virt`, `SAFE_OPEN`, `SAFE_CLOSE`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_ns_clock`; cleanup-oriented functions `cleanup`; child-oriented functions `child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_NEWTIME, CLOCK_MONOTONIC, CLOCK_BOOTTIME, CLOCK_MONOTONIC_RAW, CLOCK_MONOTONIC_COARSE, O_RDONLY`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .needs_kconfigs, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2020 Linaro Limited. Author: Viresh Kumar<viresh.kumar@linaro.org> \ Check time difference between successive readings and report a bug if difference found to be over 5 ms. This test reports a s390x BUG which has been fixed in kernel v5.12 in 5b43bd184530 ("s390/vdso: fix initializing and updating of vdso_data") The array defines the type to TST_LIBC_TIMESPEC and so we can cast this into struct. The file was read in full for this report (194 lines, 5074 bytes).

Important APIs/types/functions: Primary functions are `do_vdso_gettime`, `vdso_gettime`, `vdso_gettime64`, `my_gettimeofday`, `setup`, `run`. Important call/API signals are `tst_brk`, `tst_clock_name`, `tst_timespec_from_us`, `tst_timeval_to_us`, `clock_getres`, `tst_is_virt`, `tst_res`, `find_clock_gettime_vdso`, `clock_gettime`, `tst_ts_get`, `tst_ts_to_ns`. Relevant structs/types include `struct timeval`, `struct timespec`, `struct time64_variants`, `struct tst_ts`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; do_-oriented functions `do_vdso_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"tse_parse_vdso.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ENOSYS, CLOCK_REALTIME, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) Red Hat, Inc., 2012. Copyright (c) Linux Test Project, 2019 Author: Lingzhu Xiang <lxiang@redhat.com> Ported to new library: 07/2019 Christian Amann <camann@suse.com> \ Regression test for hrtimer early expiration during and after leap seconds A bug in the hrtimer subsystem caused all TIMER_ABSTIME CLOCK_REALTIME timers to expire one second early during leap second. The file was read in full for this report (206 lines, 5049 bytes).

Important APIs/types/functions: Primary functions are `in_order`, `adjtimex_status`, `test_hrtimer_early_expiration`, `run_leapsec`, `setup`, `cleanup`. Important call/API signals are `adjtimex_status`, `tst_brk`, `tst_res`, `test_hrtimer_early_expiration`, `SAFE_CLOCK_GETTIME`, `clock_nanosleep`, `SAFE_CLOCK_SETTIME`, `clock_was_set`. Defined constants/macros include `SECONDS_BEFORE_LEAP`, `SECONDS_AFTER_LEAP`. Relevant structs/types include `struct timespec`, `struct timex`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_leapsec`; test-oriented functions `test_hrtimer_early_expiration`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<errno.h>`, `<stdio.h>`, `<time.h>`, `"tst_test.h"`, `"tst_safe_clocks.h"`, `"lapi/common_timers.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLOCK_REALTIME, CLOCK_MONOTONIC`; harness fields `.test_all, .setup, .cleanup, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/Makefile

Purpose: Build integration for the LTP clock_nanosleep syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `LDLIBS			+= -lpthread -lrt`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep01.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Copyright (c) 2016 Linux Test Project test status of errors on man page EINTR v (function was interrupted by a signal) EINVAL v (invalid tv_nsec, etc.) ENOTSUP v (sleep not supported against the specified. The file was read in full for this report (234 lines, 5446 bytes).

Important APIs/types/functions: Primary functions are `sighandler`, `setup`, `do_test`. Important call/API signals are `tst_res`, `SAFE_SIGNAL`, `tst_get_bad_addr`, `create_sig_proc`, `tst_ts_set_sec`, `tst_ts_set_nsec`, `tst_ts_get`, `TEST`, `clock_nanosleep`, `SAFE_KILL`, `SAFE_WAIT`, `tst_ts_to_ms`, `tst_ts_valid`, `tst_strerrno`. Defined constants/macros include `TYPE_NAME`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct time64_variants`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `do_test`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<limits.h>`, `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_sig_proc.h"`, `"tst_timer.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINTR, EINVAL, ENOTSUP, EFAULT, CLOCK_REALTIME, CLOCK_THREAD_CPUTIME_ID`; harness fields `.test, .setup, .tcnt, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (C) 2017 Cyril Hrubis <chrubis@suse.cz> Test Description: clock_nanosleep() should return with value 0 and the process should be suspended for time specified by timespec structure. The file was read in full for this report (37 lines, 727 bytes).

Important APIs/types/functions: Primary functions are `sample_fn`. Important call/API signals are `clock_nanosleep`, `tst_timespec_from_us`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_timer_sample`, `tst_res`. Relevant structs/types include `struct timespec`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around entry/helper functions `sample_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (c) 2020 Cyril Hrubis <chrubis@suse.cz> \ Test that clock_nanosleep() adds correctly an offset with absolute timeout and CLOCK_MONOTONIC inside of a timer namespace. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'. The file was read in full for this report (110 lines, 3099 bytes).

Important APIs/types/functions: Primary functions are `do_clock_gettime`, `verify_clock_nanosleep`. Important call/API signals are `clock_nanosleep`, `do_clock_gettime`, `clock_gettime`, `tst_ts_get`, `tst_brk`, `clock_settime`, `verify_clock_nanosleep`, `tst_res`, `SAFE_UNSHARE`, `SAFE_FILE_PRINTF`, `tst_ts_add_us`, `SAFE_FORK`, `TEST`, `tst_clock_name`, `SAFE_WAIT`, `tst_ts_diff_us`. Defined constants/macros include `OFFSET_S`, `SLEEP_US`. Relevant structs/types include `struct time64_variants`, `struct tst_ts`. Harness metadata uses `.test_all`, `.needs_root`, `.needs_kconfigs`, `.forks_child`.

Control flow: The test is organized around verify-oriented functions `verify_clock_nanosleep`; do_-oriented functions `do_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_MONOTONIC, CLONE_NEWTIME, CLOCK_BOOTTIME`; harness fields `.test_all, .needs_root, .needs_kconfigs, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (c) M. Koehrer <mathias_koehrer@arcor.de>, 2009 Copyright (C) 2017 Cyril Hrubis <chrubis@suse.cz> The file was read in full for this report (67 lines, 1892 bytes).

Important APIs/types/functions: Primary functions are `setup`, `do_test`. Important call/API signals are `tst_res`, `TEST`, `clock_gettime`, `tst_ts_get`, `tst_clock_name`, `tst_ts_add_us`, `clock_nanosleep`. Relevant structs/types include `struct time64_variants`, `struct tst_ts`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `do_test`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<time.h>`, `<unistd.h>`, `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_MONOTONIC, CLOCK_REALTIME`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/Makefile

Purpose: Build integration for the LTP clock_settime syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `LDLIBS+=-lrt`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime01.c

Purpose: LTP regression coverage for `clock_settime` behavior. Source intent: Copyright (c) 2019 Linaro Limited. Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic test for clock_settime(2) on REALTIME clock: 1) advance DELTA_SEC seconds 2) go backwards DELTA_SEC seconds Restore wall clock at the end of test. test 01: move forward test 02: move backward The file was read in full for this report (115 lines, 3244 bytes).

Important APIs/types/functions: Primary functions are `setup`, `do_clock_gettime`, `verify_clock_settime`. Important call/API signals are `clock_settime`, `tst_res`, `do_clock_gettime`, `clock_gettime`, `tst_ts_get`, `tst_brk`, `verify_clock_settime`, `tst_ts_add_us`, `TEST`, `tst_clock_name`, `tst_ts_diff_us`, `tst_ts_sub_us`. Defined constants/macros include `DELTA_SEC`, `DELTA_US`, `DELTA_EPS`. Relevant structs/types include `struct tst_ts`, `struct time64_variants`, `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`, `.needs_root`, `.restore_wallclock`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clock_settime`; do_-oriented functions `do_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_settime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_REALTIME`; harness fields `.test_all, .setup, .needs_root, .restore_wallclock`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime02.c

Purpose: LTP regression coverage for `clock_settime` behavior. Source intent: Copyright (c) 2019 Linaro Limited. Author: Rafael David Tinoco <rafael.tinoco@linaro.org> Basic tests for errors of clock_settime(2) on different clock types. The file was read in full for this report (179 lines, 4499 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_clock_settime`. Important call/API signals are `clock_settime`, `tst_res`, `tst_get_bad_addr`, `tst_get_max_clocks`, `verify_clock_settime`, `TEST`, `clock_gettime`, `tst_ts_get`, `tst_clock_name`, `tst_ts_add_us`, `tst_ts_set_sec`, `tst_ts_set_nsec`, `tst_strerrno`. Defined constants/macros include `DELTA_SEC`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.restore_wallclock`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clock_settime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_settime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EFAULT, EINVAL, CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_PROCESS_CPUTIME_ID, CLOCK_THREAD_CPUTIME_ID, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .needs_root, .restore_wallclock`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime03.c

Purpose: LTP regression coverage for `clock_settime` behavior. Source intent: Copyright (c) 2020 Linaro Limited. Author: Viresh Kumar<viresh.kumar@linaro.org> Check Year 2038 related vulnerabilities. 50 ms Check if the kernel is y2038 safe Time just before y2038 The file was read in full for this report (114 lines, 3159 bytes).

Important APIs/types/functions: Primary functions are `setup`, `run`. Important call/API signals are `tst_res`, `tst_brk`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGPROCMASK`, `TEST`, `tst_syscall`, `timer_create`, `tst_ts_set_sec`, `tst_ts_set_nsec`, `clock_settime`, `tst_ts_get`, `tst_its_set_interval_sec`, `tst_its_set_interval_nsec`, `tst_its_set_value_sec`, `tst_its_set_value_nsec`, `timer_settime`, `tst_its_get`, `SAFE_SIGWAIT`, `clock_gettime`, `tst_ts_diff_ms`. Defined constants/macros include `TIMER_DELTA`, `ALLOWED_DELTA`. Relevant structs/types include `struct tst_ts`, `struct tst_its`, `struct time64_variants`, `struct sigevent`. Harness metadata uses `.test_all`, `.setup`, `.needs_root`, `.restore_wallclock`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<signal.h>`, `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_settime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_REALTIME`; harness fields `.test_all, .setup, .needs_root, .restore_wallclock`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c

Purpose: LTP regression coverage for `clock_settime` behavior. Source intent: Copyright (c) 2025 Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that changing the value of the CLOCK_REALTIME clock via clock_settime() shall have no effect on a thread that is blocked on absolute/relative clock_nanosleep(). The file was read in full for this report (137 lines, 3340 bytes).

Important APIs/types/functions: Primary functions are `child_nanosleep`, `run`, `setup`. Important call/API signals are `clock_settime`, `clock_nanosleep`, `SAFE_CLOCK_GETTIME`, `tst_res`, `tst_ts_set_sec`, `tst_ts_set_nsec`, `tst_ts_add_us`, `tst_ts_from_us`, `TEST`, `tst_ts_get`, `tst_brk`, `tst_timespec_lt`, `tst_timespec_to_ms`, `tst_timespec_abs_diff_us`, `SAFE_FORK`, `SAFE_CLOCK_NANOSLEEP`, `SAFE_CLOCK_SETTIME`. Defined constants/macros include `SEC_TO_US`, `CHILD_SLEEP_US`, `PARENT_SLEEP_S`, `DELTA_US`. Relevant structs/types include `struct tst_ts`, `struct time64_variants`, `struct timespec`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.forks_child`, `.restore_wallclock`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child_nanosleep`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`, `"time64_variants.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_settime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_REALTIME, CLOCK_MONOTONIC`; harness fields `.test, .setup, .tcnt, .needs_root, .forks_child, .restore_wallclock`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/Makefile

Purpose: Build integration for the LTP clone syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `CFLAGS += -Wl,-z,now`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/clone`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone01.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Basic clone() test. Use clone() to create a child process, and wait for the child process to exit, verify that the child process pid is correct. The file was read in full for this report (54 lines, 1194 bytes).

Important APIs/types/functions: Primary functions are `do_child`, `verify_clone`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `SAFE_WAIT`, `tst_res`, `WEXITSTATUS`, `tst_strstatus`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`, `.forks_child`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. The file was read in full for this report (465 lines, 10536 bytes).

Important APIs/types/functions: Primary functions are `setup`, `test_setup`, `cleanup`, `test_cleanup`, `child_fn`, `parent_test1`, `parent_test2`, `test_VM`, `test_FS`, `test_FILES`, `test_SIG`, `modified_VM`, `modified_FS`, `modified_FILES`, `modified_SIG`, `sig_child_defined_handler`, `sig_default_handler`, `main`. Important call/API signals are `clone`, `tst_parse_opts`, `tst_brkm`, `TEST_LOOPING`, `tst_resm`, `TEST`, `ltp_clone`, `wait`, `WEXITSTATUS`, `tst_exit`, `tst_sig`, `tst_tmpdir`, `syscall`, `tst_rmdir`, `open`, `SAFE_CHDIR`, `close`, `tst_get_tmpdir`, `read`. Defined constants/macros include `_GNU_SOURCE`, `FLAG_ALL`, `FLAG_NONE`, `PARENT_VALUE`, `CHILD_VALUE`, `TRUE`, `FALSE`. Relevant structs/types include `struct test_case_t`, `struct sigaction`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around setup-oriented functions `setup, test_setup`; test-oriented functions `test_setup, test_cleanup, parent_test1, parent_test2, test_VM, test_FS`; cleanup-oriented functions `cleanup, test_cleanup`; child-oriented functions `child_fn, sig_child_defined_handler`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<fcntl.h>`, `<sys/wait.h>`, `<sys/types.h>`, `<sys/syscall.h>`, `<sched.h>`, `"test.h"`, `"tso_safe_macros.h"`, `"tst_clone.h"`, `"clone_platform.h"`; legacy LTP harness APIs. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, CLONE_VM, CLONE_FS, CLONE_FILES, CLONE_SIGHAND, O_CREAT, O_RDWR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Check for equality of getpid() from a child and return value of clone(2) The file was read in full for this report (60 lines, 1158 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`, `setup`, `cleanup`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `tst_reap_children`, `TST_EXP_VAL`, `SAFE_MMAP`, `SAFE_MUNMAP`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clone`; cleanup-oriented functions `cleanup`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> Copyright (c) Linux Test Project, 2003-2023 \ Verify that clone(2) fails with - EINVAL if child stack is set to NULL The file was read in full for this report (51 lines, 1047 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_FAIL`, `ltp_clone`. Relevant structs/types include `struct tcase`, `struct tst_tag`. Harness metadata uses `.test`, `.tcnt`, `.tags`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL`; harness fields `.test, .tcnt, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> Copyright (c) 2012 Cyril Hrubis <chrubis@suse.cz> \ Call clone() with CLONE_VFORK flag set. verify that execution of parent is suspended until child finishes The file was read in full for this report (56 lines, 1095 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `TST_EXP_VAL`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sched.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: case/errno constants `CLONE_VFORK, CLONE_VM`; harness fields `.test_all`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone06.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Test to verify inheritance of environment variables by child. The file was read in full for this report (65 lines, 1298 bytes).

Important APIs/types/functions: Primary functions are `child_environ`, `verify_clone`, `setup`. Important call/API signals are `tst_res`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `tst_reap_children`, `SAFE_SETENV`. Defined constants/macros include `MAX_LINE_LENGTH`, `ENV_VAL`, `ENV_ID`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clone`; child-oriented functions `child_environ`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<sched.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) International Business Machines Corp., 2003. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Test for a libc bug where exiting child function by returning from it caused SIGSEGV. The file was read in full for this report (59 lines, 1228 bytes).

Important APIs/types/functions: Primary functions are `do_child`, `verify_clone`. Important call/API signals are `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_res`, `tst_strstatus`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sched.h>`, `<stdio.h>`, `<stdlib.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone08.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2017 Oracle and/or its affiliates. Copyright (c) 2013 Fujitsu Ltd. Author: Zeng Linggang <zenglg.jy@cn.fujitsu.com> Children cloned with CLONE_VM should avoid using any functions that might require dl_runtime_resolve, because they share thread-local storage with parent. The file was read in full for this report (193 lines, 4654 bytes).

Important APIs/types/functions: Primary functions are `test_clone_parent`, `child_clone_parent`, `test_clone_tid`, `child_clone_child_settid`, `child_clone_parent_settid`, `test_clone_thread`, `child_clone_thread`, `do_test`, `setup`, `cleanup`, `clone_child`. Important call/API signals are `test_clone_parent`, `child_clone_parent`, `test_clone_tid`, `child_clone_child_settid`, `child_clone_parent_settid`, `test_clone_thread`, `child_clone_thread`, `tst_res`, `SAFE_MALLOC`, `clone_child`, `TEST`, `ltp_clone7`, `tst_brk`, `clone`, `SAFE_FORK`, `tst_reap_children`, `tst_syscall`, `syscall`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct test_case`, `struct timespec`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `test_clone_parent, test_clone_tid, test_clone_thread, do_test`; cleanup-oriented functions `cleanup`; child-oriented functions `child_clone_parent, child_clone_child_settid, child_clone_parent_settid, child_clone_thread, clone_child`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<stdio.h>`, `<errno.h>`, `<sched.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"clone_platform.h"`, `"lapi/syscalls.h"`, `"lapi/futex.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ENOSYS, EWOULDBLOCK, CLONE_VM, CLONE_PARENT, CLONE_CHILD_SETTID, CLONE_PARENT_SETTID, CLONE_THREAD, CLONE_SIGHAND, CLONE_CHILD_CLEARTID`; harness fields `.test, .setup, .cleanup, .tcnt, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone09.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2017 Oracle and/or its affiliates. The file was read in full for this report (91 lines, 2025 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `newnet`, `clone_child`, `do_test`. Important call/API signals are `SAFE_MALLOC`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `tst_syscall`, `clone_child`, `TEST`, `ltp_clone`, `tst_brk`, `clone`, `tst_res`, `tst_reap_children`. Defined constants/macros include `_GNU_SOURCE`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `do_test`; cleanup-oriented functions `cleanup`; child-oriented functions `clone_child`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<errno.h>`, `"tst_test.h"`, `"clone_platform.h"`, `"lapi/syscalls.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, CLONE_NEWNET, CLONE_VM`; harness fields `.test_all, .setup, .cleanup, .needs_root`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2025 Red Hat Inc. Author: Chunfu Wen <chwen@redhat.com> \ Test that in a thread started by clone() that runs in the same address space (CLONE_VM) but with a different TLS (CLONE_SETTLS) writtes to a thread local variables are not propagated back from the cloned thread. The file was read in full for this report (99 lines, 2080 bytes).

Important APIs/types/functions: Primary functions are `touch_tls_in_child`, `verify_tls`, `setup`, `cleanup`. Important call/API signals are `clone`, `tst_atomic_store`, `tst_syscall`, `TEST`, `ltp_clone7`, `tst_brk`, `tst_atomic_load`, `tst_res`, `syscall`, `SAFE_MALLOC`. Defined constants/macros include `_GNU_SOURCE`, `TLS_EXP`, `ARCH_SET_FS`. Relevant structs/types include `struct user_desc`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_tls`; cleanup-oriented functions `cleanup`; child-oriented functions `touch_tls_in_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<stdio.h>`, `<errno.h>`, `<sched.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"clone_platform.h"`, `"lapi/syscalls.h"`, `"tst_atomic.h"`, `"lapi/tls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_VM, CLONE_SETTLS, CLONE_THREAD, CLONE_FS, CLONE_FILES, CLONE_SIGHAND`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2025 Stephen Bertram <sbertram@redhat.com> \ This test verifies that :manpage:`clone(2)` fails with EPERM when CAP_SYS_ADMIN has been dropped. The file was read in full for this report (81 lines, 1560 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `run`, `setup`, `cleanup`. Important call/API signals are `clone`, `TST_EXP_FAIL`, `ltp_clone`, `SAFE_MMAP`, `SAFE_MUNMAP`, `TST_CAP`. Defined constants/macros include `_GNU_SOURCE`, `DESC`. Relevant structs/types include `struct tcase`, `struct tst_cap`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"clone_platform.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLONE_NEWPID, CLONE_NEWCGROUP, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone_platform.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone_platform.h

Purpose: Shared helper/header support for the LTP clone tests. Source intent: Copyright (c) 2003 Silicon Graphics, Inc. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. Common platform specific defines for the clone system call tests The file was read in full for this report (21 lines, 817 bytes).

Important APIs/types/functions: Defined constants/macros include `CHILD_STACK_SIZE`. The file has little or no explicit LTP harness metadata.

Control flow: Control flow is mostly declarative or macro-driven. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on the local LTP syscall test build environment. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/Makefile

Purpose: Build integration for the LTP clone3 syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/clone3`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> \ Basic clone3() test. The file was read in full for this report (188 lines, 3825 bytes).

Important APIs/types/functions: Primary functions are `parent_rx_signal`, `child_rx_signal`, `do_child`, `run`, `setup`. Important call/API signals are `clone3`, `SAFE_SIGACTION`, `TST_CHECKPOINT_WAKE`, `tst_res`, `tst_strsig`, `TEST`, `ltp_clone3_raw`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `clone3_supported_by_kernel`. Defined constants/macros include `_GNU_SOURCE`, `CHILD_SIGNAL`, `DATA`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct sigaction`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_checkpoints`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child_rx_signal, do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/sched.h"`, `"lapi/pidfd.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_FS, CLONE_NEWPID, CLONE_PARENT_SETTID, CLONE_CHILD_SETTID, CLONE_PIDFD`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_checkpoints, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> \ Basic clone3() test to check various failures. Don't test CLONE_CHILD_SETTID and CLONE_PARENT_SETTID: When the parent tid is written to the memory location for CLONE_PARENT_SETTID we're past the point of no return of process creation, i.e. The file was read in full for this report (115 lines, 3329 bytes).

Important APIs/types/functions: Primary functions are `setup`, `run`. Important call/API signals are `clone3`, `clone3_supported_by_kernel`, `TST_EXP_EQ_SZ`, `tst_get_bad_addr`, `TEST`, `ltp_clone3_raw`, `tst_res`, `tst_strerrno`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct clone_args_minimal`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<assert.h>`, `"tst_test.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; an isolated LTP temporary directory. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EFAULT, EINVAL, CLONE_SIGHAND, CLONE_THREAD, CLONE_FS, CLONE_NEWNS, CLONE_PIDFD, CLONE_CHILD_SETTID, CLONE_PARENT_SETTID`; harness fields `.test, .setup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2023 SUSE LLC <wegao@suse.com> \ This test case check clone3 CLONE_INTO_CGROUP flag The file was read in full for this report (93 lines, 1660 bytes).

Important APIs/types/functions: Primary functions are `clone_into_cgroup`, `run`, `setup`, `cleanup`. Important call/API signals are `clone_into_cgroup`, `tst_clone`, `TST_CHECKPOINT_WAIT`, `SAFE_CG_READ`, `tst_res`, `tst_brk`, `clone3`, `TST_CHECKPOINT_WAKE`, `SAFE_WAITPID`, `clone3_supported_by_kernel`, `tst_cg_group_mk`, `tst_cg_group_unified_dir_fd`, `tst_cg_group_rm`. Defined constants/macros include `_GNU_SOURCE`, `BUF_LEN`. Relevant structs/types include `struct tst_cg_group`, `struct tst_clone_args`, `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`, `.min_kver`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/sched.h"`, `"lapi/pidfd.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_INTO_CGROUP`; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child, .min_kver`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2025 Stephen Bertram <sbertram@redhat.com> \ This test verifies that :manpage:`clone3(2)` fails with EPERM when CAP_SYS_ADMIN has been dropped and ``clone_args.set_tid_size`` is greater than zero. flags = 0 || CLONE_NEW*, set_tid_size > 0 => EPERM flags = CLONE_NEW*, set_tid_size = 0 => EPERM The file was read in full for this report (93 lines, 2132 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`. Important call/API signals are `clone3`, `TST_EXP_FAIL`, `ltp_clone3_raw`, `clone3_supported_by_kernel`, `SAFE_UNSHARE`, `TST_CAP`. Defined constants/macros include `_GNU_SOURCE`, `DESC`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct tst_cap`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLONE_NEW, CLONE_NEWPID, CLONE_NEWCGROUP, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS, CLONE_NEWUSER`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close/Makefile

Purpose: Build integration for the LTP close syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/close`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close/close01.c

Purpose: LTP regression coverage for `close` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer \ Test that closing a file/pipe/socket works correctly. The file was read in full for this report (54 lines, 940 bytes).

Important APIs/types/functions: Primary functions are `get_fd_file`, `get_fd_pipe`, `get_fd_socket`, `run`. Important call/API signals are `SAFE_OPEN`, `get_fd_pipe`, `SAFE_PIPE`, `SAFE_CLOSE`, `get_fd_socket`, `SAFE_SOCKET`, `TST_EXP_PASS`, `close`. Defined constants/macros include `FILENAME`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `close` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; case/errno constants `O_RDWR, O_CREAT`; harness fields `.test, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c

Purpose: LTP regression coverage for `close` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer \ Verify :manpage:`close(2)` failure cases: 1) close(-1) returns EBADF. 2) closing the same fd twice returns EBADF on the second call. The file was read in full for this report (51 lines, 1031 bytes).

Important APIs/types/functions: Primary functions are `verify_close`, `setup`. Important call/API signals are `close`, `verify_close`, `TST_EXP_FAIL`, `SAFE_OPEN`, `tst_brk`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_close`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `close` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, O_CREAT, O_RDWR`; harness fields `.test, .setup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close_range/Makefile

Purpose: Build integration for the LTP close_range syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `CFLAGS			+= -D_GNU_SOURCE`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/close_range`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c

Purpose: LTP regression coverage for `close_range` behavior. Source intent: Taken from the kernel self tests, which in turn were based on a Syzkaller reproducer. Self test author and close_range author: Christian Brauner <christian.brauner@ubuntu.com> LTP Author: Richard Palethorpe <rpalethorpe@suse.com> Copyright (c) 2021 SUSE LLC, other copyrights may apply. The file was read in full for this report (211 lines, 4261 bytes).

Important APIs/types/functions: Primary functions are `do_close_range`, `setup`, `check_cloexec`, `check_closed`, `child`, `run`. Important call/API signals are `close_range`, `do_close_range`, `tst_brk`, `close_range_supported_by_kernel`, `SAFE_GETRLIMIT`, `SAFE_SETRLIMIT`, `SAFE_FCNTL`, `tst_res`, `check_closed`, `fcntl`, `SAFE_DUP2`, `SAFE_OPEN`, `SAFE_CLONE`, `tst_reap_children`, `tst_taint_check`, `TST_CAP`. Relevant structs/types include `struct rlimit`, `struct tst_clone_args`, `struct tst_cap`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.tags`, `.forks_child`, `.taint_check`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child`; do_-oriented functions `do_close_range`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"tst_clone.h"`, `"lapi/sched.h"`, `"lapi/close_range.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `close_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: descriptor ranges can accidentally close harness fds if setup bounds are wrong

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, CLOSE_RANGE_UNSHARE, CLOSE_RANGE_CLOEXEC, F_GETFD, FD_CLOEXEC, CLONE_FILES, O_RDWR, O_CREAT`; harness fields `.test, .setup, .tcnt, .needs_root, .tags, .forks_child, .taint_check`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c

Purpose: LTP regression coverage for `close_range` behavior. Source intent: Copyright (c) 2021 SUSE LLC \ - First check close_range works on a valid range. - Then check close_range does not accept invalid paramters. - Then check it accepts a large lower fd. - Finally check CLOEXEC works The file was read in full for this report (114 lines, 2355 bytes).

Important APIs/types/functions: Primary functions are `try_close_range`, `run`. Important call/API signals are `try_close_range`, `TEST`, `close_range`, `SAFE_OPEN`, `SAFE_DUP2`, `TST_EXP_PASS`, `TST_EXP_FAIL`, `fcntl`, `tst_res`, `TST_EXP_FD_SILENT`, `SAFE_CLONE`, `tst_reap_children`, `TST_EXP_PASS_SILENT`. Relevant structs/types include `struct tst_clone_args`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"tst_clone.h"`, `"lapi/fcntl.h"`, `"lapi/close_range.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `close_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: descriptor ranges can accidentally close harness fds if setup bounds are wrong

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EBADF, CLONE_FILES, O_PATH, F_GETFD, CLOSE_RANGE_CLOEXEC, FD_CLOEXEC, CLOSE_RANGE_UNSHARE`; harness fields `.test, .setup, .tcnt, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/Makefile

Purpose: Build integration for the LTP cma syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/cma`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c

Purpose: LTP regression coverage for `process_vm_readv/process_vm_writev` behavior. Source intent: Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Test errno codes in process_vm_readv and process_vm_writev syscalls. only flags == 0 is allowed, everything else should fail with EINVAL collect result from child before the next test, otherwise TFAIL/TPASS messages will arrive asynchronously The file was read in full for this report (312 lines, 7011 bytes).

Important APIs/types/functions: Primary functions are `free_params`, `test_readv`, `test_writev`, `check_errno`, `test_sane_params`, `test_flags`, `test_iov_len_overflow`, `test_iov_invalid`, `test_invalid_pid`, `test_invalid_perm`, `test_invalid_protection`, `run`, `setup`. Important call/API signals are `SAFE_MALLOC`, `test_readv`, `TEST`, `tst_syscall`, `test_writev`, `tst_res`, `TST_EXP_EQ_LI`, `tst_get_unused_pid`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETUID`, `tst_reap_children`, `SAFE_MMAP`, `SAFE_MUNMAP`. Relevant structs/types include `struct process_vm_params`, `struct iovec`, `struct passwd`, `struct tst_option`. Harness metadata uses `.test_all`, `.setup`, `.needs_root`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `test_readv, test_writev, test_sane_params, test_flags, test_iov_len_overflow, test_iov_invalid`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, process address-space and iovec buffers, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<pwd.h>`, `<stdlib.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EFAULT, ESRCH, EPERM`; harness fields `.test_all, .setup, .needs_root, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv02.c

Purpose: LTP regression coverage for `process_vm_readv` behavior. Source intent: Copyright (c) International Business Machines Corp., 2012 Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Fork two children, one child allocates memory and initializes it; then the other one calls process_vm_readv and reads from the same memory location, it then verifies if process_vm_readv returns correct data. The file was read in full for this report (122 lines, 2887 bytes).

Important APIs/types/functions: Primary functions are `child_alloc`, `child_invoke`, `setup`, `cleanup`, `run`. Important call/API signals are `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `SAFE_MALLOC`, `TEST`, `tst_syscall`, `tst_brk`, `tst_strerrno`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_strstatus`, `TST_CHECKPOINT_WAKE`. Relevant structs/types include `struct iovec`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_alloc, child_invoke`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, process address-space and iovec buffers. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<sys/types.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c

Purpose: LTP regression coverage for `process_vm_readv` behavior. Source intent: Copyright (c) International Business Machines Corp., 2012 Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Fork two children, one child mallocs randomly sized trunks of memory and initializes them; the other child calls process_vm_readv with the remote iovecs initialized to the original process memory locations and the local iovecs initialized to. The file was read in full for this report (196 lines, 5259 bytes).

Important APIs/types/functions: Primary functions are `create_data_size`, `child_alloc`, `child_read`, `setup`, `cleanup`, `run`. Important call/API signals are `create_data_size`, `SAFE_MALLOC`, `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `child_read`, `TST_EXP_POSITIVE`, `tst_syscall`, `process_vm_read`, `tst_brk`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_strstatus`, `TST_CHECKPOINT_WAKE`. Defined constants/macros include `MAX_IOVECS`. Relevant structs/types include `struct tcase`, `struct iovec`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_alloc, child_read`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, process address-space and iovec buffers. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<sys/types.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .setup, .cleanup, .tcnt, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c

Purpose: LTP regression coverage for `process_vm_writev` behavior. Source intent: Copyright (c) International Business Machines Corp., 2012 Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Fork two children, the first one allocates a chunk of memory and the other one call process_vm_writev to write known data into the first child. The file was read in full for this report (127 lines, 2799 bytes).

Important APIs/types/functions: Primary functions are `child_alloc_and_verify`, `child_write`, `setup`, `cleanup`, `run`. Important call/API signals are `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `child_write`, `TST_EXP_POSITIVE`, `tst_syscall`, `tst_brk`, `tst_parse_int`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_strstatus`, `TST_CHECKPOINT_WAKE`. Relevant structs/types include `struct iovec`, `struct tst_option`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `child_alloc_and_verify`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_alloc_and_verify, child_write`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, process address-space and iovec buffers. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<sys/uio.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/confstr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/confstr/Makefile

Purpose: Build integration for the LTP confstr syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/confstr`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/confstr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/confstr/confstr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/confstr/confstr01.c

Purpose: LTP regression coverage for `confstr` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 11/20/2002 Port to LTP <robbiew@us.ibm.com> 06/30/2001 Port to Linux <nsharoff@us.ibm.com> Copyright (C) 2022 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> Copyright (c) 2022 Petr Vorel <pvorel@suse.cz> \ Test confstr(3) 700 (X/Open 7) functionality -- POSIX 2008. The file was read in full for this report (83 lines, 1875 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_POSITIVE`, `SAFE_MALLOC`, `TEST`, `tst_brk`, `tst_strerrno`, `tst_res`. Defined constants/macros include `_XOPEN_SOURCE`, `PAIR`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test keeps state local to automatic variables and LTP harness bookkeeping. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<unistd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `confstr` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/confstr/confstr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/connect/Makefile

Purpose: Build integration for the LTP connect syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/connect`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c

Purpose: LTP regression coverage for `connect` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. The file was read in full for this report (309 lines, 7710 bytes).

Important APIs/types/functions: Primary functions are `setup`, `start_server`, `sys_connect`, `main`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `do_child`. Important call/API signals are `connect`, `sys_connect`, `tst_syscall`, `tst_parse_opts`, `TEST_LOOPING`, `TEST`, `tst_resm`, `tst_exit`, `TST_GET_UNUSED_PORT`, `open`, `tst_brkm`, `close`, `SAFE_SOCKET`, `SAFE_CONNECT`, `socket`, `bind`, `listen`, `SAFE_GETSOCKNAME`, `tst_fork`, `accept`, `read`. Defined constants/macros include `connect`. Relevant structs/types include `struct sockaddr_in`, `struct test_case_t`, `struct sockaddr`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around setup-oriented functions `setup, setup0, setup1, setup2`; cleanup-oriented functions `cleanup, cleanup0, cleanup1`; child-oriented functions `do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<fcntl.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<sys/signal.h>`, `<sys/un.h>`, `<netinet/in.h>`, `"test.h"`; legacy LTP harness APIs; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `connect` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EFAULT, EINVAL, ENOTSOCK, EISCONN, ECONNREFUSED, EAFNOSUPPORT, EINTR, O_WRONLY`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c

Purpose: LTP regression coverage for `connect` behavior. Source intent: Copyright (C) 2017 Christoph Paasch <cpaasch@apple.com> Copyright (C) 2020 SUSE LLC <mdoucha@suse.cz> CVE-2018-9568 Test that connect() to AF_UNSPEC address correctly converts IPV6 socket to IPV4 listen socket when IPV6_ADDRFORM is set to AF_INET. Kernel memory corruption fixed in: commit 9d538fa60bad4f7b23193c89e843797a1cf71ef3 Author: Christoph Paasch <cpaasch@apple.com> Date: Tue Sep 26 17:38:50 2017 -0700 net:. The file was read in full for this report (141 lines, 3617 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `connect`, `tst_init_sockaddr_inet6_bin`, `tst_init_sockaddr_inet_bin`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_GETSOCKNAME`, `tst_init_sockaddr_inet`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_ACCEPT`, `TEST`, `tst_res`, `tst_brk`, `tst_get_connect_address`, `tst_taint_check`. Relevant structs/types include `struct sockaddr_in6`, `struct sockaddr_in`, `struct sockaddr`, `struct sockaddr_storage`, `struct tst_tag`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.tags`, `.taint_check`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/socket.h>`, `<netinet/in.h>`, `<netinet/tcp.h>`, `<arpa/inet.h>`, `"tst_test.h"`, `"tst_net.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `connect` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .tags, .taint_check`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/Makefile

Purpose: Build integration for the LTP copy_file_range syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h

Purpose: Shared helper/header support for the LTP copy_file_range tests. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Writing page_size * 4 of data into test file __COPY_FILE_RANGE_H__ else The file was read in full for this report (83 lines, 2035 bytes).

Important APIs/types/functions: Primary functions are `syscall_info`, `sys_copy_file_range`, `verify_cross_fs_copy_support`. Important call/API signals are `syscall_info`, `tst_res`, `copy_file_range`, `sys_copy_file_range`, `tst_brk`, `tst_syscall`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`, `SAFE_CLOSE`. Defined constants/macros include `__COPY_FILE_RANGE_H__`, `TEST_VARIANTS`, `MNTPOINT`, `FILE_SRC_PATH`, `FILE_DEST_PATH`, `FILE_RDONL_PATH`, `FILE_DIR_PATH`, `FILE_MNTED_PATH`, `FILE_IMMUTABLE_PATH`, `FILE_SWAP_PATH`, `FILE_CHRDEV`, `FILE_FIFO`, `FILE_COPY_PATH`, `CONTENT`, `CONTSIZE`, `MIN_OFF`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around verify-oriented functions `verify_cross_fs_copy_support`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `"lapi/syscalls.h"`, `"lapi/fs.h"`; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: case/errno constants `EXDEV, O_RDWR, O_CREAT`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) Linux Test Project, 2019 This tests the fundamental functionalities of the copy_file_range syscall. It does so by copying the contents of one file into another using various different combinations for length and input/output offsets. After a copy is done this test checks if the contents of both files are equal at the given offsets. The file was read in full for this report (237 lines, 5511 bytes).

Important APIs/types/functions: Primary functions are `check_file_content`, `check_file_offset`, `test_one`, `open_files`, `close_files`, `copy_file_range_verify`, `setup`, `cleanup`. Important call/API signals are `SAFE_FOPEN`, `tst_brk`, `SAFE_FCLOSE`, `SAFE_LSEEK`, `tst_res`, `copy_file_range`, `TEST`, `sys_copy_file_range`, `open_files`, `SAFE_OPEN`, `close_files`, `SAFE_CLOSE`, `copy_file_range_verify`, `syscall_info`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `copy_file_range_verify`; test-oriented functions `test_one`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_safe_stdio.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDONLY, O_CREAT, O_WRONLY, O_TRUNC`; harness fields `.test, .setup, .cleanup, .tcnt`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Tests basic error handling of the copy_file_range syscall 1) Try to copy contents to file open as readonly -> EBADF 2) Try to copy contents to directory -> EISDIR 3) Try to copy contents to a file opened with the O_APPEND flag -> EBADF 4) Try to copy contents to closed file descriptor -> EBADF 5) Try to copy contents with invalid 'flags' value ->. The file was read in full for this report (257 lines, 6991 bytes).

Important APIs/types/functions: Primary functions are `run_command`, `verify_copy_file_range`, `cleanup`, `setup`. Important call/API signals are `tst_cmd`, `tst_res`, `verify_copy_file_range`, `copy_file_range`, `tst_max_lfs_filesize`, `TEST`, `sys_copy_file_range`, `tst_strerrno`, `SAFE_CLOSE`, `SAFE_UNLINK`, `syscall_info`, `SAFE_MKDIR`, `tst_find_free_loopdev`, `SAFE_MKNOD`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`, `close`, `tst_fs_has_free`, `tst_fill_file`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_copy_file_range`; run-oriented functions `run_command`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EISDIR, EINVAL, EPERM, ETXTBSY, EOVERFLOW, EFBIG, O_APPEND, F_OK, O_RDWR, O_CREAT, O_RDONLY, O_DIRECTORY, O_WRONLY, O_TRUNC`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Copies the contents of one file into another and checks if the timestamp gets updated in the process. The file was read in full for this report (82 lines, 1759 bytes).

Important APIs/types/functions: Primary functions are `verify_copy_file_range_timestamp`, `cleanup`, `setup`. Important call/API signals are `fstat`, `verify_copy_file_range_timestamp`, `TEST`, `sys_copy_file_range`, `tst_brk`, `tst_timespec_diff_us`, `tst_res`, `SAFE_CLOSE`, `syscall_info`, `SAFE_OPEN`, `SAFE_WRITE`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct timespec`, `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_copy_file_range_timestamp`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDWR, O_CREAT, O_RDONLY`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/Makefile

Purpose: Build integration for the LTP creat syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `FILTER_OUT_MAKE_TARGETS	+= creat05`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/creat`. Target signals: FILTER_OUT_MAKE_TARGETS	+= creat05.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ 1. The file was read in full for this report (77 lines, 1467 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_creat`, `cleanup`. Important call/API signals are `creat`, `verify_creat`, `SAFE_CREAT`, `SAFE_STAT`, `tst_res`, `write`, `read`, `SAFE_CLOSE`. Relevant structs/types include `struct tcase`, `struct stat`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<stdio.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .setup, .cleanup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat03.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Testcase to check whether the sticky bit cleared. The file was read in full for this report (63 lines, 1134 bytes).

Important APIs/types/functions: Primary functions are `verify_creat`, `setup`, `cleanup`. Important call/API signals are `creat`, `verify_creat`, `tst_res`, `SAFE_FSTAT`, `SAFE_CLOSE`. Relevant structs/types include `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<stdio.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check :manpage:`creat(2)` fails with EACCES. The file was read in full for this report (79 lines, 1349 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_creat`, `setup`. Important call/API signals are `creat`, `SAFE_SETEUID`, `TEST`, `SAFE_UNLINK`, `tst_res`, `verify_creat`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_CLOSE`. Defined constants/macros include `DIRNAME`, `FILENAME`. Relevant structs/types include `struct tcase`, `struct passwd`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_tmpdir`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<errno.h>`, `<fcntl.h>`, `<pwd.h>`, `<sys/types.h>`, `<sys/stat.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EACCES, O_RDWR, O_CREAT`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_tmpdir, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check that :manpage:`creat(2)` system call returns EMFILE. The file was read in full for this report (83 lines, 1688 bytes).

Important APIs/types/functions: Primary functions are `verify_creat`, `setup`, `cleanup`. Important call/API signals are `creat`, `verify_creat`, `TEST`, `tst_res`, `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_CREAT`, `close`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `<sys/types.h>`, `<sys/time.h>`, `<sys/resource.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<linux/limits.h>`, `<unistd.h>`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EMFILE`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) Linux Test Project, 2014-2026 Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check that :manpage:`creat(2)` sets the following errnos correctly: 1. ENAMETOOLONG -- Attempt to :manpage:`creat(2)` a file whose name is more than VFS_MAXNAMLEN and test for ENAMETOOLONG. The file was read in full for this report (140 lines, 3393 bytes).

Important APIs/types/functions: Primary functions are `setup`, `test6_setup`, `test6_cleanup`, `bad_addr_setup`, `verify_creat`. Important call/API signals are `creat`, `verify_creat`, `TEST`, `tst_res`, `tst_strerrno`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_MMAP`, `SAFE_SETEUID`. Defined constants/macros include `TEST_FILE`, `NO_DIR`, `NOT_DIR`, `TEST6_FILE`, `TEST7_FILE`, `TEST8_FILE`, `MODE1`, `MODE2`. Relevant structs/types include `struct passwd`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup, test6_setup, bad_addr_setup`; verify-oriented functions `verify_creat`; test-oriented functions `test6_setup, test6_cleanup`; cleanup-oriented functions `test6_cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<string.h>`, `<limits.h>`, `<pwd.h>`, `<sys/mman.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<sys/mount.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EISDIR, ENAMETOOLONG, ENOENT, ENOTDIR, EFAULT, EACCES, ELOOP, EROFS`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2012-2016 Cyril Hrubis <chrubis@suse.cz> \ Check that :manpage:`creat(2)` sets ETXTBSY correctly. The file was read in full for this report (69 lines, 1338 bytes).

Important APIs/types/functions: Primary functions are `verify_creat`, `setup`. Important call/API signals are `creat`, `verify_creat`, `SAFE_FORK`, `SAFE_EXECL`, `TST_CHECKPOINT_WAIT`, `TEST`, `tst_res`, `SAFE_KILL`, `SAFE_WAITPID`, `tst_kvercmp`, `tst_brk`. Defined constants/macros include `TEST_APP`. Harness metadata uses `.test_all`, `.setup`, `.needs_checkpoints`, `.resource_files`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/stat.h>`, `<sys/wait.h>`, `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ETXTBSY, EXTBSY, O_WRONLY`; harness fields `.test_all, .setup, .needs_checkpoints, .resource_files, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2012 Cyril Hrubis <chrubis@suse.cz> The file was read in full for this report (21 lines, 321 bytes).

Important APIs/types/functions: Primary functions are `main`. Important call/API signals are `tst_reinit`, `TST_CHECKPOINT_WAKE`. Defined constants/macros include `TST_NO_DEFAULT_MAIN`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around entry/helper functions `main`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test keeps state local to automatic variables and LTP harness bookkeeping. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<unistd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; legacy LTP harness APIs. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE by Airong Zhang <zhanga@us.ibm.com> Copyright (c) 2021 SUSE LLC <mdoucha@suse.cz> \ Verify that the group ID and setgid bit are set correctly when a new file is created with :manpage:`creat(2)`. Create directories and set permissions Switch to user nobody and create two files in DIR_A Both files should inherit GID from the process Create two. The file was read in full for this report (140 lines, 3501 bytes).

Important APIs/types/functions: Primary functions are `setup`, `file_test`, `run`, `cleanup`. Important call/API signals are `creat`, `SAFE_GETPWNAM`, `tst_res`, `tst_get_free_gid`, `SAFE_CREAT`, `SAFE_STAT`, `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_CHOWN`, `tst_brk`, `SAFE_CHMOD`, `SAFE_SETGID`, `SAFE_SETREUID`, `tst_purge_dir`, `tst_tmpdir_path`. Defined constants/macros include `MODE_RWX`, `MODE_SGID`, `DIR_A`, `DIR_B`, `SETGID_A`, `NOSETGID_A`, `SETGID_B`, `NOSETGID_B`, `ROOT_SETGID`. Relevant structs/types include `struct passwd`, `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `file_test`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<pwd.h>`, `"tst_test.h"`, `"tst_uid.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_root, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) 2021 SUSE LLC <mdoucha@suse.cz> \ CVE-2018-13405 Check for possible privilege escalation through creating files with setgid bit set inside a setgid directory owned by a group which the user does not belong to. The file was read in full for this report (145 lines, 3200 bytes).

Important APIs/types/functions: Primary functions are `setup`, `file_test`, `run`, `cleanup`. Important call/API signals are `SAFE_GETPWNAM`, `tst_res`, `tst_get_free_gid`, `SAFE_MKDIR`, `SAFE_CHOWN`, `SAFE_CHMOD`, `SAFE_STAT`, `tst_brk`, `SAFE_SETGID`, `SAFE_SETREUID`, `SAFE_CREAT`, `SAFE_CLOSE`, `SAFE_OPEN`, `tst_purge_dir`. Defined constants/macros include `MODE_RWX`, `MODE_SGID`, `MNTPOINT`, `WORKDIR`, `CREAT_FILE`, `OPEN_FILE`. Relevant structs/types include `struct tcase`, `struct stat`, `struct passwd`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `file_test`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<pwd.h>`, `"tst_test.h"`, `"tst_uid.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_CREAT, O_EXCL, O_RDWR`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile

Purpose: Build integration for the LTP delete_module syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `obj-m := dummy_del_mod.o dummy_del_mod_dep.o`, `top_srcdir		?= ../../../..`, `REQ_VERSION_MAJOR	:= 2`, `REQ_VERSION_PATCH	:= 6`, `MAKE_TARGETS		:= delete_module01 delete_module02 delete_module03 \`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/module.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/delete_module`. Target signals: MAKE_TARGETS		:= delete_module01 delete_module02 delete_module03 \.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module01.c

Purpose: LTP regression coverage for `delete_module` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> Copyright (c) Linux Test Project, 2002-2023 Author: Madhu T L <madhu.tarikere@wipro.com> \ Basic test for delete_module(2). Install dummy_del_mod.ko and delete it with delete_module(2). The file was read in full for this report (60 lines, 1320 bytes).

Important APIs/types/functions: Primary functions are `do_delete_module`, `cleanup`. Important call/API signals are `delete_module`, `do_delete_module`, `tst_requires_module_signature_disabled`, `tst_module_load`, `TEST`, `tst_syscall`, `tst_res`, `tst_module_unload`. Defined constants/macros include `MODULE_NAME`, `MODULE_NAME_KO`. Harness metadata uses `.test_all`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around cleanup-oriented functions `cleanup`; do_-oriented functions `do_delete_module`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates loadable kernel module state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"tst_module.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .cleanup, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c

Purpose: LTP regression coverage for `delete_module` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> AUTHOR: Madhu T L <madhu.tarikere@wipro.com> DESCRIPTION Verify that, 1. delete_module(2) returns -1 and sets errno to ENOENT for nonexistent module entry. delete_module(2) returns -1 and sets errno to EFAULT, if module name parameter is outside program's accessible address space. The file was read in full for this report (97 lines, 2524 bytes).

Important APIs/types/functions: Primary functions are `do_delete_module`, `setup`. Important call/API signals are `delete_module`, `do_delete_module`, `tst_get_bad_addr`, `SAFE_SETEUID`, `tst_res`, `TEST`, `tst_syscall`, `tst_strerrno`, `SAFE_GETPWNAM`. Defined constants/macros include `BASEMODNAME`, `LONGMODNAMECHAR`, `MODULE_NAME_LEN`. Relevant structs/types include `struct passwd`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; do_-oriented functions `do_delete_module`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, loadable kernel module state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<pwd.h>`, `<stdio.h>`, `<string.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ENOENT, EFAULT, EPERM`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c

Purpose: LTP regression coverage for `delete_module` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> AUTHOR: Madhu T L <madhu.tarikere@wipro.com> DESCRIPTION Verify that, delete_module(2) returns -1 and sets errno to EWOULDBLOCK, if tried to remove a module while other modules depend on this module. The file was read in full for this report (85 lines, 2029 bytes).

Important APIs/types/functions: Primary functions are `do_delete_module`, `setup`, `cleanup`. Important call/API signals are `delete_module`, `do_delete_module`, `TEST`, `tst_syscall`, `tst_res`, `tst_strerrno`, `tst_module_load`, `tst_requires_module_signature_disabled`, `tst_module_unload`. Defined constants/macros include `DUMMY_MOD`, `DUMMY_MOD_KO`, `DUMMY_MOD_DEP_KO`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; cleanup-oriented functions `cleanup`; do_-oriented functions `do_delete_module`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates loadable kernel module state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<errno.h>`, `"tst_test.h"`, `"tst_module.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EWOULDBLOCK`; harness fields `.test_all, .setup, .cleanup, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod.c

Purpose: Loadable kernel module fixture used by delete_module syscall tests. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> Description: This is a kernel loadable module programme used by delete_module* testcases which insert this module as part setup. Dummy function called by dependent module The file was read in full for this report (42 lines, 855 bytes).

Important APIs/types/functions: Primary functions are `dummy_func_test`. Important call/API signals are `module_init`, `module_exit`. Defined constants/macros include `DIRNAME`. Relevant structs/types include `struct proc_dir_entry`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around test-oriented functions `dummy_func_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates loadable kernel module state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<linux/module.h>`, `<linux/init.h>`, `<linux/proc_fs.h>`, `<linux/kernel.h>`; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod_dep.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod_dep.c

Purpose: Loadable kernel module fixture used by delete_module syscall tests. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> Description: This is a kernel loadable module programme used by delete_module03 testcase which inserts this module as part of setup. This module has dependency on dummy_del_mod module (calls function of dummy_del_mod during initialization). The file was read in full for this report (40 lines, 903 bytes).

Important APIs/types/functions: Important call/API signals are `module`, `module_init`, `module_exit`. Defined constants/macros include `DIRNAME`. Relevant structs/types include `struct proc_dir_entry`. The file has little or no explicit LTP harness metadata.

Control flow: Control flow is mostly declarative or macro-driven. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates loadable kernel module state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<linux/module.h>`, `<linux/init.h>`, `<linux/proc_fs.h>`, `<linux/kernel.h>`; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/dummy_del_mod_dep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/Makefile

Purpose: Build integration for the LTP dup syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `FILTER_OUT_MAKE_TARGETS	+= dup06`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/dup`. Target signals: FILTER_OUT_MAKE_TARGETS	+= dup06.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup01.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. Copyright (c) 2020 SUSE LLC 03/30/1992 AUTHOR: William Roske CO-PILOT: Dave Fenner \ Verify that dup(2) syscall executes successfully and allocates a new file descriptor which refers to the same open file as oldfd. The file was read in full for this report (48 lines, 862 bytes).

Important APIs/types/functions: Primary functions are `verify_dup`, `setup`, `cleanup`. Important call/API signals are `TST_EXP_FD`, `SAFE_FSTAT`, `TST_EXP_EQ_LU`, `SAFE_CLOSE`, `SAFE_OPEN`. Relevant structs/types include `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_dup`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: case/errno constants `O_RDWR, O_CREAT`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. Copyright (c) 2020 SUSE LLC 03/30/1992 AUTHOR: Richard Logan CO-PILOT: William Roske \ Verify that dup(2) syscall fails with errno EBADF when called with invalid value for oldfd argument. The file was read in full for this report (37 lines, 693 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FAIL2`, `SAFE_CLOSE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. Copyright (c) 2020 SUSE LLC \ Verify that dup(2) syscall fails with errno EMFILE when the per-process limit on the number of open file descriptors has been reached. The file was read in full for this report (56 lines, 995 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `TST_EXP_FAIL2`, `SAFE_CLOSE`, `SAFE_SYSCONF`, `SAFE_MALLOC`, `SAFE_OPEN`, `SAFE_DUP`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EMFILE, O_RDWR, O_CREAT`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. 06/1994 AUTHOR: Richard Logan CO-PILOT: William Roske Copyright (c) 2023 SUSE LLC \ Basic test for dup(2) of a system pipe descriptor. The file was read in full for this report (41 lines, 707 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`. Important call/API signals are `TST_EXP_FD`, `SAFE_CLOSE`, `SAFE_PIPE`. Defined constants/macros include `_GNU_SOURCE`. Harness metadata uses `.test_all`, `.setup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: harness fields `.test_all, .setup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup05.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. 06/1994 AUTHOR: Richard Logan CO-PILOT: William Roske Copyright (c) 2012-2023 SUSE LLC \ Basic test for dup(2) of a named pipe descriptor. The file was read in full for this report (42 lines, 695 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `TST_EXP_FD`, `SAFE_CLOSE`, `SAFE_MKFIFO`, `SAFE_OPEN`. Defined constants/macros include `FNAME`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: case/errno constants `O_RDWR`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE, section2/iosuite/dup1.c, by Airong Zhang Copyright (c) 2013 Cyril Hrubis <chrubis@suse.cz> Copyright (c) Linux Test Project, 2003-2024 \ Test for dup(2) syscall with max open file descriptors. The file was read in full for this report (78 lines, 1589 bytes).

Important APIs/types/functions: Primary functions are `cnt_free_fds`, `setup`, `cleanup`, `run`. Important call/API signals are `fcntl`, `SAFE_MALLOC`, `SAFE_CREAT`, `tst_res`, `SAFE_UNLINK`, `SAFE_CLOSE`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, F_GETFD`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE, section2/iosuite/dup3.c, by Airong Zhang Copyright (c) 2013 Cyril Hrubis <chrubis@suse.cz> Copyright (c) Linux Test Project, 2006-2024 \ Verify that the file descriptor created by dup(2) syscall has the same access mode as the old one. The file was read in full for this report (56 lines, 1232 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `SAFE_CREAT`, `TST_EXP_FD_SILENT`, `SAFE_FSTAT`, `tst_res`, `SAFE_CLOSE`, `SAFE_UNLINK`. Relevant structs/types include `struct tcase`, `struct stat`. Harness metadata uses `.test`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/Makefile

Purpose: Build integration for the LTP dup2 syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `FILTER_OUT_MAKE_TARGETS	+= dup201 dup205`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/dup2`. Target signals: FILTER_OUT_MAKE_TARGETS	+= dup201 dup205.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup201.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup201.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer 01/2002 Removed EMFILE test - Paul Larson \ Negative tests for dup2() with bad fd (EBADF). - First fd argument is less than 0 - First fd argument is getdtablesize() - Second fd argument is less than 0 - Second fd argument is getdtablesize() get some test specific values The file was read in full for this report (54 lines, 1048 bytes).

Important APIs/types/functions: Primary functions are `setup`, `run`. Important call/API signals are `TST_EXP_FAIL2`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<unistd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EMFILE, EBADF`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup202.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup202.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer \ Test whether the access mode are the same for both file descriptors. Create file with mode, dup2, [change mode], check mode - read only, dup2, read only ? The file was read in full for this report (118 lines, 2595 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `SAFE_CREAT`, `SAFE_DUP`, `close`, `SAFE_CLOSE`, `SAFE_UNLINK`, `TEST`, `tst_res`, `SAFE_CHMOD`, `SAFE_FSTAT`. Relevant structs/types include `struct tcase`, `struct stat`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<stdio.h>`, `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .setup, .cleanup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup203.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer \ Testcase to check the basic functionality of dup2(). The file was read in full for this report (109 lines, 2227 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `tst_res`, `SAFE_CREAT`, `SAFE_WRITE`, `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_FCNTL`, `TEST`, `SAFE_READ`, `SAFE_UNLINK`, `close`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<stdio.h>`, `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDONLY, F_SETFD, F_GETFD, FD_CLOEXEC`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup204.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup204.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 \ Test whether the inode number are the same for both file descriptors. The file was read in full for this report (54 lines, 881 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `SAFE_PIPE`, `close`, `TST_EXP_VAL`, `SAFE_FSTAT`, `TST_EXP_EQ_LU`, `SAFE_CLOSE`. Relevant structs/types include `struct stat`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup204.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup205.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup205.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE, section2/iosuite/dup6.c, by Airong Zhang \ Negative test for dup2() with max open file descriptors. The file was read in full for this report (82 lines, 1748 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `SAFE_MALLOC`, `SAFE_CREAT`, `TEST`, `tst_brk`, `tst_res`, `SAFE_UNLINK`, `SAFE_CLOSE`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<stdio.h>`, `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EMFILE, EINVAL`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup205.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup206.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup206.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) 2021 FUJITSU LIMITED. Author: Yang Xu <xuyang2018.jy@fujitsu.com> \ If oldfd is a valid file descriptor, and newfd has the same value as oldfd, then dup2() does nothing, and returns newfd. The file was read in full for this report (47 lines, 934 bytes).

Important APIs/types/functions: Primary functions are `verify_dup2`, `setup`, `cleanup`. Important call/API signals are `TST_EXP_FD_SILENT`, `tst_res`, `SAFE_CLOSE`, `SAFE_OPEN`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_dup2`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<unistd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDWR, O_CREAT`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup206.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup207.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup207.c

Purpose: LTP regression coverage for `dup2` behavior. Source intent: Copyright (c) 2021 FUJITSU LIMITED. Author: Yang Xu <xuyang2018.jy@fujitsu.com> \ Test whether the file offset are the same for both file descriptors. The file was read in full for this report (79 lines, 1690 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_CLOSE`, `close`, `tst_res`, `SAFE_LSEEK`, `TEST`, `SAFE_READ`. Defined constants/macros include `WRITE_STR`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<stdio.h>`, `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup2` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDWR, O_CREAT`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup2/dup207.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup3/Makefile

Purpose: Build integration for the LTP dup3 syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/dup3`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_01.c

Purpose: LTP regression coverage for `dup3` behavior. Source intent: Copyright (c) Ulrich Drepper <drepper@redhat.com> Copyright (c) International Business Machines Corp., 2009 Created - Jan 13 2009 - Ulrich Drepper <drepper@redhat.com> Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> \ Testcase to check whether dup3() supports O_CLOEXEC flag. The file was read in full for this report (63 lines, 1345 bytes).

Important APIs/types/functions: Primary functions are `cleanup`, `run`. Important call/API signals are `close`, `TST_EXP_FD_SILENT`, `SAFE_FCNTL`, `tst_res`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<errno.h>`, `<unistd.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_CLOEXEC, F_GETFD, FD_CLOEXEC`; harness fields `.test, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_02.c

Purpose: LTP regression coverage for `dup3` behavior. Source intent: Copyright (c) 2013 Fujitsu Ltd. Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> \ Test for various EINVAL error. The file was read in full for this report (47 lines, 940 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FAIL2`. Defined constants/macros include `_GNU_SOURCE`, `INVALID_FLAG`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test keeps state local to automatic variables and LTP harness bookkeeping. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `"tst_test.h"`, `"tst_safe_macros.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, O_CLOEXEC`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup3/dup3_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll/Makefile

Purpose: Build integration for the LTP epoll syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c

Purpose: LTP regression coverage for `epoll` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. The file was read in full for this report (739 lines, 22902 bytes).

Important APIs/types/functions: Primary functions are `test_epoll_create`, `test_epoll_ctl`, `main`. Important call/API signals are `tst_old_flush`, `tst_fork`, `waitpid`, `WEXITSTATUS`, `tst_resm`, `epoll_create`, `test_epoll_create`, `close`, `epoll_ctl`, `EPOLL_CTL_TEST_FAIL`, `EPOLL_CTL_TEST_PASS`, `test_epoll_ctl`, `fork`, `epoll`, `tst_brkm`, `tst_exit`. Defined constants/macros include `_GNU_SOURCE`, `TRUE`, `FALSE`, `NUM_RAND_ATTEMPTS`, `BACKING_STORE_SIZE_HINT`, `PROTECT_REGION_START`, `PROTECT_REGION_EXIT`, `PROTECT_REGION_END`, `PROTECT_FUNC`, `RES_PASS`, `RES_FAIL_RETV_MIS_ERRNO_MAT`, `RES_FAIL_RETV_BAD_ERRNO_MAT`, `RES_FAIL_RETV_MAT_ERRNO_MIS`, `RES_FAIL_RETV_BAD_ERRNO_MIS`, `RES_FAIL_RETV_MIS_ERRNO_IGN`, `RES_FAIL_RETV_BAD_ERRNO_IGN`, `RES_PASS_RETV_MAT_ERRNO_IGN`, `EPOLL_CTL_TEST_RESULTS_SHOW_PARAMS`. Relevant structs/types include `struct epoll_event`, `struct timeval`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around test-oriented functions `test_epoll_create, test_epoll_ctl`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<fcntl.h>`, `<stdarg.h>`, `<string.h>`, `<signal.h>`, `<assert.h>`, `<limits.h>`, `<ctype.h>`; legacy LTP harness APIs. It integrates with the sibling `epoll` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, ENOMEM, EPOLL, EPOLLIN, EPOLLOUT, EPOLLPRI, EPOLLERR, EPOLLHUP, EPOLLET, EBADF, EPERM, EPOLL_CTL_TEST_RESULTS_SHOW_PARAMS, EPOLL_CTL_TEST_FAIL, EPOLL_CTL_TEST_PASS, EPOLL_CTL_DEL, EPOLL_CTL_MOD, EPOLL_CTL_ADD`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/Makefile

Purpose: Build integration for the LTP epoll_create syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h

Purpose: Shared helper/header support for the LTP epoll_create tests. Source intent: Copyright (c) Linux Test Project, 2021 EPOLL_CREATE_H__ The file was read in full for this report (38 lines, 620 bytes).

Important APIs/types/functions: Primary functions are `do_epoll_create`, `variant_info`. Important call/API signals are `do_epoll_create`, `tst_syscall`, `epoll_create`, `tst_res`. Defined constants/macros include `EPOLL_CREATE_H__`, `EPOLL_CREATE_VARIANTS`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around do_-oriented functions `do_epoll_create`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on the local LTP syscall test build environment. It integrates with the sibling `epoll_create` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLL_CREATE_H__, EPOLL_CREATE_VARIANTS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c

Purpose: LTP regression coverage for `epoll_create` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that epoll_create return a nonnegative file descriptor on success. The size argument informed the kernel of the number of file descriptors that the caller expected to add to the epoll instance, but it is no longer required. The file was read in full for this report (38 lines, 839 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FD`, `do_epoll_create`, `epoll_create`, `SAFE_CLOSE`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`, `"epoll_create.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLL_CREATE_VARIANTS`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create02.c

Purpose: LTP regression coverage for `epoll_create` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that epoll_create returns -1 and set errno to EINVAL if size is not greater than zero. The file was read in full for this report (40 lines, 723 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FAIL`, `do_epoll_create`, `epoll_create`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`, `"epoll_create.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/Makefile

Purpose: Build integration for the LTP epoll_create1 syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c

Purpose: LTP regression coverage for `epoll_create1` behavior. Source intent: Copyright (c) Ulrich Drepper <drepper@redhat.com> Copyright (c) International Business Machines Corp., 2009 \ Verify that epoll_create1 sets the close-on-exec flag for the returned file descriptor with EPOLL_CLOEXEC. The file was read in full for this report (48 lines, 1011 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `tst_syscall`, `tst_brk`, `epoll_create1`, `SAFE_FCNTL`, `tst_res`, `SAFE_CLOSE`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create1` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLL_CLOEXEC, F_GETFD, FD_CLOEXEC`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_02.c

Purpose: LTP regression coverage for `epoll_create1` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Verify that epoll_create1 returns -1 and set errno to EINVAL with an invalid value specified in flags. The file was read in full for this report (37 lines, 770 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FAIL`, `tst_syscall`, `epoll_create1`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create1` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EPOLL_CLOEXEC`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/Makefile

Purpose: Build integration for the LTP epoll_ctl syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Xiao Yang <yangx.jy@cn.fujitsu.com> \ Check the basic functionality of the epoll_ctl: - When epoll_ctl succeeds to register fd on the epoll instance and associates event with fd, epoll_wait will get registered fd and event correctly. - When epoll_ctl succeeds to change event which is related to fd, epoll_wait will get changed event correctly. The file was read in full for this report (145 lines, 3134 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `has_event`, `check_epoll_ctl`, `opera_epoll_ctl`, `verify_epoll_ctl`. Important call/API signals are `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`, `check_epoll_ctl`, `SAFE_WRITE`, `epoll_wait`, `tst_res`, `epoll_ctl`, `SAFE_READ`, `opera_epoll_ctl`, `TEST`, `verify_epoll_ctl`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLLOUT, EPOLL_CTL_ADD, EPOLL_CTL_MOD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Xiao Yang <yangx.jy@cn.fujitsu.com> \ Verify that epoll_ctl() fails with: - EBADF if epfd is an invalid fd. - EPERM if fd does not support epoll. - ENOENT if fd is not registered with EPOLL_CTL_DEL. - ENOENT if fd is not registered with EPOLL_CTL_MOD. The file was read in full for this report (95 lines, 2499 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `verify_epoll_ctl`. Important call/API signals are `epoll_ctl`, `SAFE_OPEN`, `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`, `verify_epoll_ctl`, `TST_EXP_FAIL`. Relevant structs/types include `struct epoll_event`, `struct testcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EPERM, EINVAL, ENOENT, EEXIST, EPOLLIN, EPOLLOUT, EFAULT, EPOLL_CTL_DEL, EPOLL_CTL_MOD, EPOLL_CTL_ADD, O_RDONLY, O_DIRECTORY`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Check that epoll_ctl returns zero with different combinations of events on success. The file was read in full for this report (76 lines, 1567 bytes).

Important APIs/types/functions: Primary functions are `run_all`, `setup`, `cleanup`. Important call/API signals are `TST_IS_BIT_SET`, `TST_EXP_PASS`, `epoll_ctl`, `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`. Defined constants/macros include `NUM_EPOLL_EVENTS`, `WIDTH_EPOLL_EVENTS`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_all`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"tst_bitmap.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; case/errno constants `EPOLLIN, EPOLLOUT, EPOLLPRI, EPOLLERR, EPOLLHUP, EPOLLET, EPOLLONESHOT, EPOLLRDHUP, EPOLL_CTL_MOD, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl04.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that the maximum number of nesting allowed inside epoll sets is 5, otherwise epoll_ctl fails with EINVAL. The file was read in full for this report (72 lines, 1482 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `verify_epoll_ctl`. Important call/API signals are `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`, `verify_epoll_ctl`, `TST_EXP_FAIL2_ARR`. Defined constants/macros include `MAX_DEPTH`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EPOLLIN, ELOOP, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that epoll_ctl() fails with ELOOP if fd refers to an epoll instance and this EPOLL_CTL_ADD operation would result in a circular loop of epoll instances monitoring one another. The file was read in full for this report (70 lines, 1508 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `verify_epoll_ctl`. Important call/API signals are `epoll_ctl`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `SAFE_CLOSE`, `verify_epoll_ctl`, `TST_EXP_FAIL`. Defined constants/macros include `MAX_DEPTH`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ELOOP, EPOLLIN, EPOLL_CTL_ADD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/Makefile

Purpose: Build integration for the LTP epoll_pwait syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2021 Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_pwait() and epoll_pwait2(). The file was read in full for this report (117 lines, 2434 bytes).

Important APIs/types/functions: Primary functions are `sighandler`, `verify_sigmask`, `verify_nonsigmask`, `run`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait`, `epoll_pwait2`, `TEST`, `do_epoll_pwait`, `tst_res`, `TST_EXP_FAIL`, `SAFE_FORK`, `TST_PROCESS_STATE_WAIT`, `SAFE_KILL`, `SAFE_WRITE`, `SAFE_READ`, `tst_reap_children`, `epoll_pwait_init`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGACTION`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct sigaction`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_sigmask, verify_nonsigmask`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINTR, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_pwait and epoll_pwait2. Checks if data avaiable in a file descriptor are reported correctly in the syscall return value. The file was read in full for this report (65 lines, 1318 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `TEST`, `do_epoll_pwait`, `tst_res`, `epoll_pwait_init`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_WRITE`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait03.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Check that epoll_pwait and epoll_pwait2 timeouts correctly. The file was read in full for this report (76 lines, 1465 bytes).

Important APIs/types/functions: Primary functions are `sample_fn`, `setup`, `cleanup`. Important call/API signals are `tst_timer_start`, `TEST`, `do_epoll_pwait`, `tst_timer_stop`, `tst_timer_sample`, `tst_res`, `epoll_pwait_init`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Defined constants/macros include `USEC_PER_NSEC`, `USEC_PER_SEC`. Relevant structs/types include `struct epoll_event`, `struct timespec`. Harness metadata uses `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_timer_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD`; harness fields `.setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait04.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Verify that, epoll_pwait() and epoll_pwait2() return -1 and set errno to EFAULT with a sigmask points outside user's accessible address space. The file was read in full for this report (63 lines, 1287 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait`, `epoll_pwait2`, `TST_EXP_FAIL`, `do_epoll_pwait`, `epoll_pwait_init`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_WRITE`, `tst_get_bad_addr`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EFAULT, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Verify that, epoll_pwait2() return -1 and set errno to EINVAL with an invalid timespec. The file was read in full for this report (71 lines, 1455 bytes).

Important APIs/types/functions: Primary functions are `run_all`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait2`, `TST_EXP_FAIL`, `epoll_pwait2_supported`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_WRITE`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct test_case_t`, `struct timespec`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_all`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"tst_timer.h"`, `"lapi/epoll.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) 2025 SUSE LLC <mdoucha@suse.cz> \ Verify that various timeout values don't get misinterpreted as infinity by epoll_pwait() and epoll_pwait2(). Regression fixed in: commit d9ec73301099ec5975505e1c3effbe768bab9490 Author: Max Kellermann <max.kellermann@ionos.com> Date: Tue Apr 29 20:58:27 2025 +0200 fs/eventpoll: fix endless busy loop after timeout has expired File descriptor types not supported by epoll The file was read in full for this report (89 lines, 1803 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait`, `epoll_pwait2`, `TST_FD_FOREACH`, `tst_res`, `tst_fd_desc`, `SAFE_EPOLL_CTL`, `do_epoll_pwait`, `epoll_pwait_init`, `SAFE_EPOLL_CREATE1`, `SAFE_CLOSE`. Relevant structs/types include `struct timespec`, `struct epoll_event`, `struct tst_tag`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"tst_epoll.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h

Purpose: Shared helper/header support for the LTP epoll_pwait tests. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> LTP_EPOLL_PWAIT_VAR_H The file was read in full for this report (45 lines, 1050 bytes).

Important APIs/types/functions: Primary functions are `do_epoll_pwait`, `epoll_pwait_init`. Important call/API signals are `do_epoll_pwait`, `epoll_pwait2`, `epoll_pwait`, `epoll_pwait_init`, `tst_res`, `epoll_pwait_supported`, `epoll_pwait2_supported`. Defined constants/macros include `LTP_EPOLL_PWAIT_VAR_H`, `TEST_VARIANTS`, `MSEC_PER_SEC`, `NSEC_PER_MSEC`. Relevant structs/types include `struct epoll_event`, `struct timespec`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around do_-oriented functions `do_epoll_pwait`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"lapi/epoll.h"`; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/Makefile

Purpose: Build integration for the LTP epoll_wait syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `epoll_wait02: LDLIBS+=-lrt`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> \ Basic test for epoll_wait. Check that epoll_wait works for EPOLLOUT and EPOLLIN events on an epoll instance and that struct epoll_event is set correctly. The file was read in full for this report (243 lines, 4866 bytes).

Important APIs/types/functions: Primary functions are `get_writesize`, `setup`, `has_event`, `dump_epevs`, `verify_epollout`, `verify_epollin`, `verify_epollio`, `cleanup`, `do_test`. Important call/API signals are `get_writesize`, `SAFE_WRITE`, `tst_brk`, `SAFE_READ`, `tst_res`, `SAFE_PIPE`, `epoll_create`, `epoll_ctl`, `verify_epollout`, `TEST`, `epoll_wait`, `verify_epollin`, `verify_epollio`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct pollfd`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epollout, verify_epollin, verify_epollio`; test-oriented functions `do_test`; cleanup-oriented functions `cleanup`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `<poll.h>`, `<string.h>`, `<errno.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLOUT, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2017 Cyril Hrubis <chrubis@suse.cz> \ Check that epoll_wait(2) timeouts correctly. The file was read in full for this report (72 lines, 1297 bytes).

Important APIs/types/functions: Primary functions are `sample_fn`, `setup`, `cleanup`. Important call/API signals are `epoll_wait`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_timer_sample`, `tst_res`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `<unistd.h>`, `<errno.h>`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD`; harness fields `.setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2021 Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_wait: - epoll_wait fails with EBADF if epfd is not a valid file descriptor. - epoll_wait fails with EINVAL if epfd is not an epoll file descriptor. The file was read in full for this report (85 lines, 2160 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_epoll_wait`, `cleanup`. Important call/API signals are `SAFE_MMAP`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `verify_epoll_wait`, `TST_EXP_FAIL`, `epoll_wait`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_wait`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/mman.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EINVAL, EFAULT, EPOLLOUT, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Check that a timeout equal to zero causes epoll_wait() to return immediately. The file was read in full for this report (70 lines, 1460 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `epoll_wait`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_res`, `tst_timer_elapsed_us`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Defined constants/macros include `USEC_PRECISION`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, CLOCK_MONOTONIC, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that epoll receives EPOLLRDHUP event when we hang a reading half-socket we are polling on. The file was read in full for this report (125 lines, 2690 bytes).

Important APIs/types/functions: Primary functions are `create_server`, `run`, `setup`, `cleanup`. Important call/API signals are `create_server`, `tst_init_sockaddr_inet_bin`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_GETSOCKNAME`, `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `SAFE_CLOSE`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `tst_init_sockaddr_inet`, `SAFE_CONNECT`, `SAFE_EPOLL_CREATE1`, `SAFE_EPOLL_CTL`, `TST_EXP_PASS_SILENT`, `SAFE_EPOLL_WAIT`, `TST_CHECKPOINT_WAKE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `fcntl`. Relevant structs/types include `struct sockaddr_in`, `struct sockaddr`, `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_net.h"`, `"tst_epoll.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLRDHUP, EPOLL_CTL_ADD, F_GETFD`; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait06.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that edge triggering is correctly handled by epoll, for both EPOLLIN and EPOLLOUT. [Algorithm] - The file descriptors for non-blocking pipe are registered on an epoll instance. - A call to epoll_wait() is done that will return a EPOLLIN event. The file was read in full for this report (106 lines, 2758 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `epoll_wait`, `SAFE_PIPE2`, `SAFE_FCNTL`, `SAFE_CLOSE`, `tst_res`, `SAFE_EPOLL_CREATE1`, `SAFE_EPOLL_CTL`, `SAFE_WRITE`, `TST_EXP_FAIL`, `write`, `TST_EXP_EQ_LI`, `SAFE_EPOLL_WAIT`, `SAFE_READ`, `read`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<fcntl.h>`, `"tst_test.h"`, `"tst_epoll.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLLOUT, EPOLLET, EAGAIN, O_NONBLOCK, F_SETPIPE_SZ, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that EPOLLONESHOT is correctly handled by epoll_wait. We open a channel, write in it two times and verify that EPOLLIN has been received only once. The file was read in full for this report (72 lines, 1563 bytes).

Important APIs/types/functions: Primary functions are `cleanup`, `run`. Important call/API signals are `SAFE_CLOSE`, `SAFE_PIPE`, `tst_res`, `SAFE_EPOLL_CREATE1`, `SAFE_EPOLL_CTL`, `SAFE_WRITE`, `TST_EXP_EQ_LI`, `SAFE_EPOLL_WAIT`, `SAFE_READ`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.cleanup`.

Control flow: The test is organized around run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"tst_epoll.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLLONESHOT, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test_all, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/Makefile

Purpose: Build integration for the LTP eventfd syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `top_srcdir		?= ../../../..`, `LDLIBS			+= $(AIO_LIBS)`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/eventfd`. Targets are inferred by the common rules from sibling sources.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd01.c

Purpose: LTP regression coverage for `eventfd` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Copyright (c) Linux Test Project, 2008-2022 Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify read operation for eventfd fail with: - EAGAIN when counter is zero on non blocking fd - EINVAL when buffer size is less than 8 bytes The file was read in full for this report (46 lines, 1006 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FD`, `eventfd`, `SAFE_READ`, `TST_EXP_EQ_LI`, `TST_EXP_FAIL`, `read`, `SAFE_CLOSE`. Defined constants/macros include `EVENT_COUNT`. Harness metadata uses `.test_all`, `.needs_kconfigs`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/eventfd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; kernel configuration predicates. It integrates with the sibling `eventfd` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EAGAIN, EINVAL, EFD_NONBLOCK`; harness fields `.test_all, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd01.c -->
