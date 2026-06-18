# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Kconfig

## Purpose
This Kconfig file is the top-level menu for Freescale/NXP Ethernet drivers. It gates the vendor menu behind `NET_VENDOR_FREESCALE`, declares classic FEC/MPC52xx/PQ/XGMAC/UCC/Gianfar symbols, and sources submenus for fs_enet, FMan, DPAA, DPAA2, and ENETC.

## Important APIs, Types, and Functions
The significant configuration symbols are `NET_VENDOR_FREESCALE`, `FEC`, `FEC_MPC52xx`, `FEC_MPC52xx_MDIO`, `FSL_PQ_MDIO`, `FSL_XGMAC_MDIO`, `UCC_GETH`, `UGETH_TX_ON_DEMAND`, and `GIANFAR`. Symbols select dependencies such as `PHYLIB`, `PHYLINK`, `FIXED_PHY`, `PAGE_POOL`, `CRC32`, `OF_MDIO`, and Freescale platform blocks.

## Control Flow
Kconfig control flow is menu-based. `NET_VENDOR_FREESCALE` depends on a broad set of Freescale-related SoC/architecture symbols or `COMPILE_TEST`; when enabled, it exposes individual driver options and includes subdirectory Kconfig files. Downstream symbols then determine which objects the Makefiles build.

## State and Persistence
State is persisted only in kernel configuration (`.config`). No runtime state exists.

## Dependencies and Integration Points
This file integrates with the kernel networking driver Kconfig hierarchy and with `drivers/net/ethernet/freescale/Makefile`. It also establishes dependency contracts for PHY, phylink, MDIO, page pool, FMan, and DPAA subdrivers.

## Risks
Incorrect dependency expressions can expose drivers on unsupported architectures or hide valid compile-test coverage. The menu's broad default `y` makes subdriver dependencies especially important. DPAA and DPAA2 functionality depends on sourced files, so missing source statements would silently remove platform support.

## Test Signals
Useful signals are `olddefconfig` and `allyesconfig`/`allmodconfig` coverage across ARM, PPC, Layerscape, S32, and `COMPILE_TEST`, plus checking that selected symbols produce the expected object lists.
