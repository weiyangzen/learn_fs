<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c

## Purpose
Implements the HiSilicon HiP04 interrupt controller, a GIC-like controller with different target-register layout and up to 510 interrupts.

## Important APIs, Types, And Functions
`struct hip04_irq_data` stores distributor and CPU interface bases, irqdomain, and IRQ count. Core callbacks are `hip04_mask_irq()`, `hip04_unmask_irq()`, `hip04_eoi_irq()`, `hip04_irq_set_type()`, `hip04_irq_set_affinity()`, and `hip04_ipi_send_mask()`. Initialization uses `hip04_of_init()`, `hip04_irq_dist_init()`, `hip04_irq_cpu_init()`, and `hip04_irq_domain_map()`.

## Control Flow
OF init maps the distributor and CPU interface, initializes CPU maps to all bits, reads the controller interrupt count and caps it at 510, allocates legacy IRQ descriptors and a legacy domain, sets the global IRQ handler, configures the distributor, and registers a CPU hotplug startup callback for CPU interfaces. Runtime handling reads INTACK in a loop and dispatches valid IDs through the legacy domain.

## State And Persistence
Global `hip04_data` and `hip04_cpu_map[]` persist for the boot lifetime. Hardware state consists of distributor target/config/enable registers and CPU interface priority/control registers. There is no PM save/restore path in this file.

## Dependencies And Integration Points
It depends on ARM exception and SMP APIs, `irq-gic-common` helpers, OF mapping, legacy irqdomains, and the `hisilicon,hip04-intc` compatible. SMP integration uses `set_smp_ipi_range()` and CPU hotplug state.

## Risks
The target register format differs from standard GIC; affinity writes use 16-bit fields for pairs of interrupts. Locking protects mask/type/affinity operations, so missing lock coverage can race MMIO updates. Legacy descriptor allocation can fail or collide with platform assumptions.

## Test Signals
Run boot, timer, peripheral IRQ, SMP IPI, affinity migration, CPU hotplug, and PPI/SPI trigger-type tests on HiP04 hardware. Check that interrupt count is capped correctly and that invalid DT mappings fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-hip04.c -->
