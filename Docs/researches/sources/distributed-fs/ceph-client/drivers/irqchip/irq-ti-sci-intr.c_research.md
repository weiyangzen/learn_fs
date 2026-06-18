# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-intr.c

## Purpose
Implements the TI K3 Interrupt Router hierarchy over TI SCI. It routes input hwirqs to allocated output interrupts, then forwards those to a parent GIC or another TI interrupt router.

## Important APIs, Types, And Functions
`struct ti_sci_intr_irq_domain` stores the TI SCI handle, output IRQ resource pool, device pointer, TI SCI device ID, and optional global trigger type. `ti_sci_intr_irq_domain_translate()` supports one-cell global-type and two-cell per-line bindings. `ti_sci_intr_alloc_parent_irq()` allocates output resources and programs TI SCI `set_irq`.

## Control Flow
Probe finds the parent domain, reads `ti,intr-trigger-type` if present, gets the TI SCI handle and device ID, obtains the IR output resource pool, and creates a hierarchy domain. Allocation translates the child fwspec, gets a free output IRQ, maps it through optional `ti,interrupt-ranges`, builds a parent fwspec for GIC or another INTR, allocates parent IRQs, calls TI SCI `set_irq`, and stores the output IRQ in chip data. Free reverses the SCI route, releases the resource, frees the parent, and resets irq_data.

## State And Persistence
Driver state is per-domain and resource-pool backed. Runtime route state is held by system firmware through TI SCI plus parent irqdomain mappings. There is no explicit suspend/resume state in this source.

## Dependencies And Integration Points
Depends on TI SCI protocol/resource APIs, OF parent domains, optional `ti,interrupt-ranges`, optional global trigger property, GIC-v3 formatting, and compatible `ti,sci-intr`.

## Risks
Incorrect interrupt ranges route to wrong parent hwirqs. Parent INTR nodes may expect one-cell or two-cell specifiers depending on their trigger-type property. Freeing must call TI SCI before resource release to avoid stale firmware routes. The module author string has a typo but does not affect behavior.

## Test Signals
Test direct GIC parent and chained INTR parent configurations, one-cell global trigger and two-cell per-line trigger DT forms, output resource exhaustion, route free/reallocation, and TI SCI set/free failure paths.
