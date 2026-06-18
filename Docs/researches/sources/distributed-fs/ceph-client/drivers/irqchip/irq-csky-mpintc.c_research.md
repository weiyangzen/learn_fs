# sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-mpintc.c

## Purpose
Implements the C-SKY multiprocessor interrupt controller with global/common IRQs, per-CPU local IRQs, trigger configuration, affinity routing, and SMP IPI support.

## Important APIs, Types, and Functions
Global `root_domain`, `INTCG_base`, `INTCL_base`, per-CPU `intcl_reg`, and `__trigger` store controller state. Important functions are `setup_trigger()`, `csky_mpintc_handler()`, mask/unmask/eoi callbacks, `csky_mpintc_set_type()`, `csky_irq_set_affinity()`, `csky_mpintc_send_ipi()`, and `csky_mpintc_init()`.

## Control Flow
Init maps the controller using an architecture control-register physical base, enables global/local blocks, creates a linear domain sized by `csky,num-irqs`, initializes each CPU's local register pointer, installs the root handler, and sets up an IPI mapping on IRQ 15 for SMP. Dispatch reads the current CPU's ready IRQ register and handles that hwirq.

## State and Persistence
`__trigger[]` caches requested trigger mode and is programmed during unmask. Per-CPU local registers control local enable/ack/IPI signaling. Global CIDSTR routing persists external IRQ affinity, using CPU 0 for broadcast/auto delivery and BIT(31) for single CPU mode.

## Dependencies and Integration Points
Depends on C-SKY traps/register ops, SMP cpumasks, irqdomain, OF, and architecture IPI registration. Local IRQs below 32 are per-CPU; common IRQs use fasteoi.

## Risks and Test Signals
Risks include memory leak/error cleanup gaps, `irq_data_update_effective_affinity()` using encoded CPU value after BIT(31), one-ready-IRQ dispatch assumptions, and trigger programming on the current CPU during unmask. Test signals include SMP IPI delivery, correct external IRQ affinity, trigger type changes, and per-CPU interrupt accounting.
