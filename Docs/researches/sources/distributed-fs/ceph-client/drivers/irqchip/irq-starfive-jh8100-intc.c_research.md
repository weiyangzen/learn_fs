# sources/distributed-fs/ceph-client/drivers/irqchip/irq-starfive-jh8100-intc.c

## Purpose
Implements the StarFive JH8100 external interrupt controller as a 32-line cascaded interrupt controller. It masks/unmasks child lines in local registers and dispatches pending status from one parent IRQ.

## Important APIs, Types, And Functions
`struct starfive_irq_chip` owns MMIO base, child domain, and raw spinlock. `starfive_intc_bit_set()` and `_clear()` perform register read-modify-write. The irq chip has mask/unmask callbacks, while `starfive_intc_irq_handler()` reads `SRC0_INT`, dispatches child hwirqs, and pulses `SRC0_CLEAR`.

## Control Flow
Probe allocates state, maps registers, gets and deasserts reset, enables the clock, creates a one-cell linear domain, obtains the parent IRQ, and installs the chained handler. Runtime dispatch iterates over set pending bits, calls `generic_handle_domain_irq()`, then sets and clears the corresponding clear bit.

## State And Persistence
The controller keeps persistent clock/reset enablement, MMIO base, domain, and a lock for mask register updates. There is no suspend/resume cache. Cleanup paths exist only for probe failure because successful initialization is early/platform irqchip lifetime.

## Dependencies And Integration Points
Depends on OF MMIO, clock, reset, chained irqchip, one-cell irqdomain APIs, and compatible `starfive,jh8100-intc` through `IRQCHIP_PLATFORM_DRIVER`.

## Risks
Missing runtime removal means clock/reset resources remain intentionally owned for the lifetime of the controller. Pending clear is a pulse sequence and must match hardware. All lines use `handle_level_irq`; edge-like sources would need upstream conditioning.

## Test Signals
Boot with clock and reset providers, verify 32 child hwirqs map, toggle mask/unmask, and trigger multiple simultaneous pending bits. Probe-failure tests should cover missing reset, clock, parent IRQ, and domain allocation failures.
