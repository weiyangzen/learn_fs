# sources/distributed-fs/ceph-client/arch/arc/kernel/traps.c

Purpose: handles ARC non-MMU exceptions and trap families that do not belong to the page fault fast path.

Important APIs/functions: `die()` emits kernel diagnostics and halts with `flag 1`. `unhandled_exception()` converts user faults to signals and kernel faults to exception-table fixups or fatal oops. Macro-generated handlers include privilege, extension, instruction, memory, breakpoint, misaligned, and trap5 errors. Specialized handlers are `do_misaligned_access()`, `do_machine_check_fault()`, `do_non_swi_trap()`, `do_insterror_or_kprobe()`, and `abort()`.

Control flow: generic exceptions call `unhandled_exception()`. User mode sets `current->thread.fault_address` and calls `force_sig_fault()`. Kernel mode first tries `fixup_exception()` for `copy_to_user()`/`copy_from_user()` style fixups, otherwise calls `die()`. Misaligned access tries software emulation before falling back to SIGBUS. Trap parameters route to GDB breakpoints, kprobes, kgdb, GCC trap5, or no-op default.

State and persistence: updates per-task `thread.fault_address`; otherwise no persistent state. Fatal kernel path terminates execution.

Dependencies and integration: integrates with signal delivery, kprobes/kgdb notifier paths, exception-table fixups, unaligned emulation in `unaligned.c`, and diagnostics in `troubleshoot.c`.

Risks: incorrect classification can either kill user tasks unnecessarily or miss fatal kernel faults. Kprobe and kgdb trap parameter handling must match low-level trap encoding. The fatal halt path is architecture-specific and intentionally unrecoverable.

Test signals: userspace illegal instruction and misaligned access tests, kprobe/kgdb breakpoint tests, uaccess exception-table tests, and kernel oops diagnostics.
