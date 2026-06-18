## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.c

Purpose: programs the v2 RGMII MAC for reset, speed, station address, and TX/RX enablement.

Important APIs, types, and functions: `xge_mac_reset` toggles `SOFT_RESET`. `xge_mac_set_speed` programs MAC, interface control, ICM/ECM, and RGMII registers for 10/100/1000 speeds based on `pdata->phy_speed`. `xge_mac_set_station_addr` writes the netdev MAC address into `STATION_ADDR0/1`. `xge_mac_init` resets, sets speed, and writes the address. `xge_mac_enable` and `xge_mac_disable` set/clear `TX_EN` and `RX_EN`.

Control flow, state, and persistence: probe defaults to 1Gbps through `xge_port_init`; PHY adjustment in `mdio.c` updates `pdata->phy_speed`, disables MAC, reprograms speed, and re-enables MAC when link settings change. MAC address changes flow from `ndo_set_mac_address` in `main.c`.

Dependencies and integration points: depends on register bit helpers in `mac.h`, CSR wrappers in `enet.c`, PHYLIB speed constants, and `net_device` address state.

Risks: bit helper masks use `GENMASK(pos + len, pos)`, so field definitions must be consistent with that convention. Reprogramming speed while RX/TX are active is guarded by the link adjust path but direct callers should avoid racing with data path. The enable function reads back `MAC_CONFIG_1` but does not use the value.

Test signals: PHY speed changes at 10/100/1000 should update link without packet corruption; MAC address changes should be reflected in hardware and visible on the network.
