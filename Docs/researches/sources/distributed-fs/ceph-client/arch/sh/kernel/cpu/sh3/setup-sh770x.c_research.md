# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh770x.c

## Purpose
`setup-sh770x.c` covers SH7706, SH7707, SH7708, and SH7709 platform setup. It conditionally describes subtype-specific vectors while registering SCI/SCIF, TMU, and RTC devices.

## Important APIs, Types, And Functions
It defines conditional INTC `vectors`/`prio_registers`, `intc_desc`, serial platform data using `sh770x_sci_port_ops`, `rtc_device`, `tmu0_device`, and hooks `sh770x_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Compile-time `CONFIG_CPU_SUBTYPE_*` blocks select the right interrupt events and priority registers. Early setup registers serial and TMU. Normal init adds serial, TMU, and RTC. Interrupt setup registers subtype INTC and common SH3 pin handling.

## State And Persistence
No persistent storage is used. Static resource arrays become platform-device state; INTC registration programs interrupt metadata.

## Dependencies And Integration Points
The file ties `sh-sci`, `sh-tmu-sh3`, `sh-rtc`, `evt2irq()`, and common SH3 IRQ-pin setup to several closely related CPU subtypes.

## Risks
Heavy conditional compilation creates subtype coverage risk; a change may compile for one SH770x but not another. Event vectors for optional LCDC/PCC/PINT/SCIF blocks must match each subtype.

## Test Signals
Subtype build matrix coverage, boot probe logs, external IRQ/PINT testing, and serial/TMU runtime tests are required for confidence.
