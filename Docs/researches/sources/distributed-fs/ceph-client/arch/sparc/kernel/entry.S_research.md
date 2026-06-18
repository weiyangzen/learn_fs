# sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.S

## Purpose
`entry.S` is the 32-bit SPARC low-level trap, interrupt, syscall, FPU, delay, KGDB, and register-window support file. It is the bridge between trap-table entries and C-level kernel handlers.

## Important APIs, Types, and Functions
Global entry points include `bad_trap_handler`, `real_irq_entry`, `linux_sparc_syscall`, `ret_from_fork`, `ret_from_kernel_thread`, `fpsave`, `fpload`, `__ndelay`, `__udelay`, `breakpoint_trap`, `flushw_all`, `restore_current`, optional `arch_kgdb_breakpoint`, `kgdb_trap_low`, and SMP IPI handlers. It calls C handlers such as `handler_irq()`, `do_hw_interrupt()`, `do_illegal_instruction()`, `do_sparc_fault()`, signal-return helpers, `sparc_fork()`/`sparc_clone()`/`sparc_vfork()`/`sparc_clone3()`, and ptrace syscall tracing.

## Control Flow and State
Trap handlers preserve PSR/WIM/window state with `SAVE_ALL`/`RESTORE_ALL`, re-enable traps where safe, and pass `pt_regs` plus PC/NPC/PSR to C. IRQ entry raises PIL, dispatches to platform IRQ handlers, and handles SMP soft IPIs and level-15 cross calls specially for sun4m, sun4d, LEON, and PCIC. Syscalls validate `%g1` against `NR_syscalls`, save user registers, optionally trace entry/exit, call the syscall table target, set/clear carry for errno, advance PC/NPC, and return through common trap exit. FPU helpers save queue/register state and recover from FSR-store traps. Delay helpers use calibrated loop counts.

## Persistence and Dependencies
State is CPU architectural state: PSR, WIM, windows, `thread_info` flags, trap table patches, floppy pseudo-DMA globals, and FPU registers. The file depends on `etrap_32.S`, `rtrap_32.S`, `winmacro.h`, generated offsets, IRQ/platform code, syscall table, and traps/signal/process C code.

## Integration Points, Risks, and Test Signals
This file is central to sparc32 execution. Risks include register convention breakage, incorrect PC/NPC advancement, window spill/fill corruption, SMP IPI misclassification, and trap recursion in FPU or unaligned paths. Test signals are clean boot, syscall/ptrace/signal tests, SMP IPIs, timer/floppy interrupts where configured, KGDB breakpoint behavior, FPU context switching, and stress tests that force register-window overflow/underflow.
