# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Kconfig

Purpose: this Kconfig fragment exposes the Aeroflex Gaisler GRETH Ethernet MAC driver option.

Important APIs, types, and functions: the relevant symbol is `GRETH`, a tristate prompt for "Aeroflex Gaisler GRETH Ethernet MAC support". It depends on `SPARC` and selects `PHYLIB` and `CRC32`.

Control flow: when the architecture is SPARC, the user may choose `GRETH` as built-in, module, or disabled. The matching Makefile uses `CONFIG_GRETH` to build `greth.o`.

State and persistence: there is no runtime state. Persistent behavior is the kernel `.config` selection that controls whether the platform driver is compiled.

Dependencies and integration points: `SPARC` reflects the primary GRLIB/LEON deployment environment and the driver's use of SPARC-specific platform/IDPROM details. `PHYLIB` supports MDIO/PHY integration, and `CRC32` supports multicast hash filtering in the driver.

Risks: the hard `SPARC` dependency prevents test builds on other architectures even though much of the driver is generic platform/netdev code. Any future non-SPARC GRETH deployment would need Kconfig loosening plus audit of `ofdev->archdata.irqs` and IDPROM fallback usage.

Test signals: expected signals are menu visibility only on SPARC, `CONFIG_GRETH=m` producing `greth.ko`, automatic selection of PHYLIB/CRC32, and a clean build of `greth.c` with the selected architecture headers.
