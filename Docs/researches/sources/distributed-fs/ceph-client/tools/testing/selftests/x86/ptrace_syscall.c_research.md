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
