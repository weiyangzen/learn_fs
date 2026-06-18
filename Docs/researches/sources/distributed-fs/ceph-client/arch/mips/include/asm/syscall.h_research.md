# sources/distributed-fs/ceph-client/arch/mips/include/asm/syscall.h

## Purpose

`syscall.h` implements the MIPS `asm-generic/syscall.h` accessors for syscall tracing, audit, seccomp, ptrace, and restart logic.

## Important APIs, Types, And Functions

Important helpers include `mips_syscall_is_indirect()`, `syscall_get_nr()`, `syscall_set_nr()`, `mips_syscall_update_nr()`, argument get/set helpers, return/error accessors, `syscall_get_arguments()`, `syscall_set_arguments()`, and `syscall_get_arch()`. Includes: `linux/compiler.h`, `uapi/linux/audit.h`, `linux/elf-em.h`, `linux/kernel.h`, `linux/sched.h`, `linux/uaccess.h`, `asm/ptrace.h`, `asm/unistd.h`. Macros/constants: `__ASM_MIPS_SYSCALL_H`, `__NR_syscall`. Types/enums/unions: `task_struct`, `pt_regs`. Functions/prototypes/helpers: `mips_syscall_is_indirect`, `syscall_get_nr`, `syscall_set_nr`, `mips_syscall_update_nr`, `mips_get_syscall_arg`, `mips_set_syscall_arg`, `syscall_get_error`, `syscall_get_return_value`, `syscall_rollback`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`.

## Control Flow

The accessors read and update syscall number/arguments in `pt_regs` and `thread_info->syscall`, including O32 indirect `syscall()` handling where the real syscall number moves from `v0` to `a0` and 32-bit arguments may live in `regs->args`.

## State And Persistence

State is per-task syscall number in `thread_info`, `pt_regs` argument/return registers, and audit architecture flags; no persistent storage is used.

## Dependencies And Integration Points

It integrates with syscall entry/exit assembly, seccomp, audit, tracepoints, ptrace, compat ABIs, and syscall tables for O32/N32/N64.

## Risks

Risks are ABI-specific argument corruption, incorrect indirect syscall rewriting, wrong audit arch for endian/N32/N64, and broken seccomp/ptrace replay.

## Test Signals

Test signals are syscall tracing tests, seccomp user-notify/filter tests, audit arch checks, O32/N32/N64 compat syscall suites, and strace comparisons.
Static review signal: this source currently has 188 lines and 4588 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
