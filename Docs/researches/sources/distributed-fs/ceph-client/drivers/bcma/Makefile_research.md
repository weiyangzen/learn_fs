# sources/distributed-fs/ceph-client/drivers/bcma/Makefile

Purpose: this Makefile composes the BCMA bus driver object from core files and feature-specific modules selected by Kconfig.

Important APIs, types, and functions: `bcma-y` always includes `main.o`, `scan.o`, `core.o`, `sprom.o`, `driver_chipcommon.o`, `driver_chipcommon_pmu.o`, and `driver_chipcommon_b.o`. Conditional additions cover pflash, sflash, nflash, PCI, PCIe2, PCI host mode, MIPS, GMAC common, GPIO, PCI host, and SoC host. `obj-$(CONFIG_BCMA)` links the aggregate `bcma.o`; `ccflags-$(CONFIG_BCMA_DEBUG)` adds `-DDEBUG`.

Control flow: Kbuild expands the object list into one composite BCMA module or built-in object. There is no runtime code in this file.

State and persistence: build state is derived entirely from Kconfig. No runtime state is stored here.

Dependencies and integration points: it must match prototypes and conditional fallbacks in `bcma_private.h` and Kconfig dependencies. Object ordering matters modestly for composite initialization/linking but most inter-file integration is via symbols.

Risks: missing an object for a selected feature causes unresolved symbols; including an object without its dependency can break builds on unsupported architectures. Debug flag behavior depends on all sources using `dev_dbg`/`bcma_debug` appropriately.

Test signals: build BCMA as built-in and module under multiple config combinations. Link success and expected symbol availability validate the Makefile.
