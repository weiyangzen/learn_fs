# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh770x.c

## Purpose
`serial-sh770x.c` supplies SH770x-specific SCI/SCIF pin initialization callbacks for the `sh-sci` driver.

## Important APIs, Types, And Functions
The important export is `struct plat_sci_port_ops sh770x_sci_port_ops`, whose init hook configures serial pins according to UART port and termios flags.

## Control Flow
When a platform SCIF device from SH7705/SH770x setup is probed, `sh-sci` calls the port ops. The implementation chooses pin control behavior based on the port and requested line mode.

## State And Persistence
State is hardware pin function selection through SoC registers. The file itself has no independent storage.

## Dependencies And Integration Points
It is referenced by `setup-sh7705.c` and `setup-sh770x.c` via `plat_sci_port.ops`. It depends on `serial_core` structures and SH serial/pin helper definitions.

## Risks
Incorrect pin setup prevents console or UART operation even when MMIO/IRQ resources are correct. Control-line behavior can vary by board wiring.

## Test Signals
Early console output, runtime `ttySC*` transmit/receive tests, and hardware-flow-control tests where available validate the callbacks.
