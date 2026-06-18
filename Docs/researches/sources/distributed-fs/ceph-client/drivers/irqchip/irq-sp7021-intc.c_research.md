# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sp7021-intc.c

## Purpose
Implements the Sunplus SP7021 interrupt controller, exposing 224 child interrupts through two cascaded external parent IRQ lines. It includes a hardware workaround for GPIO_INT0-7 edge triggering by emulating edge behavior with level mode and polarity toggling.

## Important APIs, Types, And Functions
The global `sp_intc` holds two MMIO register groups, irqdomain, raw spinlock, and GPIO workaround state bitmap. Key functions are `sp_intc_assign_bit()`, chip callbacks for ack/mask/unmask/type, `sp_intc_get_ext_irq()`, cascaded handler `sp_intc_handle_ext_cascaded()`, and `sp_intc_init_dt()`.

## Control Flow
Initialization maps both register blocks, maps two parent interrupts, programs all child interrupts masked, edge, high-active, routed to EXT_INT0, and cleared, then creates a linear two-cell domain. The chained handler reads pending groups for EXT_INT0 or EXT_INT1, resolves the highest pending line, handles the child IRQ, and performs GPIO edge workaround polarity restoration when needed.

## State And Persistence
State is mostly hardware registers plus the static bitmap tracking whether each affected GPIO line is edge, low/falling, and currently active. The global singleton design assumes one SP7021 controller instance.

## Dependencies And Integration Points
Depends on OF MMIO/IRQ parsing, chained irqchip helpers, linear irqdomains, and compatible `sunplus,sp7021-intc`. Parent interrupts are consumed from the controller node as EXT_INT0 and EXT_INT1.

## Risks
The GPIO workaround is timing-sensitive because ack toggles polarity and the cascaded handler later restores it. Register group and pending-group layout constants must match silicon. `irq_set_chip_data()` stores `&sp_intc_chip` rather than controller data, which is harmless for current callbacks but fragile if chip data is later consumed differently.

## Test Signals
Exercise normal non-GPIO interrupts and GPIO_INT0-7 rising/falling edge cases, including repeated pulses and active-level transitions. Boot tests should confirm both parent IRQs are chained, 224 hwirqs map, and initial masking/clearing prevents stale interrupts.
