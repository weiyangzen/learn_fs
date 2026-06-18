# sources/distributed-fs/ceph-client/drivers/tty/serial/Makefile

## Purpose
Defines the build composition for the top-level serial driver directory.

## Important APIs, Types, And Functions
The file builds `serial_base.o` from `serial_core.o`, `serial_base_bus.o`, `serial_ctrl.o`, and `serial_port.o` when `SERIAL_CORE` is enabled. It maps earlycon helpers and individual serial drivers to their Kconfig symbols. It always descends into `8250/` with `obj-y += 8250/`, adds Altera JTAG UART and Altera UART objects for their symbols, orders SPARC serial drivers before 8250 to preserve `ttySx` minor naming, and links modem-control GPIO and KGDB console helpers as configured.

## Control Flow
The build system evaluates each `obj-$(CONFIG_*)` line and includes the object or subdirectory as built-in or module. The explicit SPARC ordering comment documents a behavioral dependency on link/probe order for shared ttyS minor space.

## State And Persistence
No runtime state. This is build metadata that persists in the source tree and affects generated kernel images and modules.

## Dependencies And Integration Points
Consumes symbols from `drivers/tty/serial/Kconfig`, descends into 8250-specific build rules, and links drivers into the TTY, console, and platform-driver ecosystems.

## Risks And Test Signals
Risks are stale object mappings, wrong ordering for drivers sharing `ttySx`, and missing subdirectory traversal. Test signals are directory-level builds, `modpost`, boot enumeration of SPARC/8250 ttyS devices, and checking every enabled Kconfig symbol used in this work item (`SERIAL_ALTERA_JTAGUART`, `SERIAL_ALTERA_UART`, `SERIAL_8250*`) produces an expected object.
