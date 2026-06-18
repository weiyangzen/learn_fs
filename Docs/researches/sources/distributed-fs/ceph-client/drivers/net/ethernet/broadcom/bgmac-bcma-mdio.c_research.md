# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma-mdio.c

Purpose: Provides MDIO/MII bus support for the `bgmac` driver when the MAC is attached through BCMA. It translates phylib mdiobus reads/writes into Broadcom GMAC PHY access register transactions and performs legacy chipset PHY initialization.

Important APIs/functions: `bcma_mdio_phy_read()` and `bcma_mdio_phy_write()` program PHY control/access registers and wait for `BGMAC_PA_START` to clear. They choose either the GMAC common core for BCM4706 or the MAC core itself for other devices. `bcma_mdio_phy_init()` applies special register sequences for older BCM5356/5357/4749/53572 chipsets, otherwise calls `phy_init_hw()`. `bcma_mdio_phy_reset()` resets the selected PHY. `bcma_mdio_mii_register()` allocates and registers an OF mdiobus and `bcma_mdio_mii_unregister()` tears it down.

Control flow: The BCMA probe path registers this bus before shared `bgmac_enet_probe()` connects phylib. Reads/writes update the external PHY address in PHY control, start an MDIO operation, poll with microsecond delays, and return data or timeout errors. The bus reset hook reinitializes PHY hardware.

State/persistence: The mdiobus owns `bus->priv = bgmac`, a generated bus id, parent device, and phy mask derived from `bgmac->phyaddr`. No persistent stats are maintained here, but hardware register programming affects PHY state.

Dependencies/integration: Depends on BCMA core accessors, Broadcom PHY constants, OF MDIO registration, phylib, and `bgmac.h` register definitions. It exports register/unregister symbols for the BCMA front-end.

Risks/test signals: Risks include wrong core selection on BCM4706, legacy magic PHY sequences, phy mask mistakes, timeout handling, and missing OF child-node cleanup. Test by probing supported BCMA chip IDs, scanning MDIO, reading standard MII registers, reset/autonegotiation, and unload/reload with OF MDIO children.
