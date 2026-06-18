# Research Report: subset-b-006840

This grouped report covers the requested Linux kselftest and KVM selftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests`. Each section is bounded with `BEGIN_FILE_RESEARCH` / `END_FILE_RESEARCH` markers so it can be split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness.h

Purpose: this header implements the C unit-test harness used by Linux kselftests. It gives tests a gtest-like API with `TEST`, `TEST_SIGNAL`, `FIXTURE`, `FIXTURE_SETUP`, `FIXTURE_TEARDOWN`, `FIXTURE_VARIANT`, `TEST_F`, timeout variants, `ASSERT_*`, `EXPECT_*`, `SKIP`, `TH_LOG`, `XFAIL_ADD`, and `TEST_HARNESS_MAIN`. It emits TAP/kselftest output via `kselftest.h` and bridges low-level kselftest result codes with structured per-test execution.

Important APIs, types, and functions: public macros expand into static test functions, constructor-registered metadata objects, and fixture wrappers. Internal types include `__fixture_metadata`, `__fixture_variant_metadata`, `__test_metadata`, `__test_results`, and `__test_xfail`. Core helpers are `__register_fixture()`, `__register_fixture_variant()`, `__register_test()`, `__register_xfail()`, `__bail()`, `__wait_for_test()`, `test_harness_argv_check()`, `test_enabled()`, `__run_test()`, and `test_harness_run()`.

Control flow: compile-time macros create constructor functions that build fixture/test/xfail lists. `test_harness_run()` validates CLI filters, counts enabled fixture-variant-test combinations, prints the plan, allocates shared result state with `mmap`, and invokes `__run_test()` for each enabled test. `__run_test()` forks an isolated child, resets ksft state, runs the registered wrapper, waits through a pidfd/poll timeout path, classifies normal exit/signals/expected-failure state, and prints the result. Fixture tests have an extra grandchild so setup/test/teardown isolation can support child teardown or parent teardown.

State and persistence: state is process-local and mostly static. Constructor-linked lists persist for the test binary lifetime. Per-test metadata, fixture data, `no_teardown`, and result reasons may be `MAP_SHARED` so forked children can communicate result codes and skip reasons back to the parent. No durable files are written by the harness itself.

Dependencies and integration points: depends on libc/POSIX process APIs, `pidfd_open`, `poll`, `waitpid`, `mmap`, signals, and `kselftest.h` result helpers. It integrates with kselftest runner semantics, TAP output, shell runners, and compiler constructor ordering.

Risks: macro expansion is powerful but hard to debug, constructor ordering is toolchain-sensitive, and tests are explicitly not parallel within one process. The timeout path kills the child process group, so tests that modify process groups or fork further need care. Direct use of low-level `ksft_test_result_*()` inside harness tests is checked and can be treated as illegal unless encoded by exit code.

Test signals: `-l`, filtering flags, timeout behavior, signal-expected tests, XFAIL/XPASS conversion, fixture setup failure, fixture teardown-in-parent, and `SKIP` reasons are the main observable signals. `harness-selftest.c` and `harness-selftest.sh` provide a golden-output regression check for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/Makefile

Purpose: this small kselftest makefile defines the build and run artifacts for the harness selftest.

Important APIs and variables: `TEST_GEN_PROGS_EXTENDED := harness-selftest` builds the C binary but does not make it a direct default program test. `TEST_PROGS := harness-selftest.sh` makes the shell wrapper the test entry point. `TEST_FILES := harness-selftest.expected` installs the golden output file alongside the script. `EXTRA_CLEAN := harness-selftest.seen` removes the captured output. `include ../lib.mk` delegates standard kselftest build, install, and clean behavior.

Control flow: kselftest make infrastructure compiles `harness-selftest` from `harness-selftest.c`, installs the expected-output file, and runs `harness-selftest.sh`. The shell wrapper executes the binary, captures output, and diffs it against the expected fixture.

State and persistence: generated state is limited to the compiled binary and `harness-selftest.seen`; both are build artifacts, not source state. The expected output is treated as a test fixture.

Dependencies and integration points: depends on the selftests `lib.mk` convention for `TEST_GEN_PROGS_EXTENDED`, `TEST_PROGS`, `TEST_FILES`, and `EXTRA_CLEAN`. It integrates with `make kselftest`, `make install`, and the top-level selftest runner.

Risks: if the expected file is missing or harness output changes intentionally, the shell test fails until the fixture is updated. Marking the C binary as extended is important because running it directly is expected to produce failing cases as part of the golden transcript.

Test signals: a passing run is a clean `diff -u` between `harness-selftest.expected` and `harness-selftest.seen`; any stdout formatting drift, TAP count change, timeout change, or result-code classification change appears as a diff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.c

Purpose: this C program is the behavioral regression test for `kselftest_harness.h`. It deliberately defines passing, failing, signal, fixture, timeout, exit-code, and low-level result-code tests so the harness output can be compared with a golden file.

Important APIs and functions: it includes `kselftest_harness.h` after forcing `TH_LOG_STREAM stdout` for deterministic output. It defines `test_helper()`, standalone `TEST()` cases, `TEST_SIGNAL()` cases, fixture-based `TEST_F()` cases, `TEST_F_TIMEOUT()`, fixtures with normal child teardown and parent teardown, a setup-failure fixture, tests exiting with `KSFT_*` codes, and tests calling `ksft_test_result_*()` helpers. `main()` disables dumpability/core dumps, sets `RLIMIT_CORE` to zero, and calls `test_harness_run()`.

Control flow: constructors from the harness register all tests, then `main()` runs them through the standard harness. Several cases intentionally fail or abort so the harness exercises failure classification. The timeout test sleeps longer than its one-second timeout. The signal tests verify expected-signal handling. Fixture tests show setup, teardown, and same-process/parent-process teardown behavior.

State and persistence: no durable state is stored. The only process state change is disabling core dumps to keep intentional `abort()` assertions from producing core files. Fixture state stores `pid_t testpid` to validate where teardown runs.

Dependencies and integration points: depends on POSIX resource/prctl APIs and the harness header. It is not meant to be interpreted by its binary exit code alone; the companion shell script captures stdout and compares it against `harness-selftest.expected`.

Risks: because failures are intentional, running the binary directly can look alarming. Changes in line numbers, logging format, or output stream routing will alter the golden output. The test also validates that low-level ksft result functions are not misused from inside harness tests, so harness internals and public kselftest APIs are coupled here.

Test signals: expected output contains PASS, FAIL, SKIP, XFAIL, XPASS, timeout, assertion, and signal cases. The key signal is whether the full transcript remains stable and whether `test_harness_run()` returns the expected aggregate failure status consumed by the shell wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.sh

Purpose: this shell script is the executable kselftest entry point for the harness selftest. It normalizes execution through a wrapper so the intentionally failing C test binary can still be judged by output comparison.

Important APIs and commands: it uses `/bin/sh`, `set -e`, `readlink -f "$0"` to locate its directory, runs `"$DIR"/harness-selftest > harness-selftest.seen || true`, and then invokes `diff -u "$DIR"/harness-selftest.expected harness-selftest.seen`.

Control flow: the script resolves the directory containing itself, executes the compiled `harness-selftest` binary while capturing stdout into `harness-selftest.seen`, ignores the binary's nonzero exit status because failures are intentional, and fails or passes based on the unified diff result.

State and persistence: it creates or overwrites `harness-selftest.seen` in the current working directory, not necessarily in `$DIR`. The Makefile lists this file in `EXTRA_CLEAN`. No other state is kept.

Dependencies and integration points: depends on the compiled binary and `harness-selftest.expected` being installed together by the Makefile. It integrates with kselftest as `TEST_PROGS`, so runner status comes from the shell script's `diff` result.

Risks: writing `harness-selftest.seen` relative to the caller can be surprising if the runner changes cwd. Output comparison is intentionally brittle to catch format regressions; harmless whitespace or line-number shifts can fail the test.

Test signals: successful execution produces no diff output and exits zero. Any harness behavior change appears as a `diff -u` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_install.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_install.sh

Purpose: this helper installs kselftest artifacts by invoking the selftests make install target with `KSFT_INSTALL_PATH` set.

Important APIs and functions: `main()` computes `base_dir=\`pwd\``, defaults `install_dir` to `$base_dir/kselftest_install`, verifies the current directory basename is `selftests`, optionally accepts an existing destination directory argument, and runs `KSFT_INSTALL_PATH="$install_dir" make install`.

Control flow: the script rejects execution outside the selftests top-level directory. With no argument it announces and uses a default install directory under the current tree. With one argument it requires that path to exist, then uses it. It delegates all actual build/install work to `make install`.

State and persistence: it writes no files directly. Persistence is produced by the Makefile install target under `KSFT_INSTALL_PATH`. Its own state is only shell variables.

Dependencies and integration points: depends on Bash, `pwd`, `basename`, a make-capable selftests tree, and the top-level selftests install rules. It is an integration shim for packaging/running selftests outside the source tree.

Risks: it refuses to create a user-specified directory, so automation must pre-create the destination. The default path is inside the source tree, which can dirty the worktree if used casually. The basename check is simple and can reject symlinked or unusual layouts.

Test signals: visible signals are printed install-location messages, an immediate exit with status 1 when cwd/destination validation fails, or the propagated `make install` result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_module.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_module.h

Purpose: this header provides a compact framework for kernel-module selftests loaded by kselftest. It lets a module count test cases, report failures/skips, taint the kernel as tested, and expose module metadata.

Important APIs and macros: `KSTM_MODULE_GLOBALS()` declares `total_tests`, `failed_tests`, and `skipped_tests` as `__initdata`. `KSTM_CHECK_ZERO(x)` increments total tests and records a failure when `x` is nonzero. `kstm_report()` prints pass/skip/fail summaries and returns `-EINVAL` on failure. `KSTM_MODULE_LOADERS(__module)` emits module init/exit functions that call `selftest()`, add `TAINT_TEST`, report results, and register with `module_init()` / `module_exit()`. `MODULE_INFO(test, "Y")` marks the module as a test.

Control flow: a test module includes the header, defines `selftest()`, calls `KSTM_MODULE_GLOBALS()`, uses `KSTM_CHECK_ZERO()` in its checks, and uses `KSTM_MODULE_LOADERS(name)` to wire module load/unload. Loading the module runs tests synchronously from the init function and returns success or `-EINVAL`.

State and persistence: counters live only during module initialization because they are `__initdata`; no persistent state is stored. Loading the module taints the running kernel with `TAINT_TEST`, which is an intentional global diagnostic state.

Dependencies and integration points: depends on Linux kernel module APIs, `pr_info`, `pr_warn`, `add_taint`, `TAINT_TEST`, `LOCKDEP_STILL_OK`, and a module-provided `selftest()` symbol. It integrates with kselftest module loaders and kernel taint/reporting infrastructure.

Risks: the framework is intentionally minimal; skipped tests must be counted manually, failure checks only test zero/nonzero expressions, and returning failure from module init can unload the test immediately. Because it taints the kernel, it should be used only for test modules.

Test signals: kernel log output reports all-passed, skipped-plus-passed, or failed counts. Module load status is the machine-readable pass/fail signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/Makefile

Purpose: this top-level KVM selftests makefile selects supported architectures and delegates the real build to `Makefile.kvm`.

Important APIs and variables: `top_srcdir = ../../../..`, `include $(top_srcdir)/scripts/subarch.include`, `ARCH ?= $(SUBARCH)`, an `ifeq` filter for `arm64 s390 riscv x86 x86_64 loongarch`, a compatibility rewrite from `x86_64` to `x86`, and `include Makefile.kvm`. Unsupported architectures get empty `all` and `clean` targets.

Control flow: make determines `ARCH`, normalizes x86_64 to x86, and includes the shared KVM selftest rules only when the architecture is supported. Otherwise the targets are no-ops, allowing top-level selftest builds to proceed without hard failure on unsupported hosts.

State and persistence: no direct file state is created in this makefile. Build artifacts and generated test binaries are controlled by `Makefile.kvm` and lower-level rules.

Dependencies and integration points: integrates with kernel scripts/subarch detection, top-level selftests make recursion, and architecture-specific KVM selftest source lists in `Makefile.kvm`.

Risks: architecture normalization is required because the top-level selftests interface may pass `ARCH=x86_64`, while KVM selftests expect `x86`. Adding a supported architecture requires updating this filter and the delegated build rules. Unsupported architectures silently no-op, which is intentional but can hide misconfigured builds.

Test signals: on supported architectures the presence and result of `Makefile.kvm` targets are the signal; on unsupported architectures successful no-op `all`/`clean` confirms graceful exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/access_tracking_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/access_tracking_perf_test.c

Purpose: this KVM performance selftest measures the cost of access tracking when guest memory is aged through page-idle tracking or MGLRU. It times guest reads/writes to populated memory and aged memory across configurable guest modes, memory backings, vCPU counts, and overlapped/disjoint memory regions.

Important APIs, types, and functions: `struct test_params` holds backing source, bytes per vCPU, and vCPU count. Host helpers include `lookup_pfn()`, `is_page_idle()`, `mark_page_idle()`, `pageidle_mark_vcpu_memory_idle()`, `lru_gen_mark_memory_idle()`, `assert_ucall()`, `vcpu_thread_main()`, `run_iteration()`, `access_memory()`, `mark_memory_idle()`, `run_test()`, `access_tracking_unreliable()`, and `run_test_for_each_guest_mode()`. It uses `memstress`, `guest_modes`, `cgroup_util`, and `lru_gen_util`.

Control flow: `main()` parses `-m`, `-b`, `-v`, `-o`, `-s`, and `-w`, chooses MGLRU if usable or falls back to `/sys/kernel/mm/page_idle/bitmap`, optionally creates/runs inside a memory cgroup, and iterates guest modes. `run_test()` creates a memstress VM, starts vCPU worker threads, populates memory, optionally primes MGLRU generations, measures read/write control passes, ages memory, and measures idle-memory read/write passes. Worker threads spin on a global `iteration` counter and either run the vCPU or mark their memory idle.

State and persistence: global synchronization state includes `iteration`, `iteration_work`, per-vCPU completion counters, `idle_pages_warn_only`, `use_lru_gen`, `test_pages`, and `lru_gen_last_gen`. It creates/destroys a memory cgroup for MGLRU mode and touches debugfs/sysfs/proc state. No test data is persisted beyond cgroup cleanup.

Dependencies and integration points: requires KVM, memstress helpers, guest mode support, `page_idle` or MGLRU debugfs, `/proc/self/pagemap`, and often `CAP_SYS_ADMIN` for PFNs. It integrates with NUMA balancing detection and nested-virtualization heuristics to downgrade some idle-page checks to warnings.

Risks: correctness of access tracking cannot be deterministic because page-idle/MGLRU clear young bits without guaranteed TLB flush and pagevec/LRU timing is asynchronous. Nested virtualization, NUMA balancing, missing PFN visibility, cgroup setup failures, and insufficient memory can skew results or skip/fail. Busy spin synchronization is intentional but CPU-intensive.

Test signals: printed timing lines for populate/read/write/mark-idle phases are the primary performance signal. Failures come from missing kernel facilities, too many idle/old pages when not warning-only, unexpected ucalls, missing cgroup accounting, or memstress guest asserts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/access_tracking_perf_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arch_timer.c

Purpose: this host-side KVM arch-timer runner creates a multi-vCPU VM and validates timer interrupt delivery, timing margins, and optional vCPU migration stress. Architecture-specific guest logic is provided by the paired timer implementation files and common `timer_test.h`.

Important APIs and functions: global `test_args`, `vcpus`, and `vcpu_shared_data` are shared with guest/timer helpers. Host functions include `test_vcpu_run()`, `test_get_pcpu()`, `test_migrate_vcpu()`, `test_vcpu_migration()`, `test_run()`, `test_print_help()`, `parse_args()`, and `main()`.

Control flow: `main()` parses timer period, vCPU count, iteration count, migration frequency, counter offset, and error margin. It requires at least two CPUs when migration is requested, calls `test_vm_create()`, runs all vCPU threads, and cleans up. Each vCPU thread performs a single `vcpu_run()` and treats any guest exit as completion, then decodes ucalls. A migration thread periodically pins active vCPU threads to random online pCPUs until all are done.

State and persistence: state is process-local: pthread IDs, a bitmap of completed vCPUs protected by a mutex, global test arguments, and per-vCPU shared data synchronized from the guest on failure. No durable state is stored.

Dependencies and integration points: depends on pthreads, CPU affinity helpers, bitmap helpers, KVM lib helpers, timer common code, and architecture-specific `test_vm_create()` / `test_vm_cleanup()`. On arm64, this integrates with VGIC and timer IRQ setup in `arm64/arch_timer.c`.

Risks: timer tests are timing-sensitive and can fail on slow or overloaded systems unless error margins are tuned. Migration relies on CPU affinity and can race with vCPU thread completion, so `ESRCH` is tolerated. Any unexpected guest exit is a failure.

Test signals: per-vCPU `PASS(vCPU-n)` messages, guest assertion reports containing stage/iteration, timeout/margin failures, and successful process exit are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/aarch32_id_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/aarch32_id_regs.c

Purpose: this arm64 KVM selftest verifies AArch64-only vCPUs expose the AArch32 ID register views as read-as-zero, with correct write-ignore or invariant-write rejection semantics.

Important APIs and functions: guest `guest_main()` reads many AArch32 ID and media feature sysregs and asserts zero. Host helpers `test_guest_raz()`, `test_user_raz_wi()`, `test_user_raz_invariant()`, and `vcpu_aarch64_only()` exercise `KVM_GET_ONE_REG` / `KVM_SET_ONE_REG` through `vcpu_get_reg()`, `vcpu_set_reg()`, and `__vcpu_set_reg()`. Register arrays classify writable-ignore versus invariant registers.

Control flow: `main()` creates one vCPU, requires an AArch64-only EL0 profile by reading `ID_AA64PFR0_EL1`, tests userspace read/write behavior on the register arrays, then runs the guest to verify in-guest RAZ behavior.

State and persistence: no persistent state exists. Host state is the VM/vCPU and temporary register values. Guest state is only assertion progress.

Dependencies and integration points: depends on arm64 sysreg encodings, KVM one-reg UAPI, libkvm VM creation, `linux/bitfield.h`, and guest ucall assertion reporting.

Risks: the test is intentionally skipped on systems that support AArch32 at EL0. Register classification must track KVM ABI behavior: some zero registers accept writes with no effect, while invariant registers must reject nonzero writes with `EINVAL`.

Test signals: failures identify a nonzero guest read, nonzero userspace read, unexpected write acceptance/rejection, or unexpected ucall. Passing indicates both guest and userspace views conform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/aarch32_id_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer.c

Purpose: this is the arm64 guest/VM implementation for the generic `kvm/arch_timer.c` runner. It validates virtual and physical arch-timer IRQs using both CVAL and TVAL programming.

Important APIs and functions: `enum guest_stage` enumerates virtual CVAL, virtual TVAL, physical CVAL, and physical TVAL stages. Guest functions include `guest_configure_timer_action()`, `guest_validate_irq()`, `guest_irq_handler()`, `guest_run_stage()`, and `guest_code()`. Host functions include `test_init_timer_irq()`, `test_vm_create()`, and `test_vm_cleanup()`.

Control flow: host `test_vm_create()` requires VGICv3, creates N vCPUs running `guest_code`, installs IRQ descriptor tables and an IRQ handler, optionally applies `KVM_ARM_SET_COUNTER_OFFSET`, discovers virtual/physical timer IRQs, and syncs arguments to the guest. The guest masks timers, initializes GICv3, enables timer IRQs, and runs four stages. Each stage programs the timer, delays for the period plus margin, and asserts exactly one IRQ arrived.

State and persistence: `vtimer_irq`, `ptimer_irq`, `test_args`, and `vcpu_shared_data` are synced as guest-visible globals. Per-vCPU shared data tracks current stage, iteration count, and timestamp. No durable state is written.

Dependencies and integration points: uses arm64 `arch_timer`, `gic`, `vgic`, delay helpers, descriptor table helpers, and KVM counter-offset capability. It plugs into the host runner in `kvm/arch_timer.c`.

Risks: delivery timing depends on host scheduling and timer emulation latency. Physical timer support and VGICv3 are required. Counter offset support is optional but hard-fails if requested and unavailable.

Test signals: guest assertions validate IRQ ID, timer condition (`cnt >= cval`), `CTL_ISTATUS`, and arrival within margin. Host reports guest assertion stage/iteration on abort and `PASS(vCPU-n)` on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer_edge_cases.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer_edge_cases.c

Purpose: this arm64 KVM selftest stresses edge cases in virtual and physical arch-timer emulation: timers beyond TVAL range, timers in the past, counter jumps, timer reprogramming, repeated firing, masking/unmasking, long delays, userspace sleeps, scheduler yields, and vCPU migration.

Important APIs and functions: `struct test_args`, `struct test_vcpu_shared_data`, `sleep_method[]`, and `irq_wait_method[]` define the test matrix. Guest helpers include `set_cval_irq()`, `set_tval_irq()`, `guest_irq_handler()`, timer wait/sleep helpers, `reset_timer_state()`, `test_basic_functionality()`, `timers_sanity_checks()`, `test_timers_above_tval_max()`, `test_timers_in_the_past()`, counter-move tests, reprogramming tests, repeated-fire tests, and `guest_code()`. Host helpers include `kvm_set_cntxct()`, `handle_sync()`, `test_run()`, `test_vm_create()`, and `set_counter_defaults()`.

Control flow: `main()` requires VGICv3, parses timer selection and timing options, records the default cpuset, computes counter width/max defaults, then runs separate VMs for virtual and/or physical timers. Guest code initializes GIC/timers and repeatedly runs the edge-case suite. Guest syncs ask userspace to set counters, sleep, yield, or migrate; host `handle_sync()` performs those actions and resumes the vCPU.

State and persistence: shared atomic counters track handled and spurious IRQs. Host global `CVAL_MAX`, `DEF_CNT`, timer IRQ numbers, and cpuset state influence tests. No persistent files are used.

Dependencies and integration points: depends on arm64 timer sysregs, VGIC/GIC helpers, KVM timer count registers (`KVM_REG_ARM_TIMER_CNT`, `KVM_REG_ARM_PTIMER_CNT`), CPU affinity, and kselftest timeout protection for theoretically infinite waits.

Risks: many waits can hang if timer emulation is broken, relying on the outer runner timeout. Counter width inference is conservative but architecture-sensitive. Migration/yield/sleep paths can be noisy on loaded systems.

Test signals: guest assertions check IRQ counts, ISTATUS/timer-condition consistency, cval/tval relationships, no-IRQ windows, and expected firing after counter manipulation. Host unexpected ucalls or guest aborts are failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer_edge_cases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/at.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/at.c

Purpose: this arm64 KVM selftest validates emulation of address-translation (`AT`) instructions in EL2&0 and EL1&0 translation regimes, especially access-flag behavior and slow-path emulation through invalidated stage-2 mappings.

Important APIs and functions: macros `copy_el2_to_el1()`, `__at()`, and `test_at_insn()` encode AT operations and PAR_EL1 checks. Guest functions `test_at()` and `guest_code()` execute S1E2R/W and S1E1R/W with expected fault/nonfault behavior. Host `handle_sync()` clears the stage-1 PTE access flag and reloads the page-table memslot; `run_test()` drives ucalls.

Control flow: `main()` requires `KVM_CAP_ARM_EL2`, creates an EL2-capable vCPU, finalizes vCPUs, maps `TEST_ADDR`, obtains the PTE HVA, and runs the guest. The guest disables hardware access flag, expects access-flag faults, then enables HA if supported and expects successful AT results. Before each AT instruction, the guest syncs so userspace can clear PTE_AF and reload page-table mappings.

State and persistence: `ptep_hva` points to the host mapping of the tested PTE. Guest manipulates TCR/HCR/VTCR/VTTBR and PAR_EL1. No durable state is stored.

Dependencies and integration points: depends on EL2-capable arm64 KVM, sysreg helpers, libkvm page-table introspection, `vm_mem_region_reload()`, and ucall synchronization.

Risks: the test deliberately edits page tables and stage-2 mappings. It assumes the selected test virtual/physical address mapping is safe and that reloading the page-table memslot invalidates relevant KVM state. Hardware without HAFDBS only runs the faulting half.

Test signals: guest asserts PAR fault bit, fault status code, memory attributes, shareability, and translated PA. Unexpected sync commands or guest aborts fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/at.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/debug-exceptions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/debug-exceptions.c

Purpose: this arm64 KVM selftest validates guest debug exception behavior and userspace single-step debug control, covering software breakpoints, hardware breakpoints, watchpoints, single step, OS lock effects, context-linked breakpoints/watchpoints, and KVM_EXIT_DEBUG sequencing.

Important APIs and functions: debug-register writer macros generate `write_dbgbcr()`, `write_dbgbvr()`, `write_dbgwcr()`, and `write_dbgwvr()`. Guest helpers include `reset_debug_state()`, `enable_os_lock()`, `enable_monitor_debug_exceptions()`, `install_wp()`, `install_hw_bp()`, `install_wp_ctx()`, `install_hw_bp_ctx()`, `install_ss()`, `guest_code()`, and `guest_code_ss()`. Exception handlers record PCs/FAR and advance as needed. Host functions include `test_guest_debug_exceptions()`, `test_single_step_from_userspace()`, and `test_guest_debug_exceptions_all()`.

Control flow: `main()` reads `ID_AA64DFR0_EL1`, requires debug architecture >= v8, parses single-step iteration count, runs the guest exception suite across all supported breakpoint/watchpoint/context breakpoint combinations, then runs userspace-driven single-step tests. The userspace single-step loop enables `KVM_GUESTDBG_SINGLESTEP` after a bare ucall and checks sequential PC values until `iter_ss_end`.

State and persistence: guest globals record observed PCs/data addresses and single-step indices. Host `struct kvm_guest_debug` toggles debug control. No persistent state is stored.

Dependencies and integration points: depends on arm64 debug sysregs, KVM guest debug UAPI, descriptor-table exception handlers, ID register feature fields, and libkvm ucall handling.

Risks: guest ucall internals can use exclusive access instructions, so the single-step test uses a bare `GUEST_UCALL_NONE()` to avoid forward-progress issues. Hardware debug resource counts vary; the test dynamically iterates but requires at least two breakpoints. OS lock behavior is nuanced and architecture-dependent.

Test signals: assertions compare captured PCs/FAR against labeled assembly symbols, verify OS lock blocks only expected debug sources, and check userspace `KVM_EXIT_DEBUG` PC progression. Unexpected ucall or debug exit is a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/debug-exceptions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/external_aborts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/external_aborts.c

Purpose: this arm64 KVM selftest validates userspace injection and delivery of synchronous external aborts and SError exceptions, including MMIO aborts, ESR_EL2.ISV=0 NISV behavior, stage-1 page-table-walk aborts, EASE routing, RAS ESR payloads, and EL2 AMO behavior.

Important APIs and functions: VM setup helper `vm_create_with_dabt_handler()` installs data-abort handlers and maps an MMIO address. Injection helpers `vcpu_inject_sea()` and `vcpu_inject_serror()` write `struct kvm_vcpu_events`. Test cases include `test_mmio_abort()`, `test_mmio_nisv()`, `test_mmio_nisv_abort()`, `test_serror_masked()`, `test_serror()`, `test_s1ptw_abort()`, `test_serror_emulated()`, `test_mmio_ease()`, and `test_serror_amo()`.

Control flow: `main()` runs each case sequentially and gates the AMO/EL2 case on `test_supports_el2()`. MMIO cases run the guest until a KVM exit or `KVM_RUN` failure, inject an abort/event, then expect the guest handler to finish. SError cases inject pending SError before or after guest sync and validate masking/unmasking paths. S1PTW mutates a PTE to an invalid PA to force an external abort during page-table walk.

State and persistence: global `expected_abort_pc` lets guest handlers verify the precise faulting instruction. Events are held only in KVM vCPU event state. No durable state is stored.

Dependencies and integration points: depends on arm64 exception vectors, KVM vCPU events UAPI, `KVM_CAP_ARM_NISV_TO_USER`, `KVM_EXIT_ARM_NISV`, MMIO exits, RAS ID fields, SCTLR2 EASE support, and optional EL2 support.

Risks: feature availability controls some paths; unsupported DF2/EASE is skipped locally. The test edits guest page tables and relies on exact ESR/FSC semantics. NISV behavior intentionally expects an `ENOSYS` KVM_RUN failure without the capability.

Test signals: assertions check exit reasons, MMIO/NISV addresses, ESR exception classes, FSC values, SError ISS payloads under RAS, pending ISR bits, and clean `GUEST_DONE` after injected exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/external_aborts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/get-reg-list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/get-reg-list.c

Purpose: this arm64 KVM selftest detects regressions in `KVM_GET_REG_LIST` by comparing vCPU register lists against blessed register sets across feature configurations such as base FP/SIMD, PMU, SVE, pointer authentication, EL2, and EL2 E2H0.

Important APIs and data: `struct feature_id_reg` maps optional registers to feature ID fields. Helper callbacks `filter_reg()`, `check_supported_reg()`, `check_reject_set()`, `finalize_vcpu()`, and `print_reg()` are consumed by common register-list test infrastructure. Register arrays include `base_regs`, `pmu_regs`, `vregs`, `sve_regs`, `pauth_addr_regs`, `pauth_generic_regs`, `el2_regs`, and `el2_e2h0_regs`. `vcpu_configs[]` enumerates all tested sublist combinations.

Control flow: common KVM selftest code creates vCPUs using each `vcpu_reg_list` configuration, enables requested features/capabilities, finalizes when needed, gets the actual reg list, filters host-dependent DEMUX registers, omits unsupported feature-gated registers, compares against expected arrays, and uses `print_reg()` to format unexpected/missing register IDs for updating the blessed lists.

State and persistence: the file holds static expected-register arrays and configuration descriptors. Runtime state is limited to a VM/vCPU per configuration. No files are written by the test, although printed output is designed to help maintainers update source arrays.

Dependencies and integration points: depends on arm64 KVM one-reg/list UAPI, feature capability constants, sysreg encoding macros, SVE/PAuth/PMU/EL2 capabilities, and common register-list harness declarations from KVM selftests. It encodes ABI expectations that must remain stable for old kernels.

Risks: blessed lists are large and must be carefully updated when the ABI intentionally grows. Some registers are feature-gated by ID registers rather than just KVM capabilities, so `feat_id_regs` must stay current. Duplicate or missing feature mappings can cause false positives. DEMUX registers are filtered because they vary with host cache topology.

Test signals: mismatched register lists, unexpected set rejection errno, unsupported optional register exposure, or unrecognized register ID formatting failures indicate regressions. Passing across all configurations indicates the arm64 reg-list ABI remains compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/get-reg-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hello_el2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hello_el2.c

Purpose: this basic arm64 KVM selftest verifies a VM can run at EL2 with E2H described as RES1 and with virtual-host-extension expectations satisfied.

Important APIs and functions: `guest_code()` reads `ID_AA64MMFR0_EL1`, `ID_AA64MMFR1_EL1`, `ID_AA64MMFR4_EL1`, checks `get_current_el()`, `HCR_EL2_E2H`, VH field support, E2H0 semantics, and FGT behavior. `main()` creates an EL2-capable vCPU by setting `KVM_ARM_VCPU_HAS_EL2`.

Control flow: host requires `KVM_CAP_ARM_EL2`, creates a one-vCPU VM without the convenience one-vCPU helper so it can modify `struct kvm_vcpu_init`, finalizes vCPUs, runs once, and handles `UCALL_DONE` or guest abort. The guest asserts it is executing at EL2 and validates the ID register story around E2H0/FGT.

State and persistence: no persistent state. The only runtime state is vCPU feature configuration and guest register values.

Dependencies and integration points: depends on arm64 nested/EL2 KVM support, sysreg helpers, `ucall`, and KVM vCPU target/finalization APIs.

Risks: ID register behavior around E2H0 and FGT is subtle; the test allows IMPDEF trap behavior by accepting all-zero reads in the appropriate case. Systems without EL2 KVM support skip.

Test signals: guest assertions for current EL, HCR.E2H, VH support, and E2H0/FGT fields are the main signal; any unexpected ucall fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hello_el2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/host_sve.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/host_sve.c

Purpose: this selftest checks host FPSIMD/SVE/SME state save/restore across repeated `KVM_RUN` ioctls. It focuses on host context preservation rather than guest SVE support.

Important APIs and functions: guest `guest_code()` emits ten `GUEST_UCALL_NONE()` exits and then `GUEST_DONE()`. Host functions include `handle_sigill()`, `register_sigill_handler()`, `do_sve_roundtrip()`, `test_run()`, and `main()`. Inline assembly sets predicate register `p0`, counts active bits before and after a recoverable `udf #0`, and compares counts.

Control flow: `main()` checks `AT_HWCAP` for `HWCAP_SVE` and skips if absent. `test_run()` registers a SIGILL handler, creates a one-vCPU VM, tests SVE state once, then runs the vCPU loop. Each guest `UCALL_NONE` triggers two host SVE roundtrips before the next `KVM_RUN`.

State and persistence: no durable state. Host signal context is modified to skip the `udf` instruction by advancing PC. SVE predicate state is transient and tested across signal and KVM transitions.

Dependencies and integration points: depends on host SVE hardware support, signal handling, inline SVE assembly, libkvm VM creation, and ucall handling.

Risks: the inline assembly requires SVE-capable compiler/toolchain support. The test assumes SIGILL recovery from `udf #0` and that predicate register `p0` can be clobbered/observed as written. It does not validate guest SVE exposure.

Test signals: printed before/after predicate counts should match for every signal/KVM roundtrip. Mismatch calls `TEST_FAIL`; lack of SVE returns `KSFT_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/host_sve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hypercalls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hypercalls.c

Purpose: this arm64 KVM selftest validates pseudo-firmware bitmap registers and the guest-visible SMCCC hypercall interface they control, including standard, standard-hypervisor, vendor-hypervisor, and second vendor bitmap registers.

Important APIs and data: `struct kvm_fw_reg_info` describes each firmware bitmap register, max feature bit, and reset value. `hvc_info[]` and `false_hvc_info[]` define SMCCC calls to test supported/unsupported behavior. Guest `guest_test_hvc()` and `guest_code()` validate SMCCC return values by stage. Host helpers `steal_time_init()`, `test_fw_regs_before_vm_start()`, `test_fw_regs_after_vm_start()`, `test_vm_create()`, `test_guest_stage()`, and `test_run()` coordinate register UAPI and guest stages.

Control flow: host creates a VM, initializes steal-time backing, verifies firmware register reset values and writeability before first run, clears features, then runs the staged guest. After the first sync, host verifies firmware registers are locked with `EBUSY`. It then starts a fresh VM to test default-enabled feature behavior and false feature queries.

State and persistence: global `stage` is synced to the guest. Firmware bitmap register values are KVM vCPU state. Steal-time memory is added as a guest memory region. No durable state is stored.

Dependencies and integration points: depends on arm64 SMCCC constants, KVM firmware feature bitmap one-reg ABI, private vCPU device attrs for steal time, and libkvm ucall/global sync helpers.

Risks: register max-bit constants must track KVM ABI growth. Firmware bitmap registers become immutable after vCPU run, so stage ordering is critical. Some hypercall families can have nuanced return values, but the test only asserts supported versus not-supported.

Test signals: reset-value mismatches, invalid write acceptance, missing `EBUSY`, disabled features returning supported, enabled features returning not-supported, or false feature queries succeeding are failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hypercalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/idreg-idst.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/idreg-idst.c

Purpose: this selftest verifies FEAT_IDST-handled sysregs that depend on more than FEAT_AA64 trap as SYS64 accesses, rather than unexpectedly undefining or being directly readable, when the guest lacks related features.

Important APIs and functions: macros `__check_sr_read()` and `check_sr_read()` read selected sysregs and assert that `guest_sys64_handler()` ran and `guest_undef_handler()` did not. Guest `guest_code()` checks `CCSIDR2_EL1`, `SMIDR_EL1`, and `GMID_EL1`. Host `test_guest_feat_idst()` installs sync handlers for `ESR_ELx_EC_SYS64` and `ESR_ELx_EC_UNKNOWN`.

Control flow: `main()` disables default VGIC, probes `ID_AA64MMFR2_EL1.IDS`, skips if FEAT_IDST is absent, then creates a VM without MTE/SME/CCIDX and runs the guest. Each sysreg read should trap to the SYS64 handler, which advances PC and records `sys64=true`.

State and persistence: volatile guest booleans `sys64` and `undef` record which handler ran. No durable state is stored.

Dependencies and integration points: depends on arm64 ID register fields, KVM sysreg trap handling, descriptor-table sync handlers, and default-VGIC disabling to keep the VM minimal.

Risks: the test assumes the created VM lacks the features tied to the tested registers. Feature exposure changes may require updating the register list or setup.

Test signals: guest assertions fail if any tested register UNDEFs or reads without a SYS64 trap. Host fails on unknown ucalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/idreg-idst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/kvm-uuid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/kvm-uuid.c

Purpose: this small arm64 KVM selftest ensures KVM's vendor hypervisor SMCCC UID remains the hard-coded expected UUID.

Important APIs and functions: `guest_code()` calls `do_smccc(ARM_SMCCC_VENDOR_HYP_CALL_UID_FUNC_ID, ...)` and compares return registers `a0` through `a3` against constants for UUID `28b46fb6-2ec5-11e9-a9ca-4b564d003a74`. Host `main()` runs a one-vCPU VM and handles `UCALL_DONE`, `UCALL_ABORT`, `UCALL_PRINTF`, and sync.

Control flow: the guest performs one SMCCC call and either asserts the UID matches or reports failure, then signals done. The host loops until done.

State and persistence: no persistent state. The expected UUID constants are intentionally local rather than shared to detect accidental global changes.

Dependencies and integration points: depends on ARM SMCCC vendor hypervisor call handling in KVM, libkvm VM creation, and ucall reporting.

Risks: the constants must not be "deduplicated" with production headers because the point is detecting tampering or drift. If KVM intentionally changes ABI identity, this test must be deliberately updated.

Test signals: mismatch in any SMCCC return word is a guest assertion failure. Passing confirms stable KVM vendor UID exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/kvm-uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/no-vgic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/no-vgic.c

Purpose: this arm64 KVM selftest verifies that when a VM is created without a VGIC, GICv3 and GICv5 system register/instruction interfaces are hidden from the guest and accesses trap as UNDEF.

Important APIs and functions: guest macros issue sysreg reads/writes and GICv5 operations while checking a volatile `handled` flag. `guest_code_gicv3()` validates `ID_AA64PFR0_EL1.GIC == 0` and probes many ICC registers. `guest_code_gicv5()` validates `ID_AA64PFR2_EL1.GCIE == 0`, probes GICv5 ops and registers. `guest_undef_handler()` marks success and advances PC. Host `test_guest_no_vgic()` creates the no-GIC VM and installs the unknown-exception handler.

Control flow: `main()` calls `test_disable_default_vgic()`, probes whether the host supports GICv3/GICv5 in a temporary VM, requires at least one, and runs the corresponding guest tests. Each guest access is expected to trap to `ESR_ELx_EC_UNKNOWN`, except `ICC_SRE_EL1` may legally be untrappable if SRE is RAO/WI.

State and persistence: guest global `handled` records whether the last access trapped. No durable state is stored.

Dependencies and integration points: depends on arm64 GIC system register encodings, optional GICv5 helper macros, KVM no-default-VGIC mode, and descriptor-table handlers.

Risks: GIC register trap semantics have legal exceptions, which the test handles for `ICC_SRE_EL1`. New GIC registers or GICv5 features may require expanding the probe list.

Test signals: a failure indicates feature ID bits are exposed without VGIC, an access did not UNDEF, or an unexpected ucall occurred. Informational prints show skipped v3/v5 subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/no-vgic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/page_fault_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/page_fault_test.c

Purpose: this arm64 KVM selftest exercises stage-2 fault handling across guest access types, backing sources, userfaultfd, dirty logging, read-only memslots, holes in backing storage, access-flag updates, and no-syndrome instructions.

Important APIs, types, and functions: `struct test_desc` describes each generated scenario: guest prepare functions, guest access function, post-checks, userfaultfd handlers, abort handlers, MMIO/fail handlers, memslot flags, and expected event counts. Guest accessors include `guest_read64()`, `guest_write64()`, `guest_cas()`, `guest_at()`, `guest_dc_zva()`, `guest_ld_preidx()`, `guest_st_preidx()`, and `guest_exec()`. Host helpers include `setup_uffd()`, `punch_hole_in_backing_store()`, `mmio_on_test_gpa_handler()`, `check_write_in_dirty_log()`, `handle_cmd()`, `setup_memslots()`, `vcpu_run_loop()`, and `run_test()`.

Control flow: `main()` parses guest mode/backing source options, then iterates the static `tests[]` matrix across enabled guest modes. `run_test()` manually creates VM memory slots for code/data, page tables, and test data; maps `TEST_GVA` and a guest-visible PTE address; loads tiny executable code into the data memslot; configures userfaultfd and abort handlers; then runs the vCPU loop. Guest `guest_code()` performs optional preparation, syncs requested host memory mutations, executes the selected access, performs post-checks, and exits.

State and persistence: global `events` counts MMIO exits, failed vCPU runs, and userfaultfd faults. `pt_args` and `data_args` hold demand-paging copies and HVA metadata. Test descriptors can be marked `skip` when feature preparation is unavailable. No durable files are written.

Dependencies and integration points: depends on KVM memory-slot flags, dirty-log UAPI, userfaultfd demand paging helpers, guest mode helpers, backing source helpers, page-table introspection, AArch64 access-flag support, LSE atomics, DC ZVA, and MMIO exit behavior.

Risks: the matrix is broad and architecture-sensitive. No-syndrome operations should fail KVM_RUN with `ENOSYS` in read-only cases, while syndrome writes should become MMIO. Userfaultfd behavior depends on host kernel support and backing source semantics. Dirty-log page granularity uses host page size, not guest page size.

Test signals: expected counts for UFFD faults, MMIO exits, and failed KVM_RUNs must match. Dirty-log checks, PTE_AF checks, guest access assertions, unexpected abort handlers, and failed memory-hole operations all signal regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/page_fault_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/psci_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/psci_test.c

Purpose: this arm64 KVM selftest validates PSCI emulation, including CPU_ON reset state races, SYSTEM_SUSPEND UAPI exits, and PSCI v1.3 SYSTEM_OFF2 hibernate shutdown events.

Important APIs and functions: SMCCC wrappers `psci_cpu_on()`, `psci_affinity_info()`, `psci_system_suspend()`, `psci_system_off2()`, and `psci_features()` issue PSCI calls. Host helpers `vcpu_power_off()`, `setup_vm()`, `enter_guest()`, and `assert_vcpu_reset()` manage two-vCPU VMs. Test pairs include `guest_test_cpu_on()` / `host_test_cpu_on()`, `guest_test_system_suspend()` / `host_test_system_suspend()`, and `guest_test_system_off2()` / `host_test_system_off2()`.

Control flow: `main()` requires `KVM_CAP_ARM_SYSTEM_SUSPEND`, then runs the three host tests. `setup_vm()` creates two PSCI 0.2-capable vCPUs. CPU_ON powers off the target, guest calls CPU_ON, polls affinity, and host verifies target PC/x0 reset values. SYSTEM_SUSPEND enables the VM cap and expects `KVM_EXIT_SYSTEM_EVENT` with suspend type. SYSTEM_OFF2 verifies PSCI 1.3, exercises invalid-cookie and valid-cookie calls, and expects two shutdown exits flagged as PSCI_OFF2 before guest done.

State and persistence: vCPU MP state and core registers carry the tested state. No persistent state is stored.

Dependencies and integration points: depends on ARM PSCI SMCCC ABI, KVM PSCI version register, `KVM_CAP_ARM_SYSTEM_SUSPEND`, `KVM_EXIT_SYSTEM_EVENT`, MP state UAPI, and libkvm vCPU initialization/finalization.

Risks: PSCI feature availability and version are host/KVM dependent. The SYSTEM_OFF2 test restarts the source vCPU after each shutdown exit, so MP state manipulation must be correct.

Test signals: failures include wrong target reset PC/x0, missing suspend system event, missing PSCI_OFF2 shutdown flag, wrong PSCI return values, or unexpected ucall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/psci_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/sea_to_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/sea_to_user.c

Purpose: this arm64 KVM selftest validates `KVM_CAP_ARM_SEA_TO_USER`: when host APEI cannot handle a synchronous external abort, KVM exits to userspace with `KVM_EXIT_ARM_SEA`; userspace then injects a synchronous external data abort back into the guest.

Important APIs and functions: address helpers `translate_hva_to_hpa()`, EINJ writers `write_einj_entry()` and `inject_uer()`, SIGBUS handling, guest `guest_code()`, guest `expect_sea_handler()`, `vcpu_inject_sea()`, `run_vm()`, `vm_create_with_sea_handler()`, and `vm_inject_memory_uer()` form the test. Global state records EINJ GPA/HVA/HPA and whether FAR is invalid.

Control flow: `main()` requires `KVM_CAP_ARM_SEA_TO_USER`, installs a SIGBUS handler, creates a VM with a 1GB hugetlb-backed region mapped at `START_GVA`, enables SEA-to-user, poisons a selected HPA using ACPI EINJ notrigger, and runs the vCPU. The first run should exit with `KVM_EXIT_ARM_SEA`; host validates ESR/FAR/GPA information, sets guest expectation state, injects an external abort through vCPU events, and resumes until the guest handler reports done.

State and persistence: it writes to firmware/kernel debugfs EINJ control files and consumes a real injected memory error. Runtime globals expose expected FAR validity to the guest via synced memory. No project files are persisted.

Dependencies and integration points: depends on ACPI EINJ firmware table, debugfs EINJ files, notrigger support, hugepage backing, `/proc/self/pagemap`, KVM SEA-to-user capability, and host APEI not claiming the SEA. The SIGBUS handler skips when host APEI handles the error instead.

Risks: this is highly platform-dependent and potentially disruptive because it injects a real recoverable uncorrectable memory error. It requires privileges, debugfs setup, hugepages, and specific firmware behavior. FAR may be invalid, and the test explicitly handles FnV.

Test signals: skip signals come from missing capability/EINJ/APEI behavior. Success requires `KVM_EXIT_ARM_SEA`, correct ESR class/FSC fields, optional matching GVA/GPA, and clean guest handling of the injected SEA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/sea_to_user.c -->
