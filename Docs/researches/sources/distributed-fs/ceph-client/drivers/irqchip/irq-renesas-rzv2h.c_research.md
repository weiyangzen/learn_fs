<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c

## Purpose
`irq-renesas-rzv2h.c` drives the Renesas RZ/V2H(P), RZ/V2N, and RZ/G3E ICU. It handles NMI, IRQ, GPIO TINT, CA55 software interrupts, pseudo error interrupts, error-status demuxing, DMAC request selection, SoC-specific TINT layouts, and syscore restore.

## Important APIs, Types, and Functions
`struct rzv2h_icu_priv` stores MMIO, parent fwspecs, lock, SoC hardware info, and register cache. `struct rzv2h_hw_info` describes TINT offset, field width, maximum TSEL, optional LUT, and ECC status ranges. Public `rzv2h_icu_register_dma_req()` programs DMAC request selectors. IRQ operations include EOI handlers, TINT enable/disable, NMI/IRQ/TINT set-type, software interrupt and SWPE pending injection, allocation, error and software IRQ handlers, setup helpers, and common probe.

## Control Flow
Probe maps registers, parses parent interrupts, deasserts reset, enables runtime PM, creates a hierarchical domain, records hardware info, registers syscore PM, and sets up internal CA55 software/error IRQ mappings. Allocation decodes TINT hwirq plus GPIOINT from the high 16 bits, chooses among TINT/IRQ/SWINT/SWPE/NMI chips, and allocates the parent IRQ. Set-type functions program ICU sense registers, clear stale status where appropriate, and force the parent to level-high for ICU-converted sources. Error setup clears/unmasks bus, ECC, and CA55 error registers and requests an ICU error handler.

## State and Persistence
Runtime state is singleton `rzv2h_icu_data`, per-hwirq parent fwspecs, TINT GPIOINT chip data, and a static rotating SWPE bit used for pseudo error injection. Syscore suspend caches NMI/IRQ/TINT type registers and restores them on resume; TSSR is restored by pinctrl instead.

## Dependencies and Integration Points
The driver integrates with parent irqdomains, reset/runtime PM, generic IRQ injection, Renesas public ICU header, DMAC clients, pinctrl TINT clients, syscore PM, and OF platform irqchip matching for three SoC families.

## Risks and Edge Cases
The common probe sets `info` after creating the domain, so no allocation should occur before that assignment and setup. TINT `tint` values are bounds-checked before optional LUT translation, making LUT size and `max_tssel` important. Error handlers clear broad status masks and log warnings only.

## Test Signals
Validate TINT field widths of 8 and 16 bits, RZ/G3E LUT and offset, CA55 software IRQ injection with `CONFIG_GENERIC_IRQ_INJECTION`, SWPE rotation, bus/ECC/IP error clearing, DMAC helper writes, suspend/resume type restore, and invalid encoded TINT rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c -->
