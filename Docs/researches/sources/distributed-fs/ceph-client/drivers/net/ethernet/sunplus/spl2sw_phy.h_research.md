# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.h

Purpose: Declares Sunplus PHY attach/detach helpers.

Important APIs: `spl2sw_phy_connect()` attaches phylib devices for all registered ports; `spl2sw_phy_remove()` disconnects them during remove.

State and dependencies: Operates on the shared `struct spl2sw_common` and each netdev's private `struct spl2sw_mac` PHY node/mode. Requires MDIO registration first and netdevs already created.

Risks and test signals: Callers must handle partial attach failure and must not call remove before netdev private PHY pointers are meaningful. Test probe failure unwind and normal unload with one or two PHYs.
