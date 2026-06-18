# sources/distributed-fs/ceph-client/drivers/irqchip/irq-tb10x.c

## Purpose
Implements the Abilis TB10x interrupt controller as a 32-line generic-chip domain with chained parent interrupts. It supports both level and edge trigger programming using source mode/polarity registers.

## Important APIs, Types, And Functions
`tb10x_irq_set_type()` computes source mode and polarity bits from Linux trigger flags and switches generic-chip type handlers. `of_tb10x_init_irq()` maps resources, creates the domain, allocates level and edge generic chip types, and chains all parent IRQs listed in DT.

## Control Flow
Initialization requests and maps MMIO, creates a 32-line domain, allocates generic chips, populates level and edge callbacks/register offsets, chains each parent IRQ to `tb10x_irq_cascade()`, disables all interrupts, clears modes/polarities, and acks pending status. The cascaded handler dispatches the parent IRQ number into the domain.

## State And Persistence
Generic chip mask cache and MMIO source configuration provide state. There is no explicit PM handling. MMIO resource ownership is manual and cleaned up only on init failure.

## Dependencies And Integration Points
Depends on OF address/IRQ parsing, generic irq chips, chained handlers, and compatible `abilis,tb10x-ictl`.

## Risks
The cascade handler uses the Linux parent IRQ number as the hwirq, so platform mapping must align with expected domain entries. Trigger programming starts from register reads ORed with the bit and then toggles per case, making polarity/mode definitions easy to regress. Manual resource acquisition requires careful error cleanup.

## Test Signals
Boot with one or more parent interrupts, test level-low/high and edge-rising/falling lines, verify initial disable/ack state, and run invalid mixed trigger requests to confirm `-EBADR` behavior.
