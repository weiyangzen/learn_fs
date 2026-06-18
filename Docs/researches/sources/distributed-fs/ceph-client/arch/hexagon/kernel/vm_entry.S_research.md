# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_entry.S

## Purpose

`vm_entry.S` contains Hexagon virtual-machine event entry and return assembly for interrupts, traps, machine checks, debug, and fork return. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important macros are `save_pt_regs`, `restore_pt_regs`, and `vm_event_entry`; labels include `event_dispatch`, `restore_all`, `_K_enter_genex`, `_K_enter_interrupt`, `_K_enter_trap0`, and `ret_from_fork`. Concrete declarations observed in the file: Includes: `asm/asm-offsets.h`, `asm/mem-layout.h`, `asm/hexagon_vm.h`, `asm/thread_info.h`. Macros: `save_pt_regs`, `restore_pt_regs`, `vm_event_entry`. Assembly entry labels: `event_dispatch`, `check_work_pending`, `restore_all`, `_K_enter_genex`, `_K_enter_interrupt`, `_K_enter_trap0`, `_K_enter_machcheck`, `_K_enter_debug`, `ret_from_fork`.

## Control Flow, State, And Persistence

Control flow saves the interrupted register set, dispatches to C handlers, checks thread work flags on return to user mode, restores registers, and resumes through the HVM return path.

## Dependencies And Integration Points

It depends on generated offsets, thread-info flags, C handlers in `traps.c`/`vm_events.c`, and `process.c` pending-work logic.

## Risks And Test Signals

Risks are register corruption, wrong stack layout, lost interrupt state, and return-to-user work omissions. Test signals are boot, syscall, interrupt, signal, fork, and preemption stress.
 A local static signal for this file is that it has 381 lines and 10198 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
