# sources/distributed-fs/ceph-client/arch/hexagon/kernel/kgdb.c

## Purpose

`kgdb.c` maps Hexagon registers into GDB remote protocol state and handles KGDB exception notification. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `dbg_set_reg`, `kgdb_arch_set_pc`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_handle_exception`, `kgdb_notify`, `kgdb_arch_init`, and `kgdb_arch_exit`. Concrete declarations observed in the file: Includes: `linux/irq.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/kdebug.h`, `linux/kgdb.h`. Macros: `GDB_SIZEOF_REG`. Types referenced or declared: `dbg_reg_def_t`, `pt_regs`, `kgdb_arch`, `task_struct`, `die_args`, `notifier_block`. Functions/syscalls: `dbg_set_reg`, `kgdb_arch_set_pc`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_handle_exception`, `__kgdb_notify`, `kgdb_notify`, `kgdb_arch_init`, `kgdb_arch_exit`.

## Control Flow, State, And Persistence

On debug traps KGDB copies live or sleeping thread register state, optionally updates PC, and returns control according to KGDB core decisions.

## Dependencies And Integration Points

It integrates with `traps.c` debug handling, `pt_regs`, scheduler task stacks, and `linux/kgdb.h`.

## Risks And Test Signals

Risks are incorrect register numbering, broken PC updates, and bad sleeping-thread stack decoding. Test signals are KGDB breakpoint, single-step, register read/write, and detach/resume tests.
 A local static signal for this file is that it has 215 lines and 7045 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
