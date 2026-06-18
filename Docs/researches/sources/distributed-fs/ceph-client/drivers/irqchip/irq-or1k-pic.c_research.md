<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c

## Purpose
`irq-or1k-pic.c` implements the OpenRISC/OpenCores CPU-local programmable interrupt controller. It is the root interrupt controller for OR1K CPU exceptions and supports generic level, generic edge, and OR1200-specific latch behavior.

## Important APIs, Types, and Functions
`struct or1k_pic_dev` couples an `irq_chip`, flow handler, and status flags. The chip callbacks are `or1k_pic_mask()`, `or1k_pic_unmask()`, `or1k_pic_ack()`, `or1k_pic_mask_ack()`, plus OR1200 variants that clear `SPR_PICSR` by writing a zeroed bit. `pic_get_irq()` scans `SPR_PICSR`, `or1k_pic_handle_irq()` dispatches through `generic_handle_domain_irq()`, and `or1k_map()` installs the chip and handler. Init entry points are declared with `IRQCHIP_DECLARE()` for `opencores,or1200-pic`, `opencores,or1k-pic`, `opencores,or1k-pic-level`, and `opencores,or1k-pic-edge`.

## Control Flow
Initialization disables all PIC sources by clearing `SPR_PICMR`, creates a 32-entry linear root domain, and installs `or1k_pic_handle_irq()` via `set_handle_irq()`. On each CPU IRQ exception, pending bits in `SPR_PICSR` are scanned from low to high and dispatched into the domain. Mapping selects `handle_level_irq`, `handle_edge_irq`, or an SMP wrapper that delegates per-CPU requested interrupts to `handle_percpu_devid_irq()`.

## State and Persistence
State is CPU SPR backed: `SPR_PICMR` holds masks and `SPR_PICSR` holds pending/latch bits. The only global software state is `root_domain` and static chip descriptors. There is no persistent storage or suspend cache here.

## Dependencies and Integration Points
The driver depends on OR1K `mfspr()`/`mtspr()` accessors, Linux irqdomain, OF irqchip declaration, and the architecture root IRQ handler hook. It integrates directly with generic IRQ flow handlers and SMP per-CPU IRQ semantics.

## Risks and Edge Cases
The OR1200 clear-by-zero behavior differs from the OR1K spec, so choosing the wrong compatible can leave latched level interrupts stuck. `root_domain` is a singleton and assumes one root PIC. `or1k_pic_edge.flags` uses `IRQ_LEVEL`, which is unusual for an edge chip and should be treated as an inherited platform convention.

## Test Signals
Useful signals are successful boot root-domain creation, correct `/proc/interrupts` increments for all 32 hardware lines, masking/unmasking via `SPR_PICMR`, edge ACK behavior, OR1200 level-latch clearing, SMP per-CPU interrupt handling, and absence of repeated stuck interrupts after handler return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c -->
