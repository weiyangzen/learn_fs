# subset-b-009306 research

Grouped research report for LTP syscall scheduler, socket send, namespace, credential, priority, timer, and rlimit tests under `sources/test-tools/ltp/testcases/kernel/syscalls`. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c

Purpose: Verify that, sched_getattr(2) returns -1 and sets errno to: 1. ESRCH if pid is unused. 2. EINVAL if address is NULL. 3. EINVAL if size is invalid. 4. EINVAL if flag is not zero. In this shard it contributes focused coverage for scheduler attribute syscall validation around sched_attr size, flags, and pid lookup.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getattr`, `setup`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_attr`, `sched_getattr`, `sets`, `setup`, `tst_get_unused_pid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getattr`, `setup`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/Makefile

Purpose: build glue for the LTP `sched_getparam` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_getparam` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c

Purpose: Verify that: sched_getparam(2) gets correct scheduling parameters for the specified process: - If pid is zero, sched_getparam(2) gets the scheduling parameters for the calling process. - If pid is not zero, sched_getparam(2) gets the scheduling parameters for the specified [pid] process. In this shard it contributes focused coverage for scheduler parameter retrieval across libc/syscall variants and pid addressing modes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getparam`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `sched_getparam`, `sched_param`, `sched_priority`, `sched_variant`, `sched_variants`, `setup`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getparam`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c

Purpose: Verify that, sched_getparam(2) returns -1 and sets errno to - ESRCH if the process with specified pid could not be found - EINVAL if the parameter pid is an invalid value (-1) - EINVAL if the parameter p is an invalid address In this shard it contributes focused coverage for scheduler parameter retrieval across libc/syscall variants and pid addressing modes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getparam`, `setup`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_getparam`, `sched_param`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getparam`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/Makefile

Purpose: build glue for the LTP `sched_getscheduler` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_getscheduler` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c

Purpose: Testcase to check sched_getscheduler() returns correct return value. [Algorithm] Call sched_setcheduler() to set the scheduling policy of the current process. Then call sched_getscheduler() to ensure that this is same as what set by the previous call to sched_setscheduler(). Use SCHED_RR, SCHED_FIFO, SCHED_OTHER as the scheduling policies for sched_setscheduler(). In this shard it contributes focused coverage for scheduler policy readback and error handling after policy changes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `test_cases_t`. Important syscall/helper surface includes: `TEST`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `TST_RET`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setcheduler`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_check_rt_group_sched_support`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c

Purpose: Pass an unused pid to sched_getscheduler() and test for ESRCH. In this shard it contributes focused coverage for scheduler policy readback and error handling after policy changes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_getscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/Makefile

Purpose: build glue for the LTP `sched_rr_get_interval` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_rr_get_interval` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval01.c

Purpose: Gets round-robin time quantum by calling sched_rr_get_interval() and checks that the value is sane. It is also a regression test for: - 975e155ed873 (sched/rt: Show the 'sched_rr_timeslice' SCHED_RR timeslice tuning knob in milliseconds) - c7fcb99877f9 ( sched/rt: Fix sysctl_sched_rr_timeslice intial value) In this shard it contributes focused coverage for round-robin interval reporting across libc, old timespec, and time64 syscall variants.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `variants`. Important syscall/helper surface includes: `TEST`, `TST_ASSERT_INT`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`, `TST_RET`, `sched_param`, `sched_rr_get_interval`, `sched_rr_timeslice`, `sched_setscheduler`, `setup`, `tst_check_rt_group_sched_support`, `tst_res`, `tst_sched`, `tst_tag`, `tst_test`, `tst_timer`, `tst_ts`, `tst_ts_get`, `tst_ts_get_nsec`, `tst_ts_get_sec`, `tst_ts_to_ms`, `tst_ts_valid`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `variants`. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, time64/timer variant helpers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems; regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval02.c

Purpose: Verify that for a process with scheduling policy SCHED_FIFO, sched_rr_get_interval() writes zero into timespec structure for tv_sec & tv_nsec. In this shard it contributes focused coverage for round-robin interval reporting across libc, old timespec, and time64 syscall variants.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `variants`. Important syscall/helper surface includes: `TEST`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`, `TST_RET`, `sched_param`, `sched_rr_get_interval`, `sched_setscheduler`, `setup`, `tst_check_rt_group_sched_support`, `tst_res`, `tst_sched`, `tst_test`, `tst_timer`, `tst_ts`, `tst_ts_get`, `tst_ts_get_nsec`, `tst_ts_get_sec`, `tst_ts_set_nsec`, `tst_ts_set_sec`, `tst_ts_valid`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `variants`. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, time64/timer variant helpers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c

Purpose: Verify that: - sched_rr_get_interval() fails with errno set to EINVAL for an invalid pid - sched_rr_get_interval() fails with errno set to ESRCH if the process with specified pid does not exists - sched_rr_get_interval() fails with errno set to EFAULT if the address specified as &tp is invalid In this shard it contributes focused coverage for round-robin interval reporting across libc, old timespec, and time64 syscall variants.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_cases_t`, `variants`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`, `sched_param`, `sched_rr_get_interval`, `sched_setscheduler`, `setup`, `tst_check_rt_group_sched_support`, `tst_get_bad_addr`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_timer`, `tst_ts`, `tst_ts_get`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `variants`. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, time64/timer variant helpers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/Makefile

Purpose: build glue for the LTP `sched_setaffinity` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_setaffinity` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c

Purpose: Check various errnos for sched_setaffinity(): 1. EFAULT, if the supplied memory address is invalid. 2. EINVAL, if the mask doesn't contain at least one permitted cpu. 3. ESRCH, if the process whose id is pid could not be found. 4. EPERM, if the calling process doesn't have appropriate privileges. In this shard it contributes focused coverage for CPU affinity mask setting error paths, privilege checks, and cpuset allocation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `kill_pid`, `verify_test`, `setup`, `cleanup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_KILL`, `SAFE_SETEUID`, `SAFE_WAITPID`, `TEST`, `TST_ERR`, `TST_RET`, `sched_getaffinity`, `sched_setaffinity`, `setup`, `tst_brk`, `tst_get_bad_addr`, `tst_get_unused_pid`, `tst_ncpus_max`, `tst_res`, `tst_safe_macros`, `tst_strerrno`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `kill_pid`, `verify_test`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/Makefile

Purpose: build glue for the LTP `sched_setattr` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_setattr` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/sched_setattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/sched_setattr01.c

Purpose: Description: Verify that: 1) sched_setattr succeed with correct parameters 2) sched_setattr fails with unused pid 3) sched_setattr fails with invalid address 4) sched_setattr fails with invalid flag In this shard it contributes focused coverage for deadline scheduler attribute setting and sched_attr ABI validation.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `sched_setattr_verify`, `main`, `setup`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `sched_attr`, `sched_deadline`, `sched_flags`, `sched_nice`, `sched_period`, `sched_policy`, `sched_priority`, `sched_runtime`, `sched_setattr`, `sched_setattr01`, `sched_setattr_verify`, `setup`, `tst_exit`, `tst_get_unused_pid`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_strerrno`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `sched_setattr_verify`, `main`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setattr/sched_setattr01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/Makefile

Purpose: build glue for the LTP `sched_setparam` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_setparam` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam01.c

Purpose: Basic test for sched_setparam(2) Call sched_setparam(2) with pid=0 so that it will set the scheduling parameters for the calling process In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_PASS`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_variant`, `sched_variants`, `setup`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam02.c

Purpose: Checks functionality for sched_setparam(2) This test changes the scheduling priority for current process and verifies it by calling sched_getparam(). In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `test_cases_t`. Important syscall/helper surface includes: `TST_EXP_PASS_SILENT`, `sched_getparam`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_check_rt_group_sched_support`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c

Purpose: Checks functionality for sched_setparam(2) for pid != 0 This test forks a child and changes its parent's scheduling priority. In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS_SILENT`, `sched_getparam`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_brk`, `tst_check_rt_group_sched_support`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam04.c

Purpose: Verify that: 1. sched_setparam(2) returns -1 and sets errno to ESRCH if the process with specified pid could not be found. 2. sched_setparam(2) returns -1 and sets errno to EINVAL if the parameter pid is an invalid value (-1). 3. sched_setparam(2) returns -1 and sets errno to EINVAL if the parameter p is an invalid address. 4. sched_setparam(2) returns -1 sets errno to EINVAL if the value for p.sched_priority is other than 0 for scheduling policy, SCHED_OTHER. In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_cases_t`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam05.c

Purpose: Verify that sched_setparam() fails if the user does not have proper privileges. In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_variant`, `sched_variants`, `setup`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/Makefile

Purpose: build glue for the LTP `sched_setscheduler` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_setscheduler` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler01.c

Purpose: Testcase to test whether sched_setscheduler(2) sets the errnos correctly. [Algorithm] 1. Call sched_setscheduler with an invalid pid, and expect ESRCH to be returned. 2. Call sched_setscheduler with an invalid scheduling policy, and expect EINVAL to be returned. 3. Call sched_setscheduler with an invalid "param" address, which lies outside the address space of the process, and expect EFAULT to be returned. 4. Call sched_setscheduler with an invalid priority value in "param" and expect EINVAL to be returned In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_cases_t`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c

Purpose: Testcase to test whether sched_setscheduler(2) sets the errnos correctly. [Algorithm] Call sched_setscheduler as a non-root uid, and expect EPERM to be returned. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c

Purpose: nice rlimit ranges from 1 to 40, mapping to real nice value from 19 to -20. We set it to 19, as the default priority of process with fair policy is 120, which will be translated into nice 20, we make this RLIMIT_NICE smaller than that, to verify the can_nice usage issue. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `l_rlimit_show`, `l_rlimit_setup`, `verify_fn`, `setup`, `do_test`. Key structs/tables: `test_case_t`, `cases`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_GETRESUID`, `SAFE_GETRLIMIT`, `SAFE_SETEUID`, `SAFE_SETRLIMIT`, `SAFE_WAIT`, `TST_EXP_PASS`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `seteuid`, `setup`, `tst_brk`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `cases`. important local functions are `l_rlimit_show`, `l_rlimit_setup`, `verify_fn`, `setup`, `do_test`.

State and persistence behavior: exercises forked child state; process credentials; resource limits. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c

Purpose: Testcases that test if sched_setscheduler with flag SCHED_RESET_ON_FORK restores children policy to SCHED_NORMAL. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `test_reset_on_fork`. Key structs/tables: `test_case_t`, `cases`. Important syscall/helper surface includes: `SAFE_FORK`, `TST_CAP`, `TST_CAP_REQ`, `sched_getparam`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `tst_cap`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `cases`. important local functions are `test_reset_on_fork`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/Makefile

Purpose: build glue for the LTP `sched_yield` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sched_yield` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c

Purpose: NAME sched_yield01.C DESCRIPTION Testcase to check that sched_yield returns correct values. ALGORITHM Call sched_yield(), check its return value. If it is 0, then pass, otherwise fail with proper errno! USAGE: <for command-line> sched_yield01 [-c n] [-i n] [-I x] [-P x] [-t] where, -c n : Run n copies concurrently. -i n : Execute test n times. -I x : Execute test for x seconds. -P x : Pause for x seconds between iterations. -t : Turn on syscall timing. HISTORY 07/2001 Ported by Wayne Boyer RESTRICTIONS None In this shard it contributes focused coverage for legacy smoke coverage for sched_yield return handling.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `sched_yield`, `sched_yield01`, `setup`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/Makefile

Purpose: build glue for the LTP `seccomp` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `seccomp` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c

Purpose: Test PR_GET_SECCOMP and PR_SET_SECCOMP with both prctl(2) and seccomp(2). The second one is called via __NR_seccomp using tst_syscall(). - If PR_SET_SECCOMP sets the SECCOMP_MODE_STRICT for the calling thread, the only system call that the thread is permitted to make are read(2), write(2),_exit(2)(but not exit_group(2)), and sigreturn(2). Other system calls result in the delivery of a SIGKILL signal. This operation is available only if the kernel is configured with CONFIG_SECCOMP enabled. - If PR_SET_SECCOMP sets the SECCOMP_MODE_FILTER for the calling thread, the system calls allowed are defined by a pointer to a Berkeley Packet Filter. Other system calls result int the delivery of a SIGSYS signal with SECCOMP_RET_KILL. In this shard it contributes focused coverage for seccomp strict/filter mode behavior through prctl and seccomp syscalls.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `check_filter_mode_inherit`, `check_strict_mode`, `check_filter_mode`, `verify_prctl`, `setup`. Key structs/tables: `tcase`, `strict_filter`. Important syscall/helper surface includes: `GET_SECCOMP`, `SAFE_FORK`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WAITPID`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `prctl`, `seccomp`, `sets`, `setup`, `tst_brk`, `tst_kconfig`, `tst_kconfig_check`, `tst_res`, `tst_syscall`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `strict_filter`. important local functions are `check_filter_mode_inherit`, `check_strict_mode`, `check_filter_mode`, `verify_prctl`, `setup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; thread seccomp mode. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges, kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/Makefile

Purpose: build glue for the LTP `select` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `select` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select01.c

Purpose: Copyright (c) Linux Test Project, 2008-2025 Copyright (c) 2000 Silicon Graphics, Inc. All Rights Reserved. http://www.sgi.com Authors: Richard Logan, William Roske In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`, `cleanup`. Key structs/tables: `tcases`. Important syscall/helper surface includes: `SAFE_MKFIFO`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ANY`, `TEST`, `TST_RET`, `select`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`, `cleanup`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c

Purpose: Check that :manpage:`select(2)` timeouts correctly. In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `sample_fn`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_PIPE`, `TEST`, `TST_RET`, `select`, `setup`, `tst_res`, `tst_test`, `tst_timer_sample`, `tst_timer_start`, `tst_timer_stop`, `tst_timer_test`, `tst_us_to_timeval`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `sample_fn`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select03.c

Purpose: Exercises select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior. In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_select`, `run`, `setup`. Key structs/tables: `tcases`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WAITPID`, `TEST`, `TST_ERR`, `TST_RET`, `select`, `setup`, `tst_get_bad_addr`, `tst_res`, `tst_strerrno`, `tst_strstatus`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_select`, `run`, `setup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c

Purpose: Test to check if fd set bits are cleared by :manpage:`select(2)`. [Algorithm] - Check that writefds flag is cleared on full pipe - Check that readfds flag is cleared on empty pipe In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `tcases`. Important syscall/helper surface includes: `SAFE_PIPE`, `SAFE_PIPE2`, `TEST`, `TST_ERR`, `TST_RET`, `select`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select_var.h

Purpose: Header support for the LTP `select` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `select` tests. Visible symbols include functions `do_select_faulty_to`, `select_info`, structs `compat_sel_arg_struct`, arrays none, and helper macros/APIs `select`, `tst_brk`, `tst_res`, `tst_syscall`, `tst_timer`, `tst_variant`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `select` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/send/Makefile

Purpose: build glue for the LTP `send` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `send` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/send/send01.c

Purpose: Test Name: send01 Test Description: Verify that send() returns the proper errno for various failure cases HISTORY 07/2001 Ported by Wayne Boyer In this shard it contributes focused coverage for send-family socket error handling and MSG_MORE behavior.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`. Key structs/tables: `test_case_t`, `tdat`. Important syscall/helper surface includes: `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `select`, `setup`, `setup0`, `setup1`, `setup2`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. table-driven cases are held in `tdat`. important local functions are `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c

Purpose: Check that the kernel correctly handles send()/sendto()/sendmsg() calls with MSG_MORE flag. In this shard it contributes focused coverage for send-family socket error handling and MSG_MORE behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_send`, `do_sendto`, `do_sendmsg`, `setup`, `check_recv`, `cleanup`, `run`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `SAFE_ACCEPT`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_LISTEN`, `SAFE_SEND`, `SAFE_SENDMSG`, `SAFE_SENDTO`, `SAFE_SOCKET`, `TEST`, `TST_ERR`, `TST_RET`, `sendmsg`, `sendto`, `setup`, `tst_init_sockaddr_inet_bin`, `tst_net`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_send`, `do_sendto`, `do_sendmsg`, `setup`, `check_recv`, `cleanup`, `run`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP network helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/Makefile

Purpose: build glue for the LTP `sendfile` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sendfile` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c

Purpose: Test the basic functionality of the sendfile() system call: 1. Call sendfile() with offset = 0. 2. Call sendfile() with offset in the middle of the file. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `sendfile`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c

Purpose: Testcase to test that sendfile(2) system call returns EBADF when passing wrong out_fd or in_fd. There are four cases: - in_fd == -1 - out_fd = -1 - in_fd opened with O_WRONLY - out_fd opened with O_RDONLY In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_OPEN`, `TST_EXP_FAIL2`, `sendfile`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile04.c

Purpose: Testcase to test that sendfile(2) system call returns EFAULT when passing wrong offset pointer. [Algorithm] Given wrong address or protected buffer as OFFSET argument to sendfile: - a wrong address is created by munmap a buffer allocated by mmap - a protected buffer is created by mmap with specifying protection In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TST_EXP_FAIL2`, `sendfile`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile05.c

Purpose: Testcase to test that sendfile(2) system call returns EINVAL when passing negative offset. [Algorithm] Call sendfile with offset = -1. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_OPEN`, `TST_EXP_FAIL`, `sendfile`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile06.c

Purpose: Test that sendfile() system call updates file position of in_fd correctly when passing NULL as offset. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_FSTAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `sendfile`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile07.c

Purpose: Testcase to test that sendfile(2) system call returns EAGAIN when passing full out_fd opened with O_NONBLOCK. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_OPEN`, `SAFE_SOCKETPAIR`, `TEST`, `TST_ERR`, `TST_EXP_FAIL`, `TST_RET`, `sendfile`, `setup`, `tst_brk`, `tst_fill_file`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, TST_RET. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c

Purpose: Bug in the splice code has caused the file position on the write side of the sendfile system call to be incorrectly set to the read side file position. This can result in the data being written to an incorrect offset. This is a regression test for kernel commit 2cb4b05e76478. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `sendfile`, `setup`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`, `cleanup`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile09.c

Purpose: Testcase copied from sendfile02.c to test the basic functionality of the sendfile() system call on large file. There is a kernel bug which introduced by commit 8f9c0119d7ba9 and fixed by commit 5d73320a96fcc. Only supports 64bit systems. [Algorithm] 1. Call sendfile() with offset at 0. 2. Call sendfile() with offset at 3GB. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_GB`, `TST_RET`, `sendfile`, `setup`, `tst_brk`, `tst_fs_has_free`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/Makefile

Purpose: build glue for the LTP `sendmmsg` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sendmmsg` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg.h

Purpose: Header support for the LTP `sendmmsg` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `sendmmsg` tests. Visible symbols include functions none, structs none, arrays `variants`, and helper macros/APIs `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`, `sendmmsg`, `tst_safe_macros`, `tst_test`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `sendmmsg` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c

Purpose: Basic sendmmsg() test that sends and receives messages. This test is based on source contained in the man pages for sendmmsg and recvmmsg in release 4.15 of the Linux man-pages project. In this shard it contributes focused coverage for batched datagram send syscall wrappers and time64 variant coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_SOCKET`, `TST_GET_UNUSED_PORT`, `sendmmsg`, `setup`, `tst_buffers`, `tst_res`, `tst_test`, `tst_ts`, `tst_ts_get`, `tst_ts_set_nsec`, `tst_ts_set_sec`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c

Purpose: Exercises batched datagram send syscall wrappers and time64 variant coverage. In this shard it contributes focused coverage for batched datagram send syscall wrappers and time64 variant coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_test`, `setup`, `cleanup`. Key structs/tables: `test_case`, `tcase`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_SOCKET`, `TST_EXP_FAIL`, `sendmmsg`, `setup`, `tst_buffers`, `tst_res`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `tcase`. important local functions are `do_test`, `setup`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h

Purpose: Header support for the LTP `sendmmsg` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `sendmmsg` tests. Visible symbols include functions none, structs none, arrays none, and helper macros/APIs `sendmmsg`, `tst_brk`, `tst_syscall`, `tst_timer`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `sendmmsg` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/Makefile

Purpose: build glue for the LTP `sendmsg` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sendmsg` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c

Purpose: Test Name: sendmsg01 Test Description: Verify that sendmsg() returns the proper errno for various failure cases HISTORY 07/2001 Ported by Wayne Boyer 05/2003 Modified by Manoj Iyer - Make setup function set up lo device. In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `start_server`, `do_child`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`, `setup4`. Key structs/tables: `test_case_t`, `tdat`. Important syscall/helper surface includes: `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`, `TEST_LOOPING`, `TST_GET_UNUSED_PORT`, `TST_TOTAL`, `select`, `sendmsg`, `setup`, `setup0`, `setup1`, `setup2`, `setup3`, `setup4`, `setup5`, `setup6`, `setup8`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_require_root`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. table-driven cases are held in `tdat`. important local functions are `main`, `start_server`, `do_child`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`, `setup4`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c

Purpose: Copyright (C) 2013 Linux Test Project This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Further, this software is distributed without any warranty that it is free of the rightful claim of any third person regarding infringement or the like. Any license provided herein, whether implied or otherwise, applies only to this software file. In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `client`, `server`, `reproduce`, `help`, `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETVAL`, `SAFE_MALLOC`, `SAFE_STRTOL`, `SETVAL`, `TEST_LOOPING`, `sendmsg`, `setting`, `setup`, `tst_brkm`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_rmdir`, `tst_tmpdir`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `client`, `server`, `reproduce`, `help`, `main`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c

Purpose: CVE-2017-17712 Test for race condition vulnerability in sendmsg() on SOCK_RAW sockets. Changing the value of IP_HDRINCL socket option in parallel with sendmsg() call may lead to uninitialized stack pointer usage, allowing arbitrary code execution or privilege escalation. Fixed in 4.15 8f659a03a0ba ("net: ipv4: fix for a race condition in raw_sendmsg") In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_SETSOCKOPT_INT`, `SAFE_SOCKET`, `TST_SR_SKIP`, `TST_TAINT_D`, `TST_TAINT_W`, `sendmsg`, `setsockopt`, `setup`, `tst_fuzzy_sync`, `tst_fzsync_end_race_a`, `tst_fzsync_end_race_b`, `tst_fzsync_pair`, `tst_fzsync_pair_cleanup`, `tst_fzsync_pair_init`, `tst_fzsync_pair_reset`, `tst_fzsync_run_a`, `tst_fzsync_run_b`, `tst_fzsync_start_race_a`, `tst_fzsync_start_race_b`, `tst_path_val`, `tst_res`, `tst_setup_netns`, `tst_tag`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems; regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/Makefile

Purpose: build glue for the LTP `sendto` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sendto` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c

Purpose: Test Name: sendto01 Test Description: Verify that sendto() returns the proper errno for various failure cases HISTORY 07/2001 Ported by Wayne Boyer In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`. Key structs/tables: `test_case_t`, `tdat`. Important syscall/helper surface includes: `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `select`, `sendto`, `setup`, `setup0`, `setup1`, `setup2`, `setup3`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. table-driven cases are held in `tdat`. important local functions are `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c

Purpose: When SCTP protocol created wih socket(2) and buffer is invalid, sendto(2) should fail and set errno to EFAULT, but it sets errno to ENOMEM. This is a regression test fixed by kernel 3.7 6e51fe757259 (sctp: fix -ENOMEM result with invalid user space pointer in sendto() syscall) In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `verify_sendto`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `TEST`, `TST_ERR`, `TST_RET`, `sendto`, `sets`, `setup`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `verify_sendto`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c

Purpose: CVE-2020-14386 Check for vulnerability in tpacket_rcv() which allows an unprivileged user to write arbitrary data to a memory area outside the allocated packet buffer. Kernel crash fixed in 5.9 acf69c946233 ("net/packet: fix overflow in tpacket_rcv") In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `check_tiny_frame`, `check_vnet_hdr`, `run`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_IOCTL`, `SAFE_SENDTO`, `SAFE_SETSOCKOPT_INT`, `SAFE_SOCKET`, `SAFE_SYSCONF`, `TEST`, `TST_ERR`, `TST_RET`, `TST_SR_SKIP`, `TST_TAINT_D`, `TST_TAINT_W`, `setsockopt`, `setup`, `tst_brk`, `tst_net`, `tst_path_val`, `tst_res`, `tst_setup_netns`, `tst_tag`, `tst_taint_check`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `check_tiny_frame`, `check_vnet_hdr`, `run`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP network helpers, kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/Makefile

Purpose: build glue for the LTP `set_mempolicy` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `set_mempolicy` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy.h

Purpose: Header support for the LTP `set_mempolicy` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `set_mempolicy` tests. Visible symbols include functions none, structs none, arrays none, and helper macros/APIs `SET_MEMPOLICY_H__`, `tse_nodemap`, `tse_nodemap_count_pages`, `tse_numa_fault`, `tse_numa_map`, `tse_numa_unmap`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `set_mempolicy` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c

Purpose: In most cases, set_mempolicy01 finish quickly, but when the platform has multiple NUMA nodes, the test matrix combination grows exponentially and bring about test time to increase extremely fast. Here reset the entire timeout according to the NUMA nodes. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TEST`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`, `numa_allocate_nodemask`, `numa_bitmask_setbit`, `numa_free_nodemask`, `set_mempolicy`, `set_mempolicy01`, `setup`, `tse_get_nodemap`, `tse_mempolicy_mode_name`, `tse_nodemap`, `tse_nodemap_free`, `tse_nodemap_print_counters`, `tse_nodemap_reset_counters`, `tse_numa`, `tst_brk`, `tst_reap_children`, `tst_res`, `tst_set_timeout`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`.

State and persistence behavior: exercises forked child state; NUMA policy and page placement. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on NUMA/libnuma and `tse_numa` helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy02.c

Purpose: We are testing set_mempolicy() with MPOL_INTERLEAVE. The test tries different subsets of memory nodes, sets the mask with memopolicy, and checks that the memory was interleaved between the nodes accordingly. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `alloc_and_check`, `verify_set_mempolicy`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TEST`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`, `numa_allocate_nodemask`, `numa_bitmask_setbit`, `numa_free_nodemask`, `set_mempolicy`, `sets`, `setup`, `tse_get_nodemap`, `tse_nodemap`, `tse_nodemap_free`, `tse_nodemap_reset_counters`, `tse_numa`, `tst_brk`, `tst_reap_children`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `alloc_and_check`, `verify_set_mempolicy`.

State and persistence behavior: exercises forked child state; NUMA policy and page placement. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on NUMA/libnuma and `tse_numa` helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy03.c

Purpose: Exercises NUMA memory policy behavior and architecture-specific compat syscall regression coverage. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TEST`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`, `numa_allocate_nodemask`, `numa_bitmask_setbit`, `numa_free_nodemask`, `set_mempolicy`, `setup`, `tse_get_nodemap`, `tse_mempolicy_mode_name`, `tse_nodemap`, `tse_nodemap_free`, `tse_nodemap_reset_counters`, `tse_numa`, `tst_brk`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`.

State and persistence behavior: exercises NUMA policy and page placement. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on NUMA/libnuma and `tse_numa` helpers, root privileges, LTP all-filesystems mount matrix. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy04.c

Purpose: Exercises NUMA memory policy behavior and architecture-specific compat syscall regression coverage. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `alloc_and_check`, `verify_set_mempolicy`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TEST`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`, `numa_allocate_nodemask`, `numa_bitmask_setbit`, `numa_free_nodemask`, `set_mempolicy`, `setup`, `tse_get_nodemap`, `tse_nodemap`, `tse_nodemap_free`, `tse_nodemap_reset_counters`, `tse_numa`, `tst_brk`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `alloc_and_check`, `verify_set_mempolicy`.

State and persistence behavior: exercises NUMA policy and page placement. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on NUMA/libnuma and `tse_numa` helpers, root privileges, LTP all-filesystems mount matrix. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c

Purpose: reproduces the set_mempolicy 32-bit compat syscall information-leak regression by placing a known byte pattern on the user stack, issuing the compat-style syscall with invalid node-mask arguments, and verifying that the stack pattern is not overwritten before the kernel returns EFAULT or EINVAL. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `set_mempolicy`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`.

State and persistence behavior: exercises user-stack contents, compat syscall argument handling, and NUMA policy validation without creating durable files or changing repository state. The test keeps all observable state in the local stack buffer and syscall return code.

Dependencies and integration points: depends on architecture gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/Makefile

Purpose: build glue for the LTP `set_robust_list` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `set_robust_list` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c

Purpose: Test Name: set_robust_list01 Test Description: Verify that set_robust_list() returns the proper errno for various failure cases Usage: <for command-line> set_robust_list01 [-c n] [-e][-i n] [-I x] [-p x] [-t] where, -c n : Run n copies concurrently. -e : Turn on errno logging. -i n : Execute test n times. -I x : Execute test for x seconds. -P x : Pause for x seconds between iterations. -t : Turn on syscall timing. History 07/2008 Ramon de Carvalho Valle <rcvalle@br.ibm.com> -Created Restrictions: None. In this shard it contributes focused coverage for robust futex list syscall errno validation.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: `robust_list`, `robust_list_head`. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `set_robust_list`, `set_robust_list01`, `setup`, `tst_count`, `tst_parse_opts`, `tst_resm`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/Makefile

Purpose: build glue for the LTP `set_thread_area` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `set_thread_area` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area01.c

Purpose: Basic test of i386 thread-local storage for set_thread_area and get_thread_area syscalls. It verifies a simple write and read of an entry works. [Algorithm] - Call set_thread_area to a struct user_desc pointer with entry_number = -1, which will be set to a free entry_number upon exiting. - Call get_thread_area to read the new entry. - Use the new entry_number in another pointer and call get_thread_area. - Make sure they have the same data. In this shard it contributes focused coverage for i386 TLS descriptor set/get ABI validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`, `set_thread_area`, `setup`, `tst_buffers`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on architecture gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_PASS. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area02.c

Purpose: Exercises i386 TLS descriptor set/get ABI validation. In this shard it contributes focused coverage for i386 TLS descriptor set/get ABI validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `set_thread_area`, `setup`, `tst_buffers`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on architecture gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_thread_area/set_thread_area02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/Makefile

Purpose: build glue for the LTP `set_tid_address` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `set_tid_address` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/set_tid_address01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/set_tid_address01.c

Purpose: Copyright (c) Crackerjack Project., 2007 Copyright (c) Linux Test Project, 2007-2024 In this shard it contributes focused coverage for set_tid_address return value and child-clear-tid pointer registration.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_set_tid_address`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_VAL`, `set_tid_address`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_set_tid_address`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_tid_address/set_tid_address01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/Makefile

Purpose: build glue for the LTP `setdomainname` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setdomainname` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname.h

Purpose: Header support for the LTP `setdomainname` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `setdomainname` tests. Visible symbols include functions `setdomainname_info`, `do_setdomainname`, `setup`, `cleanup`, structs none, arrays none, and helper macros/APIs `GET_SYSCALL`, `SETDOMAINNAME_H__`, `SET_SYSCALL`, `TST_VALID_DOMAIN_NAME`, `setdomainname`, `setdomainname_info`, `sethostname`, `setup`, `tst_brk`, `tst_res`, `tst_syscall`, `tst_test`, `tst_variant`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `setdomainname` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname01.c

Purpose: Exercises domain-name setting wrapper shared with sethostname tests. In this shard it contributes focused coverage for domain-name setting wrapper shared with sethostname tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_test`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GET_SYSCALL`, `TEST`, `TST_ERR`, `TST_RET`, `TST_VALID_DOMAIN_NAME`, `setdomainname`, `setup`, `tst_brk`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_test`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname02.c

Purpose: Exercises domain-name setting wrapper shared with sethostname tests. In this shard it contributes focused coverage for domain-name setting wrapper shared with sethostname tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setdomainname`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `TEST`, `TST_ERR`, `TST_RET`, `TST_VALID_DOMAIN_NAME`, `setdomainname`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setdomainname`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname03.c

Purpose: Exercises domain-name setting wrapper shared with sethostname tests. In this shard it contributes focused coverage for domain-name setting wrapper shared with sethostname tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_test`, `setup_setuid`, `cleanup_setuid`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TEST`, `TST_ERR`, `TST_RET`, `TST_VALID_DOMAIN_NAME`, `setdomainname`, `setup`, `setup_setuid`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_test`, `setup_setuid`, `cleanup_setuid`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setdomainname/setdomainname03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setegid/Makefile

Purpose: build glue for the LTP `setegid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setegid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid01.c

Purpose: Verify that setegid() sets the effective UID of the calling process correctly, and does not modify the saved GID and real GID. In this shard it contributes focused coverage for effective group ID update behavior for privileged and unprivileged callers.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `setegid_verify`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_GETRESGID`, `SAFE_SETEGID`, `TST_EXP_EQ_LU`, `setegid`, `setegid_verify`, `sets`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `setegid_verify`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_EQ, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c

Purpose: Verify that setegid() fails with EPERM when the calling process is not privileged and egid does not match the current real group ID, current effective group ID, or current saved set-group-ID. In this shard it contributes focused coverage for effective group ID update behavior for privileged and unprivileged callers.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `setegid_verify`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`, `setegid`, `setegid_verify`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `setegid_verify`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/Makefile

Purpose: build glue for the LTP `setfsgid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setfsgid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid01.c

Purpose: Verify that setfsgid() correctly updates the filesystem group ID to the value given in fsgid argument. In this shard it contributes focused coverage for filesystem group ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETFSGID`, `TST_EXP_VAL`, `TST_EXP_VAL_SILENT`, `setfsgid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c

Purpose: Testcase for setfsgid() syscall to check that - privileged user can change a filesystem group ID different from saved value of previous setfsgid() call - unprivileged user cannot change it In this shard it contributes focused coverage for filesystem group ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETFSGID`, `TEST`, `TST_RET`, `setfsgid`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c

Purpose: Testcase to check the basic functionality of setfsgid(2) system call fails when called by a non-root user. In this shard it contributes focused coverage for filesystem group ID transitions and permission side effects.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETFSGID`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setfsgid`, `setfsgid03`, `setuid`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TEST_RETURN, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/Makefile

Purpose: build glue for the LTP `setfsuid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setfsuid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid01.c

Purpose: Verify that setfsuid() correctly updates the filesystem user ID to the value given in fsuid argument. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETFSUID`, `TST_EXP_VAL`, `setfsuid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid02.c

Purpose: Verify that setfsuid() syscall fails if an invalid fsuid is given. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETFSUID`, `TST_EXP_VAL`, `TST_EXP_VAL_SILENT`, `setfsuid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c

Purpose: Verify that setfsuid() correctly updates the filesystem uid when caller is a non-root user and provided fsuid matches caller's real user ID. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_GETRESUID`, `SAFE_SETEUID`, `SETFSUID`, `TST_EXP_VAL`, `TST_EXP_VAL_SILENT`, `setfsuid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c

Purpose: Check if setfsuid behaves correctly with file permissions. The test creates a file as ROOT with permissions 0644, does a setfsuid and then tries to open the file with RDWR permissions. The same test is done in a fork to check if new UIDs are correctly passed to the son. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `do_master_child`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_OPEN`, `SETFSUID`, `TEST`, `TST_TOTAL`, `setfsuid`, `setfsuid04`, `setfsuid04_testfile`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_record_childstatus`, `tst_require_root`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `do_master_child`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgid/Makefile

Purpose: build glue for the LTP `setgid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setgid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid01.c

Purpose: Exercises real/effective group ID setting and EPERM handling. In this shard it contributes focused coverage for real/effective group ID setting and EPERM handling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETGID`, `TST_EXP_PASS`, `setgid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_PASS. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c

Purpose: Test if setgid() system call sets errno to EPERM correctly. [Algorithm] Call setgid() to set the gid to that of root. Run this test as nobody, and expect to get EPERM. In this shard it contributes focused coverage for real/effective group ID setting and EPERM handling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_SETUID`, `SETGID`, `TST_EXP_FAIL`, `setgid`, `sets`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid03.c

Purpose: [Algorithm] As a root sets current group id to nobody and expects success. In this shard it contributes focused coverage for real/effective group ID setting and EPERM handling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SETGID`, `TST_EXP_PASS`, `setgid`, `sets`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/Makefile

Purpose: build glue for the LTP `setgroups` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setgroups` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups01.c

Purpose: Copyright (c) 2000 Silicon Graphics, Inc. All Rights Reserved. Copyright (c) Linux Test Project, 2003-2023 Author: William Roske CO-PILOT: Dave Fenner In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setgroups`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETGROUPS`, `SETGROUPS`, `TST_EXP_POSITIVE`, `setgroups`, `setup`, `tst_brk`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setgroups`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through compile success and absence of unexpected syscall errors. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c

Purpose: Copyright (c) International Business Machines Corp., 2001 Copyright (c) Linux Test Project, 2003-2023 07/2001 Ported by Wayne Boyer In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setgroups`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETGROUPS`, `SETGROUPS`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_VAL`, `setgroups`, `tst_buffers`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setgroups`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ, TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c

Purpose: Test for EINVAL, EPERM, EFAULT errors. - setgroups() fails with EINVAL if the size argument value is > NGROUPS. - setgroups() fails with EPERM if the calling process is not super-user. - setgroups() fails with EFAULT if the list has an invalid address. In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setgroups`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETGROUPS`, `TST_EXP_FAIL`, `setgroups`, `setup`, `tst_buffers`, `tst_get_bad_addr`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setgroups`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c

Purpose: Test Name: setgroups04 Test Description: Verify that, setgroups() fails with -1 and sets errno to EFAULT if the list has an invalid address. Expected Result: setgroups() should fail with return value -1 and set expected errno. Algorithm: Setup: Setup signal handling. Pause for SIGUSR1 if option specified. Test: Loop if the proper options are given. Execute system call Check return code, if system call failed (return=-1) if errno set == expected errno Issue sys call fails with expected return value and errno. Otherwise, Issue sys call fails with unexpected errno. Otherwise, Issue sys call returns unexpected value. In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETGROUPS`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setgroups`, `setgroups04`, `sets`, `setup`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sethostname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sethostname/Makefile

Purpose: build glue for the LTP `sethostname` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `sethostname` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sethostname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/Makefile

Purpose: build glue for the LTP `setitimer` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setitimer` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c

Purpose: Spawn a child, verify that setitimer() syscall passes and it ends up counting inside expected boundaries. Then verify from the parent that the syscall sent the correct signal to the child. In this shard it contributes focused coverage for interval timer setup, signal delivery, old kernel itimerval ABI, and errno behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `sig_routine`, `set_setitimer_value`, `verify_setitimer`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_CLOCK_GETRES`, `SAFE_FORK`, `SAFE_SIGNAL`, `SAFE_WAITPID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `set_setitimer_value`, `setitimer`, `setup`, `tst_brk`, `tst_buffers`, `tst_no_corefile`, `tst_res`, `tst_safe_clocks`, `tst_strsig`, `tst_strstatus`, `tst_test`, `tst_timer`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `sig_routine`, `set_setitimer_value`, `verify_setitimer`, `setup`.

State and persistence behavior: exercises forked child state; interval timers and signals. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers, LTP syscall-number wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c

Purpose: Check that setitimer() call fails: 1. EFAULT with invalid itimerval pointer 2. EINVAL when called with an invalid first argument In this shard it contributes focused coverage for interval timer setup, signal delivery, old kernel itimerval ABI, and errno behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setitimer`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_FAIL`, `setitimer`, `setup`, `tst_buffers`, `tst_test`, `tst_timer`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setitimer`, `setup`.

State and persistence behavior: exercises interval timers and signals. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers, LTP syscall-number wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/Makefile

Purpose: build glue for the LTP `setns` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setns` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h

Purpose: Copyright (c) Linux Test Project, 2014-2020

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `setns` tests. Visible symbols include functions `get_ns_fd`, `init_ns_type`, `init_available_ns`, `close_ns_fds`, structs none, arrays none, and helper macros/APIs `SAFE_CLOSE`, `SAFE_OPEN`, `tst_brk`, `tst_res`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `setns` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns01.c

Purpose: Copyright (c) Linux Test Project, 2014-2020 errno tests for setns(2) - reassociate thread with a namespace In this shard it contributes focused coverage for namespace fd discovery and setns error/functional tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup0`, `setup1`, `setup2`, `setup3`, `setup4`, `cleanup4`, `test_setns`, `setup`, `cleanup`. Key structs/tables: `testcase_t`, `tcases`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_GETPWNAM`, `SAFE_OPEN`, `SAFE_SETEUID`, `SAFE_UNLINK`, `setns`, `setup`, `setup0`, `setup1`, `setup2`, `setup3`, `setup4`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `tcases`. important local functions are `setup0`, `setup1`, `setup2`, `setup3`, `setup4`, `cleanup4`, `test_setns`, `setup`, `cleanup`.

State and persistence behavior: exercises temporary files or descriptors; namespace membership. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c

Purpose: Copyright (c) Linux Test Project, 2014-2020 functional test for setns(2) - reassociate thread with a namespace 1. create child with CLONE_NEWUTS, set different hostname in child, set namespace back to parent ns and check that hostname has changed 2. create child with CLONE_NEWIPC, set up shared memory in parent and verify that child can't shmat it, then set namespace back to parent one and verify that child is able to do shmat In this shard it contributes focused coverage for namespace fd discovery and setns error/functional tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_child_newuts`, `do_child_newipc`, `test_flag`, `test_all`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_GETCWD`, `SAFE_MALLOC`, `SAFE_SHMCTL`, `SAFE_SHMGET`, `SAFE_WAITPID`, `sethostname`, `setns`, `setns_dummy_uts`, `setup`, `tst_brk`, `tst_res`, `tst_safe_sysv_ipc`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_child_newuts`, `do_child_newipc`, `test_flag`, `test_all`, `setup`, `cleanup`.

State and persistence behavior: exercises namespace membership. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/Makefile

Purpose: build glue for the LTP `setpgid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setpgid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c

Purpose: Verify basic setpgid() functionality, re-setting group ID inside both parent and child. In the first case, we obtain getpgrp() and set it. In the second case, we use setpgid(0, 0). In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setpgid_test1`, `setpgid_test2`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_PID`, `setpgid`, `setpgid_test1`, `setpgid_test2`, `setting`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setpgid_test1`, `setpgid_test2`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c

Purpose: Verify that setpgid(2) syscall fails with: - EINVAL when given pgid is less than 0. - ESRCH when pid is not the calling process and not a child of the calling process. - EPERM when an attempt was made to move a process into a nonexisting process group. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FILE_SCANF`, `TST_EXP_FAIL`, `setpgid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c

Purpose: Exercises process group mutation, session/exec restrictions, and checkpointed parent-child races. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_child`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_EXECLP`, `SAFE_FORK`, `SAFE_SETSID`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_EXP_FAIL`, `setpgid`, `setpgid03_child`, `setsid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_child`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c

Purpose: Exercises process group mutation, session/exec restrictions, and checkpointed parent-child races. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses mixed direct syscall and LTP helper API. Key local functions: `main`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_NO_DEFAULT_MAIN`, `tst_reinit`, `tst_test`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through compile success and absence of unexpected syscall errors. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/Makefile

Purpose: build glue for the LTP `setpgrp` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setpgrp` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp01.c

Purpose: TEST CASE: Call the setpgrp system call In this shard it contributes focused coverage for legacy and modern process group creation smoke tests.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setpgrp`, `setpgrp01`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c

Purpose: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer Copyright (c) Linux Test Project, 2001-2016 Copyright (C) 2024 SUSE LLC Andrea Manzini <andrea.manzini@suse.com> In this shard it contributes focused coverage for legacy and modern process group creation smoke tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setpgrp`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS`, `setpgrp`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setpgrp`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile

Purpose: build glue for the LTP `setpriority` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setpriority` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority01.c

Purpose: Verify that setpriority(2) succeeds set the scheduling priority of the current process, process group or user. In this shard it contributes focused coverage for nice priority setting by process, process group, and user plus permission errors.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setpriority_test`, `verify_setpriority`, `setup`, `cleanup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPRIORITY`, `SAFE_GETPWNAM`, `SAFE_SETPGID`, `SAFE_SETUID`, `TEST`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_CMD_PASS_RETVAL`, `TST_RET`, `setpriority`, `setpriority_test`, `setup`, `tst_brk`, `tst_cmd`, `tst_reap_children`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setpriority_test`, `verify_setpriority`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c

Purpose: Verify that, 1) setpriority(2) fails with -1 and sets errno to EINVAL if 'which' argument was not one of PRIO_PROCESS, PRIO_PGRP, or PRIO_USER. 2) setpriority(2) fails with -1 and sets errno to ESRCH if no process was located for 'which' and 'who' arguments. 3) setpriority(2) fails with -1 and sets errno to EACCES if an unprivileged user attempted to lower a process priority. 4) setpriority(2) fails with -1 and sets errno to EPERM if an unprivileged user attempted to change a process which ID is different from the test process. In this shard it contributes focused coverage for nice priority setting by process, process group, and user plus permission errors.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setpriority_test`, `verify_setpriority`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETPGID`, `SAFE_SETUID`, `TEST`, `TST_ERR`, `TST_RET`, `setpriority`, `setpriority_test`, `sets`, `setup`, `tst_reap_children`, `tst_res`, `tst_strerrno`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setpriority_test`, `verify_setpriority`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/Makefile

Purpose: build glue for the LTP `setregid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setregid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid01.c

Purpose: Verify the basic functionality of setregid(2) system call. In this shard it contributes focused coverage for real/effective group ID transitions and saved-id semantics.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SETREGID`, `TST_EXP_PASS`, `setregid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_EXP_PASS. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c

Purpose: Test that setregid() fails and sets the proper errno values when a non-root user attemps to change the real or effective group id to a value other than the current gid or the current effective gid. In this shard it contributes focused coverage for real/effective group ID transitions and saved-id semantics.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `gid_verify`, `run`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_SETUID`, `SETREGID`, `TEST`, `TST_ERR`, `TST_RET`, `setregid`, `sets`, `setup`, `tst_get_gids`, `tst_res`, `tst_strerrno`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `gid_verify`, `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid03.c

Purpose: Test setregid() when executed by a non-root user. In this shard it contributes focused coverage for real/effective group ID transitions and saved-id semantics.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `test_success`, `test_failure`, `gid_verify`, `run`, `run_all`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_SETREGID`, `SETREGID`, `TEST`, `TST_ERR`, `TST_RET`, `setregid`, `setup`, `tst_get_gids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `test_success`, `test_failure`, `gid_verify`, `run`, `run_all`.

State and persistence behavior: exercises forked child state; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid04.c

Purpose: The following structure contains all test data. Each structure in the array is used for a separate test. The tests are executed in the for loop below. In this shard it contributes focused coverage for real/effective group ID transitions and saved-id semantics.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `gid_verify`, `run`, `setup`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SETREGID`, `TEST`, `TST_RET`, `setregid`, `setup`, `tst_get_gids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `gid_verify`, `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/Makefile

Purpose: build glue for the LTP `setresgid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setresgid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid01.c

Purpose: Verify that setresgid() syscall correctly sets real user ID, effective user ID and the saved set-user ID in the calling process. In this shard it contributes focused coverage for real/effective/saved group ID transitions and filesystem GID coupling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `tcase`, `tcases`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_GETRESGID`, `SETRESGID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_PASS`, `setresgid`, `sets`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `tcases`. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c

Purpose: Verify that setresgid() will successfully set the expected GID when called by root with the following combinations of arguments: - setresgid(-1, -1, -1) - setresgid(-1, -1, other) - setresgid(-1, other, -1) - setresgid(other, -1, -1) - setresgid(root, root, root) - setresgid(root, main, main) In this shard it contributes focused coverage for real/effective/saved group ID transitions and filesystem GID coupling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`, `test_cases`. Important syscall/helper surface includes: `SAFE_SETRESGID`, `SETRESGID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setresgid`, `setup`, `tst_check_resgid`, `tst_get_gids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `test_cases`. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid03.c

Purpose: Verify that setresgid() fails with EPERM if unprivileged user tries to set process group ID which requires higher permissions. In this shard it contributes focused coverage for real/effective/saved group ID transitions and filesystem GID coupling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`, `test_cases`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETRESGID`, `SAFE_SETUID`, `SETRESGID`, `TST_EXP_FAIL`, `TST_PASS`, `setresgid`, `setup`, `tst_check_resgid`, `tst_get_gids`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `test_cases`. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid04.c

Purpose: Verify that setresgid() syscall always sets the file system GID to the same value as the new effective GID. In this shard it contributes focused coverage for real/effective/saved group ID transitions and filesystem GID coupling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_STAT`, `SAFE_TOUCH`, `SETRESGID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `setresgid`, `sets`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/Makefile

Purpose: build glue for the LTP `setresuid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setresuid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid01.c

Purpose: Test setresuid() when executed by root. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SETRESUID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setresuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c

Purpose: Test that a non-root user can change the real, effective and saved uid values through the setresuid system call. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETRESUID`, `SETRESUID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setresuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid03.c

Purpose: Test that the setresuid system call sets the proper errno values when a non-root user attempts to change the real, effective or saved uid to a value other than one of the current uid, the current effective uid or the current saved uid. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_SETRESUID`, `SETRESUID`, `TST_EXP_FAIL`, `TST_PASS`, `setresuid`, `sets`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid04.c

Purpose: Verify that setresuid() behaves correctly with file permissions. The test creates a file as ROOT with permissions 0644, does a setresuid to change euid to a non-root user and tries to open the file with RDWR permissions, which should fail with EACCES errno. The same test is done in a fork also to check that child process also inherits new euid and open fails with EACCES. Test verifies the successful open action after reverting the euid back ROOT user. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_OPEN`, `SAFE_WAITPID`, `SETRESUID`, `TST_EXP_FAIL2`, `TST_EXP_FD`, `TST_EXP_PASS_SILENT`, `TST_RET`, `setresuid`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_FAIL, TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid05.c

Purpose: Verify that after updating euid with setresuid(), any file creation also gets the new euid as its owner user ID. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_STAT`, `SAFE_TOUCH`, `SAFE_UNLINK`, `SETRESUID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`, `setresuid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/Makefile

Purpose: build glue for the LTP `setreuid` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setreuid` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid01.c

Purpose: Verify the basic functionality of setreuid(2) system call when executed as non-root user. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETREUID`, `TST_EXP_PASS`, `setreuid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid02.c

Purpose: Test setreuid() when executed by root. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETUID`, `SETREUID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setreuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid03.c

Purpose: Test setreuid() when executed by an unpriviledged user. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETUID`, `SETREUID`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_PASS`, `setreuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c

Purpose: Verify that root user can change the real and effective uid to an unprivileged user. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETEUID`, `GETUID`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SETREUID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `setreuid`, `setup`, `tst_reap_children`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises forked child state; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid05.c

Purpose: Test the setreuid() feature, verifying the role of the saved-set-uid and setreuid's effect on it. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run_child`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETUID`, `SETREUID`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_PASS`, `setreuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_reap_children`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run_child`, `run`.

State and persistence behavior: exercises forked child state; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid06.c

Purpose: Verify that setreuid(2) syscall fails with EPERM errno when the calling process is not privileged and a change other than (i) swapping the effective user ID with the real user ID, or (ii) setting one to the value of the other or (iii) setting the effective user ID to the value of the saved set-user-ID was specified. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETUID`, `SETREUID`, `TST_EXP_FAIL`, `setreuid`, `setting`, `setup`, `tst_get_uids`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid07.c

Purpose: Check if setreuid behaves correctly with file permissions. The test creates a file as ROOT with permissions 0644, does a setreuid and then tries to open the file with RDWR permissions. The same test is done in a fork to check if new UIDs are correctly passed to the child process. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_OPEN`, `SETREUID`, `TST_EXP_FAIL2`, `TST_EXP_FD`, `TST_EXP_PASS_SILENT`, `TST_RET`, `setreuid`, `setup`, `tst_reap_children`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_FAIL, TST_RET. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/Makefile

Purpose: build glue for the LTP `setrlimit` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setrlimit` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit01.c

Purpose: Spawn a child process, and reduce the filesize to 10 by calling setrlimit(). We can't do this in the parent, because the parent needs a bigger filesize as its output will be saved to the logfile (instead of stdout) when the testcase (parent) is run from the driver. In this shard it contributes focused coverage for resource limit behavior for file descriptors, file size, process count, and core dumps.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `test1`, `test2`, `test3`, `test4`, `sighandler`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETRLIMIT`, `SAFE_PIPE`, `SAFE_WAITPID`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setrlimit`, `setrlimit01`, `setrlimit1`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `test1`, `test2`, `test3`, `test4`, `sighandler`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; resource limits. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TEST_RETURN, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit01.c -->
