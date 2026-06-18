# sources/distributed-fs/ceph-client/drivers/tty/serdev/Kconfig

## Purpose
Defines configuration for the serial device bus and its tty-port controller bridge.

## Important APIs, types, and functions
- `menuconfig SERIAL_DEV_BUS`: tristate core support for devices connected over serial ports.
- `config SERIAL_DEV_CTRL_TTYPORT`: boolean tty-port controller support for using common tty drivers as serdev controllers.

## Control flow
The Kconfig block exposes the serdev bus as a selectable feature. When `SERIAL_DEV_BUS` is enabled, `SERIAL_DEV_CTRL_TTYPORT` becomes available, depends on `TTY`, depends on the bus not being modular, and defaults to `y`.

## State and persistence behavior
No runtime state. The file controls compile-time inclusion of `core.o` and `serdev-ttyport.o` through the matching Makefile.

## Dependencies and integration points
Integrates the serdev subsystem with kernel configuration. The tty-port controller option is intentionally built-in only when the serdev core is built-in, avoiding a bool-to-module mismatch.

## Risks and edge cases
Disabling `SERIAL_DEV_CTRL_TTYPORT` while enabling `SERIAL_DEV_BUS` leaves serdev core available but prevents tty serial ports from acting as controllers. The dependency `SERIAL_DEV_BUS != m` means module builds of the core do not get this bool controller path.

## Test signals
Kconfig coverage should check built-in, module, and disabled combinations for `SERIAL_DEV_BUS`, and verify that `serdev-ttyport.o` only appears when `CONFIG_SERIAL_DEV_CTRL_TTYPORT=y`.
