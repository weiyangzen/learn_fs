<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h

## Purpose
This header defines low-level m68k exception/syscall entry stack layout and assembly macros for saving/restoring register state, interrupt masking, switch-stack handling, user stack pointer access, and current task lookup.

## Important APIs, Types, And Functions
- `ALLOWINT` defines interrupt enable mask, with an Atari-specific HSYNC exclusion.
- Assembly macros include `SAVE_ALL_SYS`, `SAVE_ALL_INT`, `RESTORE_USER`/`RESTORE_ALL`, `SAVE_SWITCH_STACK`, `RESTORE_SWITCH_STACK`, `RDUSP`, `WRUSP`, and `GET_CURRENT`.
- ColdFire paths distinguish software A7 user-stack emulation from modern separate USP/KSP support.
- MMU builds reserve `%a2` as `curptr` and define `get_current` to derive current from stack base.
- C-string macros expose `SAVE_ALL_INT` and `GET_CURRENT(tmp)` for inline assembly in C code.

## Control Flow
Exception and syscall assembly expands these macros at entry. They push `pt_regs` fields, mark non-syscall interrupts with `orig_d0 = -1`, optionally switch stacks, disable interrupts for sensitive ColdFire paths, and restore state with `rte` on return.

## State And Persistence Behavior
The macros mutate the kernel stack, saved register frames, `sw_usp`/`sw_ksp` on older ColdFire, `%a2` current pointer on MMU systems, and processor status. The saved frame persists until exception return or scheduler handling consumes it.

## Dependencies And Integration Points
It depends on setup, page/thread-info sizes, assembler context, `pt_regs` offsets from generated asm offsets, and CPU config flags. It is central to syscall, interrupt, trap, signal, ptrace, and context-switch paths.

## Risks And Edge Cases
Stack layout comments must match generated offsets and assembly users exactly. ColdFire software USP handling disables interrupts because stack switching is fragile. Register ordering affects ptrace, signals, and core dumps.

## Test Signals
Syscall entry/exit, nested interrupts, signal delivery/return, ptrace register inspection, context-switch stress, ColdFire SW_A7 configs, and Atari interrupt masking tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/entry.h -->
