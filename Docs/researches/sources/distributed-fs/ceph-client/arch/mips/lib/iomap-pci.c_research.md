# sources/distributed-fs/ceph-client/arch/mips/lib/iomap-pci.c

Purpose: implements legacy PCI IO port mapping helpers for MIPS.

Important APIs/functions: `__pci_ioport_map` and exported `pci_iounmap` under `CONFIG_PCI_DRIVERS_LEGACY`.

Control flow: IO port mapping derives the host controller from `dev->bus->sysdata`, uses `io_map_base`, and warns/falls back to `mips_io_port_base` if unset; multiple PCI domains can panic to avoid corruption. `pci_iounmap()` only calls `iounmap()` for addresses outside the controller IO resource window.

State and persistence: may initialize `ctrl->io_map_base` as a fallback.

Dependencies and integration: used by legacy PCI drivers and MIPS PCI controller structures.

Risks: fallback mapping is explicitly unsafe for multiple domains. Incorrect resource bounds can leak or unmap wrong IO regions.

Test signals: legacy PCI IO driver probe, multi-domain panic path review, and IO resource mapping/unmapping tests.
