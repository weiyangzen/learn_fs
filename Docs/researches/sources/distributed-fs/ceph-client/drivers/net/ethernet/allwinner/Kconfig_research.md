# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Kconfig

## Purpose
This Kconfig file defines the Allwinner Ethernet vendor menu and the `SUN4I_EMAC` option for the Allwinner A10 EMAC driver.

## Important configuration
- `NET_VENDOR_ALLWINNER` is a boolean vendor gate, defaulting to `y`, depending on `ARCH_SUNXI`.
- `SUN4I_EMAC` is a tristate depending on `ARCH_SUNXI` and `OF`, selecting `CRC32`, `MII`, `PHYLIB`, and `MDIO_SUN4I`.

## Control flow and integration
When `SUN4I_EMAC` is enabled, kbuild includes `sun4i-emac.o` through the directory Makefile. The selected libraries provide PHY/MDIO and multicast hash support for the platform driver.

## State and persistence behavior
No runtime state exists here. The file controls build-time availability.

## Dependencies and integration points
It integrates into the networking Ethernet driver Kconfig tree and restricts visibility to SUNXI/OF platforms.

## Risks and edge cases
The `ARCH_SUNXI` dependency means cross-architecture compile testing needs config overrides or SUNXI builds. Selecting `MDIO_SUN4I` assumes the EMAC driver uses the matching MDIO bus provider in devicetree systems.

## Test signals
Verify config visibility under SUNXI/OF, module and built-in builds for `SUN4I_EMAC`, and automatic selection of PHYLIB/MII/MDIO_SUN4I/CRC32.
