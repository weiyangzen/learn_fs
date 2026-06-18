# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/Kconfig

## Purpose
This Kconfig file exposes the Calxeda Highbank XGMAC Ethernet driver. It defines `NET_CALXEDA_XGMAC`, a tristate option for the 1G/10G XGMAC IP block used on Calxeda Highbank platforms.

## Important symbols and dependencies
`NET_CALXEDA_XGMAC` depends on `HAS_IOMEM` and `ARCH_HIGHBANK || COMPILE_TEST`, and selects `CRC32`. The architecture dependency limits normal use to Highbank while preserving wider compile coverage.

## Control flow, state, integration, and tests
There is no runtime control flow or persisted state. The symbol controls whether `xgmac.o` is built by the directory Makefile. Risks are mostly build coverage erosion for older Highbank-specific hardware. Test by building with `ARCH_HIGHBANK` and with `COMPILE_TEST` on other `HAS_IOMEM` architectures.
