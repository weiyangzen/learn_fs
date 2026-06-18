# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Kconfig

## Purpose
This Kconfig file defines the STMMAC core driver, optional selftests, platform-bus glue drivers, PCI helpers, and many SoC/vendor-specific DWMAC variants.

## Important APIs, Types, And Functions
- `STMMAC_ETH` is the main tristate for Synopsys Ethernet IP based controllers. It depends on I/O memory, DMA, optional PTP clock support, and ethtool netlink, and selects core subsystems including MII, PCS_XPCS, PAGE_POOL, PHYLINK, CRC32, reset controller, and devlink.
- `STMMAC_SELFTESTS` enables ethtool selftests when INET is present.
- `STMMAC_PLATFORM` enables platform-bus support and selects `MFD_SYSCON`.
- Platform glue options include DWC QoS, generic, Anarion, EIC7700, Ingenic, i.MX8, Intel platform, and many other SoC integrations.
- PCI-related options include `STMMAC_LIBPCI`, `DWMAC_INTEL`, `DWMAC_LOONGSON`, `DWMAC_MOTORCOMM`, and generic `STMMAC_PCI`.

## Control Flow
Selecting `STMMAC_ETH` enables the nested menus. Platform drivers are visible only under `STMMAC_PLATFORM`, while PCI choices are under the main STMMAC block. Each symbol maps to objects in `stmmac/Makefile`.

## State And Persistence
Configuration only; no runtime state.

## Dependencies And Integration Points
The file coordinates STMMAC with PHYLINK, XPCS, page pool, PTP, reset, syscon, MDIO mux/regmap, and architecture-specific symbols. It gates the build for all STMMAC core and glue sources in this work item.

## Risks
- Operator precedence in expressions such as `depends on OF && HAS_DMA && ARCH_ESWIN || COMPILE_TEST` should be read as allowing compile-test even without the earlier terms; this is common but can surprise maintainers.
- Selecting `STMMAC_PLATFORM` defaults to `y`, which may pull many platform options into config menus.
- Missing dependencies in individual glue options can surface as compile-test failures rather than menu constraints.

## Test Signals
Run `allmodconfig`/`allyesconfig`/architecture configs and verify the intended objects are selected. Confirm `DWMAC_EIC7700`, `DWMAC_IMX8`, `DWMAC_INTEL_PLAT`, and `DWMAC_INTEL` each map to their corresponding object files.
