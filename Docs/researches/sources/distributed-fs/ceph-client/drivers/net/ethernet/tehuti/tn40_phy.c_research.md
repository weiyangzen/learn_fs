# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_phy.c

## Purpose
This file binds TN40xx MAC control to the Linux phylink framework. It discovers the first PHY on the MDIO bus, creates a phylink instance for an XAUI netdev MAC, and maps link-up/link-down callbacks to TN40 MAC speed programming and netdev queue state.

## Important APIs, Types, and Functions
Public functions are `tn40_phy_register` and `tn40_phy_unregister`. Internal callbacks are `tn40_link_up`, `tn40_link_down`, `tn40_mac_config`, and `tn40_config_to_priv`. `tn40_mac_ops` supplies those callbacks to `phylink_create`.

## Control Flow and State
Registration calls `phy_find_first` on `priv->mdio`, initializes `priv->phylink_config` with `PHYLINK_NETDEV`, `MAC_10000FD`, and XAUI support, creates phylink, and stores `phydev`/`phylink` in `tn40_priv`. On link up, phylink calls `tn40_set_link_speed` with the negotiated speed and wakes the queue. On link down, it stops the queue and programs speed 0. Unregister destroys the phylink object.

## Dependencies and Integration Points
The file depends on `tn40.h`, Linux PCI/netdevice, phylink, and phylib. It integrates with `tn40_open`/`tn40_close`, which connect/disconnect and start/stop phylink, and with `tn40_set_link_speed` in `tn40.c`, which applies low-level PCS/MAC register sequences.

## Risks and Test Signals
Only `MAC_10000FD` is advertised even though `tn40_set_link_speed` has register sequences for 100M, 1G, 2.5G, 5G, and 10G, so capability modeling may be narrower than hardware. `tn40_mac_config` is empty, so interface changes rely entirely on link-up programming. Tests should cover missing PHY, XAUI mode negotiation, link up/down queue transitions, speed changes, and phylink destroy on probe failure/remove.
