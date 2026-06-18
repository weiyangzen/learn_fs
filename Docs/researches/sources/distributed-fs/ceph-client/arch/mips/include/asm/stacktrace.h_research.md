# sources/distributed-fs/ceph-client/arch/mips/include/asm/stacktrace.h

## Purpose

`stacktrace.h` declares MIPS stack unwind interfaces and provides `prepare_frametrace()` for synthesizing a `pt_regs` snapshot of the current register file.

## Important APIs, Types, And Functions

Important APIs are `unwind_stack()`, `unwind_stack_by_address()`, `raw_show_trace`, and `prepare_frametrace()`; helper macros stringify MIPS load/store mnemonics to save registers through inline assembly. Includes: `asm/ptrace.h`, `asm/asm.h`, `linux/stringify.h`. Macros/constants: `_ASM_STACKTRACE_H`, `raw_show_trace`, `STR_PTR_LA`, `STR_LONG_S`, `STR_LONG_L`, `STR_LONGSIZE`, `STORE_ONE_REG`. Types/enums/unions: `task_struct`, `pt_regs`. Functions/prototypes/helpers: `unwind_stack`, `unwind_stack_by_address`, `prepare_frametrace`.

## Control Flow

When KALLSYMS is available the unwind functions are implemented elsewhere; otherwise they degrade to raw trace behavior. `prepare_frametrace()` stores the current PC and registers into caller-supplied `pt_regs`.

## State And Persistence

State is only the caller-owned register snapshot; no persistent kernel state is modified.

## Dependencies And Integration Points

It integrates with oops reporting, stack dump code, kallsyms-aware unwinding, raw backtraces, and architecture register layout.

## Risks

Risks are wrong register slot arithmetic, clobbering `$1`, misleading traces without KALLSYMS, and 32/64-bit load-store mismatch.

## Test Signals

Test signals are `show_stack()`, oops dumps, panic traces, and kallsyms-off builds.
Static review signal: this source currently has 90 lines and 2199 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
