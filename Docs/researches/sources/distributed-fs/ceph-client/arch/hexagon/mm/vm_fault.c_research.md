# sources/distributed-fs/ceph-client/arch/hexagon/mm/vm_fault.c

## Purpose

`vm_fault.c` implements Hexagon page-fault handling for execute, load, and store protection faults. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `read_protection_fault`, `write_protection_fault`, `execute_protection_fault`, and internal `do_page_fault`. Concrete declarations observed in the file: Includes: `asm/traps.h`, `asm/vm_fault.h`, `linux/uaccess.h`, `linux/mm.h`, `linux/sched/signal.h`, `linux/signal.h`, `linux/extable.h`, `linux/hardirq.h`, `linux/perf_event.h`. Macros: `FLT_IFETCH`, `FLT_LOAD`, `FLT_STORE`. Types referenced or declared: `pt_regs`, `vm_area_struct`, `mm_struct`, `exception_table_entry`. Functions/syscalls: `do_page_fault`, `read_protection_fault`, `write_protection_fault`, `execute_protection_fault`.

## Control Flow, State, And Persistence

Runtime flow rejects faults in interrupt/no-mm context, enables IRQs, finds/locks the VMA, checks access rights, calls `handle_mm_fault`, handles retry/OOM/SIGBUS/SIGSEGV, and uses exception-table fixups for kernel faults.

## Dependencies And Integration Points

It integrates with `traps.c`, generic MM fault machinery, perf page-fault events, uaccess exception tables, and signal delivery.

## Risks And Test Signals

Risks are mmap-lock leaks, wrong access-right classification, failure to fix up kernel uaccess faults, and signal-code mismatch. Test signals are page-fault selftests, COW/mmap stress, invalid user access, and kernel uaccess fault injection.
 A local static signal for this file is that it has 178 lines and 3856 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
