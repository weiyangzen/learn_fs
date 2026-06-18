<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c

## Purpose
`irq-pic32-evic.c` drives the Microchip PIC32MZDA EVIC interrupt controller. It maps the controller's linear interrupt list into Linux IRQs, separates persistent and non-persistent interrupts into level and edge generic-chip types, and handles external IRQ polarity.

## Important APIs, Types, and Functions
`struct evic_chip_data` caches per-hwirq trigger types and up to eight externally polarity-programmable hwirqs. `plat_irq_dispatch()` reads `REG_INTSTAT` and invokes `do_domain_IRQ()` on MIPS. Type and configuration helpers are `pic32_set_ext_polarity()`, `pic32_set_type_edge()`, `pic32_bind_evic_interrupt()`, and `pic32_set_irq_priority()`. Domain operations are `pic32_irq_domain_xlate()` and `pic32_irq_domain_map()`, with setup in `pic32_of_init()`.

## Control Flow
Probe maps EVIC MMIO, allocates private data and a linear domain sized to `NR_IRQS`, then allocates two generic-chip types per 32-bit bank. DT translation records each hwirq's sense type. Mapping invokes `irq_map_generic_chip()`, switches to the edge chip when the recorded type indicates an edge interrupt, masks and clears the source, and programs a default priority. External IRQ numbers from `microchip,external-irqs` are used to permit rising/falling polarity changes through `INTCON`.

## State and Persistence
The global `evic_base` and `evic_irq_domain` back a single controller. Trigger type choices are cached in `evic_chip_data.irq_types` so mapping can select the right generic chip. EVIC enable, flag, priority, offset, and polarity registers are volatile hardware state without explicit suspend persistence.

## Dependencies and Integration Points
The file integrates with MIPS trap dispatch, Microchip PIC32 register helper macros, OF address parsing, Linux generic IRQ chips, default irqdomain selection, and optional board EIC binding through `board_bind_eic_interrupt`.

## Risks and Edge Cases
The driver assumes all interrupts are described through DT so `xlate()` can pre-cache trigger types before mapping. External interrupts support only one edge polarity, not both. `NR_IRQS` bounds hwirq validation; mismatched kernel configuration and hardware interrupt count can reject valid hardware or expose unused slots.

## Test Signals
Useful tests include DT-triggered level and edge mappings, external rising/falling polarity, EVIC priority programming, MIPS dispatch from `REG_INTSTAT`, masking and flag clearing during map, and boot logs/errors for invalid hwirqs or oversized external IRQ lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c -->
