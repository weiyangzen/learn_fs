# sources/distributed-fs/ceph-client/arch/hexagon/kernel/ptrace.c

## Purpose

`ptrace.c` implements Hexagon ptrace register access and syscall tracing hooks. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `genregs_get`, `genregs_set`, `user_enable_single_step`, `user_disable_single_step`, `ptrace_disable`, and `arch_ptrace`. Concrete declarations observed in the file: Includes: `linux/kernel.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/mm.h`, `linux/smp.h`, `linux/errno.h`, `linux/ptrace.h`, `linux/regset.h`, `linux/user.h`, `linux/elf.h`, `asm/user.h`. Macros: `INEXT`. Types referenced or declared: `task_struct`, `user_regset`, `membuf`, `pt_regs`, `user_regs_struct`, `hexagon_regset`, `user_regset_view`. Functions/syscalls: `user_enable_single_step`, `user_disable_single_step`, `genregs_get`, `genregs_set`, `ptrace_disable`, `arch_ptrace`.

## Control Flow, State, And Persistence

Ptrace regset flow copies fields between `pt_regs` and `user_regs_struct`, toggles single-step in HVME state, and delegates generic requests to `ptrace_request`.

## Dependencies And Integration Points

It integrates with `registers.h`, ELF regsets, signal/core-dump ABI, and `traps.c` syscall/debug reporting.

## Risks And Test Signals

Risks are register offset mismatch, bad single-step masking, and syscall trace regressions. Test signals are strace, GDB register set/get, single-step, and core-dump register validation.
 A local static signal for this file is that it has 174 lines and 4594 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
