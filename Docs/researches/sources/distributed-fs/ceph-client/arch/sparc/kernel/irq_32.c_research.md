# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_32.c

## Purpose
`irq_32.c` provides generic sparc32 IRQ glue: local interrupt enable/disable primitives, virtual IRQ allocation and PIL chaining, generic IRQ dispatch from trap level, `/proc/interrupts` extras, floppy fast interrupt integration, and platform IRQ initialization dispatch.

## Important APIs, Types, and Functions
Exported functions include `arch_local_irq_save()`, `arch_local_irq_enable()`, `arch_local_irq_restore()`, and optional `sparc_floppy_request_irq()`. Other key functions are `irq_alloc()`, `irq_link()`, `irq_unlink()`, `arch_show_interrupts()`, `handler_irq()`, `sparc_floppy_irq()`, and `init_IRQ()`.

## Control Flow and State
Local IRQ primitives manipulate PSR PIL bits. `irq_alloc()` reuses or creates a virtual IRQ in `irq_table` for a `(real_irq,pil)` pair. `irq_link()` inserts the bucket into `irq_map[pil]`; `irq_unlink()` removes it. `handler_irq()` sets IRQ regs, enters IRQ context, walks the bucket chain for the PIL, and invokes `generic_handle_irq()`. Floppy setup requests a normal IRQ, records globals used by `floppy_hardint`, patches trap table entries for a fast handler, and flushes caches. `init_IRQ()` selects sun4m, sun4d, or LEON controller initialization based on `sparc_cpu_model`.

## Persistence and Dependencies
Persistent state includes `sparc_config`, `irq_table`, `irq_map`, locks, optional floppy pseudo-DMA globals, and patched trap table instructions. Dependencies include generic IRQ core, platform IRQ files, cache flush, PCIC, LEON, and assembly entry points.

## Integration Points, Risks, and Test Signals
Integration points are trap-level IRQ entry, platform interrupt controllers, floppy driver, SMP interrupt statistics, and timer setup. Risks include linked-list corruption in `irq_unlink()` if bucket is absent, virtual IRQ exhaustion, trap-table patch coherency, and PSR PIL manipulation bugs. Test signals include timer and device interrupts, shared PIL dispatch, request/free cycles, floppy transfer interrupts, `/proc/interrupts` RES/CAL/NMI lines, and platform boot on sun4m/sun4d/LEON.
