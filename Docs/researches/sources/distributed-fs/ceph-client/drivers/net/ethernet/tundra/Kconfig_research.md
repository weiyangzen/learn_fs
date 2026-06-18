# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Kconfig

Purpose: Adds Kconfig menu entries for Tundra Ethernet devices and the TSI108 gigabit Ethernet driver.

Important APIs and symbols: Defines `NET_VENDOR_TUNDRA` as a vendor-menu boolean defaulting to `y` when `TSI108_BRIDGE` is available, and `TSI108_ETH` as a tristate driver option for Tundra TSI108 gigabit Ethernet ports. The help text documents that the module name is `tsi108_eth`.

Control flow and integration: Kconfig has no runtime flow. The vendor symbol gates visibility of the driver option through `if NET_VENDOR_TUNDRA`. The driver option is consumed by the local Makefile to build `tsi108_eth.o` and by source-level conditional compilation in the kernel configuration.

State and persistence: Kernel configuration persists in `.config`. Selecting `TSI108_ETH=y` builds the driver into the kernel; `m` builds a loadable module; `n` omits it.

Dependencies and integration points: Both symbols depend on `TSI108_BRIDGE`, tying this Ethernet support to platforms that expose the Tundra TSI108 bridge infrastructure and headers. It integrates with the broader Ethernet vendor menu.

Risks: Because `NET_VENDOR_TUNDRA` depends on `TSI108_BRIDGE`, the menu disappears entirely on non-TSI108 platforms. There are no extra dependencies on PHY/MII helpers here even though `tsi108_eth.c` uses MII APIs; those must be satisfied by surrounding kernel networking config selects.

Test signals: `oldconfig`/`menuconfig` visibility with and without `TSI108_BRIDGE`; built-in and module builds for `CONFIG_TSI108_ETH`; verify module name `tsi108_eth`; compile dependency coverage for MII, platform-device, and TSI108 register headers.
