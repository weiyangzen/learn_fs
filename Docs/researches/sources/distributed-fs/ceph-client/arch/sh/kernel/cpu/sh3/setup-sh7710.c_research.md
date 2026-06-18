# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7710.c

## Purpose
`setup-sh7710.c` supports SH7710 and SH7712 by registering interrupt mappings plus RTC, two SCIF ports, and TMU.

## Important APIs, Types, And Functions
The file defines `intc_desc`, `rtc_device`, `scif0_device`, `scif1_device`, `tmu0_device`, device arrays, and setup hooks `sh7710_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Normal init adds all platform devices. Early init adds SCIF and TMU for console and clock use. IRQ setup registers SH7710 INTC and then common SH3 pin setup.

## State And Persistence
State is static device/interrupt description and hardware state in INTC and peripheral drivers. RTC capabilities include four-digit year through platform data.

## Dependencies And Integration Points
It depends on `sh7710_sci_port_ops`, `evt2irq()`, `sh-tmu-sh3`, `sh-rtc`, and common SH3 IRQ code. SH7712 reuses this setup through the Makefile.

## Risks
Shared setup for SH7710/SH7712 can miss subtype differences. SCIF IRQ ordering and register type must match the serial driver expectations.

## Test Signals
Boot on both subtypes, serial loopback, TMU tick stability, RTC probe, and IRQ-pin tests are the relevant signals.
