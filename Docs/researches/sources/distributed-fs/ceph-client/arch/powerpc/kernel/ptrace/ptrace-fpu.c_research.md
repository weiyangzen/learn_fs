# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-fpu.c

## Purpose
This file implements legacy `PTRACE_PEEKUSR`/`PTRACE_POKEUSR` access to individual floating-point registers and FPSCR.

## Important APIs, Types, And Functions
It exports `ptrace_get_fpr()` and `ptrace_put_fpr()`. It uses `flush_fp_to_thread()`, `PT_FPR0`, `PT_FPSCR`, `TS_FPR()`, and `CONFIG_PPC_FPU_REGS`.

## Control Flow
Both functions reject indexes past `PT_FPSCR`. With FPU registers configured, they flush live FP state to `thread.fp_state`; register indexes before FPSCR read or write FPR words, with PPC32 treating the index as 32-bit words and non-PPC32 copying a native long from the selected FPR lane. The FPSCR index reads or writes `thread.fp_state.fpscr`. Without FPU registers, reads return zero and writes are ignored after validation.

## State And Persistence
State is persisted in `task->thread.fp_state`. There is no file-local state.

## Dependencies And Integration Points
The functions are called by `arch_ptrace()` and `compat_arch_ptrace()` for USER-area FPR access. Whole-regset FPR access is handled by `ptrace-vsx.c` or `ptrace-novsx.c`.

## Risks
The PPC32 word-index ABI differs from native 64-bit FPR layout and can break debuggers if changed. Missing flushes can expose stale FPU state. The code relies on PPC32 and VSX being incompatible, checked in `pt_regs_check()`.

## Test Signals
Tests should cover PEEK/POKE of FPR0, middle registers, FPSCR, out-of-range indexes, PPC32 word halves, and no-FPU configurations.
