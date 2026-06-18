# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Kconfig

## Purpose
This Kconfig file defines `ALTERA_TSE`, the Altera Triple-Speed Ethernet MAC driver option.

## Important configuration
- `ALTERA_TSE` is a tristate depending on `HAS_DMA` and `HAS_IOMEM`.
- It selects `PHYLIB`, `PHYLINK`, `PCS_LYNX`, `MDIO_REGMAP`, and `REGMAP_MMIO`, reflecting the MAC/PCS/MDIO stack used by the full driver.

## Control flow and integration
When enabled, the Altera Makefile builds the composite `altera_tse` object from main, ethtool, DMA, and utility sources. The same option covers both SGDMA and mSGDMA variants selected by devicetree match data at probe time.

## State and persistence behavior
No runtime state exists here. It controls driver availability at build time.

## Dependencies and integration points
The option integrates with the Ethernet driver menu and ensures the required phylink/PCS/regmap infrastructure is available.

## Risks and edge cases
Systems without DMA or IOMEM cannot select the driver. Because both DMA backends are compiled into one module, build errors in either backend break the single driver.

## Test signals
Check built-in and module builds, verify selected dependencies appear in generated configs, and confirm the composite object links with both DMA backends.
