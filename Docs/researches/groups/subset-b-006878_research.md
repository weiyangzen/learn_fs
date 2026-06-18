# Research Report: subset-b-006878

This grouped report covers the requested PowerPC selftest math, MCE, MM, NX gzip, PAPR, and PMU/EBB files. Each section is delimited for deterministic reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S

Purpose: PowerPC assembly helper for the MMA selftest. It exercises matrix multiply assist accumulator setup, one signed halfword GER operation, and result extraction into VSX registers.

Important APIs and types: Exports the global `test_mma` entry. It uses `lxvh8x`, raw encodings for `xxsetaccz`, `xvi16ger2s`, and `xxmfacc`, then stores four vector words with `stxvw4x`.

Control flow: The caller passes two 8x16-bit matrices and a 4x4 32-bit output image in argument registers. The routine loads operands, clears the MMA accumulator, performs one rank-2 update, deprimes accumulator state, stores four result vectors, and returns with `blr`.

State and persistence: No persistent software state is kept. The only mutable architectural state is transient VSX/MMA accumulator content and the caller-provided output buffer.

Dependencies and integration points: Integrated only through `mma.c`, the powerpc math Makefile, and hardware with MMA support. It depends on assembler acceptance of VSX mnemonics plus raw opcodes for newer MMA instructions.

Risks: The raw `.long` encodings are opaque to older tools and must match the ISA exactly. Register argument ordering is fragile because the routine directly consumes ABI registers and does not preserve temporary VSX state beyond the selftest contract.

Test signals: A passing `mma` selftest on MMA-capable hardware validates instruction availability, accumulator save/restore behavior, and the expected 4x4 result image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c

Purpose: C harness for the basic MMA arithmetic test. It prepares deterministic small matrices, invokes the assembly routine, and checks the resulting 4x4 product values.

Important APIs and types: Declares `extern void test_mma(...)`, implements `mma()`, and calls `test_harness(mma, "mma")` from `main`. Uses `uint16_t` operand arrays and `uint32_t` result arrays.

Control flow: `mma()` skips when `PPC_FEATURE2_MMA` is absent, initializes two 2x8 halfword rows, calls `test_mma`, compares each output lane with a fixed expected matrix, and reports failures through `FAIL_IF`.

State and persistence: State is stack-local test data only. Hardware MMA state is exercised by the assembly helper but not persisted by this file.

Dependencies and integration points: Depends on `utils.h` for HWCAP probing and harness macros, and on `mma.S` for the tested instruction sequence. It is built as a powerpc selftest.

Risks: Expected values encode the exact signed halfword matrix operation; changing operand layout in assembly or compiler ABI assumptions can silently invalidate the comparison. The test is hardware-gated, so non-MMA systems only provide skip coverage.

Test signals: Signals are skip on missing MMA and zero exit on exact matrix match. Failures identify data-path, assembler, or kernel context-management problems for MMA state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S

Purpose: Assembly support for VMX/Altivec register preservation tests. It fills, checks, and repeatedly mutates vector registers across syscall/preemption/signal scenarios.

Important APIs and types: Exports `check_vmx`, `test_vmx`, and `preempt_vmx` via `FUNC_START/FUNC_END`. It relies on helper macros from `basic_asm.h` and `vmx_asm.h` to load, compare, and poison vector registers.

Control flow: `check_vmx` validates a vector register image against memory. `test_vmx` loads all VMX registers, performs a syscall path driven by the caller, and verifies registers. `preempt_vmx` coordinates thread startup/running flags while spinning through VMX register checks under scheduler pressure.

State and persistence: The functions mutate architectural VMX registers and caller-visible status return values. Persistent test state lives in C globals supplied by callers, not in assembly storage.

Dependencies and integration points: Used by `vmx_preempt.c`, `vmx_signal.c`, and `vmx_syscall.c`; depends on powerpc VMX support, ABI-compatible vector register save/restore, and selftest assembly macros.

Risks: This code is highly ABI-sensitive: incorrect clobber expectations, missing VMX enablement, or kernel lazy-save bugs show up as false mismatches. Assembly loops can run for long periods and assume C-side flags remain valid.

Test signals: Passing VMX preempt, signal, and syscall tests indicates the kernel preserves Altivec state across context switches, signal delivery, and syscall entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c

Purpose: Multithreaded VMX preemption stress test. It tries to expose lost Altivec state while many worker threads spin in VMX assembly for a fixed time.

Important APIs and types: Defines `PREEMPT_TIME`, `THREAD_FACTOR`, globals `threads_starting` and `running`, declares `preempt_vmx`, and implements `test_preempt_vmx()` plus `main()`.

Control flow: The test skips without Altivec, sizes the thread count from online CPUs times a factor, allocates a shared vector image, starts pthreads that call `preempt_vmx`, waits until all are running, sleeps for the stress interval, clears `running`, and joins workers while checking return codes.

State and persistence: Shared global counters coordinate startup and stop state. VMX register images are per-thread stack/heap data and are not persisted after the run.

Dependencies and integration points: Depends on pthreads, scheduler preemption, `utils.h`, and `vmx_asm.S`. It integrates into kselftest as `vmx_preempt`.

Risks: The test is timing-sensitive and can be noisy on overloaded systems. Races in unsynchronized integer flags are intentional stress mechanics but make it unsuitable as a general threading pattern.

Test signals: A pass after the full preemption window shows no VMX register corruption across many context switches; skips indicate missing Altivec hardware support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c

Purpose: VMX signal-delivery stress test. It verifies that Altivec register contents survive asynchronous signal handling while VMX code is active.

Important APIs and types: Defines `ITERATIONS` and `THREAD_FACTOR`, installs `signal_vmx_sig` with `SA_SIGINFO`, declares `preempt_vmx`, and implements `test_signal_vmx()` and `main()`.

Control flow: The harness starts VMX worker threads, repeatedly sends signals to them or to the process, and uses the same assembly register-check loop as the preemption test. The handler executes during the stress interval and returns to code that continues checking vector state.

State and persistence: Global flags coordinate worker lifetime and signal sentinel behavior. Signal state is transient; no persistent files or kernel state are modified.

Dependencies and integration points: Depends on Altivec, pthreads, POSIX signals, `utils.h`, and `vmx_asm.S`. It exercises the kernel signal frame save/restore path for VMX registers.

Risks: Signal timing is inherently nondeterministic. If signal masks or delivery target rules change, the test may lose stress value without failing for the intended reason.

Test signals: Pass means delivered signals did not corrupt VMX registers; failures point at signal-frame or lazy vector state handling regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c

Purpose: VMX syscall preservation test. It checks that Altivec registers survive repeated syscall entry and return, including child process execution.

Important APIs and types: Declares `extern int test_vmx(vector int *varray, pid_t *pid)`, implements `vmx_syscall()`, `test_vmx_syscall()`, and `main()`.

Control flow: `test_vmx_syscall()` skips without Altivec, forks a child path around `vmx_syscall`, and uses the assembly helper to load/check VMX state while syscalls such as `getpid`/wait paths execute. Parent and child status are validated through kselftest macros.

State and persistence: Only process-local vector arrays and child PID/status are stored. The test has no persistent filesystem state.

Dependencies and integration points: Depends on `vmx_asm.S`, `utils.h`, POSIX fork/wait, and kernel syscall VMX context save/restore.

Risks: Fork and syscall paths must be interpreted carefully: a failure can be in register preservation, child status handling, or unsupported hardware gating.

Test signals: Passing output validates VMX state preservation across syscall boundaries and process control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S

Purpose: Assembly support for VSX register preservation under preemption. It is the VSX analogue of the VMX helpers but targets wider VSR state.

Important APIs and types: Exports `check_vsx` and `preempt_vsx`. Uses `basic_asm.h` and `vsx_asm.h` macros to load/check VSX registers and return mismatch status.

Control flow: `check_vsx` compares active VSX register contents with a caller-provided memory image. `preempt_vsx` waits for C-side thread coordination, repeatedly validates VSR contents while `running` is set, and reports the first mismatch.

State and persistence: Architectural VSX registers are transiently modified. Coordination state is supplied via pointers to C globals.

Dependencies and integration points: Used by `vsx_preempt.c`; depends on VSX hardware support, the powerpc ABI, and kernel VSR save/restore.

Risks: The code is sensitive to register numbering and compiler/linker ABI mode. Because it tests low-level state, ordinary sanitizers or instrumentation may interfere.

Test signals: Passing the VSX preempt test shows stable VSR content across scheduler preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c

Purpose: Multithreaded VSX preemption stress test. It targets kernel preservation of VSX registers across heavy context switching.

Important APIs and types: Defines `PREEMPT_TIME`, `THREAD_FACTOR`, `vsx_memcmp`, pthread worker `preempt_vsx_c`, `test_preempt_vsx()`, and `main()`. Declares assembly `preempt_vsx`.

Control flow: The test skips without VSX, allocates per-thread vector data, starts many threads, waits for all to enter the assembly loop, runs for 20 seconds, stops workers, and checks that each returns no mismatch.

State and persistence: Globals `threads_starting` and `running` coordinate the stress interval. Per-thread vector images are temporary.

Dependencies and integration points: Depends on pthreads, `utils.h`, `vsx_asm.S`, and powerpc VSX HWCAP support. It is part of the math selftests.

Risks: Like other preemption stress tests, runtime load and CPU count affect stress coverage. Unsynchronized globals are intentional but not a reusable synchronization model.

Test signals: A clean pass indicates no observed VSX register loss across high-frequency thread preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile

Purpose: Build definition for the powerpc machine-check selftest directory. It currently builds the recoverable-address error injection program.

Important APIs and types: `TEST_GEN_PROGS := inject-ra-err` is the main exported target. It includes common `lib.mk` and powerpc `flags.mk`, and links generated programs with `../harness.c`.

Control flow: Invoking the directory without arguments recurses to the parent. Normal kselftest build compiles `inject-ra-err` with shared harness support.

State and persistence: No runtime state. Build outputs are produced under kselftest `OUTPUT` as usual.

Dependencies and integration points: Depends on the parent powerpc selftest build system and the local `inject-ra-err.c` source.

Risks: Small Makefile, but target name drift would make the test disappear from generated runs.

Test signals: Build success and `make run_tests` discovering `inject-ra-err` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c

Purpose: Recoverable-address machine check exercise using VAS/NX mapping behavior. It intentionally maps a VAS paste address and probes that recoverable faults are surfaced as SIGBUS rather than killing unrelated state.

Important APIs and types: Defines `sigbus_handler`, `test_ra_error()`, and `main()`. Uses `VAS_TX_WIN_OPEN`, `struct vas_tx_win_open_attr`, `mmap`, `ioctl`, and `test_harness`.

Control flow: `test_ra_error()` opens `/dev/crypto/nx-gzip`, opens a VAS transmit window, maps the window, installs a SIGBUS handler, touches the mapped paste area to trigger the machine-check path, and validates that the expected fault was observed.

State and persistence: The only persistent state is the open/mapped device window during the test. `faulted` records signal delivery.

Dependencies and integration points: Depends on the local `vas-api.h`, `utils.h`, the NX gzip character device, VAS kernel support, and signal delivery.

Risks: The test requires privileged/platform-specific hardware support and will skip/fail differently depending on `/dev/crypto/nx-gzip` availability. Fault injection around accelerator mappings is architecture-sensitive.

Test signals: Pass means the kernel reports the recoverable access error through the expected signal path; absent device should lead to a skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h

Purpose: Local copy of the userspace VAS ioctl ABI needed by the MCE test. It defines how to request a transmit window from `/dev/crypto/nx-gzip`.

Important APIs and types: Defines `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr` with version, VAS id, reserved fields, and flags.

Control flow: No executable control flow. Callers fill `vas_tx_win_open_attr` and pass it to `ioctl(fd, VAS_TX_WIN_OPEN, ...)`.

State and persistence: No mutable state. The structure describes kernel-created VAS state after ioctl success.

Dependencies and integration points: Depends on `<linux/types.h>` and `<asm/ioctl.h>`. Duplicated in the NX gzip include tree for standalone build locality.

Risks: ABI drift from the kernel UAPI header would cause ioctl failures or incorrect window attributes. Reserved fields should remain zeroed by callers.

Test signals: Compile success plus successful VAS_TX_WIN_OPEN calls in MCE/NX tests validate this header copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/vas-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile

Purpose: Build and run definition for powerpc memory-management selftests. It enumerates executable tests for huge pages, permissions, pkeys, stack growth, bad accesses, and TLBIE stress.

Important APIs and types: Defines `TEST_GEN_PROGS`, `TEST_PROGS`, `TEST_GEN_PROGS_EXTENDED`, and `TEST_GEN_FILES`. Adds 64-bit CFLAGS to tests needing high addresses or powerpc64 ABI, pthread libraries for `tlbie_test`/`pkey_siginfo`, and a generated `tempfile`.

Control flow: Default `noarg` recurses to the parent. Normal builds produce the listed binaries plus `stress_code_patching.sh`; `tlbie_test` is extended rather than a default generated program.

State and persistence: No runtime persistence except generated build files and `tempfile` under `OUTPUT`.

Dependencies and integration points: Depends on `../../lib.mk`, `../flags.mk`, shared `harness.c`, `utils.c`, and `../pmu/lib.c` for stack signal plumbing.

Risks: Misclassified targets or missing `-m64` flags would silently reduce high-address test coverage. The generated tempfile is required by `subpage_prot` file-backed coverage.

Test signals: Signals are successful compilation, test enumeration by kselftest, and the ability to run both default and extended MM tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c

Purpose: Tests that invalid user accesses to kernel and boundary addresses fault with the expected SIGSEGV metadata on 64-bit powerpc.

Important APIs and types: Defines `PAGE_OFFSET`, global fault tracking, `segv_handler`, `bad_access(char *p, bool write)`, `test()`, and `main()`.

Control flow: `bad_access` uses `setjmp`/`longjmp` around reads or writes to intentionally bad addresses. `test()` derives kernel virtual limits, installs a SIGSEGV handler, forks where needed, and checks access/error combinations near kernel and user address boundaries.

State and persistence: Fault code/address globals capture one fault at a time. No state persists after process exit.

Dependencies and integration points: Depends on signal info, 64-bit address layout, `utils.h`, and kernel address fault classification.

Risks: The test encodes assumptions about `PAGE_OFFSET` and address layout. It can be invalid on non-64-bit or changed virtual address split configurations.

Test signals: Pass means invalid accesses reliably fault without kernel oops and report expected si_code/address data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c

Purpose: Validates execute permission behavior for anonymous memory on radix-capable powerpc systems. It ensures non-executable mappings fault and executable mappings run.

Important APIs and types: Defines PPC instruction constants, `is_fault_expected`, SIGTRAP/SIGSEGV handlers, `check_exec_fault(int rights)`, `test()`, and `main()`.

Control flow: `test()` skips without POWER9/radix-era capability, maps one page writable, fills it with NOPs and a final BLR, then exercises read/write/execute combinations through `mprotect`. Fault handlers restore permissions so each case can continue.

State and persistence: Global `fault_code`, `remaining_faults`, `fault_addr`, `pgsize`, and instruction buffer track the active case. No persistent state is written.

Dependencies and integration points: Depends on `pkeys.h` for helpers/HWCAP checks, POSIX signals, `mprotect`, and the powerpc instruction set.

Risks: Expected fault codes differ when pkeys are enabled, so the helper accepts `SEGV_PKUERR` only when pkeys are supported. Signal handler recovery must stay async-signal-safe enough for test use.

Test signals: Pass confirms read/write/execute permission separation and expected fault reporting for executable anonymous pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/exec_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c

Purpose: Regression test ensuring explicit hugetlb mappings do not get confused with transparent huge pages.

Important APIs and types: Defines `SIZE`, `test_body()`, `test_main()`, and `main()`. Uses `mmap`, `madvise`, and kselftest harness helpers.

Control flow: The body maps a 16 MiB region, applies huge-page related advice, touches memory, and checks that hugetlb/THP behavior remains consistent with the kernel contract. `test_main` wraps skip conditions and harness execution.

State and persistence: Only transient anonymous mappings are used; no persistent state is kept.

Dependencies and integration points: Depends on Linux huge page/THP VM behavior, `utils.h`, and page-size support on the running kernel.

Risks: Host hugepage configuration can affect skip/failure interpretation. The test targets regressions in VM accounting and mapping selection rather than generic performance.

Test signals: Pass means the selected huge mapping behavior is stable; skip indicates missing required hugepage support/configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c

Purpose: Tests separation of very large virtual memory areas across fork on 64-bit powerpc. It targets high-address mapping bugs around parent/child address-space handling.

Important APIs and types: Defines `MAP_FIXED_NOREPLACE` fallback, `test()`, and `main()`. Uses high fixed addresses, `mmap`, fork/wait, and memory writes.

Control flow: `test()` maps memory above the usual low address range, forks, lets child and parent modify their views, and checks copy-on-write separation rather than aliasing/corruption.

State and persistence: State is transient VM mappings and forked process status.

Dependencies and integration points: Depends on 64-bit userspace, high virtual address availability, `utils.h`, and COW VM behavior.

Risks: The fallback maps with `MAP_FIXED` on old headers and assumes high addresses are safe. Nonstandard address space limits can cause skips or mapping failures.

Test signals: Pass demonstrates fork does not confuse high virtual mappings or leak writes between parent and child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c

Purpose: Stress test for general-purpose register corruption during faults on large virtual-memory mappings. It targets SLB/high-address exception paths.

Important APIs and types: Defines high-address mapping constants, `signal_handler`, `CHECK_REG` macro, `touch_mappings()`, `test()`, and `main()`.

Control flow: `test()` maps many high-address regions, installs a signal handler, poisons/checks GPR values around loads/stores that fault or touch mappings, and verifies registers retain expected values after exception handling.

State and persistence: Transient mappings plus register snapshots are the only state. No files are persisted.

Dependencies and integration points: Depends on 64-bit powerpc, signal delivery, high virtual address support, and inline assembly/register constraints.

Risks: Register-specific inline assembly is fragile across compiler options. The test is meaningful only on configurations that exercise large VM/SLB paths.

Test signals: Pass indicates exception handling around high-address VM activity preserves user GPR state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c

Purpose: Tests execute protection using powerpc memory protection keys. It verifies IAMR/AMR interactions for read, write, and execute faults.

Important APIs and types: Defines PPC instruction words, signal handlers, `test()`, and `main()`. Uses `sys_pkey_alloc`, `sys_pkey_mprotect`, `pkey_set_rights`, `next_pkey_rights`, and `siginfo_pkey` from `pkeys.h`.

Control flow: `test()` maps an instruction page, allocates pkeys with execute-disabled and other right combinations, performs read/write/branch attempts, and expects either access faults or `SEGV_PKUERR`. The SIGSEGV handler restores rights or remaps execute-only pages so testing can continue.

State and persistence: Global fault metadata records expected pkey, fault type, code, and address. Pkeys are allocated/freed during each case.

Dependencies and integration points: Depends on kernel pkey support, powerpc IAMR behavior, POSIX signals, and executable anonymous mappings.

Risks: Subtle risk is distinguishing ordinary access faults from pkey faults when PROT bits and pkey rights both deny access. Handler recovery depends on pkey semantics that userspace cannot fully control for IAMR.

Test signals: Pass confirms correct pkey signal metadata and execute restriction behavior across valid rights combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c

Purpose: Concurrency test for pkey signal metadata. It checks that faults report the restrictive pkey when two threads race to protect the same page with permissive and restrictive keys.

Important APIs and types: Defines `struct region`, SIGSEGV handler, thread functions `protect` and `protect_access`, `reset_pkeys`, `test()`, and `main()`. Uses pthread barriers and pkey syscalls.

Control flow: `test()` prepares an executable page, clears pkey restrictions, then runs three thread pairs for read, write, and execute restrictions. One thread repeatedly applies a permissive pkey while the other applies a restrictive pkey and accesses a random instruction word, expecting `SEGV_PKUERR` to name the restrictive key.

State and persistence: Global volatile fields hold the current permissive/restrictive pkeys, rights, fault count, and fault address. The barrier synchronizes each iteration across one million loops.

Dependencies and integration points: Depends on pthreads, `pkeys.h`, signal metadata, and powerpc AMR/IAMR pkey implementation.

Risks: The test is race-oriented and long-running. Random fault addresses and competing `pkey_mprotect` calls are intentional, so failures require distinguishing real kernel metadata bugs from unsupported pkey setups.

Test signals: Pass means `siginfo` pkey reporting remains accurate under concurrent protection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c

Purpose: Tests support for `PROT_SAO` mappings on processors that advertise Strong Access Ordering capability.

Important APIs and types: Defines `SIZE`, `test_prot_sao()`, and `main()`. Uses `mmap`, `mprotect`, `memset`, `munmap`, and `PPC_FEATURE_ARCH_2_06` style capability checks through `utils.h`.

Control flow: `test_prot_sao()` maps memory with ordinary permissions, applies SAO protection when supported, writes to the region, and validates kernel acceptance/rejection paths.

State and persistence: Only a temporary mapping is modified.

Dependencies and integration points: Depends on `<asm/cputable.h>`, powerpc SAO support, and the shared harness.

Risks: SAO is hardware/configuration-specific and may skip on many systems. The test is mostly ABI coverage for `mprotect` flag validation.

Test signals: Pass indicates `PROT_SAO` is accepted and usable where advertised, or skipped where unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c

Purpose: Validates SIGSEGV `si_code` values for mapping and permission errors. It focuses on distinguishing map errors from access errors.

Important APIs and types: Defines `segv_handler`, `test_segv_errors()`, and `main()`, with global `faulted` and `si_code` state.

Control flow: The test installs a handler, triggers faults for unmapped memory and protected mappings, and checks the kernel reports expected `SEGV_MAPERR` or `SEGV_ACCERR` semantics.

State and persistence: Fault status is process-local global state reset per case.

Dependencies and integration points: Depends on POSIX signals, `mmap`/`mprotect`, ucontext availability, and `utils.h`.

Risks: Signal-code expectations can vary for architecture-specific fault classes; this file is intentionally narrow to common SEGV cases.

Test signals: Passing confirms basic powerpc fault classification visible to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c

Purpose: Tests stack expansion behavior caused by load/store accesses near the stack boundary. It checks that valid growth succeeds and invalid deltas fault.

Important APIs and types: Defines `enum access_type`, `consume_stack`, `/proc/maps` search helper, child/test wrappers, and two `main()` variants depending on build configuration.

Control flow: The child consumes stack to a target depth, probes addresses with load or store operations at configured deltas, and exits with status expected by the parent. The parent runs multiple sizes around page and rlimit boundaries.

State and persistence: State is child process stack, resource limits, and `/proc/self/maps` parsing results. No persistent files are created.

Dependencies and integration points: Depends on no stack protector for accurate stack probing, process control, signals, `utils.h`, and kernel stack expansion policy.

Risks: Compiler instrumentation can invalidate stack layout, hence `-fno-stack-protector` in the Makefile. Results depend on rlimit and guard-gap policy.

Test signals: Pass means stack growth/fault behavior matches expected load/store semantics across tested offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c

Purpose: Tests stack expansion when a signal is delivered while a child has consumed a large portion of stack. It targets signal-frame placement near growth boundaries.

Important APIs and types: Defines `sigusr1_handler`, `consume_stack`, `child`, `test_one_size`, `test()`, and `main()`. Uses pipe helpers from `../pmu/lib.h`.

Control flow: For each stack size, the child recursively/locally consumes stack, notifies the parent, waits for SIGUSR1, and verifies the signal handler ran. The parent coordinates with pipes and checks child status.

State and persistence: State is child stack usage, pipe synchronization, and the `sig_occurred` flag.

Dependencies and integration points: Depends on signal delivery, stack expansion policy, fork/pipe helpers, and `utils.h`.

Risks: Stack sizes and guard behavior are platform-sensitive. Pipe synchronization failures can mask the intended VM behavior.

Test signals: Pass shows signal-frame creation can expand stack safely for the tested sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh

Purpose: Shell stress test for spurious faults while kernel code is being mapped/patched through ftrace. It repeatedly toggles function tracing and watches for ftrace bug reports.

Important APIs and types: Defines `TIMEOUT`, discovers debugfs tracing paths, checks current trace health, clears dmesg, loops setting `current_tracer` to `function` and `nop`, then inspects dmesg for `ftrace bug`.

Control flow: The script skips if debugfs/tracing is unavailable, aborts if tracing is already corrupted, runs for 30 seconds or until a bug appears, restores `nop`, and returns pass/fail.

State and persistence: It mutates global tracing state and clears/reads the kernel log; those effects are system-wide during the test.

Dependencies and integration points: Depends on debugfs, ftrace, dmesg access, and shell utilities. Integrated as `TEST_PROGS` by the MM Makefile.

Risks: Requires permissions to clear/read dmesg and alter tracing. Running on shared systems can disturb tracing users.

Test signals: Pass prints that mapping kernel memory does not cause spurious faults; failure is any observed ftrace bug marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stress_code_patching.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c

Purpose: Exercises the powerpc `subpage_prot` syscall for 64 KiB pages split into smaller protected subpages. It covers anonymous and file-backed mappings.

Important APIs and types: Defines signal handler `segv`, access helpers, `check_faulted`, `run_test`, `syscall_available`, `test_anon`, `test_file`, and `main()`.

Control flow: `run_test()` applies a subpage protection bitmap, performs read/write probes across subpages, and checks which accesses fault. `test_anon` maps anonymous memory; `test_file` maps a generated tempfile. `main` handles optional filename input and syscall availability.

State and persistence: Global `file_name`, `in_test`, `errors`, and signal context track the active probe. File-backed test uses the Makefile-generated tempfile.

Dependencies and integration points: Depends on powerpc-specific `subpage_prot` syscall, signal/ucontext reporting, `mmap`, ptrace/syscall headers, and `utils.h`.

Risks: The syscall is powerpc-specific and page-size dependent. Fault address handling must align with subpage granularity or the test can misattribute failures.

Test signals: Pass demonstrates correct read/write blocking for protected subpages in anonymous and file mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c

Purpose: Long-running stress test for a TLB invalidate versus PID/context switch race. It tries to detect stores that continue after mappings are made read-only.

Important APIs and types: Defines cache flush helper `dcbf`, store-pattern encoders/decoders, verification logging helpers, `rim_fn`, `mem_snapshot_fn`, signal/CPU-affinity helpers, alarm handler, and `main()`.

Control flow: Worker threads each own a shared-memory chunk and repeatedly flush/load/compare/store encoded sweep patterns. A snapshot thread repeatedly marks the alias read-only, copies through a second writable alias, restores permissions, and yields. On corruption, all threads verify their chunks and write anomaly logs.

State and persistence: Persistent state includes optional log files under `/tmp/logdir-$pid` when corruption is detected. Runtime state uses SysV shared memory, two attachments, worker pthreads, forked yield loops, CPU affinity, and alarm timeout.

Dependencies and integration points: Depends on pthreads, SysV shared memory, `mprotect`, cache flush instructions, scheduler affinity, signals, and powerpc TLB behavior.

Risks: This is timing-sensitive and can run for a long timeout. It globally creates temporary logs and forked CPU-yield children; cleanup depends on process exit/PDEATHSIG.

Test signals: Pass is reaching timeout without corruption. Failure creates per-thread chunk logs that encode expected versus observed store patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c

Purpose: Tests register preservation and signal behavior when branching through a wild count register target. It intentionally executes an invalid indirect branch.

Important APIs and types: Defines `BAD_NIP`, context save/handlers, register poisoning/checking helpers, OPD handling for ELFv1, `test_wild_bctr()`, and `main()`.

Control flow: `test_wild_bctr()` poisons GPRs, attempts a branch to a bad target (`bctr` path), handles SIGSEGV/SIGUSR2, saves ucontext registers, and checks the kernel did not corrupt preserved registers while reporting the bad NIP.

State and persistence: Global register snapshots and signal status are process-local. No persistent state.

Dependencies and integration points: Depends on powerpc64 ABI differences, ucontext register layout, signals, and inline assembly.

Risks: Highly ABI-sensitive: ELFv1 function descriptors and ELFv2 direct code pointers differ. Compiler register allocation must not defeat the poison/check assumptions.

Test signals: Pass indicates wild indirect branch faults preserve expected userspace register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules

Purpose: udev rule for making the NX gzip accelerator device accessible to selftests.

Important APIs and types: Contains a single rule matching `SUBSYSTEM=="nxgzip"` and `KERNEL=="nx-gzip"`, setting `MODE="0666"`.

Control flow: udev applies the rule when the device node is created, affecting permissions before tests open `/dev/crypto/nx-gzip`.

State and persistence: Persistent state is system device-node permissions managed by udev, not by the test binary.

Dependencies and integration points: Integrates with the NX gzip kernel driver and the selftest deployment environment.

Risks: Broad world-writable mode is appropriate for test machines but may be undesirable on production systems.

Test signals: Test signal is unprivileged ability to open `/dev/crypto/nx-gzip`; the shell wrapper skips when it is not writable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/99-nx-gzip.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile

Purpose: Build definition for NX gzip accelerator selftests. It builds compression and decompression samples and runs them via a shell harness.

Important APIs and types: Defines `TEST_GEN_FILES := gzfht_test gunz_test`, `TEST_PROGS := nx-gzip-test.sh`, includes common lib/flags, and sets `CFLAGS = -O3 -m64 -I./include -I../include`.

Control flow: Both generated files link `gzip_vas.c` and `../utils.c`, giving them common VAS submission and file/sysfs helpers.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Depends on the local include directory, powerpc64 compiler support, and shared kselftest libraries.

Risks: If `gzip_vas.c` is not linked into both tools, hardware submission symbols are missing. The forced `-m64` reflects VAS/NX ABI expectations.

Test signals: Build success plus wrapper execution over random files validates the Makefile wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c

Purpose: Sample NX hardware gzip decompressor. It parses gzip headers, streams compressed data through NX, resumes partial deflate states, and verifies trailer CRC/ISIZE.

Important APIs and types: Key helpers are FIFO macros, `nx_append_dde`, `nx_touch_pages_dde`, `nx_submit_job`, `decompress_file`, and `main`. Uses `struct nx_gzip_crb_cpb_t`, DDE lists, CPB/CSB field macros, and `nx_function_begin/end`.

Control flow: `decompress_file()` opens stdin/file input, parses gzip metadata, allocates ring buffers, alternates read/write/decompress states, builds source/target DDEs including history for resume, submits jobs, handles NX condition codes (`ERR_NX_AT_FAULT`, `ERR_NX_DATA_LENGTH`, `ERR_NX_TARGET_SPACE`, `ERR_NX_OK`), updates FIFO offsets, and verifies the gzip trailer.

State and persistence: State includes input/output FIFOs, history length, compression-ratio heuristic, CPB/CRB status, page-fault retry counts, and output file handles. It writes `<input>.nx.gunzip` for file input.

Dependencies and integration points: Depends on `nxu.h`, `nx.h`, `crb.h`, `gzip_vas.c`, POSIX files, aligned allocation, signals, and the NX gzip VAS device.

Risks: This is demonstration code, not production decompression. The state machine is complex, condition-code handling is hardware-specific, and page-fault retries assume userspace can fault pages in before NX access.

Test signals: Pass through `nx-gzip-test.sh` means hardware decompression completed and checksum/size matched for generated compressed streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c

Purpose: Sample NX gzip compressor using fixed Huffman blocks. It compresses a file to `<name>.nx.gz` through the NX accelerator and emits a simple gzip wrapper.

Important APIs and types: Important routines are `compress_fht_sample`, `gzip_header_blank`, `append_sync_flush`, `set_bfinal`, `compress_file`, and `main`. Uses CPB/CRB/DDE macros and `nxu_submit_job`.

Control flow: `compress_file()` reads the full input, chooses chunk size from NX sysfs capability or a fallback, writes a gzip header, submits fixed-Huffman compression jobs chunk by chunk, handles page-fault condition code retries, inserts sync flush blocks between chunks, carries CRC state, appends trailer CRC/ISIZE, and writes the output file.

State and persistence: State includes allocated input/output buffers, CRB/CPB command block, CRC, source/target totals, chunk size, and fault retry counter. It creates `<input>.nx.gz`.

Dependencies and integration points: Depends on `utils.h` for file/sysfs helpers, `nxu.h`/`nx.h`, `gzip_vas.c`, and NX gzip VAS device support.

Risks: Output buffer sizing and fixed-Huffman-only behavior make it a sample rather than full gzip implementation. Hardware condition codes and sysfs caps are platform-specific.

Test signals: Pass means the accelerator can compress random files and the paired `gunz_test` can decompress and validate them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c

Purpose: Shared VAS/NX submission backend for the gzip compressor and decompressor samples. It opens the accelerator, maps a paste window, submits CRBs with copy/paste instructions, waits for CSB completion, and faults in pages.

Important APIs and types: Defines `struct nx_handle`, `open_device_nodes`, `nx_function_begin`, `nx_function_end`, `nx_wait_for_csb`, `nxu_run_job`, `nxu_submit_job`, `nxu_sigsegv_handler`, and `nxu_touch_pages`.

Control flow: `nx_function_begin()` opens `/dev/crypto/nx-gzip`, issues `VAS_TX_WIN_OPEN`, maps the VAS window, and records the paste address. Job submission copies the CRB, pastes to the window, polls CSB validity with timebase/usleep backoff, handles fault-storage addresses from SIGSEGV, and returns NX completion code. `nx_function_end()` unmaps/closes/frees resources.

State and persistence: State is the heap `nx_handle`, mapped VAS page, file descriptor, and global `nx_fault_storage_address`. No durable state is stored.

Dependencies and integration points: Depends on local `vas-api.h`, `copy-paste.h`, `nxu.h`, `nx_dbg.h`, PPC timebase APIs, and the NX/VAS kernel driver.

Risks: Paste retry/poll loops can hang or run long on broken hardware. Signal-based fault recovery is specialized and assumes the test process owns the fault context.

Test signals: Successful compression/decompression jobs validate device open, VAS mapping, copy/paste instructions, CSB polling, and page touching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h

Purpose: Inline assembly helpers for PowerPC VAS copy and paste instructions used to submit accelerator work.

Important APIs and types: Defines instruction encodings `PPC_INST_COPY`/`PPC_INST_PASTE`, register-field macros, `PPC_COPY`, `PPC_PASTE`, CR0 extraction constants, and inline functions `vas_copy` and `vas_paste`.

Control flow: `vas_copy` emits a copy instruction for the CRB address and returns CR0 status. `vas_paste` emits a paste instruction to the mapped paste address and returns CR0 status so callers can distinguish accepted/retry cases.

State and persistence: No persistent state; only condition register bits and memory ordering around accelerator submission are affected.

Dependencies and integration points: Consumed by `gzip_vas.c`. Depends on compiler inline asm and raw instruction support for VAS instructions.

Risks: Raw instruction encoding must match the architecture. Incorrect CR0 interpretation changes retry behavior and can make jobs appear submitted when they were not.

Test signals: Passing NX gzip tests demonstrate that copy/paste status codes are interpreted correctly enough to drive hardware jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/copy-paste.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h

Purpose: Defines generic NX coprocessor request/status/descriptor block layouts and constants. It is a lower-level hardware-format header used by the gzip sample code.

Important APIs and types: Declares `struct coprocessor_completion_block`, `struct coprocessor_status_block`, `struct data_descriptor_entry`, and `struct coprocessor_request_block`; defines CCB/CSB/DDE/CRB sizes, alignments, masks, completion codes, and field access macros.

Control flow: No executable flow. Callers populate DDEs and CRBs, submit to NX, then decode CSB completion codes and processed-byte counts using these definitions.

State and persistence: No software persistence. Structures are shared memory contracts with the accelerator and kernel driver.

Dependencies and integration points: Included by `gunz_test.c` and related NX code; depends on endian helpers and `nx.h`.

Risks: The structs are hardware ABI. Padding, endianness, alignment, and bit masks are all correctness-critical.

Test signals: Successful NX jobs and sensible CSB condition codes validate the header definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h

Purpose: Small public interface header for NX accelerator function selection and generic buffer descriptors.

Important APIs and types: Defines `NX_FUNC_COMP_842`, `NX_FUNC_COMP_GZIP`, `__aligned`, `struct nx842_func_args`, `struct nxbuf_t`, and prototypes `nx_function`/`nx_function_end`.

Control flow: No control flow. It gives callers common constants and prototypes for accelerator setup/teardown.

State and persistence: No state is held here; callers own handles and buffers.

Dependencies and integration points: Included by NX gzip and CRB headers. It mirrors older/libnxz-style user API shapes.

Risks: Prototype drift from actual implementation can break builds. Some declarations are broader than the gzip-only implementation in this directory.

Test signals: Compile/link coverage from `gzfht_test` and `gunz_test` validates the used subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h

Purpose: Debug and tracing macro header for NX gzip sample code.

Important APIs and types: Declares external debug globals and defines `prt`, `prt_err`, `prt_warn`, `prt_info`, `prt_trace`, `prt_stat`, `hw_trace`, `sw_trace`, plus `nx_lib_debug` prototype.

Control flow: Macros conditionally print to `stderr` or `nx_gzip_log` depending on global trace/debug flags. There is no function body in this header.

State and persistence: State is external: `nx_dbg`, trace masks, implementation flags, and optional log file pointer.

Dependencies and integration points: Used by `gzip_vas.c` and compatible with libnxz-style debug controls.

Risks: Because logging macros evaluate variadic arguments in conditional blocks, callers should avoid side effects. Missing global definitions cause link failures.

Test signals: Trace output during NX failures is the primary test signal; normal tests usually run with debug disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h

Purpose: Primary NX gzip hardware-format and utility macro header. It defines gzip CRB/CPB layouts, bitfield access helpers, function codes, errors, and helper prototypes.

Important APIs and types: Important types include `nx_dde_t`, `nx_csb_t`, `nx_ccb_t`, `vas_stamped_crb_t`, `nx_stamped_fault_crb_t`, `nx_gzip_cpb_t`, `nx_gzip_crb_t`, `nx_gzip_crb_cpb_t`, and `nx_eft_crb_t`. It defines `getnn/putnn`, CSB completion helpers, gzip function codes, and `ERR_NX_*` values.

Control flow: No executable flow, but the macros are the way compressor/decompressor code encodes and decodes all CRB/CPB fields before and after hardware submission.

State and persistence: No persistent state. It defines memory layouts shared between userspace and NX hardware/kernel.

Dependencies and integration points: Included by all NX gzip C files and relies on endian conversion, PPC timebase when enabled, and matching accelerator documentation.

Risks: Very high ABI risk: bit offsets, endian conversions, and struct alignment must remain exact. Macro misuse can silently write wrong fields.

Test signals: Passing compression/decompression plus correct condition-code handling validate the portions of this header used by the samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nxu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h

Purpose: Local VAS ioctl ABI copy for NX gzip selftests. It lets the tests open a transmit window without depending on installed kernel headers.

Important APIs and types: Defines `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr`.

Control flow: No executable flow. `gzip_vas.c` fills the struct and issues the ioctl before mapping the paste window.

State and persistence: No direct state; ioctl success creates kernel VAS state associated with the file descriptor.

Dependencies and integration points: Depends on Linux type/ioctl headers and must match the kernel VAS uAPI.

Risks: Header drift from the kernel ABI breaks accelerator open or silently changes attributes.

Test signals: Successful `nx_function_begin()` is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh

Purpose: End-to-end shell harness for NX gzip hardware compression/decompression samples.

Important APIs and types: Checks `/dev/crypto/nx-gzip` writability, defines cleanup and `test_sizes`, creates random files with `dd`, runs `gzfht_test`, then `gunz_test`, and executes both serial and 16-way parallel loops.

Control flow: The script skips when the device is inaccessible, enables `set -e`, tests 4K/64K/1M/64M random inputs, removes temporary files on exit, and reports OK after all background jobs finish.

State and persistence: Creates temporary `nx-tempfile*`, `.nx.gz`, and `.nx.gunzip` outputs in the working directory until cleanup runs.

Dependencies and integration points: Depends on bash, `dd`, the two generated binaries, and NX gzip device permissions.

Risks: Parallel stress can be resource-heavy and assumes enough disk/time for 16 sets of large random files. Cleanup is filename-pattern based.

Test signals: Pass means all serial and parallel compression/decompression runs complete with matching checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/nx-gzip-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile

Purpose: Build definition for the PAPR energy/frequency attributes selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := attr_test`, includes kselftest libs and powerpc flags, and links with `../harness.c` plus `../utils.c`.

Control flow: Normal kselftest build emits the single `attr_test` binary.

State and persistence: No runtime state is defined here.

Dependencies and integration points: Depends on the parent selftest framework and `attr_test.c`.

Risks: If the target is omitted, PAPR attribute coverage disappears from test enumeration.

Test signals: Build and run discovery of `attr_test` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c

Purpose: Tests sysfs PAPR energy/frequency attribute exposure and type correctness.

Important APIs and types: Defines `enum energy_freq_attrs`, `enum type`, `value_type`, `verify_energy_info`, and `main()`.

Control flow: `verify_energy_info()` walks expected sysfs attributes, determines whether each value should be string or numeric, reads files, and validates presence/format. `main()` runs it through the harness.

State and persistence: No state is modified; it only reads sysfs attribute files.

Dependencies and integration points: Depends on PAPR platform sysfs layout, `utils.h` file helpers, and the kselftest harness.

Risks: Sysfs availability is platform/firmware dependent. Format checks must track kernel ABI changes for new attributes.

Test signals: Pass means expected PAPR energy/frequency attributes are present and parseable on supported systems; unsupported systems should skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/attr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile

Purpose: Build definition for the `/dev/papr-sysparm` ioctl ABI selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := papr_sysparm`, includes common make fragments, links shared harness/utils, and adds `$(KHDR_INCLUDES)` for kernel UAPI headers.

Control flow: The default target recurses to the parent; normal builds produce `papr_sysparm`.

State and persistence: No runtime persistence.

Dependencies and integration points: Depends on `<asm/papr-sysparm.h>` availability through kernel headers and the local test source.

Risks: Missing `KHDR_INCLUDES` would break builds on systems without installed headers.

Test signals: Compile success and test enumeration validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c

Purpose: Exercises the `/dev/papr-sysparm` character-device ioctl ABI for reading and rejecting system parameters.

Important APIs and types: Defines tests `open_close`, `get_splpar`, `get_bad_parameter`, `check_efault_get`, `check_efault_set`, `set_hmc0`, `set_with_ro_fd`, the `sysparm_test` table, and `main()`.

Control flow: `main()` iterates table-driven subtests. The tests open the device, GET parameter 20, verify unsupported parameter leaves buffers unchanged, verify NULL pointers return `EFAULT`, and verify SET permission/read-only-fd errors are `EPERM` or `EBADF` with skips for unsupported firmware operations.

State and persistence: No persistent state is changed; attempted SETs target non-settable HMC0 and are expected to fail.

Dependencies and integration points: Depends on `/dev/papr-sysparm`, `<asm/papr-sysparm.h>`, errno semantics, and `utils.h`.

Risks: Firmware may not support SET, producing skips. Error-code expectations are part of the ABI and should be changed only with kernel/userspace contract updates.

Test signals: Pass means the sysparm device handles valid GETs and rejects invalid operations with stable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile

Purpose: Build definition for the `/dev/papr-vpd` ioctl/read ABI selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := papr_vpd`, includes common make fragments, links harness/utils, and adds `$(KHDR_INCLUDES)` for `<asm/papr-vpd.h>`.

Control flow: Normal kselftest builds the `papr_vpd` binary.

State and persistence: No runtime state here.

Dependencies and integration points: Depends on kernel UAPI headers and `papr_vpd.c`.

Risks: Header include configuration is the main risk; without it, local builds may fail despite source being correct.

Test signals: Build success and emitted test name are validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c

Purpose: Table-driven tests for the `/dev/papr-vpd` Vital Product Data interface. It validates handle creation, reads, invalid inputs, rereads, and system location-code lookup.

Important APIs and types: Defines tests for open/close, all-VPD handle, byte-at-a-time reads, unterminated location code, NULL handle pointer, close-without-read, reread consistency, system location code, plus `get_system_loc_code`, `vpd_test` table, and `main()`.

Control flow: Each subtest opens `/dev/papr-vpd`, creates a read handle with `PAPR_VPD_IOC_CREATE_HANDLE`, reads via the returned fd, checks size/EOF/content containing `System VPD`, or verifies invalid inputs return `EINVAL`/`EFAULT`. System location code is derived from device-tree `model` and `system-id` files.

State and persistence: No persistent kernel state should change. It allocates buffers and opens transient fds for VPD handles.

Dependencies and integration points: Depends on `/dev/papr-vpd`, `<asm/papr-vpd.h>`, device-tree sysfs files, GNU `memmem`, and `utils.h` file helpers.

Risks: Platform VPD content and location-code formatting are firmware-dependent, so some subtests skip when data cannot be determined. The test assumes `System VPD` appears in returned blobs.

Test signals: Pass confirms stable PAPR VPD ioctl, read, EOF, and error handling semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile

Purpose: Top-level build/run definition for powerpc PMU selftests. It builds basic PMU counter tests and recurses into EBB, sampling, and event-code subdirectories.

Important APIs and types: Defines `TEST_GEN_PROGS`, `EXTRA_SOURCES`, `SUB_DIRS`, custom `RUN_TESTS`, `emit_tests`, `INSTALL_RULE`, and `CLEAN`. Adds `-m64` and `loop.S` dependencies for instruction-count tests.

Control flow: Builds local tests, then creates per-subdir output directories and invokes sub-makes. Run/install/emit/clean logic wraps default kselftest behavior and then iterates subdirectories.

State and persistence: No runtime persistence beyond build outputs and recursive output trees.

Dependencies and integration points: Depends on `event.c`, `lib.c`, `../utils.c`, `../harness.c`, `loop.S`, and child directory Makefiles.

Risks: Recursive make logic can hide failures if output paths are wrong. `loop.S` must be built 64-bit for instruction count accuracy.

Test signals: Signals are correct emitted test names for local and child tests plus successful recursive builds/runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S

Purpose: Assembly loop for PMU branch event testing. It repeatedly performs an indirect branch via CTR for a large iteration count.

Important APIs and types: Exports `indirect_branch_loop` and defines `ITER_SHIFT` to set loop count to `1 << 31`.

Control flow: The function initializes a counter, decrements it, loads the address of a local branch target through the TOC/GOT, moves it into CTR, and executes `bctr` until the count reaches zero.

State and persistence: No persistent state. It consumes CPU and branch predictor/PMU resources.

Dependencies and integration points: Depends on powerpc assembly macros from `ppc-asm.h` and PMU tests that call it.

Risks: Long loops are intentionally expensive. ABI/TOC addressing must match the link mode.

Test signals: PMU branch counter tests use this routine to produce repeatable indirect branch traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c

Purpose: Counts a known instruction loop with perf events and verifies PMU instruction counters are close to expected values.

Important APIs and types: Defines `setup_event`, `do_count_loop`, `determine_overhead`, `test_body`, `count_instructions`, and `main()`. Calls external `thirty_two_instruction_loop` from `loop.S`.

Control flow: `test_body()` configures events, measures overhead, runs loops for requested instruction counts, reads perf counters, and checks deltas against expected instruction totals with tolerances.

State and persistence: State lives in local `struct event` objects and perf fds; no persistence.

Dependencies and integration points: Depends on `event.h`, `lib.h`, `utils.h`, perf_event_open support, and 64-bit assembly loop code.

Risks: Counter skid, privilege filters, and PMU availability can affect accuracy. The test assumes the assembly loop contains a stable instruction count.

Test signals: Pass means instruction PMU events count deterministic userspace loops within expected bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c

Purpose: Counts failed store-conditional operations with PMU events. It validates marked and unmarked `stcx.` failure event behavior.

Important APIs and types: Defines `setup_event`, `do_count_loop`, `determine_overhead`, constants `PM_MRK_STCX_FAIL`/`PM_STCX_FAIL`, `test_body`, `count_ll_sc`, and `main()`. Calls `thirty_two_instruction_loop_with_ll_sc`.

Control flow: The test configures PMU events, runs a deterministic loop containing load-linked/store-conditional sequences against a target, reads counters, subtracts overhead, and checks expected failure counts.

State and persistence: State is local perf events and the LL/SC target memory word.

Dependencies and integration points: Depends on perf events, PMU event codes, `event.h`, `lib.h`, and the assembly loop implementation.

Risks: Event encodings can vary by CPU generation; marked-event behavior can be privilege/filter sensitive.

Test signals: Pass confirms PMU event codes count failed `stcx.` sequences as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile

Purpose: Build definition for Event Based Branching selftests. It compiles all EBB tests with the shared handler, helpers, event library, and 64-bit/non-PIE constraints.

Important APIs and types: Defines a long `TEST_GEN_PROGS` list, includes build/lib/flags, forces `CFLAGS += -m64`, detects `-no-pie`, and links every test with `ebb.c`, `ebb_handler.S`, `trace.c`, `busy_loop.S`, PMU event/lib sources, harness, and utils.

Control flow: Normal builds produce each EBB binary. Special dependency adds `../loop.S` for `instruction_count_test` and extra `../lib.c` for `lost_exception_test`.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Depends on powerpc64 EBB assembly, perf event helpers, and toolchain support for non-PIE handler code.

Risks: PIE builds break absolute handler assumptions; missing `-m64` breaks the EBB handler ABI.

Test signals: Successful build of all EBB binaries is the primary Makefile test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c

Purpose: Tests delivery of many EBBs back-to-back without losing handler state. It forces repeated PMC overflows.

Important APIs and types: Defines `NUMBER_OF_EBBS`, custom `ebb_callee`, `back_to_back_ebbs`, and `main()`.

Control flow: The test sets an EBB handler that counts and resets overflows, configures a cycles event, repeatedly drives the busy loop until the target EBB count is reached, then disables/freezes PMCs and validates counts.

State and persistence: Uses global `ebb_state` and `sample_period` from `ebb.c`; perf event fd is local.

Dependencies and integration points: Depends on `ebb.h`, perf events, and `core_busy_loop`.

Risks: Very small sample periods can expose timing races; handler reset ordering is critical.

Test signals: Pass means repeated adjacent overflows are delivered and accounted without spurious loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S

Purpose: Assembly CPU burner used by EBB tests to generate PMU events predictably.

Important APIs and types: Exports `core_busy_loop` and contains long loops of arithmetic/branch work with EBB-safe return behavior.

Control flow: Callers invoke it repeatedly while PMCs count cycles/instructions. It returns control for C-side checks after loop completion or interruption.

State and persistence: No persistent state; only CPU/PMU activity is generated.

Dependencies and integration points: Linked into all EBB tests by the EBB Makefile.

Risks: Instruction mix and loop length affect event rates and test timing. Assembly must remain compatible with the EBB handler ABI.

Test signals: Tests pass when this loop reliably causes configured PMU overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c

Purpose: Verifies that closing an EBB perf event clears PMU control state enough that later privileged PMC access faults as expected.

Important APIs and types: Defines `close_clears_pmcc()` and `main()`, using `catch_sigill`, `write_pmc1`, and event helpers.

Control flow: The test opens/enables an EBB event, closes it, then attempts direct PMC access under a SIGILL catcher to ensure permissions/control bits were cleared.

State and persistence: Local perf event state is opened and closed; no persistence.

Dependencies and integration points: Depends on `ebb.h`, perf event cleanup, and SIGILL behavior for unauthorized SPR access.

Risks: If hardware allows PMC writes for other reasons, interpretation changes. Cleanup ordering matters.

Test signals: Pass means perf close removes user PMC access enabled for EBB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c

Purpose: Tests conflict behavior between a pinned CPU perf event and a task EBB event.

Important APIs and types: Defines `setup_cpu_event`, `cpu_event_pinned_vs_ebb`, and `main()`.

Control flow: It opens a pinned CPU event on a target CPU, forks or coordinates an EBB child, attempts to enable the EBB event, and checks that scheduling/conflict behavior matches expectations.

State and persistence: Perf fds and child process state are transient.

Dependencies and integration points: Depends on `ebb.h`, CPU-bound perf events, fork/wait, and event pinning semantics.

Risks: Results depend on PMU scheduling policy and available counters. Pinned conflicts are architecture/kernel policy sensitive.

Test signals: Pass confirms pinned CPU events and EBB events arbitrate consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c

Purpose: Tests coexistence/conflict behavior between a non-pinned CPU perf event and an EBB event.

Important APIs and types: Defines `setup_cpu_event`, `cpu_event_vs_ebb`, and `main()`.

Control flow: The test starts a CPU-wide event, runs an EBB workload, then checks whether both can be scheduled or whether expected failures are reported without leaving child processes behind.

State and persistence: Only transient perf and child process state is used.

Dependencies and integration points: Depends on PMU event scheduling, `ebb_child`, and synchronization helpers from the PMU library.

Risks: Kernel PMU scheduling changes can alter whether events coexist. The test must distinguish expected scheduling failure from EBB malfunction.

Test signals: Pass validates non-pinned CPU event interaction with EBB task events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c

Purpose: Basic EBB cycles event test. It verifies that a cycles event can generate EBBs and increment state.

Important APIs and types: Defines `cycles()` and `main()`; uses `event_init_named`, `event_leader_ebb_init`, `setup_ebb_handler`, `ebb_global_enable`, and `core_busy_loop`.

Control flow: `cycles()` skips without EBB support, configures a cycles event excluding kernel/hypervisor/idle, enables counting, seeds PMC1, runs the busy loop until EBBs arrive, disables/freezes, dumps state, and checks count > 0.

State and persistence: Uses shared `ebb_state`; perf event fd is local.

Dependencies and integration points: Depends on `ebb.h`, perf events, and POWER8+ EBB support.

Risks: If counters are frozen or sample period unsuitable, no EBB arrives. Environment PMU restrictions can cause skips/failures.

Test signals: Pass is at least one counted EBB with sane state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c

Purpose: Tests EBB behavior while PMCs are deliberately frozen and unfrozen. It checks that no EBBs are counted during freeze windows.

Important APIs and types: Defines global `counters_frozen`, `ebbs_while_frozen`, custom `ebb_callee`, `cycles_with_freeze()`, and `main()`.

Control flow: The test configures a cycles EBB event, alternates `ebb_freeze_pmcs`/`ebb_unfreeze_pmcs` while running busy loops, and the handler records if an EBB arrives while the frozen flag is set.

State and persistence: Shared globals record freeze state and unexpected EBBs; `ebb_state` records normal counts.

Dependencies and integration points: Depends on MMCR0 freeze behavior, EBB handler reset, and perf setup helpers.

Risks: Races around the software `counters_frozen` flag and hardware freeze transition can produce edge-sensitive failures.

Test signals: Pass means freeze suppresses PMU progress/EBB delivery during the tested windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c

Purpose: Checks that MMCR2 freeze-control bits interact correctly with EBB cycles events.

Important APIs and types: Defines expected MMCR2 constants, `cycles_with_mmcr2()`, and `main()`.

Control flow: The test programs MMCR2, runs a cycles EBB workload, samples hardware state, and verifies expected MMCR2 bit patterns before/after enabling and freezing counters.

State and persistence: State is hardware PMU registers plus shared EBB stats.

Dependencies and integration points: Depends on SPR access through `ebb.h`, perf event setup, and CPU support for MMCR2 semantics.

Risks: MMCR2 layout is CPU-generation specific; expected constants must match supported processors.

Test signals: Pass means EBB setup preserves/uses MMCR2 freeze controls as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c

Purpose: Shared runtime library for EBB selftests. It manages handler setup, EBB reset, PMU register access, event initialization, child workload coordination, tracing, and diagnostics.

Important APIs and types: Exports `ebb_hook`, `reset_ebb`, `ebb_check_mmcr0`, `ebb_check_count`, `standard_ebb_callee`, `setup_ebb_handler`, dump/clear helpers, `count_pmc`, `ebb_event_enable`, freeze/global enable controls, `ebb_is_supported`, event init helpers, `ebb_child`, `catch_sigill`, `write_pmc`, `read_pmc`, and constructor `ebb_init`.

Control flow: Tests call event init/setup helpers, install `ebb_handler` into EBBHR, enable global EBB state, run loops until PMCs overflow, and handlers call `standard_ebb_callee` or custom callees to count/reset PMCs. The constructor initializes trace buffers and SIGTERM diagnostics.

State and persistence: Global `ebb_state`, `sample_period`, `ebb_user_func`, trace buffer, and signal handlers persist for the process lifetime. Hardware PMU SPRs are modified and reset during tests.

Dependencies and integration points: Depends on `ebb.h`, `trace.h`, PMU event helpers, powerpc SPR macros, pipe synchronization from `lib.c`, and assembly `ebb_handler`/`core_busy_loop`.

Risks: High-risk shared code: wrong reset ordering can leave PMCs frozen or EBB disabled, and direct SPR access is privileged/CPU-feature sensitive. Global state means tests must clean up before exit.

Test signals: All EBB test binaries exercise this file; state dumps and EBB counts are primary diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h

Purpose: Public header for the EBB selftest support library. It defines shared state shape, constants, inline helpers, and exported helper prototypes.

Important APIs and types: Defines `PMC_INDEX`, `NUM_PMC_VALUES`, `COUNTER_OVERFLOW`, `struct ebb_state`, `pmc_sample_period`, `ebb_enable_pmc_counting`, and prototypes for handler setup, event init, PMU controls, diagnostics, child runner, SIGILL catcher, and PMC access.

Control flow: No executable control flow except tiny inline helpers. Tests include it to configure events and inspect shared `ebb_state`.

State and persistence: Declares external `ebb_state` and `sample_period`, which are process-global in `ebb.c`.

Dependencies and integration points: Depends on PMU `event.h`, powerpc SPR macros via included utilities, and `core_busy_loop` assembly.

Risks: Header/API drift breaks all EBB tests. Inline SPR manipulation assumes callers already verified EBB/PMU support.

Test signals: Compile coverage by every EBB binary plus runtime helper use validates the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S

Purpose: Low-level Event Based Branching handler. It saves user context, calls the C hook, restores context, and returns with `rfebb`.

Important APIs and types: Defines save-area layout for GPRs, selected SPRs, and VSRs; helper macros for saving/restoring/trashing registers; entry handling for ELFv1/ELFv2; and exports `ebb_handler`.

Control flow: On EBB entry the handler creates an ABI-compliant stack frame, saves registers and vector/scalar state, restores TOC as needed, calls `ebb_hook`, restores all saved state, and executes the raw `RFEBB` instruction.

State and persistence: It uses only the current thread stack for save state but modifies hardware EBB return state. No persistent memory is written outside the stack.

Dependencies and integration points: Linked with all EBB tests and installed into EBBHR by `setup_ebb_handler` in `ebb.c`.

Risks: This is the most ABI-sensitive EBB component. Stack layout, TOC restore, VSR save/restore, and `rfebb` encoding must be correct or tests can corrupt user state.

Test signals: Passing EBB tests, especially register access and repeated EBB tests, validates the handler save/restore path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c

Purpose: Tests attempting to create/use EBB events on a child process that is not explicitly cooperating.

Important APIs and types: Defines `victim_child`, `ebb_on_child`, and `main()`.

Control flow: The parent forks a child workload synchronized by pipes, attempts to attach/configure an EBB event against that child, and checks that kernel policy rejects or handles it as expected.

State and persistence: State is child PID, pipes, and perf event fd.

Dependencies and integration points: Depends on `ebb.h`, PMU lib pipe helpers, fork/wait, and perf task attachment semantics.

Risks: Expected behavior is policy-sensitive; tests must avoid leaving child processes running on failure.

Test signals: Pass confirms EBB task attachment to an unwilling child follows the kernel contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c

Purpose: Tests EBB operation with a child process that cooperates in setting up/running the EBB workload.

Important APIs and types: Defines `victim_child`, `ebb_on_willing_child`, and `main()`.

Control flow: The child waits for parent coordination, then runs EBB setup/workload or allows parent-controlled event setup. The parent synchronizes and verifies successful EBB delivery/cleanup.

State and persistence: Uses child process and pipe synchronization state only.

Dependencies and integration points: Depends on `ebb_child`/pipe helpers, perf events, and EBB support.

Risks: Parent/child synchronization failures can look like PMU failures. Cleanup must kill/wait child on error.

Test signals: Pass indicates EBB works in the intended child coordination scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c

Purpose: Tests the reverse ordering of EBB event creation versus CPU-wide perf event creation.

Important APIs and types: Defines `setup_cpu_event`, `ebb_vs_cpu_event`, and `main()`.

Control flow: The test starts an EBB workload first, then attempts a CPU event and checks expected scheduling/conflict behavior, contrasting with the CPU-first tests.

State and persistence: Transient perf and child state only.

Dependencies and integration points: Depends on PMU scheduling, `ebb.h`, fork/wait, and event helper APIs.

Risks: Ordering-sensitive PMU constraints may differ by kernel/CPU. The test encodes expected arbitration behavior.

Test signals: Pass confirms event ordering does not leave EBB/CPU events in an inconsistent state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c

Purpose: Validates perf event attribute requirements for EBB events. It checks accepted/rejected combinations of pinned, exclusive, config bits, and grouping.

Important APIs and types: Defines `event_attributes()` and `main()` using event initialization helpers from `ebb.h`/`event.h`.

Control flow: The test constructs several perf event attributes, opens them, and expects success or failure depending on EBB constraints such as leader/pinned/exclusive configuration.

State and persistence: Perf fds are opened/closed per case; no persistence.

Dependencies and integration points: Depends on perf_event_open validation in the kernel and local event wrappers.

Risks: Kernel policy changes to EBB attribute validation require updating expected outcomes.

Test signals: Pass means userspace receives stable success/error behavior for EBB perf attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c

Purpose: Tests that EBB state is cleaned up correctly across fork. It ensures a child does not inherit usable stale EBB PMU state unexpectedly.

Important APIs and types: Defines global `event`, child function `child`, `fork_cleanup`, and `main()`.

Control flow: The parent configures EBB state, forks, the child probes inherited PMC/EBB access with SIGILL-catching behavior, and the parent waits/validates cleanup semantics.

State and persistence: Global event state exists only for the process lifetime and is closed before exit.

Dependencies and integration points: Depends on fork semantics, EBB state cleanup in the kernel, and `catch_sigill` helpers.

Risks: Fork inheritance rules are subtle; failure could indicate either kernel cleanup issues or test ordering mistakes.

Test signals: Pass means forked children do not retain unsafe EBB access/state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c

Purpose: EBB variant of deterministic instruction counting. It verifies PMU instruction counts collected via EBB overflows.

Important APIs and types: Defines `do_count_loop`, `determine_overhead`, custom `pmc4_ebb_callee`, `instruction_count`, and `main()`. Calls `thirty_two_instruction_loop`.

Control flow: The test measures overhead, configures an instruction-counting EBB event, runs fixed-size loops, handles PMC4 overflows in the custom callee, and checks accumulated counts against expected instruction totals.

State and persistence: Uses shared `ebb_state`, local event state, and measured overhead values.

Dependencies and integration points: Depends on `ebb.h`, `loop.S`, perf instruction events, and PMU counter routing to PMC4.

Risks: Instruction count tolerance depends on exact assembly loop and handler overhead. PMU event placement must match the custom handler.

Test signals: Pass shows EBB-based instruction counting is accurate enough for deterministic loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c

Purpose: Regression test for lost EBB exceptions around scheduling and signal/mmap activity. It tries to expose pending EBBs that fail to deliver.

Important APIs and types: Defines `test_body`, wrapper `lost_exception`, and `main()`.

Control flow: `test_body()` configures EBBs, runs busy loops and scheduler activity, may use mappings/signals, and checks that expected EBB counts arrive rather than being silently lost.

State and persistence: Uses process-global EBB state and transient mappings.

Dependencies and integration points: Depends on `ebb.h`, scheduler behavior, and PMU exception delivery.

Risks: Race/timing-sensitive by design; failures can be hard to reproduce without the same CPU load.

Test signals: Pass indicates no lost EBB delivery under the tested stress pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c

Purpose: Tests EBB handling when multiple PMCs are enabled. It verifies overflows and counts across more than one counter.

Important APIs and types: Defines `multi_counter()` and `main()`.

Control flow: The test configures a group of EBB-capable events/counters, enables relevant PMC counting bits, runs the busy loop, then validates each enabled counter through shared EBB stats.

State and persistence: Uses `ebb_state.pmc_enable` and per-PMC accumulated counts.

Dependencies and integration points: Depends on EBB support for multiple PMCs, perf grouping, and handler `count_pmc` logic.

Risks: Counter routing and availability differ by CPU; the test assumes the selected events can coexist.

Test signals: Pass means the handler accounts multiple counter overflows correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c

Purpose: Runs multiple EBB child processes in parallel to test isolation and concurrent PMU use.

Important APIs and types: Defines SIGINT handler/action, `cycles_child`, `NR_CHILDREN`, `multi_ebb_procs`, and `main()`.

Control flow: `multi_ebb_procs()` forks several children running cycles EBB workloads, waits for completion, handles interrupt cleanup, and fails if any child reports EBB failure.

State and persistence: State is child PID list, signal action, and per-child EBB process state.

Dependencies and integration points: Depends on `ebb.h`, fork/wait, and PMU scheduling across processes.

Risks: Parallel PMU tests can be affected by system load and counter scarcity. Cleanup on interrupt is important to avoid stray busy children.

Test signals: Pass means separate processes can use EBBs concurrently without corrupting each other.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c

Purpose: Tests behavior when EBBs are enabled without installing a valid userspace handler.

Important APIs and types: Defines `no_handler_test()` and `main()`.

Control flow: The test configures an EBB event but deliberately avoids normal handler setup, runs enough work to trigger an EBB, and verifies the kernel reports or handles the missing handler as expected rather than corrupting state.

State and persistence: Transient perf and signal/process state only.

Dependencies and integration points: Depends on EBB exception delivery semantics and `ebb.h` helpers.

Risks: Expected failure mode is architecture-specific; unsafe handler address behavior must be contained by the test process.

Test signals: Pass confirms missing-handler EBB behavior is controlled and diagnosable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c

Purpose: Tests PMAE/PMEO handling around syscalls from within an EBB handler. It verifies reset logic when EBBs occur near syscall boundaries.

Important APIs and types: Defines custom `syscall_ebb_callee`, `test_body`, `pmae_handling`, and `main()`.

Control flow: The handler performs a syscall or syscall-like operation while servicing an EBB, then resets EBB state. The body drives events and checks PMAE/PMEO bits are handled so counting continues correctly.

State and persistence: Uses global EBB stats and hardware BESCR/MMCR0 state.

Dependencies and integration points: Depends on `ebb.h`, syscall behavior from handler context, and PMU SPR semantics.

Risks: Calling into C/syscall paths from an exception handler is delicate and can expose ABI ordering issues.

Test signals: Pass means PMAE handling remains correct across handler/syscall interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c

Purpose: Verifies EBB delivery and accounting for PMC5/PMC6 overflows, not just PMC1-4.

Important APIs and types: Defines custom `ebb_callee`, `pmc56_overflow`, and `main()`.

Control flow: The test configures events routed to PMC5/PMC6, enables counting, runs work until overflows occur, and the handler counts/resets those PMCs before validation.

State and persistence: Uses shared EBB per-PMC counters.

Dependencies and integration points: Depends on hardware support for PMC5/PMC6 EBB overflow and local handler logic.

Risks: Some CPUs or event combinations may not route as expected. Overflow detection for higher PMCs must match SPR numbering.

Test signals: Pass indicates PMC5/PMC6 overflow handling is covered by EBB support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c

Purpose: Checks userspace access to PMU/EBB registers when EBB is enabled. It validates that expected SPR accesses are legal or faulting.

Important APIs and types: Defines `reg_access()` and `main()` and uses helpers such as `catch_sigill`, `write_pmc`, and EBB setup APIs.

Control flow: The test attempts selected SPR reads/writes before/after EBB event setup and verifies SIGILL behavior or success matches the kernel access-control contract.

State and persistence: No persistence; only PMU SPRs and event fds are touched.

Dependencies and integration points: Depends on powerpc SPR access rules, EBB support, and signal handling.

Risks: Hardware generation and kernel policy determine which registers are accessible; expected cases must stay aligned with the ABI.

Test signals: Pass confirms PMU register access control around EBB setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c

Purpose: Tests PMU register access when the extended PMCC capability is involved. It is a focused access-control regression test.

Important APIs and types: Defines `regs_access_pmccext()` and `main()`.

Control flow: The test probes PMC access under conditions involving PMCC extension support, expecting allowed operations to succeed and disallowed ones to SIGILL/fail.

State and persistence: Only transient PMU and signal state is used.

Dependencies and integration points: Depends on kernel exposure of PMC access extension semantics and `ebb.h` helpers.

Risks: CPU feature availability controls whether the test is meaningful. Misdetecting support can create false failures.

Test signals: Pass means extended PMC access rules are enforced as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c

Purpose: Tests conflict behavior between a pinned task perf event on a child and an EBB event.

Important APIs and types: Defines `setup_child_event`, `task_event_pinned_vs_ebb`, and `main()`.

Control flow: The test creates a child workload, attaches a pinned task event, then attempts/runs EBB setup and checks expected scheduling failure or coexistence behavior.

State and persistence: State is child PID, perf event fd, and pipe/wait coordination.

Dependencies and integration points: Depends on task-attached perf events, event pinning, and EBB scheduling rules.

Risks: Pinned task events can monopolize counters; expected behavior may vary with PMU counter availability.

Test signals: Pass validates kernel arbitration between pinned task events and EBB events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c

Purpose: Tests interaction between a non-pinned task perf event on a child and an EBB event.

Important APIs and types: Defines `setup_child_event`, `task_event_vs_ebb`, and `main()`.

Control flow: The test attaches a normal task event to a child, runs or attempts an EBB workload, and validates expected scheduling/coexistence outcomes with cleanup.

State and persistence: Transient child and perf state only.

Dependencies and integration points: Depends on `ebb.h`, perf task event scheduling, fork/wait, and pipe helpers.

Risks: PMU scheduler policy can affect whether both events run together. Child cleanup is important on early failure.

Test signals: Pass confirms non-pinned task event and EBB interaction remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c -->
