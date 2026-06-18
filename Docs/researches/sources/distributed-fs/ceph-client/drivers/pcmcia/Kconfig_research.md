# sources/distributed-fs/ceph-client/drivers/pcmcia/Kconfig

Purpose: Defines the Kconfig surface for the PCCard subsystem: core PCCard support, 16-bit PCMCIA, CardBus, CIS firmware loading, resource probing, bridge/socket drivers, and embedded CompactFlash/PCMCIA controller drivers.

Important APIs and symbols: Top-level `PCCARD` builds `pcmcia_core`. `PCMCIA` builds 16-bit services and selects `CRC32`; `PCMCIA_LOAD_CIS` selects `FW_LOADER`; `CARDBUS` depends on PCI. Socket/controller symbols include `YENTA`, `PD6729`, `PCMCIA_ALCHEMY_DEVBOARD`, `PCMCIA_BCM63XX`, `OMAP_CF`, `ELECTRA_CF`, SoC families, `PCMCIA_MAX1600`, and `PCCARD_NONSTATIC`.

Control flow: This file has no runtime logic. Its dependency graph controls which source files in the directory are compiled, whether CardBus code is included in `pcmcia_core`, whether CIS replacement firmware can be loaded, and whether non-static resource managers are available.

State and persistence: Persistent state is the kernel configuration. Defaults such as `PCMCIA=y`, `CARDBUS=y`, Yenta quirks, and `PCMCIA_LOAD_CIS=y` influence built kernels and modules.

Dependencies and integration points: Ties the PCMCIA directory to architecture symbols (`ARM`, `MIPS_DB1XXX`, `BCM63XX`, `PPC_PASEMI`, `ARCH_OMAP16XX`), bus facilities (`PCI`, `HAS_IOMEM`, `HAS_IOPORT`), and firmware/resource subsystems.

Risks: Wrong dependencies can expose drivers on unsupported architectures, omit helper objects selected by board drivers, or build CardBus without required PCI support. Defaults also matter because PCMCIA is legacy hardware and often only tested on niche platforms.

Test signals: Kconfig coverage includes `allyesconfig`, targeted builds for Yenta, BCM63XX, Alchemy, OMAP, Electra, and SA/PXA sockets, plus checks that selected helper modules appear in the linked objects.
