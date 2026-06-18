# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Makefile

Purpose: build map for the 8390 Ethernet driver directory. It connects Kconfig symbols to object files and, for drivers using the shared core wrapper, ensures the appropriate `8390.o` or `8390p.o` object is linked.

Important APIs, types, and functions: object mappings are `mac8390.o`, `apne.o 8390.o`, `etherh.o`, `ax88796.o`, `hydra.o`, `mcf8390.o`, `ne.o 8390p.o`, `ne2k-pci.o 8390.o`, `pcnet_cs.o 8390.o`, `stnic.o 8390.o`, `xsurf100.o`, and `zorro8390.o`.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment. Some board drivers include `lib8390.c` directly and therefore build as a single object (`mac8390`, `etherh`, `ax88796`, `hydra`, `mcf8390`); others link against wrapper objects exporting `ei_*` or `eip_*`.

State and persistence: no runtime state. The persistent effect is build composition, module contents, and whether the normal or delayed 8390 core is available.

Dependencies and integration points: paired with Kconfig and the 8390 core wrappers. `NE2000` intentionally uses `8390p.o` for ISA delays, while APNE, NE2K PCI, PCMCIA PCNET, and STNIC use normal `8390.o`.

Risks: omitting the wrapper object for a dependent driver causes unresolved `ei_*`/`eip_*` symbols. Adding `8390.o` to a driver that already includes `lib8390.c` would duplicate core code unnecessarily. Selecting `8390.o` versus `8390p.o` affects hardware timing.

Test signals: incremental and modular builds for each Kconfig symbol, `modpost` without unresolved symbols, correct module dependencies, and boot/probe tests for both direct-include and wrapper-linked drivers.
