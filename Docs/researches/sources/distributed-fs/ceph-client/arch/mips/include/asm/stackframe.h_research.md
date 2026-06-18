# sources/distributed-fs/ceph-client/arch/mips/include/asm/stackframe.h

## Purpose

`stackframe.h` defines the assembly macros used by MIPS exception and interrupt entry code to build, save, and restore `pt_regs` stack frames.

## Important APIs, Types, And Functions

Key APIs are assembly macros such as `SAVE_SOME`, `SAVE_ALL`, `RESTORE_SOME`, `RESTORE_ALL`, `SAVE_TEMP`, `SAVE_STATIC`, `SAVE_AT`, `RESTORE_TEMP`, `RESTORE_STATIC`, and `get_saved_sp`/`set_saved_sp`; they encode register save slots, CFI annotations, kernel stack selection, CP0 status/cause capture, and CPU-specific HI/LO or Octeon multiplier handling. Includes: `linux/threads.h`, `asm/asm.h`, `asm/asmmacro.h`, `asm/mipsregs.h`, `asm/asm-offsets.h`, `asm/thread_info.h`. Macros/constants: `_ASM_STACKFRAME_H`, `STATMASK`.

## Control Flow

Entry code expands these macros at trap boundaries: detect whether the trap came from user or kernel mode, switch to the per-CPU kernel stack when needed, allocate `PT_SIZE`, save GPRs, CP0 state, EPC, BADVADDR, and optional scratch state, then later restore status and GPRs before returning through the low-level exception path.

## State And Persistence

State is transient CPU register state stored in the current kernel stack's `pt_regs`; the only persistent architectural state it touches is per-CPU `kernelsp` and CP0 state. There is no filesystem persistence.

## Dependencies And Integration Points

It depends on `asm-offsets.h`, `mipsregs.h`, `thread_info.h`, CPU errata config, EVA handling, SMP CPU-id storage, and entry assembly. It integrates directly with exception handlers, signal delivery, ptrace, unwinding, FPU emulation, and low-level return-to-user code.

## Risks

Risks are catastrophic register corruption, bad `pt_regs` offsets, broken CFI unwinding, incorrect user/kernel stack switching, or CPU-errata workaround regressions.

## Test Signals

Test signals are boot-to-user, syscall/interrupt/fault stress, ptrace and signal tests, oops backtraces, SMP bring-up, EVA builds, Octeon builds, and objdump checks against generated offsets.
Static review signal: this source currently has 496 lines and 11140 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
