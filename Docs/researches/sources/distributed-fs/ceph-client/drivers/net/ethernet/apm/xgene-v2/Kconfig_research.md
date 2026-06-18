## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/Kconfig

Purpose: defines `NET_XGENE_V2`, the selectable APM X-Gene Ethernet v2 driver.

Important APIs, types, and functions: the symbol is tristate, named "APM X-Gene SoC Ethernet-v2 Driver", depends on `ARCH_XGENE || COMPILE_TEST`, and documents that the module name is `xgene-enet-v2`.

Control flow, state, and dependencies: build-time selection controls whether the v2 platform driver and helpers compile. The help text identifies the linked-list DMA descriptor architecture used by this generation.

Integration points: paired with `xgene-v2/Makefile`, which builds `main.o`, `mac.o`, `enet.o`, `ring.o`, `mdio.o`, and `ethtool.o` into `xgene-enet-v2.o`.

Risks: the driver uses PHYLIB APIs in code but this Kconfig does not explicitly select PHYLIB in this file; it may rely on other dependency paths. Changes should verify compile-test coverage on non-X-Gene architectures.

Test signals: enable as module and built-in under `COMPILE_TEST`; build should include ACPI/platform, PHY, MDIO, DMA, and ethtool references without unresolved symbols.
