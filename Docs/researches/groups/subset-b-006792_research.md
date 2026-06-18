# Research: subset-b-006792

This grouped report covers the requested ARM64 floating-point/vector, guarded control stack, and MTE selftest files. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S

Purpose: standalone nolibc-style AArch64 assembly benchmark for measuring `getpid` syscall overhead before and after SVE use. It isolates libc/toolchain FP side effects by issuing raw syscalls and timer reads.

Important APIs and functions: `_start` is the only entry point. `test_loop` is a macro that times a fixed loop using `CNTVCT_EL0`, `__NR_getpid`, optional per-iteration SVE work, and `putdec`/`puts` helpers from `assembler.h`. It probes SVE by reading `ID_AA64PFR0_EL1` and uses `rdvl` to establish active vector length.

Control flow: print iteration count, time `getpid` with no SVE, check SVE support, touch SVE once, time subsequent syscalls, time syscalls with `rdvl` before each `svc`, then time no-SVE work again after SVE has been used. It exits via raw `__NR_exit`.

State and persistence: no persistent state; only registers, timer values, and stdout output. Dependencies include `asm/unistd.h`, `assembler.h`, privileged-readable architectural feature registers, and SVE instruction availability.

Integration points: built as an arm64 selftest helper/benchmark in the FP test folder. It complements correctness tests by detecting syscall overhead changes caused by lazy SVE/FPSIMD state management.

Risks: direct `ID_AA64PFR0_EL1` access assumes userspace visibility on the target kernel/config; benchmark results are noisy under virtualization and CPU frequency changes. It is not TAP-plan based and reports raw timings.

Test signals: successful output has timing lines for "No SVE", "SVE used once", "SVE used per syscall", and "No SVE after SVE"; unsupported SVE prints a skip-like message and exits cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S

Purpose: assembly half of the comprehensive FP/SVE/SME ptrace test. It loads known register state from globals, stops for parent ptrace manipulation, saves resulting state back to globals, stops again, and exits streaming mode before returning.

Important APIs and symbols: exports `load_and_save(int flags)`. It consumes `HAVE_SVE`, `HAVE_SME`, `HAVE_SME2`, `HAVE_FA64`, and `HAVE_FPMR` from `fp-ptrace.h`, and SME helper macros from `sme-inst.h`. It accesses globals such as `v_in/out`, `z_in/out`, `p_in/out`, `ffr_in/out`, `za_in/out`, `zt_in/out`, `svcr_in/out`, `sve_vl_out`, `sme_vl_out`, and `fpmr_in/out`.

Control flow: save callee scratch registers, load FPSIMD V registers unconditionally, optionally set SVCR and load ZA/ZT for SME, optionally load SVE or streaming SVE Z/P/FFR state, optionally load FPMR, then execute `brk #0`. After the parent writes regsets, it saves FPSIMD/FPMR/SME/SVE/FFR state back to memory, executes a second `brk #0`, clears SME state, restores temporaries, and returns.

State and persistence: state is intentionally global and shared with `fp-ptrace.c` via fork-inherited virtual addresses. The BRK instructions are synchronization points; the parent advances PC by 4 to continue.

Dependencies and integration: tied directly to `fp-ptrace.c` and Linux NT_ARM_* ptrace regset semantics. It uses encoded SME/SME2 instructions for portability across assemblers.

Risks: any mismatch in global layout, VL selection, or SVCR mode invalidates comparisons. FFR is skipped when base SME lacks FA64, and streaming mode must be cleared before returning to avoid contaminating the C runtime.

Test signals: correct behavior is observed through parent-side ptrace reads and memory comparisons; failures surface as kselftest mismatch diagnostics in `fp-ptrace.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c

Purpose: exhaustive ptrace selftest for arm64 FPSIMD, SVE, streaming SVE, SME ZA, SME2 ZT, SVCR, vector lengths, and FPMR. It verifies both initial ptrace visibility and effects of ptrace writes across mode/VL transitions.

Important APIs, types, and functions: `struct test_config` captures input and expected SVE/SME VL plus SVCR state; `struct test_definition` describes supported/write/expected callbacks. Feature probes use `getauxval(AT_HWCAP/HWCAP2)`. Regset operations use `PTRACE_GETREGSET`/`PTRACE_SETREGSET` for `NT_PRFPREG`, `NT_ARM_SVE`, `NT_ARM_SSVE`, `NT_ARM_ZA`, `NT_ARM_ZT`, and `NT_ARM_FPMR`. Key routines include `run_child`, `run_parent`, `continue_breakpoint`, `check_ptrace_values_*`, `set_initial_values`, `check_memory_values`, `fpsimd_write`, `sve_write_sve`, `sve_write_fpsimd`, `za_write`, `zt_write`, `fpmr_write`, `probe_vls`, `run_sve_tests`, and `run_sme_tests`.

Control flow: main probes supported VLs, computes the kselftest plan, installs a SIGALRM timeout handler, then runs FPSIMD-only, SVE, and SME matrix tests. Each test fills globals with random valid state, forks a child, has the child set requested VLs and call `load_and_save`, checks initial ptrace-visible state while stopped at BRK, optionally writes new regset state, resumes the child to save state, reads saved globals via `process_vm_readv`, detaches, waits for clean exit, and compares saved state to expected data.

State and persistence: global buffers hold input, expected, and output register state for all tested register classes. No disk persistence. The parent relies on fork-inherited virtual addresses to read child memory directly. Random values are seeded by PID and masked for safe FPMR bits.

Dependencies and integration: depends on `fp-ptrace-asm.S`, `fp-ptrace.h`, `sme-inst.h`, `kselftest.h`, asm sigcontext/SVE ptrace layout macros, and arm64 Linux regset ABI. It integrates with the selftests Makefile as the high-coverage FP ptrace contract test.

Risks: the state-space is large on systems with both SVE and SME. Some expectations encode delicate ABI rules: FPSIMD writes flush SVE state, SME VL changes can clear ZA/ZT/SVE data, streaming mode changes whether NT_ARM_SVE/SSVE returns full SVE or FPSIMD-format state, and FFR validity depends on FA64. A code-level risk is that pointer arithmetic on `void *` relies on GNU C.

Test signals: TAP results for each test definition and VL/SVCR combination. Failures print precise mismatch names such as initial/saved V, Z, P, FFR, ZA, ZT, FPMR, SVCR, SVE VL, or SME VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h

Purpose: small shared ABI header between the C and assembly halves of `fp-ptrace`.

Important definitions: defines SVCR bit shifts and masks `SVCR_SM` and `SVCR_ZA`, plus feature flag shifts/masks `HAVE_SVE`, `HAVE_SME`, `HAVE_SME2`, `HAVE_FA64`, and `HAVE_FPMR`.

Control flow and state: no runtime control flow or storage. The numeric bit positions must remain stable because assembly uses `tbz`/`ubfx` on these flags.

Dependencies and integration: included by `fp-ptrace.c` and `fp-ptrace-asm.S`. It bridges C feature detection and assembly register load/save behavior.

Risks: adding features or changing bit positions without updating both sides would silently corrupt test coverage.

Test signals: indirect; correct flags enable or skip corresponding assembly state paths during `fp-ptrace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c

Purpose: orchestrates a stress run of multiple FP/vector child tests across CPUs and vector lengths, while periodically injecting signals. It exercises context switching, signal save/restore, preemption, and kernel FP users concurrently.

Important APIs and functions: uses `fork`, `pipe`, `dup2`, `execl`, `epoll`, `waitpid`, `SIGCHLD`, `SIGUSR1`, `SIGTERM`, `prctl(PR_SVE_SET_VL/PR_SME_SET_VL)`, and `getauxval`. Core functions are `child_start`, `child_output_read`, `child_output`, `child_tickle`, `child_stop`, `child_cleanup`, `start_fpsimd`, `start_kernel`, `start_sve`, `start_ssve`, `start_za`, `start_zt`, `probe_vls`, and `drain_output`.

Control flow: parse `--timeout`, count CPUs, probe SVE/SME VLs, schedule FPSIMD and kernel tests for every CPU plus SVE/SSVE/ZA per supported VL and ZT for SME2. Children wait on a shared startup pipe until all have forked. The parent reads child stdout with epoll, waits until all children emitted startup output, then periodically sends SIGUSR1 until timeout or termination, sends SIGTERM, drains output, waits, and reports per-child TAP results.

State and persistence: in-memory `children` table tracks PID, stdout pipe, partial output, and exit status. No persistent files; child output is streamed through kselftest logs.

Dependencies and integration: runs sibling binaries `fpsimd-test`, `kernel-test`, `sve-test`, `ssve-test`, `za-test`, and `zt-test`; depends on HWCAP feature bits and prctl VL inheritance so execed children start with intended VLs.

Risks: high process counts scale with CPUs and VLs. Startup detection depends on each child printing output. Signal and epoll handling must avoid losing child output or leaving live processes on failure.

Test signals: kselftest plan equals scheduled child count; success requires each child to produce output and exit with status 0 after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress

Purpose: shell stress wrapper for `fpsimd-test`, launching many instances and repeatedly sending SIGUSR1 to stress signal-frame FPSIMD preservation.

Important APIs and functions: shell functions `cleanup`, `interrupt`, and `child_died`; uses `nproc`, `mktemp`, background jobs, `kill`, `wait`, `trap`, and `sleep`.

Control flow: start `NR_CPUS * 4 + 1` `./fpsimd-test` processes with per-child temp logs, sleep 10 seconds for startup, start an infinite signal sender, and wait. INT/TERM/EXIT clean up children and print logs; CHLD treats early death as failure.

State and persistence: temporary log files are created and removed during cleanup. Process IDs and log paths are tracked in shell variables.

Dependencies and integration: assumes `fpsimd-test` is built in the current directory. It is a simple alternative to the C stress harness for prolonged manual stress runs.

Risks: tight infinite signal loop can consume CPU. Trap cleanup uses unquoted lists and assumes simple temp paths. `kill`/`wait` failures are ignored during cleanup.

Test signals: normal operator interruption exits 0 after printing logs; premature child death exits 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-stress -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S

Purpose: assembly FPSIMD context-switch and signal-restore stress test. It writes unique patterns to all 32 V registers and verifies they survive syscalls, preemption, and signals.

Important APIs and symbols: `_start` is the entry. Accessor functions are generated with `define_accessor setv/getv`. Helpers include `pattern`, `setup_vreg`, `memcmp`, `check_vreg`, `irritator_handler`, `tickle_handler`, `terminate_handler`, `setsignal`, and `barf`. It uses raw `rt_sigaction`, `getpid`, `sched_yield`, `kill`, and `exit` syscalls.

Control flow: install signal handlers, validate fixed 128-bit vector length, get PID, then loop by generation. Each iteration fills V registers and shadow memory with PID/register/generation/lane patterns, yields, reads each register back into scratch, compares against shadow memory, and increments generation. SIGUSR1 intentionally corrupts live V registers in the handler; signal return should restore interrupted state.

State and persistence: `.data` contains `vref` and `scratch`. Registers x20-x23 hold PID, register index/generation, and signal counts. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, raw Linux syscall numbers, and optional `enable_gcs` macro for GCS-compatible entry. Invoked by `fpsimd-stress` and `fp-stress`.

Risks: assumes signal-frame offsets from `asm-offsets.h`; if kernel signal ABI or helper macros drift, false failures or crashes can occur. The test exits via SIGABRT on mismatch.

Test signals: prints vector length and PID at startup; clean SIGTERM prints iteration and signal counts; mismatch dumps expected and actual bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c

Purpose: stress test for kernel-mode FP/SIMD use by repeatedly running AF_ALG hash operations backed by known arm64 crypto drivers and checking digest stability under signals.

Important APIs and functions: `create_socket` scans `/proc/crypto`, opens `AF_ALG` hash socket, binds to a matching driver, accepts an operation socket, creates a zero-copy pipe, and allocates digest buffers. `compute_digest` sends data using `vmsplice` and `splice`, then `recv`s the digest. Signal handlers count SIGUSR1/SIGUSR2 and report on SIGTERM.

Control flow: install signal handlers, allocate a zeroed 64 KiB buffer, discover a kernel crypto hash driver using FP/NEON/CE, or fall back to `./fpsimd-test` if unsupported. Compute a reference digest, then loop computing and comparing digests forever.

State and persistence: global sockets, pipe FDs, algorithm name, digest buffers, signal count, and iteration count. No persistent files; reads `/proc/crypto`.

Dependencies and integration: called by `fp-stress` as a child named `KERNEL-*`. Depends on AF_ALG, kernel crypto drivers, and splice/vmsplice support.

Risks: driver list is static and can miss newer implementations. The `recv` retry compares `errno` to `-EAGAIN`, which is unusual because `errno` is positive. Fallback typo in the error message says `fspimd-test`.

Test signals: startup prints selected algorithm. Any digest mismatch, socket failure, or allocation failure exits nonzero; SIGTERM reports iterations and signal count with exit 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c

Purpose: tiny helper program that prints the current SME streaming vector length in bytes.

Important APIs and functions: `main` calls `rdvl_sme()` declared in `rdvl.h` and implemented in `rdvl.S`, then prints the integer.

Control flow and state: no branching or persistent state; read VL and exit 0.

Dependencies and integration: used by `vec-syscfg.c` to verify default and inherited SME vector length across exec.

Risks: must only be run when SME/RDSVL is supported or under a build/runtime setup that can handle the instruction.

Test signals: stdout contains one decimal VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c

Purpose: tiny helper program that prints the current SVE vector length in bytes.

Important APIs and functions: `main` calls `rdvl_sve()` from `rdvl.S` via `rdvl.h`, then prints the result.

Control flow and state: no persistent state; one helper call, one print, exit 0.

Dependencies and integration: used by `sve-probe-vls.c` and `vec-syscfg.c` to cross-check prctl/procfs vector-length reporting after exec.

Risks: must run only on SVE-capable systems or under a caller that has already skipped unsupported cases.

Test signals: stdout contains one decimal VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S

Purpose: assembly implementation of two vector-length readers used by C selftests.

Important APIs and symbols: exports `rdvl_sve` and `rdvl_sme`. `rdvl_sve` executes `rdvl x0, #1`; `rdvl_sme` executes encoded `rdsvl 0, 1`. Both start with BTI-compatible `hint 34` and return VL in x0.

Control flow and state: straight-line leaf functions with no storage.

Dependencies and integration: includes `sme-inst.h`, requires SVE/SME instruction support as appropriate, and is linked with `rdvl-sve`, `rdvl-sme`, `sve-probe-vls`, and `vec-syscfg`.

Risks: callers must feature-gate execution. Incorrect assembler encoding for `rdsvl` would affect every SME VL validation.

Test signals: return value must match `prctl(...SET_VL)` and procfs default VL expectations in caller tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h

Purpose: declaration header for assembly vector-length helper functions.

Important APIs: declares `int rdvl_sme(void);` and `int rdvl_sve(void);`.

Control flow and state: none.

Dependencies and integration: included by VL probing and syscfg tests that link against `rdvl.S`.

Risks: signature changes must stay in lockstep with assembly return convention and C callers.

Test signals: indirect through caller comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h

Purpose: assembler macro header for SME, SME2, and FPMR instructions not always understood by all toolchains.

Important definitions: `REG_FPMR`, `rdsvl`, `smstop`, `smstart_za`, `smstart_sm`, `_ldr_za`, `_str_za`, `_ldr_zt`, and `_str_zt`.

Control flow and state: no runtime state; macros expand into `msr`, `.inst`, or `sys/sysl`-style encodings.

Dependencies and integration: included by FP ptrace, RDVL, SVE/ZA/ZT tests, and fork helpers. It centralizes architecture encodings used throughout this test subset.

Risks: incorrect instruction encodings create broad false failures. Macro operands are simple textual parameters, so callers must pass valid register numbers.

Test signals: indirect; successful ZA/ZT/SM/VL tests validate these encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress

Purpose: shell stress wrapper for `ssve-test`, the streaming SVE variant of the SVE signal/context-switch test.

Important APIs and functions: same process/log/trap structure as `sve-stress`; launches `./ssve-test`, stores temp logs, sends SIGUSR1 continuously, and cleans up on EXIT/INT/TERM.

Control flow: spawn `NR_CPUS * 4 + 1` children, wait 10 seconds, run an infinite signal sender, and wait for termination. This script does not install the CHLD failure trap present in `fpsimd-stress`, so early child death handling differs.

State and persistence: shell PID and temp-log lists only; logs are printed then removed during cleanup.

Dependencies and integration: depends on `ssve-test` being built, typically from `sve-test.S` with `SSVE` enabled.

Risks: no CHLD trap means unexpected child death may not stop the script immediately. Tight signal loop can be aggressive.

Test signals: logs show child startup and mismatch/termination output; process exit is governed by cleanup or failed `wait`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/ssve-stress -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c

Purpose: enumerates supported SVE vector lengths and validates that `PR_SVE_SET_VL` agrees with hardware `RDVL`.

Important APIs and functions: `main` uses `getauxval(AT_HWCAP)`, `prctl(PR_SVE_SET_VL)`, `rdvl_sve()`, and sigcontext helpers `sve_vl_valid`/`sve_vq_from_vl`.

Control flow: skip if SVE unsupported, iterate downward from `SVE_VQ_MAX`, set each candidate VL, mask returned flags, compare against `rdvl_sve`, validate the VL, store unique VQs, then report two kselftest passes and print supported VLs in ascending order.

State and persistence: stack/static VQ array only. No files.

Dependencies and integration: links with `rdvl.S` and uses kselftest output. It provides a capability/probing signal for other VL-dependent tests.

Risks: many iterations on implementations with unusual VL sets; exits fail on prctl or invalid VL rather than recording individual subtest failures.

Test signals: plan of 2; pass messages for enumeration and validity, followed by supported VL list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-probe-vls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c

Purpose: ptrace ABI selftest for SVE and streaming SVE regsets, including unsupported behavior, VL setting, inherit flags, FPSIMD-format access, and SVE/FPSIMD data conversion.

Important APIs, types, and functions: `struct vec_type` describes SVE and streaming SVE regset metadata. Helpers include `do_child`, `get_fpsimd`, `set_fpsimd`, `get_sve`, `set_sve`, `read_fails`, `write_fails`, `ptrace_set_get_inherit`, `ptrace_set_get_vl`, `ptrace_set_vl_ranges`, `ptrace_sve_fpsimd`, `ptrace_sve_fpsimd_no_sve`, `ptrace_set_sve_get_sve_data`, `ptrace_set_sve_get_fpsimd_data`, `ptrace_set_fpsimd_get_sve_data`, and `do_parent`.

Control flow: child calls `PTRACE_TRACEME` and stops. Parent waits for the specific SIGSTOP, then for each vector type checks unsupported reads/writes, FPSIMD-format writes through SVE regset, inherit flag set/clear, invalid VL rejection, every candidate VQ up to `TEST_VQ_MAX`, and data round-trips for supported VLs. SME-only systems also test FPSIMD writes through NT_ARM_SVE despite no SVE hardware.

State and persistence: dynamic buffers hold variable-size `user_sve_header` payloads. No disk persistence. Random data is generated with `random()`.

Dependencies and integration: uses Linux arm64 ptrace regsets, `asm/sigcontext.h`, `asm/ptrace.h`, kselftest, and HWCAP/HWCAP2 feature bits.

Risks: intentionally limits VQ coverage to architecture-relevant range plus one; future wider architectures may need updates. Big-endian SVE/FPSIMD comparisons are skipped. A typo in one fail message says `FPSMID`.

Test signals: fixed expected test count; failure messages identify unsupported access, flag handling, VL, FPSIMD conversion, or data mismatch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress

Purpose: shell stress wrapper for `sve-test`, launching many SVE register integrity loops and bombarding them with SIGUSR1.

Important APIs and functions: `cleanup`, `interrupt`, and `child_died` manage process and temp-log lifecycle; uses `nproc`, `mktemp`, `trap`, `kill`, and `wait`.

Control flow: launch `NR_CPUS * 4 + 1` `./sve-test` processes, wait 10 seconds, start infinite SIGUSR1 loop, and wait. EXIT/INT/TERM run cleanup; CHLD exits with failure.

State and persistence: temp log files are transient and printed during cleanup. Process IDs are kept in shell variables.

Dependencies and integration: depends on `sve-test` and SVE-capable runtime.

Risks: tight signal loop can dominate CPU. Simple cleanup may emit errors if children have already exited.

Test signals: child logs show startup and any mismatch; early child death returns 1, user interruption returns 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-stress -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S

Purpose: assembly SVE and streaming SVE context-switch/signal-restore test. It repeatedly writes/verifies all Z registers, P registers, and FFR, with optional `SSVE` build behavior.

Important APIs and symbols: generated accessors `setz/getz` and `setp/getp`; helpers `pattern`, `setup_zreg`, `setup_preg`, `setup_ffr`, `check_zreg`, `check_preg`, `check_ffr`, signal handlers, `setsignal`, `barf`, `vl_barf`, and `svcr_barf`; `_start` drives the loop. Uses `rdvl`, `rdffr`, `wrffr`, optional `smstart_sm`, and raw syscalls.

Control flow: install handlers, optionally enter streaming mode, validate VL, print PID, loop by generation. Each iteration verifies VL stability, fills Z/P/FFR shadow buffers and registers with PID/register/generation patterns, checks streaming SVCR when built as SSVE, compares all registers, and repeats. SIGUSR1 intentionally corrupts live vector and predicate state; signal return must restore interrupted values.

State and persistence: `.data` contains `zref`, `pref`, `ffrref`, and `scratch`. Registers track PID, generation, register index, and signal count. No files.

Dependencies and integration: built as `sve-test` and likely as `ssve-test` with preprocessor defines. Used by shell stress scripts and `fp-stress`.

Risks: streaming SVE syscalls exit streaming mode, so code must restart it carefully. FFR is skipped in SSVE mode. Signal ucontext offsets and vector-length calculations must match kernel ABI.

Test signals: startup prints vector length and PID; mismatch dumps expected/actual bytes and SVCR for SSVE; clean termination reports iterations and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c

Purpose: system-configuration selftest for SVE and SME vector length controls via procfs defaults and prctl process controls.

Important APIs, types, and functions: `struct vec_data` captures per-vector-type metadata, including HWCAP, `rdvl` helper, prctl operations, and procfs default file. Key functions include `get_child_rdvl`, `file_read_integer`, `file_write_integer`, `proc_read_default`, `proc_write_min`, `proc_write_max`, `prctl_get`, `prctl_set_same`, `prctl_set`, `prctl_set_no_child`, `prctl_set_for_child`, `prctl_set_onexec`, `prctl_set_all_vqs`, and `change_sve_with_za`.

Control flow: main sets a plan for all per-type tests plus cross-type tests, skips unsupported vector types, and runs procfs/prctl checks in an order that establishes default/min/max values before inheritance and all-VQ tests. Cross-type `change_sve_with_za` runs only when both SVE and SME are present.

State and persistence: mutates `/proc/sys/abi/sve_default_vector_length` and `/proc/sys/abi/sme_default_vector_length` when run as root, then attempts to restore defaults. Spawns helper binaries `rdvl-sve` and `rdvl-sme` to observe exec-time VL behavior.

Dependencies and integration: depends on `rdvl.S`, helper binaries, kselftest, root privileges for write tests, HWCAP bits, and procfs ABI files.

Risks: procfs mutation affects system-wide defaults during the test; restoration paths are best-effort and can be skipped after some failures. `change_sve_with_za` has a TODO for verifying ZA preservation beyond surviving activity.

Test signals: TAP results distinguish default reads, min/max writes, prctl get/set/inherit/onexec/all-VQ behavior, and SVE changes while SME is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vec-syscfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c

Purpose: command wrapper that sets SVE or SME vector length for the next exec, then executes a requested command.

Important APIs and functions: `parse_options` handles `--force`, `--inherit`, `--no-inherit`, `--max`, `--sme`, and help. `main` validates VL, checks SVE HWCAP unless forced, calls `prctl(PR_SVE_SET_VL or PR_SME_SET_VL, vl | PR_SVE_SET_VL_ONEXEC | optional INHERIT)`, reads back current flags with `PR_*_GET_VL`, and `execvp`s the command.

Control flow: parse options and VL, reject invalid/missing command, optionally continue without SVE under `--force`, set on-exec VL, verify prctl get succeeds, then exec. Return codes follow shell conventions: 2 for usage, 126 for not executable, 127 for not found.

State and persistence: only process-local prctl state that affects the execed child. No files.

Dependencies and integration: helper utility for running tests/programs at specific SVE/SME VLs.

Risks: HWCAP check only tests SVE even when `--sme` is requested. The VL validation expression `vl & ~(vl & PR_SVE_VL_LEN_MASK)` is suspicious and may not implement the intended mask rejection. `--no-inherit` is parsed but not actively used beyond conflict detection.

Test signals: stderr explains usage, missing feature, prctl, or exec failures; success replaces the process image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S

Purpose: assembly setup and verification for testing ZA preservation across `fork`.

Important APIs and symbols: exports `fork_test` and `verify_fork`; tail-calls C function `fork_test_c`. Uses `smstart_za`, `_ldr_za`, `_str_za`, SVCR reads, and a `MAGIC` value stored in ZA row 0.

Control flow: `fork_test` enables ZA, writes `MAGIC` into scratch, loads it into ZA, then jumps to C. `verify_fork` checks SVCR has ZA enabled and SM disabled, stores ZA row 0 back into scratch, compares against `MAGIC`, and returns boolean.

State and persistence: `.data scratch` backs one vector-sized buffer. ZA architectural state is the tested state.

Dependencies and integration: paired with `za-fork.c`; includes `sme-inst.h`; built with nolibc constraints.

Risks: only verifies one word in one ZA vector, relying on broader ZA corruption coverage elsewhere. Assumes SVCR bit meanings from the test suite.

Test signals: C wrapper reports `fork_test` pass/fail based on parent and child `verify_fork`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c

Purpose: C wrapper for the ZA fork preservation test.

Important APIs and functions: declares assembly `fork_test` and `verify_fork`. `fork_test_c` forks, has the child and parent call `verify_fork`, waits for child exit, and combines results. `main` sets a one-test plan and checks `/proc/sys/abi/sme_default_vector_length` as a nolibc-compatible SME availability proxy.

Control flow: if SME proxy file opens, run `fork_test`; otherwise skip. Child exits 1 on successful verification and 0 on failure so the parent can combine `WEXITSTATUS(child_status) && parent_result`.

State and persistence: no file writes; opens procfs read-only. Depends on ZA state prepared by assembly.

Dependencies and integration: paired with `za-fork-asm.S`, `kselftest.h`, nolibc-compatible headers, and Linux wait/fork APIs.

Risks: using procfs default VL as support detection can misclassify unusual systems. Child exit convention is inverted relative to normal pass/fail and must remain understood by parent code.

Test signals: one TAP result named `fork_test`; diagnostic messages identify parent/child invalid ZA state or wait failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c

Purpose: ptrace ABI selftest for SME ZA register set, including VL changes, disabled ZA representation, and ZA data round-trips.

Important APIs and functions: `get_za` dynamically sizes `user_za_header` reads from `NT_ARM_ZA`; `set_za` writes ZA regsets. `ptrace_set_get_vl`, `ptrace_set_no_data`, `ptrace_set_get_data`, `do_child`, and `do_parent` implement the cases.

Control flow: skip if SME unsupported, fork a traced child, wait for its SIGSTOP, iterate VQs from `SVE_VQ_MIN` to `TEST_VQ_MAX`, set each VL via ptrace after comparing prctl-supported VL in parent, and for supported VLs verify disabled ZA header-only writes and full ZA data write/read.

State and persistence: dynamic buffers for ZA payloads; random data seeded by PID. No disk state.

Dependencies and integration: uses `PTRACE_GETREGSET`/`SETREGSET`, `NT_ARM_ZA`, `PR_SME_SET_VL`, sigcontext ZA sizing macros, and kselftest.

Risks: `ksft_test_result(new_za->vl = prctl_vl, ...)` uses assignment instead of comparison, so that subtest can pass incorrectly if `prctl_vl` is nonzero. Coverage is limited to current architectural VQ range plus one.

Test signals: expected tests are three per candidate VQ; data mismatch, read/write failures, and unsupported VL skips are reported via kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress

Purpose: shell stress wrapper for `za-test`, exercising SME ZA context preservation under repeated signals and many parallel processes.

Important APIs and functions: same shell structure as SVE wrappers: `cleanup`, `interrupt`, `child_died`, `trap`, `mktemp`, `kill`, and `wait`.

Control flow: spawn `NR_CPUS * 4 + 1` `./za-test` children into temp logs, sleep 10 seconds, continuously send SIGUSR1, wait, and clean up on exit.

State and persistence: temp logs are transient; process IDs tracked in shell variables.

Dependencies and integration: requires `za-test` and SME-capable hardware/kernel.

Risks: no CHLD trap is installed despite defining `child_died`, so premature exits may be handled only by `wait`. Infinite signal loop can be CPU-heavy.

Test signals: `za-test` logs contain vector length/PID and mismatch reports; wrapper exits nonzero if wait fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-stress -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S

Purpose: assembly SME ZA context-switch and signal-restore test. It fills every ZA horizontal vector with deterministic data and verifies preservation across syscalls, preemption, and signal delivery.

Important APIs and symbols: helpers `pattern`, `setup_za`, `memcmp`, `check_za`, signal handlers, `setsignal`, `barf`, `vl_barf`, and `svcr_barf`. Uses `smstart_za`, `rdsvl`, `_ldr_za`, `_str_za`, `sched_yield`, and raw signal/syscall interfaces.

Control flow: install handlers, enable ZA, validate streaming vector length, get PID, then loop by generation. Each iteration checks VL stability, fills all ZA rows with row/generation/PID/lane patterns, yields, checks SVCR is ZA=1/SM=0, stores and compares every ZA row, then repeats.

State and persistence: `.data` has large `zaref` and `scratch` buffers sized for max VL. Architectural ZA is the target state. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, `sme-inst.h`; launched by `za-stress` and `fp-stress`.

Risks: large static buffer sized for 2048-bit VL squared. Signal handler intentionally resets ZA and relies on signal return to restore interrupted state. Any SVCR/VL ABI change affects the test.

Test signals: startup prints streaming mode, vector length, and PID; mismatch dumps expected/actual row data and SVCR; clean termination reports iterations and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c

Purpose: ptrace ABI selftest for SME2 ZT0 register state and its interaction with ZA enablement.

Important APIs and functions: `get_za`/`set_za` access `NT_ARM_ZA`; `get_zt`/`set_zt` access `NT_ARM_ZT`; tests are `ptrace_za_disabled_read_zt`, `ptrace_set_get_zt`, and `ptrace_enable_za_via_zt`.

Control flow: skip if SME2 unsupported, read current SME VL, fork traced child, wait for SIGSTOP, disable ZA and confirm ZT reads zero, write/read ZT and compare bytes, then disable ZA, write ZT, read ZA header/data to verify ZA became enabled with same VL and expected backing data state.

State and persistence: process-local traced child register state and stack buffers. No files.

Dependencies and integration: uses SME2 HWCAP, `ZT_SIG_REG_BYTES`, ZA sizing macros, ptrace regsets, and kselftest.

Risks: in `ptrace_enable_za_via_zt`, the comment says ZA register data should be non-zero but the loop marks any non-zero byte as failure; this inconsistency needs scrutiny against the intended ABI. It also assumes writing ZT implies PSTATE.ZA-visible ZA data.

Test signals: three TAP tests report disabled read, set/get ZT, and ZA enable via ZT behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S

Purpose: assembly SME2 ZT0 context-switch and signal-restore stress test.

Important APIs and symbols: helpers `pattern`, `setup_zt`, `memcmp`, `check_zt`, signal handlers, `setsignal`, `barf`, and `svcr_barf`; `_start` drives execution. Uses `smstart_za`, `_ldr_zt`, `_str_zt`, raw syscalls, and SVCR reads.

Control flow: install handlers, enable ZA, get PID, then loop by generation. Each iteration fills ZT0 and shadow memory, yields, verifies SVCR has ZA=1/SM=0, stores ZT0 to scratch, compares against shadow, and repeats. SIGUSR1 resets SME state; signal return should restore interrupted state.

State and persistence: `.data` contains `ztref` and `scratch` sized to 512 bits. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, and `sme-inst.h`; run by `fp-stress` on SME2 systems.

Risks: only tests ZT0, consistent with current SME2 ZT regset size. Requires SME2 instruction support and accurate signal context restoration.

Test signals: startup prints PID; mismatch dumps expected/actual ZT bytes and SVCR; clean SIGTERM reports iterations and signal count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile

Purpose: build rules for arm64 Guarded Control Stack selftests.

Important definitions: `TEST_GEN_PROGS` includes `basic-gcs`, `libc-gcs`, `gcs-locking`, `gcs-stress`, `gcspushm`, and `gcsstr`; `TEST_GEN_PROGS_EXTENDED` includes `gcs-stress-thread`; `LDLIBS += -lpthread`.

Control flow: includes `../../lib.mk` after target definitions. Custom rules build `basic-gcs` with nolibc/static/freestanding options to avoid toolchain/dynamic-linker interaction, and build assembly helpers with `-nostdlib`.

State and persistence: build artifacts only under kselftest output.

Dependencies and integration: depends on kselftest lib.mk, nolibc include path, kernel UAPI headers, pthread for libc tests, and assembler support for GCS instruction encodings used in `.S` files.

Risks: nolibc/static flags are sensitive to include path layout. GCS tests deliberately avoid normal runtime startup for some binaries.

Test signals: successful build creates all generated test programs and the extended stress thread helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/asm-offsets.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/asm-offsets.h

Purpose: placeholder/header stub for assembly offset inclusion in the GCS folder.

Important APIs/types/functions: none; file is empty.

Control flow, state, and dependencies: no runtime behavior. Its existence can satisfy include conventions shared with other assembly selftests.

Integration points: may be included by generated or future assembly files expecting an `asm-offsets.h` path.

Risks: because it is empty, any assembly that actually needs offsets must define them elsewhere.

Test signals: none directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c

Purpose: nolibc-style basic Guarded Control Stack selftest covering prctl status, permissions, shadow stack mapping, and fork/vfork inheritance.

Important APIs and functions: `gcs_set_status` wraps raw `prctl(PR_SET_SHADOW_STACK_STATUS)` and validates `PR_GET_SHADOW_STACK_STATUS` plus `CHKFEAT`; `read_status`, `base_enable`, `read_gcspr_el0`, `enable_writeable`, `enable_push_pop`, `enable_all`, `enable_invalid`, `map_guarded_stack`, `test_fork`, and `test_vfork` are test cases.

Control flow: skip if `HWCAP_GCS` absent, ensure GCS enabled, set kselftest plan, run test table, then attempt one final disable. Mapping test calls `map_shadow_stack` with marker/token flags and validates zero terminator, cap token, and zero-filled body.

State and persistence: process GCS status is mutated; mapped shadow stacks are `munmap`ed. Child processes inherit/check mode in fork and vfork tests.

Dependencies and integration: uses raw syscalls from nolibc, `gcs-util.h`, PR shadow stack UAPI constants, `map_shadow_stack`, and HWCAP_GCS. Built specially by the GCS Makefile.

Risks: hard-coded maximum page size of 65536 is used because nolibc lacks `sysconf`. Enabling/disabling GCS around C returns is delicate; unused syscall args are explicitly zeroed because kernel validates them.

Test signals: TAP results for each test table entry; diagnostics print mode, GCSPR, mapping bounds, cap token, and child exit details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/basic-gcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c

Purpose: kselftest harness tests for locking GCS mode bits and ensuring locked modes cannot be changed.

Important APIs and functions: uses `PR_LOCK_SHADOW_STACK_STATUS`, `PR_SET_SHADOW_STACK_STATUS`, `PR_GET_SHADOW_STACK_STATUS`, and inline `my_syscall2` to zero unused syscall arguments. Tests include `lock_all_modes`, fixture variants for enable/write/push combinations, `set`, `enable_lock_disable`, `lock_enable`, and `lock_enable_disable_others`.

Control flow: main skips if no HWCAP_GCS, fails/skips if GCS already enabled because tests rely on unconfigured mode, then runs the harness. Each fixture test runs in a forked harness child and exits after assertions.

State and persistence: process-local GCS status and locked bits. No persistent files.

Dependencies and integration: uses `kselftest_harness.h`, `gcs-util.h`, Linux prctl UAPI, and harness process isolation.

Risks: cannot run after a loader or environment has already enabled GCS. Negative syscall return comparisons depend on the raw syscall wrapper returning kernel negative errno values.

Test signals: harness assertions compare returned modes and `-EBUSY` behavior for locked bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-locking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S

Purpose: minimal assembly program used by `gcs-stress` to stress GCS context switching with recursion, syscalls, and signals.

Important APIs and symbols: `_start` enables GCS via raw prctl, installs signal handlers, prints "Running", and loops through generated `recurse1` and `recurse2`. Helpers implement raw `puts`, `putdec`, signal setup, and handlers for SIGTERM/SIGUSR1/SIGSEGV.

Control flow: enable shadow stack, install handlers, then repeatedly recurse to depth 5 through two different functions. Each return path issues a `getpid` syscall immediately before returning to provoke scheduling/migration near GCS updates. SIGSEGV handler disables GCS and reports `si_code`, identifying `SEGV_CPERR`.

State and persistence: no files; live GCS, call stack, and signal state are the test target.

Dependencies and integration: execed by `gcs-stress`; uses raw syscall numbers and GCS system registers/instructions.

Risks: intentionally sensitive to GCS faults and runtime environment. Offset constants for `siginfo_t` and ucontext are hard-coded.

Test signals: prints `Running` after setup; SIGTERM exits 0 with message; GCS violations print SIGSEGV code then exit 255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c

Purpose: C controller for concurrent GCS stress threads/processes. It starts one more GCS assembly worker than CPU count and periodically signals them.

Important APIs and functions: mirrors `fp-stress` structure with `start_thread`, `child_output_read`, `child_output`, `child_tickle`, `child_stop`, `child_cleanup`, signal handlers, and `drain_output`. Uses `epoll`, `fork`, `execl("gcs-stress-thread")`, startup pipe gating, and kselftest.

Control flow: parse `--timeout`, skip if no GCS tests scheduled, allocate child state, fork all workers blocked on startup pipe, close pipe, wait for startup output from all children, then every 100 ms send SIGUSR1 until timeout. Finally sends SIGTERM, drains output, cleans children, and reports TAP results.

State and persistence: in-memory child table and stdout pipes only.

Dependencies and integration: requires `gcs-stress-thread` and HWCAP_GCS. Built as a GCS selftest binary.

Risks: output-seen gating depends on workers printing. SIGCHLD handler records `si_status` but does not distinguish signaled exits until cleanup. High CPU counts create many processes.

Test signals: plan equals worker count; success requires every worker to print startup output and exit with status 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h

Purpose: shared GCS UAPI and inline-instruction helper header.

Important definitions and functions: syscall/regset constants `__NR_map_shadow_stack`, `NT_ARM_GCS`; prctl operations and mode bits; token flags and cap token masks; `get_gcspr` reads `GCSPR_EL0`; `gcsss1`/`gcsss2` implement GCS stack-switch instructions; `chkfeat_gcs` executes CHKFEAT for GCS.

Control flow and state: inline helpers access architectural state but store nothing persistently.

Dependencies and integration: included by C GCS tests and bridges missing or new UAPI definitions until libc/kernel headers catch up.

Risks: fallback syscall numbers and constants must match the running kernel ABI. Encoded instructions require correct toolchain/CPU support.

Test signals: indirect; basic, libc, and locking tests validate helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S

Purpose: standalone assembly smoke test that enables GCS push permission and executes GCSPUSHM/GCSPOPM.

Important APIs and symbols: `_start` uses raw `prctl(PR_SET_SHADOW_STACK_STATUS, ENABLE|PUSH)`, then `GCSPUSHM` and `GCSPOPM` encoded as `sys`/`sysl`. Includes simple `puts` for failure output.

Control flow: enable GCS with push permission; on failure print message and exit `KSFT_SKIP`; on success push/pop and exit 0.

State and persistence: process-local GCS state only; no files.

Dependencies and integration: built `-nostdlib` by GCS Makefile; uses raw syscall ABI.

Risks: skips rather than fails if enabling permission is rejected, which is appropriate for missing support but can hide configuration issues.

Test signals: exit 0 means instruction sequence executed; exit 4 indicates skipped setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S

Purpose: standalone assembly smoke test that enables GCS write permission and executes a GCS store instruction.

Important APIs and symbols: `_start` enables `PR_SHADOW_STACK_ENABLE | PR_SHADOW_STACK_WRITE`, reads `GCSPR_EL0`, subtracts one slot, and emits encoded `GCSSTR x1, x0`.

Control flow: enable GCS write permission; on failure print and exit skip; on success perform store and exit 0.

State and persistence: writes process shadow stack memory only; no files.

Dependencies and integration: built `-nostdlib`, uses raw syscall and encoded GCS instruction.

Risks: direct GCS store targets `GCSPR_EL0 - 8`; incorrect pointer assumptions would fault. Like `gcspushm`, setup failure exits as skip.

Test signals: exit 0 for successful instruction use, 4 for skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c

Purpose: libc-based GCS harness test covering calls, threads, ptrace access, mapped shadow stacks, stack switching, overflow faults, invalid mapping sizes, and invalid mprotect.

Important APIs and functions: `gcs_recurse` prevents tail-call optimization and creates GCS entries. Tests include `can_call_function`, `gcs_enabled_thread`, `gcs_find_terminator`, `ptrace_read_write`, map fixture tests `stack_capped`, `stack_terminated`, `not_writeable`, `stack_switch`, `stack_overflow`, invalid map fixture `do_map`, and invalid mprotect tests. Uses `map_shadow_stack`, `gcsss1/gcsss2`, `PTRACE_GETREGSET NT_ARM_GCS`, `PTRACE_PEEKDATA/POKEDATA`, `process_vm_readv`, pthreads, and mprotect.

Control flow: main skips if no GCS, forcibly enables GCS using raw syscall if not already enabled, then exits through the kselftest harness to avoid returning through libc in an unsupported GCS configuration. Harness fixtures map stacks at multiple sizes/flags and validate token/marker behavior and pivot semantics.

State and persistence: process GCS state, pthread child state, traced child GCS memory, and temporary mapped shadow stacks. No files.

Dependencies and integration: requires libc/pthread, `gcs-util.h`, kselftest harness, and kernel support for GCS ptrace/mapping APIs.

Risks: enabling GCS in a libc process is delicate when libc lacks GCS awareness; the code uses raw syscalls and `exit` to reduce return-path hazards. The fixture variant `s3k_marker` actually uses 4 KiB, likely a label typo.

Test signals: harness assertions and expected SIGSEGV tests validate read/write protections, stack switching, overflow faulting, invalid map rejection, and ptrace visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile

Purpose: build rules for arm64 Memory Tagging Extension selftests.

Important definitions: sets `CFLAGS += -std=gnu99 -I. -pthread`, `LDFLAGS += -pthread`, discovers all `.c` files except `mte_common_util.c` as programs, and checks compiler support for `-march=armv8.5-a+memtag` unless using LLVM.

Control flow: if compiler supports MTE, assigns `TEST_GEN_PROGS := $(PROGS)` and adds dependency on `mte_common_util.c mte_helper.S`; otherwise emits warnings and builds no MTE tests. Includes `../../lib.mk`.

State and persistence: build artifacts only.

Dependencies and integration: relies on GCC/Clang MTE support, pthread, shared MTE utility C/assembly files, and kselftest lib.mk.

Risks: compiler probe uses shell syntax embedded in make; nonstandard compilers may be misdetected. Excluding only `mte_common_util.c` means any helper `.c` added later could accidentally become a test binary.

Test signals: successful build produces one binary per test `.c` when support is detected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c

Purpose: MTE memory correctness selftest for byte/block writes, underflow/overflow behavior, tag-check modes, and initial tag state.

Important APIs and functions: uses shared helpers `mte_default_setup`, `mte_switch_mode`, `mte_allocate_memory`, `mte_allocate_memory_tag_range`, `mte_insert_tags`, `mte_wait_after_trig`, `mte_free_*`, and current fault context. Core tests are `check_buffer_by_byte`, `check_buffer_underflow_by_byte`, `check_buffer_overflow_by_byte`, `check_buffer_by_block_iterate`, `check_buffer_by_block`, `compare_memory_tags`, and `check_memory_initial_tags`.

Control flow: main fills size table with page-size boundary cases, sets up MTE and SIGSEGV handling, plans 20 tests, then evaluates sync/async/no-error modes across mmap and mprotect allocations. Underflow/overflow tests validate precise vs imprecise fault timing and whether neighboring bytes were modified.

State and persistence: allocates and frees anonymous/file mappings; creates temporary files through shared utilities for file mmap initial-tag checks. Uses global `cur_mte_cxt` fault state.

Dependencies and integration: depends on `mte_common_util.h`, `mte_def.h`, kselftest, MTE-capable kernel/hardware, and signal handlers.

Risks: async fault timing is inherently imprecise, so checks must allow writes before fault. Size calculations around unaligned allocation lengths and granule alignment are sensitive.

Test signals: 20 kselftest evaluations; diagnostics identify buffer index, tag mismatch, or unexpected fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_buffer_fill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c

Purpose: verifies MTE tag inheritance and fault behavior across `fork` for anonymous and file-backed mappings.

Important APIs and functions: `check_child_tag_inheritance` forks and has the child write tagged memory, compare tags across granules, and validate underflow/overflow faults. `check_child_memory_mapping` allocates anonymous tagged ranges; `check_child_file_mapping` maps temp files, inserts tags, and reuses inheritance checks.

Control flow: main initializes page-size boundary sizes, sets up MTE and SIGSEGV/SIGBUS handlers, plans 12 tests, and evaluates private/shared mappings for mmap/mprotect and sync/async modes.

State and persistence: temporary memory/file mappings and child processes. Shared `cur_mte_cxt` captures fault state in parent/child contexts. Temp files are created and closed via utilities.

Dependencies and integration: depends on MTE shared utilities, kselftest, fork/wait, and Linux memory mapping behavior.

Risks: several file-memory test labels call `check_child_memory_mapping` instead of `check_child_file_mapping` for async/mprotect cases, so label and behavior may diverge. Async fault timing can vary.

Test signals: child exits encode fault; kselftest failures print child creation, tag mismatch, or unexpected fault diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c

Purpose: stress test that GCR_EL1-related tag control state is restored correctly across context switches, forks, and threads.

Important APIs and functions: `execute_thread` chooses a random tag mask and sync/async TCF mode, repeatedly calls `prctl(PR_SET_TAGGED_ADDR_CTRL)` and compares `PR_GET_TAGGED_ADDR_CTRL`. `execute_test` starts five threads. `mte_gcr_fork_test` forks 1024 children, each running threaded checks.

Control flow: main runs MTE setup, plans one test, evaluates `mte_gcr_fork_test`, restores setup, and returns based on failure count.

State and persistence: no files; heavy process/thread state. Each thread has random desired tagged address control bits.

Dependencies and integration: depends on pthreads, MTE prctl ABI, shared MTE setup, and kselftest.

Risks: very high fork/thread count can be expensive. `pthread_join` writes a pointer return value into `int thread_data[]`, which is not portable and can truncate on 64-bit systems; current returned constants are small but the type mismatch is risky.

Test signals: one kselftest result; failure prints mismatched `prctl_set`/`prctl_get` values or `prctl` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c

Purpose: tests MTE behavior on hugetlb mappings, including tag insertion, tag checking with TCO on/off, clearing PROT_MTE, and child tag inheritance.

Important APIs and functions: `default_huge_page_size`, `is_hugetlb_allocated`, `allocate_hugetlb`, `free_hugetlb`, `check_child_tag_inheritance`, `check_mte_memory`, `check_hugetlb_memory_mapping`, `check_clear_prot_mte_flag`, and `check_child_hugetlb_memory_mapping`.

Control flow: main sets up MTE and signal handlers, writes `/proc/sys/vm/nr_hugepages` to allocate two huge pages, verifies `MAP_HUGETLB | PROT_MTE` support, plans 12 tests, toggles PSTATE.TCO, runs hugetlb mapping and child inheritance tests across sync/async/no-error and mmap/mprotect modes, restores MTE setup, frees hugepages, and reports counts.

State and persistence: mutates global hugetlb pool via `/proc/sys/vm/nr_hugepages`; maps/unmaps huge pages; forks children. It attempts to free huge pages at the end.

Dependencies and integration: requires root or suitable privileges for hugepage allocation, hugetlb support, MTE support on huge pages, and shared MTE utilities.

Risks: early failure after `allocate_hugetlb` may skip `free_hugetlb`, leaving system hugepage count changed. System-wide hugepage pool mutation can disrupt other workloads. `tag_check` parameter is not meaningfully used in `check_mte_memory`.

Test signals: skips if PROT_MTE is unsupported with hugetlb; otherwise reports 12 kselftest cases with memory/tag/child inheritance diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c

Purpose: verifies that tagged MTE pages are not merged by Kernel Samepage Merging under MADV_MERGEABLE.

Important APIs and functions: `read_sysfs`, `write_sysfs`, `mte_ksm_setup`, `mte_ksm_restore`, `mte_ksm_scan`, and `check_madvise_options`.

Control flow: main performs MTE setup, reads page size, installs SIGBUS/SIGSEGV handlers, plans four tests, mutates KSM sysfs knobs to speed scanning, runs private/shared mmap checks under sync and async modes, restores KSM and MTE settings, and reports counts.

State and persistence: mutates `/sys/kernel/mm/ksm/*` values for merge behavior, scan timing, run state, max sharing, and pages-to-scan. Allocates tagged pages and calls `madvise(MADV_MERGEABLE)`.

Dependencies and integration: requires KSM sysfs, MTE utilities, permissions to write KSM knobs, and page scan progress.

Risks: `mte_ksm_setup` writes `max_page_sharing` using `ksm_sysfs[3]` before it is read from sysfs, likely setting it relative to zero rather than preserving original. The pass condition around `pages_shared`/`pages_sharing` is subtle and can be affected by unrelated KSM activity. Restoration happens only at normal end.

Test signals: four kselftest cases; diagnostics report missing KSM config, sysfs parse/write issues, or madvise failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_ksm_options.c -->
