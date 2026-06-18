# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_entry.c

## Purpose
This file contains the main wm-FPU-emu entry point, instruction decode loop, address-mode handling, exception deferral behavior, and soft-FPU regset get/set functions.

## Important APIs, Types, and Functions
Public entry points are `math_emulate()`, `math_abort()`, `fpregs_soft_set()`, and `fpregs_soft_get()`. Static decode data includes `st_instr_table` and `type_table`. `valid_prefix()` parses FPU instruction prefixes. The file coordinates with `FPU_get_address()`, `FPU_get_address_16()`, `FPU_load_store()`, arithmetic tables, `FPU_exception()`, and signal delivery.

## Control Flow
`math_emulate()` records the trap context, derives default address mode from VM86, flat user mode, kernel mode, or LDT descriptor mode, parses prefixes, handles FWAIT and pending exception summary state, fetches ModRM, decodes memory versus register forms, checks segmented limits, loads memory operands when needed, handles NaN and denormal priority, dispatches arithmetic/load-store/register handlers, records instruction and operand addresses, and optionally looks ahead to emulate multiple FPU instructions unless tracing/reschedule prevents it. `math_abort()` restores the original EIP, sends a signal, and unwinds through the saved emulator stack. Regset set/get copy soft-FPU state to and from ptrace/core interfaces, rotate register order by `ftop`, and recompute tags on set.

## State and Persistence
The file mutates the current task's soft-FPU state: `FPU_info`, EIP/original EIP, control/status/tag words, top pointer, instruction and operand addresses, register stack, access limit, and no-update/lookahead flags. It also sends SIGFPE, SIGILL, or SIGSEGV through the current task.

## Dependencies and Integration Points
It integrates with x86 trap handling, user accessors, VM86 and LDT segmentation, FPU regset APIs, task FPU storage, scheduler reschedule checks, and all emulator operation tables. It is the boundary between the kernel's device-not-available/math fault path and the software x87 implementation.

## Risks and Test Signals
Risks include instruction decode errors, bad segment limit enforcement, incorrect exception priority, stale instruction pointer updates, non-reentrancy during user faults, and regset rotation/tag bugs. Test signals include forced math emulation across 16-bit, VM86, and flat modes where possible, ptrace/core dump FPU state checks, invalid instruction/fault signal tests, and comparison of decoded x87 instruction streams with hardware.
