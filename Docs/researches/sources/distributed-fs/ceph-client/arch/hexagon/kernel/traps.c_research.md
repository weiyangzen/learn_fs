# sources/distributed-fs/ceph-client/arch/hexagon/kernel/traps.c

## Purpose

`traps.c` implements Hexagon exception, syscall trap, debug trap, oops, and stack display handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `show_stack`, `die`, `die_if_kernel`, `do_genex`, `do_trap0`, `do_machcheck`, and `do_debug_exception`. Concrete declarations observed in the file: Includes: `linux/init.h`, `linux/sched/signal.h`, `linux/sched/debug.h`, `linux/sched/task_stack.h`, `linux/module.h`, `linux/kallsyms.h`, `linux/kdebug.h`, `linux/syscalls.h`, `linux/signal.h`, `linux/ptrace.h`, `asm/traps.h`, `asm/vm_fault.h`, `asm/syscall.h`, `asm/registers.h`, `asm/unistd.h`, `asm/sections.h`, `linux/kgdb.h`. Macros: `TRAP_SYSCALL`, `TRAP_DEBUG`. Types referenced or declared: `task_struct`, `hexagon_switch_stack`, `thread_info`, `pt_regs`. Functions/syscalls: `is_valid_bugaddr`, `do_show_stack`, `show_stack`, `die`, `die_if_kernel`, `misaligned_instruction`, `misaligned_data_load`, `misaligned_data_store`, `illegal_instruction`, `precise_bus_error`, `cache_error`, `do_genex`, `do_trap0`, `do_machcheck`, `do_debug_exception`.

## Control Flow, State, And Persistence

General exceptions dispatch by `pt_cause` into page-fault or fatal signal paths. `do_trap0` handles syscall trap #1 by enabling interrupts, saving syscall metadata, indexing `sys_call_table`, and running ptrace entry/exit hooks; debug traps signal userspace or enter KGDB.

## Dependencies And Integration Points

It integrates with `vm_entry.S`, `vm_fault.c`, syscall table, ptrace, KGDB, kallsyms, and scheduler stacks.

## Risks And Test Signals

Risks are fatal misdecode of causes, syscall restart breakage, missing ptrace hooks, or unsafe oops locking. Test signals are page-fault tests, illegal instruction/sigill, strace, KGDB breakpoints, and panic/oops stack traces.
 A local static signal for this file is that it has 433 lines and 10139 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
