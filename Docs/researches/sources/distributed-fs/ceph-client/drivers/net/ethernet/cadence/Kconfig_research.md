# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Kconfig

## Purpose
This Kconfig file exposes the Cadence Ethernet driver family to the Linux networking configuration menu. It defines the vendor gate `NET_VENDOR_CADENCE`, the main Cadence MACB/GEM platform driver option `MACB`, optional GEM IEEE 1588 hardware timestamping through `MACB_USE_HWSTAMP`, and the `MACB_PCI` wrapper that instantiates the platform driver from a Cadence PCI function.

## Important symbols and dependencies
- `NET_VENDOR_CADENCE` is a boolean vendor menu guarded by `HAS_IOMEM` and defaults to enabled so Cadence devices remain discoverable in normal network driver configuration.
- `MACB` is tristate, depends on `HAS_DMA`, `COMMON_CLK`, and `PTP_1588_CLOCK_OPTIONAL`, and selects `PHYLINK` and `CRC32`.
- `MACB_USE_HWSTAMP` is a boolean dependent on `MACB` and `PTP_1588_CLOCK`; when enabled it causes `macb_ptp.o` to be linked into the `macb` module.
- `MACB_PCI` is a tristate dependent on both `MACB` and `PCI`; it builds the PCI wrapper module `macb_pci`.

## Control flow and integration
This file controls object inclusion rather than runtime control flow. `MACB` enables `macb_main.o`; `MACB_USE_HWSTAMP` adds PTP support and activates `CONFIG_MACB_USE_HWSTAMP` declarations in `macb.h`; `MACB_PCI` builds a separate wrapper that registers a platform device named `macb`.

## State, risks, and test signals
The state is compile-time configuration. Risk appears as missing timestamp, PCI, phylink, DMA, or clock support if dependencies change incorrectly. Build tests should cover `MACB=y/m`, timestamp enabled/disabled, and `MACB_PCI=y/m`; runtime signals include normal netdev registration and `ethtool -T` reporting PHC support only when Kconfig and hardware both allow it.
