# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.c

Purpose: Connects each Sunplus netdev to its PHY and mirrors phylib link state into forced RMII switch mode registers.

Important APIs/functions: `spl2sw_phy_connect()` iterates registered netdevs, calls `of_phy_connect()` with each port's PHY node/mode and `spl2sw_mii_link_change()` callback, enables asymmetric pause support, and logs attached PHY info. `spl2sw_phy_remove()` disconnects each netdev PHY. `spl2sw_mii_link_change()` updates link, speed, duplex, and pause bits in `L2SW_MAC_FORCE_MODE` for the port bit represented by `mac->lan_port`, then calls `phy_print_status()`.

Control flow and state: Link state is not cached in driver memory; each phylib callback rewrites the forced RMII register. The per-port bitmask controls which of the two RMII lanes is affected.

Dependencies and integration points: Depends on MDIO bus registration, valid `phy-handle` nodes parsed in probe, phylib state machine, and Sunplus force-mode bit definitions. Open/stop call `phy_start()`/`phy_stop()` in `spl2sw_driver.c`.

Risks and test signals: Register updates are not locked, so simultaneous link callbacks on two PHYs can race read-modify-write updates. Partial failure in `spl2sw_phy_connect()` does not disconnect already connected PHYs before returning. Test both PHYs flapping concurrently, 10/100 speed, half/full duplex, pause on/off, missing PHY, and remove after a one-port connect failure.
