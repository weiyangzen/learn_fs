# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Kconfig

Purpose: this vendor Kconfig file declares the Actions Semi Ethernet menu and the Owl EMAC driver option.

Important APIs, types, and functions: `config NET_VENDOR_ACTIONS` is a boolean vendor gate depending on `ARCH_ACTIONS || COMPILE_TEST` and defaulting to `ARCH_ACTIONS`. `config OWL_EMAC` is a tristate for the Actions Semi Owl Ethernet MAC and selects `PHYLIB`. The help text identifies S500 and S900 SoCs and 10/100 Mb/s IEEE 802.3 operation.

Control flow: the top-level Ethernet Kconfig sources this file. If the vendor gate is disabled, `OWL_EMAC` is hidden. When enabled, `OWL_EMAC=y/m` controls whether `actions/Makefile` builds `owl-emac.o` built-in or as a module.

State and persistence: configuration state persists in `.config`. No runtime state is stored here.

Dependencies and integration points: integrates with `drivers/net/ethernet/Kconfig`, `drivers/net/ethernet/Makefile`, `actions/Makefile`, and the `owl-emac.c` driver. It selects `PHYLIB` because the driver uses phylib helpers, MDIO registration, and PHY connection APIs. The vendor dependency permits native Actions builds and compile-test coverage elsewhere.

Risks: this symbol does not explicitly depend on `HAS_IOMEM`, `HAS_DMA`, OF, clocks, or reset support even though the driver uses MMIO, DMA, device tree, clock, and reset APIs; broader architecture and compile-test coverage need to catch missing dependencies. If `PHYLIB` selection is removed, `owl-emac` will fail to link.

Test signals: Kconfig parsing with `ARCH_ACTIONS`, without `ARCH_ACTIONS`, and with `COMPILE_TEST`. Build `CONFIG_OWL_EMAC=m` and `=y`, verify `PHYLIB` is selected, and confirm menu visibility under `ETHERNET`.
