# sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_32.c

## Purpose
`kgdb_32.c` implements KGDB architecture support for 32-bit SPARC, including register conversion, breakpoint trap handling, continue/detach semantics, and PC updates.

## Important APIs, Types, and Functions
Key functions are `pt_regs_to_gdb_regs()`, `sleeping_thread_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `kgdb_arch_handle_exception()`, `kgdb_trap()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, and `kgdb_arch_set_pc()`. It defines `arch_kgdb_ops` with breakpoint instruction `ta 0x7d`.

## Control Flow and State
Register conversion copies globals/outs from `pt_regs`, locals/ins from the register window pointed to by frame pointer, and fills unavailable FP/control registers with zero. Sleeping-thread conversion uses `thread_info` saved kernel stack, PSR/WIM, and PC. Reverse conversion updates saved registers and preserves PSR CWP when changing PSR. `kgdb_arch_handle_exception()` handles continue and detach/kill packets, optionally sets PC from a hex parameter, and skips over `arch_kgdb_breakpoint` when resuming. `kgdb_trap()` forwards user-mode traps to normal hardware interrupt handling; kernel-mode traps flush windows, disable local IRQs, invoke KGDB core, and restore IRQs.

## Persistence and Dependencies
Persistent state is minimal; it reads/writes `pt_regs`, task `thread_info`, and live register windows. Dependencies include KGDB core, trapbase symbols, `flushw_all()`, `arch_kgdb_breakpoint`, and 32-bit register-window layout.

## Integration Points, Risks, and Test Signals
Integration points are `entry.S` KGDB trap entry, GDB remote protocol, and normal trap handling for user-mode breakpoints. Risks include dereferencing invalid user frame pointers while converting locals/ins, PSR/CWP corruption, and failing to skip breakpoint instructions. Test signals are KGDB connect, register read/write, continue from breakpoint, sleeping task inspection, and user-mode breakpoint fallback to normal trap behavior.
