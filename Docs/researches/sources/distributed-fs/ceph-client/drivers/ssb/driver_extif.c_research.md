# sources/distributed-fs/ceph-client/drivers/ssb/driver_extif.c

## Purpose
Driver helpers for the SSB EXTIF core, providing external interface timing setup, optional external UART discovery, watchdog control, clock-control reads, and GPIO helpers.

## Important APIs, Types, and Functions
Important functions are `ssb_extif_init`, `ssb_extif_timing_init`, `ssb_extif_get_clockcontrol`, watchdog setters, GPIO helpers (`ssb_extif_gpio_*`), and optional `ssb_extif_serial_init`. Internal helpers wrap `ssb_read/write` and masked RMW.

## Control Flow
Init creates the EXTIF GPIO lock when an EXTIF device exists. Timing init enables programmable interface access and programs flash/UART wait counts from a supplied bus-cycle nanosecond value. Serial init disables GPIO interrupts, probes up to two UART windows at `SSB_EUART` with loopback modem-control checks, and fills port descriptors. GPIO and watchdog helpers perform direct register or locked masked updates.

## State and Persistence
State lives in EXTIF hardware registers and `extif->gpio_lock`. Watchdog/timing/GPIO settings persist until reset or overwritten.

## Dependencies and Integration Points
Used by MIPS core initialization, embedded watchdog/GPIO APIs, GPIO driver, and clock calculations. Depends on serial core constants, ioremap/iounmap for UART probing, and SSB register accessors.

## Risks
UART probing maps and unmaps a small fixed physical region and assumes legacy register layout. Timing values depend on correct bus clock. GPIO interrupt support is elsewhere and assumes polarity toggling semantics.

## Test Signals
Validate detected UART count/baud/IRQ, EXTIF watchdog programming, GPIO direction/value/interrupt mask behavior, and stable flash/external UART access after timing init.
