# sources/distributed-fs/ceph-client/drivers/irqchip/irq-crossbar.c

## Purpose
Implements the TI IRQ crossbar, a hierarchical interrupt router that maps many SoC interrupt sources onto a limited number of parent GIC SPI inputs.

## Important APIs, Types, and Functions
`struct crossbar_device` stores the routing lock, source/IRQ limits, safe map value, allocation map, MMIO base, register offsets, and selected write width. `crossbar_domain_alloc()`, `crossbar_domain_free()`, and `crossbar_domain_translate()` implement the hierarchical domain. `crossbar_of_init()` parses DT properties and initializes hardware safe routes.

## Control Flow
Init locates the parent domain, parses maximum sources and GIC IRQ slots, marks reserved/skipped GIC inputs, computes non-linear register offsets, writes safe-map values to routable entries, then creates a hierarchy above the parent. Allocation validates GIC-style SPI specs, finds a free parent SPI from high to low, allocates the parent IRQ, and writes the crossbar source into the chosen register.

## State and Persistence
Global `cb` owns `irq_map[]` where entries are free, reserved, skipped, or assigned to a source hwirq. Hardware crossbar registers persist routing and are reset to `safe_map` on free.

## Dependencies and Integration Points
Depends on OF properties `ti,max-crossbar-sources`, `ti,max-irqs`, `ti,reg-size`, optional reserved/skip/safe-map lists, hierarchical irqdomains, and GIC parent fwspecs.

## Risks and Test Signals
Risks include global singleton limitations, freeing using source hwirq versus allocated parent slot assumptions, invalid reserved/skip lists, and missing rollback if hierarchy creation fails after hardware init. Test signals are successful allocation of routed SPIs, correct parent GIC fwspecs, safe-map restoration on disposal, and rejection of PPI/non-SPI requests.
