# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Makefile

## Purpose
Defines the object graph for the 8250 serial subsystem, splitting the common driver into module components and wiring each Kconfig option to its platform or bus-specific object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SERIAL_8250) += 8250.o` and `8250-y := 8250_core.o` form the main module, with conditional additions for PNP, DMA, PCI library, Fintek, and RSA. `obj-$(CONFIG_SERIAL_8250) += 8250_base.o` builds the base-port module from `8250_port.o`, `8250_dma.o` when enabled, and `8250_dwlib.o` when selected. Console support adds `8250_early.o`. The remaining `obj-*` lines map individual options to files such as `8250_pxa.o`, `8250_rt288x.o`, `serial_cs.o`, `8250_uniphier.o`, and `8250_tegra.o`.

## Control Flow
The build graph enforces the division described in `8250_rsa.c`: common port operations live in `8250_base`, while `8250.ko` can pass operation pointers to RSA support without direct circular references. Enabled Kconfig symbols determine which registration frontends are compiled as built-ins or modules.

## State And Persistence
No runtime state. The file is build metadata that persists in the kernel build tree and affects generated modules and link order.

## Dependencies And Integration Points
Depends directly on the symbols declared in `8250/Kconfig` and integrates with the parent serial Makefile, which always descends into `8250/`. Its object naming must match source files and module aliases expected by platform/PCI/PCMCIA binding.

## Risks And Test Signals
Risks are missing object mappings for Kconfig entries, circular module dependencies, and feature objects linked into the wrong module. Test signals include `make drivers/tty/serial/8250/`, `modpost` dependency output, loading `8250`, `8250_base`, and selected platform modules, and verifying console/earlycon objects appear only when configured.
