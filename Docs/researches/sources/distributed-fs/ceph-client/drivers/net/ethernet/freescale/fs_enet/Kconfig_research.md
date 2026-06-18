# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Kconfig

## Purpose
Defines build-time configuration for the legacy Freescale `fs_enet` Ethernet driver and its FEC/FCC/SCC MAC and MDIO support.

## Important APIs, Types, and Functions
Key symbols are `FS_ENET`, `FS_ENET_MPC5121_FEC`, `FS_ENET_HAS_SCC`, `FS_ENET_HAS_FCC`, `FS_ENET_HAS_FEC`, `FS_ENET_MDIO_FEC`, and `FS_ENET_MDIO_FCC`. `FS_ENET` selects `MII` and `PHYLINK`; FEC support selects FEC MDIO; FCC MDIO selects `MDIO_BITBANG`.

## Control Flow and State
There is no runtime control flow. The file controls which source files are compiled and which platform/device-tree compatibles can bind at runtime. Platform constraints limit the driver to Freescale vendor support on CPM1, CPM2, or PPC MPC512x systems.

## Dependencies and Integration Points
Feeds the local Makefile and conditional code in `fs_enet.h`, `fs_enet-main.c`, and the MAC/MDIO backends. It integrates with kernel networking, phylink, MII, and mdio-bitbang subsystems through selected symbols.

## Risks and Test Signals
Risks include build combinations where declarations are present without matching objects, missing MDIO support for selected FEC hardware, and accidental exposure outside supported PowerPC/CPM platforms. Test signals are randconfig/allmodconfig coverage for CPM1, CPM2, and MPC512x, plus module dependency checks for FEC/FCC/SCC and MDIO variants.
