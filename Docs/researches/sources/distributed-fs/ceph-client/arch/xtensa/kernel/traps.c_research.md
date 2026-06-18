# sources/distributed-fs/ceph-client/arch/xtensa/kernel/traps.c

Purpose: Initializes and handles Xtensa exceptions, interrupts, debug traps, coprocessor traps, fatal oops reporting, and stack/register dumps.

Important APIs, types, and functions: `dispatch_init_table`, per-CPU `exc_table` and `debug_table`, `do_unhandled()`, `do_interrupt()`, `do_illegal_instruction()`, `do_div0()`, `do_load_store()`, `do_unaligned_user()`, `do_coprocessor()`, `do_debug()`, `trap_set_handler()`, `trap_init()`, `secondary_trap_init()`, `show_regs()`, `show_stack()`, and `die()`.

Control flow: `trap_init()` seeds all causes with default user/kernel fast handlers and `do_unhandled`, then overlays configured fast and C handlers from `dispatch_init_table`, and writes per-CPU exception/debug save registers. Interrupt handling loops by priority level, masks previously unhandled bits, dispatches each pending IRQ via `do_IRQ()`, and exits through generic IRQ accounting. Exception handlers kill userspace with appropriate signals or call `die()` for kernel faults.

State and persistence: Per-CPU dispatch tables hold handler pointers; debug table stores debug exception entry; fake NMI path tracks per-CPU `nmi_count`; `die()` updates static `die_counter` and taints the kernel.

Dependencies and integration: Coupled to `vectors.S` table layout, `asm/traps.h`, page-fault handler, fast handlers, PMU NMI handler, hardware breakpoint code, stacktrace support, signal delivery, IRQ core, and coprocessor state management.

Risks: Dispatch table ordering must agree with vector assembly offsets; fake NMI validation can bugcheck if unexpected high-level IRQs fire; illegal divide-by-zero detection relies on the `DIV0` marker after an illegal instruction; `die()` in interrupt context panics.

Test signals: Boot trap initialization, user illegal instruction/div0/unaligned/load-store faults, kernel exception-table fixups, PMU/debug breakpoints, IRQ storms, stack dump format, and SMP secondary trap init.
