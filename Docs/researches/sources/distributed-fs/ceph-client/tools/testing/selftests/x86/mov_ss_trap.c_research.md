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
