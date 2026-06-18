# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Kconfig

Purpose: adds the `CONFIG_LAN865X` tristate for Microchip LAN8650/1 10BASE-T1S MAC-PHY support under `NET_VENDOR_MICROCHIP`.

Important behavior: the symbol depends on `SPI` and selects `OA_TC6`, making the OPEN Alliance TC6 helper layer mandatory when the driver is enabled. The help text documents LAN8650/1 Rev.B0/B1 support and that the module name is `lan865x`.

Control flow and state: no runtime control flow or state. At build time it controls whether `lan865x.o` is built and whether the OA-TC6 support is pulled in.

Dependencies and integration points: integrates with the kernel networking vendor menu, SPI subsystem, and OA-TC6 MAC-PHY framework. The runtime driver depends on PHYLIB through source includes and netdev operations, but the Kconfig dependency expressed here is SPI plus selected OA_TC6.

Risks and test signals: missing dependencies show up as build failures in randconfig/allmodconfig. Test signals are `CONFIG_LAN865X=m/y/n` builds, SPI-disabled configurations, and verification that enabling this symbol selects OA_TC6 and produces a `lan865x` module.
