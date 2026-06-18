# sources/distributed-fs/ceph-client/arch/mips/include/asm/syscalls.h

## Purpose

`syscalls.h` declares MIPS-specific syscall entry points and compat syscall shims.

## Important APIs, Types, And Functions

The APIs include signal-return trampolines, `sysm_pipe()`, MIPS MT affinity syscalls, O32/N32 signal returns, and 32-bit argument-splitting wrappers for fallocate, fadvise, readahead, and sync_file_range. Includes: `linux/linkage.h`, `linux/compat.h`. Macros/constants: `_ASM_MIPS_SYSCALLS_H`. Functions/prototypes/helpers: `sys_sigreturn`, `sys_rt_sigreturn`, `sysm_pipe`, `mipsmt_sys_sched_setaffinity`, `mipsmt_sys_sched_getaffinity`, `sys32_fallocate`, `sys32_fadvise64_64`, `sys32_readahead`, `sys32_sync_file_range`, `sys32_rt_sigreturn`, `sys32_sigreturn`, `sys32_sigsuspend`, `sysn32_rt_sigreturn`.

## Control Flow

There is no local flow; syscall tables reference these prototypes and implementations elsewhere marshal ABI-specific register/stack arguments into generic kernel operations.

## State And Persistence

State is syscall-callsite state in `pt_regs` and user memory passed through `__user` pointers.

## Dependencies And Integration Points

It integrates with generated syscall tables, signal delivery, compat code, scheduler affinity, and large-file syscall wrappers.

## Risks

Risks are prototype/table mismatches, wrong 64-bit argument pairing on 32-bit ABIs, and signal-frame compatibility breaks.

## Test Signals

Test signals are syscall table builds, LTP syscall coverage, signal return tests, and 32-bit userspace compatibility.
Static review signal: this source currently has 34 lines and 1313 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
