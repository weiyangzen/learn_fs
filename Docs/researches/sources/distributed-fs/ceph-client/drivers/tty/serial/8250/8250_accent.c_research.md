# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_accent.c

## Purpose
Registers fixed legacy I/O-port definitions for Accent Async 8250-compatible serial cards through the platform `serial8250` driver.

## Important APIs, types, and functions
- `accent_data[]` declares two ports at I/O bases `0x330` and `0x338`, both IRQ 4, using `SERIAL8250_PORT`.
- `accent_device` is a `platform_device` named `serial8250` with ID `PLAT8250_DEV_ACCENT`.
- `accent_init()` registers the platform device.

## Control flow
At module init, the platform device is registered. The generic 8250 platform driver consumes the `plat_serial8250_port` array and registers the two legacy ports.

## State and persistence behavior
Static platform data only. No remove path is defined in this tiny probe module, so lifetime is effectively module/device lifetime.

## Dependencies and integration points
Depends on `serial_8250.h`, `8250.h` macros, and the generic `serial8250` platform-device consumer.

## Risks and edge cases
Hard-coded I/O bases and IRQs can conflict with other hardware. Shared IRQ behavior and resource ownership are delegated to generic 8250 handling.

## Test signals
Module load should create a `serial8250` platform device with two expected ports; verify no I/O resource conflicts and that the generic 8250 driver probes both entries.
