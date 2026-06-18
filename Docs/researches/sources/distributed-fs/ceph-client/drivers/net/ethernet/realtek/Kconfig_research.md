# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Kconfig

Purpose: Defines configuration options for Realtek Ethernet drivers in this vendor directory.

Important entries: `NET_VENDOR_REALTEK` gates the vendor menu and depends on PCI. `8139CP` enables RTL-8139C+ support and selects CRC32/MII. `8139TOO` enables older RTL-8129/8130/8139 support and selects CRC32/MII. Associated booleans configure PIO, Twister tuning, older 8129/8130 support, and old RX reset behavior. `R8169` enables RTL8169/8168/8101/8125 and selects firmware loading, CRC32, PHYLIB, and REALTEK_PHY. `R8169_LEDS` gates optional LED class support. `RTASE` enables automotive switch PCIe support with CRC32 and PAGE_POOL.

Control flow and integration: Symbols drive object selection in the Makefile and compile-time branches inside `8139too.c` and `r8169_leds.c`. Dependency expressions prevent unsupported combinations such as built-in R8169 with modular LED class.

State and persistence: No runtime state. Kernel `.config` persists these choices and changes compiled code shape.

Risks and test signals: Risks include incorrect defaults, missing selects when source dependencies change, and option combinations that leave unresolved symbols. Test signals include randconfig/allmodconfig builds, `8139TOO_PIO` and `8139TOO_8129` variant builds, and R8169 LED modularity combinations.
