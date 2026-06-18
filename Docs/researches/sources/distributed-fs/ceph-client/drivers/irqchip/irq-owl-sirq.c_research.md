<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c

## Purpose
`irq-owl-sirq.c` implements the Actions Semi Owl SIRQ controller, a small hierarchical controller that adapts three external interrupt lines into parent GIC SPIs while handling polarity and edge conversion in Owl-specific registers.

## Important APIs, Types, and Functions
`struct owl_sirq_params` describes whether SIRQ control fields share one register or use separate offsets. `struct owl_sirq_chip_data` stores mapped registers, the spinlock, and parent SPI numbers. Register helpers include `owl_field_get()`, `owl_field_prep()`, `owl_sirq_read_extctl()`, `owl_sirq_write_extctl()`, and `owl_sirq_clear_set_extctl()`. IRQ operations are `owl_sirq_mask()`, `owl_sirq_unmask()`, `owl_sirq_eoi()`, and `owl_sirq_set_type()`. Domain callbacks are `owl_sirq_domain_translate()` and `owl_sirq_domain_alloc()`.

## Control Flow
Init locates the parent domain, allocates chip data, maps the register block, parses three parent interrupts, records each parent SPI, and selects a 24 MHz external interrupt clock. A hierarchical domain is then created for three child IRQs. Allocation validates a two-cell child spec, converts falling/low child requests into rising/high parent semantics, installs `owl_sirq_chip`, and allocates the corresponding GIC SPI from the parent.

## State and Persistence
State lives in the chip data and the SIRQ control registers. The raw spinlock serializes shared-register read/modify/write operations. No suspend cache exists; register contents must survive power management or be restored by platform setup.

## Dependencies and Integration Points
The driver depends on OF irq parsing, parent irqdomains, GIC binding cell layout, hierarchical IRQ APIs, `irq_chip_*_parent()` helpers, and `dt-bindings/interrupt-controller/arm-gic.h`. Compatibles cover `actions,s500-sirq`, `actions,s700-sirq`, and `actions,s900-sirq`.

## Risks and Edge Cases
Only three SIRQ lines are valid; wrong DT cell counts or parent interrupt cells fail allocation/init. Because GIC cannot directly represent falling edge or active-low here, the child controller must correctly invert/convert signals. Edge EOI clears pending only for non-level interrupts, so incorrect trigger typing can cause missed or repeated interrupts.

## Test Signals
Validate all three SIRQ lines, S500/S700 shared-field packing, S900 independent offsets, low/falling conversion to parent high/rising, edge pending clear on EOI, SMP affinity pass-through, and failure reporting for malformed DT interrupt specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c -->
