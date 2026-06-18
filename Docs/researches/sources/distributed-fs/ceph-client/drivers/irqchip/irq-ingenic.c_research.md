<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c

## Purpose
Implements the main Ingenic XBurst SoC interrupt controller for one-chip and two-chip variants, using generic irqchips and a shared cascade interrupt.

## Important APIs, Types, And Functions
`struct ingenic_intc_data` stores MMIO base, irqdomain, and chip count. `ingenic_intc_of_init()` maps the parent IRQ and register block, creates the domain, allocates generic chips, configures mask/unmask/wake callbacks, masks all IRQs, and requests the parent cascade IRQ. `intc_cascade()` reads each chip's pending register and dispatches set bits.

## Control Flow
The one-chip wrappers register 32 hwirqs for JZ4740/JZ4725B; two-chip wrappers register 64 hwirqs for JZ4760/JZ4770/JZ4775/JZ4780. Runtime handling iterates chips, reads `JZ_REG_INTC_PENDING`, and forwards each pending bit to the domain.

## State And Persistence
State is the private struct, domain, generic chip mask cache, and hardware mask registers. Wake-enabled masks are set for all 32 bits per chip, and `irq_gc_set_wake()` manages wake state. There is no explicit suspend/resume state beyond generic irqchip suspend behavior.

## Dependencies And Integration Points
It depends on OF mapping, generic irqchip, parent IRQ request, and Ingenic compatibles for one-chip and two-chip SoCs. It integrates with the arch interrupt path through a shared parent IRQ rather than `set_handle_irq()`.

## Risks
`request_irq()` passes NULL dev_id while handler data is set on the IRQ descriptor, so cleanup would be awkward if later added. All interrupts are configured as level handled; source-specific edge semantics must be handled elsewhere. Two-chip offset math must remain aligned to `CHIP_SIZE`.

## Test Signals
Test one-chip and two-chip DTs, pending dispatch from both chips, mask/unmask and wake callbacks, parent IRQ request failure logging, and hwirq-to-domain mapping around bit 31/32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic.c -->
