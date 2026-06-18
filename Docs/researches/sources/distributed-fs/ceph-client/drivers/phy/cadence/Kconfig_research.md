# sources/distributed-fs/ceph-client/drivers/phy/cadence/Kconfig

Purpose: Defines the Kconfig symbols that expose Cadence PHY drivers to kernel configuration: Torrent, MIPI D-PHY TX, MIPI D-PHY RX, Sierra, and Salvo.

Important APIs and symbols: `PHY_CADENCE_TORRENT` depends on OF, HAS_IOMEM, and COMMON_CLK and selects GENERIC_PHY. `PHY_CADENCE_DPHY` and `PHY_CADENCE_DPHY_RX` depend on HAS_IOMEM and OF, select GENERIC_PHY and GENERIC_PHY_MIPI_DPHY, and build `cdns-dphy` or `cdns-dphy-rx` when modular. `PHY_CADENCE_SIERRA` depends on OF, HAS_IOMEM, RESET_CONTROLLER, and COMMON_CLK and selects GENERIC_PHY. `PHY_CADENCE_SALVO` depends on OF and HAS_IOMEM and selects GENERIC_PHY.

Control flow: Kconfig does not execute at runtime. Its selection controls whether the corresponding object files in the Cadence PHY Makefile are compiled and whether dependent PHY framework support is enabled.

State and persistence: Configuration state persists in the kernel `.config`. Choosing `m` versus `y` determines module availability and autoload behavior through OF module aliases in each driver.

Dependencies and integration points: The dependencies match visible driver requirements: MMIO and OF platform probing across all drivers, common clock support for Torrent/Sierra and D-PHY TX, reset controller support for Sierra, and MIPI D-PHY helper validation for TX/RX D-PHY drivers.

Risks: Missing `select GENERIC_PHY_MIPI_DPHY` would break D-PHY helper usage. Underdeclared reset or clock dependencies can create compile/link failures or unusable runtime configurations. Help text is brief, so board integrators must rely on device-tree bindings for detailed compatible and property requirements.

Test signals: `allmodconfig`, `allyesconfig`, and targeted builds for each symbol, plus module autoload on matching DT compatibles, validate the menu wiring.
