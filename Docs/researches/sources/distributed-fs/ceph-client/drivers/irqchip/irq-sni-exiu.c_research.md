# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sni-exiu.c

## Purpose
Implements the Socionext SynQuacer External Interrupt Unit, a 32-line interrupt translator in front of a parent GIC. It supports DT early irqchip initialization and ACPI platform probing, translating EXIU local lines to parent SPI lines while programming level/edge and polarity registers.

## Important APIs, Types, And Functions
`struct exiu_irq_data` stores MMIO base and the parent SPI base. The irq chip implements ack, eoi, enable, mask, unmask, affinity forwarding, and type configuration. Domain callbacks `exiu_domain_translate()` and `exiu_domain_alloc()` convert DT GIC-style or ACPI two-cell specifiers into EXIU hwirqs and parent fwspecs.

## Control Flow
Initialization reads `socionext,spi-base`, maps MMIO, clears and masks all EXIU interrupts, then creates a hierarchical domain under the parent. Allocation validates SPI specifiers, maps the local hwirq, installs the EXIU chip, and allocates the parent GIC IRQ. Type setting programs EILVL/EIEDG, selects fasteoi or fasteoi-ack handlers, clears stale latch state, and forces the parent to level-high.

## State And Persistence
Persistent state is register-backed: mask bits, level/polarity/edge bits, and latched request status. The driver stores only the base pointer and SPI base. There is no suspend state cache, so correctness after low-power states depends on EXIU registers being retained or firmware restoring them.

## Dependencies And Integration Points
Depends on parent irqdomain lookup, GIC DT binding constants, OF address/IRQ parsing, ACPI resource/platform-device support, and compatible `socionext,synquacer-exiu` or ACPI HID `SCX0008`.

## Risks
`spi_base` translation must match firmware; otherwise child IRQs are routed to the wrong parent SPI. Level-triggered lines require EOI-time clearing to avoid stuck interrupts. The parent is always programmed as level-high, so EXIU polarity conversion must remain correct. ACPI and DT fwspec formats differ and must be kept in sync.

## Test Signals
Validate DT and ACPI boot paths, all four trigger types, affinity forwarding, mask/unmask ordering, and level lines that remain asserted across EOI. Firmware tests should confirm `socionext,spi-base` and parent interrupt ranges map to the expected GIC SPIs.
