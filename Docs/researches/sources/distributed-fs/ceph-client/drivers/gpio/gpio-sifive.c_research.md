# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sifive.c

## Purpose
This driver exposes SiFive GPIO controllers using generic GPIO MMIO helpers and hierarchical IRQ domains. Each GPIO line may have a distinct parent IRQ, and the driver programs SiFive rise/fall/high/low interrupt-enable and pending registers through regmap.

## Important APIs, Types, and Functions
`struct sifive_gpio` stores MMIO base, `gpio_generic_chip`, regmap, per-line IRQ enable state, trigger type, and parent Linux IRQ numbers. `sifive_gpio_set_ie()` maps software trigger/enable state to four interrupt-enable registers. IRQ operations include type, enable/disable, EOI, affinity, parent mask/unmask, wake passthrough, and child-to-parent hwirq translation.

## Control Flow
Probe maps MMIO, creates a no-lock regmap, collects optional IRQs until the first missing one, derives the parent IRQ domain from the first IRQ, initializes the generic GPIO chip, disables all GPIO interrupt enables, fills gpio chip metadata, configures hierarchical `gpio_irq_chip`, and registers the chip. IRQ enable forces the line to input, clears all sticky pending bits, marks the line enabled in `irq_state`, and programs IE bits.

## State and Persistence
`trigger[]` and `irq_state` are the software source of truth for IE programming. Pending bits are cleared on enable and EOI. GPIO direction/value state lives in hardware. There is no suspend/resume handling.

## Dependencies and Integration Points
The driver uses platform IRQ arrays, regmap over MMIO, `gpio_generic_chip`, hierarchical irqchip parent operations, firmware nodes, and generic GPIO locking guards. It assumes all parent IRQs share one parent domain.

## Risks
At least one IRQ is mandatory, so GPIO-only use without interrupts fails probe. Parent IRQ collection stops at the first missing IRQ and sets `ngpio` to the number found, tying GPIO count to IRQ count. `sifive_gpio_irq_set_type()` stores any trigger bits without rejecting unsupported combinations. Regmap locking is disabled because the generic chip lock is expected to serialize updates.

## Test Signals
Test parent IRQ enumeration, GPIO count equal to parent IRQ count, all trigger combinations, enable clears pending registers and switches to input, hierarchical IRQ mapping, affinity/wake propagation, and failure with zero IRQs.
