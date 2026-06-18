# sources/distributed-fs/ceph-client/drivers/irqchip/irq-clps711x.c

## Purpose
Implements the Cirrus EP7209/CLPS711X interrupt controller as a legacy ARM root controller with three banks and per-line EOI quirks.

## Important APIs, Types, and Functions
The static `clps711x_irqs[]` table describes valid lines, FIQ-only lines, enableable IRQs, and optional EOI offsets. `clps711x_irqh()` is the root handler. `clps711x_intc_irq_map()` chooses level, fasteoi, or bad handlers. `_clps711x_intc_init()` performs shared resource/domain setup.

## Control Flow
DT init reads the MMIO resource and calls the shared init. Init maps registers, stores status/mask pointers for three banks, masks all sources, allocates legacy descriptors, creates a legacy domain, sets it as default, installs the root handler, and initializes FIQ support when configured. Dispatch scans bank 0 then bank 1 and handles the highest pending bit.

## State and Persistence
Global `clps711x_intc` stores base, register pointers, domain, and ops. Hardware mask registers persist enabled state. Optional EOI writes clear line-specific peripherals. FIQ lines are mapped as bad/noautoen rather than normal IRQs.

## Dependencies and Integration Points
Depends on ARM legacy descriptor allocation, OF address parsing, FIQ support, and irqdomain legacy mapping. It integrates as the platform default IRQ domain for older ARM systems.

## Risks and Test Signals
Risks include only banks 0 and 1 being processed in the handler, FIQ lines accidentally requested as IRQs, invalid table entries without flags, and legacy descriptor base assumptions. Test signals are successful default-domain setup, EOI-cleared timers/UARTs, no normal IRQ handling for FIQ-only lines, and stable interrupt delivery on EP7209 hardware.
