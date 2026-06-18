# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2836.c

## Purpose
Implements the BCM2836 local root interrupt controller for per-CPU timer, PMU, GPU fast interrupt, mailbox, and SMP IPI delivery.

## Important APIs, Types, and Functions
`struct bcm2836_arm_irqchip_intc` stores the local register base and domain. `bcm2836_map()` assigns chips/handlers by local hwirq. `bcm2836_arm_irqchip_handle_irq()` handles per-CPU pending bits. SMP support includes `ipi_domain`, mailbox chained handling, `bcm2836_arm_irqchip_ipi_send_mask()`, CPU hotplug callbacks, and `set_smp_ipi_range()`.

## Control Flow
OF init maps local registers, programs local timer frequency scaling, creates a wired domain, initializes SMP/IPI support, and installs the root handler. Root dispatch reads the current CPU pending register and handles the first set bit. IPI setup maps mailbox0 as a mux IRQ, creates a separate IPI domain, allocates 32 IPIs, and chains mailbox dispatch.

## State and Persistence
Global `intc` holds base/domain. Per-CPU masks live in local timer/mailbox/PM routing registers. IPI state persists through mailbox set/clear registers and the allocated IPI domain. Timer frequency configuration is persistent hardware state.

## Dependencies and Integration Points
Depends on `irq-bcm2836.h` register definitions, SMP/hotplug infrastructure, irqdomain IPI bus tokens, and ARM exception handling. It integrates with the generic SMP IPI framework via `set_send_ipi` equivalent range setup.

## Risks and Test Signals
Risks include single-bit dispatch if multiple local pending bits are set, CPU-id based register offsets, incorrect affinity for PMU/GPU fast IRQs, and mailbox masking during hotplug. Test signals include working local timers, SMP IPIs, CPU hotplug mailbox mask transitions, and correct `/proc/interrupts` per-CPU counts.
