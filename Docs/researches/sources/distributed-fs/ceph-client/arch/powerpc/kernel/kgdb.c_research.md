# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kgdb.c

## Purpose
Implements the PowerPC backend for KGDB, including trap-to-signal mapping, register serialization, breakpoint patching, single-step handling, and installation of architecture debugger hooks.

## Important APIs, Types, And Functions
Important functions include `kgdb_skipexception`, `kgdb_roundup_cpus`, `sleeping_thread_to_gdb_regs`, `dbg_get_reg`, `dbg_set_reg`, `kgdb_arch_set_pc`, `kgdb_arch_handle_exception`, `kgdb_arch_set_breakpoint`, `kgdb_arch_remove_breakpoint`, `kgdb_arch_init`, and `kgdb_arch_exit`. Internal handlers include `computeSignal`, `kgdb_debugger_ipi`, `kgdb_debugger`, `kgdb_handle_breakpoint`, `kgdb_singlestep`, `kgdb_iabr_match`, `kgdb_break_match`, and `kgdb_not_implemented`. Data includes `hard_trap_info`, `dbg_reg_def`, and saved old `__debugger*` hook pointers.

## Control Flow
Trap entry maps the PowerPC vector to a GDB signal and invokes generic KGDB exception handling. Breakpoint handling ignores user-mode traps, calls KGDB, and advances NIP past `BREAK_INSTR` when appropriate. Register get/set functions marshal `pt_regs` and optional SPE EVR state into GDB's register order. Continue/step packets optionally update PC and set MSR_SE or BookE DBCR0 single-step bits. Breakpoint install saves the original instruction with nofault read and patches in `BREAK_INSTR`; removal restores the saved instruction. Init swaps architecture debugger callbacks to KGDB handlers, and exit restores prior hooks.

## State And Persistence
State includes patched breakpoint instructions, saved original instructions in `kgdb_bkpt`, current task EVR state for SPE, global debugger hook pointers, `kgdb_cpu_doing_single_step`, and register contents in `pt_regs`. Text patches persist until breakpoint removal.

## Dependencies And Integration Points
Depends on generic KGDB, SMP debugger IPIs, PowerPC debug hook globals, text patching, instruction constants, ptrace register layout, SPE support, and trap numbering from exception code. It integrates with kdebug, single-step/debug exceptions, and kernel text mutation.

## Risks And Edge Cases
Risks include patching inaccessible or module-unloaded text, stale removed breakpoints, wrong register sizes between PPC32/PPC64/SPE, single-step state not cleared, user-mode traps accidentally consumed by KGDB, and failing to restore previous debugger hooks on exit. Breakpoint patching must preserve instruction cache coherency through `patch_instruction`.

## Test Signals
Signals include KGDB connect/continue/step, software breakpoint set/remove, SMP CPU roundup, register read/write through GDB, sleeping thread backtraces, BookE advanced debug stepping, SPE register access on 85xx, and module breakpoint tests.
