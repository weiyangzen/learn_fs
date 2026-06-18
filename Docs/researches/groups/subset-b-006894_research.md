# subset-b-006894 research

This grouped report covers Linux x86 selftests, zram kselftests, userspace testing shims, and VMA harness compatibility files under `sources/distributed-fs/ceph-client/tools/testing`. Each section preserves the original source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/mov_ss_trap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/mov_ss_trap.c

## Purpose

`mov_ss_trap.c` is an x86 selftest for delayed debug exceptions after `MOV SS`. It targets the interaction between stack-segment loads, hardware watchpoints, breakpoint-like instructions, syscall entry paths, and fault delivery, covering regressions related to CVE-2018-1087 and CVE-2018-8897.

## Important APIs, Types, and Functions

The test uses `ptrace(PTRACE_ATTACH/POKEUSER/DETACH)` to program debug registers, `prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY)` to allow the helper child to attach, `sigaction` helpers from `helpers.h`, `sigsetjmp/siglongjmp`, raw inline assembly for `mov %ss`, `int3`, `int $N`, `icebp`, `cli`, page faults, `syscall`, `sysenter`, and `int $0x80`. `enable_watchpoint()` writes DR0 for `ss`, DR1 for the labeled NOP, and DR7 watchpoint controls. Signal handlers print trapped IP and Resume Flag state.

## Control Flow and State

`main()` snapshots the current SS, enables watchpoints from a child tracer, then runs a sequence of `MOV SS` plus one following instruction. Some cases return normally through `SIGTRAP`; faulting or emulator-sensitive cases use `sigsetjmp()` to continue after `SIGSEGV` or `SIGILL`. State is process-local: debug registers persist while the test runs, `ss` is the watched memory, `jmpbuf` carries recovery, and handlers inspect ucontext registers.

## Dependencies and Integration Points

The file integrates with kselftest x86 builds and depends on `helpers.h`, ptrace debug-register layout in `struct user`, architecture-specific ucontext register names, and kernel entry paths for interrupts and syscalls. It is most meaningful on real x86 hardware or accurate emulators.

## Risks and Test Signals

Risks include incorrect #DB deferral across kernel entries, double delivery, lost watchpoints, wrong RF state, unsafe `INT $1`, and broken SYSENTER/SYSCALL recovery. Passing output shows expected `SIGTRAP` or handled fault messages without process death; failures are crashes, missing traps, wrong signal class, or inability to continue past tested entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/mov_ss_trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c

## Purpose

`nx_stack.c` verifies that the userspace stack is non-executable when the binary is linked with a no-exec-stack PT_GNU_STACK policy. It fills stack pages with `INT3` bytes and tries to execute through them, expecting instruction-fetch faults rather than breakpoints.

## Important APIs, Types, and Functions

The assembly helpers `make_stack1()` and `make_stack2()` use `rep stosb` with direction flag changes to paint the stack with `0xcc`. `sigsegv()` drives the state machine by rewriting `RIP/EIP` and `RDI/EDI` in the signal context. `sigtrap()` is the failure path for executable stack pages. `main()` installs SA_SIGINFO handlers, caps `RLIMIT_STACK`, allocates an alternate signal stack with `mmap()` and `sigaltstack()`, and starts the downward stack overwrite.

## Control Flow and State

`test_state` advances from clearing below the current stack pointer, to clearing the other direction, to probing each page, to final success. `stack_min_addr` records the low bound found by the first fault. The test never returns from the first helper in ordinary control flow; it progresses through signal context edits. No persistent state survives the process.

## Dependencies and Integration Points

The test depends on x86 ucontext register layout, signal delivery on an alternate stack, the kernel's stack expansion and NX page protections, and the build system supplying no-exec-stack linking. It is part of the x86 selftest suite.

## Risks and Test Signals

The main risks are executable user stacks, failure to clear DF before signal handlers, stack-limit assumptions, and altstack exhaustion. A pass prints that all stack pages are NX. A `SIGTRAP` means an `INT3` on the stack executed and the test fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ptrace_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ptrace_syscall.c

## Purpose

`ptrace_syscall.c` tests ptrace observation and syscall restart behavior across x86 syscall entry mechanisms. It checks 32-bit `int $0x80` and `__kernel_vsyscall` register preservation, syscall trace-stop metadata, signal interruption, restart blocks, and tracer interactions.

## Important APIs, Types, and Functions

Key pieces are `struct syscall_args32`, `do_full_int80()`, `do_full_vsyscall32()` on i386, `wait_trap()`, `setsigign()`, `test_sys32_regs()`, `test_ptrace_syscall_restart()`, and `test_restart_under_ptrace()`. It uses `PTRACE_TRACEME`, `PTRACE_SYSCALL`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, wait APIs, ignored and handled signals, `getauxval(AT_SYSINFO)`, and raw 32-bit helper assembly from `raw_syscall_helper_32.S`.

## Control Flow and State

The register tests invoke a syscall with controlled register values, then validate that non-return registers are preserved as expected. Restart tests fork tracees, stop them at syscall entry/exit, inject or ignore signals, and inspect the syscall number, return value, and instruction pointer around restartable syscalls. State is held in child process registers, wait status, `nerrs`, and optional `vsyscall32` address.

## Dependencies and Integration Points

The file depends on architecture-specific `struct user_regs_struct` fields, `asm/ptrace-abi.h`, `helpers.h`, 32-bit build support for the full vsyscall path, and the kernel ptrace syscall-stop ABI. It integrates with the x86 kselftest Makefile and raw syscall assembly helper.

## Risks and Test Signals

Risks include clobbered syscall arguments, wrong `orig_ax`, incorrect restart IP, lost signal semantics, and behavior differences between native, compat, and vDSO syscall paths. Test output reports `[FAIL]` when preserved registers, stop reasons, or restart behavior mismatch expected ABI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ptrace_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S

## Purpose

`raw_syscall_helper_32.S` provides 32-bit assembly glue for x86 syscall ABI tests. It lets C tests load all 32-bit syscall registers, call an arbitrary syscall entry function, and capture the resulting registers without compiler ABI interference.

## Important APIs, Types, and Functions

The exported `sys32_helper` accepts a `struct syscall_args32 *` and a function pointer. It saves `%ebp/%ebx/%esi/%edi`, loads `%eax/%ebx/%ecx/%edx/%esi/%edi/%ebp` from the argument block, calls the supplied entry point, writes all registers back into the block, restores callee-saved registers, and returns. `int80_and_ret` is a tiny `int $0x80; ret` entry point.

## Control Flow and State

All state is transient CPU register state plus the caller-owned argument block. The helper carefully pushes `%eax` after the syscall so the return value can be stored without losing the pointer to the argument block. It has no global data or persistence.

## Dependencies and Integration Points

This file is consumed by `ptrace_syscall.c` and similar 32-bit selftests. It depends on i386 calling conventions, the caller's struct layout matching the assembly offsets, and a non-executable stack note.

## Risks and Test Signals

The primary risks are offset drift between C and assembly, failing to preserve callee-saved registers, or corrupting syscall return values while recovering the pointer. Successful downstream tests validate that syscall argument registers round-trip as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c

## Purpose

`sigaltstack.c` tests x86 signal alternate-stack minimum-size behavior. It validates that too-small altstacks are rejected or fail safely, and that the kernel-reported `AT_MINSIGSTKSZ` is usable for signal delivery.

## Important APIs, Types, and Functions

`setup_altstack()` wraps `sigaltstack()`. `sigsegv()` catches expected delivery failures with `longjmp()`. `sigalrm()` confirms successful alternate-stack signal delivery. `test_sigaltstack()` configures a candidate stack, arms handlers, raises or alarms into the stack, and checks whether the result matches expectations. `main()` reads `getauxval(AT_MINSIGSTKSZ)` and exercises enforced and auxv-derived sizes.

## Control Flow and State

The test uses globals `nerrs`, `sigalrm_expected`, `at_minstack_size`, and `jmpbuf`. Each case installs an altstack, triggers a signal, and either observes normal handler execution or a controlled `SIGSEGV`. State is process-local and reset between cases.

## Dependencies and Integration Points

It depends on libc signal APIs, auxv support, x86 signal-frame sizing, and the kselftest environment. It is sensitive to kernel XSAVE feature size because enabled xstate increases required signal-frame space.

## Risks and Test Signals

Risks include accepting altstacks below the architecture-enforced minimum, underreporting `AT_MINSIGSTKSZ`, or corrupting delivery when large xstate is enabled. Passing output shows expected signal delivery on adequate stacks and expected rejection or safe failure for inadequate stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigaltstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c

## Purpose

`sigreturn.c` is a comprehensive x86 signal-return and exit-to-userspace ABI regression test. It exercises `sigreturn(2)`, IRET, SYSRET-adjacent state restoration, segment selectors, stack pointer restoration, espfix behavior, and strict SS restore semantics.

## Important APIs, Types, and Functions

The file defines local copies of ucontext SS flags, LDT/GDT descriptor setup, an `int3` trampoline, selector helpers `GDT3()`, `LDT3()`, `cs_bitness()`, and `is_valid_ss()`. `setup_ldt()` creates 16-bit code/data and not-present segments with `modify_ldt` and probes `set_thread_area`. `sigusr1()` edits the signal context to request specific CS/SS/SP/IP values. `sigtrap()` records resulting registers and restores the original context. `test_valid_sigreturn()`, `test_bad_iret()`, and `test_nonstrict_ss()` implement the core checks.

## Control Flow and State

`main()` records current CS/SS, builds LDT entries, installs an alternate stack and signal handlers, then runs valid and invalid sigreturn cases. Valid cases return through the `int3` trampoline and are validated in the SIGTRAP handler. Invalid cases expect SIGSEGV, SIGBUS, or SIGILL after IRET failure. Global state stores initial, requested, and resulting gregsets, requested selectors, trap metadata, and error counts.

## Dependencies and Integration Points

The test depends on x86 segmentation, `asm/desc_defs.h`, `asm/ldt.h`, glibc ucontext layouts, `helpers.h`, altstack signal delivery, and kernel compatibility support for 16-bit and 32-bit segments. It directly targets historical CVE classes around espfix and malformed sigreturn frames.

## Risks and Test Signals

Risks include lost high stack-pointer bits, incorrect SS restore under `UC_STRICT_RESTORE_SS`, accepting invalid GDT/LDT descriptors, wrong trap reporting, and kernel stack leaks through espfix failures. Passing cases print register validation success or expected exception class; failures are register mismatches, missing signals, or incorrect strict SS handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c

## Purpose

`sigtrap_loop.c` is a small x86 selftest for trap-flag single-step forward progress. It detects regressions where returning from `SIGTRAP` re-enters the same instruction repeatedly and creates an apparent infinite trap loop.

## Important APIs, Types, and Functions

The program defines a local `sethandler()` wrapper, installs a SA_SIGINFO `SIGTRAP` handler, inspects `REG_RIP` or `REG_EIP`, and uses inline assembly to push `0x302` into EFLAGS, execute four single-stepped instructions, then restore `0x202`.

## Control Flow and State

The handler stores the last trap IP and a same-IP repeat counter. If the same IP appears more than ten times in a row, the test exits failure. Otherwise `main()` completes the short single-step sequence and prints success. State is limited to static handler counters and signal context.

## Dependencies and Integration Points

It is part of the x86 selftest suite and depends on kernel signal delivery, correct saved IP/EFLAGS semantics, and architecture ucontext register names. It complements `single_step_syscall.c` and `mov_ss_trap.c` by focusing on trap-loop avoidance in ordinary single-step signal return.

## Risks and Test Signals

The key risk is an infinite SIGTRAP loop caused by wrong resume IP or trap flag handling. Passing behavior reaches normal process termination; failure appears as a hang, excessive trap count, or explicit failure output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c

## Purpose

`single_step_syscall.c` verifies x86 single-step behavior around fast syscall entry and return. It ensures the trap flag does not leak, disappear, or generate traps at the wrong instruction boundary around `syscall` and other entry paths.

## Important APIs, Types, and Functions

The test uses `get_eflags()`/`set_eflags()` from `helpers.h`, a `SIGTRAP` handler that counts traps and records EFLAGS, a generic fault handler using `sigsetjmp`, and inline assembly in `fast_syscall_no_tf()` and `main()` to execute syscalls with controlled flags. `check_result()` validates expected trap counts and flag state.

## Control Flow and State

`main()` installs signal handlers, toggles TF, runs syscall sequences, and validates whether the kernel delivered a single-step trap and restored flags correctly. State is held in `sig_traps`, `sig_eflags`, and jump-buffer recovery for exceptional cases.

## Dependencies and Integration Points

It depends on x86 EFLAGS semantics, syscall instruction behavior, signal frames, and kselftest helper functions. It integrates with broader x86 entry-path selftests.

## Risks and Test Signals

Risks include losing TF across syscall, taking an unexpected SIGTRAP after return, leaking internal flags, or mishandling fault recovery. Successful output shows expected trap counts; failures report wrong flags or signal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c

## Purpose

`srso.c` is a focused x86 selftest for AMD SRSO Safe-RET mitigation behavior using raw performance counters. It samples retired returns and retired mispredicted returns while the process sleeps and tells the operator that the mitigation is working if the two counts are nearly equal.

## Important APIs, Types, and Functions

The program uses `__cpuid(1)` to restrict execution to Zen 1 through Zen 4 CPUID ranges. It configures two `perf_event_attr` objects with `PERF_TYPE_RAW`, raw configs `0xc8` and `0xc9`, `exclude_user=1`, and `exclude_hv=1`, opens them with `perf_event_open`, resets/enables both counters, sleeps for ten seconds, disables them, reads counts, and prints the retired/mispredicted return totals.

## Control Flow and State

The flow is linear: validate CPU family/model, open both perf counters, enable them around a fixed sleep window, then print the two counts. Kernel state is limited to per-process perf events and hardware counter state for the measurement interval.

## Dependencies and Integration Points

It depends on AMD Zen hardware, raw PMU event encodings for retired returns and retired mispredicted returns, `perf_event_open` permissions, and PMU availability. It integrates with CPU mitigation regression testing by providing a coarse runtime signal rather than an automated pass/fail threshold.

## Risks and Test Signals

Risks include unsupported CPUID ranges, unavailable raw PMU events, perf permission restrictions, noisy system activity during the ten-second sleep, and lack of an enforced numeric threshold. The test signal is the printed count pair; Safe-RET is considered healthy when retired and mispredicted return counts are close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c

## Purpose

`syscall_arg_fault.c` tests x86 syscall entry behavior when syscall arguments or return paths are arranged to fault. It verifies signal delivery, IP advancement, and trap behavior around invalid user pointers and consecutive syscall instructions.

## Important APIs, Types, and Functions

The file uses `SIGSEGV`/`SIGBUS`, `SIGTRAP`, and `SIGILL` handlers, `sigsetjmp`, ucontext register edits, raw inline `syscall` or `int $0x80` style assembly, and direct inspection of `REG_AX` and `REG_IP`. `sigsegv_or_sigbus()` recovers from expected memory faults. `sigtrap()` tracks consecutive syscall single-step behavior. `sigill()` handles unsupported instruction paths.

## Control Flow and State

`main()` installs handlers, executes syscall sequences with invalid or boundary arguments, and uses signal handlers to skip or validate the faulting instruction. State includes `n_errs`, `sigtrap_consecutive_syscalls`, and the jump buffer. The test mutates only its own context.

## Dependencies and Integration Points

It depends on architecture-specific ucontext names, x86 syscall ABI, signal delivery from bad user memory access, and kselftest helper conventions. It complements syscall numbering and single-step tests by focusing on fault handling.

## Risks and Test Signals

Risks include wrong signal type, failure to advance or restore IP, losing `rax/eax` error conventions, and incorrect trap behavior between adjacent syscalls. Passing cases recover through handlers and report no accumulated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c

## Purpose

`syscall_nt.c` checks that x86 syscall entry and return handle the EFLAGS Nested Task bit correctly. User mode can set unusual flags, and the kernel must avoid returning with unsafe or architecturally invalid state.

## Important APIs, Types, and Functions

`do_it()` sets extra EFLAGS bits and performs syscalls with inline assembly. `sigtrap()` observes trap delivery and saved context. `main()` runs baseline and NT-modified cases, accumulating `nerrs`.

## Control Flow and State

The test is linear: install a SIGTRAP handler, run syscall sequences with selected extra flags, and verify that no unexpected trap or crash occurs. State is limited to the global error counter and signal context.

## Dependencies and Integration Points

It depends on x86 EFLAGS semantics, syscall instruction behavior, and Linux signal delivery. It is part of the x86 selftest entry-path coverage.

## Risks and Test Signals

Risks include preserving NT inappropriately, causing task-switch faults, or delivering unexpected signals. Passing behavior completes the syscall cases without incrementing `nerrs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c

## Purpose

`syscall_numbering.c` verifies x86-64 syscall-number interpretation, including ignored high 32 bits, x32 syscall-bit handling, out-of-range numbers, and ptrace preservation of `orig_rax`.

## Important APIs, Types, and Functions

`probe_syscall()` issues raw `syscall` with a 64-bit number and saves a duplicate in `%rbx` for tracer comparison. `test_x32()`, `test_syscalls_common()`, `test_syscalls_with_x32()`, and `test_syscalls_without_x32()` encode the expected syscall matrix. `syscall_numbering_tracee()`, `mess_with_syscall()`, and `syscall_numbering_tracer()` run ptrace passes that read, write back, fuzz return values, fuzz high bits, or sign-extend syscall numbers.

## Control Flow and State

`main()` opens `/dev/null`, maps shared memory for counters and tracer state, detects x32 support by calling x32 `getpid`, runs untraced tests, then forks a traced child for repeated ptrace passes. Shared state tracks indentation, total errors, current ptrace pass, and whether the tracee is inside `probe_syscall()`.

## Dependencies and Integration Points

The test depends on x86-64 raw syscall ABI, optional x32 ABI support, `/dev/null`, shared anonymous `mmap`, `PTRACE_SYSCALL`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, and kselftest result conventions.

## Risks and Test Signals

Risks include honoring high syscall-number bits, accepting x32 numbers without the x32 bit, losing `orig_rax` fidelity under ptrace, or mishandling tracer-modified returns. Passing output reports expected `0`, `-ENOSYS`, or ptrace-modified sentinel values for all tested ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_rip.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_rip.c

## Purpose

`sysret_rip.c` tests how x86-64 handles return to canonical and noncanonical instruction pointers through sigreturn and syscall fallthrough paths. It is aimed at correctness and robustness in SYSRET versus IRET selection.

## Important APIs, Types, and Functions

The file declares an assembly `test_syscall_ins()` page, stores `initial_regs`, and uses handlers `sigsegv_for_sigreturn_test()`, `sigusr1()`, and `sigsegv_for_fallthrough()`. `test_sigreturn_to()` edits a signal frame IP. `test_syscall_fallthrough_to()` maps or positions a syscall instruction near tested addresses and recovers with `setjmp`.

## Control Flow and State

`main()` sets signal handlers, tests sigreturn to selected IP values, and tests syscall return/fallthrough to similar values. Global `rip`, `current_test_page_addr`, and saved registers coordinate expected recovery. State is transient and process-local.

## Dependencies and Integration Points

It depends on x86-64 canonical-address rules, signal-frame register editing, executable test pages, syscall return path behavior, and `helpers.h`. It integrates with x86 entry selftests.

## Risks and Test Signals

Risks include using SYSRET for a noncanonical RIP, reporting the wrong fault IP, or failing to recover from expected SIGSEGV. Passing behavior shows faults or traps at expected addresses without kernel instability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_rip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c

## Purpose

`sysret_ss_attrs.c` verifies that x86 SYSRET returns with usable hidden SS descriptor attributes, especially on AMD systems where SYSRET can otherwise leave the cached SS descriptor unusable even when the selector value looks valid.

## Important APIs, Types, and Functions

The test creates a busy-loop pthread in `threadproc()` to encourage repeated kernel exits on the same CPU. On x86-64 it uses `call32_from_64()` from `thunks.S`, a low 32-bit `MAP_32BIT` stack, and a small 32-bit `test_ss` function that pushes and pops through `%ss`-dependent state. `main()` pins to CPU 0 when possible, calls `usleep(2)` in a loop, and then executes the 32-bit validation thunk.

## Control Flow and State

The busy worker never terminates during the test; it only creates scheduler pressure. The main thread loops 1000 times, sleeping through syscall return paths and then validating that a compat-mode stack operation survives. State is minimal: the worker thread, optional 32-bit stack mapping, CPU affinity, and process register/segment state.

## Dependencies and Integration Points

It depends on pthreads, CPU affinity support, syscall return behavior, 64-bit builds linking `thunks.S`, fixed Linux user selectors in the thunk, and compatibility-mode execution. It complements `sigreturn.c` and `sysret_rip.c` by checking hidden segment attributes rather than IP validity.

## Risks and Test Signals

Risks include invalid cached SS attributes after SYSRET, container CPU-affinity restrictions, wrong mixed-bitness thunk setup, and failures that manifest as crashes rather than explicit comparisons. Passing output is `[OK] We survived` after 1000 syscall/sleep and compat-stack validation iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c

## Purpose

`test_FCMOV.c` tests x87 conditional move instructions under different EFLAGS conditions. It ensures the emulator, CPU, signal path, and compiler output preserve expected floating-point behavior.

## Important APIs, Types, and Functions

The `TEST(insn)` macro emits noinline functions for individual `fcmov*` instructions. `main()` sets up signal handling, runs functions with different flag masks, and compares long double results against expected move or no-move outcomes. `sighandler()` catches illegal-instruction or floating exceptions.

## Control Flow and State

The program loops through generated instruction helpers, injecting flag values and validating returned x87 stack results. Global state is limited to test results and signal status; no persistence exists.

## Dependencies and Integration Points

It depends on i387/x87 instruction support, correct assembler mnemonics, signal delivery for unsupported instructions, and kselftest x86 build rules. It integrates with sibling x87 tests for `FCOMI` and `FISTTP`.

## Risks and Test Signals

Risks include wrong condition-code mapping, x87 stack mishandling, or failures on hardware/emulators lacking instruction support. Passing output confirms all conditional moves match expected flag conditions; signal paths may skip unsupported cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c

## Purpose

`test_FCOMI.c` tests x87 floating-point compare instructions that update integer flags, including ordered and unordered variants, pop variants, quiet NaN, and signaling NaN behavior.

## Important APIs, Types, and Functions

The file defines flag-result enums, NaN test data, and helpers `test()`, `test_qnan()`, `testu_qnan()`, `testu_snan()`, `testp()`, `testp_qnan()`, and `testup_qnan()`. Each uses inline x87 assembly to execute `fcomi/fucomi` style instructions and return flag state. `sighandler()` catches floating or illegal instruction signals.

## Control Flow and State

`main()` initializes signal handling, executes compare variants with baseline flags, and validates result globals such as `res_fcomi_pi_1`, `res_fcomi_1_pi`, and NaN cases. State is in global result variables and process signal status.

## Dependencies and Integration Points

It depends on x87 compare instruction availability, assembler support, EFLAGS extraction, and Linux signal behavior for exceptional floating-point cases. It is part of x86 instruction selftest coverage.

## Risks and Test Signals

Risks include incorrect unordered compare flag results, pop/no-pop x87 stack mistakes, mishandling signaling NaNs, and emulator differences. Passing output means all compare-result flags match expected values without unexpected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCOMI.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c

## Purpose

`test_FISTTP.c` tests the SSE3-era x87 `FISTTP` instruction, which stores integer values with truncation independent of the x87 rounding mode. It covers 16-bit, 32-bit, and 64-bit destinations.

## Important APIs, Types, and Functions

Global result buffers `res64`, `res32`, and `res16` receive instruction output. `test()` emits inline x87 assembly for `fisttp` variants and checks truncation results. `sighandler()` handles unsupported instruction signals. `main()` runs the test and reports pass or failure.

## Control Flow and State

The test runs a fixed sequence of floating-point loads and truncating stores, then compares memory results. State is confined to global result variables and the signal handler path.

## Dependencies and Integration Points

It depends on x87/SSE3 instruction support, assembler support for `fisttp`, signal handling for `SIGILL`, and x86 kselftest build configuration.

## Risks and Test Signals

Risks include silent rounding-mode dependence, wrong operand-size stores, or unsupported instruction behavior. Passing output confirms truncation results for all tested integer widths; unsupported systems should exit through the signal path rather than corrupt results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c

## Purpose

`test_mremap_vdso.c` verifies that a process can move the vDSO mapping with `mremap()` when it is not sealed, and that the process continues or exits cleanly afterward. It protects the ABI around the special vDSO mapping.

## Important APIs, Types, and Functions

`try_to_remap()` reserves a destination with `mmap()`, then calls `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` on the vDSO. `vdso_sealed()` parses `/proc/self/smaps` for `[vdso]` and `VmFlags: sl`. `main()` uses `getauxval(AT_SYSINFO_EHDR)`, forks a child, retries with increasing page-sized guesses, and exits via a raw syscall on i386.

## Control Flow and State

The parent plans one kselftest result, skips sealed vDSO cases, then forks. The child locates and moves the vDSO, exiting with the remap result. The parent inspects wait status and reports pass/fail. State is the child's address space only; no persistent mapping changes affect the parent.

## Dependencies and Integration Points

It depends on auxv vDSO discovery, `/proc/self/smaps`, `mmap`, `mremap`, fork/wait, and kselftest result helpers. It integrates with memory-management and x86 vDSO ABI tests.

## Risks and Test Signals

Risks include rejecting legal vDSO moves, moving only part of the vDSO, failing on sealed mappings without a skip, or glibc crashing after the move. Passing output shows the child exits zero after remapping; failure reports child crash or nonzero exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c

## Purpose

`test_shadow_stack.c` tests core x86 userspace CET shadow-stack behavior without relying on libc shadow-stack enablement. It covers `arch_prctl` enable/disable, `map_shadow_stack`, WRSS writes, shadow-stack faults, guard gaps, `mprotect`, GUP, userfaultfd, ptrace NT_X86_SHSTK state, 32-bit signal interaction, and return uprobes.

## Important APIs, Types, and Functions

Important interfaces include `ARCH_PRCTL()` inline syscall, `create_shstk()`, `write_shstk()`, `get_ssp()`, `try_shstk()`, `test_shstk_pivot()`, `test_shstk_faults()`, `test_shstk_violation()`, `test_gup()`, `test_mprotect()`, `test_userfaultfd()`, guard-gap tests, `sigaction32()`, `test_32bit()`, `test_uretprobe()`, and `test_ptrace()`. Kernel APIs exercised include `__NR_map_shadow_stack`, `ARCH_SHSTK_ENABLE/DISABLE/STATUS`, `ARCH_SHSTK_WRSS`, `/proc/self/mem`, `userfaultfd`, `perf_event_open` uprobes, and `PTRACE_GETREGSET/SETREGSET` with `NT_X86_SHSTK`.

## Control Flow and State

`main()` enables shadow stack, disables and reenables it to test control ABI, enables WRSS, then runs each subtest in sequence. Signal handlers fix corrupted shadow-stack entries or convert expected faults into success paths. Global state tracks current shadow-stack pointer, saved SSP value, access mode, file descriptors, and `segv_triggered`. Most subtests allocate and release shadow-stack mappings; the final cleanup disables shadow stack before returning where necessary.

## Dependencies and Integration Points

The file depends on GCC CET instruction support, x86 CET-capable kernel and hardware, raw arch prctl support, `asm/mman.h`, `linux/userfaultfd.h`, `linux/perf_event.h`, ptrace regsets, `/sys/bus/event_source/devices/uprobe`, and 32-bit compat signal behavior. It is a high-value integration test across mm, signal, ptrace, perf uprobes, and x86 arch code.

## Risks and Test Signals

Risks include missing guard pages, writable shadow stacks through ordinary writes, broken WRSS or COW behavior, `mprotect` permission confusion, userfaultfd mishandling, invalid ptrace SSP acceptance, 32-bit signal crashes, and uretprobe return-address corruption. Passing output prints `[OK]` for each subtest; skips occur when shadow stack, WRSS, userfaultfd, or uprobes are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c

## Purpose

`test_syscall_vdso.c` is a 32-bit x86 syscall ABI conformance test. It checks `__kernel_vsyscall` and `int $0x80` argument preservation, flags behavior, ptrace syscall tracing, and absence of leaked 64-bit register contents on 64-bit kernels.

## Important APIs, Types, and Functions

`get_syscall()` finds `AT_SYSINFO`. `int80` is an inline assembly entry. `struct regs64`, `get_regs64`, and `poison_regs64` use mixed-bitness thunks from `thunks_32.S` to check high registers. `prep_args()` builds a 6-argument `pselect` call. `run_syscall()` invokes the selected syscall entry and validates argument registers and R8-R15. `ptrace_me()` forks a parent tracer using `PTRACE_SYSCALL`.

## Control Flow and State

The 32-bit `main()` detects whether it runs on a 64-bit kernel from CS, discovers the vDSO syscall entry, runs the test through vDSO and `int $0x80`, starts a ptraced child, and repeats under tracing. State includes `syscall_addr`, `kernel_is_64bit`, register snapshots, fd sets, timespec, and signal mask descriptors.

## Dependencies and Integration Points

It depends on a 32-bit userspace build, ELF auxv, mixed 32/64 thunks, ptrace, `pselect`, and x86 syscall ABI details. Non-i386 builds skip immediately.

## Risks and Test Signals

Risks include clobbered syscall arguments, leaking kernel data into R8-R15 on compat syscalls, unexpected flag preservation differences, and ptrace altering syscall behavior. Passing output reports preserved arguments and no register leaks for both syscall entry mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c

## Purpose

`test_vsyscall.c` validates legacy vsyscall and vDSO time-related ABI behavior. It compares `gettimeofday`, `time`, and `getcpu` results between syscalls, vDSO symbols, and fixed-address vsyscall functions, then checks vsyscall page permissions and emulation behavior on x86-64.

## Important APIs, Types, and Functions

`init_vdso()` opens `linux-vdso.so.1` or `linux-gate.so.1` and resolves `__vdso_gettimeofday`, `__vdso_clock_gettime`, `__vdso_time`, and `__vdso_getcpu`. `init_vsys()` parses `/proc/self/maps` for `[vsyscall]`. `test_gtod()`, `test_time()`, and `test_getcpu()` compare syscall, vDSO, and vsyscall results. x86-64-only tests include `test_vsys_r()`, `test_vsys_x()`, `test_process_vm_readv()`, and `test_emulation()`.

## Control Flow and State

`main()` declares a kselftest plan, initializes vDSO and vsyscall state, runs time/getcpu checks, then installs signal handlers for vsyscall read/execute probes and single-step emulation detection. Global booleans track read and execute permissions for the vsyscall page, and trap globals track fault class.

## Dependencies and Integration Points

The file depends on dlopen/dlsym, `/proc/self/maps`, `process_vm_readv`, CPU affinity, signal ucontext trap fields, kselftest helpers, and legacy fixed vsyscall addresses. It integrates with x86 vDSO/vsyscall compatibility policy.

## Risks and Test Signals

Risks include vDSO returning inconsistent time, vsyscall map permissions diverging from actual access, debugger read semantics regressing, and native rather than emulated vsyscalls. Passing output records correct timing windows, CPU/node matches, expected permission faults, and emulated vsyscall single-step behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_vsyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S

## Purpose

`thunks.S` provides a 64-bit object helper for calling 32-bit compatibility-mode functions from 64-bit test code. It is used by mixed-bitness x86 selftests that need to exercise compat paths from one process image.

## Important APIs, Types, and Functions

The exported `call32_from_64` takes a stack pointer in `%rdi` and a 32-bit function pointer in `%esi`. It saves callee-saved 64-bit registers and flags, switches to the supplied stack, performs an `lretq` to USER32_CS, calls the function in `.code32`, jumps back to USER64_CS, restores the original stack, flags, and registers, then returns.

## Control Flow and State

The thunk temporarily changes CS and stack state. Caller-provided memory stores the old `%rsp` at the top of the new stack. No global data is used.

## Dependencies and Integration Points

It depends on Linux user segment selectors `0x23` and `0x33`, x86 long-mode compatibility transitions, and callers that provide a valid low 32-bit callable address and stack. It integrates with x86 selftests needing compat transitions.

## Risks and Test Signals

Risks include selector mismatch on unusual environments, invalid stack layout, or failure to preserve callee-saved state. Downstream mixed-bitness tests are the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S

## Purpose

`thunks_32.S` provides the inverse mixed-bitness helper: a 32-bit object can call a 64-bit function while running on a 64-bit kernel. It supports compat syscall tests that inspect or poison 64-bit registers.

## Important APIs, Types, and Functions

The exported `call64_from_32` reads the function pointer from the 32-bit stack, saves registers clobbered by the 64-bit ABI, far-jumps to USER64_CS, calls the function through `%rax`, then returns to USER32_CS using an `lretq` sequence designed to avoid problematic 32-bit relocations.

## Control Flow and State

State is transient in CPU registers and the user stack. The helper does not allocate memory or store globals; it only performs controlled segment transitions and register save/restore.

## Dependencies and Integration Points

It depends on standard Linux x86 user selectors, compatibility-mode execution, and a 64-bit kernel. It is used by `test_syscall_vdso.c` to check whether compat syscalls leak high registers.

## Risks and Test Signals

Risks include wrong relocation handling, incorrect selector constants, or register corruption across the transition. Successful downstream tests observe expected 64-bit register poison and preservation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_32bit_program.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_32bit_program.c

## Purpose

`trivial_32bit_program.c` is a build-environment probe for x86 kselftests. It confirms that the toolchain can compile and run a 32-bit i386 userspace binary.

## Important APIs, Types, and Functions

The file uses `#ifndef __i386__ #error wrong architecture` as the main check. `main()` prints a newline and exits zero.

## Control Flow and State

There is no meaningful runtime state. Failure normally occurs at compile time if the build flags or compiler target are wrong.

## Dependencies and Integration Points

It depends on 32-bit libc and compiler support. The x86 selftest build uses it to decide whether 32-bit-specific tests can be built and run.

## Risks and Test Signals

The risk is false confidence when a compiler accepts `-m32` but runtime libraries are missing. A successful compile and zero exit are the test signal; compile-time architecture error is intentional for wrong targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_32bit_program.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c

## Purpose

`trivial_64bit_program.c` is the 64-bit companion build probe for x86 kselftests. It verifies that the build environment targets x86-64 when expected.

## Important APIs, Types, and Functions

The `__x86_64__` preprocessor check enforces architecture. `main()` prints a newline and returns zero.

## Control Flow and State

The program has trivial runtime flow and no persistent state. Its value is mostly compile-time validation.

## Dependencies and Integration Points

It depends on x86-64 compiler and libc support. It is used by the selftest build to gate 64-bit-specific test binaries.

## Risks and Test Signals

The main risk is misconfigured compiler flags. Compile success and zero exit indicate a usable 64-bit test environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c

## Purpose

`trivial_program.c` is a generic compilation and execution probe. It checks that a selected set of build flags can produce a runnable C program.

## Important APIs, Types, and Functions

`main()` calls `puts("")` and returns zero. There are no custom types or helper APIs.

## Control Flow and State

The flow is a single print and exit. There is no state beyond libc stdout handling.

## Dependencies and Integration Points

It depends on the active compiler, linker, and libc configuration. Selftest Makefiles can use it to validate flag combinations independent of x86 bitness.

## Risks and Test Signals

The only meaningful failure is build or process startup failure. A zero exit is a pass signal for the build environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c

## Purpose

`unwind_vdso.c` tests unwind metadata for the 32-bit vDSO `AT_SYSINFO` syscall entry. It verifies that single-stepping through the fast syscall path still permits correct stack unwinding and argument recovery.

## Important APIs, Types, and Functions

The test uses `getauxval(AT_SYSINFO)`, `dladdr()`, `_Unwind_Backtrace()`, `_Unwind_GetIP()`, `_Unwind_GetGR()`, and a `SIGTRAP` handler. `trace_fn()` walks frames until the expected return address and validates syscall number and argument registers. `sigtrap()` detects entry into AT_SYSINFO and disables TF at the return address.

## Control Flow and State

`main()` discovers AT_SYSINFO, installs SIGTRAP, forces lazy binding with one syscall, sets TF, and calls `syscall(SYS_getpid, 1, 2, 3, 4, 5, 6)`. The handler tracks whether it has reached the vDSO, records the return address from the stack, and runs unwinding on trap events. Globals store `sysinfo`, `return_address`, `got_sysinfo`, and error count.

## Dependencies and Integration Points

It depends on a libc new enough for `getauxval`, the 32-bit vDSO fast syscall path, libgcc unwind support, `helpers.h`, and correct vDSO unwind annotations. It integrates with compat ABI and debugger/unwinder expectations.

## Risks and Test Signals

Risks include missing or wrong unwind info, failed AT_SYSINFO discovery, trap flag not being cleared, and incorrect register recovery. Passing output maps AT_SYSINFO to the vDSO and reports recovered syscall number and arguments as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/unwind_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c

## Purpose

`vdso_restorer.c` tests 32-bit signal handling when user code supplies `sa_restorer == NULL`, requesting a kernel-provided vDSO signal restorer. It preserves an old ABI that modern libc rarely exercises.

## Important APIs, Types, and Functions

The file open-codes `struct real_sigaction` to avoid libc wrapper behavior. It resolves `linux-vdso.so.1` or `linux-gate.so.1` with `dlopen()`. It installs handlers through raw `SYS_rt_sigaction` and `SYS_sigaction` syscalls, then raises `SIGUSR1`. `handler_with_siginfo()` and `handler_without_siginfo()` set `handler_called`.

## Control Flow and State

`main()` skips if the vDSO cannot be found, installs an SA_SIGINFO action with no restorer, raises the signal, validates the handler returned, then repeats for a non-SA_SIGINFO handler. State is just the volatile `handler_called` flag and error count.

## Dependencies and Integration Points

It depends on 32-bit signal ABI, kernel vDSO restorer support, raw signal syscalls, and dynamic linker visibility of the vDSO. It is not relevant for native 64-bit userspace, which does not support this ABI.

## Risks and Test Signals

Risks include kernel rejection of NULL restorer, failure to choose vDSO restorer, or broken return from either handler style. Passing output confirms both handler forms execute and return successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c

## Purpose

`xstate.c` is a generic userspace x86 extended-state regression suite. For selected xfeatures such as AVX, AVX-512, AMX tile data, and APX, it tests context switching, ptrace injection, and signal-frame exposure of XSAVE state.

## Important APIs, Types, and Functions

Key helpers are `xgetbv()`, `load_rand_xstate()`, `load_init_xstate()`, `copy_xstate()`, `validate_xstate_same()`, and `validate_xregs_same()`. Context switching uses `struct futex_info`, pthreads, mutex handoff, CPU affinity, `test_context_switch()`, and randomized `xrstor/xsave`. Ptrace uses `PTRACE_GETREGSET/SETREGSET` and `NT_X86_XSTATE`. Signal testing uses `validate_sigfpstate()` to inspect the signal frame's `_fpx_sw_bytes` and saved xstate contents. `test_xstate()` orchestrates per-feature execution.

## Control Flow and State

For each supported feature, the code gets CPUID xstate metadata, validates the feature mask, forces context switches among threads with random register contents, forks a ptracee for state injection, and raises a signal after stashing expected state. Global `xstate` identifies the current feature, and per-test buffers hold aligned XSAVE images. State is process-local and randomized to avoid initial-state false positives.

## Dependencies and Integration Points

It depends on CPUID leaf 0xd, XCR0 feature enablement, XSAVE/XRSTOR instructions, pthreads, ptrace xstate regsets, signal frame layout, `helpers.h`, and `xstate.h`. It complements feature-specific selftests like PKRU by focusing on generic kernel save/restore ABI.

## Risks and Test Signals

Risks include lost xstate during context switch, ptrace format mismatch, signal-frame feature-bit errors, dynamic xstate allocation bugs, or unsupported feature mishandling. Passing output reports no incorrect context-switch cases and successful ptrace and signal checks for each tested feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h

## Purpose

`xstate.h` provides shared data structures and inline helpers for x86 extended-state selftests. It abstracts XSAVE buffer layout, feature metadata, CPUID discovery, and low-level XSAVE/XRSTOR operations.

## Important APIs, Types, and Functions

The header defines `enum xfeature`, `xfeature_names`, `struct xsave_buffer`, `struct xstate_info`, `xsave()`, `xrstor()`, `get_xbuf_size()`, `get_xstate_info()`, `alloc_xbuf()`, `clear_xstate_header()`, `set_xstatebv()`, `get_fpx_sw_bytes()`, `get_fpx_sw_bytes_features()`, `set_rand_data()`, and the exported `test_xstate()` declaration.

## Control Flow and State

There is no standalone control flow. Inline helpers use CPUID leaf 0xd to compute XSAVE area size and per-feature offsets, allocate 64-byte aligned buffers, manipulate the XSAVE header, and fill feature data with nonzero randomized words. State lives in caller-owned buffers.

## Dependencies and Integration Points

It depends on `<stdint.h>`, kselftest helpers, compiler support for inline x86 assembly, CPUID, XSAVE/XRSTOR, and signal-frame `_fpx_sw_bytes` layout. `xstate.c` is the main consumer.

## Risks and Test Signals

Risks include feature-number drift with kernel definitions, wrong XSAVE offsets, insufficient alignment, and random data accidentally representing init state. Successful `xstate.c` runs validate that these helpers match kernel ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile

## Purpose

The zram selftest `Makefile` registers the zram shell test entrypoint and support files with kselftest.

## Important APIs, Types, and Functions

It defines an empty `all` target, `TEST_PROGS := zram.sh`, `TEST_FILES := zram01.sh zram02.sh zram_lib.sh`, `EXTRA_CLEAN := err.log`, and includes `../lib.mk`.

## Control Flow and State

There is no runtime flow in the Makefile. Kselftest uses the variables to install or run `zram.sh` and copy helper scripts. `err.log` is declared as cleanup state produced by the shell tests.

## Dependencies and Integration Points

It depends on the kselftest `lib.mk` contract and the adjacent shell scripts. It integrates with `make kselftest` and packaging/install of selftests.

## Risks and Test Signals

Risks include omitting helper scripts from `TEST_FILES` or failing to clean `err.log`. A successful signal is that `zram.sh` is discoverable and both helper tests run under the kselftest harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config

## Purpose

The zram selftest `config` declares kernel configuration requirements for running the zram tests.

## Important APIs, Types, and Functions

The file sets `CONFIG_ZSMALLOC=y` and `CONFIG_ZRAM=m`, indicating the allocator must be built in and zram should be available as a module for the older module-loading path.

## Control Flow and State

There is no executable flow. The file is consumed by kselftest configuration tooling.

## Dependencies and Integration Points

It integrates with kernel selftest config fragment handling and the zram shell tests, which call `modprobe zram` and manipulate `/sys/block/zram*`.

## Risks and Test Signals

Risks include mismatches with kernels that build zram in or provide only zram-control hotplug. The shell library handles some variants, but this fragment documents the expected testable configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh

## Purpose

`zram.sh` is the top-level zram selftest runner. It performs prerequisite checks and runs filesystem and swap zram scenarios.

## Important APIs, Types, and Functions

It sources `zram_lib.sh`, defines `TCID="zram.sh"`, and implements `run_zram()` to execute `./zram01.sh` and `./zram02.sh` with separators.

## Control Flow and State

The script calls `check_prereqs` first, then runs both child tests. It does not aggregate child exit codes explicitly, so visible pass/fail messages come from the child scripts and their cleanup behavior.

## Dependencies and Integration Points

It depends on root privileges, the current working directory containing the zram scripts, and kselftest invoking it from the installed selftest directory. It integrates with the Makefile via `TEST_PROGS`.

## Risks and Test Signals

Risks include child failures not being propagated as a final exit status and dependence on relative paths. Test signals are the printed `zram01` and `zram02` pass/fail lines plus kselftest process status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh

## Purpose

`zram01.sh` creates a zram block device, formats it, mounts it, fills it with zero data, and checks that compression produces a ratio above 1:1.

## Important APIs, Types, and Functions

The script sources `zram_lib.sh`, sets `dev_num=1`, `zram_max_streams=2`, `zram_sizes=2097152`, `zram_mem_limits=2M`, `zram_filesystems=ext4`, and `zram_algs=lzo`. Its local `zram_fill_fs()` appends zero-filled 1 KiB blocks with `dd`, reads `/sys/block/zram$i/mm_stat`, computes a compression ratio with shell arithmetic and `bc`, and sets `ERR_CODE` on failure.

## Control Flow and State

The flow is prerequisites, load/create device, set streams, set compression algorithm, set disk size, set memory limit, make filesystem, mount, fill, cleanup, and print `[PASS]` or `[FAIL]`. Shared state from `zram_lib.sh` tracks device range, mounted devices, swap devices, and module/control mode.

## Dependencies and Integration Points

It depends on root privileges, `modprobe`, zram sysfs, `mkfs.ext4` or fallback behavior in the library, `mount`, `dd`, `awk`, `bc`, and writable working directory for mount points and `err.log`.

## Risks and Test Signals

Risks include missing `lzo`, missing filesystem tools, low device size, `mm_stat` format drift, and cleanup failures leaving mounted devices. Passing output includes a compression ratio and `zram01 : [PASS]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh

## Purpose

`zram02.sh` tests zram as swap. It creates a small zram device, configures memory limits, runs `mkswap`, enables swap, disables swap, and cleans up.

## Important APIs, Types, and Functions

The script sources `zram_lib.sh`, sets `dev_num=1`, `zram_max_streams=2`, `zram_sizes=1048576`, and `zram_mem_limits=1M`, then calls library helpers `check_prereqs`, `zram_load`, `zram_max_streams`, `zram_set_disksizes`, `zram_set_memlimit`, `zram_makeswap`, `zram_swapoff`, and `zram_cleanup`.

## Control Flow and State

Flow is linear and cleanup is explicit at the end. State is inherited from `zram_lib.sh`, especially `dev_makeswap`, `dev_start`, `dev_end`, module-load mode, and sysfs-control mode.

## Dependencies and Integration Points

It depends on root privileges, zram sysfs, `mkswap`, `swapon`, `swapoff`, and module or zram-control device creation. It is invoked by `zram.sh` and registered as a support file by the Makefile.

## Risks and Test Signals

Risks include active swap preventing cleanup, missing swap utilities, small memory limits causing setup failures, and failure not reflected in `ERR_CODE` for some library echo-only failures. Passing output ends with `zram02 : [PASS]` after swapoff and cleanup messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh

## Purpose

`zram_lib.sh` is the shared shell library for zram selftests. It handles root checks, zram device creation across old and new kernels, sysfs configuration, filesystem and swap setup, and cleanup.

## Important APIs, Types, and Functions

Global state includes `dev_makeswap`, `dev_mounted`, `dev_start`, `dev_end`, `module_load`, `sys_control`, `ksft_skip`, and parsed kernel version components. Functions are `check_prereqs()`, `kernel_gte()`, `zram_cleanup()`, `zram_load()`, `zram_max_streams()`, `zram_compress_alg()`, `zram_set_disksizes()`, `zram_set_memlimit()`, `zram_makeswap()`, `zram_swapoff()`, `zram_makefs()`, and `zram_mount()`.

## Control Flow and State

Test scripts set per-device arrays as whitespace-separated strings, call `zram_load()` to determine existing device count and create devices either with `/sys/class/zram-control/hot_add` or `modprobe zram num_devices=`, then call configuration helpers. `zram_cleanup()` reverses state by swapoff, umount, sysfs reset, directory removal, hot_remove, and optional `rmmod`.

## Dependencies and Integration Points

The library depends on root privileges, `/sys/class/zram-control`, `/sys/block/zram*/`, `/proc/modules`, `modprobe`, `rmmod`, `mkswap`, `swapon`, `swapoff`, `mkfs.*`, `mount`, `umount`, `seq`, and shell arithmetic. It encodes kselftest skip code 4.

## Risks and Test Signals

Risks include races with pre-existing zram devices, partial cleanup when commands fail, old-kernel `max_comp_streams` behavior, missing compression algorithms, and echo-only failure reporting. Passing signals are successful sysfs writes, mounted or swap-enabled devices, and cleanup messages without leaked devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/autoconf.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/autoconf.h

## Purpose

`autoconf.h` is a generated-header seed for userspace testing of kernel data structures. It supplies minimal configuration needed by xarray and related tests.

## Important APIs, Types, and Functions

The file includes `bit-length.h` and defines `CONFIG_XARRAY_MULTI 1`.

## Control Flow and State

There is no runtime control flow. `shared.mk` copies this file into `generated/autoconf.h`, where other headers include it during userspace test builds.

## Dependencies and Integration Points

It depends on `generated/bit-length.h` creation by `shared.mk` and integrates with xarray, radix-tree, idr, and maple-tree userspace builds.

## Risks and Test Signals

Risks include stale config macros relative to kernel code expectations. A successful build of shared userspace tests is the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/autoconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c

## Purpose

`interval_tree-shim.c` pulls the kernel interval tree implementation into userspace tests as a standalone compilation unit.

## Important APIs, Types, and Functions

It simply includes `../../../lib/interval_tree.c`, exposing the interval tree implementation through the userspace shim include path.

## Control Flow and State

All control flow and state come from the included kernel source. The shim itself has no logic.

## Dependencies and Integration Points

It depends on shared userspace kernel-compat headers under `tools/testing/shared/linux` and the kernel `lib/interval_tree.c` source. It integrates with rbtree and interval-tree tests.

## Risks and Test Signals

Risks include include-path drift or missing compatibility stubs. Successful userspace interval-tree builds and tests validate the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux.c

## Purpose

`linux.c` implements userspace stand-ins for selected Linux memory-allocation and slab-cache APIs used by radix tree, xarray, maple tree, and related tests.

## Important APIs, Types, and Functions

It defines globals `nr_allocated`, `preempt_count`, and `test_verbose`. Key APIs include `kmem_cache_set_callback()`, `kmem_cache_set_private()`, `kmem_cache_set_non_kernel()`, allocation counters, `kmem_cache_alloc_lru()`, `kmem_cache_free()`, `kmem_cache_alloc_bulk()`, `kmem_cache_free_bulk()`, `__kmem_cache_create_args()`, sheaf helpers `kmem_cache_prefill_sheaf()`, `kmem_cache_refill_sheaf()`, `kmem_cache_return_sheaf()`, `kmem_cache_alloc_from_sheaf()`, and `test_kmem_cache_bulk()`.

## Control Flow and State

Allocations use a mutex-protected freelist stored through `struct radix_tree_node::parent` for small unaligned caches, or `malloc`/`posix_memalign` for fresh and aligned objects. Counters are updated with `uatomic`. Nonblocking allocation behavior is simulated through `non_kernel` and optional callbacks. Bulk operations reuse cached objects when possible and unwind partial failure.

## Dependencies and Integration Points

The file depends on pthreads, malloc, Userspace RCU atomic operations, kernel slab/radix-tree headers, and shared compatibility headers. It is linked by `shared.mk` into xarray, radix-tree, maple-tree, idr, and VMA test binaries.

## Risks and Test Signals

Risks include diverging from kernel slab semantics, freelist corruption through reused object fields, missing constructor or zeroing behavior, and counter mismatches. `test_kmem_cache_bulk()` asserts expected freelist reuse and aligned-cache behavior; sanitizers from `shared.mk` provide additional signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h

## Purpose

`linux/bug.h` is a userspace include shim for kernel BUG/WARN support.

## Important APIs, Types, and Functions

It includes `<stdio.h>` and `"asm/bug.h"`, relying on the test include path to provide architecture-specific warning and bug macros.

## Control Flow and State

There is no runtime code in this wrapper.

## Dependencies and Integration Points

It depends on the shared testing include hierarchy and architecture shim headers. It is pulled in by `shared.h` and many kernel data-structure sources compiled in userspace.

## Risks and Test Signals

Risks are missing or incompatible `asm/bug.h` definitions. Successful compilation of shared tests validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h

## Purpose

`linux/cleanup.h` forwards userspace test builds to the kernel cleanup helper definitions.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/cleanup.h`.

## Control Flow and State

The wrapper contains no runtime logic.

## Dependencies and Integration Points

It depends on the kernel include tree being reachable from tools/testing/shared. It integrates with any imported kernel code that uses cleanup annotations or helpers.

## Risks and Test Signals

Risks include relative include path drift or compiler incompatibility with cleanup attributes. Successful userspace builds are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h

## Purpose

`linux/cpu.h` stubs CPU hotplug registration for userspace tests.

## Important APIs, Types, and Functions

It defines `cpuhp_setup_state_nocalls(a, b, c, d)` to return `0`.

## Control Flow and State

There is no real CPU hotplug state. Callers see successful registration without side effects.

## Dependencies and Integration Points

It is used when imported kernel data-structure code references CPU hotplug APIs that are irrelevant in userspace.

## Risks and Test Signals

The risk is hiding bugs that depend on hotplug callback execution. For data-structure unit tests, successful build and absence of hotplug-dependent behavior are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h

## Purpose

`linux/idr.h` adapts the kernel IDR header for userspace shared tests.

## Important APIs, Types, and Functions

It undefines `__CONCAT` if present to avoid collisions with system headers, then includes `../../../../include/linux/idr.h`.

## Control Flow and State

The wrapper has no runtime logic. IDR behavior comes from imported kernel code and linked generated objects.

## Dependencies and Integration Points

It depends on kernel IDR headers and the shared Makefile's generated `idr.c` from `lib/idr.c`. It integrates IDR with radix-tree and xarray test support.

## Risks and Test Signals

Risks include macro conflicts with libc/system headers and kernel include drift. Successful IDR userspace builds and tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h

## Purpose

`linux/interval_tree.h` forwards interval-tree userspace builds to the kernel interval-tree header.

## Important APIs, Types, and Functions

It wraps inclusion of `../../../../include/linux/interval_tree.h` with a local guard `_TEST_INTERVAL_TREE_H`.

## Control Flow and State

No runtime behavior exists in this shim.

## Dependencies and Integration Points

It depends on kernel interval-tree and rbtree headers plus userspace compatibility headers. `interval_tree-shim.c` provides the implementation.

## Risks and Test Signals

Risks include missing kernel dependencies or guard conflicts. Successful interval-tree test builds validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h

## Purpose

`linux/interval_tree_generic.h` forwards generic interval-tree macro definitions into userspace tests.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/interval_tree_generic.h`.

## Control Flow and State

There is no independent logic; generated interval tree operations come from the included kernel macros.

## Dependencies and Integration Points

It depends on the kernel include tree and the rbtree compatibility environment. It is included indirectly by interval-tree userspace tests.

## Risks and Test Signals

Risks are include path drift and macro incompatibilities with userspace compilation. Successful interval-tree builds are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h

## Purpose

`linux/kconfig.h` forwards Kconfig helper macros for userspace test builds.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/kconfig.h`.

## Control Flow and State

There is no runtime behavior.

## Dependencies and Integration Points

It lets imported kernel headers use `IS_ENABLED()` and related Kconfig macros in userspace.

## Risks and Test Signals

Risks include relative include path drift or missing generated config macros. Successful shared-test compilation validates the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h

## Purpose

`linux/kernel.h` supplies a userspace-compatible wrapper around core kernel helper macros for shared data-structure tests.

## Important APIs, Types, and Functions

It includes the tools kernel header, libc string/stdio/limits headers, compiler, error, bitops, log2, and kconfig headers. It maps `printk`, `pr_err`, `pr_info`, `pr_debug`, and `pr_cont` to `printf`, defines `schedule()` as a no-op, sets `PAGE_SHIFT` to 12, and stubs `EXPORT_PER_CPU_SYMBOL_GPL`.

## Control Flow and State

No runtime state exists beyond print macro expansion. Scheduling and export behavior are intentionally inert in userspace.

## Dependencies and Integration Points

It is a central dependency for imported kernel libraries compiled by `shared.mk`. It bridges kernel logging and helper expectations to libc.

## Risks and Test Signals

Risks include hiding scheduling assumptions, mismatched page size assumptions, or print macro side effects. Sanitized test builds and data-structure tests validate practical compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kmemleak.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/kmemleak.h

## Purpose

`linux/kmemleak.h` stubs kmemleak integration for userspace tests.

## Important APIs, Types, and Functions

It defines `kmemleak_update_trace(const void *ptr)` as an empty inline function.

## Control Flow and State

There is no leak-tracking state. Calls compile away.

## Dependencies and Integration Points

It supports imported kernel code that conditionally updates kmemleak metadata while running in userspace test binaries.

## Risks and Test Signals

The risk is that tests do not exercise kmemleak-specific behavior. This is acceptable for data-structure correctness tests; successful compilation is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kmemleak.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h

## Purpose

`linux/local_lock.h` provides no-op local-lock primitives for userspace tests.

## Important APIs, Types, and Functions

It defines an empty `local_lock_t`, inline `local_lock()` and `local_unlock()`, and `INIT_LOCAL_LOCK(x)`.

## Control Flow and State

No lock state is maintained. Calls have no synchronization effect.

## Dependencies and Integration Points

It supports imported kernel code that expects local locks in contexts where userspace tests either serialize differently or do not need CPU-local locking.

## Risks and Test Signals

Risks include masking concurrency bugs that require local-lock semantics. Threaded tests should use real pthread primitives where needed; successful builds validate this stub for single-process harness use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h

## Purpose

`linux/lockdep.h` stubs lock dependency APIs for userspace tests.

## Important APIs, Types, and Functions

It includes `<linux/spinlock.h>`, defines `struct lock_class_key`, provides no-op `lockdep_set_class()`, and declares `lockdep_is_held()`.

## Control Flow and State

No lock class graph or dependency state is tracked. Callers can compile code that annotates locks without invoking kernel lockdep.

## Dependencies and Integration Points

It is used by shared data-structure code that includes lockdep annotations. The actual `lockdep_is_held()` definition must be supplied elsewhere if referenced.

## Risks and Test Signals

Risks include missing deadlock checking and unresolved references if imported code uses `lockdep_is_held()` without a stub. Successful linkage is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h

## Purpose

`linux/maple_tree.h` adapts the kernel maple-tree header for userspace testing.

## Important APIs, Types, and Functions

It includes `<linux/atomic.h>`, defines `U8_MAX` as `UCHAR_MAX`, and includes `../../../../include/linux/maple_tree.h`.

## Control Flow and State

There is no wrapper flow. Maple-tree behavior comes from the included kernel header and `maple-shim.c`.

## Dependencies and Integration Points

It depends on userspace atomic compatibility, limits definitions, and the kernel maple-tree include. It integrates with `maple-shared.h`, `maple-shim.c`, and VMA tests using maple trees for VMA indexing.

## Risks and Test Signals

Risks include missing constants expected by kernel code and header drift. Successful maple-tree and VMA test builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h

## Purpose

`linux/percpu.h` maps kernel per-CPU APIs onto single-process userspace variables for tests.

## Important APIs, Types, and Functions

It defines `DECLARE_PER_CPU`, `DEFINE_PER_CPU`, `__get_cpu_var`, `this_cpu_ptr`, `this_cpu_read`, `this_cpu_xchg`, `this_cpu_cmpxchg`, `per_cpu_ptr`, and `per_cpu`. Atomic exchange and compare-exchange use `uatomic_xchg` and `uatomic_cmpxchg`.

## Control Flow and State

All per-CPU variables collapse to one ordinary variable instance; the CPU argument is ignored in `per_cpu_ptr()`.

## Dependencies and Integration Points

It depends on Userspace RCU atomics and is consumed by imported kernel data-structure code that has per-CPU counters or caches.

## Risks and Test Signals

Risks include hiding real per-CPU concurrency and CPU-indexing bugs. For unit tests focused on algorithms, successful compilation and deterministic single-instance behavior are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h

## Purpose

`linux/preempt.h` provides minimal preemption accounting for userspace tests.

## Important APIs, Types, and Functions

It declares `extern int preempt_count`, maps `preempt_disable()` and `preempt_enable()` to atomic increment/decrement of that count, and defines `in_interrupt()` to return false.

## Control Flow and State

Only `preempt_count` changes. There is no scheduler or interrupt context emulation.

## Dependencies and Integration Points

It depends on Userspace RCU atomics and `linux.c` defining `preempt_count`. Imported kernel code can assert or inspect preemption-like state.

## Risks and Test Signals

Risks include masking bugs that depend on real preemption or interrupt context. Counter balance can still be observed by tests; successful shared-test execution validates the stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h

## Purpose

`linux/radix-tree.h` adapts the kernel radix-tree header for userspace tests and instruments RCU-delayed frees.

## Important APIs, Types, and Functions

It includes the kernel radix-tree header, declares `kmalloc_verbose` and `test_verbose`, defines `trace_call_rcu()` to optionally print delayed frees before calling `call_rcu`, defines `printv()`, and remaps `call_rcu(x, y)` to `trace_call_rcu(x, y)`.

## Control Flow and State

Wrapper flow is limited to RCU callback tracing and verbosity-controlled printing. Actual radix-tree behavior comes from generated `radix-tree.c` and shared allocation stubs.

## Dependencies and Integration Points

It depends on Userspace RCU, kernel radix-tree headers, `linux.c` slab stubs, and `shared.mk` generation of `radix-tree.c`.

## Risks and Test Signals

Risks include callback macro recursion, verbosity side effects, or divergence from kernel RCU timing. Passing radix-tree/xarray tests and optional verbose output validate the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h

## Purpose

`linux/rbtree.h` forwards userspace test builds to the kernel rbtree header.

## Important APIs, Types, and Functions

It includes `<linux/kernel.h>` and `../../../../include/linux/rbtree.h` under a local guard.

## Control Flow and State

There is no wrapper logic. Rbtree operations are supplied by kernel headers and `rbtree-shim.c`.

## Dependencies and Integration Points

It depends on the shared `linux/kernel.h` wrapper and kernel rbtree include. It integrates with rbtree, interval tree, and VMA tests.

## Risks and Test Signals

Risks are include drift or missing helper macros. Successful rbtree userspace builds and tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h

## Purpose

`linux/rbtree_augmented.h` forwards augmented rbtree helpers to userspace tests.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/rbtree_augmented.h` under a local guard.

## Control Flow and State

There is no runtime code in the wrapper. Augmented callbacks and rotations come from the kernel header.

## Dependencies and Integration Points

It depends on rbtree types and kernel include compatibility. Interval-tree tests rely on augmented rbtree support.

## Risks and Test Signals

Risks include macro incompatibility or missing callback definitions in consumers. Successful interval-tree and rbtree tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h

## Purpose

`linux/rbtree_types.h` exposes kernel rbtree type definitions to userspace test builds.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/rbtree_types.h` with a local guard.

## Control Flow and State

The wrapper has no logic or state.

## Dependencies and Integration Points

It is a dependency for rbtree and interval-tree headers used by shared tests and VMA harness code.

## Risks and Test Signals

The risk is type definition drift or include path failure. Successful shared builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h

## Purpose

`linux/rcupdate.h` maps kernel RCU pointer APIs onto Userspace RCU for shared tests.

## Important APIs, Types, and Functions

It includes `<urcu.h>` and defines `rcu_dereference_raw()`, `rcu_dereference_protected()`, `rcu_dereference_check()`, and `RCU_INIT_POINTER()`.

## Control Flow and State

Pointer dereference helpers collapse to Userspace RCU dereference or plain assignment. RCU callback scheduling is provided elsewhere by liburcu and wrappers such as `radix-tree.h`.

## Dependencies and Integration Points

It depends on liburcu development headers and is used by imported kernel data structures that rely on RCU pointer annotations.

## Risks and Test Signals

Risks include weaker checking than kernel RCU debug modes and simplified protected/check variants. Successful concurrent userspace data-structure tests are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h

## Purpose

`linux/xarray.h` adapts the kernel xarray header for userspace tests.

## Important APIs, Types, and Functions

It includes generated `map-shift.h` to set `XA_CHUNK_SHIFT`, then includes `../../../../include/linux/xarray.h`.

## Control Flow and State

No wrapper runtime logic exists. Xarray behavior comes from the kernel header and `xarray-shared.c`.

## Dependencies and Integration Points

It depends on `shared.mk` generating `generated/map-shift.h` and on kernel xarray includes. It integrates with xarray, radix-tree, and idr userspace tests.

## Risks and Test Signals

Risks include stale chunk-shift generation or include path drift. Successful xarray tests across different `SHIFT` settings validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h

## Purpose

`maple-shared.h` sets up shared userspace configuration for maple-tree tests.

## Important APIs, Types, and Functions

It defines `CONFIG_DEBUG_MAPLE_TREE`, `CONFIG_MAPLE_SEARCH`, and `MAPLE_32BIT`, includes `shared.h`, stdlib/time, and `linux/init.h`, declares `maple_rcu_cb()`, remaps `rcu_cb`, and defines `kfree_rcu()` in terms of `call_rcu()` and the maple callback.

## Control Flow and State

The header controls compile-time feature flags and RCU callback routing. Actual free behavior is implemented in `maple-shim.c`.

## Dependencies and Integration Points

It depends on shared kernel-compat headers, maple-tree slot macros, and Userspace RCU. It is included before importing `lib/maple_tree.c`.

## Risks and Test Signals

Risks include configuration drift from kernel maple-tree expectations and incorrect callback container types. Successful maple-tree and VMA tests validate the setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c

## Purpose

`maple-shim.c` imports the kernel maple-tree implementation into userspace and supplies the maple RCU free callback.

## Important APIs, Types, and Functions

It includes `maple-shared.h`, `<linux/slab.h>`, and `../../../lib/maple_tree.c`. `maple_rcu_cb()` converts an `rcu_head` to `struct maple_node` and frees it through `kmem_cache_free(maple_node_cache, node)`.

## Control Flow and State

All maple-tree algorithms come from the included kernel C file. The shim's callback handles delayed node freeing after RCU grace periods. State includes the kernel maple node cache managed by the shared slab stubs.

## Dependencies and Integration Points

It depends on `linux.c` slab emulation, Userspace RCU, and kernel maple-tree source. VMA tests use maple trees as the VMA index.

## Risks and Test Signals

Risks include mismatched `rcu_head` member name, freeing nodes through the wrong cache, or kernel source requiring additional stubs. Maple-tree selftests and sanitizer-enabled VMA tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c

## Purpose

`rbtree-shim.c` imports the kernel rbtree implementation as a userspace compilation unit.

## Important APIs, Types, and Functions

It includes `../../../lib/rbtree.c`; no additional functions are defined in the shim.

## Control Flow and State

Runtime behavior is entirely from the included kernel source. The shim has no local state.

## Dependencies and Integration Points

It depends on shared rbtree headers and compatibility macros. It supports rbtree, interval-tree, and VMA tests.

## Risks and Test Signals

Risks are include path drift and missing kernel helper stubs. Successful rbtree-dependent test builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/shared.h

## Purpose

`shared.h` is the central userspace compatibility header for imported kernel data-structure tests.

## Important APIs, Types, and Functions

It includes kernel-compatible types, bug, kernel, bitops, GFP, and RCU headers. It stubs module metadata macros `module_init`, `module_exit`, `MODULE_AUTHOR`, `MODULE_LICENSE`, and `MODULE_DESCRIPTION`. It maps missing `dump_stack()` to `assert(0)`.

## Control Flow and State

No runtime flow exists except the `dump_stack()` assertion fallback when invoked.

## Dependencies and Integration Points

It is included by xarray and maple shared headers and indirectly by many imported kernel sources. It provides the minimal module-like environment required to compile kernel code in userspace.

## Risks and Test Signals

Risks include macro collisions with imported headers and over-aggressive stubbing of module behavior. Successful shared test compilation is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk -->
# sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk

## Purpose

`shared.mk` is the common build fragment for userspace tests that import kernel data-structure code.

## Important APIs, Types, and Functions

It sets include paths into `../shared`, tools headers, arch headers, and kernel `lib`; enables debug and sanitizer flags; links pthread and liburcu; defines shared object lists; generates `radix-tree.c` and `idr.c` by stripping static/inline qualifiers; and creates generated headers `autoconf.h`, `map-shift.h`, and `bit-length.h`. It supports `SHIFT`, `BUILD=32`, and `LONG_BIT` overrides.

## Control Flow and State

Make rules generate compatibility files when inputs or parameters change. Generated state lives under `generated/`. Object dependencies force rebuilds when shared headers or imported kernel sources change.

## Dependencies and Integration Points

It depends on `Makefile.arch`, GCC/Clang-compatible sanitizer flags, pthreads, liburcu, kernel source paths, and standard shell utilities. It is included by tests such as `tools/testing/vma/Makefile`.

## Risks and Test Signals

Risks include sed transformations changing kernel semantics, stale generated headers when `SHIFT` or bitness changes, missing sanitizer libraries, and include path drift. A successful sanitized build of xarray/maple/radix/VMA tests is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h

## Purpose

`trace/events/maple_tree.h` stubs maple-tree tracepoints for userspace builds.

## Important APIs, Types, and Functions

It defines `trace_ma_op(a, b)`, `trace_ma_read(a, b)`, and `trace_ma_write(a, b, c, d)` as empty `do { } while (0)` macros.

## Control Flow and State

Trace calls compile to no-ops and record no state.

## Dependencies and Integration Points

It is included by imported maple-tree code through the shared test include path. It avoids pulling in kernel tracing infrastructure.

## Risks and Test Signals

The risk is losing trace visibility in userspace tests. Functional maple-tree tests should still pass; trace behavior is not validated here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/trace/events/maple_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c

## Purpose

`xarray-shared.c` imports the kernel xarray implementation into userspace tests.

## Important APIs, Types, and Functions

It includes `xarray-shared.h` and then `../../../lib/xarray.c`.

## Control Flow and State

All xarray logic and state come from the included kernel source. The wrapper only ensures `XA_DEBUG` and shared compatibility headers are active before inclusion.

## Dependencies and Integration Points

It depends on shared allocation, RCU, radix-tree, and generated map-shift headers from `shared.mk`. It is linked into shared object lists for xarray and related tests.

## Risks and Test Signals

Risks include missing stubs for kernel helpers used by xarray and generated shift mismatches. Successful xarray tests validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h

## Purpose

`xarray-shared.h` configures xarray userspace tests.

## Important APIs, Types, and Functions

It defines `XA_DEBUG` and includes `shared.h`.

## Control Flow and State

The header has no runtime flow. Its compile-time state enables xarray debug checks.

## Dependencies and Integration Points

It is included by `xarray-shared.c` before importing `lib/xarray.c`. It depends on the shared compatibility header set.

## Risks and Test Signals

Risks include debug-mode behavior diverging from production or missing compatibility macros. Successful xarray test execution validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/vma/Makefile

## Purpose

The VMA `Makefile` builds the userspace VMA test binary that imports kernel VMA code and runs it against compatibility stubs.

## Important APIs, Types, and Functions

It includes `../shared/shared.mk`, sets `OFILES = $(SHARED_OFILES) main.o shared.o maple-shim.o`, builds target `vma`, and adds `-DNUM_VMA_FLAG_BITS=128 -DNUM_MM_FLAG_BITS=128`. The `main.o` dependency list includes local tests and kernel `mm/vma*.c` sources. `clean` removes targets, objects, generated shared files, and generated config headers.

## Control Flow and State

Make builds shared infrastructure first, then local and imported VMA objects, then links with sanitizer, pthread, and liburcu flags from `shared.mk`. Generated headers and transformed sources are build-state artifacts.

## Dependencies and Integration Points

It depends on shared userspace testing infrastructure, maple-tree shim, kernel mm sources, local VMA tests, and sanitizer-capable toolchains. It integrates kernel VMA logic with the standalone tools/testing/vma harness.

## Risks and Test Signals

Risks include stale object dependencies when kernel mm headers change, mismatched flag-bit counts, missing sanitizer runtimes, and kernel source drift requiring new stubs. A successful `make` and passing `./vma` run validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h

## Purpose

`custom.h` contains VMA test harness definitions that intentionally customize kernel behavior for userspace testing.

## Important APIs, Types, and Functions

It declares or defines `mmap_min_addr`, `dac_mmap_min_addr`, `TASK_SIZE`, and `pr_warn_once`. It defines a test `struct anon_vma` with `was_cloned` and `was_unlinked` flags. Inline helpers include `unlink_anon_vmas()`, `vma_start_write()`, `vma_start_write_killable()`, `anon_vma_clone()`, `__anon_vma_prepare()`, `anon_vma_prepare()`, `vma_lock_init()`, and `vma_kernel_pagesize()`.

## Control Flow and State

The helpers deliberately mutate test-visible fields rather than performing full kernel anon-vma locking and RMAP behavior. `vma_start_write*()` increments `vm_lock_seq` so tests can observe write locking. `anon_vma_prepare()` allocates a small anon-vma object with `calloc`.

## Dependencies and Integration Points

It depends on VMA harness definitions from `dup.h` and stubs, libc allocation, and kernel VMA code expecting anon-vma APIs. It integrates with tests that assert clone/unlink/write-lock side effects.

## Risks and Test Signals

Risks include over-simplifying anon-vma semantics, memory leaks in test-only allocations, and `TASK_SIZE` assumptions fixed to a 47-bit user address space. VMA unit tests checking cloned/unlinked markers and lock sequence changes validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h

## Purpose

`dup.h` duplicates a large subset of kernel mm/VMA declarations for userspace VMA testing. It provides the types, flags, and inline helpers needed to compile imported `mm/vma*.c` code outside the kernel.

## Important APIs, Types, and Functions

It defines partial kernel types such as `mm_struct`, `address_space`, `file_operations`, `file`, `anon_vma_chain`, `task_struct`, `kref`, and `anon_vma_name`. It duplicates VMA flag bit definitions, legacy `VM_*` masks, `vma_flags_t` helpers, `vm_flags_*` and `vma_*` accessors, VMA iterator helpers, mapping accounting helpers, `compat_set_desc_from_vma()`, `compat_vma_mmap()`, `vfs_mmap()`, `vma_set_page_prot()`, gap helpers, `mlock_future_ok()`, and file/mapping writable helpers.

## Control Flow and State

The header is mostly inline code. It maps VMA flags to bitmaps, converts between legacy and new VMA flag forms, mutates `vm_refcnt` for attach/detach, initializes VMAs, updates mm accounting counters, drives maple-tree iterators, and mediates file mmap hooks. State lives in caller-owned VMA, mm, file, and mapping structs.

## Dependencies and Integration Points

It depends on local stubs/custom headers, kernel maple-tree/rbtree/list/refcount/bitmap helpers, architecture config macros, and VMA harness globals such as `current`, `stack_guard_gap`, `sysctl_max_map_count`, `rlimit()`, and `vma_dummy_vm_ops`. It is the central compatibility layer for `tools/testing/vma`.

## Risks and Test Signals

Risks are high because duplicated kernel definitions can drift from real mm headers, especially flag bit positions, architecture-specific aliases, `VM_SHADOW_STACK`, pkeys, soft-dirty, and VMA iterator semantics. Passing VMA tests, sanitizer runs, and compile failures after upstream mm changes are the key signals that this duplicate layer remains aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/dup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h

## Purpose

`stubs.h` supplies no-op or simplified kernel APIs for the userspace VMA harness. It lets imported mm/VMA code compile without pulling in page tables, mempolicy, userfaultfd internals, KSM, locking, and filesystem internals.

## Important APIs, Types, and Functions

It forward-declares many kernel structs, defines attributes and constants, and stubs functions such as `userfaultfd_unmap_complete()`, `move_page_tables()`, `free_pgd_range()`, `ksm_execve()`, `ksm_exit()`, `vma_numab_state_init/free()`, anon-vma-name helpers, mmap action hooks, `fixup_hugetlb_reservations()`, `shmem_file()`, `ksm_vma_flags()`, PFN remap hooks, `do_munmap()`, lock helpers, `userfaultfd_unmap_prep()`, `can_modify_mm()`, `arch_unmap()`, `mpol_equal()`, `khugepaged_enter_vma()`, and VMA property predicates.

## Control Flow and State

Most functions either return success, return false, return input flags, or do nothing. They intentionally remove side effects outside the VMA algorithms under test.

## Dependencies and Integration Points

It is included by the VMA harness before imported kernel mm code. It depends on basic types from `dup.h` and shared kernel compatibility headers.

## Risks and Test Signals

Risks include masking failures in page-table moves, unmap completion, mempolicy, KSM, userfaultfd, locking, and filesystem interactions. The test harness should use these stubs only for VMA logic whose correctness can be asserted without those subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h

## Purpose

`vma/linux/mmzone.h` provides a minimal mmzone header for userspace VMA testing.

## Important APIs, Types, and Functions

It declares `first_online_pgdat()` and `next_online_pgdat()`, defines `for_each_online_pgdat`, `enum zone_type`, `MAX_NR_ZONES`, `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, pageblock macros, `struct zone` with `managed_pages`, and `pg_data_t` containing `node_zones`.

## Control Flow and State

Iteration over online pgdats is delegated to externally supplied harness functions. Zone state is reduced to managed page counters.

## Dependencies and Integration Points

It depends on Linux atomic types and alignment/bit macros from shared headers. It supports imported mm code that expects zone and pgdat types while running in the VMA harness.

## Risks and Test Signals

Risks include oversimplified NUMA/zone behavior and fixed pageblock order assumptions. Successful VMA tests that touch page accounting or pgdat iteration validate the minimal model for harness purposes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h -->
