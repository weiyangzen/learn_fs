# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Makefile

## Purpose
This Makefile composes the Mantis/Hopper media PCI bridge objects and maps Kconfig symbols to kernel modules.

## Important APIs, Types, and Functions
It defines object lists for `mantis_core`, `mantis`, and `hopper`, including PCI, DMA, I2C, DVB, HIF/CA/PCMCIA/input, card tables, and per-board frontend files. It adds the DVB frontend include path through `ccflags-y`.

## Control Flow
There is no runtime flow. Kbuild links `mantis_core.o`, `mantis.o`, and `hopper.o` when their configuration symbols are enabled.

## State and Persistence Behavior
No runtime state is stored. Build composition determines which code is present in the kernel or modules.

## Dependencies and Integration Points
It integrates with the media PCI build, local Kconfig symbols, shared Mantis core modules, card-specific implementations, and headers under `drivers/media/dvb-frontends`.

## Risks
Object-list drift can omit required code or link unused/incompatible board files. Shared CA/HIF code lives in core, so card drivers depend on correct module ordering and symbol exports.

## Test Signals
Build tests for each Kconfig combination, module link checks, `modpost` symbol validation, and include-path validation for frontend headers are key signals.
