# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7750.c

## Purpose
`setup-sh7750.c` supports SH7091, SH7750, SH7750S, SH7750R, SH7751, and SH7751R platform devices and interrupt controllers.

## Important APIs, Types, And Functions
It defines RTC, SCI, SCIF, TMU0, optional TMU1 devices, multiple INTC descriptors (`intc_desc`, DMA4/DMA8, TMU34, IRLM, PCI), `sh7750_devices_setup()`, `plat_early_device_setup()`, `plat_irq_setup()` variants, and `plat_irq_setup_pins()`.

## Control Flow
Normal init registers SCI/SCIF depending on `mach_is_rts7751r2d()` and then adds timers/RTC. Early init similarly registers console serial devices and early timers. Compile-time subtype blocks select which interrupt descriptors `plat_irq_setup()` registers. `plat_irq_setup_pins(IRQ_MODE_IRQ)` enables IRLM on supported subtypes and registers IRL vectors.

## State And Persistence
Static platform data becomes driver state. Interrupt setup writes `INTC_ICR` for IRLM mode and registers descriptors for DMA, PCI, and timer interrupts. No disk state exists.

## Dependencies And Integration Points
It integrates with `sh-sci`, `sh-tmu`, `sh-rtc`, generated machine type helpers, SH INTC, and board-specific RTS7751R2D serial behavior.

## Risks
Many subtype conditionals make build and runtime coverage important. Calling IRQ pin setup on SH7750/SH7091 intentionally `BUG()`s because interrupts cannot be masked in that mode. Board-specific serial clock enable flags can affect early console.

## Test Signals
Subtype build tests, early console on RTS7751R2D and non-RTS boards, TMU/RTC probe, DMA/PCI IRQ delivery, and IRL pin-mode tests validate behavior.
