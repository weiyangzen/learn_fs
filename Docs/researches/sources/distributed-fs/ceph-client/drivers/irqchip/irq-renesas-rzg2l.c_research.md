<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c

## Purpose
`irq-renesas-rzg2l.c` implements the Renesas RZ/G2L, RZ/G3L, and RZ/Five IRQC. It exposes NMI, direct IRQ, and GPIO TINT sources through a hierarchical domain, with SoC-specific IRQ/TINT counts, shared IRQ selection, TINT lookup tables, and suspend/resume restoration.

## Important APIs, Types, and Functions
`struct rzg2l_irqc_priv` stores MMIO, selected IRQ/TINT chips, parent fwspecs, lock, hardware info, register cache, and shared-line bitmap. `struct rzg2l_hw_info` captures TINT LUT, counts, and shared IRQ layout. Key paths include clear helpers for NMI/IRQ/TINT, RZ/Five mask/unmask helpers, TINT enable/disable, NMI/IRQ/TINT set-type functions, shared IRQ allocation/free, `rzg2l_irqc_alloc()`, `rzg2l_irqc_free()`, interrupt parsing, common probe, and syscore suspend/resume.

## Control Flow
Common probe finds the parent domain, allocates singleton driver state, maps registers, stores SoC info, parses every parent interrupt into fwspecs, deasserts reset, enables runtime PM, initializes the lock, creates a hierarchical domain, and registers syscore callbacks. Allocation translates a two-cell child spec. Hwirq 0 uses the NMI chip; TINT specs may encode GPIOINT in the high 16 bits; direct IRQs use IRQ chips. Shared IRQ-capable variants reserve one of eight shared routes and program `INTTSEL` to select IRQ or TINT mode before allocating the parent.

## State and Persistence
Runtime state includes a global singleton pointer, `used_irqs` bitmap for shared routes, TINT source values stored as chip data, and cached `NITSR`, `IITSR`, `INTTSEL`, and `TITSR` registers for syscore resume. `TSSR` is intentionally restored by pinctrl later to avoid invalid-pin spurious interrupts.

## Dependencies and Integration Points
It integrates with reset control, runtime PM, parent irqdomains, pinctrl GPIO interrupt clients, syscore PM, RZ/Five-specific parent masking, and compat strings `renesas,rzg2l-irqc`, `renesas,r9a08g046-irqc`, and `renesas,r9a07g043f-irqc`.

## Risks and Edge Cases
The singleton design assumes one controller instance. Shared IRQ allocation can return `-EBUSY` if a direct IRQ and TINT compete for the same physical route. TINT source programming temporarily disables the byte lane to avoid spurious delivery. Resume ordering with pinctrl is delicate because `TSSR` is not restored here.

## Test Signals
Validate NMI, direct IRQ, TINT, and shared-route allocation; RZ/G3L LUT mapping; RZ/Five IMSK/TMSK masking; all trigger types supported per source class; suspend/resume register restoration; and failure behavior for invalid encoded TINT hwirqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c -->
