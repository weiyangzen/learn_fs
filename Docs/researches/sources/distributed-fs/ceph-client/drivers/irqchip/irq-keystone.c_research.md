<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c

## Purpose
Implements the TI Keystone IRQ controller, which reads and clears source bits from a syscon register and exposes 28 child IRQs.

## Important APIs, Types, And Functions
`struct keystone_irq_device` stores device pointer, irqchip, software mask, parent IRQ, child domain, syscon regmap, offset, and workaround lock. Key functions are `keystone_irq_probe()`, `keystone_irq_handler()`, `keystone_irq_map()`, `keystone_irq_setmask()`, `keystone_irq_unmask()`, and `keystone_irq_remove()`.

## Control Flow
Probe resolves `ti,syscon-dev` with one argument for the register offset, gets the parent IRQ, initializes all child sources masked, creates a 28-entry linear domain, requests the parent IRQ, and clears all source bits. Runtime handler reads pending bits, writes the same value back to clear them, shifts off reserved low bits, applies the software mask, and dispatches each active source under `wa_lock`.

## State And Persistence
The software `mask` is the primary mask state; hardware pending state is cleared by writing the syscon register. There is no PM state. Removal frees the parent IRQ, disposes child mappings, and removes the domain.

## Dependencies And Integration Points
It depends on platform probing, OF, syscon/regmap, linear irqdomains, and compatible `ti,keystone-irq`. It integrates with device-control registers rather than a dedicated MMIO mapping.

## Risks
Mask/unmask only update software, so pending bits are still read and cleared for masked sources. The source ID bits start at bit 4; off-by-one shifts would deliver wrong hwirqs. Dispatch under `wa_lock` suggests a hardware or ordering workaround; removing it may reintroduce races.

## Test Signals
Test all 28 hwirqs, masked pending bits not dispatched, pending clear writeback, syscon lookup failure, parent IRQ request failure, remove cleanup, and interrupt storms with multiple simultaneous sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-keystone.c -->
