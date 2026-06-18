# subset-b-006880 Research

Grouped source research for subset B work item `subset-b-006880`. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-tar.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-tar.c

Purpose: exercises ptrace access to TAR, PPR, and DSCR while a child is in a suspended transactional-memory section. It verifies the live suspended state, the checkpointed state, and the effect of writing checkpointed special-purpose registers before transaction abort recovery.

Important APIs/types/functions: `tm_spd_tar()` is the tracee, `trace_tm_spd_tar()` is the tracer, and `ptrace_tm_spd_tar()` owns fork/shared-memory setup. It uses `shmget/shmat/shmdt/shmctl`, `tbegin.`, `tsuspend.`, `tresume.`, `mfspr/mtspr`, `show_tar_registers()`, `show_tm_checkpointed_state()`, and `write_ckpt_tar_registers()`.

Control flow: the child loads baseline checkpoint values, enters TM, changes TAR/PPR/DSCR, suspends, installs a third visible state, then waits for the parent. The parent attaches with ptrace, validates live values as `TAR_3/PPR_3/DSCR_3`, validates checkpoint values as `TAR_1/PPR_1/DSCR_1`, writes `TAR_4/PPR_4/DSCR_4`, releases the child, and expects the abort path to observe those written checkpoint values.

State and persistence behavior: SysV shared memory carries two control flags plus a ready flag. Register state exists only in the child CPU/TM context; the persistent test signal is the child's exit status. Shared memory is removed after `wait()`.

Dependencies and integration points: depends on HTM availability, non-synthetic TM, `tm.h`, `ptrace.h`, and `ptrace-tar.h`. It integrates with kselftest through `test_harness()`.

Risks and test signals: busy-wait synchronization can hang if the child never reaches suspend. Failures report mismatched register tuples or abnormal child status. The test skips on systems without real HTM.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-tar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-vsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-vsx.c

Purpose: validates ptrace access to VMX and VSX state when a traced process is in a suspended transaction, including checkpointed VMX/VSX writes and post-abort restoration.

Important APIs/types/functions: `load_vsx*()` wrappers feed assembly helpers from `ptrace-vsx.h`; `tm_spd_vsx()` drives the tracee transaction; `trace_tm_spd_vsx()` reads and writes live/checkpointed `NT_PPC_TM_CVMX` and `NT_PPC_TM_CVSX` regsets via helpers in `ptrace.h`.

Control flow: random arrays seed live, speculative, checkpoint, and replacement checkpoint data. The child loads checkpoint vectors before `tbegin.`, loads speculative values, suspends, loads suspended live values, and waits. The parent validates live VMX/VSX against `fp_load`, checkpointed state against `fp_load_ckpt`, writes `fp_load_ckpt_new`, detaches, and the child confirms the final restored state after abort.

State and persistence behavior: shared memory coordinates ready/release/abort flags. The vector arrays are process globals copied by fork and used as immutable expectations. No external persistence exists beyond the per-run child exit code.

Dependencies and integration points: requires real HTM, VSX/VMX ptrace regset support, assembly `loadvsx/storevsx`, and endian-aware vector validation helpers.

Risks and test signals: endian packing mistakes are caught by `validate_vmx()` and `compare_vsx_vmx()`. A stuck transaction or ptrace failure causes the parent to kill the child and fail.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-vsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spr.c

Purpose: tests ptrace readout of transactional-memory SPRs (`TFHAR`, `TEXASR`, `TFIAR`) from a child stopped while a transaction is suspended.

Important APIs/types/functions: `struct shared` carries a completion flag plus `struct tm_spr_regs`; `validate_tm_spr()` checks expected `TFHAR` and tolerated KVM reschedule encoding; `tm_spr()` constructs the transaction; `trace_tm_spr()` calls `show_tm_spr()`.

Control flow: the child computes the transaction fail-handler address around `tbegin.`, suspends, signals readiness through a second shared-memory page, and loops. The parent attaches, fetches TM SPRs into shared memory, marks the flag, detaches, and waits. The abort path then validates the fetched data against the locally calculated `tfhar`.

State and persistence behavior: two SysV shared-memory regions separate SPR payload from the simple ready flag. The expected `tfhar` is a process global in the child and is adjusted for instruction distance.

Dependencies and integration points: requires `ptrace.h` TM regset constants, `tm.h` HTM checks, and working `NT_PPC_TM_SPR`.

Risks and test signals: instruction-layout assumptions are central; compiler/assembler changes near `tbegin.` can break `tfhar` expectations. The test treats synthetic TM as skip and uses child exit status as the final signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-tar.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-tar.c

Purpose: validates ptrace visibility and checkpoint modification of TAR/PPR/DSCR while a child is inside a normal transaction rather than the separate suspended-state variant.

Important APIs/types/functions: `tm_tar()` creates the child transaction and suspended synchronization point; `trace_tm_tar()` attaches and uses TAR helpers from `ptrace.h`; `ptrace_tm_tar()` handles SysV shared memory and lifecycle.

Control flow: the child initializes checkpoint values, begins a transaction, changes the live transactional values, suspends only long enough to set a parent-visible flag, resumes, and loops. The parent waits for that flag, reads live registers (`TAR_2/PPR_2/DSCR_2`), reads checkpointed registers (`TAR_1/PPR_1/DSCR_1`), writes new checkpoint values, and detaches so the child abort path can validate them.

State and persistence behavior: a two-slot shared memory array carries release and ready flags. Register state is transient and verified through both ptrace and direct child `mfspr()` after abort.

Dependencies and integration points: real HTM, `ptrace-tar.h` constants, and powerpc ptrace regsets are required. It uses `test_harness()` for kselftest status.

Risks and test signals: the infinite transactional loop relies on the parent to change shared memory. Any ptrace, validation, or child-exit mismatch fails the test.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-tar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-vsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-vsx.c

Purpose: checks ptrace VMX/VSX live and checkpoint state while a child is in a transaction and validates that checkpoint writes become the restored state after abort.

Important APIs/types/functions: `tm_vsx()`, `trace_tm_vsx()`, `load_vsx_vmx()`, `show_vsx()`, `show_vmx()`, `show_vsx_ckpt()`, `show_vmx_ckpt()`, `write_vsx_ckpt()`, and `write_vmx_ckpt()` are the important pieces.

Control flow: the child loads checkpoint vector state, starts a transaction, loads live vector state, suspends to signal readiness, resumes, and loops. The parent verifies live VSX/VMX state against `fp_load`, checkpoint state against `fp_load_ckpt`, writes the new checkpoint vector pair built from `fp_load_ckpt_new`, releases the child, and expects the abort path to store and compare the new values.

State and persistence behavior: shared memory has release and ready slots. Global vector buffers persist across fork and are used as deterministic per-run expectations.

Dependencies and integration points: requires HTM, non-synthetic TM, VSX hardware support implied by regsets, `ptrace-vsx.h` validation, and kernel ptrace regset plumbing.

Risks and test signals: VMX/VSX endian layout is a major risk; helper validation handles it. Failure surfaces as `FAIL_IF`, parent kill, or nonzero child exit.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-vsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.c

Purpose: non-TM ptrace test for ordinary live VMX/VSX register get/set behavior in a child process.

Important APIs/types/functions: `vsx()` loads vector data and waits; `trace_vsx()` uses `PTRACE_GETVSRREGS`, `PTRACE_GETVRREGS`, `PTRACE_SETVSRREGS`, and `PTRACE_SETVRREGS` through helpers; `ptrace_vsx()` seeds random expectations and owns process cleanup.

Control flow: the child loads initial VSX/VMX content and signals readiness. The parent attaches, reads and validates VSX and VMX state against `fp_load`, constructs replacement regsets from `fp_load_new`, writes both regsets, detaches, and releases the child. The child stores its registers and compares them with the replacement data.

State and persistence behavior: shared memory carries ready/release flags. Vector arrays are globals copied into both processes at fork.

Dependencies and integration points: requires `PPC_FEATURE_HAS_VSX`, ptrace regset support, `ptrace.h`, and `ptrace-vsx.h`.

Risks and test signals: partial write/read failures are reported by ptrace helper errors. The child exit status detects register state that did not survive detach.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.h

Purpose: shared validation and packing helper for ptrace VMX/VSX tests.

Important APIs/types/functions: defines `VEC_MAX`, `VSX_MAX`, `VMX_MAX`, `validate_vsx()`, `validate_vmx()`, `compare_vsx_vmx()`, `load_vsx_vmx()`, and prototypes for assembly `loadvsx()`/`storevsx()`.

Control flow: validators compare ptrace-exposed arrays against the synthetic 128-word load buffer. `validate_vsx()` checks the high doubleword mapping for VSX 0-31. `validate_vmx()` and `compare_vsx_vmx()` branch on compile-time endianness because VMX pairs are stored in alternate order on little endian. `load_vsx_vmx()` converts a flat buffer into ptrace write payloads.

State and persistence behavior: the header has no persistent state; it operates on caller-owned buffers. It is intentionally included directly by tests, so function definitions are emitted into each translation unit.

Dependencies and integration points: assumes `TEST_FAIL/TEST_PASS` and `printf()` from including test context, and assembly helpers supplied elsewhere in the ptrace directory.

Risks and test signals: off-by-one or endian mistakes cause explicit index/value diagnostics. Because this is a header with definitions, multiple inclusion in one object would be unsafe.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace.h

Purpose: central ptrace helper implementation for powerpc selftests, covering attach/detach, scalar SPRs, GPR/FPR, VMX/VSX, checkpointed TM regsets, and TM SPR readout.

Important APIs/types/functions: defines fallback `NT_PPC_*` regset constants, `struct fpr_regs`, `struct tm_spr_regs`, `start_trace()`, `stop_trace()`, `ptrace_read_regs()`, `ptrace_write_regs()`, TAR/PPR/DSCR helpers, checkpointed GPR/FPR/VMX/VSX helpers, `show_tm_spr()`, and TEXASR analysis helpers.

Control flow: most helpers build an `iovec`, issue `ptrace(PTRACE_GETREGSET/SETREGSET)` or legacy requests, copy relevant pieces into caller buffers, and return `TEST_PASS/TEST_FAIL`. Basic trace helpers attach and wait before reads, then detach afterward for the generic read/write wrappers.

State and persistence behavior: no durable state; allocations are per-call. Some error paths return without freeing allocated buffers, which is tolerable in short selftests but relevant if reused in long-running tools.

Dependencies and integration points: depends on Linux UAPI ptrace, powerpc `reg.h`, `utils.h`, and TM SPR definitions. It is included as implementation by many tests rather than compiled as a library.

Risks and test signals: helpers assume caller has already stopped the child for many direct regset accesses. Error messages sometimes name GETREGSET for SET failures, so diagnostics can be imprecise.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/scripts/hmi.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/scripts/hmi.sh

Purpose: manual-style powerpc HMI injection script that uses xscom utilities to inject recoverable core FIR errors and checks kernel HMI handling through `dmesg`.

Important APIs/types/functions: shell functions and variables include `GETSCOM`, `PUTSCOM`, `expected_hmis`, and `COUNT_HMIS()`. It uses `ppc64_cpu`, `/sys/firmware/opal/msglog`, `/dev/kmsg`, and xscom `getscom/putscom`.

Control flow: the script locates xscom tools, expands SMT snooze delay, iterates chip/core pairs parsed from OPAL msglog, verifies the target FIR is zero, writes a recoverable error, then waits up to about a minute for the expected number of harmless HMI log messages.

State and persistence behavior: it mutates hardware FIR state and system SMT snooze delay, restoring snooze delay via `trap`. It writes marker lines to the kernel log and relies on kernel state outside the workspace.

Dependencies and integration points: requires OpenPOWER/skiboot xscom utilities, OPAL firmware paths, root-like hardware access, and a kernel that logs the expected HMI text.

Risks and test signals: parsing is intentionally fragile and marked as such. Failure is indicated by nonzero exit after missing xscom tools, nonzero FIR, injection failure, or insufficient HMI messages.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/scripts/hmi.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/Makefile

Purpose: builds the powerpc security mitigation selftests for RFI, entry, uaccess, and Spectre v2 behavior.

Important APIs/types/functions: declares `TEST_GEN_PROGS := rfi_flush entry_flush uaccess_flush spectre_v2` and `TEST_PROGS := mitigation-patching.sh`, pulls in `../../lib.mk` and `../flags.mk`, and adds `$(KHDR_INCLUDES)`.

Control flow: build rules link common `../harness.c` and `../utils.c`; `spectre_v2` is forced to `-m64` and links `../pmu/event.c` plus `branch_loops.S`; the flush tests link `flush_utils.c`.

State and persistence behavior: no runtime state. Generated binaries are under `$(OUTPUT)` per kselftest conventions.

Dependencies and integration points: integrates with kselftest make infrastructure and powerpc PMU/security helpers.

Risks and test signals: missing PMU headers, 64-bit compiler support, or assembly support breaks build before runtime. The shell mitigation stress test is included as a script rather than a generated binary.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/branch_loops.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/branch_loops.S

Purpose: provides branch-prediction workload loops for the Spectre v2 mitigation measurement test.

Important APIs/types/functions: exports `pattern_cache_loop` and `indirect_branch_loop` with `FUNC_START/FUNC_END`. `ITER_SHIFT` controls loop length, and `jump_table` drives pattern-cache transitions.

Control flow: `pattern_cache_loop` cycles through eight aligned state labels using a computed count-register branch, creating a predictable but indirect branch pattern. `indirect_branch_loop` repeatedly branches through CTR to a local aligned label. Both loops run for `1 << 31` iterations unless interrupted by completion.

State and persistence behavior: no persistent state; only GPR/CTR state during execution. The data jump table is read-only for test purposes.

Dependencies and integration points: consumed by `spectre_v2.c` and built only for 64-bit powerpc by the security Makefile.

Risks and test signals: PMU test quality depends on these loops generating stable branch prediction counts. Changes to alignment or loop length can alter thresholds in `spectre_v2.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/branch_loops.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/entry_flush.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/entry_flush.c

Purpose: measures whether the `powerpc/entry_flush` mitigation produces the expected L1D cache-miss behavior on syscall entry.

Important APIs/types/functions: `entry_flush_test()` uses `read_debugfs_int()`, `write_debugfs_int()`, `perf_event_open_counter()`, `perf_event_enable/reset/disable()`, `syscall_loop()`, and `set_dscr()`.

Control flow: the test skips unless root and Power7-or-newer PMU support exist. It records original `rfi_flush` and `entry_flush`, disables RFI flushing, runs repeated syscall/cacheline loops under perf, checks miss thresholds with the original entry setting, toggles entry_flush, repeats, then restores both debugfs controls.

State and persistence behavior: mutates debugfs mitigation knobs and DSCR prefetch behavior. Intended restoration happens on normal control flow, but early failures after writes can leave mitigation state changed.

Dependencies and integration points: requires debugfs powerpc controls, perf hardware cache events, `flush_utils.c`, and `utils.c`.

Risks and test signals: PMU contention can distort counts. PASS/FAIL messages include miss totals and comparison thresholds; non-root or unavailable knobs result in skip.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/entry_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.c

Purpose: common cache-miss workload and DSCR-control support for the powerpc flush mitigation tests.

Important APIs/types/functions: defines inline `load()`, `syscall_loop()`, `syscall_loop_uaccess()`, `sigill_handler()`, and `set_dscr()`.

Control flow: the syscall loops repeatedly touch one cacheline per `CACHELINE_SIZE` across the supplied buffer, then issue either `getppid()` or `uname()` to trigger kernel entry/uaccess paths. `set_dscr()` installs a SIGILL handler once, then attempts `mtspr(SPRN_DSCR, val)`; the handler skips unavailable DSCR writes.

State and persistence behavior: static `init` ensures signal handler registration once, and static `warned` limits DSCR warning noise. DSCR changes affect the running thread's prefetch behavior until reset by callers.

Dependencies and integration points: depends on `reg.h`, `utils.h`, and `flush_utils.h`. Used by `rfi_flush.c`, `entry_flush.c`, and `uaccess_flush.c`.

Risks and test signals: signal-handler PC patching assumes instruction encoding for DSCR writes. If an unrelated SIGILL occurs, the handler aborts the process.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.h

Purpose: declares shared constants and helper prototypes for powerpc cache flush mitigation selftests.

Important APIs/types/functions: defines `CACHELINE_SIZE` as 128 and `PERF_L1D_READ_MISS_CONFIG` as the hardware L1D read-miss perf-event encoding. Declares `syscall_loop()`, `syscall_loop_uaccess()`, and `set_dscr()`.

Control flow: no executable control flow; it centralizes the perf config and workload interfaces for multiple C tests.

State and persistence behavior: no state. Callers own all buffers and perf counters.

Dependencies and integration points: requires Linux perf event constants to be visible through the including translation unit, normally via `utils.h` and kernel headers.

Risks and test signals: the fixed 128-byte cacheline assumption matches the targeted powerpc systems; using it elsewhere would skew expected miss counts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/mitigation-patching.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/mitigation-patching.sh

Purpose: stress-tests runtime patching of powerpc security mitigation knobs by toggling them concurrently while optional memory stress runs.

Important APIs/types/functions: `do_one()` toggles one mitigation file for `TIMEOUT` seconds and restores its original value. The script targets `barrier_nospec`, `stf_barrier`, `count_cache_flush`, `rfi_flush`, `entry_flush`, and `uaccess_flush`.

Control flow: it enters `/sys/kernel/debug/powerpc`, records current kernel taint, starts one background toggler per available mitigation file, optionally starts `stress-ng` or `stress`, waits for all jobs, then verifies the taint value has not changed.

State and persistence behavior: writes debugfs mitigation controls and restores each file's original value at the end of its toggler. It observes persistent kernel taint as the main health signal.

Dependencies and integration points: requires bash, debugfs powerpc mitigation knobs, and optionally stress tooling. It is registered as `TEST_PROGS` in the security Makefile.

Risks and test signals: abrupt termination can leave a mitigation file at the last toggled value. Failure is new taint or inability to enter debugfs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/mitigation-patching.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/rfi_flush.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/rfi_flush.c

Purpose: measures whether the `powerpc/rfi_flush` mitigation causes the expected L1D miss pattern on return-from-interrupt/syscall paths.

Important APIs/types/functions: `rfi_flush_test()` uses debugfs integer helpers, perf cache counters, `syscall_loop()`, and `set_dscr()`.

Control flow: after root and PMU skips, the test reads original RFI flush and optional entry flush state, disables entry flush if present, opens an L1D miss counter, disables prefetching through DSCR, runs a repeated syscall/cacheline loop, checks misses against threshold, toggles RFI flush, repeats, then restores original knobs.

State and persistence behavior: temporarily mutates debugfs and DSCR state. It closes the perf fd and restores knobs only on the normal path.

Dependencies and integration points: requires real debugfs mitigation controls, Power7+ PMU events, and `flush_utils.c`.

Risks and test signals: perf noise and scheduler contention may cause false failures. PASS/FAIL output reports total misses and threshold direction for each RFI setting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/rfi_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/spectre_v2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/spectre_v2.c

Purpose: cross-checks the kernel-reported Spectre v2 mitigation state with observed userspace branch prediction/misprediction behavior.

Important APIs/types/functions: `do_count_loop()`, `setup_event()`, `get_sysfs_state()`, `spectre_v2_test()`, `enum spectre_v2_state`, PMU event constants, and external `pattern_cache_loop()`/`indirect_branch_loop()` are core.

Control flow: the test reads `/sys/devices/system/cpu/vulnerabilities/spectre_v2`, maps the text to an enum, opens branch prediction/misprediction PMU events, runs an architecture-specific loop, computes miss percent, and compares that rate against expected bands for vulnerable/not-affected/flush/disabled/serialization states.

State and persistence behavior: perf events are opened, enabled for the loop, read, reported, and closed. No kernel mitigation state is changed.

Dependencies and integration points: requires Power8+ PMU support, `../pmu/event.c`, `utils.c`, and `branch_loops.S`.

Risks and test signals: PMU group running/enabled mismatch fails immediately. A very high miss rate with software count-cache flush returns skip because firmware may have disabled count cache without Linux knowing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/spectre_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/uaccess_flush.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/uaccess_flush.c

Purpose: measures whether the `powerpc/uaccess_flush` mitigation produces expected L1D misses around kernel user-access paths.

Important APIs/types/functions: `uaccess_flush_test()` uses debugfs reads/writes, perf event helpers, `syscall_loop_uaccess()`, and `set_dscr()`.

Control flow: the test skips unless root and Power7+ PMU support are available, reads original RFI/entry/uaccess flush settings, disables RFI and entry flushing, measures L1D misses for repeated `uname()` calls with the original uaccess setting, toggles uaccess flushing and repeats, then restores all three knobs.

State and persistence behavior: debugfs mitigation files and DSCR are temporary mutable state. Normal cleanup restores them; early hard failures may not.

Dependencies and integration points: depends on debugfs powerpc security knobs, perf counters, and common flush utilities.

Risks and test signals: the error message for missing uaccess debugfs says entry_flush, which can mislead diagnosis. PASS/FAIL messages provide miss totals and thresholds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/uaccess_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/Makefile

Purpose: builds the powerpc signal selftests covering plain signal delivery, TM signal delivery, sigreturn edge cases, and the TM-aware signal fuzzer.

Important APIs/types/functions: declares `TEST_GEN_PROGS` for `signal`, `signal_tm`, `sigfuz`, `sigreturn_vdso`, `sig_sc_double_restart`, `sigreturn_kernel`, and `sigreturn_unaligned`; adds `TEST_FILES := settings`.

Control flow: includes common kselftest `lib.mk` and powerpc `flags.mk`, compiles all programs with `../harness.c`, `../utils.c`, and `signal.S`, and adds targeted CFLAGS: `-mhtm` for `signal_tm`, `-pthread -m64` for `sigfuz`, and `-maltivec` generally.

State and persistence behavior: no runtime state; it produces binaries under `$(OUTPUT)`.

Dependencies and integration points: relies on the common selftest harness and powerpc assembly helper file for raw signal syscalls.

Risks and test signals: toolchains lacking HTM/Altivec flags or 64-bit support will fail at build time rather than runtime.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sig_sc_double_restart.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sig_sc_double_restart.c

Purpose: regression test for powerpc double syscall restart bugs when nested signals interrupt a restartable syscall.

Important APIs/types/functions: `raw_read()` issues a hand-written `sc` sequence with a branch just before it; `SIGUSR1_handler()` raises `SIGUSR2`; `test_restart()` drives the pipe/fork scenario.

Control flow: the child installs restarting handlers, duplicates the pipe read fd until it is 512 so interrupted `read()` places `ERESTARTSYS` in `r3`, and calls `raw_read()`. The parent signals `SIGUSR1`, writes data, and waits. If the kernel restarts twice, NIP retreats before the syscall and `raw_read()` returns sentinel `ENOANO`.

State and persistence behavior: only process signal masks, pipe fds, and child status are stateful. No filesystem state is persisted.

Dependencies and integration points: uses raw powerpc syscall ABI and kselftest `test_harness_set_timeout(10)`.

Risks and test signals: timing uses short `usleep()` delays to get the child blocked. Failure is explicit `ENOANO`, bad pipe data, abnormal child exit, or nonzero child status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sig_sc_double_restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigfuz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigfuz.c

Purpose: TM-aware signal and sigreturn fuzzer that mutates signal contexts, TM state, and MSR transaction-state bits to catch kernel crashes or hangs.

Important APIs/types/functions: option bits `ARG_MESS_WITH_TM_AT`, `ARG_MESS_WITH_TM_BEFORE`, `ARG_MESS_WITH_MSR_AT`, `ARG_FOREVER`; `mess_with_tm()`, `trap_signal_handler()`, `seg_signal_handler()`, `sigfuz_test()`, and `signal_fuzzer()`.

Control flow: multiple pthreads repeatedly fork children. Each child optionally enters or suspends TM, raises `SIGUSR1`, and lets the handler randomize `ucontext_t` and `uc_link` fields, including MSR, NIP, trap, DSISR, DAR, and other mcontext slots. SIGSEGV exits cleanly so fuzz iterations can continue.

State and persistence behavior: global arguments control mode, `tmp_uc` is per-process mutable heap state, and random context mutations are intentionally not reproducible unless the seed path is controlled.

Dependencies and integration points: uses HTM instructions inline, pthreads, signal APIs, `ucontext_t`, and powerpc register constants from `utils.h`.

Risks and test signals: this is a crash-resilience test, not a semantic validator. Success means no kernel crash under the fuzz run; user-space segfaults are expected and handled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigfuz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.S

Purpose: assembly helper for the signal delivery tests, providing raw `kill` syscalls both outside and inside suspended transactional memory.

Important APIs/types/functions: exports `signal_self(pid_t,int)` and `tm_signal_self(pid_t,int,long *)` using `FUNC_START/FUNC_END`, stack macros, `tbegin.`, `tsuspend.`, `tabort.`, and `tresume.`.

Control flow: `signal_self` loads syscall 37 and executes `sc`, converting error condition to a negative errno-like return. `tm_signal_self` starts a transaction, suspends to execute `kill`, stores the syscall result through the caller-provided pointer, aborts the transaction, resumes to force cleanup, and returns from the abort handler path.

State and persistence behavior: no persistent storage except the caller's `ret` word. It temporarily saves `ret` on stack across the syscall.

Dependencies and integration points: linked into signal Makefile tests and uses powerpc basic assembly stack macros.

Risks and test signals: hardware can abort between `tbegin.` and `tsuspend.`, so C callers must tolerate missing signal attempts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.c

Purpose: stress-tests that sending `SIGUSR1` to the current process is reliably delivered, including through a raw assembly syscall helper.

Important APIs/types/functions: uses external `signal_self()`, `signal_handler()`, global `signaled/fail`, and `test_signal()`.

Control flow: installs handlers for `SIGUSR1` and `SIGALRM`, first forks 1000 children that signal the parent, then performs `MAX_ATTEMPT` direct self-signal attempts via the assembly helper. Each iteration arms an alarm and busy-waits until the signal flag is set.

State and persistence behavior: `sig_atomic_t` globals carry signal state between handler and loop. No filesystem or durable state is changed.

Dependencies and integration points: built with `signal.S`, the selftest harness, and Altivec flags even though this file itself does not use vector operations directly.

Risks and test signals: busy waits rely on signal delivery and alarm timeout. Failure prints iteration and return code; test timeout is extended to 300 seconds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal_tm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal_tm.c

Purpose: verifies self-signalling from a suspended transaction and checks that the signal handler is not invoked while still in active transactional state.

Important APIs/types/functions: external `tm_signal_self()`, `signal_handler()`, `test_signal_tm()`, and TM helpers `have_htm()`, `htm_is_synthetic()`, `tcheck_active()`, and `tcheck_transactional()`.

Control flow: after installing handlers and skipping unsupported HTM, the loop calls `tm_signal_self()` repeatedly. A special untouched return sentinel means the transaction aborted too early and the iteration is retried. Otherwise the test expects a successful syscall result and eventual `SIGUSR1` delivery.

State and persistence behavior: global signal flags coordinate handler and main loop; per-iteration local sentinels distinguish abort timing from syscall failure.

Dependencies and integration points: built with `-mhtm`, `signal.S`, and `../tm/tm.h`.

Risks and test signals: HTM temporary aborts are expected. Persistent failures print TEXASR/TFIAR plus iteration context; alarms prevent indefinite waits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal_tm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_kernel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_kernel.c

Purpose: tests that sigreturn cannot restore execution to kernel addresses or kernel privilege by modifying signal context.

Important APIs/types/functions: `sigusr1_handler()` rewrites `UCONTEXT_NIA()` and masks `UCONTEXT_MSR()`, `fork_child()` raises the signal in a child, and `expect_segv()` verifies SIGSEGV.

Control flow: the parent installs a SA_SIGINFO handler, then repeatedly forks children with crafted return addresses covering kernel segments, kernel virtual ranges, no-man's land around task limits, and 0xd/0xe/0xf spaces. A second pass also tries clearing `MSR_PR`. A final no-address-change case proves PR clearing alone is blocked without killing normal return.

State and persistence behavior: volatile globals carry the requested NIA and MSR mask into children after fork.

Dependencies and integration points: depends on powerpc context access macros from `utils.h` and standard wait status checks.

Risks and test signals: expected success is child death by SIGSEGV for bad addresses and normal exit for the PR-only case.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_unaligned.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_unaligned.c

Purpose: validates that returning from a signal to an unaligned NIA does not trigger problematic kernel warnings or crashes.

Important APIs/types/functions: `sigusr1_handler()` ORs the low two bits into `UCONTEXT_NIA()`, and `test_sigreturn_unaligned()` installs it and raises `SIGUSR1`.

Control flow: the test registers a SA_SIGINFO handler, raises SIGUSR1 once, and returns. The handler mutates the saved next instruction address to be unaligned before sigreturn.

State and persistence behavior: no persistent state. The only state change is the signal frame's NIA modification.

Dependencies and integration points: uses `ucontext_t` and powerpc `UCONTEXT_NIA()` helper from `utils.h`.

Risks and test signals: this is mainly a kernel robustness smoke test. A pass is simply returning from `raise()` without fatal signal or harness failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_vdso.c

Purpose: tests powerpc signal delivery paths with the VDSO mapped normally, moved, and unmapped, covering both VDSO trampoline and stack trampoline fallback behavior.

Important APIs/types/functions: `search_proc_maps()` locates mappings; `sigusr1_handler()` increments `took_signal`; `test_sigreturn_vdso()` drives mapping changes using `mmap()`, `mremap()`, `munmap()`, and `mprotect()`.

Control flow: the test confirms `[vdso]` exists, sends a signal, remaps the VDSO to a fresh anonymous address and signals again, unmaps it entirely, makes the stack executable, and sends a third signal. Assertions verify each signal was delivered.

State and persistence behavior: mutates only the current process address space and stack protections. No external files are changed, though `/proc/self/maps` is read repeatedly.

Dependencies and integration points: relies on Linux VDSO mapping names, GNU `mremap` flags, and kselftest harness.

Risks and test signals: uses `assert()`, intentionally kept enabled. Failures abort immediately on mapping or signal delivery mismatch.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/Makefile

Purpose: builds the string primitive tests for powerpc `memcmp` and `strlen`, including 64-bit and optional 32-bit variants.

Important APIs/types/functions: `build_32bit` probes whether `$(CC) $(CFLAGS) -m32` works. `TEST_GEN_PROGS` always includes `memcmp_64` and `strlen`, and conditionally includes `memcmp_32` and `strlen_32`.

Control flow: `memcmp_64` links `memcmp.c` with `../utils.c` and compiles with `-m64 -maltivec`; `strlen` links `strlen.c` and `string.c`; all tests link `../harness.c`. Include path `-I$(CURDIR)` lets local kernel-style asm headers override normal kernel headers.

State and persistence behavior: no runtime state; build products live under `$(OUTPUT)`.

Dependencies and integration points: integrates with kselftest `lib.mk`, powerpc flags, and local `asm/` plus `linux/` compatibility headers.

Risks and test signals: the 32-bit probe is shell-fragile but only gates optional targets. Missing Altivec support or assembler opcode support can fail `memcmp_64` build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/cache.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/cache.h

Purpose: minimal local replacement for a kernel asm cache header needed by imported `strlen_32.S`.

Important APIs/types/functions: defines `IFETCH_ALIGN_BYTES 4`.

Control flow: no executable logic; used by assembly `.balign IFETCH_ALIGN_BYTES`.

State and persistence behavior: no state.

Dependencies and integration points: included through local `-I$(CURDIR)` when building stringloop assembly.

Risks and test signals: if imported assembly begins relying on more kernel cache definitions, this one-line shim would become insufficient.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc-opcode.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc-opcode.h

Purpose: local opcode macro shim for vector compare instructions that older assemblers may not know by mnemonic.

Important APIs/types/functions: defines `PPC_INST_VCMPEQUD_RC`, `PPC_INST_VCMPEQUB_RC`, field encoders `___PPC_RA/RB/RS/RT`, and macro emitters `VCMPEQUD_RC()` and `VCMPEQUB_RC()`.

Control flow: no runtime flow; macros emit `.long` instruction words in assembly.

State and persistence behavior: no state.

Dependencies and integration points: used by `memcmp_64.S` VMX loops to generate record-form vector compares.

Risks and test signals: incorrect opcode encodings would silently make the assembly test invalid or crash at runtime. Build success alone is not enough; `memcmp.c` comparisons validate behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc-opcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc_asm.h

Purpose: adapts kernel powerpc assembly naming and feature macros for userspace selftest builds.

Important APIs/types/functions: maps `_GLOBAL()` and `_GLOBAL_TOC()` to `FUNC_START(test_...)`, defines `CONFIG_ALTIVEC`, register aliases, stack offsets, and no-op feature-section macros.

Control flow: no executable logic; it shapes symbol names and assembly preprocessing.

State and persistence behavior: no state.

Dependencies and integration points: includes `<ppc-asm.h>` from the tools environment and is consumed by imported kernel-style assembly implementations.

Risks and test signals: no-op feature sections mean code guarded for CPU features may assemble unconditionally in the test context, so C tests must perform hardware capability skips where needed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/linux/export.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/linux/export.h

Purpose: minimal userspace stub for Linux `EXPORT_SYMBOL()` used by imported kernel string assembly.

Important APIs/types/functions: defines `EXPORT_SYMBOL(x)` as empty.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: lets `memcmp_32.S`, `memcmp_64.S`, and `strlen_32.S` compile outside the kernel.

Risks and test signals: adequate only for symbol export annotations; any future use of richer export macros would need expansion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/linux/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp.c

Purpose: randomized and boundary-sensitive harness for imported powerpc `test_memcmp()` assembly implementations.

Important APIs/types/functions: `enter_vmx_ops()`/`exit_vmx_ops()` track VMX critical-section pairing; `test_one()` compares libc `memcmp()` with `test_memcmp()` for many offsets/sizes; `testcase()` builds protected mappings and randomized data.

Control flow: the test maps four pages, places two buffers at page ends, unmaps following pages to catch overreads, then runs small and large randomized cases with single-byte and multi-byte differences. It verifies only sign equivalence, matching C `memcmp()` contract, and checks VMX enter/exit count returns to zero.

State and persistence behavior: `vmx_count` is global instrumentation state. Mappings are per-process and not fully unmapped at the end, acceptable for one-shot tests.

Dependencies and integration points: links to either `memcmp_64.S` or `memcmp_32.S`, plus `utils.c`; 64-bit path skips if Power ISA 2.07 vector compare support is absent.

Risks and test signals: randomness is time-seeded, so failures may be hard to reproduce exactly. Protected page placement is the main signal for illegal overread.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_32.S

Purpose: 32-bit powerpc `memcmp` implementation imported for selftest validation.

Important APIs/types/functions: exports `test_memcmp` through `_GLOBAL(memcmp)`, using word, halfword, and byte comparisons.

Control flow: the function compares length/4 words with `lwzx`, handles remaining halfword and byte tails, and returns 0 on equality or +/-1 style sign on word mismatch; tail byte/halfword paths return arithmetic differences.

State and persistence behavior: stateless leaf assembly routine.

Dependencies and integration points: assembled only when the Makefile detects 32-bit compiler support. Uses local `linux/export.h` and `asm/ppc_asm.h`.

Risks and test signals: tests validate sign, not exact magnitude, which matches `memcmp` requirements. Alignment and tail handling are covered by `memcmp.c` exhaustive offset loops.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_64.S

Purpose: optimized 64-bit powerpc `memcmp` implementation under test, including scalar and VMX paths for same-offset and different-offset buffers.

Important APIs/types/functions: exports `test_memcmp`; key macros include endian-adjusted `LH/LW/LD/LVS/VPERM`, `ENTER_VMX_OPS`, `EXIT_VMX_OPS`, and `LD_VSR_CROSS16B()`.

Control flow: short lengths or different 8-byte offsets start in byte loop. Same-offset aligned data uses scalar 8/32-byte loops, with an optional VMX path for lengths >= 4096 after a 32-byte precheck. Different-offset data aligns source 1 and either uses scalar long loops or VMX permutation to compare unaligned 16-byte chunks. Difference labels return sign according to the first unequal word/byte region.

State and persistence behavior: no durable state; VMX entry/exit callbacks update the C harness counter and ensure vector use is paired.

Dependencies and integration points: uses local opcode macros for vector compare record forms and C callbacks `enter_vmx_ops()`/`exit_vmx_ops()`. Built with `-m64 -maltivec`.

Risks and test signals: page-boundary tail logic deliberately falls back to byte comparison to avoid overread. The harness catches sign mismatches, page faults, and unpaired VMX sections.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/string.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/string.c

Purpose: simple C reference-style `test_strlen()` implementation copied from Linux `lib/string.c` for the `strlen` selftest target.

Important APIs/types/functions: defines `size_t test_strlen(const char *s)`.

Control flow: increments a pointer until the first NUL byte and returns the distance from the original pointer.

State and persistence behavior: stateless and read-only over caller memory.

Dependencies and integration points: linked into the default `strlen` target when not testing the 32-bit assembly implementation.

Risks and test signals: this simple implementation is effectively the baseline, so the surrounding `strlen.c` benchmark mostly validates harness behavior for this target.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen.c

Purpose: test and micro-benchmark harness for `test_strlen()` implementations over many offsets and NUL positions.

Important APIs/types/functions: `test_one()` compares libc `strlen()` with `test_strlen()` at every offset; `bench_test()` prints timing; `testcase()` creates randomized nonzero buffers and inserts NUL terminators.

Control flow: it first grows a string one byte at a time with nonzero random characters, validating after each write. It then performs randomized iterations where the final several bytes are set to zero in turn. Finally it runs timing loops for several string lengths.

State and persistence behavior: a single aligned heap buffer holds mutable test data. No external state is changed.

Dependencies and integration points: links either `string.c` or `strlen_32.S` as the `test_strlen` provider and uses kselftest harness.

Risks and test signals: mismatches are printed but `test_one()` does not abort or return failure on mismatch, so this file has weaker failure enforcement than `memcmp.c`. Build/runtime harness failure is otherwise the main signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen_32.S

Purpose: 32-bit powerpc optimized `strlen` implementation imported for selftest builds.

Important APIs/types/functions: exports `test_strlen` through `_GLOBAL(strlen)` and uses classic word-at-a-time zero-byte detection with `lomagic` and `himagic` constants.

Control flow: aligned strings loop over words, using subtract/and masks to detect any zero byte, then isolate the byte position with big-endian-safe logic. Misaligned strings adjust the first loaded word so bytes before the string cannot appear as NUL.

State and persistence behavior: stateless leaf routine.

Dependencies and integration points: built conditionally when 32-bit compiler support exists, using local `asm/cache.h`, `asm/ppc_asm.h`, and `linux/export.h`.

Risks and test signals: correctness depends on endian and misalignment bit manipulation. `strlen.c` compares against libc across offsets, but its mismatch handling is diagnostic-only.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/Makefile

Purpose: builds the standalone powerpc64 endian-switch syscall test and generates reversed-endian instruction bytes for part of the executable.

Important APIs/types/functions: `TEST_GEN_PROGS := switch_endian_test`; `EXTRA_CLEAN` includes generated object and `check-reversed.S`; `ASFLAGS` use `-nostdlib -m64`.

Control flow: `check.o` is converted with `objcopy --reverse-bytes=4` to a binary blob, then `hexdump` emits `.byte` directives into `check-reversed.S`. `switch_endian_test.S` includes that generated file so instructions execute correctly after endianness flips.

State and persistence behavior: generated intermediate files live under `$(OUTPUT)`.

Dependencies and integration points: depends on `objcopy`, `hexdump`, assembler support, kselftest `lib.mk`, and powerpc flags.

Risks and test signals: if byte reversal generation is wrong, the runtime test exits failure or hits illegal instructions. The test is intentionally low-level and does not link libc.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/check.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/check.S

Purpose: register-preservation checker used in both native and reversed byte order by the endian-switch test.

Important APIs/types/functions: checks r3-r8, r13-r14, r16-r31, LR, and preserved CR fields against a pattern in r15, then either exits with a failing value or performs another `switch_endian` syscall.

Control flow: starts with a `nop` that is illegal in reverse-endian to guard wrong execution mode, compares each expected register value, branches to failure if any mismatch occurs, otherwise loads `__NR_switch_endian` and reaches the trailing syscall site.

State and persistence behavior: no persistent state; uses register contents set by `switch_endian_test.S`.

Dependencies and integration points: included directly and also transformed into `check-reversed.S` by the Makefile.

Risks and test signals: exact register contract must match kernel syscall clobber rules. Failure exits immediately through `__NR_exit` with a diagnostic register value in r3.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/check.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/common.h

Purpose: shared assembly include for endian-switch tests, providing syscall number fallback and common powerpc asm includes.

Important APIs/types/functions: includes `<ppc-asm.h>` and `<asm/unistd.h>`, and defines `__NR_switch_endian` as 363 if missing.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: included by `check.S` and `switch_endian_test.S`.

Risks and test signals: fallback syscall number is architecture-specific; stale numbers would make the test fail on old or divergent headers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/switch_endian_test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/switch_endian_test.S

Purpose: libc-free executable that verifies `switch_endian` flips user endianness and preserves the expected register state across switches.

Important APIs/types/functions: `_start` loads a pattern, initializes CR/LR/GPRs, invokes `__NR_switch_endian`, includes reversed checker bytes, switches back with reversed `sc`, includes native `check.S`, then writes success or failure and exits.

Control flow: after the first syscall, an endian-sensitive `tdi` instruction detects whether execution mode changed. The generated reversed checker validates registers in opposite endian mode and switches back. Native checker validates again before printing success.

State and persistence behavior: all state is register-local plus static success/failure message strings. No files are modified.

Dependencies and integration points: depends on generated `check-reversed.S`, direct Linux syscall ABI, and `common.h`.

Risks and test signals: any clobbered register, failed endian switch, or wrong generated bytes leads to failure message or abnormal termination.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/switch_endian_test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/Makefile

Purpose: builds powerpc syscall ABI tests for unmuxed IPC syscalls and RTAS syscall filtering.

Important APIs/types/functions: `TEST_GEN_PROGS := ipc_unmuxed rtas_filter`; includes common kselftest make files and adds `$(KHDR_INCLUDES)`.

Control flow: both tests link `../harness.c` and `../utils.c`.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: requires kernel headers for syscall numbers and RTAS ABI definitions.

Risks and test signals: missing headers can remove IPC cases or fail RTAS compilation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc.h

Purpose: declarative list of IPC syscall numbers used twice by `ipc_unmuxed.c` to generate and run tests.

Important APIs/types/functions: conditionally invokes `DO_TEST(name, __NR_name)` for SysV semaphore, message queue, and shared memory calls when each syscall number is defined.

Control flow: no standalone flow; including file behavior is defined by the current `DO_TEST` macro.

State and persistence behavior: none.

Dependencies and integration points: included by `ipc_unmuxed.c` first to generate functions and again to execute them.

Risks and test signals: if built with old headers defining none of the syscalls, the caller skips rather than falsely passing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc_unmuxed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc_unmuxed.c

Purpose: verifies that powerpc exposes direct/unmuxed SysV IPC syscall numbers rather than returning ENOSYS.

Important APIs/types/functions: macro-generated `test_<name>()` functions call `syscall(_num, -1, 0, 0, 0, 0, 0)` and treat `errno == ENOSYS` as failure. `ipc_unmuxed()` runs all generated cases.

Control flow: the file includes `ipc.h` once to emit static test functions and once to execute them while counting tests. If no syscall numbers were available at build time, it skips.

State and persistence behavior: no persistent IPC objects are intentionally created because invalid arguments are supplied.

Dependencies and integration points: depends on kernel headers defining `__NR_*` and kselftest `FAIL_IF/SKIP_IF`.

Risks and test signals: this only checks syscall implementation presence, not semantic correctness. Unexpected errno values other than ENOSYS are accepted as proof the syscall exists.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc_unmuxed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/rtas_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/rtas_filter.c

Purpose: tests kernel filtering of the powerpc RTAS syscall, ensuring permitted calls pass and prohibited or out-of-RMO buffers are rejected.

Important APIs/types/functions: `struct rtas_args`, `struct region`, `get_property()`, `rtas_token()`, `read_kregion_bounds()`, `rtas_call()`, and `test()` are core.

Control flow: helper functions read RTAS tokens from `/proc/device-tree/rtas`, build big-endian RTAS argument blocks, and call `__NR_rtas`. The test checks `get-time-of-day`, `nvram-fetch`, reads `/proc/ppc64/rtas/rmo_buffer`, then probes permitted and invalid buffer ranges for RTAS calls.

State and persistence behavior: reads firmware/procfs state only; no persistent RTAS mutation is intended.

Dependencies and integration points: requires powerpc RTAS firmware interfaces, procfs/device-tree paths, and `utils.c` file allocation helpers.

Risks and test signals: unavailable RTAS calls are treated as skip-like acceptable outcomes. Buffer-boundary checks depend on parsing RMO region data accurately.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/rtas_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/Makefile

Purpose: builds the main powerpc transactional-memory selftest suite.

Important APIs/types/functions: groups signal-context checks in `SIGNAL_CONTEXT_CHK_TESTS` and adds many `TEST_GEN_PROGS`, including syscall, signal, SPR, TAR, trap, unavailable, poison, and VMX copy tests.

Control flow: all binaries link `../harness.c` and `../utils.c`, with global `CFLAGS += -mhtm`. Selected targets add `-pthread`, `-m64`, `-mvsx`, `-O0`, kernel header includes, or PMU support; signal-context checks depend on `tm-signal.S`.

State and persistence behavior: build-only file; output binaries and `settings` test file are the generated state.

Dependencies and integration points: integrates with kselftest `lib.mk`, powerpc flags, HTM-capable compiler, and architecture-specific assembly helpers.

Risks and test signals: unsupported compiler flags or missing HTM instruction support fail at build time. Many runtime tests skip on systems without real HTM.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-exec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-exec.c

Purpose: verifies that a suspended transaction does not survive `exec()`, and that post-exec TM startup is not reported as nested.

Important APIs/types/functions: `test_exec()` starts/suspends a transaction and calls `execl()` on its own path with `--child`; `after_exec()` starts a fresh transaction and checks `failure_is_nesting()`.

Control flow: parent mode skips if HTM is unavailable/synthetic, enters suspended TM, then replaces itself with the same binary. Child mode repeats a TM begin/suspend sequence and fails if the failure code indicates nesting from a stale pre-exec transaction.

State and persistence behavior: `path` stores `argv[0]`; process image replacement is the key state transition. No file state is changed.

Dependencies and integration points: uses `tm.h` failure-code helpers and kselftest harness only in parent mode.

Risks and test signals: `execl()` failure is a test failure. The child path returns directly rather than through `test_harness()`, which is intentional for exec mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-fork.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-fork.c

Purpose: smoke-tests entering the kernel through a `fork` syscall while in an active hardware transaction.

Important APIs/types/functions: `test_fork()` emits inline assembly with `tbegin.`, syscall number 2, `sc`, and `tend.`.

Control flow: after HTM skips, the test starts a transaction and executes the fork syscall directly. Reaching the end without kernel crash or process failure is treated as pass.

State and persistence behavior: a fork may create a child depending on transaction/syscall behavior, but the test does not manage child state explicitly because it is probing crash behavior.

Dependencies and integration points: depends on real HTM and raw powerpc syscall ABI.

Risks and test signals: it is intentionally shallow and does not verify child cleanup or specific failure code. Its useful signal is absence of kernel crash and harness completion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-poison.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-poison.c

Purpose: detects leakage of FP or VMX register state between parent and child across TM context switching on the same CPU.

Important APIs/types/functions: `tm_poison_test()` binds parent and child to one picked online CPU, child writes poison to f31/vr31, and parent repeatedly checks f31 then vr31 inside transactions.

Control flow: after HTM skips and CPU affinity setup, the child loops yielding and writing poison. The parent sets target registers to 1, then uses time-base-limited transactional loops to read back f31 and vr31; any value other than 1 indicates leaked state. The child is killed at the end.

State and persistence behavior: CPU affinity, live child process, FP/VMX registers, and time-base loop variables are the only state. No persistent files.

Dependencies and integration points: requires VSX move instructions, scheduler affinity, and real HTM. Harness timeout is extended to about 250 seconds.

Risks and test signals: long runtime and same-CPU scheduling are deliberate. Failure prints leaked register value and returns nonzero.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-poison.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-resched-dscr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-resched-dscr.c

Purpose: verifies DSCR SPR preservation when a suspended transaction is doomed by rescheduling/context switch.

Important APIs/types/functions: `test_body()` sets DSCR, begins/suspends TM, loops on `tcheck` until doomed, records DSCR and TEXASR; `tm_resched_dscr()` wraps it in `eat_cpu()`.

Control flow: the loop repeats until the transaction abort cause is reschedule. For that cause, it compares DSCR after reclaim with the pre-transaction value and reports OK/FAIL.

State and persistence behavior: DSCR is thread SPR state; no external state. The transaction may repeat many times until a suitable reschedule abort occurs.

Dependencies and integration points: depends on HTM, `../pmu/lib.h` `eat_cpu()`, SPR constants, and TM failure-code encodings.

Risks and test signals: could spin for a long time on systems that do not reschedule the thread as expected. Failure is explicit DSCR mismatch.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-resched-dscr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-fpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-fpu.c

Purpose: verifies signal frame placement of checkpointed and speculative nonvolatile FPR state when a signal is delivered during TM.

Important APIs/types/functions: `tm_signal_self_context_load()` assembly helper seeds contexts; `signal_usr1()` checks `uc_mcontext.fp_regs`; `tm_signal_context_chk_fpu()` loops until `MAX_ATTEMPT` or mismatch.

Control flow: the helper loads first-context FPR14-FPR31 values, begins/suspends a transaction, loads second-context values, and sends SIGUSR1. The handler expects checkpointed values in the primary context and speculative values in `uc_link`.

State and persistence behavior: static `fps[]` contains expected first and second context values. `broken` persists the first detected mismatch.

Dependencies and integration points: depends on `tm-signal.S`, HTM, signal frame `ucontext_t`, and FPU register layout.

Risks and test signals: hardware aborts before suspend can make helper delivery intermittent, so the test loops many times. Mismatches print register names and expected/actual values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-gpr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-gpr.c

Purpose: validates that nonvolatile GPR checkpoint and speculative states are placed in the correct signal contexts for TM signal delivery.

Important APIs/types/functions: expected `gprs[]` covers r14-r31 for first and second contexts; `signal_usr1()` compares `gp_regs`; `tm_signal_context_chk_gpr()` drives repeated helper calls.

Control flow: after installing the signal handler and HTM skips, the test repeatedly calls `tm_signal_self_context_load(pid, gprs, NULL, NULL, NULL)`. The handler checks primary `ucontext` for checkpointed values and `uc_link` for speculative values.

State and persistence behavior: `broken` and `fail` are signal-visible globals. Expected data is static.

Dependencies and integration points: uses `tm-signal.S` and powerpc signal frame register indices.

Risks and test signals: mismatches are printed with GPR number and expected value. Helper return must equal pid or the test fails immediately.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-gpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vmx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vmx.c

Purpose: verifies VMX/Altivec nonvolatile register state is split correctly between checkpointed and speculative signal contexts under TM.

Important APIs/types/functions: `vms[]` holds expected `vector int` values for vr20-vr31 in both contexts; `signal_usr1()` compares `uc_mcontext.v_regs->vrregs`; `tm_signal_context_chk()` invokes `tm_signal_self_context_load()`.

Control flow: the assembly helper loads first and second VMX values around a suspended transaction and sends SIGUSR1. The handler compares primary context VMX20-31 against first half of `vms[]` and `uc_link` VMX20-31 against the second half.

State and persistence behavior: static vector expectations and global `broken` carry state. No external persistence.

Dependencies and integration points: requires VMX signal frame layout, Altivec compiler support, real HTM, and `tm-signal.S`.

Risks and test signals: mismatch diagnostics print actual and expected vector hex. The printed second-context label uses `NV_VMX_REGS + i` instead of `VMX20 + i`, a diagnostic-only numbering issue.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vsx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vsx.c

Purpose: validates VSX state reconstruction from FP and VMX-reserve parts of the signal frame for checkpointed and speculative TM contexts.

Important APIs/types/functions: `vsxs[]` holds expected vsr20-vsr31 values; `signal_usr1()` reconstructs each VSX register from `fp_regs` high doubleword and the least-significant VSX slots after `v_regs`; `tm_signal_context_chk()` drives helper calls.

Control flow: the helper seeds VSX values before and during a suspended transaction, then sends SIGUSR1. The handler rebuilds and compares primary-context VSX values and `uc_link` values separately.

State and persistence behavior: global `broken/fail` signal test outcome; expected vectors are static.

Dependencies and integration points: depends on powerpc UAPI signal frame layout, VSX/Altivec compiler support, real HTM, and `tm-signal.S`.

Risks and test signals: the test encodes detailed assumptions about `mcontext_t.v_regs` and VSX/FPR overlap. Mismatches print compact byte dumps and expected vector words.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-chk-vsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-force-tm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-force-tm.c

Purpose: stress-tests sigreturn handling when a signal handler forces MSR[TS] in the saved context and induces page faults/segfault recovery.

Important APIs/types/functions: `usr_signal_handler()` allocates and installs a `uc_link`, copies mcontext, sets `MSR_TS_S`, and forks; `seg_signal_handler()` increments `count` and restores `init_context`; `tm_trap_test()` loops through `COUNT_MAX`.

Control flow: each iteration allocates a fresh alternate signal stack, marks it cold with `madvise`, installs handlers, raises SIGUSR1, and either continues or recovers from SIGSEGV through `setcontext()`. The test is designed to reveal kernel crashes, not return semantic failures.

State and persistence behavior: intentionally leaks mmap'd contexts/stacks to force heap growth and page faults. `init_context` and volatile `count` preserve loop progress across segfault recovery.

Dependencies and integration points: requires HTM and ppc64le; uses signal alt stacks, `mmap`, `madvise`, `fork`, and `ucontext_t`.

Risks and test signals: the test returns success unless the kernel crashes/hangs or process setup calls fail. It skips non-64-bit LE environments.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-context-force-tm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-msr-resv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-msr-resv.c

Purpose: verifies sigreturn rejects reserved TM MSR transaction-state bit combinations by delivering SIGSEGV instead of crashing.

Important APIs/types/functions: `signal_usr1()` sets `uc_link` and ORs invalid TM bits into saved MSR; `signal_segv()` exits success only when `segv_expected` is set; `tm_signal_msr_resv()` installs both handlers.

Control flow: after HTM skip, the test raises SIGUSR1. The handler mutates the signal context to invalid TM state and marks SIGSEGV expected. Returning from the handler should trigger kernel validation and SIGSEGV, which exits 0.

State and persistence behavior: global `segv_expected` synchronizes expected failure path.

Dependencies and integration points: handles different 64-bit vs 32-bit mcontext MSR access paths and uses `tm.h`.

Risks and test signals: reaching normal control flow after `raise()` is failure. Success is an expected SIGSEGV caught by the handler.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-msr-resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-pagefault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-pagefault.c

Purpose: stresses kernel TM signal handling when signal-stack and signal-frame memory faults are serviced by userfaultfd.

Important APIs/types/functions: `get_uf_mem()`, `fault_handler_thread()`, `setup_uf_mem()`, `signal_handler()`, `have_userfaultfd()`, and `tm_signal_pagefault()` coordinate userfaultfd-backed memory and TM traps.

Control flow: the test sets up a userfaultfd-managed region and a fault-handler thread that copies backing data into faulting pages. It installs an alt stack from that region, handles SIGTRAP by redirecting `v_regs`, TM `v_regs`, and `uc_link` into userfaultfd memory, then triggers SIGTRAP once in active TM and once in suspended TM.

State and persistence behavior: `uf_mem`, `backing_mem`, offsets, and handler thread are process-global. Faulting pages are populated lazily with saved backing data.

Dependencies and integration points: requires HTM, non-synthetic TM, `userfaultfd`, pthreads, signal alt stack, and powerpc signal frame layout.

Risks and test signals: timeout is only 2 seconds because bugs may hang the kernel path. Failure appears as setup errors, timeout, or process crash.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-pagefault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-sigreturn-nt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-sigreturn-nt.c

Purpose: tests returning from a signal handler while CPU is suspended in a transaction but the user context does not explicitly set MSR transaction-state bits.

Important APIs/types/functions: `trap_signal_handler()` executes `tbegin.; tsuspend.;` and advances saved NIP; `tm_signal_sigreturn_nt()` installs it for SIGTRAP and raises SIGTRAP.

Control flow: after HTM skips, SIGTRAP enters the handler, which creates a suspended transaction and adjusts NIP to skip the trap on return. The test succeeds if sigreturn handles this state without crashing.

State and persistence behavior: no external state; CPU TM state is intentionally altered inside the handler.

Dependencies and integration points: real HTM and powerpc ucontext register access are required.

Risks and test signals: this is a robustness test with success as normal return. Synthetic TM is skipped.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-sigreturn-nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-stack.c

Purpose: verifies kernel signal delivery from TM does not reclaim twice or crash when the user stack pointer is invalid.

Important APIs/types/functions: `tm_signal_stack()` forks a child; child installs `signal_segv()`, sets r1 to zero, enters/suspends TM, then faults by loading from NULL stack.

Control flow: the parent waits for child termination and treats any child exit as evidence the machine did not crash. The child should not actually run the SIGSEGV handler because its stack is invalid.

State and persistence behavior: child process and signal disposition only. No persistent state.

Dependencies and integration points: requires real HTM and raw inline assembly control of stack pointer.

Risks and test signals: intentionally dangerous; useful signal is absence of kernel crash. Comments contain typos but behavior is clear.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal.S

Purpose: shared assembly helper that loads first and second register contexts and sends SIGUSR1 while in a suspended transaction for signal-frame validation tests.

Important APIs/types/functions: exports `tm_signal_self_context_load(pid,gprs,fps,vms,vss)` and uses `load_gpr`, `load_fpu`, `load_vmx`, and `load_vsx` helpers from included assembly headers.

Control flow: the routine saves nonvolatile/vector state, loads non-transactional expected context from non-NULL arrays, starts a transaction, suspends, loads transactional/speculative expected context from the second half of each array, performs raw `kill(SIGUSR1)`, aborts/resumes to force cleanup, then restores saved state and returns.

State and persistence behavior: uses stack storage for parameters and saved registers. It mutates CPU register files only for the duration of the test.

Dependencies and integration points: linked into TM signal-context tests and depends on `basic_asm.h`, `gpr_asm.h`, `fpu_asm.h`, `vmx_asm.h`, and `vsx_asm.h`.

Risks and test signals: hardware may abort before the signal is sent; callers therefore loop and validate the returned pid. Stack-frame offsets and vector save/restore must remain consistent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-sigreturn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-sigreturn.c

Purpose: verifies sigreturn from inside a suspended transaction reclaims/discards the transaction before restoring TM SPRs.

Important APIs/types/functions: `handler()` starts/suspends a transaction in the SIGSEGV handler; `tm_sigreturn()` triggers SIGSEGV inside an active transaction and checks abort-path return code.

Control flow: the main test installs a SIGSEGV handler, begins a transaction, stores to address zero to fault, and expects signal handling plus sigreturn to abort the transaction. The final `ret` value must be 2 from the abort handler path.

State and persistence behavior: local `ret` communicates assembly path outcome; no external state.

Dependencies and integration points: requires real HTM and ppc64le.

Risks and test signals: normal transaction continuation after fault is failure. The test exits explicitly with success/failure rather than returning normally from the test function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall-asm.S

Purpose: assembly syscall primitives for testing `sc` and `scv` behavior in active and suspended transactions.

Important APIs/types/functions: exports `getppid_tm_active`, `getppid_tm_suspended`, `getppid_scv_tm_active`, and `getppid_scv_tm_suspended`; defines `scv` instruction encoding macro.

Control flow: active variants begin a transaction and issue getppid directly, expecting transaction abort. Suspended variants begin, suspend, issue syscall, resume, and commit. Abort handler paths return -1.

State and persistence behavior: stateless aside from CPU TM state and return registers; `scv` variants use stack save/restore macros.

Dependencies and integration points: called by `tm-syscall.c` and requires syscall number headers plus assembler support for emitted `scv`.

Risks and test signals: incorrect abort return handling would confuse C failure-code checks. `scv` paths are only used when hardware capability reports support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall.c

Purpose: verifies syscalls from active transactions abort persistently with syscall failure code, while syscalls from suspended transactions succeed, for both `sc` and optional `scv`.

Important APIs/types/functions: `getppid_tm()` wraps assembly helpers with retry/failure-code logic; `tm_syscall()` runs for `TEST_DURATION` seconds and checks failure helpers from `tm.h`.

Control flow: each iteration calls suspended getppid and expects success, then active getppid and expects -1 plus persistent syscall failure. If `PPC_FEATURE2_SCV` is present, it repeats the same checks with `scv`.

State and persistence behavior: global `retries` counts temporary TM aborts. No external state.

Dependencies and integration points: requires `PPC_FEATURE2_HTM_NOSC`, non-synthetic TM, `tm-syscall-asm.S`, and powerpc failure-code builtins.

Risks and test signals: temporary aborts are retried up to `TM_RETRIES`; exceeding that prints TEXASR/TFIAR and exits. Test duration is time-based.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tar.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tar.c

Purpose: checks TAR rollback and suspended-mode persistence across transaction commit/abort.

Important APIs/types/functions: `test_tar()` loops inline assembly that writes SPRN_TAR before, inside, and while suspended in a transaction.

Control flow: each loop sets TAR=1, begins a transaction, repeatedly sets TAR=2 inside TM and TAR=3 while suspended, then either commits and expects TAR=3 or aborts and expects rollback to TAR=1. Encoded result values 7 and 9 are accepted.

State and persistence behavior: `num_loops` is configurable from argv; TAR is per-thread SPR state.

Dependencies and integration points: requires real HTM, ppc64le, and `SPRN_TAR`.

Risks and test signals: low iteration counts can false-pass; default is 10000. Any unexpected encoded result indicates TAR corruption.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tmspr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tmspr.c

Purpose: stress-tests preservation of TM SPRs (`TFIAR`, `TFHAR`, and `TEXASR`) across many threads and transactions.

Important APIs/types/functions: `tfiar_tfhar()` writes unique thread values and repeatedly reads them back; `texasr()` repeatedly aborts transactions and checks `TEXASR_FS`; `test_tmspr()` launches many pthreads.

Control flow: thread count is 10 times online CPUs. Even-indexed threads validate TFIAR/TFHAR stability; odd-indexed threads validate TEXASR failure summary after `tabort`. Main joins all and returns based on global `passed`.

State and persistence behavior: global `num_loops` and `passed`; per-thread SPR state; no external persistence.

Dependencies and integration points: requires pthreads and real HTM.

Risks and test signals: `passed` is unsynchronized but only transitions from 1 to 0, sufficient for this stress test. Failures are reported through final nonzero status without detailed offending values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tmspr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-trap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-trap.c

Purpose: checks that thread endianness is not inadvertently flipped on traps taken in TM when FP/VEC state is unavailable or after context-switch pressure.

Important APIs/types/functions: `trap_signal_handler()` manipulates MSR.LE and NIP based on trap event and machine endianness; `ping()` executes endian-sensitive instruction sequence in TM; `pong()` induces context switches; `tm_trap_test()` binds both threads to one CPU.

Control flow: after HTM skips, the test installs SIGTRAP and SIGUSR1 handlers, creates two CPU-affined threads, waits for context-switch pressure, and executes a sequence whose native/opposite-endian interpretations route to success or failure labels. Handler logic adapts for LE and BE machines.

State and persistence behavior: globals `trap_event`, `le`, `success`, thread IDs, and exit flag coordinate the two threads and signal handler.

Dependencies and integration points: requires real HTM, pthread affinity, raw instruction encodings, and powerpc signal context MSR/NIP access.

Risks and test signals: very timing and architecture sensitive. Success prints that endianness did not flip; failure returns nonzero after routing to failure label.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-unavailable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-unavailable.c

Purpose: verifies FP, VEC, and VSX unavailable exceptions inside transactions do not corrupt checkpointed FP/VEC register state across all MSR.FP/MSR.VEC pre-touch combinations.

Important APIs/types/functions: `struct Flags`, `expecting_failure()`, `is_failure()`, `tm_una_ping()`, `tm_una_pong()`, `test_fp_vec()`, and `tm_unavailable_test()`.

Control flow: a background pong thread yields on one CPU. For each unavailable exception type, the test runs ping cases with FP/VEC pre-touched or not. Inline assembly primes vs0/vs32 expected values, optionally enables FP/VEC, begins a transaction, executes the target unavailable instruction, captures CR and vector values, and validates expected failure cause plus register integrity.

State and persistence behavior: global `flags` carries selected case and accumulated result. Threads are CPU-affined; FP/VEC/VSX register state is local to the test thread.

Dependencies and integration points: requires real HTM, pthreads, ppc64, VSX, and no optimization assumptions (`-O0`) per Makefile.

Risks and test signals: retries tolerate reschedule/KVM aborts. Failure prints unexpected cause or corrupted FP/VEC values and exits nonzero; timeout is extended to 220 seconds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-unavailable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmx-unavail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmx-unavail.c

Purpose: focused stress test that VMX unavailable during a transaction does not corrupt checkpointed VMX0 after abort.

Important APIs/types/functions: `worker()` executes inline VMX/TM sequence; `tm_vmx_unavail_test()` launches 4x online CPU worker threads; global `passed` records corruption.

Control flow: each worker initializes VMX0 from a stack value, busy-waits to encourage VMX being turned off by the kernel, begins a transaction, executes a VMX instruction to trigger unavailable, then on abort compares VMX0 to the saved value. Mismatch prints TEXASR details.

State and persistence behavior: global `passed` is shared by worker threads. No persistent external state.

Dependencies and integration points: requires pthreads, VMX, ppc64, HTM, and `htmintrin.h`.

Risks and test signals: race/stress based, so absence of failure is not exhaustive. `passed` is unsynchronized but only clears to 0.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmx-unavail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmxcopy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmxcopy.c

Purpose: tests that kernel VMX copy loops during a page fault do not leak suspended transactional vector state into checkpointed state after abort.

Important APIs/types/functions: `test_vmxcopy()` creates a temp file mapping, uses VSR40, triggers a page faulting store while suspended, aborts, and compares vector value.

Control flow: the test maps file-backed pages, loads `vecin` into VSR40, begins a transaction, suspends, zeroes VSR40, stores into the mapping to force a kernel copy/page path, aborts, and stores VSR40 to `vecout`. If the transaction aborted, `vecout` must equal original `vecin`.

State and persistence behavior: temporary file is unlinked after mapping; mapped pages and fd are cleaned up on normal path. Vector register state is transient.

Dependencies and integration points: requires real HTM, ppc64le, VSX instructions, filesystem temp file support, and mmap.

Risks and test signals: uses assertions for setup. Failure prints leaked vector state and returns nonzero.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmxcopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm.h

Purpose: common HTM capability and failure-code helper header for powerpc transactional-memory selftests.

Important APIs/types/functions: `have_htm()`, `have_htm_nosc()`, `htm_is_synthetic()`, `failure_code()`, `failure_is_persistent()`, `failure_is_syscall()`, `failure_is_unavailable()`, `failure_is_reschedule()`, `failure_is_nesting()`, `tcheck()`, and `tcheck_*()` predicates.

Control flow: capability helpers query HWCAP2 bits. `htm_is_synthetic()` attempts `tbegin./tend.` up to `TM_RETRIES` and classifies Power10 synthetic TM by persistent implementation-specific failures. Failure helpers decode TEXASRU bits and `tcheck` condition result.

State and persistence behavior: stateless inline functions. They read CPU SPR/builtin state from the current thread.

Dependencies and integration points: includes `<asm/tm.h>`, `utils.h`, and `reg.h`, and is widely included by ptrace, signal, and TM tests.

Risks and test signals: synthetic detection is heuristic by necessity and loops to reduce false classification. Missing HWCAP definitions cause printed messages and false capability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/utils.c

Purpose: common userspace utility implementation for powerpc selftests, covering file I/O, auxv/HWCAP support, CPU affinity, debugfs/sysfs helpers, perf counters, MMU detection, and signal-handler stacking.

Important APIs/types/functions: key functions include `read_file()`, `read_file_alloc()`, `write_file()`, `read_auxv()`, `get_auxv_entry()`, `read_debugfs_int()`, `write_debugfs_int()`, `read_sysfs_file()`, `pick_online_cpu()`, `bind_to_cpu()`, `is_ppc64le()`, `perf_event_open_counter()`, `perf_event_enable/disable/reset()`, `using_hash_mmu()`, `push_signal_handler()`, and `pop_signal_handler()`.

Control flow: file helpers open/read/write with negative errno returns and parse helpers validate complete numeric input. CPU helpers inspect current affinity and prefer primary SMT threads. Perf helpers configure disabled group-capable counters excluding kernel/hypervisor/guest. Signal helpers install SA_SIGINFO handlers and return previous dispositions.

State and persistence behavior: static `auxv[4096]` caches raw auxiliary-vector reads only per call path; debugfs/sysfs write helpers can mutate kernel runtime state for callers. Affinity helpers can change process CPU mask.

Dependencies and integration points: used throughout powerpc selftests and depends on Linux UAPI, `utils.h`, and `FAIL_IF` style macros for some helper paths.

Risks and test signals: `read_file_alloc()` does not NUL-terminate buffers by itself, so callers parsing strings need care. Utility functions generally return negative errno, while some test-facing helpers call harness failure macros directly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/Makefile

Purpose: builds the VPHN associativity unpacking selftest.

Important APIs/types/functions: declares `TEST_GEN_PROGS := test-vphn`, includes kselftest make files, and sets `CFLAGS += -m64 -I$(CURDIR) -fno-strict-aliasing`.

Control flow: `test-vphn` links with `../harness.c`; `test-vphn.c` includes `vphn.c` directly for userspace testing.

State and persistence behavior: build-only file, no runtime state.

Dependencies and integration points: depends on local `asm/vphn.h`, powerpc 64-bit compiler support, and kselftest harness.

Risks and test signals: 32-bit builds are not targeted. Strict-aliasing is disabled because the parser views packed register bytes through different integer widths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/asm/vphn.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/asm/vphn.h

Purpose: userspace-visible VPHN constants and hcall prototype shared by the parser and its selftest.

Important APIs/types/functions: defines `VPHN_REGISTER_COUNT`, `VPHN_ASSOC_BUFSIZE`, `VPHN_FLAG_VCPU`, `VPHN_FLAG_PCPU`, and prototype `hcall_vphn()`.

Control flow: no executable logic.

State and persistence behavior: no state.

Dependencies and integration points: mirrors kernel VPHN ABI expectations for `H_HOME_NODE_ASSOCIATIVITY`.

Risks and test signals: buffer size calculation must match six 64-bit registers unpacked into 16/32-bit associativity cells plus length cell.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/asm/vphn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/test-vphn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/test-vphn.c

Purpose: table-driven userspace test for unpacking VPHN associativity data returned as six packed 64-bit hypervisor registers.

Important APIs/types/functions: `struct test`, `all_tests[]`, `test_one()`, and `test_vphn()` are central. The file defines endian conversion helpers and includes `vphn.c` directly.

Control flow: each fixture supplies six packed register values and an expected big-endian associativity property. `test_one()` calls `vphn_unpack_associativity()`, verifies the reported length, then checks elements `1..len-1`; `test_vphn()` reports each case through subunit `test_finish()`.

State and persistence behavior: all state is static test data and stack output buffer. No external state.

Dependencies and integration points: depends on local VPHN header, `utils.h`, `subunit.h`, and direct inclusion of the implementation under test.

Risks and test signals: the element loop uses `i < len`, so it does not check the final element when length is the number of data cells; this weakens coverage. Some malformed expected entries include trailing values that are therefore inert.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/test-vphn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/vphn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/vphn.c

Purpose: implementation for unpacking VPHN associativity register streams and, in kernel builds, issuing the VPHN hcall.

Important APIs/types/functions: static `vphn_unpack_associativity()` parses mixed-width fields. Kernel-only `hcall_vphn()` calls `plpar_hcall9(H_HOME_NODE_ASSOCIATIVITY)` and unpacks on success.

Control flow: the parser converts six native longs to big-endian 64-bit words, walks 16-bit fields, stops on `0xffff`, emits 15-bit values when the high bit is set, or combines a high-15-bit field with the next 16 bits for 32-bit values. It writes the data-cell count into output cell 0.

State and persistence behavior: stateless; caller owns packed and output buffers.

Dependencies and integration points: userspace selftest includes this file directly; kernel build path depends on `asm/hvcall.h`.

Risks and test signals: truncated 32-bit values at the end are handled by consuming the next field even if malformed. Output capacity is tied to `VPHN_ASSOC_BUFSIZE`; parser loop bounds protect against overrun.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/vphn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/Makefile

Purpose: builds prctl selftests on native x86 only.

Important APIs/types/functions: under `ifndef CROSS_COMPILE`, normalizes `ARCH` to `x86` and sets `TEST_PROGS` to TSC controls, anonymous VMA naming, and process-name tests.

Control flow: if the normalized architecture is x86, `all` builds the listed programs and includes `../lib.mk`; otherwise no tests are built from this Makefile.

State and persistence behavior: build-only. No runtime state.

Dependencies and integration points: intentionally excludes cross-compile and non-x86 for TSC-dependent tests, though the VMA/name tests are also gated by that condition here.

Risks and test signals: the coarse x86 gating means non-x86 environments will skip even architecture-neutral prctl tests in this source version.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/config

Purpose: kselftest config fragment requesting anonymous VMA naming support.

Important APIs/types/functions: contains `CONFIG_ANON_VMA_NAME=y`.

Control flow: none.

State and persistence behavior: no runtime state; informs kernel config requirements.

Dependencies and integration points: paired with `set-anon-vma-name-test.c`.

Risks and test signals: without this kernel option, anonymous VMA name prctl behavior may be unavailable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-ctxt-sw-stress-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-ctxt-sw-stress-test.c

Purpose: x86 stress test that PR_SET_TSC state is preserved correctly across context switches.

Important APIs/types/functions: `rdtsc()`, `sigsegv_expect()`, `segvtask()`, `sigsegv_fail()`, and `rdtsctask()` implement enabled/disabled TSC roles.

Control flow: main forks 100 children; even children enable TSC and spin reading it, odd children set `PR_TSC_SIGSEGV`, install a handler, and attempt `rdtsc()`. Any enabled SIGSEGV or disabled successful read prints fatal error.

State and persistence behavior: each child has independent prctl TSC mode and alarm timeout. Parent only waits for children.

Dependencies and integration points: x86 `rdtsc`, `PR_GET_TSC/PR_SET_TSC`, and signal delivery.

Risks and test signals: child failures call `exit(0)`, so parent status may not catch all printed fatal errors; this is a legacy stress pattern where stderr output is part of the signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-ctxt-sw-stress-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-on-off-stress-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-on-off-stress-test.c

Purpose: x86 stress test repeatedly toggling a process between TSC-enabled and TSC-SIGSEGV modes.

Important APIs/types/functions: `rdtsc()`, global `should_segv`, `sigsegv_cb()`, and `task()`.

Control flow: main forks 100 worker children. Each worker loops reading TSC, setting `PR_TSC_SIGSEGV`, expecting the next `rdtsc()` to fault, handler re-enables TSC and reads it once.

State and persistence behavior: `should_segv` tracks expected handler mode per child; prctl state is per-thread/process execution state.

Dependencies and integration points: x86 timestamp counter instruction and prctl TSC controls.

Risks and test signals: fatal conditions also exit 0 after printing, so automated pass/fail relies on absence of error output more than exit status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-on-off-stress-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-test.c

Purpose: basic x86 functional test for `PR_GET_TSC` and `PR_SET_TSC`.

Important APIs/types/functions: `rdtsc()`, `sigsegv_cb()`, and `tsc_names[]` provide read, fault handling, and diagnostics.

Control flow: the program reads TSC, gets current TSC mode, enables TSC, reads again, sets `PR_TSC_SIGSEGV`, then attempts `rdtsc()`. SIGSEGV handler confirms mode, re-enables TSC, and returns so the read can proceed.

State and persistence behavior: signal disposition and per-process TSC control state are mutated. No file state.

Dependencies and integration points: x86 inline assembly and Linux prctl constants, with local fallback definitions for older headers.

Risks and test signals: mostly diagnostic and exits success if the final flow completes; unexpected prctl errors are printed but do not always abort immediately.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-anon-vma-name-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-anon-vma-name-test.c

Purpose: tests `PR_SET_VMA` / `PR_SET_VMA_ANON_NAME` for naming anonymous VMAs.

Important APIs/types/functions: `rename_vma()` wraps prctl and returns negative errno; `was_renaming_successful()` parses `/proc/self/maps`; fixture `vma` owns anonymous and non-anonymous mappings.

Control flow: setup maps one anonymous private area and one non-anonymous private area. The test successfully names the anonymous VMA and confirms `[anon:goodname]` appears at the mapping start, then expects `-EINVAL` for a non-printable name and for a non-anonymous VMA.

State and persistence behavior: modifies only current process VMA metadata and reads `/proc/self/maps`. Teardown unmaps both regions.

Dependencies and integration points: uses `kselftest_harness.h`, `CONFIG_ANON_VMA_NAME`, and prctl VMA naming support.

Risks and test signals: `mmap(... MAP_PRIVATE, fd=0, offset=0)` for the non-anonymous mapping depends on fd 0 being mappable; in unusual test environments setup may fail before intended assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-anon-vma-name-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-process-name.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-process-name.c

Purpose: tests `PR_SET_NAME` and `PR_GET_NAME` and confirms `/proc/self/task/<pid>/comm` reflects the prctl name.

Important APIs/types/functions: `set_name()`, `check_is_name_correct()`, `check_null_pointer()`, and `check_name()` are exercised by the `rename_process` kselftest.

Control flow: the test sets a normal name and empty name, verifies `PR_GET_NAME`, checks that a NULL output pointer fails, then compares `PR_GET_NAME` with the thread comm file in procfs.

State and persistence behavior: changes current task name, visible through procfs for the duration of the process.

Dependencies and integration points: uses kselftest harness, Linux prctl process-name ABI, and `/proc/self/task`.

Risks and test signals: `check_name()` uses `fscanf("%s")`, so embedded whitespace names would not round-trip, but test names avoid whitespace. File handle is not explicitly closed in that helper.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/set-process-name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/Makefile

Purpose: builds a broad set of procfs selftests, including the fd and kthread tests researched in this subset.

Important APIs/types/functions: sets `CFLAGS += -Wall -O2 -Wno-unused-function`, `CFLAGS += $(TOOLS_INCLUDES)`, `LDFLAGS += -pthread`, and appends many `TEST_GEN_PROGS`.

Control flow: includes `../lib.mk` after listing test programs.

State and persistence behavior: build-only, generating test binaries under kselftest output.

Dependencies and integration points: relies on common proc test headers such as `proc.h` and kselftest build infrastructure.

Risks and test signals: this Makefile covers more tests than the current work item; build failures in unrelated proc tests can affect running the whole directory.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/config

Purpose: kselftest config fragment requiring procfs support.

Important APIs/types/functions: contains `CONFIG_PROC_FS=y`.

Control flow: none.

State and persistence behavior: no runtime state.

Dependencies and integration points: applies to the proc selftest directory.

Risks and test signals: without procfs enabled, all researched proc tests are invalid or skipped by environment rather than by this one-line file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-001-lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-001-lookup.c

Purpose: validates `/proc/self/fd/<fd>` lookup accepts only canonical numeric fd names and rejects junk, negative, and overflow-like names.

Important APIs/types/functions: `test_lookup_pass()`, `test_lookup_fail()`, `test_lookup()`, and helpers from `proc.h` such as `xreaddir()`, `xstrtoull()`, and `streq()`.

Control flow: the program unshares the file table, closes all open fds by reading `/proc/self/fd`, opens `/` so it becomes fd 0, tests lookup acceptance/rejection around that fd, then duplicates fd 0 to a high target fd and repeats tests.

State and persistence behavior: mutates the process fd table heavily after `unshare(CLONE_FILES)`. No external files are modified.

Dependencies and integration points: requires procfs fd symlinks, `O_PATH`, `CLONE_FILES` unshare, and proc test helper header.

Risks and test signals: uses `assert()` for all checks. Running under environments with unusual inherited fds is handled by wiping the fd table, but permissions/procfs restrictions can still fail early.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-001-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-002-posix-eq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-002-posix-eq.c

Purpose: verifies opening `/proc/self/fd/<fd>` and `/proc/thread-self/fd/<fd>` yields the same underlying file as the original fd.

Important APIs/types/functions: main uses `open()`, `fstat()`, and compares `st_dev`/`st_ino`.

Control flow: opens `/` as a directory fd, constructs both proc fd paths, opens them, stats all three descriptors, and asserts device/inode equality.

State and persistence behavior: opens three fds; no persistent filesystem changes.

Dependencies and integration points: requires procfs `self` and `thread-self` fd views.

Risks and test signals: only checks POSIX identity by dev/inode, not file flags or offsets. All failures are assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-002-posix-eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-003-kthread.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-003-kthread.c

Purpose: tests that `/proc/<kernel-thread>/fd/` is empty and rejects numeric fd lookups.

Important APIs/types/functions: `kernel_thread_fd()` identifies kernel threads by parsing `/proc/<pid>/stat` flags for `PF_KHTREAD`; `test_readdir()` checks only `.` and `..`; `test_lookup()` uses `statx` to verify ENOENT for many names.

Control flow: starting at pid 2, the program scans pids below 1024 until it can open an fd directory for a kernel thread. It then validates directory entries and negative/overflow fd lookup rejection.

State and persistence behavior: opens procfs descriptors only. No process or kernel state is changed.

Dependencies and integration points: depends on procfs exposing task flags in stat, accessible kernel thread proc entries, and `SYS_statx`.

Risks and test signals: typo `PF_KHTREAD` names the kernel-thread flag constant locally but value is what matters. Non-root or hidepid settings may prevent finding a suitable pid, returning failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-003-kthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-2-is-kthread.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-2-is-kthread.c

Purpose: verifies procfs reports pid 2 (`kthreadd`) as a kernel thread via `/proc/2/status`.

Important APIs/types/functions: main opens `/proc/2/status`, reads it into a buffer, and asserts it contains `Kthread:	1
`.

Control flow: single open/read/string-search sequence with assertions.

State and persistence behavior: read-only procfs access; no persistent state.

Dependencies and integration points: assumes pid 2 is kthreadd and procfs status includes the Kthread field.

Risks and test signals: containers, pid namespaces, hidepid, or kernels without the field can fail the test even if procfs fd behavior is otherwise correct.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-2-is-kthread.c -->
