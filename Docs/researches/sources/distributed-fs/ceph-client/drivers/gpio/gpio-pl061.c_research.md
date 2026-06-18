<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c

## Purpose
AMBA ARM PrimeCell PL061 8-bit GPIO driver with direction/value operations, chained parent IRQ handling, edge/level type programming, wake forwarding, and suspend/resume context restore.

## Important APIs, types, and functions
`struct pl061` stores lock, base, chip, parent IRQ, and saved registers. GPIO callbacks are direction/get/set functions. IRQ support includes `pl061_irq_type()`, chained handler, mask/unmask/ack/wake, and immutable IRQ chip.

## Control flow
Probe maps the AMBA resource, initializes callbacks, disables IRQs, sets up a parent IRQ and irqchip, registers the chip, and stores drvdata. Output direction writes value, enables output direction, then writes value again. IRQ type updates `GPIOIS`, `GPIOIBE`, and `GPIOIEV` and selects edge/level flow.

## State and persistence behavior
Suspend saves output data for output lines plus direction and IRQ configuration. Resume restores line direction/value, then IRQ registers.

## Dependencies and integration points
Depends on AMBA bus ID `0x00041061`, gpiolib, chained IRQ helpers, raw spinlocks, generic GPIO request/free, and simple PM.

## Risks and edge cases
No-IRQ platforms still set one parent entry with IRQ 0 after warning. Mixed level and edge requests are rejected; no-trigger installs `handle_bad_irq`. Masked-address data register usage is easy to break.

## Test signals
Masked data addressing, output double-write, all IRQ trigger modes, `GPIOMIS` dispatch, edge ack, wake forwarding, and suspend/resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pl061.c -->
