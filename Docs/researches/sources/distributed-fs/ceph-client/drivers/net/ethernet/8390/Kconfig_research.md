# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Kconfig

Purpose: Kconfig menu for National Semiconductor 8390 and compatible Ethernet drivers. It gates the vendor submenu and declares platform, bus, and hardware choices for AX88796, XSurf 100, Hydra, ARM EtherH/EtherM, Macintosh 8390, ColdFire 8390, ISA NE2000, PCI NE2K, Amiga PCMCIA APNE, PCMCIA PCNET, STNIC, and Zorro8390.

Important APIs, types, and functions: this is build metadata rather than C code. Important symbols are `NET_VENDOR_8390`, `AX88796`, `AX88796_93CX6`, `XSURF100`, `HYDRA`, `ARM_ETHERH`, `MAC8390`, `MCF8390`, `NE2000`, `NE2K_PCI`, `APNE`, `PCMCIA_PCNET`, `STNIC`, and `ZORRO8390`.

Control flow: selecting `NET_VENDOR_8390` exposes the submenu. Each driver entry constrains architecture or bus support with `depends on`, pulls helper code with `select`, and documents the module name. `XSURF100` selects the AX88796 base driver and AX88796B PHY support, while AX88796 can optionally select `EEPROM_93CX6`.

State and persistence: persistent output is kernel configuration state. Tristate selections determine which object files the Makefile builds into the kernel or as modules.

Dependencies and integration points: integrates with `drivers/net/ethernet/8390/Makefile`, architecture symbols (`ZORRO`, `ARM`, `ARCH_ACORN`, `MAC`, `COLDFIRE`, `SUPERH`, `AMIGA_PCMCIA`), bus symbols (`PCI`, `PCMCIA`, `HAS_IOPORT`), and shared libraries (`CRC32`, `PHYLIB`, `MDIO_BITBANG`, `NETDEV_LEGACY_INIT`).

Risks: incorrect dependencies can expose uncompilable drivers on unsupported architectures. Missing `select CRC32` would break multicast hashing users. Confusing ISA `NE2000` with PCI `NE2K_PCI` remains a user-facing configuration risk.

Test signals: `allyesconfig`/`allmodconfig` across relevant architectures, menu visibility for `NET_VENDOR_NATSEMI`, expected module names, and successful dependency resolution for AX88796 PHY/EEPROM and legacy ISA/PCMCIA options.
